"""Writes the sound-effect <audio> clips into index.html between the SFX markers."""
SFX = [
    ("whoosh", 0.0, .55), ("pop", 0.1, .55), ("click", 1.8, .6), ("pop", 2.9, .5), ("riser", 2.35, .3), ("pop", 4.3, .45),
    ("pop", 5.2, .5), ("buzz", 5.45, .32), ("pop", 6.25, .5), ("buzz", 6.5, .32),
    ("riser", 6.95, .5), ("impact", 7.78, .8), ("shimmer", 7.85, .35),
    ("whoosh", 8.75, .55), ("pop", 9.3, .45), ("stamp", 10.5, .5), ("pop", 11.65, .45), ("ding", 14.3, .35), ("stamp", 15.9, .55),
    ("whoosh", 17.5, .55), ("pop", 17.95, .45), ("pop", 20.8, .5), ("ding", 22.55, .35), ("pop", 24.25, .5), ("pop", 25.9, .5),
    ("whoosh", 26.85, .55), ("pop", 27.3, .45), ("pop", 28.35, .5), ("pop", 30.3, .5), ("pop", 32.2, .5),
    ("whoosh", 32.95, .55), ("pop", 33.4, .45), ("click", 34.9, .55), ("ding", 37.25, .32), ("ding", 38.25, .32), ("ding", 39.75, .32),
    ("whoosh", 40.5, .55), ("pop", 40.95, .45), ("riser", 43.4, .3), ("ding", 45.1, .38), ("pop", 46.0, .5), ("ding", 47.8, .32),
    ("whoosh", 49.25, .55), ("pop", 49.7, .45), ("pop", 50.9, .45), ("click", 52.3, .5), ("stamp", 53.85, .45), ("click", 54.85, .7),
    ("whoosh_big", 55.8, .65), ("impact", 56.6, .35), ("shimmer", 56.75, .45), ("pop", 57.62, .5), ("pop", 58.3, .5), ("shimmer", 59.3, .22),
]
SFX += [("tick", 12.65 + i * 0.13, .28) for i in range(12)]
SFX += [("tick", 20.95 + i * 0.12, .25) for i in range(6)]
LEN = dict(whoosh=.7, whoosh_big=1.1, pop=.16, click=.05, tick=.035, ding=1.1, impact=1.4, riser=.9, buzz=.32, shimmer=2.2, stamp=.35)
lines = [f'  <audio id="sfx{i}" src="assets/sfx/{n}.wav" data-start="{t:.3f}" data-duration="{LEN[n]:.3f}" data-volume="{v}" data-track-index="{12 + i % 4}"></audio>'
         for i, (n, t, v) in enumerate(sorted(SFX, key=lambda x: x[1]))]
p = "index.html"; s = open(p).read()
A, B = "<!-- SFX:BEGIN -->", "<!-- SFX:END -->"
if A not in s:
    s = s.replace('  <div id="sfx"></div>', f"  {A}\n  {B}")
s = s[: s.index(A) + len(A)] + "\n" + "\n".join(lines) + "\n  " + s[s.index(B):]
open(p, "w").write(s); print(len(lines), "sfx clips")
