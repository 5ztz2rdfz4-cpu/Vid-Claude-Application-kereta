"""Build the shared timeline (scene times, karaoke phrases, SFX cues) for the film.

Writes assets/data/timeline.js (read by index.html) and tools/timeline.json (read by make_audio.py).
usage: python3 -I build_timeline.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

vo = json.load(open(os.path.join(HERE, "vo_timing.json")))

# ---- clean words: merge "RM1" ",800" tokens, fix spellings ----
FIX = {"ProDua": "Perodua"}
words = []
for w in vo["words"]:
    t = FIX.get(w["w"], w["w"])
    if t.startswith(",") and words:
        words[-1]["w"] += t
        words[-1]["e"] = w["e"]
        continue
    words.append({"w": t, "s": w["s"], "e": w["e"]})
# nudge the RM numbers: whisper spreads them; keep as is but ensure monotonic
for a, b in zip(words, words[1:]):
    if b["s"] < a["s"]:
        b["s"] = a["s"]

KEY = {"kereta", "baru", "gaji", "rm1,800", "rm2,000", "tiga", "sesuai", "saga", "mc3", "axia", "bezza",
       "rm423", "rm455", "rm415", "proton", "perodua", "form", "a", "z", "bawah", "kegunaan", "bantu"}

def norm(t):
    return t.lower().strip(".,?!")

# ---- phrase chunks: break on punctuation or after 4 words ----
import math

sentences = []
cur = []
for i, w in enumerate(words):
    cur.append(w)
    if w["w"][-1] in ".,?!" or i == len(words) - 1:
        sentences.append(cur)
        cur = []
phrases = []
for snt in sentences:
    n = len(snt)
    k = math.ceil(n / 4)
    base, extra = divmod(n, k)
    i = 0
    for c in range(k):
        size = base + (1 if c < extra else 0)
        phrases.append(snt[i:i + size])
        i += size

ph_out = []
for k, p in enumerate(phrases):
    start = p[0]["s"] - 0.06
    nxt = phrases[k + 1][0]["s"] - 0.06 if k + 1 < len(phrases) else p[-1]["e"] + 0.5
    end = min(nxt, p[-1]["e"] + 0.9)
    ph_out.append({
        "s": round(start, 3),
        "e": round(end, 3),
        "w": [{"t": x["w"].rstrip(","), "s": x["s"], "k": norm(x["w"]) in KEY} for x in p],
    })

def at(word, nth=1):
    c = 0
    for w in words:
        if norm(w["w"]) == word.lower():
            c += 1
            if c == nth:
                return w["s"]
    raise KeyError(word)

# ---- scenes ----
T = {
    "hook": 0.0,
    "intro": 7.75,
    "saga": 11.72,
    "axia": 18.78,
    "bezza": 24.72,
    "compare": 31.66,
    "cta": 37.66,
    "outro": 44.70,
    "end": 50.4,
}

# ---- key beats (from the voice) ----
B = {
    "keretaBaru": at("kereta", 1),
    "tapiGaji": at("tapi"),
    "rm1800": at("rm1,800"),
    "rm2000": at("rm2,000"),
    "tiga": at("tiga"),
    "model": at("model", 1),
    "sesuai": at("sesuai", 1),
    "saga": at("proton"),
    "mc3": at("mc3"),
    "sagaBulanan": at("bulanan", 1),
    "rm423": at("rm423"),
    "sagaSebulan": at("sebulan", 1),
    "axiaKedua": at("kedua"),
    "axia": at("perodua", 1),
    "axiaBulanan": at("bulanan", 2),
    "rm455": at("rm455"),
    "axiaSebulan": at("sebulan", 2),
    "bezzaKetiga": at("ketiga"),
    "bezza": at("perodua", 2),
    "bezzaBulanan": at("bulanan", 3),
    "rm415": at("rm415"),
    "bezzaSebulan": at("sebulan", 3),
    "jadi": at("jadi"),
    "manaSatu": at("mana"),
    "lebihSesuai": at("lebih"),
    "kegunaan": at("kegunaan"),
    "gajiQ": at("gaji", 2),
    "tunggu": at("tunggu"),
    "isiForm": at("isi"),
    "diBawah": at("bawah"),
    "kitaBantu": at("kita"),
    "guide": at("guide"),
    "dariA": at("a"),
    "sampaiZ": at("z"),
}
B = {k: round(v, 3) for k, v in B.items()}

# ---- SFX cues (time, name, gain) ----
cues = [
    (0.02, "carpass", 0.55),
    (0.70, "brake", 0.35),
    (B["keretaBaru"] - 0.02, "impact_soft", 0.55),
    (B["tapiGaji"] + 0.12, "whoosh_up", 0.4),
    (B["rm1800"], "count", 0.25),
    (B["rm1800"] + 0.72, "pop", 0.35),
    (B["rm2000"] - 0.02, "pop", 0.4),
    (T["intro"] - 0.55, "riser", 0.35),
    (T["intro"] - 0.05, "whoosh", 0.5),
    (B["tiga"], "impact", 0.65),
    (B["model"] + 0.05, "pop", 0.3), (B["model"] + 0.20, "pop", 0.3), (B["model"] + 0.35, "pop", 0.3),
    (B["sesuai"] + 0.02, "ding", 0.28), (B["sesuai"] + 0.17, "ding", 0.24), (B["sesuai"] + 0.32, "ding", 0.28),
]
for name, t0 in (("saga", T["saga"]), ("axia", T["axia"]), ("bezza", T["bezza"])):
    rm = {"saga": "rm423", "axia": "rm455", "bezza": "rm415"}[name]
    cues += [
        (t0 - 0.08, "whoosh", 0.5),
        (t0 + 0.12, "impact_soft", 0.45),
        (B[name] - 0.05, "swipe", 0.45),
        (B[name + "Bulanan"], "pop", 0.35),
        (B[rm], "count", 0.25),
        (B[rm] + 0.72, "cash", 0.42),
        (B[name + "Sebulan"] + 0.05, "fill", 0.3),
    ]
cues += [
    (T["compare"] - 0.08, "whoosh", 0.5),
    (T["compare"] + 0.30, "pop", 0.28), (T["compare"] + 0.45, "pop", 0.28), (T["compare"] + 0.60, "pop", 0.28),
    (T["compare"] + 0.35, "fill", 0.28),
    (B["manaSatu"], "impact_soft", 0.45),
    (B["kegunaan"], "pop", 0.4),
    (B["gajiQ"], "pop", 0.4),
    (B["gajiQ"] + 0.35, "ding", 0.3),
    (T["cta"] - 0.08, "whoosh", 0.5),
    (T["cta"] + 0.3, "swipe", 0.35),
    (B["isiForm"], "impact_soft", 0.45),
    (B["isiForm"] + 0.55, "click", 0.55),
    (B["diBawah"], "pop", 0.3),
    (B["kitaBantu"] - 0.1, "whoosh_up", 0.35),
    (B["dariA"] - 0.05, "pop", 0.35),
    (B["dariA"] + 0.05, "carpass_soft", 0.35),
    (B["sampaiZ"] + 0.05, "ding", 0.35),
    (T["outro"] - 0.6, "riser", 0.4),
    (T["outro"] - 0.05, "whoosh", 0.55),
    (T["outro"] + 0.25, "logo_hit", 0.75),
    (T["outro"] + 0.95, "shimmer", 0.35),
    (T["outro"] + 2.30, "sparkle", 0.3),
]
cues = sorted([(round(t, 3), n, g) for t, n, g in cues])

data = {"T": T, "B": B, "phrases": ph_out, "voEnd": vo["duration"]}
os.makedirs(os.path.join(ROOT, "assets", "data"), exist_ok=True)
with open(os.path.join(ROOT, "assets", "data", "timeline.js"), "w") as f:
    f.write("// generated by tools/build_timeline.py — do not edit by hand\n")
    f.write("window.FILM = " + json.dumps(data, ensure_ascii=False) + ";\n")
json.dump({"T": T, "B": B, "cues": cues, "words": words}, open(os.path.join(HERE, "timeline.json"), "w"), indent=1)
print(json.dumps(B, indent=0))
print(len(ph_out), "phrases;", len(cues), "cues")
for p in ph_out:
    print(f'{p["s"]:6.2f}-{p["e"]:6.2f}', " ".join(w["t"] for w in p["w"]))
