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
FIX = {"ProDua": "Perodua", "3": "tiga"}
words = []
for w in vo["words"]:
    t = FIX.get(w["w"], w["w"])
    if t.startswith(",") and words:
        words[-1]["w"] += t
        words[-1]["e"] = w["e"]
        continue
    words.append({"w": t, "s": w["s"], "e": w["e"]})

# ---- snap word starts onto real voice onsets (whisper stretches words over the silence before them) ----
import wave
import numpy as np
_wf = wave.open(os.path.join(ROOT, "assets", "audio", "vo.wav"))
_sr = _wf.getframerate()
_a = np.frombuffer(_wf.readframes(_wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768
_h = int(_sr * 0.01)
_n = len(_a) // _h
_db = 20 * np.log10(np.sqrt((_a[: _n * _h].reshape(_n, _h) ** 2).mean(1)) + 1e-9)
def _is_silent(t):
    i = int(t / 0.01)
    return 0 <= i < _n and _db[i] < -50
for w in words:
    t = w["s"]
    if _is_silent(t):
        while t < w["e"] and _is_silent(t):
            t += 0.01
        w["s"] = round(t, 3)
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

# ---- scenes (derived from the voice) ----
def model_start(n):
    return at("model", n) - 0.2

VO_END = max(w["e"] for w in words)
T = {
    "hook": 0.0,
    "intro": round(at("ini") - 0.22, 2),
    "saga": round(at("model", 2) - 0.2, 2),   # "model" #1 is in the intro line ("tiga model kereta")
    "axia": round(at("model", 3) - 0.2, 2),
    "bezza": round(at("model", 4) - 0.2, 2),
    "compare": round(at("jadi") - 0.2, 2),
    "cta": round(at("tunggu") - 0.2, 2),
    "outro": round(VO_END + 0.3, 2),
}
T["end"] = round(T["outro"] + 5.7, 2)

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
    "axiaKedua": at("kedua"),
    "axia": at("perodua", 1),
    "axiaBulanan": at("bulanan", 2),
    "rm455": at("rm455"),
    "bezzaKetiga": at("ketiga"),
    "bezza": at("perodua", 2),
    "bezzaBulanan": at("bulanan", 3),
    "rm415": at("rm415"),
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
# the read no longer says "sebulan": the salary ring fills just after the price lands
for _m, _rm in (("saga", "rm423"), ("axia", "rm455"), ("bezza", "rm415")):
    B[_m + "Sebulan"] = B[_rm] + 0.9
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
# ---- write the timing into index.html (data-start / data-duration) ----
import re
o = T["outro"]
LAYOUT = {
    "root": (0, T["end"]),
    "a-vo": (0, vo["duration"]),
    "a-music": (0, T["end"]),
    "a-sfx": (0, T["end"]),
    "bg": (0, o + 0.6),
    "s-hook": (0, T["intro"] + 0.3),
    "s-intro": (T["intro"], T["saga"] - T["intro"] + 0.3),
    "s-saga": (T["saga"], T["axia"] - T["saga"] + 0.3),
    "s-axia": (T["axia"], T["bezza"] - T["axia"] + 0.3),
    "s-bezza": (T["bezza"], T["compare"] - T["bezza"] + 0.3),
    "s-compare": (T["compare"], T["cta"] - T["compare"] + 0.3),
    "s-cta": (T["cta"], o - T["cta"] + 0.35),
    "brand": (T["intro"], o - T["intro"] + 0.15),
    "subs": (0, o + 0.05),
    "fx": (0, o + 0.5),
    "iris": (o - 0.45, 1.2),
    "s-outro": (o, T["end"] - o),
}
html_path = os.path.join(ROOT, "index.html")
html = open(html_path).read()
for el, (st, du) in LAYOUT.items():
    pat = re.compile(r'(<[a-z]+ id="%s"[^>]*?data-start=")[^"]*("[^>]*?data-duration=")[^"]*(")' % re.escape(el))
    html, n = pat.subn(lambda m: f"{m.group(1)}{round(st, 3)}{m.group(2)}{round(du, 3)}{m.group(3)}", html)
    assert n == 1, el
open(html_path, "w").write(html)
print("T", T)
print(json.dumps(B, indent=0))
print(len(ph_out), "phrases;", len(cues), "cues")
for p in ph_out:
    print(f'{p["s"]:6.2f}-{p["e"]:6.2f}', " ".join(w["t"] for w in p["w"]))
