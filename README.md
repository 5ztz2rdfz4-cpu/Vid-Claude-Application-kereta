# Vid-Claude-Application-kereta

TikTok edit (HyperFrames) — **"Loan kereta kena reject? 3 benda wajib tahu"**

- Final video: `tiktok-loan-kereta/renders/loan-kereta-tiktok.mp4` (1080x1920, 30fps, 69.5s, -14 LUFS)
- Project HyperFrames: `tiktok-loan-kereta/`
  - `index.html` — root (video talking-head + punch-in jump cut + SFX)
  - `compositions/` — hook, tip1, tip2, tip3, cta, captions
  - `tools/build.py` — generator semua composition (ubah teks/timing di sini, kemudian `python3 tools/build.py`)
  - `assets/talk.mp4` — footage asal yang dah dipotong (buang jeda & filler) + tonemap HDR→SDR

Render semula:

```bash
cd tiktok-loan-kereta
python3 tools/build.py
npx hyperframes@0.9.52 check
npx hyperframes@0.9.52 render -o renders/loan-kereta-tiktok.mp4
```
