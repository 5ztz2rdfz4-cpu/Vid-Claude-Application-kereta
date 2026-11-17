# Salam Automobile — Saga MC3: 4AT vs CVT (TikTok 9:16)

Video infografik 2D (HyperFrames + GSAP), 1080×1920, 30fps, 60s.

**Output:** `out/salam-automobile-saga-mc3.mp4` · cover: `out/cover.jpg`

## Struktur
| Masa | Babak |
|---|---|
| 0–5.3s | Hook: "Korang tahu tak, SAGA MC3 ada 2 jenis gear… BERBEZA!" |
| 5.3–19s | 3 varian → Standard/Executive = 4AT, Premium = CVT |
| 19–24s | VS: mana satu lagi bagus? |
| 24–27.5s | Bergantung pada cara pemanduan |
| 27.5–36s | 01 Kaki Lenjan → Gear 4AT (Standard / Executive) |
| 36–44s | 02 Bawa Santai → Gear CVT (Premium) |
| 44–52.8s | CTA: ISI FORM DI BAWAH |
| 52.8–60s | Closing logo Salam Automobile — "Kami guide anda dari A hingga Z" |

## Bina semula
```bash
npm install
python3 scripts/build_html.py            # source/index.template.html + assets/captions.json -> index.html
python3 scripts/make_audio.py assets/audio/vo_edit.wav /tmp/audio   # muzik + SFX + mix
scripts/master_audio.sh /tmp/audio/final_premaster.wav assets/audio/final_mix.wav
npx hyperframes render . -o out/salam-automobile-saga-mc3.mp4 --fps 30 --quality delivery
```
Voiceover asal (IMG_9984.MOV) dipotong 66.9s → 58.3s: buang "Haa, jadi", ayat tersasul
"which is Saga eksekutif ataupun Saga standard", dan jeda panjang. Muzik & SFX disintesis sendiri (bebas hak cipta).
