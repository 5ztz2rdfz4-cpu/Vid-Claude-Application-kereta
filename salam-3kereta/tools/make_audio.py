"""Synthesize the background music bed and the SFX track, timed to tools/timeline.json.

Everything here is generated from scratch (no samples), so it is royalty-free.
usage: python3 -I make_audio.py <vo.wav> <out_dir>
"""
import json
import os
import sys
import wave

import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
vo_path, out_dir = sys.argv[1], sys.argv[2]
TL = json.load(open(os.path.join(HERE, "timeline.json")))
T, B = TL["T"], TL["B"]
DUR = T["end"]
N = int(DUR * SR)
rng = np.random.default_rng(7)


# ----------------------------------------------------------------- helpers
def t_arr(d):
    return np.arange(int(d * SR)) / SR


def onepole_lp(x, fc):
    """one-pole low-pass, fc may be scalar or per-sample array"""
    fc = np.broadcast_to(np.asarray(fc, dtype=np.float64), x.shape)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def lp_fast(x, fc):
    """constant cutoff one-pole low-pass via scipy-free IIR (vectorised with lfilter-like loop in chunks)"""
    a = np.exp(-2 * np.pi * fc / SR)
    try:
        from scipy.signal import lfilter
        return lfilter([1 - a], [1, -a], x)
    except Exception:
        return onepole_lp(x, fc)


def hp_fast(x, fc):
    return x - lp_fast(x, fc)


def biquad_bp(x, f0, q):
    from scipy.signal import lfilter
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    b = [al, 0, -al]
    a = [1 + al, -2 * np.cos(w0), 1 - al]
    return lfilter(b, a, x)


def env_ad(n, a, d, curve=4.0):
    na = max(1, int(a * SR))
    e = np.zeros(n)
    e[:min(na, n)] = np.linspace(0, 1, na)[:min(na, n)]
    if n > na:
        tt = np.arange(n - na) / SR
        e[na:] = np.exp(-curve * tt / max(d, 1e-3))
    return e


def place(buf, sig, t, gain=1.0, pan=0.0):
    """add mono or stereo sig into stereo buf at time t"""
    i0 = int(round(t * SR))
    if sig.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4)
        r = np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l * 1.414, sig * r * 1.414], axis=1)
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    i1 = min(len(buf), i0 + len(sig))
    if i1 > i0:
        buf[i0:i1] += sig[: i1 - i0] * gain


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def simple_reverb(x, mix=0.25, decay=1.6):
    """cheap stereo reverb: a few feedback comb-ish delays via FFT convolution with noise IR"""
    from scipy.signal import fftconvolve
    n = int(decay * SR)
    tt = np.arange(n) / SR
    out = np.zeros((len(x) + n - 1, 2))
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-6.9 * tt / decay)
        ir = lp_fast(ir, 5500)
        ir[: int(0.012 * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
        src = x[:, ch] if x.ndim == 2 else x
        out[:, ch] = fftconvolve(src, ir)
    dry = np.zeros_like(out)
    dry[: len(x)] = x if x.ndim == 2 else np.stack([x, x], 1)
    return dry * (1 - mix) + out * mix


# ----------------------------------------------------------------- SFX
def sfx_whoosh(d=0.55, up=False):
    n = int(d * SR)
    x = rng.standard_normal(n)
    tt = np.linspace(0, 1, n)
    f = (400 + 3200 * tt ** 1.5) if up else (2600 * np.exp(-2.2 * tt) + 300)
    # time-varying band via two one-pole filters
    y = onepole_lp(x, f * 1.6) - onepole_lp(x, f * 0.5)
    e = np.sin(np.pi * np.clip(tt, 0, 1)) ** (1.2 if up else 0.8)
    if up:
        e = tt ** 2.2 * (1 - np.clip((tt - 0.9) / 0.1, 0, 1))
    y = y * e
    y /= np.max(np.abs(y)) + 1e-9
    pan = np.linspace(-0.6, 0.6, n)
    st = np.stack([y * np.cos((pan + 1) * np.pi / 4), y * np.sin((pan + 1) * np.pi / 4)], 1) * 1.4
    return st


def sfx_impact(big=True):
    d = 1.6 if big else 0.8
    tt = t_arr(d)
    f = 30 + (95 if big else 120) * np.exp(-tt * 9)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-tt * (2.6 if big else 6))
    click = rng.standard_normal(len(tt)) * np.exp(-tt * 70)
    click = lp_fast(click, 3500)
    noise = lp_fast(rng.standard_normal(len(tt)), 1200) * np.exp(-tt * 9) * 0.6
    y = body * 1.0 + click * 0.35 + noise * (0.5 if big else 0.25)
    y = np.tanh(y * 1.4)
    st = simple_reverb(y, mix=0.22 if big else 0.12, decay=1.4)
    return st / (np.max(np.abs(st)) + 1e-9)


def sfx_pop():
    tt = t_arr(0.12)
    f = 1100 * np.exp(-tt * 18) + 520
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(len(tt), 0.002, 0.05, 5)
    y += lp_fast(rng.standard_normal(len(tt)), 4000) * np.exp(-tt * 120) * 0.25
    return y / np.max(np.abs(y))


def sfx_tick():
    tt = t_arr(0.03)
    y = np.sin(2 * np.pi * 2600 * tt) * np.exp(-tt * 260) + rng.standard_normal(len(tt)) * np.exp(-tt * 500) * 0.3
    return y / np.max(np.abs(y))


def sfx_count(d=0.7):
    out = np.zeros(int((d + 0.05) * SR))
    k = 0
    t = 0.0
    while t < d:
        place2 = int(t * SR)
        tk = sfx_tick() * (0.5 + 0.5 * k % 2)
        out[place2: place2 + len(tk)] += tk[: len(out) - place2]
        k += 1
        t += 0.055 + 0.03 * (t / d) ** 2
    return out


def bell(freq, d=1.2, bright=1.0):
    tt = t_arr(d)
    y = np.zeros(len(tt))
    for ratio, amp, dec in ((1, 1, 2.2), (2.0, 0.45, 3.5), (2.76, 0.35 * bright, 4.5), (5.4, 0.18 * bright, 7), (8.9, 0.08 * bright, 10)):
        y += amp * np.sin(2 * np.pi * freq * ratio * tt) * np.exp(-tt * dec)
    y *= env_ad(len(tt), 0.002, 9, 0.01)
    return y / np.max(np.abs(y))


def sfx_ding():
    y = bell(1568, 1.0) * 0.8 + np.pad(bell(2349, 0.8), (0, int(0.2 * SR))) * 0.4
    st = simple_reverb(y, 0.25, 1.2)
    return st / np.max(np.abs(st))


def sfx_cash():
    # "cha-ching": short metallic rattle + two bright bells
    tt = t_arr(0.12)
    rattle = biquad_bp(rng.standard_normal(len(tt)), 5200, 2.5) * np.exp(-tt * 40)
    y = np.zeros(int(1.3 * SR))
    y[: len(rattle)] += rattle * 0.6
    b1 = bell(2093, 1.1)
    b2 = bell(2637, 1.0)
    o = int(0.09 * SR)
    y[o:o + len(b1)] += b1[: len(y) - o] * 0.7
    o2 = int(0.17 * SR)
    y[o2:o2 + len(b2)] += b2[: len(y) - o2] * 0.6
    st = simple_reverb(y, 0.2, 1.0)
    return st / np.max(np.abs(st))


def sfx_swipe():
    st = sfx_whoosh(0.32, up=False)
    return st * 0.8


def sfx_fill():
    # rising soft blip sweep (progress bar fill)
    tt = t_arr(0.5)
    f = 500 + 900 * (tt / 0.5) ** 1.4
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.5) ** 1.5 * 0.6
    y += 0.25 * np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * np.sin(np.pi * tt / 0.5) ** 2
    return y / np.max(np.abs(y))


def sfx_click():
    tt = t_arr(0.25)
    c = rng.standard_normal(len(tt)) * np.exp(-tt * 400)
    thump = np.sin(2 * np.pi * (180 * np.exp(-tt * 30) + 60) * tt) * np.exp(-tt * 30)
    y = lp_fast(c, 6000) * 0.6 + thump * 0.8
    return y / np.max(np.abs(y))


def sfx_riser(d=0.65):
    n = int(d * SR)
    tt = np.linspace(0, 1, n)
    x = rng.standard_normal(n)
    y = onepole_lp(x, 300 + 7000 * tt ** 2) * tt ** 2.5
    tone = np.sin(2 * np.pi * np.cumsum(200 + 700 * tt ** 2) / SR) * tt ** 3 * 0.25
    y = y / (np.max(np.abs(y)) + 1e-9) + tone
    st = np.stack([y, y], 1)
    return st / np.max(np.abs(st))


def sfx_carpass(d=1.15, soft=False):
    n = int(d * SR)
    tt = np.arange(n) / SR
    u = tt / d
    # engine: detuned saws with doppler drop around the pass point
    pass_t = 0.42
    dop = 1.12 - 0.24 / (1 + np.exp(-(u - pass_t) * 14))
    f0 = 72 * dop * (1 + 0.04 * np.sin(2 * np.pi * 9 * tt))
    ph = np.cumsum(f0) / SR
    saw = 2 * (ph % 1) - 1 + 0.6 * (2 * ((ph * 2.01) % 1) - 1)
    eng = lp_fast(saw, 700)
    tyre = onepole_lp(rng.standard_normal(n), 900 + 2200 * np.exp(-((u - pass_t) / 0.18) ** 2))
    loud = np.exp(-((u - pass_t) / 0.30) ** 2)
    y = (eng * 0.7 + tyre * 0.9) * loud
    y /= np.max(np.abs(y)) + 1e-9
    pan = np.tanh((u - pass_t) * 5) * 0.85
    st = np.stack([y * np.cos((pan + 1) * np.pi / 4), y * np.sin((pan + 1) * np.pi / 4)], 1) * 1.4
    if soft:
        st = st * 0.6
    return st


def sfx_brake():
    tt = t_arr(0.35)
    y = biquad_bp(rng.standard_normal(len(tt)), 2400, 6) * np.sin(np.pi * tt / 0.35) ** 2
    y += np.sin(2 * np.pi * 95 * tt) * np.exp(-tt * 14) * 0.6  # suspension thud
    return y / np.max(np.abs(y))


def sfx_logo_hit():
    tt = t_arr(2.6)
    sub = np.sin(2 * np.pi * np.cumsum(28 + 70 * np.exp(-tt * 7)) / SR) * np.exp(-tt * 1.6)
    # warm chord stab (D major add9) for the brand moment
    chord = np.zeros(len(tt))
    for m in (50, 57, 62, 66, 69, 76):
        f = mtof(m)
        ph = np.cumsum(np.full(len(tt), f)) / SR
        chord += (np.sin(2 * np.pi * ph) + 0.3 * np.sin(4 * np.pi * ph)) * np.exp(-tt * 1.1)
    chord = lp_fast(chord / 6, 3000)
    noise = lp_fast(rng.standard_normal(len(tt)), 2500) * np.exp(-tt * 8) * 0.4
    y = np.tanh(sub * 1.2) + chord * 0.7 + noise
    st = simple_reverb(y, 0.3, 2.2)
    return st / np.max(np.abs(st))


def sfx_shimmer():
    out = np.zeros(int(2.0 * SR))
    for k, m in enumerate((86, 90, 93, 98, 102)):
        b = bell(mtof(m), 1.4, 0.6)
        o = int(k * 0.07 * SR)
        out[o:o + len(b)] += b[: len(out) - o] * (0.8 - k * 0.1)
    st = simple_reverb(out, 0.4, 1.8)
    return st / np.max(np.abs(st))


def sfx_sparkle():
    out = np.zeros(int(1.4 * SR))
    for k, m in enumerate((98, 105, 101, 110)):
        b = bell(mtof(m), 0.6, 0.4)
        o = int(k * 0.05 * SR)
        out[o:o + len(b)] += b[: len(out) - o] * 0.6
    st = simple_reverb(out, 0.45, 1.5)
    return st / np.max(np.abs(st))


SFX = {
    "whoosh": lambda: sfx_whoosh(0.55),
    "whoosh_up": lambda: sfx_whoosh(0.6, up=True),
    "impact": lambda: sfx_impact(True),
    "impact_soft": lambda: sfx_impact(False),
    "pop": sfx_pop,
    "count": sfx_count,
    "ding": sfx_ding,
    "cash": sfx_cash,
    "swipe": sfx_swipe,
    "fill": sfx_fill,
    "click": sfx_click,
    "riser": sfx_riser,
    "carpass": sfx_carpass,
    "carpass_soft": lambda: sfx_carpass(0.9, soft=True),
    "brake": sfx_brake,
    "logo_hit": sfx_logo_hit,
    "shimmer": sfx_shimmer,
    "sparkle": sfx_sparkle,
}
cache = {}
sfx = np.zeros((N + SR * 3, 2))
for t, name, g in TL["cues"]:
    if name not in cache:
        cache[name] = SFX[name]()
    sig = cache[name]
    # whoosh/riser cues are placed so they *end* near the cut
    off = 0.0
    if name in ("riser",):
        off = -0.0
    place(sfx, sig, t + off, g)
sfx = sfx[:N]

# ----------------------------------------------------------------- MUSIC
BPM = 100.0
beat = 60 / BPM
bar = beat * 4
origin = T["intro"] - 4 * bar  # bar grid lands the drop on the intro cut
# chord progression (MIDI): Dm9, Bbmaj7, Fmaj7/A, C(add9)/G
CH = [
    ([38], [62, 65, 69, 72, 76]),
    ([34], [62, 65, 69, 70, 74]),
    ([33], [60, 64, 65, 69, 72]),
    ([31], [59, 62, 67, 69, 74]),
]
music = np.zeros((N + SR * 4, 2))


def pad_note(m, d, bright):
    tt = t_arr(d)
    f = mtof(m)
    y = np.zeros(len(tt))
    for det in (-0.08, 0.0, 0.07):
        ph = np.cumsum(np.full(len(tt), f * 2 ** (det / 12))) / SR
        y += 2 * (ph % 1) - 1
    y = lp_fast(y / 3, bright)
    e = np.minimum(1, tt / 0.35) * np.minimum(1, (d - tt) / 0.45).clip(0, 1)
    return y * e


def pluck(m, d=0.5):
    tt = t_arr(d)
    f = mtof(m)
    y = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt) + 0.12 * np.sin(6 * np.pi * f * tt)
    return y * env_ad(len(tt), 0.003, 0.28, 4.5)


def kick():
    tt = t_arr(0.45)
    f = 45 + 110 * np.exp(-tt * 28)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7)
    y += rng.standard_normal(len(tt)) * np.exp(-tt * 300) * 0.15
    return np.tanh(y * 1.5)


def clap():
    tt = t_arr(0.3)
    n = rng.standard_normal(len(tt))
    e = np.zeros(len(tt))
    for o in (0, 0.011, 0.022):
        e += (tt >= o) * np.exp(-(tt - o).clip(0) * 60) * (1 if o == 0.022 else 0.6)
    e += np.exp(-tt * 14) * 0.35
    return biquad_bp(n, 1400, 0.9) * e


def hat(open_=False):
    tt = t_arr(0.18 if open_ else 0.05)
    n = hp_fast(rng.standard_normal(len(tt)), 7000)
    return n * np.exp(-tt * (18 if open_ else 90))


K, C, H, HO = kick(), clap(), hat(), hat(True)


def add_mono(bus, sig, t):
    i0 = int(round(t * SR))
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    i1 = min(len(bus), i0 + len(sig))
    if i1 > i0:
        bus[i0:i1] += sig[: i1 - i0]
music_end = T["outro"]
pad_bus = np.zeros(N + SR * 4)
arp_bus = np.zeros(N + SR * 4)
bass_bus = np.zeros(N + SR * 4)
drum_bus = np.zeros((N + SR * 4, 2))

nbars = int((music_end - origin) / bar) + 2
for bi in range(nbars):
    t0 = origin + bi * bar
    if t0 > music_end:
        break
    roots, voicing = CH[bi % 4]
    section_hook = t0 < T["intro"] - 1e-3
    # pad
    for m in voicing[:4]:
        add_mono(pad_bus, pad_note(m, bar + 0.4, 1400 if section_hook else 2200), t0)
    # arp 8ths
    pattern = [0, 2, 1, 3, 4, 2, 3, 1]
    for k in range(8):
        tk = t0 + k * beat / 2
        if tk < 0 or tk > music_end:
            continue
        m = voicing[pattern[k]] + 12
        add_mono(arp_bus, pluck(m, 0.45) * (0.9 if k % 2 == 0 else 0.6), tk)
    # bass
    for k, (off, ln) in enumerate(((0, 1.5), (1.75, 0.5), (2.5, 1.4))):
        tk = t0 + off * beat
        if tk < 0 or tk > music_end or section_hook:
            continue
        tt = t_arr(ln * beat)
        f = mtof(roots[0] + 12)
        b = (np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(4 * np.pi * f * tt)) * env_ad(len(tt), 0.01, ln * beat, 1.2)
        add_mono(bass_bus, b, tk)
    # drums
    for k in range(16):
        tk = t0 + k * beat / 4
        if tk < 0 or tk > music_end - 0.05:
            continue
        if section_hook:
            # light pulse in the hook: kick on 1 & 3 only in the second half
            if k in (0, 8) and tk > 2.0:
                place(drum_bus, K, tk, 0.55)
            continue
        if k in (0, 6, 10):
            place(drum_bus, K, tk, 0.9 if k == 0 else 0.7)
        if k in (4, 12):
            place(drum_bus, C, tk, 0.38, 0.0)
        if k % 2 == 0:
            place(drum_bus, H, tk, 0.13 if k % 4 == 0 else 0.2, 0.3)
        if k == 14:
            place(drum_bus, HO, tk, 0.12, -0.3)

# stereo widen pad + arp with short delay
def widen(mono, ms=11):
    d = int(ms * SR / 1000)
    r = np.concatenate([np.zeros(d), mono[:-d]])
    return np.stack([mono, r], 1)


arp_delay = arp_bus.copy()
dl = int(beat * 0.75 * SR)
arp_delay[dl:] += arp_bus[:-dl] * 0.35
arp_st = widen(lp_fast(arp_delay, 5200), 7)
pad_st = widen(pad_bus, 15)
# hook arp filtered (opens at the drop)
i_drop = int(T["intro"] * SR)
for ch in range(2):
    arp_st[:i_drop, ch] = lp_fast(arp_st[:i_drop, ch], 1500)
music = pad_st * 0.16 + arp_st * 0.12 + np.stack([bass_bus, bass_bus], 1) * 0.30 + drum_bus * 0.55
music = music[:N]
# tail: everything stops at the outro hit; let the reverb of the logo hit carry it
fade_n = int(0.12 * SR)
i_out = int(music_end * SR)
music[i_out:i_out + fade_n] *= np.linspace(1, 0, fade_n)[:, None]
music[i_out + fade_n:] = 0
# outro bed: soft sustained pad chord under the logo
od = DUR - music_end
po = np.zeros(int(od * SR))
for m in (50, 57, 62, 66, 69, 74):
    p = pad_note(m, od, 1600)
    po[: len(p)] += p
po *= np.minimum(1, np.arange(len(po)) / (0.6 * SR)) * np.minimum(1, (len(po) - np.arange(len(po))) / (1.4 * SR))
place(music, widen(po * 0.12, 13), music_end + 0.2)
music = music[:N]
music[: int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))[:, None]

# ----------------------------------------------------------------- duck under VO
wf = wave.open(vo_path)
vo = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768
if wf.getframerate() != SR:
    raise SystemExit("vo must be 48k")
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
h = int(0.01 * SR)
nb = N // h
rms = np.sqrt(np.mean(vo[: nb * h].reshape(nb, h) ** 2, axis=1))
active = (20 * np.log10(rms + 1e-9) > -38).astype(float)
# smooth: fast attack 60ms, slow release 350ms
sm = np.zeros(nb)
acc = 0.0
for i in range(nb):
    target = active[i]
    coef = 0.15 if target > acc else 0.03
    acc += (target - acc) * coef
    sm[i] = acc
duck_db = -5.0 * sm
gain = 10 ** (duck_db / 20)
gain = np.repeat(gain, h)
gain = np.pad(gain, (0, N - len(gain)), constant_values=1)
music *= gain[:, None]


def write(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype(np.int16)
    w = wave.open(path, "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
    w.close()


pk_m = np.max(np.abs(music))
pk_s = np.max(np.abs(sfx))
print("music peak", pk_m, "sfx peak", pk_s)
music = music / pk_m * 0.5
sfx = sfx / max(pk_s, 1.0) * 0.85 if pk_s > 0.85 else sfx
write(os.path.join(out_dir, "music.wav"), music)
write(os.path.join(out_dir, "sfx.wav"), sfx)
print("wrote", out_dir)
