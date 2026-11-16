#!/usr/bin/env python3
"""Generates the HyperFrames project files for the Proton S70 TikTok edit."""
import json, os, sys

P = sys.argv[1]
os.makedirs(f"{P}/compositions", exist_ok=True)

TOTAL = 28.60
# Talking-head segments: (id, file, out_start, out_dur, media_start)
SEGS = [
    ("seg-offer", "take5090.mp4", 0.00, 7.60, 8.15),
    ("seg-specs", "take5089.mp4", 7.60, 13.03, 0.12),
    ("seg-cta", "take5090.mp4", 20.63, 7.97, 15.98),
]
# B-roll inserts (muted, cropped from the 4K source): (id, file, start, dur, media_start)
BROLL = [
    ("br-front", "broll_front.mp4", 0.00, 3.40, 0.30),
    ("br-badge", "broll_badge.mp4", 10.80, 3.50, 0.30),
    ("br-hood", "broll_hood.mp4", 14.30, 3.60, 0.20),
]
# Overlay scenes: (id, start, dur)
SCENES = [
    ("hook", 0.00, 3.40),
    ("model", 7.60, 3.20),
    ("specs", 12.00, 5.90),
    ("rahmah", 19.00, 2.00),
    ("cta", 22.30, TOTAL - 22.30),
]

# Caption groups: list of (word, out_start). Group end = next group's start or explicit end.
HL = {"RM2,300", "S70", "MC2", "1.5", "NA", "CVT", "RAHMAH", "FORM", "BAWAH", "A", "Z", "BANTU"}
GROUPS = [
    ([("Kita", 4.66), ("dah", 5.35), ("boleh", 5.49), ("bantu", 5.63)], 5.89),
    ([("korang", 5.91), ("untuk", 6.25)], 6.59),
    ([("bawa", 6.61), ("balik", 6.77), ("kereta", 7.03), ("ni", 7.37)], 7.60),
    ([("Proton", 7.66), ("S70", 8.48), ("MC2", 9.40)], 10.80),
    ([("dijanakan", 10.84), ("dengan", 11.46)], 11.92),
    ([("engine", 11.96), ("1.5", 12.40), ("NA", 13.30)], 14.56),
    ([("menggunakan", 14.60), ("gearbox", 15.64)], 16.22),
    ([("jenis", 16.26), ("CVT", 16.76)], 17.92),
    ([("ataupun", 17.94), ("ada", 18.36), ("orang", 18.60)], 18.72),
    ([("panggil", 18.74), ("sebagai", 19.04)], 19.44),
    ([("S70", 19.48), ("Rahmah", 20.22)], 20.66),
    ([("So", 20.71), ("untuk", 20.89), ("korang", 21.13)], 21.33),
    ([("kat", 21.35), ("luar", 21.53), ("sana", 21.79)], 21.95),
    ([("yang", 21.97), ("mana", 22.17), ("berminat", 22.47)], 23.40),
    ([("boleh", 23.51), ("isi", 23.61), ("form", 23.91)], 24.07),
    ([("yang", 24.09), ("ada", 24.23), ("kat", 24.41), ("bawah", 24.51)], 24.69),
    ([("sekarang", 24.71)], 25.45),
    ([("Kita", 25.55), ("akan", 25.83), ("guide", 26.11), ("korang", 26.29)], 26.53),
    ([("daripada", 26.55), ("A", 26.91), ("sampai", 27.71), ("Z", 28.15)], TOTAL),
]

GSAP = '<script src="assets/vendor/gsap.min.js"></script>'

# ---------------------------------------------------------------- index.html
vids = []
z = 1
for vid, f, st, du, ms in SEGS:
    vids.append(f'''      <div class="frame" id="{vid}-wrap">
        <video id="{vid}" class="clip" src="assets/{f}" data-start="{st:.2f}" data-duration="{du:.2f}" data-media-start="{ms:.2f}" data-track-index="0" data-has-audio="true" data-volume="1" data-fade-in="0.03" data-fade-out="0.03" playsinline style="z-index:{z}"></video>
      </div>''')
for bid, f, st, du, ms in BROLL:
    vids.append(f'''      <div class="frame broll" id="{bid}-wrap">
        <video id="{bid}" class="clip" src="assets/{f}" data-start="{st:.2f}" data-duration="{du:.2f}" data-media-start="{ms:.2f}" data-track-index="1" muted playsinline></video>
      </div>''')
hosts = []
for i, (sid, st, du) in enumerate(SCENES):
    hosts.append(f'''      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{st:.2f}" data-duration="{du:.2f}" data-track-index="{3+i}" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:{20+i}"></div>''')
hosts.append(f'''      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL:.2f}" data-track-index="2" data-track-kind="captions" data-width="1080" data-height="1920" style="z-index:40"></div>''')

index = f'''<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    {GSAP}
    <style>
      :root {{ --ground: #000; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      .frame {{ position: absolute; inset: 0; z-index: 1; }}
      .frame.broll {{ z-index: 5; }}
      .frame video {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #scrim {{ position: absolute; inset: 0; z-index: 10; pointer-events: none;
        background: linear-gradient(180deg, rgba(0,0,0,.50) 0%, rgba(0,0,0,0) 34%, rgba(0,0,0,0) 52%, rgba(0,0,0,.45) 78%, rgba(0,0,0,.25) 100%); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.2f}" data-width="1080" data-height="1920" data-fps="30">
{chr(10).join(vids)}
      <div id="scrim" data-layout-ignore></div>
{chr(10).join(hosts)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      // Punch-ins on the talking head (origin on the speaker's face) to hide jump cuts.
      const P = (sel, t, s, ox, oy) => tl.set(sel, {{ scale: s, transformOrigin: ox + "px " + oy + "px" }}, t);
      P("#seg-offer-wrap", 0, 1.18, 760, 640);
      P("#seg-offer-wrap", 5.60, 1.36, 760, 640);
      P("#seg-specs-wrap", 7.60, 1.0, 640, 700);
      P("#seg-specs-wrap", 17.90, 1.28, 660, 660);
      P("#seg-cta-wrap", 20.63, 1.12, 700, 640);
      P("#seg-cta-wrap", 23.50, 1.26, 700, 380);
      // Slow push on each B-roll insert.
      tl.fromTo("#br-front-wrap", {{ scale: 1.0 }}, {{ scale: 1.10, duration: 3.40, ease: "none", transformOrigin: "50% 45%" }}, 0);
      tl.fromTo("#br-badge-wrap", {{ scale: 1.12, x: 0 }}, {{ scale: 1.0, x: 0, duration: 3.50, ease: "none", transformOrigin: "50% 40%" }}, 10.80);
      tl.fromTo("#br-hood-wrap", {{ scale: 1.0, y: 0 }}, {{ scale: 1.08, y: -30, duration: 3.60, ease: "none", transformOrigin: "50% 50%" }}, 14.30);
      // Quick dip on the B-roll exits so the cut back reads as intended.
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
open(f"{P}/index.html", "w").write(index)

# ---------------------------------------------------------------- shared style
BASE_CSS = '''
    #root { position: absolute; inset: 0; font-family: "Montserrat", sans-serif; color: #fff; }
    .ink { color: #FFD400; }
    .chip { display: inline-block; background: #0b0b0d; color: #fff; font-weight: 800; letter-spacing: .06em;
      padding: 14px 28px 14px 24px; border-left: 10px solid #FFD400; border-radius: 6px; text-transform: uppercase; }
    .center { position: absolute; left: 70px; width: 850px; text-align: center; }
'''

def scene(sid, css, body, js):
    return f'''<template>
  <style>
    {BASE_CSS}
    {css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1080" data-height="1920">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
'''

# ---- hook (0 – 3.40): frame 0 already carries the bold line.
open(f"{P}/compositions/hook.html", "w").write(scene("hook", '''
    #hook-kicker { top: 250px; }
    #hook-kicker .chip { font-size: 44px; }
    #hook-price { top: 330px; font-family: "Archivo Black", sans-serif; font-size: 188px; line-height: 1; color: #FFD400;
      text-shadow: 0 10px 0 rgba(0,0,0,.55), 0 0 60px rgba(0,0,0,.45); letter-spacing: -.02em; }
    #hook-sub1 { top: 560px; font-size: 58px; font-weight: 900; text-shadow: 0 5px 18px rgba(0,0,0,.7); }
    #hook-sub2 { top: 636px; font-family: "Archivo Black", sans-serif; font-size: 100px; line-height: 1.05; text-shadow: 0 6px 20px rgba(0,0,0,.7); }
''', '''    <div id="hook-kicker" class="center"><span class="chip" data-var-text="hook_kicker">Minimum gaji bersih</span></div>
    <div id="hook-price" class="center">RM2,300</div>
    <div id="hook-sub1" class="center">DAH BOLEH BAWA BALIK</div>
    <div id="hook-sub2" class="center">PROTON <span class="ink">S70</span></div>''', '''
    // Kicker + price are on screen at frame 0 (thumbnail); the payoff line lands next.
    tl.fromTo("#hook-sub1", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power4.out" }, 0.45);
    tl.fromTo("#hook-sub2", { opacity: 0, scale: 1.25 }, { opacity: 1, scale: 1, duration: 0.35, ease: "expo.out" }, 0.75);
    // Hit on "RM2300" as it is spoken.
    tl.fromTo("#hook-price", { scale: 1 }, { scale: 1.08, duration: 0.10, ease: "power2.out" }, 2.10);
    tl.to("#hook-price", { scale: 1, duration: 0.30, ease: "power3.out" }, 2.20);
    // Exit.
    tl.to(["#hook-kicker", "#hook-price", "#hook-sub1", "#hook-sub2"], { opacity: 0, filter: "blur(10px)", duration: 0.2, ease: "power2.in", stagger: 0.03 }, 3.08);'''))

# ---- model title (7.60 – 10.80)
open(f"{P}/compositions/model.html", "w").write(scene("model", '''
    #model-brand { top: 250px; font-size: 52px; font-weight: 800; letter-spacing: .5em; text-indent: .5em; text-shadow: 0 4px 16px rgba(0,0,0,.7); }
    #model-name { top: 315px; font-family: "Archivo Black", sans-serif; font-size: 170px; line-height: 1; text-shadow: 0 8px 26px rgba(0,0,0,.6); }
    #model-bar { position: absolute; top: 508px; left: 345px; width: 300px; height: 10px; background: #FFD400; border-radius: 5px; }
''', '''    <div id="model-brand" class="center">PROTON</div>
    <div id="model-name" class="center"><span id="model-s70">S70</span> <span id="model-mc2" class="ink">MC2</span></div>
    <div id="model-bar"></div>''', '''
    tl.fromTo("#model-brand", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }, 0.05);
    tl.fromTo("#model-s70", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power4.out" }, 0.86);
    tl.fromTo("#model-mc2", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power4.out" }, 1.78);
    tl.fromTo("#model-bar", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "expo.out" }, 1.85);
    tl.to(["#model-brand", "#model-name", "#model-bar"], { opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power2.in" }, 2.98);'''))

# ---- spec cards (12.00 – 17.90) over the B-roll
open(f"{P}/compositions/specs.html", "w").write(scene("specs", '''
    .spec { position: absolute; left: 90px; width: 900px; height: 190px; border-radius: 28px;
      background: rgba(12,12,16,.80); border: 2px solid rgba(255,255,255,.14); backdrop-filter: blur(22px);
      display: flex; align-items: center; padding: 0 44px; gap: 34px; box-shadow: 0 24px 60px rgba(0,0,0,.45); }
    #spec-engine { top: 330px; }
    #spec-gear { top: 560px; }
    .spec .ico { width: 104px; height: 104px; border-radius: 22px; background: #FFD400; display: flex; align-items: center; justify-content: center; flex: none; }
    .spec .lbl { font-size: 34px; font-weight: 800; letter-spacing: .14em; color: rgba(255,255,255,.62); }
    .spec .val { font-family: "Archivo Black", sans-serif; font-size: 84px; line-height: 1.02; color: #fff; }
''', '''    <div id="spec-engine" class="spec">
      <div class="ico"><svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#0b0b0d" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10h2V8h4V6h4v2h3l2 2h1v6h-1l-2 2H9l-2-2H4z"/><path d="M2 11v4"/></svg></div>
      <div><div class="lbl">ENJIN</div><div class="val">1.5L <span class="ink">NA</span></div></div>
    </div>
    <div id="spec-gear" class="spec">
      <div class="ico"><svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#0b0b0d" stroke-width="2.2" stroke-linecap="round"><circle cx="6" cy="6" r="2"/><circle cx="12" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><circle cx="12" cy="18" r="2"/><path d="M6 8v8M12 8v8M18 8v4H6"/></svg></div>
      <div><div class="lbl">GEARBOX</div><div class="val ink">CVT</div></div>
    </div>''', '''
    // "1.5" is spoken at 12.40, "CVT" at 16.76 (film time).
    tl.fromTo("#spec-engine", { opacity: 0, x: -140, filter: "blur(12px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }, 0.30);
    tl.fromTo("#spec-gear", { opacity: 0, x: 140, filter: "blur(12px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }, 4.66);
    tl.to(["#spec-engine", "#spec-gear"], { opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power2.in", stagger: 0.04 }, 5.62);'''))

# ---- rahmah chip (19.20 – 20.63)
open(f"{P}/compositions/rahmah.html", "w").write(scene("rahmah", '''
    #rah { top: 300px; }
    #rah .chip { font-size: 58px; padding: 22px 40px 22px 34px; }
''', '''    <div id="rah" class="center"><span class="chip"><span class="ink">S70</span> RAHMAH</span></div>''', '''
    tl.fromTo("#rah", { opacity: 0, scale: 0.85 }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.6)" }, 0.45);
    tl.to("#rah", { opacity: 0, duration: 0.15, ease: "power2.in" }, 1.80);'''))

# ---- CTA (22.30 – end)
open(f"{P}/compositions/cta.html", "w").write(scene("cta", '''
    #cta-q { top: 200px; }
    #cta-q .chip { font-size: 46px; }
    #cta-main { top: 285px; font-family: "Archivo Black", sans-serif; font-size: 108px; line-height: 1.0; text-shadow: 0 8px 26px rgba(0,0,0,.6); }
    #cta-sub { top: 530px; }
    #cta-sub span { display: inline-block; background: #FFD400; color: #0b0b0d; font-weight: 900; font-size: 50px; padding: 14px 34px; border-radius: 999px; letter-spacing: .03em; }
    #cta-arrow { position: absolute; left: 425px; top: 1360px; width: 140px; height: 160px; }
''', '''    <div id="cta-q" class="center"><span class="chip">Berminat?</span></div>
    <div id="cta-main" class="center">ISI FORM<br/><span class="ink">DI BAWAH</span></div>
    <div id="cta-sub" class="center"><span>KAMI GUIDE DARI A&ndash;Z</span></div>
    <svg id="cta-arrow" viewBox="0 0 140 160" data-layout-ignore><path d="M70 8v120M18 84l52 52 52-52" fill="none" stroke="#FFD400" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/></svg>''', '''
    // film 22.47 "berminat", 23.61 "isi form", 24.51 "bawah", 25.55 "kita akan guide".
    tl.fromTo("#cta-q", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.35, ease: "expo.out" }, 0.15);
    tl.fromTo("#cta-main", { opacity: 0, scale: 1.3, filter: "blur(10px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }, 1.25);
    tl.fromTo("#cta-arrow", { opacity: 0, y: -80 }, { opacity: 1, y: 0, duration: 0.55, ease: "back.out(2)" }, 2.15);
    tl.fromTo("#cta-sub", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }, 3.20);'''))

# ---- captions
grp_html, grp_js = [], []
for gi, (words, end) in enumerate(GROUPS):
    st = max(words[0][1] - 0.04, 0.0)
    spans = []
    for wi, (w, wt) in enumerate(words):
        cls = "w hl" if w.upper() in HL else "w"
        spans.append(f'<span id="c{gi}w{wi}" class="{cls}">{w.upper()}</span>')
    grp_html.append(f'    <div id="cg{gi}" class="cg">{" ".join(spans)}</div>')
    grp_js.append(f'    tl.fromTo("#cg{gi}", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "power3.out" }}, {st:.2f});')
    for wi, (w, wt) in enumerate(words):
        if wi == 0:
            continue
        grp_js.append(f'    tl.fromTo("#c{gi}w{wi}", {{ opacity: 0.35 }}, {{ opacity: 1, duration: 0.06 }}, {max(wt - 0.02, st):.2f});')
    grp_js.append(f'    tl.set("#cg{gi}", {{ opacity: 0, visibility: "hidden" }}, {min(end, TOTAL - 0.01):.2f});')

open(f"{P}/compositions/captions.html", "w").write(f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; font-family: "Montserrat", sans-serif; }}
    .cg {{ position: absolute; left: 70px; width: 850px; top: 1140px; text-align: center; opacity: 0;
      font-size: 60px; font-weight: 900; line-height: 1.12; color: #fff; overflow: visible;
      text-shadow: 0 0 2px #000, 0 4px 0 #000, 0 6px 18px rgba(0,0,0,.85); -webkit-text-stroke: 2px #000; paint-order: stroke fill; }}
    .cg .hl {{ color: #FFD400; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(grp_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(grp_js)}
    window.__timelines["captions"] = tl;
  </script>
</template>
''')
print("ok")
