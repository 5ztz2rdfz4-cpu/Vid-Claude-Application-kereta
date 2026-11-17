"""Tight voiceover edit: keep only the spoken phrases (VAD segments), drop repeated/dragging bits,
re-space the pauses, and speed the read up slightly.

usage: python3 -I edit_vo.py <vo_clean48.wav> <out.wav> <segmap.json>

Segment times are in the ORIGINAL recording (IMG_0036.MOV), found with Silero VAD and checked
by transcribing each segment on its own.
"""
import subprocess
import sys
import tempfile
import wave

import numpy as np

src, out_wav, map_path = sys.argv[1:4]
import json
VO_OFFSET = 0.25   # seconds of air before the first word (hook car whoosh plays here)
TEMPO = 1.05       # gentle speed-up, pitch preserved (ffmpeg atempo)

# (start, end, pause_after) — pause_after is the silence inserted after this phrase
KEEP = [
    (0.24, 7.32, 0.30),    # Korang teringin nak pakai kereta baru tapi gaji korang dalam range RM1,800 hingga RM2,000
    (7.88, 11.38, 0.30),   # Ini tiga model kereta baru yang sesuai dengan korang
    (11.95, 13.01, 0.14),  # Model yang pertama
    (13.48, 14.74, 0.18),  # Proton Saga MC3
    (15.18, 16.24, 0.10),  # Bulanan serendah
    (16.56, 18.36, 0.50),  # RM423            (dropped: "sebulan" 18.60-19.16 + 0.95 s drag)
    (20.11, 21.08, 0.12),  # Model kedua
    (21.52, 22.32, 0.18),  # Perodua Axia
    (22.89, 23.86, 0.10),  # Bulanan serendah
    (24.30, 26.23, 0.50),  # RM455            (dropped: "sebulan" 26.60-27.12 + 0.8 s drag)
    (27.92, 28.98, 0.12),  # Model yang ketiga
    (29.52, 30.32, 0.18),  # Perodua Bezza
    (30.73, 31.86, 0.10),  # Bulanan serendah
    (32.20, 34.20, 0.55),  # RM415            (dropped: "sebulan" 34.48-35.00 + 0.6 s drag)
    (35.63, 39.385, 0.0),  # Jadi korang nak tahu mana satu yang lebih sesuai untuk kegunaan
    (39.99, 41.30, 0.28),  # dan gaji korang  (dropped: repeated "korang" 39.385-39.99)
    (41.74, 42.55, 0.14),  # Tunggu apa lagi
    (42.89, 44.95, 0.10),  # isi form yang ada di bawah sekarang
    (45.07, 47.96, 0.10),  # kita akan bantu guide dan assist korang daripada A
    (48.27, 48.82, 0.0),   # sampai Z
]
PRE, POST = 0.035, 0.06    # breathing room around each VAD segment edge (soft onsets / tails)

wf = wave.open(src)
sr = wf.getframerate()
a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768

xf = int(sr * 0.010)
pieces = []
segmap = []
pos = 0.0
for k, (s, e, gap) in enumerate(KEEP):
    # hard word-splice (gap 0 and contiguous) gets no extra padding
    s_pad = 0 if (k > 0 and KEEP[k - 1][2] == 0.0) else PRE
    e_pad = 0 if gap == 0.0 and k < len(KEEP) - 1 else POST
    seg = a[int((s - s_pad) * sr):int((e + e_pad) * sr)].copy()
    f = min(xf, len(seg) // 4)
    seg[:f] *= np.linspace(0, 1, f)
    seg[-f:] *= np.linspace(1, 0, f)
    pieces.append(seg)
    segmap.append({"orig": [s, e], "new": [pos + s_pad, pos + len(seg) / sr - e_pad]})
    pos += len(seg) / sr
    if gap > 0:
        pieces.append(np.zeros(int(gap * sr), dtype=np.float32))
        pos += int(gap * sr) / sr
out = np.concatenate(pieces)

# tempo (pitch-preserving) via ffmpeg atempo
with tempfile.TemporaryDirectory() as td:
    p_in, p_out = f"{td}/in.wav", f"{td}/out.wav"
    w = wave.open(p_in, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p_in, "-af", f"atempo={TEMPO}", "-ar", str(sr), p_out], check=True)
    w = wave.open(p_out)
    out = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768

out = np.concatenate([np.zeros(int(VO_OFFSET * sr), dtype=np.float32), out, np.zeros(int(0.05 * sr), dtype=np.float32)])
ow = wave.open(out_wav, "wb"); ow.setnchannels(1); ow.setsampwidth(2); ow.setframerate(sr)
ow.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes()); ow.close()
for m in segmap:
    m["new"] = [round(VO_OFFSET + t / TEMPO, 3) for t in m["new"]]
json.dump(segmap, open(map_path, "w"), indent=1)
print("edited VO:", round(len(out) / sr, 2), "s")
