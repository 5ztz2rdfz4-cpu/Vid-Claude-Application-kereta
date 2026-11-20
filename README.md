# Saga MC3 — 4AT vs CVT (TikTok edit)

Video TikTok 9:16 (1080x1920, 30fps, ~50s) yang diedit dengan [HyperFrames](https://hyperframes.heygen.com).

- **Video siap:** `output/saga-mc3-4at-vs-cvt-tiktok.mp4`
- **Projek HyperFrames:** `hyperframes-project/`

## Apa yang dibuat
| Masa | Bahagian | Isi |
|---|---|---|
| 0.0–2.5s | Hook | Punch-zoom, tajuk "SAGA MC3 — GEAR TAK SAMA?!", sticker "JANGAN SALAH PILIH!" |
| 2.5–5.1s | B-roll | Gambar Saga (Ken Burns) + "4AT VS CVT" |
| 5.1–10s | 01 Infografik | 3 spek: Standard / Executive / Premium (kamera jadi PiP) |
| 10–23.3s | 02 Infografik | Kad perbandingan 4AT (Standard & Executive) vs CVT (Premium) |
| 23.3–29s | Talking head | "Mana satu lagi bagus?" → "Ikut cara pemanduan korang" |
| 29–39.4s | 03 Infografik | Kaki lenjan → 4AT, Santai & rilek → CVT, meter gaya pemanduan |
| 39.4–47.3s | CTA | "Isi form di bawah", "Kami bantu dari A sampai Z" |
| 47.3–50s | End card | FOLLOW + simpan & share |

- Scene dibuang: jeda panjang, "baik" pada 6s, ayat berulang ("jadi kalau korang kat luar sana yang nak tahu…"), dan diam 4 saat di hujung (57s → 47s).
- Audio suara dibersihkan (high-pass, denoise, compressor, loudnorm -16 LUFS).
- Caption perkataan-demi-perkataan dengan highlight kuning (gaya rujukan).
- Muzik latar & SFX (whoosh, pop, stamp, riser, impact, ding) dijana sendiri dengan `tools/synth_audio.py`, jadi bebas hak cipta.

## Render semula
```bash
cd hyperframes-project
python3 src/build.py          # jana index.html daripada src/template.html.tpl + transcript.json
npx hyperframes@0.9.71 render -q delivery -o ../output/saga-mc3-4at-vs-cvt-tiktok.mp4
```
Untuk tukar teks caption, edit `transcript.json` (perkataan + masa), kemudian jalankan `build.py` semula.
