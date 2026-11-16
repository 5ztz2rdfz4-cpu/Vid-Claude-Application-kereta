"""Generates index.html (HyperFrames composition) for the TikTok 'first car' edit.

All cut points and graphic cues are written in SOURCE time (seconds in the raw
clip) and mapped onto the edited timeline, so re-timing an edit only means
changing SEGMENTS below and re-running:  python3 build/build.py
"""
import json, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = "assets/video/aroll.mp4"

# (src_in, src_out, mode, zoom)   mode: face | info
SEGMENTS = [
    (61.98, 65.83, "face", 1.06),  # S0  cold-open hook
    (0.00, 5.26, "face", 1.00),    # S1  "Tiga benda penting..."
    (5.98, 15.79, "face", 1.10),   # S2  #1 kegunaan  (-> info at 9.1)
    (17.29, 24.96, "face", 1.00),  # S3  jenis kereta (-> info at 20.4)
    (24.96, 36.55, "face", 1.08),  # S4  #2 kos
    (36.62, 39.55, "info", 1.00),  # S5  4 kos
    (42.55, 44.05, "info", 1.00),  # S6  bulanan
    (44.95, 47.37, "info", 1.00),  # S7  service
    (47.66, 49.97, "info", 1.00),  # S8  maintenance
    (50.20, 55.27, "info", 1.00),  # S9  expenses
    (56.81, 61.98, "face", 1.00),  # S10 #3 kemampuan
    (61.98, 67.06, "face", 1.10),  # S11 gaji 1700 S70 X50
    (70.56, 72.81, "face", 1.00),  # S12 ukur baju
    (72.91, 78.20, "info", 1.00),  # S13 walaupun gaji...
    (78.34, 84.14, "info", 1.00),  # S14 Saga A->B
    (84.86, 97.10, "face", 1.06),  # S15 CTA
]
ENDCARD_EXTRA = 2.2

segs = []
t = 0.0
for i, (a, b, mode, z) in enumerate(SEGMENTS):
    segs.append(dict(i=i, a=a, b=b, mode=mode, z=z, o=round(t, 3)))
    t += b - a
VIDEO_END = round(t, 3)
TOTAL = round(VIDEO_END + ENDCARD_EXTRA, 3)


def o(src, seg=None):
    """Map a source time to output time. seg pins a specific segment (needed
    because S0 and S11 share source material)."""
    cands = [segs[seg]] if seg is not None else segs
    for s in cands:
        if s["a"] - 0.05 <= src <= s["b"] + 0.05:
            return round(s["o"] + (min(max(src, s["a"]), s["b"]) - s["a"]), 3)
    raise ValueError(f"src {src} not in edit")


def so(i):
    return segs[i]["o"]


def se(i):
    return round(segs[i]["o"] + segs[i]["b"] - segs[i]["a"], 3)


# ---------------------------------------------------------------- captions
FIX = {
    "mengandung": "mengada-ngada", "-andung": None, "S50": "X50", "sagar,": "Saga,",
    "Air": "Saga", "strong": None, "alat": None, "ulang": "ulang-alik", "Insya": "Insya-Allah",
    "'Allah": None, ",700": None, "RM1": "RM1,700", "-patah,": None, "-tua": None,
}
words = []
for seg in json.load(open(os.path.join(HERE, "transcript.json"))):
    for w in seg["words"]:
        raw = w["w"].strip()
        trail = ""
        if raw in FIX:
            rep = FIX[raw]
            if rep is None:
                if raw == ",700" and words:
                    pass
                if raw.endswith(",") and words:
                    words[-1]["w"] += ","
                if raw in ("'Allah",) and words:
                    pass
                if words:
                    words[-1]["e"] = w["e"]
                continue
            # keep punctuation that followed in following token
            raw = rep
        words.append(dict(w=raw, s=w["s"], e=w["e"]))
# RM1,700 punctuation & kerja comma kept as is

PUNCT_END = re.compile(r"[.,?!]$")


def caption_groups():
    groups = []
    for s in segs:
        if s["i"] == 0:
            continue  # hook has its own big titles
        ws = [w for w in words if w["s"] >= s["a"] - 0.08 and w["s"] < s["b"] - 0.05]
        cur = []
        for w in ws:
            ow = dict(w=w["w"], s=o(max(w["s"], s["a"]), s["i"]), e=o(min(w["e"], s["b"]), s["i"]))
            if cur:
                chars = sum(len(x["w"]) + 1 for x in cur) + len(ow["w"])
                gap = ow["s"] - cur[-1]["e"]
                if chars > 17 or len(cur) >= 3 or gap > 0.32 or PUNCT_END.search(cur[-1]["w"]):
                    groups.append(cur)
                    cur = []
            cur.append(ow)
        if cur:
            groups.append(cur)
    # timing: show until next group start (max 1.2s after last word), clamp to segment
    out = []
    for gi, g in enumerate(groups):
        start = g[0]["s"]
        end = g[-1]["e"] + 0.25
        if gi + 1 < len(groups):
            end = min(end, groups[gi + 1][0]["s"])
        out.append(dict(start=round(start, 3), end=round(max(end, start + 0.3), 3), words=g))
    return out


CAPS = caption_groups()
# stop captions before end card
CAPS = [c for c in CAPS if c["start"] < VIDEO_END - 0.05]
for c in CAPS:
    c["end"] = min(c["end"], VIDEO_END)


def clean(w):
    return w.rstrip(",.").upper()


# ------------------------------------------------------------------- icons
ICON = {
    "briefcase": '<rect x="8" y="20" width="48" height="34" rx="6"/><path d="M24 20v-6a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v6M8 34h48"/>',
    "box": '<path d="M32 6 56 18v28L32 58 8 46V18z"/><path d="M8 18l24 12 24-12M32 30v28"/>',
    "parking": '<rect x="8" y="8" width="48" height="48" rx="10"/><path d="M25 46V18h9a8 8 0 0 1 0 16h-9"/>',
    "calendar": '<rect x="8" y="12" width="48" height="44" rx="6"/><path d="M8 24h48M20 6v12M44 6v12M20 36h6M30 36h6M40 36h6M20 46h6M30 46h6"/>',
    "wrench": '<path d="M41 8a14 14 0 0 0-13 18L9 45a5 5 0 0 0 8 8l19-19a14 14 0 0 0 18-13l-8 7-7-1-2-7z"/>',
    "gear": '<circle cx="32" cy="32" r="8"/><circle cx="32" cy="32" r="18"/><path d="M32 6v8M32 50v8M6 32h8M50 32h8M13.6 13.6l5.7 5.7M44.7 44.7l5.7 5.7M13.6 50.4l5.7-5.7M44.7 19.3l5.7-5.7"/>',
    "fuel": '<rect x="10" y="10" width="28" height="46" rx="4"/><path d="M10 26h28M38 22l10 6v20a4 4 0 0 0 8 0V20l-8-8"/>',
    "wallet": '<rect x="6" y="16" width="52" height="38" rx="6"/><path d="M6 26h40M46 35h12v10H46a5 5 0 0 1 0-10z"/>',
    "smile": '<circle cx="32" cy="32" r="24"/><path d="M22 38a12 12 0 0 0 20 0M24 26h.01M40 26h.01"/>',
    "check": '<path d="M14 34l12 12 24-26"/>',
    "cross": '<path d="M18 18l28 28M46 18L18 46"/>',
    "down": '<path d="M32 8v44M14 36l18 18 18-18"/>',
    "salary": '<rect x="6" y="14" width="52" height="36" rx="6"/><circle cx="32" cy="32" r="8"/><path d="M14 22h.01M50 42h.01"/>',
}


def icon(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg>'


CARS = {
    "SUV": ('M8 60 L8 42 Q10 35 28 33 L60 30 L80 13 Q84 10 96 10 L158 11 Q168 12 174 21 L186 36 Q192 40 192 48 L192 60 Z M98 4 L160 5 L160 8 L98 7 Z',
            'M86 17 L96 16 L124 16 L124 29 L70 29 Z M130 16 L156 16 Q164 17 168 23 L172 29 L130 29 Z', (52, 156), 17),
    "MPV": ('M8 64 L8 46 Q9 40 18 36 L40 10 Q45 5 58 5 L182 5 Q190 5 191 14 L193 44 L193 64 Z',
            'M46 12 L58 10 L92 10 L92 31 L30 31 Z M98 10 L136 10 L136 31 L98 31 Z M142 10 L184 10 Q186 10 186 16 L187 31 L142 31 Z', (46, 162), 13),
    "SEDAN": ('M6 64 L6 50 Q8 43 28 41 L56 38 L76 22 Q81 18 96 18 L132 18 Q142 18 151 28 L162 38 L186 42 Q194 44 194 52 L194 64 Z',
              'M82 24 L96 23 L110 23 L110 37 L66 37 Z M116 23 L132 23 Q140 23 146 30 L152 37 L116 37 Z', (50, 156), 13),
    "HATCHBACK": ('M30 64 L30 48 Q32 42 48 40 L72 24 Q78 19 92 19 L130 19 Q140 20 148 28 L166 44 Q170 48 170 54 L170 64 Z',
                  'M78 25 L92 24 L112 24 L112 37 L62 37 Z M118 24 L130 24 Q138 25 144 31 L150 37 L118 37 Z', (62, 144), 13),
}


def car_svg(name):
    body, win, (w1, w2), r = CARS[name]
    return (f'<svg class="car" viewBox="0 0 200 90">'
            f'<ellipse cx="100" cy="82" rx="92" ry="5" fill="rgba(0,0,0,.35)"/>'
            f'<path d="{body}" fill="#FFD21F"/><path d="{win}" fill="#0E131C" opacity=".85"/>'
            f'<circle cx="{w1}" cy="66" r="{r}" fill="#0E131C"/><circle cx="{w1}" cy="66" r="{r*0.45:.1f}" fill="#9aa4b2"/>'
            f'<circle cx="{w2}" cy="66" r="{r}" fill="#0E131C"/><circle cx="{w2}" cy="66" r="{r*0.45:.1f}" fill="#9aa4b2"/>'
            f'</svg>')


# --------------------------------------------------------------- builders
els = []      # html chunks
js = []       # gsap lines
sfx = []      # (time, name, vol)
uid = [0]


def nid(p):
    uid[0] += 1
    return f"{p}{uid[0]}"


def clip(id_, start, end, inner, cls="", style=""):
    els.append(f'<div id="{id_}" class="clip {cls}" data-start="{start:.3f}" data-duration="{end-start:.3f}" style="{style}">{inner}</div>')


def T(x):
    return f"{x:.3f}"


# ---- video clips
for s in segs:
    dur = s["b"] - s["a"]
    els.append(
        f'<video id="v{s["i"]}" class="clip vid" src="{SRC}" data-start="{s["o"]:.3f}" data-duration="{dur:.3f}" '
        f'data-media-start="{s["a"]:.3f}" data-fade-in="0.03" data-fade-out="0.04" data-has-audio="true" playsinline></video>')
    js.append(f'tl.set("#camzoom",{{scale:{s["z"]}}},{T(s["o"])});')

# ---- mode switches (face <-> info)
PIP_CLIP = "inset(500px 170px 740px 170px round 44px)"
FULL_CLIP = "inset(0px 0px 0px 0px round 0px)"
info_ranges = []  # (enter, exit)


def info(enter, exit_):
    info_ranges.append((enter, exit_))
    js.append(f'tl.to("#cam",{{clipPath:"{PIP_CLIP}",scale:0.62,y:430,duration:0.5,ease:"power3.inOut"}},{T(enter)});')
    js.append(f'tl.to("#pipframe",{{opacity:1,duration:0.15}},{T(enter+0.4)});')
    js.append(f'tl.to("#caps",{{y:220,duration:0.4,ease:"power2.inOut"}},{T(enter+0.05)});')
    js.append(f'tl.to("#pipframe",{{opacity:0,duration:0.1}},{T(exit_-0.02)});')
    js.append(f'tl.to("#cam",{{clipPath:"{FULL_CLIP}",scale:1,y:0,duration:0.45,ease:"power3.inOut"}},{T(exit_)});')
    js.append(f'tl.to("#caps",{{y:0,duration:0.35,ease:"power2.inOut"}},{T(exit_)});')
    sfx.append((enter - 0.05, "whoosh", 0.35))
    sfx.append((exit_ - 0.08, "whoosh", 0.25))


def info_header(start, end, num, title, sub):
    id_ = nid("ih")
    inner = (f'<div class="ihead"><div class="inum">{num}</div><div class="itxt">'
             f'<div class="ititle">{title}</div><div class="isub">{sub}</div></div></div>')
    clip(id_, start, end, inner, "layer")
    js.append(f'tl.from("#{id_} .inum",{{scale:0.3,opacity:0,duration:0.45,ease:"back.out(2)"}},{T(start+0.25)});')
    js.append(f'tl.from("#{id_} .ititle",{{x:-60,opacity:0,duration:0.4,ease:"power3.out"}},{T(start+0.35)});')
    js.append(f'tl.from("#{id_} .isub",{{x:-60,opacity:0,duration:0.4,ease:"power3.out"}},{T(start+0.45)});')
    js.append(f'tl.to("#{id_}",{{opacity:0,duration:0.2}},{T(end-0.2)});')


def topcard(start, end, inner, cls="", pop=True):
    id_ = nid("tc")
    clip(id_, start, end, f'<div class="topcard {cls}">{inner}</div>', "layer")
    js.append(f'tl.from("#{id_} .topcard",{{y:-40,opacity:0,scale:0.92,duration:0.38,ease:"back.out(1.6)"}},{T(start)});')
    js.append(f'tl.to("#{id_} .topcard",{{y:-30,opacity:0,duration:0.22,ease:"power2.in"}},{T(end-0.22)});')
    if pop:
        sfx.append((start, "pop", 0.35))
    return id_


# =============================================================== S0 HOOK
s0, e0 = so(0), se(0)
hook = (
    '<div class="hookshade"></div>'
    '<div class="hookchip">TIPS BELI KERETA PERTAMA</div>'
    '<div class="hl hl1">GAJI <span class="y">RM1,700</span></div>'
    '<div class="hl hl2">NAK PAKAI <span class="s70">S70?</span></div>'
    '<div class="stamp">JANGAN!</div>'
)
clip("hook", s0, e0, hook, "layer")
js.append(f'tl.fromTo("#camzoom",{{scale:1.04}},{{scale:1.16,duration:{e0-s0:.3f},ease:"none"}},{T(s0)});')
js.append(f'tl.from("#hook .hookchip",{{y:-30,opacity:0,duration:0.3,ease:"power3.out"}},{T(s0)});')
js.append(f'tl.from("#hook .stamp",{{scale:2.6,opacity:0,rotation:-20,duration:0.28,ease:"power4.in"}},{T(o(62.18,0)-0.1)});')
sfx.append((o(62.18, 0) + 0.15, "thud", 0.6))
js.append(f'tl.from("#hook .hl1",{{x:-120,opacity:0,duration:0.32,ease:"power3.out"}},{T(o(62.62,0))});')
js.append(f'tl.from("#hook .hl2",{{x:120,opacity:0,duration:0.32,ease:"power3.out"}},{T(o(64.15,0))});')
js.append(f'tl.fromTo("#hook .s70",{{color:"#ffffff"}},{{color:"#FF3B3B",scale:1.12,duration:0.2}},{T(o(64.78,0))});')
sfx.append((o(62.62, 0), "pop", 0.3))
sfx.append((o(64.15, 0), "pop", 0.3))
# flash into the title
els.append(f'<div id="flash" class="clip layer" data-start="{e0-0.12:.3f}" data-duration="0.4"></div>')
js.append(f'tl.fromTo("#flash",{{opacity:0}},{{opacity:0.9,duration:0.1}},{T(e0-0.12)});')
js.append(f'tl.to("#flash",{{opacity:0,duration:0.25}},{T(e0-0.02)});')
sfx.append((e0 - 0.3, "whoosh", 0.45))

# =============================================================== S1 TITLE
s1, e1 = so(1), se(1)
title = (
    '<div class="titlecard">'
    '<div class="tbig"><span class="t3">3</span> BENDA</div>'
    '<div class="tline tl1">WAJIB TAHU SEBELUM</div>'
    '<div class="tline tl2"><span class="ybox">BELI FIRST CAR</span></div>'
    '<div class="dots"><span>1</span><span>2</span><span>3</span></div>'
    '</div>'
)
clip("title", s1, e1, title, "layer")
js.append(f'tl.from("#title .tbig",{{scale:0.4,opacity:0,duration:0.45,ease:"back.out(2)"}},{T(s1+0.05)});')
js.append(f'tl.from("#title .tl1",{{y:30,opacity:0,duration:0.35,ease:"power3.out"}},{T(o(2.48,1)-0.1)});')
js.append(f'tl.from("#title .tl2",{{y:30,opacity:0,scale:0.8,duration:0.4,ease:"back.out(2)"}},{T(o(4.2,1)-0.1)});')
js.append(f'tl.from("#title .dots span",{{scale:0,opacity:0,duration:0.3,stagger:0.12,ease:"back.out(3)"}},{T(o(4.6,1))});')
js.append(f'tl.to("#title .titlecard",{{y:-30,opacity:0,duration:0.22}},{T(e1-0.22)});')
sfx.append((s1 + 0.05, "thud", 0.45))
sfx.append((o(4.2, 1) - 0.1, "pop", 0.3))

# =============================================================== S2 #1 kegunaan
s2 = so(2)
INFO1_IN = o(9.05, 2)
topcard(s2 + 0.05, INFO1_IN + 0.1,
        '<div class="tcnum">#1</div><div class="tctext">KEGUNAAN<br><span class="y">KERETA</span></div>', "row")
info(INFO1_IN, so(3))
info_header(INFO1_IN, so(3), "01", "KEGUNAAN KERETA", "Kereta ni untuk apa?")
uses = [("briefcase", "Ulang-alik <b>kerja</b>", 10.75), ("box", "Bawa barang <b>banyak</b>", 12.10),
        ("parking", "Senang masuk <b>parking</b>", 14.35)]
for k, (ic, txt, at) in enumerate(uses):
    id_ = nid("use")
    clip(id_, o(at, 2), so(3), f'<div class="irow" style="top:{430 + k*205}px">{icon(ic)}<div class="irtxt">{txt}</div></div>', "layer")
    js.append(f'tl.from("#{id_} .irow",{{x:-140,opacity:0,duration:0.4,ease:"back.out(1.5)"}},{T(o(at,2))});')
    sfx.append((o(at, 2), "pop", 0.35))

# =============================================================== S3 jenis kereta
s3 = so(3)
INFO2_IN = o(20.35, 3)
topcard(o(17.95, 3), INFO2_IN + 0.1,
        '<div class="tcsmall">KEGUNAAN</div><div class="tcarrow">↓</div><div class="tcmid">TENTUKAN <span class="y">JENIS KERETA</span></div>', "stack")
info(INFO2_IN, so(4))
info_header(INFO2_IN, so(4), "01", "PILIH JENIS KERETA", "Ikut kegunaan korang")
types = [("SUV", 20.62), ("MPV", 21.95), ("SEDAN", 23.08), ("HATCHBACK", 24.10)]
for k, (nm, at) in enumerate(types):
    id_ = nid("car")
    x = 70 + (k % 2) * 480
    y = 420 + (k // 2) * 310
    clip(id_, o(at, 3), so(4), f'<div class="carcard" style="left:{x}px;top:{y}px">{car_svg(nm)}<div class="carname">{nm}</div></div>', "layer")
    js.append(f'tl.from("#{id_} .carcard",{{scale:0.5,opacity:0,y:40,duration:0.38,ease:"back.out(1.8)"}},{T(o(at,3))});')
    js.append(f'tl.from("#{id_} .car",{{x:-80,duration:0.6,ease:"power3.out"}},{T(o(at,3))});')
    sfx.append((o(at, 3), "pop", 0.35))

# =============================================================== S4 #2 kos
s4 = so(4)
topcard(s4 + 0.08, o(29.15, 4),
        '<div class="tcnum">#2</div><div class="tctext">KOS <span class="y">SEBENAR</span><br>KERETA</div>', "row")
q_id = topcard(o(29.25, 4), o(34.0, 4),
               '<div class="tcmid">KOS KERETA =</div><div class="tcbig">BULANAN JE<span class="y">?</span></div>', "stack")
st_id = nid("st")
clip(st_id, o(34.0, 4), se(4), '<div class="bigstamp">MINDSET SALAH ✕</div>', "layer")
js.append(f'tl.from("#{st_id} .bigstamp",{{scale:2.4,opacity:0,rotation:-14,duration:0.26,ease:"power4.in"}},{T(o(34.0,4))});')
sfx.append((o(34.0, 4) + 0.2, "thud", 0.6))
js.append(f'tl.to("#camzoom",{{scale:1.24,duration:0.22,ease:"power3.out"}},{T(o(35.68,4))});')

# =============================================================== S5-S9 4 kos (info)
INFO3_IN = so(5)
INFO3_OUT = so(10)
info(INFO3_IN, INFO3_OUT)
info_header(INFO3_IN, INFO3_OUT, "02", "4 KOS SEBENAR KERETA", "Bukan bayar bulanan je")
costs = [("calendar", "BULANAN", "Bayaran ansuran bank", o(42.6, 6)),
         ("wrench", "SERVIS", "Ikut jadual servis berkala", o(45.0, 7)),
         ("gear", "MAINTENANCE", "Baiki & tukar alat ganti", o(47.7, 8)),
         ("fuel", "EXPENSES", "Wear &amp; tear + duit minyak", o(50.3, 9))]
slot_t = o(38.2, 5)
for k, (ic, ttl, sub, at) in enumerate(costs):
    top = 420 + k * 152
    sid = nid("slot")
    clip(sid, slot_t, INFO3_OUT, f'<div class="slot" data-layout-ignore style="top:{top}px"><div class="snum">{k+1}</div></div>', "layer")
    js.append(f'tl.from("#{sid} .slot",{{opacity:0,x:60,duration:0.3,ease:"power2.out"}},{T(slot_t + k*0.08)});')
    cid = nid("cost")
    clip(cid, at, INFO3_OUT,
         f'<div class="costrow" style="top:{top}px"><div class="cnum">{k+1}</div>{icon(ic,"cic")}'
         f'<div class="ctxt"><div class="ct">{ttl}</div><div class="cs">{sub}</div></div></div>', "layer")
    js.append(f'tl.from("#{cid} .costrow",{{scaleX:0.2,opacity:0,duration:0.35,ease:"power3.out",transformOrigin:"left center"}},{T(at)});')
    js.append(f'tl.from("#{cid} .ctxt, #{cid} .cic",{{opacity:0,x:-20,duration:0.25,stagger:0.05}},{T(at+0.15)});')
    sfx.append((at, "pop", 0.4))
sub_t = o(52.96, 9)
js.append(f'tl.fromTo("#cost{uid[0]} .cs",{{color:"#c9d1dc"}},{{color:"#FFD21F",duration:0.2}},{T(sub_t)});')
js.append(f'tl.to(".costrow",{{borderColor:"#FFD21F",scale:1.03,duration:0.18,stagger:0.08,yoyo:true,repeat:1}},{T(o(54.3,9))});')
sfx.append((o(54.3, 9), "ding", 0.3))

# =============================================================== S10 #3
s10 = so(10)
topcard(o(57.3, 10), se(10),
        '<div class="tcnum">#3</div><div class="tctext">KEMAMPUAN<br><span class="y">&amp; KELAYAKAN</span></div>', "row")

# =============================================================== S11 gaji vs S70/X50
s11 = so(11)
gid = nid("gaji")
inner = ('<div class="topcard vs"><div class="vsl"><div class="vlab">GAJI</div><div class="vval">RM1,700</div></div>'
         '<div class="vsmid">VS</div><div class="vsr"><div class="vcar c1">S70<i class="strike"></i></div><div class="vcar c2">X50<i class="strike"></i></div></div></div>')
clip(gid, o(62.6, 11), se(11), inner, "layer")
js.append(f'tl.from("#{gid} .topcard",{{y:-40,opacity:0,duration:0.35,ease:"back.out(1.6)"}},{T(o(62.6,11))});')
js.append(f'tl.from("#{gid} .vsmid",{{scale:0,duration:0.3,ease:"back.out(3)"}},{T(o(64.2,11))});')
js.append(f'tl.from("#{gid} .c1",{{x:60,opacity:0,duration:0.3,ease:"power3.out"}},{T(o(64.7,11))});')
js.append(f'tl.from("#{gid} .c2",{{x:60,opacity:0,duration:0.3,ease:"power3.out"}},{T(o(66.0,11))});')
js.append(f'tl.to("#{gid} .vcar",{{color:"#FF3B3B",duration:0.1}},{T(o(66.6,11))});')
js.append(f'tl.fromTo("#{gid} .strike",{{scaleX:0}},{{scaleX:1,duration:0.25,ease:"power2.out"}},{T(o(66.6,11))});')
js.append(f'tl.to("#{gid} .topcard",{{opacity:0,duration:0.15}},{T(se(11)-0.15)});')
sfx += [(o(62.6, 11), "pop", 0.3), (o(64.7, 11), "pop", 0.3), (o(66.0, 11), "pop", 0.3), (o(66.6, 11), "thud", 0.45)]

# =============================================================== S12 quote
s12 = so(12)
qid = topcard(s12 + 0.02, se(12),
              '<div class="quote">“</div><div class="qtxt">UKUR BAJU DI<br><span class="y">BADAN SENDIRI</span></div>', "stack quotecard")
js.append(f'tl.fromTo("#camzoom",{{scale:1.0}},{{scale:1.14,duration:{se(12)-s12:.3f},ease:"power1.inOut"}},{T(s12)});')

# =============================================================== S13-14 info: kemampuan
INFO4_IN = so(13)
INFO4_OUT = o(85.95, 15)
info(INFO4_IN, INFO4_OUT)
info_header(INFO4_IN, INFO4_OUT, "03", "PILIH IKUT KEMAMPUAN", "Ukur baju di badan sendiri")
a1 = o(73.5, 13)
id_ = nid("k")
clip(id_, a1, INFO4_OUT,
     f'<div class="kcard" style="top:420px">{icon("salary","kic")}<div class="ktxt"><div class="kt">GAJI RM1,700?</div>'
     f'<div class="ks">{icon("check","mini")} Masih boleh apply kereta</div></div></div>', "layer")
js.append(f'tl.from("#{id_} .kcard",{{x:-120,opacity:0,duration:0.4,ease:"back.out(1.5)"}},{T(a1)});')
js.append(f'tl.from("#{id_} .ks",{{opacity:0,y:10,duration:0.3}},{T(o(75.2,13))});')
sfx += [(a1, "pop", 0.35), (o(75.2, 13), "pop", 0.3)]
a2 = o(76.5, 13)
id_ = nid("saga")
route = ('<div class="route"><div class="pt pa">A</div><div class="track"><div class="fill"></div>'
         '<svg class="minicar" viewBox="0 0 200 90"><path d="M6 64 L6 50 Q8 43 28 41 L56 38 L76 22 Q81 18 96 18 L132 18 Q142 18 151 28 L162 38 L186 42 Q194 44 194 52 L194 64 Z" fill="#FFD21F"/>'
         '<circle cx="50" cy="66" r="13" fill="#0E131C"/><circle cx="156" cy="66" r="13" fill="#0E131C"/></svg></div><div class="pt pb">B</div></div>')
clip(id_, a2, INFO4_OUT,
     f'<div class="sagacard" style="top:640px"><div class="sgtop"><span class="sgl">PILIHAN BIJAK</span><span class="sgn">PROTON SAGA</span></div>{route}</div>', "layer")
js.append(f'tl.from("#{id_} .sagacard",{{scale:0.6,opacity:0,duration:0.4,ease:"back.out(1.7)"}},{T(a2)});')
r0, r1 = o(79.3, 14), o(80.9, 14)
js.append(f'tl.fromTo("#{id_} .fill",{{scaleX:0}},{{scaleX:1,duration:{r1-r0:.3f},ease:"power1.inOut"}},{T(r0)});')
js.append(f'tl.fromTo("#{id_} .minicar",{{x:0}},{{x:470,duration:{r1-r0:.3f},ease:"power1.inOut"}},{T(r0)});')
js.append(f'tl.fromTo("#{id_} .pb",{{scale:1}},{{scale:1.25,backgroundColor:"#22D07A",duration:0.2,yoyo:true,repeat:1}},{T(r1-0.05)});')
sfx += [(a2, "thud", 0.4), (r1, "ding", 0.25)]
for k, (ic, txt, at) in enumerate([("wallet", "Poket <b>selamat</b>", 82.1), ("smile", "Tak <b>sakit kepala</b>", 83.35)]):
    id_ = nid("ok")
    at_o = o(at, 14)
    clip(id_, at_o, INFO4_OUT,
         f'<div class="okrow" style="top:{905 + 0}px;left:{70 + k*480}px">{icon(ic,"oic")}<div class="oktxt">{txt}</div>{icon("check","okc")}</div>', "layer")
    js.append(f'tl.from("#{id_} .okrow",{{y:40,opacity:0,duration:0.35,ease:"back.out(1.8)"}},{T(at_o)});')
    sfx.append((at_o, "pop", 0.35))

# =============================================================== S15 CTA
s15 = so(15)
topcard(o(86.2, 15), o(88.85, 15),
        '<div class="tcmid">NAK CARI</div><div class="tcbig y">FIRST CAR?</div>', "stack")
cta = nid("cta")
clip(cta, o(88.85, 15), VIDEO_END,
     f'<div class="ctacard"><div class="ctabtn">ISI FORM DI BAWAH</div><div class="ctaarrow">{icon("down","arr")}</div>'
     f'<div class="ctasub">Kami bantu dapatkan first car<br>yang sesuai — <span class="y">dari A sampai Z</span></div></div>', "layer")
js.append(f'tl.from("#{cta} .ctabtn",{{scale:0.4,opacity:0,duration:0.4,ease:"back.out(2)"}},{T(o(88.85,15))});')
js.append(f'tl.from("#{cta} .ctaarrow",{{opacity:0,duration:0.2}},{T(o(89.2,15))});')
for k in range(5):
    js.append(f'tl.to("#{cta} .arr",{{y:22,duration:0.35,yoyo:true,repeat:1,ease:"sine.inOut"}},{T(o(89.2,15)+k*0.75)});')
js.append(f'tl.from("#{cta} .ctasub",{{y:20,opacity:0,duration:0.35}},{T(o(90.7,15))});')
sfx += [(o(88.85, 15), "ding", 0.3)]

# =============================================================== END CARD
ec_s = o(95.95, 15)
endc = ('<div class="endbg"></div><div class="endwrap">'
        '<div class="endsmall">SIMPAN VIDEO NI &amp; SHARE</div>'
        '<div class="endbig">FOLLOW</div>'
        '<div class="endmid">untuk lebih banyak <span class="y">tips kereta</span></div>'
        '<div class="ctabtn endbtn">ISI FORM DI BAWAH ↓</div></div>')
clip("endcard", ec_s, TOTAL, endc, "layer")
js.append(f'tl.from("#endcard .endbg",{{opacity:0,duration:0.35}},{T(ec_s)});')
js.append(f'tl.from("#endcard .endsmall",{{y:30,opacity:0,duration:0.3}},{T(ec_s+0.15)});')
js.append(f'tl.from("#endcard .endbig",{{scale:0.5,opacity:0,duration:0.4,ease:"back.out(2)"}},{T(ec_s+0.25)});')
js.append(f'tl.from("#endcard .endmid",{{y:30,opacity:0,duration:0.3}},{T(ec_s+0.4)});')
js.append(f'tl.from("#endcard .endbtn",{{scale:0.6,opacity:0,duration:0.35,ease:"back.out(2)"}},{T(ec_s+0.55)});')
sfx.append((ec_s + 0.25, "whoosh", 0.35))

# ---- captions
cap_html = []
for ci, c in enumerate(CAPS):
    cid = f"cap{ci}"
    spans = "".join(f'<span class="w" id="{cid}w{wi}">{html.escape(clean(w["w"]))}</span>' for wi, w in enumerate(c["words"]))
    cap_html.append(f'<div id="{cid}" class="clip cap" data-start="{c["start"]:.3f}" data-duration="{c["end"]-c["start"]:.3f}"><div class="capline">{spans}</div></div>')
    js.append(f'tl.from("#{cid} .capline",{{scale:0.82,opacity:0,duration:0.12,ease:"back.out(2)"}},{T(c["start"])});')
    for wi, w in enumerate(c["words"]):
        js.append(f'tl.set("#{cid}w{wi}",{{backgroundColor:"#FFD21F",color:"#111111",webkitTextStrokeWidth:"0px",textShadow:"none"}},{T(w["s"])});')
        if wi < len(c["words"]) - 1:
            js.append(f'tl.set("#{cid}w{wi}",{{backgroundColor:"rgba(0,0,0,0)",color:"#ffffff",webkitTextStrokeWidth:"12px",textShadow:"0 6px 18px rgba(0,0,0,.55)"}},{T(c["words"][wi+1]["s"])});')

# ---- sfx audio
sfx_html = []
for k, (at, name, vol) in enumerate(sorted(sfx)):
    at = max(0.0, at)
    dur = {"whoosh": 0.55, "pop": 0.12, "thud": 0.4, "ding": 0.9}[name]
    if at + dur > TOTAL:
        continue
    sfx_html.append(f'<audio id="sfx{k}" class="clip" src="assets/sfx/{name}.wav" data-start="{at:.3f}" data-duration="{dur:.3f}" data-volume="{vol}"></audio>')

# ---- progress bar
js.append(f'tl.fromTo("#progress",{{scaleX:0}},{{scaleX:1,duration:{VIDEO_END:.3f},ease:"none"}},0);')

videos = [e for e in els if e.startswith("<video")]
layers = [e for e in els if not e.startswith("<video")]

tpl = open(os.path.join(HERE, "template.html")).read()
out = (tpl.replace("{{TOTAL}}", f"{TOTAL:.3f}")
          .replace("{{VIDEOS}}", "\n        ".join(videos))
          .replace("{{LAYERS}}", "\n      ".join(layers))
          .replace("{{CAPS}}", "\n        ".join(cap_html))
          .replace("{{SFX}}", "\n      ".join(sfx_html))
          .replace("{{JS}}", "\n      ".join(js)))
open(os.path.join(ROOT, "index.html"), "w").write(out)
json.dump(dict(segments=segs, total=TOTAL, captions=len(CAPS), info=info_ranges), open(os.path.join(HERE, "edit_map.json"), "w"), indent=1)
print("total", TOTAL, "video", VIDEO_END, "captions", len(CAPS), "sfx", len(sfx_html))
