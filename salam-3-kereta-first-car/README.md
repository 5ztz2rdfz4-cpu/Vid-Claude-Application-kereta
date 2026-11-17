# Salam Automobile — "3 Kereta First Car" (TikTok 9:16)

Video infografik 2D (HyperFrames + GSAP), ~60s, 1080x1920 @30fps.

## Struktur
| Masa | Babak |
|---|---|
| 0.0–3.6 | **Hook** — "Baru start kerja? & perlukan kereta UNTUK BERGERAK?" + kereta 2D masuk |
| 3.6–6.9 | "3 Model Kereta" + 3 kad kereta |
| 6.9–11.5 | Bajet bulanan RM400–RM600 (kaunter + slider) |
| 11.5–24.7 | 01 Proton Saga MC3 — enjin 1.5 VVT, gearbox 4AT / CVT |
| 24.7–33.7 | 02 Perodua Axia — hatchback, 1.0L, CVT |
| 33.7–43.8 | 03 Perodua Bezza — 1.3L / 1.0L, 4AT (low spec) |
| 43.8–50.2 | Ringkasan: jadual perbandingan |
| 50.2–54.0 | **CTA** — butang "ISI FORM DI BAWAH" + tap + chevron |
| 54.0–60.0 | **Closing** — circle wipe ke krim, motion logo Salam Automobile, "A hingga Z", kilauan |

## Audio
- VO asal (IMG_9988.MOV) — jeda senyap dipadatkan (`scripts/tighten.py`), compress + normalise.
- Muzik latar & semua SFX disintesis sendiri (`scripts/audio.py`) — bebas hak cipta.
- Muzik di-duck bawah suara; master -14 LUFS / -1 dBTP (standard TikTok).

## Render semula
```bash
cd project
npx hyperframes@0.9.61 render . -o out.mp4 -q high -f 30
```
Logo layers dijana dari logo asal dengan `scripts/logo.py`.
