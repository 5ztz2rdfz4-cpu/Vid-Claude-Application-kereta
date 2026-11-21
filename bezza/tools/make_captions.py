"""Builds assets/captions.js from assets/words_edit.json: fixes ASR spelling, merges split
tokens, groups words into short karaoke phrases."""
import json, re
W = json.load(open("assets/words_edit.json"))
FIX = {"buk": "but", "bubur": "bubuh", "get": "guide", "ni,": "ni,"}
END = 56.1          # captions stop when the closing logo starts
# merge split tokens (",000", ".3", ".3X", "-banyak")
words = []
for w in W:
    t = w["w"]
    if words and re.match(r"^[,.\-]", t) and not t.startswith(", "):
        words[-1]["w"] += t; words[-1]["e"] = w["e"]; continue
    words.append(dict(w=t, s=w["s"], e=w["e"]))
for i, w in enumerate(words):
    w["w"] = FIX.get(w["w"], w["w"])
    if w["w"] == "nak" and i and words[i - 1]["w"] == "stroller": w["w"] = "anak"
words = [w for w in words if w["s"] < END - 0.05]
GOLD = {"paling", "laris", "bezza", "perodua", "73,000", "2026", "508", "litre", "luas", "1.3", "1.3x",
        "tahan", "lasak", "jimat", "minyak", "push", "start", "button", "kawalan", "kestabilan", "hill",
        "assist", "2030", "spare", "part", "gaji", "form", "stroller", "raya", "axia", "myvi", "variant",
        "pertama", "kedua", "ketiga", "empat", "lebih"}
BREAK_AT = {17.7, 27.1, 33.2, 40.7, 49.5}   # scene boundaries
phrases, cur = [], []
for i, w in enumerate(words):
    if cur:
        gap = w["s"] - cur[-1]["e"]
        scene_cut = any(cur[-1]["s"] < b <= w["s"] + 0.05 for b in BREAK_AT)
        if w["w"].lower() in ("mengikut", "jadi") or len(cur) >= 5 or re.search(r"[,.?]$", cur[-1]["w"]) or gap > 0.35 or scene_cut:
            phrases.append(cur); cur = []
    cur.append(w)
phrases.append(cur)
# fold very short single-word phrases back into the previous one
merged = []
for k, p in enumerate(phrases):
    nxt = phrases[k + 1][0]["s"] if k + 1 < len(phrases) else END
    if merged and len(p) == 1 and nxt - p[0]["s"] < 0.8 and len(merged[-1]) <= 5 \
            and not any(merged[-1][-1]["s"] < b <= p[0]["s"] + 0.05 for b in BREAK_AT):
        merged[-1] = merged[-1] + p
    else:
        merged.append(p)
phrases = merged
out = []
for k, p in enumerate(phrases):
    nxt = phrases[k + 1][0]["s"] if k + 1 < len(phrases) else END
    out.append(dict(s=round(p[0]["s"] - 0.04, 3), e=round(min(nxt - 0.02, END), 3),
                    w=[dict(t=x["w"].rstrip(",."), s=round(x["s"], 3),
                            g=x["w"].lower().rstrip(",.") in GOLD) for x in p]))
open("assets/captions.js", "w").write("window.CAPTIONS = " + json.dumps(out, ensure_ascii=False) + ";\n")
for p in out: print(p["s"], p["e"], " ".join(("*" if x["g"] else "") + x["t"] for x in p["w"]))
