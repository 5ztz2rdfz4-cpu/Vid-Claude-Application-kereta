# Salam Automobile — "4 Kos Sebenar Miliki Kereta" (TikTok, 1080×1920)

Video infografik 2D dibina dengan [HyperFrames](https://hyperframes.heygen.com) (HTML + GSAP → MP4).

- `index.html` — komposisi utama (hook, intro 4 kos, Kos 01–04, CTA, closing logo)
- `assets/cues.js` — masa setiap cue (dijana dari `tools/cues.json`)
- `assets/captions.js` — kapsyen perkataan demi perkataan (dari `tools/build_captions.py`)
- `assets/audio/vo.wav` — voiceover asal yang dipotong & dibersihkan (69s → 60s)
- `assets/audio/mix.wav` — mix akhir: VO + muzik latar + SFX (semua muzik/SFX disintesis sendiri, bebas royalti), -14 LUFS
- `out/` — MP4 siap untuk TikTok

## Bina semula
```bash
npm install
python3 tools/cut_vo.py <vo_asal.wav> vo_cut.wav vo_map.json      # potong jeda
python3 tools/build_captions.py tools/transcript_vo.json assets/captions.js
python3 tools/make_audio.py tools/cues.json assets/audio/vo.wav mix_raw.wav   # lalu loudnorm -14 LUFS
npx hyperframes check
npx hyperframes render -f 30 -q high -o out/salam-automobile-4-kos-kereta.mp4
```
