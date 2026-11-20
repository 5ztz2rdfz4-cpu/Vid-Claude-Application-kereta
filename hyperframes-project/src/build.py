#!/usr/bin/env python3
"""Generate index.html (HyperFrames composition) from transcript.json.

Edited-time timeline (talk.mp4 = 47.3s, end card to 50s):
  0.00  HOOK (full cam)          2.55 B-roll Saga + "4AT vs CVT"
  5.10  01 3 SPEK (PiP)          10.0 02 2 JENIS TRANSMISI (PiP)
  23.30 MANA LAGI BAGUS? (full)  29.10 03 GAYA PEMANDUAN (PiP)
  39.40 CTA (full)               47.30 END CARD
"""
import json, html, pathlib

ROOT = pathlib.Path(__file__).parent.parent
TOTAL = 50.0
TALK = 47.3
words = json.load(open(ROOT / "transcript.json"))

KEY = {"mc3", "saga", "4at", "cvt", "premium", "standard", "executive", "proton saga",
       "3 spek", "transmisi", "bagus?", "simple", "kaki lenjan", "kepuasan", "santai,",
       "rilek,", "form", "sesuai", "z", "pemanduan", "dua", "berbeza"}

# ---------- caption groups ----------
groups, cur = [], []
for i, x in enumerate(words):
    cur.append(x)
    nxt = words[i + 1] if i + 1 < len(words) else None
    brk = (len(cur) >= 3 or nxt is None or nxt["s"] - x["e"] > 0.3
           or x["w"].endswith((",", "?", ".")) or len(" ".join(c["w"] for c in cur)) > 15)
    if brk:
        groups.append(cur); cur = []

cap_html, cap_js = [], []
for gi, g in enumerate(groups):
    gs = g[0]["s"]
    ge = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else min(g[-1]["e"] + 0.4, TALK)
    ge = min(ge, g[-1]["e"] + 0.6) if gi + 1 < len(groups) else ge
    spans = []
    for wi, x in enumerate(g):
        txt = x["w"].strip(",.").upper()
        cls = "w key" if x["w"].lower() in KEY else "w"
        spans.append(f'<span class="{cls}" id="w{gi}_{wi}">{html.escape(txt)}</span>')
        on, off = (('{backgroundColor:"#FFD60A",color:"#0B0B0B",scale:1.05}', '{backgroundColor:"rgba(255,214,10,0)",color:"#FFD60A",scale:1}')
                   if "key" in cls else ('{color:"#FFD60A",scale:1.05}', '{color:"#FFFFFF",scale:1}'))
        cap_js.append(f'tl.set("#w{gi}_{wi}",{on},{x["s"]:.2f});')
        cap_js.append(f'tl.set("#w{gi}_{wi}",{off},{min(x["e"]+0.05, ge):.2f});')
    cap_html.append(f'<div class="cg" id="g{gi}">{" ".join(spans)}</div>')
    cap_js.append(f'tl.set("#g{gi}",{{autoAlpha:1}},{gs:.2f});'
                  f'tl.fromTo("#g{gi}",{{scale:0.8,y:24}},{{scale:1,y:0,duration:0.16,ease:"back.out(2.5)"}},{gs:.2f});'
                  f'tl.set("#g{gi}",{{autoAlpha:0}},{ge:.2f});')

# ---------- sfx ----------
SFX = [
    ("impact", 0.00, 0.55), ("whoosh", 0.05, 0.5), ("pop", 0.95, 0.6),
    ("whoosh", 2.40, 0.6), ("stamp", 3.38, 0.5), ("swish", 4.95, 0.5),
    ("tick", 7.74, 0.7), ("tick", 8.72, 0.7), ("pop", 9.74, 0.6),
    ("whoosh", 9.95, 0.5), ("pop", 11.50, 0.6),
    ("tick", 16.82, 0.7), ("tick", 17.38, 0.7), ("riser", 17.68, 0.35), ("stamp", 19.28, 0.6),
    ("tick", 21.22, 0.7), ("stamp", 22.84, 0.6),
    ("whoosh", 23.20, 0.5), ("pop", 23.40, 0.5), ("riser", 24.86, 0.3), ("ding", 26.46, 0.45),
    ("whoosh", 29.00, 0.5), ("pop", 29.70, 0.55), ("swish", 31.05, 0.5), ("stamp", 33.34, 0.6),
    ("pop", 34.40, 0.55), ("swish", 35.95, 0.5), ("stamp", 38.90, 0.6), ("ding", 39.00, 0.3),
    ("whoosh", 39.30, 0.5), ("pop", 39.60, 0.5), ("impact", 43.00, 0.35), ("pop", 43.05, 0.5),
    ("whoosh", 47.20, 0.6), ("impact", 47.35, 0.6), ("ding", 48.30, 0.35),
]
sfx_html = "\n".join(
    f'<audio id="sfx{i}" src="assets/sfx/{n}.wav" data-start="{t:.2f}" data-duration="{ {"riser":1.6,"impact":1.4,"ding":1.2,"whoosh":0.6}.get(n,0.4) }" '
    f'data-volume="{v}" data-track-index="{3 + i % 3}"></audio>'
    for i, (n, t, v) in enumerate(SFX))

tpl = (ROOT / "src" / "template.html.tpl").read_text()
out = (tpl.replace("{{CAPTIONS}}", "\n".join(cap_html))
          .replace("{{CAPTION_JS}}", "\n".join(cap_js))
          .replace("{{SFX}}", sfx_html)
          .replace("{{TOTAL}}", str(TOTAL))
          .replace("{{TALK}}", str(TALK)))
(ROOT / "index.html").write_text(out)
print(f"groups={len(groups)} sfx={len(SFX)}")
