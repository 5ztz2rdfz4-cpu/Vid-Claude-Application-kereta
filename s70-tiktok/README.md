# Proton S70 MC2 – TikTok edit (HyperFrames)

Video jualan 1080×1920, 30 fps, ~28.6 s, dibina dengan [HyperFrames](https://hyperframes.heygen.com).

## Struktur suntingan

| Masa (s) | Sumber | Isi |
| --- | --- | --- |
| 0.0 – 7.6 | IMG_5090 8.15–15.75 | **Hook**: "Minimum kelaikan gaji bersih RM2,300 sahaja, kita dah boleh bantu korang bawa balik kereta ni". B-roll grille + teks besar RM2,300 dari frame pertama. |
| 7.6 – 20.6 | IMG_5089 0.12–13.15 | Spec: Proton S70 MC2, enjin 1.5 NA, gearbox CVT, "S70 Rahmah". B-roll logo & bonet + kad spec. |
| 20.6 – 28.6 | IMG_5090 15.98–23.95 | CTA: "isi form kat bawah… kita guide korang A sampai Z". |

Dibuang: bahagian "dah official launching" (IMG_5089 13.3–15.5 s), ayat-ayat berulang dari take pertama, dan hujung klip yang kamera bergerak.

## Cara render semula

Video sumber (`assets/take5089.mp4`, `take5090.mp4`, `broll_*.mp4`) tidak di-commit kerana saiznya besar.
Ia dijana daripada fail asal Google Drive (IMG_5089.MOV, IMG_5090.MOV) dengan ffmpeg:

```bash
E="-c:v libx264 -preset medium -crf 17 -g 15 -pix_fmt yuv420p"
ffmpeg -i IMG_5089.MOV -vf "scale=1080:1920:flags=lanczos,fps=30" $E -c:a aac -b:a 192k assets/take5089.mp4
ffmpeg -i IMG_5090.MOV -vf "scale=1080:1920:flags=lanczos,fps=30" $E -c:a aac -b:a 192k assets/take5090.mp4
ffmpeg -ss 7 -t 4 -i IMG_5089.MOV -an -vf "crop=1040:1849:0:1780,scale=1080:1920,fps=30" $E assets/broll_front.mp4
ffmpeg -ss 4 -t 4 -i IMG_5089.MOV -an -vf "crop=720:1280:400:1800,scale=1080:1920,fps=30" $E assets/broll_badge.mp4
ffmpeg -ss 9 -t 4 -i IMG_5089.MOV -an -vf "crop=1000:1778:0:1100,scale=1080:1920,fps=30" $E assets/broll_hood.mp4
```

Kemudian:

```bash
python3 build.py .          # jana semula index.html + compositions/ (masa, teks, caption)
npx hyperframes check
npx hyperframes render --quality delivery -o S70_tiktok.mp4
```

Teks, masa caption dan punch-in semuanya ditetapkan dalam `build.py`.
