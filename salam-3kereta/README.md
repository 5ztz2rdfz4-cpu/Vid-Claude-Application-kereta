# Salam Automobile — 3 Kereta Baru untuk Gaji RM1.8K

TikTok video (1080×1920, 30 fps, 50.4 s) built with [HyperFrames](https://hyperframes.heygen.com):
2D infographic animation over the original voiceover, ending with the Salam Automobile logo build.

**Final video:** `renders/Salam-Automobile-3-Kereta-Gaji-1.8K.mp4`

## Structure
| Scene | Time | Content |
|---|---|---|
| Hook | 0.0–7.75 | 2D car drive-in, "Teringin pakai KERETA BARU?", salary card RM1,800–RM2,000 |
| Intro | 7.75–11.7 | "3 MODEL KERETA BARU" + three model cards |
| 01 Saga | 11.7–18.8 | Proton Saga MC3 — RM423/bulan (~24% of RM1,800) |
| 02 Axia | 18.8–24.7 | Perodua Axia — RM455/bulan (~25%) |
| 03 Bezza | 24.7–31.7 | Perodua Bezza — RM415/bulan (~23%) |
| Compare | 31.7–37.7 | Monthly bar chart, Kegunaan + Gaji = Pilihan tepat |
| CTA | 37.7–44.7 | "Tunggu apa LAGI?", ISI FORM DI BAWAH button, A→Z guide steps |
| Outro | 44.7–50.4 | Salam Automobile logo build on cream, "Kami guide anda dari A hingga Z" |

## Rebuild
```bash
python3 -I tools/edit_vo.py <vo_clean48.wav> <transcript.json> assets/audio/vo.wav tools/vo_timing.json  # tighten pauses
python3 -I tools/build_timeline.py          # scene times, karaoke phrases, SFX cues
python3 -I tools/make_audio.py assets/audio/vo.wav assets/audio   # synthesized music + SFX (royalty-free)
python3 -I tools/logo_layers.py <logo.png> assets/img              # logo animation layers
npm run check
npx hyperframes render -o renders/out.mp4 -q delivery
```
Music and sound effects are synthesized from scratch in `tools/make_audio.py` (no samples). Font: Montserrat (OFL).
