# SPEC — Proton Saga MC3 · 5 Fakta (Salam Automobile)

GOAL:    Viewer on TikTok stops on frame 0, learns 5 buying facts about the Saga MC3 in ~1 min,
         and leaves knowing they can apply from RM1,800 net salary via Salam Automobile.
OUTPUT:  HyperFrames, 1080 x 1920 (9:16), 30 fps
TIME:    62.0 s x 30 = 1860 frames. Voiceover (owner's own, trimmed 95.1 s -> 57.8 s) starts at 0.30 s.

LOOK
- Ground A (info scenes): #F3F2EF warm light grey + 1 px grid lines every 90 px at 5% ink.
- Ground B (hook + CTA): #1D2025 charcoal, gold diagonal hairlines at 10%.
- Ink #1D2025, muted ink #6B6F76, accent gold #BE935B (logo gold) — gold only on the one key value
  per scene (the number / spec), progress fill and icon highlights.
- Display: Montserrat 800, 120-300 px for hero values, tracking -2%; labels Inter 700 30-34 px caps
  tracking +12%; body Inter 500 40-46 px.
- Medium: flat 2D line-art icons, 6 px stroke, round caps, drawn on with stroke-dash; cards #FFFFFF
  radius 28 px, shadow 0 18 40 rgba(29,32,37,0.10).
- No glow, no gradients-as-decoration, no glass, no particles.

SAFE AREA: all words between y 200 and y 1320, x 80-1000; below 1330 only decoration.

MOTION
- Enter: expo.out / power4.out 0.5-0.7 s; exit: power3.in 0.25-0.3 s (shorter than entrances).
- Words stagger 0.07 s; tags 0.08 s; icons draw 0.6-0.9 s power2.inOut.
- Landed titles hold dead still.
- Transitions (each with a cause): colour flood (hook->1, 5->CTA), whip (1->2, 3->4),
  blur swap (2->3, 4->5), iris open (CTA->logo).

SHOTS (film time)
- 0.00-5.50  HOOK: "5 FAKTA" + "korang tak tahu" already on frame 0; sedan line-art draws; "PROTON SAGA MC3" lands on "Saga MC3" (3.5 s).
- 5.50-9.88  FAKTA 1 ENJIN: engine icon draws; 1.3L (struck, grey) -> 1.5L gold on "1.5" (~8.0 s); bars grow.
- 9.88-18.43 FAKTA 2 DIGITAL METER: cluster draws; Standard/Executive/Premium ticks on each word; at "pilih 2 jenis display" splits into MODERN vs TRADITIONAL.
- 18.43-29.68 FAKTA 3 CARPLAY: "Sedan Segmen A" + "#1 di Malaysia" badge; screen + phone link; Apple CarPlay & Android Auto rows on each word; tag Executive & Premium.
- 29.68-41.63 FAKTA 4 GEARBOX: two cards; 4AT (stepped ratio graph) for Standard/Executive; CVT (smooth curve) for Premium.
- 41.63-47.63 FAKTA 5 ADAS: top-view car with radar arcs; "ADAS LEVEL 1" + tag Spec Premium (spoken "spek standard" line removed per owner correction).
- 47.63-58.20 CTA: charcoal; "Gaji bersih RM1,800" counter; "Isi form di bawah" + arrow; "Guide dari A sampai Z".
- 58.20-62.00 LOGO: white iris; gold S + swoosh wipe, dark A rises, wordmark + line + tagline; hold 2 s.

SOUND
- Voice = clock. Music bed (local MusicGen, royalty-free) at 0.12 under voice, rises to 0.5 for logo.
- SFX (Pixabay licence, bundled): whoosh variants on scene cuts, pop on tags, ping on hero numbers,
  riser -> impact on logo only.

BANNED: dark void with floating small text, glow/neon, purple-blue gradients, every element fading up,
text moving while read, captions in the bottom 590 px.

QA FRAMES: 0.0, 3.8, 8.3, 13.0, 17.0, 24.0, 28.5, 34.0, 40.8, 45.5, 52.5, 57.0, 59.0, 61.5
