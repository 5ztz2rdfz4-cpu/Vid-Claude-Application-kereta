"""Tighten the voiceover: shorten long pauses, remap word timestamps.

usage: python3 -I edit_vo.py <vo_clean48.wav> <transcript.json> <out.wav> <out_timing.json>
"""
import json
import sys
import wave

import numpy as np

src, tx_path, out_wav, out_json = sys.argv[1:5]

VO_OFFSET = 0.30  # VO starts this many seconds into the film (hook car whoosh first)

wf = wave.open(src)
sr = wf.getframerate()
a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768

# --- find quiet regions (20 ms RMS, relative threshold) ---
h = int(sr * 0.02)
n = len(a) // h
rms = np.array([np.sqrt(np.mean(a[i * h:(i + 1) * h] ** 2)) + 1e-9 for i in range(n)])
db = 20 * np.log10(rms)
thr = np.percentile(db, 10) + 8
low = db < thr
quiet = []
i = 0
while i < n:
    if low[i]:
        j = i
        while j < n and low[j]:
            j += 1
        quiet.append((i * 0.02, j * 0.02))
        i = j
    else:
        i += 1

# section boundaries (original seconds) keep a bit more air for the scene change
BOUNDARIES = [7.6, 11.6, 19.9, 27.4, 35.3, 41.5]
segments = []  # (orig_start, orig_end) of kept audio
cursor = 0.0
for qs, qe in quiet:
    dur = qe - qs
    if dur < 0.26:
        continue
    is_boundary = any(qs - 0.1 <= b <= qe + 0.1 for b in BOUNDARIES)
    keep = 0.34 if is_boundary else 0.20
    if qs < 0.05:  # leading silence: drop it almost entirely
        cursor = max(cursor, qe - 0.04)
        continue
    if qe > len(a) / sr - 0.05:  # trailing silence
        segments.append((cursor, qs + 0.15))
        cursor = None
        break
    if dur <= keep:
        continue
    cut_s = qs + keep / 2
    cut_e = qe - keep / 2
    segments.append((cursor, cut_s))
    cursor = cut_e
if cursor is not None:
    segments.append((cursor, len(a) / sr))

# --- assemble with short crossfades ---
xf = int(sr * 0.012)
out = np.zeros(0, dtype=np.float32)
for s, e in segments:
    seg = a[int(s * sr):int(e * sr)].copy()
    if len(out) and len(seg) > xf:
        ramp = np.linspace(0, 1, xf, dtype=np.float32)
        out[-xf:] = out[-xf:] * (1 - ramp) + seg[:xf] * ramp
        seg = seg[xf:]
    out = np.concatenate([out, seg])
# fade tail
ft = int(sr * 0.08)
out[-ft:] *= np.linspace(1, 0, ft)

# --- time map orig -> edited ---
def remap(t):
    acc = 0.0
    for k, (s, e) in enumerate(segments):
        if t < s:
            return acc
        if t <= e:
            return acc + (t - s)
        acc += (e - s) - (xf / sr if k > 0 else 0)
    return acc

tx = json.load(open(tx_path))
words = []
for seg in tx:
    for w in seg["words"]:
        words.append({"w": w["w"].strip(), "s": round(remap(w["s"]) + VO_OFFSET, 3), "e": round(remap(w["e"]) + VO_OFFSET, 3)})

pad = np.zeros(int(VO_OFFSET * sr), dtype=np.float32)
out = np.concatenate([pad, out])
pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
ow = wave.open(out_wav, "wb")
ow.setnchannels(1)
ow.setsampwidth(2)
ow.setframerate(sr)
ow.writeframes(pcm.tobytes())
ow.close()

json.dump({"duration": round(len(out) / sr, 3), "segments": segments, "words": words}, open(out_json, "w"), indent=1)
print("segments:", len(segments), "orig", round(len(a) / sr, 2), "-> edited", round(len(out) / sr, 2))
