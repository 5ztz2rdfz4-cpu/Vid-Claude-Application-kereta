# TikTok: 3 Benda Wajib Tahu Sebelum Beli First Car

HyperFrames project for the TikTok edit of `IMG_7473.MOV` (Google Drive).

## Edit summary
- **Hook (0–3.8s):** cold open with the strongest line ("Gaji RM1,700 nak pakai S70?") + red "JANGAN!" stamp, flash into the title.
- **Cuts:** 97s raw → ~88s. Removed "ok" fillers, dead pauses, the repeated "dia cost, lepas tu kita pecahkan lagi kepada empat", "Itu yang kedua", and "bak kata pepatah, orang tua-tua kata apa".
- **B-roll = infographics:** camera shrinks into a picture-in-picture while animated cards play (kegunaan, 4 jenis kereta, 4 kos sebenar, Saga A→B, checklist).
- **Captions:** word-by-word, active word highlighted yellow. Jump-cut punch-ins, SFX (whoosh/pop/thud/ding), top progress bar, CTA + end card.

## Rebuild / render
The source clip is too large for git. To rebuild: convert the HDR iPhone clip to a 1080x1920 SDR file at
`assets/video/aroll.mp4` (see the ffmpeg command in `build/README-source.txt`), then:

```bash
python3 build/build.py            # regenerates index.html from build/template.html
npx hyperframes@0.9.56 check
npx hyperframes@0.9.56 render -o out.mp4 --quality delivery
```

Edit timing in `SEGMENTS` (source seconds) and graphics/text in `build/build.py`.
