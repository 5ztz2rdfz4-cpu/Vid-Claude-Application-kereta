---
name: salam-automobile
description: House style for Salam Automobile TikTok car-sales videos. Use whenever the user mentions "Salam Automobile" (or asks for a car video for their TikTok sales account) - build a ~1 minute vertical 2D infographic video with HyperFrames from their Drive folder (voiceover video + car photos + logo), with hook, photo cards per point, SFX, royalty-free music and the animated Salam Automobile logo closing.
---

# Salam Automobile — TikTok car video house style

The approved reference build is `video/saga/` (Proton Saga MC3, "5 fakta") and its render
`video/out/saga-mc3-salam-automobile.mp4`. **Copy that project as the starting point** for every new
video and swap the content; do not redesign from scratch. Read `video/saga/SPEC.md` first.

Talk to the user in Malay (casual, like they write). They want it: cantik, kemas, infografik,
profesional — "tak over sangat, tak sikit sangat".

## What the user gives

A Google Drive folder link containing typically:
- a `.MOV` that is often a **black screen with the owner's voiceover** (the content is the audio),
- car photos (exterior, engine, meter, infotainment, gear knob, feature slides) — one per point,
- the Salam Automobile logo PNG (white background, gold `#BE935B` + charcoal).

Download: `gdown --folder <url> --skip-download` style listing fails on file hosts, so list file ids with
`gdown --folder` and fetch each file with
`curl -L "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`.
Keep downloads in the scratchpad, not the repo.

## Workflow

1. **Transcribe** the voiceover (`faster-whisper`, model `large-v3`, `language="ms"`, word timestamps;
   set `HF_HUB_DISABLE_XET=1`; load audio via numpy/wave, not PyAV). Re-check unclear lines.
2. **Trim to ~55–60 s** of voice (+ ~4 s logo): drop repeats, restatements ("iaitu …"), long pauses.
   Cut inside silences (`silencedetect` at -26/-30 dB); 12 ms fades; then
   `highpass=70, afftdn, acompressor, loudnorm I=-16`. Re-transcribe the cut to verify no word is clipped.
   Scene boundaries = the cut map (voice starts at 0.30 s in film time).
3. **Facts may be misspoken** in the voiceover — confirm any spec/variant claim that looks off with the
   user. If the user corrects one, remove the wrong spoken phrase rather than leaving audio and text
   contradicting.
4. **Build** (HyperFrames, 1080×1920, 30 fps) — one sub-composition per scene:
   - **Hook** (charcoal ground, gold diagonal hairlines): big gold number/claim + white headline +
     the car exterior photo card, all visible on frame 0 (thumbnail); model name lands on its word.
   - **Each point** (light `#F3F2EF` ground + 90 px grid): a **photo card from the user's images**
     (radius 28, soft shadow, slow push-in on an inner wrapper) **plus** 2D infographic elements —
     line-art icons drawn with stroke-dash, before→after numbers, check chips per variant, comparison
     cards with small graphs, badges ("#1"). The user explicitly wants their photos used in the points.
   - Persistent **"FAKTA x / N"** counter + gold segment progress bar at the top.
   - **CTA** (charcoal): financing line (e.g. "Gaji bersih RM1,800" counter), "Isi form di bawah" card
     with arrow, "Kami guide dari A sampai Z".
   - **Closing**: white iris → layered logo animation (gold S/swoosh wipe, charcoal A rises, SALAM wipe,
     AUTOMOBILE line opens from centre, tagline fades), hold ≥ 2 s. Split the logo PNG into gold/dark
     layers and horizontal bands with PIL; never redraw the logo.
5. **Sound**: voice = clock. Music bed generated locally with MusicGen (`facebook/musicgen-medium`,
   ~110 bpm upbeat corporate/automotive, no vocals) so it is copyright-free; loop on bar lines to film
   length; bed volume ~0.16 under voice, rising to ~0.5 for the logo. SFX from the bundled Pixabay set
   (`video/saga/assets/sfx`): whoosh variants on scene cuts, pop on chips/badges, ping on hero numbers,
   bass impact on the logo. Place each hit so its peak lands on the visual.
6. **Check & render**: `npx hyperframes check`, `snapshot` key frames and look at them, then
   `hyperframes render -q delivery`. Finally re-encode audio only with
   `loudnorm=I=-15:TP=-1.2` (TikTok loudness). Verify frames from the MP4, send it, commit + push.

## Design tokens

- Charcoal `#1D2025`, light ground `#F3F2EF`, card white `#FFFFFF`, gold `#BE935B` (fills / on dark),
  gold text on light `#A57A42` (contrast), muted `#6B6F76`.
- Montserrat 800/900 for display (hero values 120–400 px), Inter 500–700 for labels/body, labels in
  caps with +12–20% tracking; nothing under 28 px.
- Safe area: all words between y 200–1320 and x 80–1000; keep the bottom ~590 px free for TikTok UI.
- Motion: arrivals `expo.out` 0.5–0.7 s, exits `power3.in` 0.25–0.3 s; transitions vary (colour flood,
  whip, blur swap, vertical whip, iris). Titles hold still once landed. No glow/neon/gradients.

## Gotchas in this environment

- Load GSAP from `assets/vendor/gsap.min.js` (copied from the `gsap` npm package) — the render browser
  cannot reach the CDN.
- Use the project-pinned CLI: `video/node_modules/.bin/hyperframes`.
- Some user photos carry third-party watermarks; mention it in the delivery note.
