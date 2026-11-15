#!/usr/bin/env python3
"""Generate the HyperFrames compositions for the TikTok car-loan video.

All times below are seconds on the EDITED timeline (assets/talk.mp4, 69.5 s).
Run:  python3 tools/build.py   (from the project folder)
Then: npx hyperframes check && npx hyperframes render -o renders/final.mp4
"""
import json, html, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOTAL = 69.5
W, H = 1080, 1920

words = json.load(open(ROOT / "tools/words.json"))
cuts = json.load(open(ROOT / "tools/cutpoints.json"))

# ---------------------------------------------------------------- scenes
SCENES = [  # id, start, end
    ("hook", 0.0, 6.40),
    ("tip1", 6.40, 18.47),
    ("tip2", 18.47, 44.67),
    ("tip3", 44.67, 58.83),
    ("cta", 58.83, TOTAL),
]

# ---------------------------------------------------------------- icons
ICON = {
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    "x": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    "warn": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"><path d="M12 3.5L2.8 19.5h18.4z"/><path d="M12 10v4.2"/><circle cx="12" cy="17" r=".6" fill="currentColor"/></svg>',
    "doc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/></svg>',
    "bank": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round"><path d="M3 9.5L12 4l9 5.5M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20.5h18"/></svg>',
    "idcard": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round"><rect x="2.5" y="5" width="19" height="14" rx="2"/><circle cx="8.5" cy="11" r="2.2"/><path d="M5 16.2c.8-1.6 2-2.3 3.5-2.3s2.7.7 3.5 2.3M14.5 10h4M14.5 13.5h3"/></svg>',
    "form": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>',
    "cap": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2.5 9 2.5 12 0v-5M22 9v6"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v15M5.5 12.5L12 19l6.5-6.5"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg>',
}

BASE_CSS = """
#root { position:absolute; inset:0; overflow:visible; font-family:'Montserrat', sans-serif; color:#fff; }
.abs { position:absolute; }
.band { position:absolute; left:100px; right:100px; top:300px; display:flex; flex-direction:column; align-items:center; text-align:center; }
.pill { display:inline-flex; align-items:center; gap:14px; background:#FFD21F; color:#0B1430; font-weight:900; font-size:44px; letter-spacing:.04em; padding:12px 30px; border-radius:999px; box-shadow:0 10px 30px rgba(0,0,0,.35); }
.pill svg { width:44px; height:44px; }
.ttl { font-weight:900; font-size:112px; line-height:.98; letter-spacing:-.01em; text-transform:uppercase; text-shadow:0 6px 28px rgba(0,0,0,.55); }
.ttl .w { display:inline-block; }
.y { color:#FFD21F; } .r { color:#FF3B3F; } .g { color:#2BD46B; }
.sub { font-family:'Inter',sans-serif; font-weight:700; font-size:46px; line-height:1.2; text-shadow:0 4px 18px rgba(0,0,0,.6); }
.glass { background:rgba(11,20,48,.82); border:2px solid rgba(255,255,255,.14); border-radius:30px; box-shadow:0 18px 50px rgba(0,0,0,.45); }
.chip { display:inline-flex; align-items:center; gap:16px; padding:18px 30px; font-family:'Inter',sans-serif; font-weight:700; font-size:44px; }
.chip svg { width:46px; height:46px; }
.stamp { display:inline-block; border:9px solid #FF3B3F; color:#FF3B3F; font-weight:900; font-size:96px; letter-spacing:.06em; padding:4px 30px; border-radius:18px; background:rgba(255,255,255,.92); text-transform:uppercase; }
/* full-screen B-roll cutaway */
.broll { position:absolute; inset:0; }
.broll .bg { position:absolute; inset:0;
  background:
    repeating-linear-gradient(0deg, rgba(255,255,255,.035) 0 2px, transparent 2px 90px),
    repeating-linear-gradient(90deg, rgba(255,255,255,.035) 0 2px, transparent 2px 90px),
    radial-gradient(120% 70% at 50% 30%, #1E3270 0%, #0B1430 55%, #050916 100%); }
.broll .head { position:absolute; left:100px; right:100px; top:300px; text-align:center; }
.row { position:absolute; left:90px; width:900px; height:170px; display:flex; align-items:center; gap:30px; padding:0 34px; background:#fff; color:#0B1430; border-radius:30px; box-shadow:0 18px 40px rgba(0,0,0,.35); }
.row .ic { width:100px; height:100px; border-radius:24px; background:#EEF2FF; color:#1E3270; display:flex; align-items:center; justify-content:center; flex:none; }
.row .ic svg { width:62px; height:62px; }
.row .tx { flex:1; text-align:left; }
.row .t1 { font-weight:900; font-size:50px; line-height:1.05; }
.row .t2 { font-family:'Inter',sans-serif; font-weight:700; font-size:34px; color:#55607A; margin-top:6px; }
.tick { width:84px; height:84px; border-radius:50%; background:#22C55E; color:#fff; display:flex; align-items:center; justify-content:center; flex:none; }
.tick svg { width:54px; height:54px; }
.tick.bad { background:#FF3B3F; }
"""


def esc(s):
    return html.escape(s, quote=True)


def scene_file(sid, start, end, css, body, js):
    dur = round(end - start, 3)
    return f"""<template>
  <style>
{BASE_CSS}
{css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}" data-duration="{dur}" data-layout-allow-overlap>
{body}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const IN = (sel, t, extra) => tl.fromTo(sel, Object.assign({{ opacity: 0, y: 40, filter: "blur(10px)" }}, (extra && extra.from) || {{}}),
                                              Object.assign({{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }}, (extra && extra.to) || {{}}), t);
      const WORDS = (sel, t, gap) => tl.fromTo(sel, {{ opacity: 0, filter: "blur(8px)", scale: 1.08 }},
                                              {{ opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.2, ease: "power4.out", stagger: gap || 0.08 }}, t);
      const OUT = (sel, t) => tl.to(sel, {{ opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power2.in" }}, t);
      const POP = (sel, t) => tl.fromTo(sel, {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2.2)" }}, t);
      const SLAM = (sel, t, rot) => tl.fromTo(sel, {{ scale: 2.2, opacity: 0, rotation: rot || -8 }}, {{ scale: 1, opacity: 1, rotation: rot || -8, duration: 0.22, ease: "power4.in" }}, t);
      const BROLL_IN = (sel, t) => tl.fromTo(sel, {{ opacity: 0, scale: 1.08, filter: "blur(14px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.3, ease: "power3.out" }}, t);
{js}
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""


def clip(cid, start_abs, end_abs, s0, inner, cls="", style=""):
    st = round(start_abs - s0, 3)
    du = round(end_abs - start_abs, 3)
    return f'    <div id="{cid}" class="clip {cls}" data-start="{st}" data-duration="{du}" style="{style}">\n{inner}\n    </div>'


def L(t, s0):
    return round(t - s0, 3)


def words_html(text, cls=""):
    return " ".join(f'<span class="w {cls}">{esc(w)}</span>' for w in text.split())


# ================================================================ HOOK
def build_hook():
    s0, s1 = 0.0, 6.40
    body = []
    body.append(clip("hook-a", 0.0, 3.07, s0, f"""
      <div class="band" id="hook-a-in" style="top:300px">
        <div class="ttl" style="font-size:112px">LOAN KERETA</div>
        <div class="ttl r" style="font-size:104px;white-space:nowrap">KENA REJECT?</div>
        <div class="ttl" id="hook-reduce" style="font-size:66px;margin-top:22px;white-space:nowrap"><span class="w">ATAU</span> <span class="w">KENA</span> <span class="w y">REDUCE?</span></div>
      </div>
      <div class="abs" id="hook-stamp-w" style="left:0;right:0;top:612px;text-align:center"><div class="stamp" id="hook-stamp" style="font-size:72px">REJECTED</div></div>
    """))
    body.append(clip("hook-b", 3.07, 6.40, s0, f"""
      <div class="band" style="top:310px;flex-direction:row;justify-content:center;gap:34px;align-items:center">
        <div class="ttl y" id="hook-3" style="font-size:360px;line-height:.8">3</div>
        <div style="text-align:left">
          <div class="ttl" id="hook-b1" style="font-size:118px">BENDA</div>
          <div class="ttl" id="hook-b2" style="font-size:96px">WAJIB</div>
          <div class="ttl y" id="hook-b3" style="font-size:96px">TAHU</div>
        </div>
      </div>
      <div class="band" style="top:700px"><div class="glass chip" id="hook-sub">sebelum apply loan kereta</div></div>
    """))
    js = f"""
      // frame 0 is the thumbnail: headline already on screen
      tl.set("#hook-a-in", {{ opacity: 1 }}, 0);
      SLAM("#hook-stamp", {L(1.09, s0)}, -9);
      tl.fromTo("#hook-a-in", {{ x: 0 }}, {{ keyframes: [{{ x: -14, duration: .04 }}, {{ x: 12, duration: .05 }}, {{ x: -6, duration: .05 }}, {{ x: 0, duration: .05 }}] }}, {L(1.31, s0)});
      WORDS("#hook-reduce .w", {L(2.05, s0)}, 0.12);
      OUT("#hook-a-in, #hook-stamp-w", {L(2.95, s0)});
      tl.fromTo("#hook-3", {{ scale: 1.6, opacity: 0, filter: "blur(16px)" }}, {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: .45, ease: "expo.out" }}, {L(3.25, s0)});
      WORDS("#hook-b1, #hook-b2, #hook-b3", {L(3.55, s0)}, 0.12);
      IN("#hook-sub", {L(4.9, s0)});
      OUT("#hook-3, #hook-b1, #hook-b2, #hook-b3, #hook-sub", {L(6.18, s0)});
    """
    return scene_file("hook", s0, s1, "", "\n".join(body), js)


def chapter(prefix, n, title_html, s0, t_in, t_out, extra_html="", top=300):
    return clip(f"{prefix}-ch", t_in, t_out, s0, f"""
      <div class="band" style="top:{top}px">
        <div class="pill" id="{prefix}-pill">TIP #{n}</div>
        <div class="ttl" id="{prefix}-ttl" style="margin-top:26px">{title_html}</div>
        {extra_html}
      </div>
    """)


# ================================================================ TIP 1
def build_tip1():
    s0, s1 = 6.40, 18.47
    body = [chapter("t1", 1, f'{words_html("DOKUMEN")}<br>{words_html("LENGKAP", "y")}', s0, 6.40, 9.87)]
    rows = [
        ("t1-r1", "doc", "PAYSLIP", "3 bulan terkini", 520),
        ("t1-r2", "bank", "BANK STATEMENT", "3 bulan terkini", 720),
        ("t1-r3", "idcard", "IC & LESEN", "kad pengenalan & lesen memandu", 920),
    ]
    rows_html = "\n".join(
        f'<div class="row" id="{rid}" style="top:{top}px"><div class="ic">{ICON[ic]}</div><div class="tx"><div class="t1">{t1}</div><div class="t2">{t2}</div></div><div class="tick" id="{rid}-tk">{ICON["check"]}</div></div>'
        for rid, ic, t1, t2, top in rows)
    body.append(clip("t1-broll", 9.87, 14.35, s0, f"""
      <div class="broll" id="t1-b-in">
        <div class="bg"></div>
        <div class="head"><div class="pill" style="font-size:36px">TIP #1</div><div class="ttl" style="font-size:80px;margin-top:20px">DOKUMEN <span class="y">WAJIB</span></div></div>
        {rows_html}
      </div>
    """))
    body.append(clip("t1-alt", 14.35, 18.40, s0, f"""
      <div class="band" style="top:300px">
        <div class="ttl" id="t1-q" style="font-size:88px">{words_html("TIADA PAYSLIP")}<br>{words_html("3 BULAN?", "y")}</div>
        <div class="sub" id="t1-cond" style="margin-top:22px">Kalau cukup syarat…</div>
        <div class="pill" id="t1-skim" style="margin-top:26px;font-size:44px">{ICON["cap"]} APPLY SKIM GRADUAN</div>
      </div>
    """))
    js = f"""
      tl.fromTo("#t1-pill", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: .35, ease: "back.out(2.2)" }}, 0.05);
      WORDS("#t1-ttl .w", 0.2, 0.12);
      OUT("#t1-pill, #t1-ttl", {L(9.67, s0)});
      BROLL_IN("#t1-b-in", {L(9.87, s0)});
      IN("#t1-r1", {L(10.62, s0)}, {{ from: {{ x: 80, y: 0 }}, to: {{ x: 0 }} }}); POP("#t1-r1-tk", {L(10.95, s0)});
      IN("#t1-r2", {L(11.80, s0)}, {{ from: {{ x: 80, y: 0 }}, to: {{ x: 0 }} }}); POP("#t1-r2-tk", {L(12.45, s0)});
      IN("#t1-r3", {L(13.10, s0)}, {{ from: {{ x: 80, y: 0 }}, to: {{ x: 0 }} }}); POP("#t1-r3-tk", {L(13.40, s0)});
      tl.to("#t1-b-in", {{ opacity: 0, scale: .96, filter: "blur(10px)", duration: .2, ease: "power2.in" }}, {L(14.15, s0)});
      WORDS("#t1-q .w", {L(14.40, s0)}, 0.1);
      IN("#t1-cond", {L(15.40, s0)});
      POP("#t1-skim", {L(17.15, s0)});
      OUT("#t1-q, #t1-cond, #t1-skim", {L(18.2, s0)});
    """
    return scene_file("tip1", s0, s1, "", "\n".join(body), js)


# ================================================================ TIP 2
def build_tip2():
    s0, s1 = 18.47, 44.67
    body = [chapter("t2", 2, f'{words_html("REKOD")}<br>{words_html("CTOS & CCRIS", "y")}', s0, 18.47, 25.63,
                    extra_html='<div class="glass chip" id="t2-hp" style="margin-top:30px">Hire Purchase (HP) = Loan kereta</div>')]
    squares = "".join(f'<div class="sq" id="t2-sq{i}"></div>' for i in range(12))
    body.append(clip("t2-broll", 25.63, 33.45, s0, f"""
      <div class="broll" id="t2-b-in">
        <div class="bg"></div>
        <div class="head">
          <div class="pill" style="font-size:36px">{ICON["search"]} BANK SEMAK DULU</div>
          <div class="sub" id="t2-bsub" style="margin-top:22px">sebelum luluskan loan korang</div>
        </div>
        <div class="card" id="t2-ctos" style="top:500px">
          <div class="lbl">CTOS</div>
          <div class="gauge">
            <svg viewBox="0 0 200 110" width="330" height="182">
              <path d="M15 100 A85 85 0 0 1 185 100" fill="none" stroke="#FF3B3F" stroke-width="20" stroke-dasharray="89 400"/>
              <path d="M15 100 A85 85 0 0 1 185 100" fill="none" stroke="#FFD21F" stroke-width="20" stroke-dasharray="0 89 89 400"/>
              <path d="M15 100 A85 85 0 0 1 185 100" fill="none" stroke="#22C55E" stroke-width="20" stroke-dasharray="0 178 90 400"/>
            </svg>
            <div class="needle" id="t2-needle"></div>
          </div>
          <div class="ok" id="t2-ctos-ok">SKOR BAIK</div>
        </div>
        <div class="card" id="t2-ccris" style="top:820px">
          <div class="lbl">CCRIS</div>
          <div class="sqs">{squares}</div>
          <div class="ok" id="t2-ccris-ok">BAYAR TEPAT 12 BULAN</div>
        </div>
      </div>
    """))
    body.append(clip("t2-why", 33.45, 36.13, s0, f"""
      <div class="band" style="top:300px">
        <div class="ttl" id="t2-w1" style="font-size:76px">{words_html("INI PUNCA RAMAI")}</div>
        <div class="ttl r" id="t2-w2" style="font-size:136px;margin-top:10px">{words_html("TAK LEPAS")}</div>
      </div>
    """))
    body.append(clip("t2-flags", 36.13, 44.60, s0, f"""
      <div class="band" style="top:310px">
        <div class="sub" id="t2-f0" style="font-size:52px">Bukan CTOS &amp; CCRIS je…</div>
        <div style="display:flex;gap:26px;margin-top:30px">
          <div class="glass chip flag" id="t2-saa">{ICON["warn"]} SAA</div>
          <div class="glass chip flag" id="t2-akpk">{ICON["warn"]} AKPK</div>
        </div>
        <div style="margin-top:44px"><div class="stamp" id="t2-stuck" style="font-size:72px;white-space:nowrap">LOAN SANGKUT!</div></div>
      </div>
    """))
    css = """
    .card { position:absolute; left:90px; width:900px; height:280px; background:#fff; color:#0B1430; border-radius:34px; box-shadow:0 18px 40px rgba(0,0,0,.35); display:flex; align-items:center; padding:0 40px; gap:30px; }
    .card .lbl { font-weight:900; font-size:72px; width:250px; }
    .card .ok { position:absolute; right:30px; bottom:22px; font-weight:900; font-size:30px; color:#fff; background:#22C55E; padding:8px 18px; border-radius:999px; }
    .gauge { position:relative; width:330px; height:182px; margin-top:-20px; }
    .needle { position:absolute; left:161px; bottom:16px; width:8px; height:140px; border-radius:6px; background:#0B1430; transform-origin:50% 100%; }
    .sqs { display:grid; grid-template-columns:repeat(6, 70px); gap:12px; margin-top:-30px; }
    .sq { width:70px; height:56px; border-radius:12px; background:#E3E8F3; }
    .flag { color:#FF6B6E; border-color:rgba(255,59,63,.7); font-size:58px; padding:20px 38px; }
    .flag svg { width:60px; height:60px; }
    """
    js = f"""
      tl.fromTo("#t2-pill", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: .35, ease: "back.out(2.2)" }}, 0.05);
      WORDS("#t2-ttl .w", 0.2, 0.12);
      IN("#t2-hp", {L(23.95, s0)});
      OUT("#t2-pill, #t2-ttl, #t2-hp", {L(25.43, s0)});
      BROLL_IN("#t2-b-in", {L(25.63, s0)});
      IN("#t2-bsub", {L(27.55, s0)});
      IN("#t2-ctos", {L(28.0, s0)}, {{ from: {{ y: 60 }} }});
      tl.fromTo("#t2-needle", {{ rotation: -88 }}, {{ rotation: 58, duration: .9, ease: "power3.out" }}, {L(30.15, s0)});
      POP("#t2-ctos-ok", {L(30.95, s0)});
      IN("#t2-ccris", {L(28.9, s0)}, {{ from: {{ y: 60 }} }});
      tl.fromTo("#t2-ccris .sq", {{ backgroundColor: "#E3E8F3" }}, {{ backgroundColor: "#22C55E", duration: .08, stagger: .045 }}, {L(31.62, s0)});
      POP("#t2-ccris-ok", {L(32.10, s0)});
      tl.to("#t2-b-in", {{ opacity: 0, scale: .96, filter: "blur(10px)", duration: .2, ease: "power2.in" }}, {L(33.25, s0)});
      WORDS("#t2-w1 .w", {L(33.55, s0)}, 0.12);
      tl.fromTo("#t2-w2 .w", {{ scale: 1.8, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: .22, ease: "power4.in", stagger: .12 }}, {L(35.40, s0)});
      OUT("#t2-w1, #t2-w2", {L(35.93, s0)});
      IN("#t2-f0", {L(36.40, s0)});
      POP("#t2-saa", {L(37.95, s0)});
      POP("#t2-akpk", {L(38.80, s0)});
      SLAM("#t2-stuck", {L(43.10, s0)}, -6);
      OUT("#t2-f0, #t2-saa, #t2-akpk, #t2-stuck", {L(44.38, s0)});
    """
    return scene_file("tip2", s0, s1, css, "\n".join(body), js)


# ================================================================ TIP 3
def build_tip3():
    s0, s1 = 44.67, 58.83
    body = [chapter("t3", 3, f'{words_html("REKOD")}<br>{words_html("BAYARAN", "y")}', s0, 44.67, 51.83,
                    extra_html='<div class="glass chip" id="t3-run" style="margin-top:30px">Ada loan sedang berjalan?</div>')]
    months = ["JAN", "FEB", "MAC", "APR", "MEI", "JUN"]
    cells = "".join(
        f'<div class="mo" id="t3-m{i}"><div class="mn">{m}</div><div class="tick {"bad" if i == 4 else ""}" id="t3-k{i}">{ICON["x" if i == 4 else "check"]}</div></div>'
        for i, m in enumerate(months))
    body.append(clip("t3-broll", 51.83, 55.45, s0, f"""
      <div class="broll" id="t3-b-in">
        <div class="bg"></div>
        <div class="head"><div class="pill" style="font-size:36px">BAYAR IKUT MASA</div></div>
        <div class="cal" id="t3-cal">{cells}</div>
        <div class="abs" style="left:0;right:0;top:860px;text-align:center">
          <div class="ttl r" id="t3-late" style="font-size:96px">LEWAT 1 BULAN</div>
          <div class="sub" id="t3-late2" style="margin-top:16px">pun boleh bagi kesan!</div>
        </div>
      </div>
    """))
    body.append(clip("t3-eff", 55.45, 58.70, s0, f"""
      <div class="band" style="top:300px">
        <div class="glass chip" id="t3-e0" style="color:#FFD21F;font-size:50px">{ICON["warn"]} AWAS</div>
        <div class="ttl" id="t3-e1" style="font-size:74px;margin-top:26px">{words_html("BERI KESAN PADA")}<br>{words_html("APPLICATION LOAN", "y")}</div>
      </div>
    """))
    css = """
    .cal { position:absolute; left:60px; right:60px; top:470px; display:grid; grid-template-columns:repeat(6, 1fr); gap:16px; }
    .mo { background:#fff; border-radius:26px; height:290px; display:flex; flex-direction:column; align-items:center; justify-content:space-around; color:#0B1430; box-shadow:0 14px 34px rgba(0,0,0,.35); }
    .mo .mn { font-weight:900; font-size:40px; }
    .mo .tick { width:96px; height:96px; }
    """
    js = f"""
      tl.fromTo("#t3-pill", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: .35, ease: "back.out(2.2)" }}, 0.05);
      WORDS("#t3-ttl .w", 0.2, 0.12);
      IN("#t3-run", {L(47.75, s0)});
      OUT("#t3-pill, #t3-ttl, #t3-run", {L(51.63, s0)});
      BROLL_IN("#t3-b-in", {L(51.83, s0)});
      IN(".mo", {L(51.90, s0)}, {{ from: {{ y: 50 }}, to: {{ stagger: .06, duration: .35 }} }});
      tl.fromTo("#t3-k0, #t3-k1, #t3-k2, #t3-k3, #t3-k5", {{ scale: 0 }}, {{ scale: 1, duration: .25, ease: "back.out(2.4)", stagger: .07 }}, {L(52.20, s0)});
      tl.fromTo("#t3-m4", {{ backgroundColor: "#ffffff" }}, {{ backgroundColor: "#FFE1E2", duration: .15 }}, {L(52.85, s0)});
      SLAM("#t3-k4", {L(52.85, s0)}, 0);
      tl.fromTo("#t3-m4", {{ x: 0 }}, {{ keyframes: [{{ x: -10, duration: .04 }}, {{ x: 9, duration: .05 }}, {{ x: -4, duration: .05 }}, {{ x: 0, duration: .05 }}] }}, {L(53.07, s0)});
      WORDS("#t3-late", {L(53.40, s0)});
      IN("#t3-late2", {L(53.85, s0)});
      tl.to("#t3-b-in", {{ opacity: 0, scale: .96, filter: "blur(10px)", duration: .2, ease: "power2.in" }}, {L(55.25, s0)});
      POP("#t3-e0", {L(55.5, s0)});
      WORDS("#t3-e1 .w", {L(55.85, s0)}, 0.1);
      OUT("#t3-e0, #t3-e1", {L(58.45, s0)});
    """
    return scene_file("tip3", s0, s1, css, "\n".join(body), js)


# ================================================================ CTA
def build_cta():
    s0, s1 = 58.83, TOTAL
    body = []
    body.append(clip("c-q", 58.90, 64.80, s0, f"""
      <div class="band" style="top:300px">
        <div class="ttl" id="c-q1" style="font-size:100px">{words_html("NAK TAHU")}</div>
        <div class="ttl y" id="c-q2" style="font-size:104px">{words_html("KORANG LAYAK?")}</div>
        <div class="glass chip" id="c-q3" style="margin-top:30px">untuk kereta yang korang minat</div>
      </div>
    """))
    body.append(clip("c-form", 64.93, TOTAL, s0, f"""
      <div class="band" style="top:300px">
        <div class="ttl" id="c-f1" style="font-size:100px">{words_html("ISI FORM")}</div>
        <div class="ttl y" id="c-f2" style="font-size:100px">{words_html("DI BAWAH")}</div>
        <div class="arrow" id="c-arrow">{ICON["arrow"]}</div>
        <div class="pill free" id="c-free">{ICON["check"]} SEMAKAN KELAYAKAN PERCUMA</div>
      </div>
    """))
    css = """
    .arrow { width:110px; height:110px; color:#FFD21F; margin-top:6px; filter:drop-shadow(0 8px 20px rgba(0,0,0,.5)); }
    .arrow svg { width:110px; height:110px; }
    .free { font-size:34px; white-space:nowrap; background:#22C55E; color:#fff; margin-top:0; padding:12px 26px; } .free svg { width:36px; height:36px; }
    """
    js = f"""
      WORDS("#c-q1 .w", {L(58.99, s0)}, 0.12);
      tl.fromTo("#c-q2 .w", {{ scale: 1.5, opacity: 0, filter: "blur(10px)" }}, {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: .3, ease: "expo.out", stagger: .14 }}, {L(60.80, s0)});
      IN("#c-q3", {L(62.40, s0)});
      OUT("#c-q1, #c-q2, #c-q3", {L(64.60, s0)});
      WORDS("#c-f1 .w", {L(65.20, s0)}, 0.14);
      WORDS("#c-f2 .w", {L(65.70, s0)}, 0.14);
      tl.fromTo("#c-arrow", {{ opacity: 0, y: -40 }}, {{ opacity: 1, y: 0, duration: .35, ease: "power3.out" }}, {L(66.00, s0)});
      tl.to("#c-arrow", {{ y: 26, duration: .32, ease: "power1.inOut", yoyo: true, repeat: 5 }}, {L(66.40, s0)});
      POP("#c-free", {L(66.60, s0)});
    """
    return scene_file("cta", s0, s1, css, "\n".join(body), js)


# ================================================================ CAPTIONS
FIX = {"ac": "IC", "setos": "CTOS", "secret": "CCRIS", "sae": "SAA", "jahatkan": "luluskan",
       "graduand": "graduan", "scheme": "skim", "sankut": "sangkut", "eventur": "walaupun"}
HL = {"reject", "reduce", "3", "dokumen", "lengkap", "payslip", "statement", "ic", "lesen", "skim", "graduan",
      "ctos", "ccris", "saa", "akpk", "sangkut", "susah", "lepas", "cantik", "lambat", "sebulan",
      "layak", "form", "percuma", "semakan", "kelayakan", "pertama", "kedua", "ketiga", "record", "effect"}


def caption_words():
    out = []
    i = 0
    while i < len(words):
        w = dict(words[i]); t = w["text"].strip()
        low = t.lower().strip(",.?")
        if low == "ac" and 13.7 < w["start"] < 14.0:
            i += 1; continue
        if low in ("okey", "so") and 58 < w["start"] < 59.5:
            i += 1; continue
        if t.startswith("-") and out:  # kadang + -kadang
            out[-1]["text"] += t; out[-1]["end"] = w["end"]; i += 1; continue
        if low == "saya" and i + 1 < len(words) and words[i + 1]["text"].strip().lower() == "makan":
            out.append({"text": "semakan", "start": w["start"], "end": words[i + 1]["end"]}); i += 2; continue
        if low == "pay" and i + 1 < len(words) and words[i + 1]["text"].strip().lower().startswith("statement"):
            t = "bank"
        elif low in FIX:
            t = FIX[low] + (t[len(low):] if len(t) > len(low) else "")
        out.append({"text": t, "start": w["start"], "end": w["end"]})
        i += 1
    return out


def build_captions():
    cw = caption_words()
    groups, cur = [], []
    for i, w in enumerate(cw):
        cur.append(w)
        nxt = cw[i + 1] if i + 1 < len(cw) else None
        chars = sum(len(x["text"]) + 1 for x in cur)
        brk = (nxt is None or len(cur) >= 3 or chars > 16 or w["text"].endswith((",", ".", "?"))
               or (nxt and nxt["start"] - w["end"] > 0.15 and len(cur) >= 2)
               or any(c in cuts for c in []))
        if brk:
            groups.append(cur); cur = []
    body, js = [], []
    for gi, g in enumerate(groups):
        st = max(0.12, g[0]["start"] - 0.03)
        nxt_st = groups[gi + 1][0]["start"] - 0.03 if gi + 1 < len(groups) else TOTAL - 0.05
        en = min(nxt_st, g[-1]["end"] + 0.6, TOTAL - 0.02)
        if en - st < 0.25:
            en = st + 0.25
        spans = []
        for wi, w in enumerate(g):
            txt = w["text"].rstrip(",.")
            cls = "hl" if txt.lower().strip("?") in HL else ""
            spans.append(f'<span class="cw {cls}" id="cg{gi}w{wi}">{esc(txt)}</span>')
        body.append(f'    <div id="cg{gi}" class="clip cg" data-start="{st:.3f}" data-duration="{en - st:.3f}"><div class="cgi" id="cg{gi}i">{" ".join(spans)}</div></div>')
        js.append(f'      tl.fromTo("#cg{gi}i", {{ scale: .82, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: .14, ease: "back.out(2)" }}, {st:.3f});')
        for wi, w in enumerate(g):
            js.append(f'      tl.fromTo("#cg{gi}w{wi}", {{ color: "#ffffff" }}, {{ color: "{"#FFD21F" if spans[wi].find("hl") > 0 else "#ffffff"}", duration: .01 }}, {max(st, w["start"]):.3f});')
    css = """
    #root { position:absolute; inset:0; pointer-events:none; }
    .cg { position:absolute; left:0; width:1080px; top:1130px; text-align:center; }
    .cgi { display:inline-block; padding:0 20px; max-width:840px; font-family:'Montserrat',sans-serif; font-weight:900; font-size:70px; line-height:1.08; color:#fff; text-transform:uppercase;
           -webkit-text-stroke: 12px #000; paint-order: stroke fill; text-shadow: 0 6px 0 rgba(0,0,0,.85), 0 10px 30px rgba(0,0,0,.6); }
    .cw { display:inline-block; }
    """
    return f"""<template>
  <style>
{css}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}" data-duration="{TOTAL}">
{chr(10).join(body)}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
""", groups


# ================================================================ INDEX
def build_index():
    # punch-in scale per jump-cut segment (alternating framing hides the jump cuts)
    seg_bounds = [0.0] + cuts
    scales = []
    for i, t in enumerate(seg_bounds):
        scales.append(1.0 if i % 2 == 0 else 1.12)
    cam_js = "\n".join(f'      tl.set("#cam", {{ scale: {s} }}, {t:.3f});' for t, s in zip(seg_bounds[1:], scales[1:]))
    sfx = [  # (id, file, time, volume)
        ("sfx-stamp1", "impact.wav", 1.09, 0.55),
        ("sfx-w1", "whoosh2.wav", 3.10, 0.35),
        ("sfx-w2", "whoosh1.wav", 6.38, 0.35),
        ("sfx-w3", "whoosh3.wav", 9.80, 0.9),
        ("sfx-p1", "pop.wav", 10.95, 0.3),
        ("sfx-p2", "pop.wav", 12.45, 0.3),
        ("sfx-p3", "pop.wav", 13.40, 0.3),
        ("sfx-w4", "whoosh2.wav", 18.45, 0.35),
        ("sfx-w5", "whoosh1.wav", 25.58, 0.35),
        ("sfx-stamp2", "impact.wav", 35.42, 0.4),
        ("sfx-w6", "whoosh3.wav", 44.65, 0.9),
        ("sfx-stamp3", "impact.wav", 43.12, 0.5),
        ("sfx-w7", "whoosh2.wav", 51.78, 0.35),
        ("sfx-stamp4", "impact.wav", 52.87, 0.4),
        ("sfx-p4", "pop.wav", 66.62, 0.35),
    ]
    sfx_html = "\n".join(
        f'      <audio id="{i}" class="clip" data-start="{t:.2f}" data-track-index="{20 + n}" src="assets/sfx/{f}" data-volume="{v}"></audio>'
        for n, (i, f, t, v) in enumerate(sfx))
    hosts = "\n".join(
        f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="{2 + n}" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:{10 + n}"></div>'
        for n, (sid, a, b) in enumerate(SCENES))
    return f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      #cam {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 590px 900px; }}
      #talk {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #scrim {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1100px; z-index: 5;
                background: linear-gradient(180deg, rgba(4,8,22,.70) 0%, rgba(4,8,22,.52) 45%, rgba(4,8,22,0) 100%); }}
      #scrim-b {{ position: absolute; left: 0; top: 1050px; width: 1080px; height: 870px; z-index: 5;
                background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,.28) 30%, rgba(0,0,0,.28) 70%, rgba(0,0,0,0) 100%); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
      <div id="cam">
        <video id="talk" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="0" src="assets/talk.mp4" playsinline data-has-audio="true" data-volume="1"></video>
      </div>
      <div id="scrim" data-layout-ignore></div>
      <div id="scrim-b" data-layout-ignore></div>
{hosts}
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL}" data-track-index="9" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:40"></div>
{sfx_html}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      // hook punch-in on "reject"
      tl.fromTo("#cam", {{ scale: 1 }}, {{ scale: 1.14, duration: .22, ease: "power3.out" }}, 1.09);
{cam_js}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


def main():
    (ROOT / "compositions").mkdir(exist_ok=True)
    for sid, fn in [("hook", build_hook), ("tip1", build_tip1), ("tip2", build_tip2), ("tip3", build_tip3), ("cta", build_cta)]:
        (ROOT / f"compositions/{sid}.html").write_text(fn())
    cap, groups = build_captions()
    (ROOT / "compositions/captions.html").write_text(cap)
    (ROOT / "index.html").write_text(build_index())
    print(f"wrote scenes; {len(groups)} caption groups")


if __name__ == "__main__":
    main()
