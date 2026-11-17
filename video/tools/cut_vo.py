"""Shrink long pauses in the voiceover and write a time map.
usage: cut_vo.py in.wav out.wav map.json"""
import sys, json, numpy as np, soundfile as sf
src, dst, mapf = sys.argv[1:4]
a, sr = sf.read(src)
# (gap_start, gap_end, seconds_to_keep) in original time
GAPS = [
    (9.50, 10.30, 0.18), (14.95, 15.30, 0.10), (16.55, 17.12, 0.15),
    (19.25, 19.95, 0.18), (26.00, 26.50, 0.15), (33.05, 33.45, 0.12),
    (40.00, 40.60, 0.18), (43.32, 43.76, 0.15), (49.35, 49.85, 0.15),
    (51.50, 51.90, 0.12), (52.75, 53.95, 0.20), (54.75, 55.10, 0.15),
    (58.32, 59.52, 0.22), (63.30, 63.95, 0.18),
]
XF = int(0.02 * sr)
segs, t = [], 0.0
for g0, g1, keep in GAPS:
    segs.append((t, g0 + keep / 2)); t = g1 - keep / 2
segs.append((t, len(a) / sr - 0.2))
out, m, now = [], [], 0.0
for s0, s1 in segs:
    chunk = a[int(s0 * sr):int(s1 * sr)].copy()
    if out:  # equal-power crossfade with previous chunk
        prev = out[-1]
        f = np.linspace(0, 1, XF)[:, None]
        prev[-XF:] = prev[-XF:] * np.cos(f * np.pi / 2) + chunk[:XF] * np.sin(f * np.pi / 2)
        chunk = chunk[XF:]
        s0 += XF / sr
    m.append({"o0": s0, "o1": s1, "n0": now})
    now += (s1 - s0)
    out.append(chunk)
y = np.concatenate(out)
sf.write(dst, y, sr, subtype="PCM_24")
json.dump(m, open(mapf, "w"), indent=1)
print(f"in {len(a)/sr:.2f}s -> out {len(y)/sr:.2f}s")
