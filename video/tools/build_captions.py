"""Turn the word-level transcript into caption groups (assets/captions.js)."""
import json, re, sys
words = [w for s in json.load(open(sys.argv[1])) for w in s["words"]]
FIX = {"dompayment": "down payment", "Robtex": "road tax", "format": "form", "anda": "yang ada",
       "get": "guide", "E": "A", "empat": "4", "toll,": "tol,", "Yang": "Yang"}
HL = {"monthly", "instalment", "instalment.", "salah.", "4", "kos", "sebenar", "down", "payment", "tahun",
      "service", "wear", "and", "tear", "tear.", "10,000", "km", "standby", "road", "tax", "insurance.",
      "renew", "terbeban", "expenses.", "minyak,", "tol,", "kira", "planning", "form", "bawah,", "A", "Z."}
START, END = 9.40, 55.45
toks = []
i = 0
while i < len(words):
    w = words[i]; t = w["w"].strip(); s = w["s"]
    if t == "10" and i + 1 < len(words) and words[i + 1]["w"].strip() == ",000":
        t = "10,000"; i += 1
    t = FIX.get(t, t)
    for k, part in enumerate(t.split(" ")):
        toks.append({"t": part, "s": round(s + k * 0.12, 2)})
    i += 1
toks = [x for x in toks if START <= x["s"] < END]
for j, x in enumerate(toks):
    x["e"] = toks[j + 1]["s"] if j + 1 < len(toks) else x["s"] + 0.6
    x["h"] = 1 if re.sub(r"[^\w,.]", "", x["t"]).lower() in {h.lower() for h in HL} else 0
# Hand-picked phrase breaks (token counts per caption line)
PHRASES = """So, hari ni saya nak share | dengan korang | 4 kos sebenar | yang korang kena fikir | sebelum beli kereta.
| Yang pertama adalah | monthly instalment. | Ianya bergantung kepada | berapa bajet down payment korang
| dan berapa tahun | korang ikat pinjaman tu | dengan pihak bank.
| Yang kedua adalah | service dan juga | wear and tear. | Yang ini regular service | korang setiap 10,000 km
| dan juga wear and tear | yang korang kena standby | in case kalau apa -apa | berlaku dekat kereta.
| Yang ketiga adalah | road tax dan juga insurance. | Benda ni korang kena | renew setiap tahun tahu.
| So, jangan sampai tahap | korang terbeban | bila korang nak renew benda tu.
| Dan yang terakhir adalah | expenses. | Duit minyak, | duit tol, | semua benda tu pun | korang kena kira juga.
| Kalau korang kat luar sana | yang mana ada planning | nak cari kereta"""
groups, k = [], 0
for ph in PHRASES.replace("\n", " ").split("|"):
    n = len(ph.split())
    cur = toks[k:k + n]; k += n
    exp = [w.strip() for w in ph.split()]
    assert [c["t"] for c in cur] == exp, (exp, [c["t"] for c in cur])
    for j in range(len(cur) - 1, 0, -1):  # "apa -apa" -> "apa-apa"
        if cur[j]["t"] == "-apa":
            cur[j - 1]["t"] += "-apa"; cur[j - 1]["e"] = cur[j]["e"]; del cur[j]
    groups.append({"s": cur[0]["s"], "e": min(cur[-1]["e"], cur[-1]["s"] + 0.9), "w": cur})
assert k == len(toks), (k, len(toks))
for g in groups:
    print(f'{g["s"]:6.2f}-{g["e"]:6.2f}  ' + " ".join(("*" + y["t"] + "*") if y["h"] else y["t"] for y in g["w"]))
open(sys.argv[2], "w").write("window.CAPTIONS = " + json.dumps(groups, ensure_ascii=False) + ";\n")
