"""Word timestamps for the edited VO, written as tools/vo_timing.json.

Each kept phrase is transcribed on its own (faster-whisper medium) and placed with the exact
segment map from edit_vo.py, so words cannot drift across the cuts.
usage: python3 -I align_words.py <vo.wav> <segmap.json> <out.json>
"""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
segmap = json.load(open(sys.argv[2]))
m = WhisperModel("medium", device="cpu", compute_type="int8")
PAD = 0.5
# canonical script per kept segment (same order as KEEP in edit_vo.py) — subtitles use these spellings
SCRIPT = [
    "Korang teringin nak pakai kereta baru tapi gaji korang dalam range RM1,800 hingga RM2,000.",
    "Ini tiga model kereta baru yang sesuai dengan korang.",
    "Model yang pertama,",
    "Proton Saga MC3.",
    "Bulanan serendah,",
    "RM423.",
    "Model kedua,",
    "Perodua Axia.",
    "Bulanan serendah,",
    "RM455.",
    "Model yang ketiga,",
    "Perodua Bezza.",
    "Bulanan serendah,",
    "RM415.",
    "Jadi korang nak tahu mana satu yang lebih sesuai untuk kegunaan",
    "dan gaji korang.",
    "Tunggu apa lagi,",
    "isi form yang ada di bawah sekarang.",
    "Kita akan bantu guide dan assist korang dari A",
    "sampai Z.",
]
assert len(SCRIPT) == len(segmap)
words = []
for si, sg in enumerate(segmap):
    s, e = sg["new"]
    c0 = max(0, s - 0.04)
    clip = a[int(c0 * 16000):int((e + 0.04) * 16000)]
    clip = np.concatenate([np.zeros(int(PAD * 16000), np.float32), clip, np.zeros(int(PAD * 16000), np.float32)])
    r, _ = m.transcribe(clip, language="ms", word_timestamps=True, beam_size=5, condition_on_previous_text=False,
                        initial_prompt="Proton Saga, Perodua Axia, Perodua Bezza, RM423, RM455, RM415, RM1,800.")
    ws = []
    for x in r:
        for w in x.words:
            t = w.word.strip()
            if t.startswith(",") and ws:          # "RM1" ",800" -> one token
                ws[-1] = (ws[-1][0] + t, ws[-1][1], w.end)
            else:
                ws.append((t, w.start, w.end))
    times = [(min(max(c0 - PAD + a_, s), e), min(max(c0 - PAD + b_, s), e + 0.05)) for _, a_, b_ in ws]
    canon = SCRIPT[si].split()
    if len(times) >= len(canon):
        times = times[:len(canon)]
    else:  # spread the canonical words over the heard span by length
        t0, t1 = (times[0][0], times[-1][1]) if times else (s, e)
        L = sum(len(c) + 1 for c in canon)
        acc, times = 0, []
        for c in canon:
            a_ = t0 + (t1 - t0) * acc / L
            acc += len(c) + 1
            times.append((a_, t0 + (t1 - t0) * acc / L))
    times[0] = (s, times[0][1])
    for c, (a_, b_) in zip(canon, times):
        words.append({"w": c, "s": round(a_, 3), "e": round(max(b_, a_ + 0.05), 3)})
    print(f"{s:6.2f}-{e:6.2f}: heard: {' '.join(t for t, _, _ in ws)}", flush=True)
json.dump({"duration": round(len(a) / 16000, 3), "words": words}, open(sys.argv[3], "w"), indent=1, ensure_ascii=False)
