# Salam Automobile — "Perodua Bezza Paling Laris" (TikTok 9:16)

Video infografik 2D dibina dengan [HyperFrames](https://hyperframes.heygen.com) (HTML + GSAP → MP4).
1080×1920, 30 fps, ~62.5 s.

## Struktur
| Masa | Scene |
|---|---|
| 0 – 9 s | Hook: "Kereta PALING LARIS?" → bukan Axia ✕, bukan Myvi ✕ → reveal gambar sebenar Perodua Bezza #1 |
| 9 – 17.7 s | Statistik: sehingga Sept 2026, 73,000+ unit didaftarkan |
| 17.7 – 27.1 s | Sebab 01: ruang but 508 L, paling luas dalam segmen |
| 27.1 – 33.2 s | Sebab 02: enjin 1.3 L, tahan lasak & jimat minyak |
| 33.2 – 40.7 s | Sebab 03: variant 1.3X — push start, kawalan kestabilan, hill start assist |
| 40.7 – 49.5 s | Sebab 04: dijual hingga 2030, spare part senang dicari |
| 49.5 – 56.1 s | CTA: variant mana sesuai dengan gaji → ISI FORM DI BAWAH |
| 56.1 – 62.5 s | Closing: circle wipe → logo Salam Automobile reveal, "A hingga Z" |

## Bina semula
```bash
npm install
python3 tools/edit_vo.py <IMG_0400.MOV> <words.json> assets   # potong VO (buang ayat/ jeda)
python3 tools/make_captions.py                                 # caption karaoke
python3 tools/make_audio.py assets                             # BGM + SFX (disintesis)
tools/duck_bgm.sh                                              # BGM auto-duck di bawah suara
python3 tools/cutout_bezza.py assets/img/bezza.jpg assets/img/bezza_cut.png
python3 tools/gen_sfx.py                                       # letak SFX dalam index.html
npx hyperframes check
npx hyperframes render -f 30 -q delivery -o renders/out.mp4
```

## Audio
- VO: RNNoise (`tools/models/sh.rnnn`) + afftdn, EQ (−3 dB @280 Hz, +2.5 dB @3.6 kHz, air shelf), de-esser,
  rubberband 1.08× (formant dijaga), compressor, loudnorm −14 LUFS / −1.5 dBTP.
- BGM: sidechain duck ~12 dB bila suara bercakap, naik semula pada closing logo.
