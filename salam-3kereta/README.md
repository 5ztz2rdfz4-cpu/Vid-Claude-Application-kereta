# Salam Automobile — 3 Kereta Baru untuk Gaji RM1.8K

TikTok video (1080×1920, 30 fps, 46.8 s) built with [HyperFrames](https://hyperframes.heygen.com):
2D infographic animation over the original voiceover, ending with the Salam Automobile logo build.

**Final video:** `renders/Salam-Automobile-3-Kereta-Gaji-1.8K.mp4`

## Structure
| Scene | Time | Content |
|---|---|---|
| Hook | 0.0–7.2 | 2D car drive-in, "Teringin pakai KERETA BARU?", salary card RM1,800–RM2,000 |
| Intro | 7.2–10.9 | "3 MODEL KERETA BARU" + three model cards |
| 01 Saga | 10.9–17.1 | Proton Saga MC3 — RM423/bulan (~24% of RM1,800) |
| 02 Axia | 17.1–22.8 | Perodua Axia — RM455/bulan (~25%) |
| 03 Bezza | 22.8–28.8 | Perodua Bezza — RM415/bulan (~23%) |
| Compare | 28.8–34.0 | Monthly bar chart, Kegunaan + Gaji = Pilihan tepat |
| CTA | 34.0–41.1 | "Tunggu apa LAGI?", ISI FORM DI BAWAH button, A→Z guide steps |
| Outro | 41.1–46.8 | Salam Automobile logo build on cream, "Kami guide anda dari A hingga Z" |

Voiceover edit (`tools/edit_vo.py`): only the spoken phrases are kept (Silero VAD segments), the
repeated "…sebulan" after each price and the repeated "korang" in "kegunaan korang dan gaji korang"
are removed, every pause is re-spaced (0.10–0.55 s), and the read is sped up 1.05× (pitch kept).

## Rebuild
```bash
python3 -I tools/edit_vo.py <vo_clean48.wav> assets/audio/vo.wav tools/segmap.json   # cut & re-space the read
python3 -I tools/align_words.py assets/audio/vo.wav tools/segmap.json tools/vo_timing.json  # word timings
python3 -I tools/build_timeline.py          # scene times (written into index.html), karaoke, SFX cues
python3 -I tools/make_audio.py assets/audio/vo.wav assets/audio   # synthesized music + SFX (royalty-free)
python3 -I tools/logo_layers.py <logo.png> assets/img              # logo animation layers
npm run check
npx hyperframes render -o renders/out.mp4 -q delivery
```
Music and sound effects are synthesized from scratch in `tools/make_audio.py` (no samples). Font: Montserrat (OFL).
