"""Synthesize original background music + sound effects and mix them under the voiceover.

usage: python3 make_audio.py cues.json vo.wav out_mix.wav [stems_dir]
Everything here is generated from scratch (no samples), so it is royalty-free.
"""
import json, sys, os
import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
rng = np.random.default_rng(7)
cues = json.load(open(sys.argv[1]))
vo, vsr = sf.read(sys.argv[2])
assert vsr == SR
if vo.ndim == 1:
    vo = np.stack([vo, vo], 1)
END = cues["END"]
N = int(END * SR)
stems = sys.argv[4] if len(sys.argv) > 4 else None


# ---------------------------------------------------------------- helpers
def t_arr(d):
    return np.arange(int(d * SR)) / SR


def env_adsr(n, a=0.005, d=0.1, s=0.0, r=0.05, sus_len=None):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    if sus_len is None:
        sus_len = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([
        np.linspace(0, 1, max(a_n, 1)),
        np.linspace(1, s, max(d_n, 1)),
        np.full(max(int(sus_len), 0), s),
        np.linspace(s, 0, max(r_n, 1)),
    ])
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)))
    return e[:n]


def lp(x, f, order=2):
    sos = signal.butter(order, min(f, SR * 0.45), "low", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def hp(x, f, order=2):
    sos = signal.butter(order, f, "high", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def bp(x, f1, f2, order=2):
    sos = signal.butter(order, [f1, f2], "band", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def sweep_filter(x, f0, f1, kind="band", q=1.2, block=256):
    """Time-varying biquad (exponential sweep from f0 to f1)."""
    if x.ndim == 2:
        return np.stack([sweep_filter(x[:, c], f0, f1, kind, q, block) for c in range(x.shape[1])], 1)
    out = np.zeros_like(x)
    n = len(x)
    zi = None
    for i in range(0, n, block):
        frac = i / max(n - 1, 1)
        f = f0 * (f1 / f0) ** frac
        w0 = 2 * np.pi * f / SR
        alpha = np.sin(w0) / (2 * q)
        c = np.cos(w0)
        if kind == "band":
            b = [alpha, 0, -alpha]
        elif kind == "low":
            b = [(1 - c) / 2, 1 - c, (1 - c) / 2]
        else:
            b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]
        a = [1 + alpha, -2 * c, 1 - alpha]
        b = np.array(b) / a[0]
        a = np.array(a) / a[0]
        if zi is None:
            zi = signal.lfilter_zi(b, a) * 0
        seg, zi = signal.lfilter(b, a, x[i:i + block], zi=zi)
        out[i:i + block] = seg
    return out


def stereo(x, width=0.0):
    if x.ndim == 2:
        return x
    if width <= 0:
        return np.stack([x, x], 1)
    d = int(width * SR)
    r = np.concatenate([np.zeros(d), x[:-d]]) if d else x
    return np.stack([x, r], 1)


def make_ir(dur=2.2, decay=2.6, damp=5000):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-decay * t)[:, None]
    ir = lp(ir, damp)
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(0)).max()


IR_HALL = make_ir(2.4, 2.4, 6000)
IR_ROOM = make_ir(0.9, 6.0, 7000)


def reverb(x, ir=IR_HALL, wet=0.25):
    x = stereo(x)
    w = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - wet) + w * wet


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def norm(x, peak=0.9):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x


# ---------------------------------------------------------------- SFX
def sfx_whoosh(d=0.6, f0=300, f1=4500, q=1.6):
    n = int(d * SR)
    x = rng.standard_normal(n)
    y = sweep_filter(x, f0, f1, "band", q)
    e = np.sin(np.linspace(0, np.pi, n)) ** 1.6
    y = y * e
    return norm(reverb(stereo(y, 0.006), IR_ROOM, 0.2), 0.8)


def sfx_swoosh_down(d=0.5):
    return sfx_whoosh(d, 5000, 400, 1.4)


def sfx_pop(f=900, d=0.12):
    t = t_arr(d)
    fr = f * (1 + 1.2 * np.exp(-t * 60))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.sin(ph) * np.exp(-t * 32)
    return norm(reverb(stereo(y), IR_ROOM, 0.15), 0.55)


def sfx_click(d=0.05):
    t = t_arr(d)
    y = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 180)
    y += 0.5 * np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 120)
    return norm(stereo(y), 0.5)


def sfx_impact(d=2.0, big=True):
    t = t_arr(d)
    f = 30 + 110 * np.exp(-t * 14)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (2.6 if big else 5))
    crack = bp(rng.standard_normal(len(t)), 300, 6000) * np.exp(-t * 22)
    sub = np.sin(2 * np.pi * 42 * t) * np.exp(-t * 3) * 0.6
    y = body * 1.0 + crack * 0.55 + sub
    y = np.tanh(y * 1.6)
    return norm(reverb(stereo(y), IR_HALL, 0.28), 0.95)


def sfx_bell(f=880, d=2.2, bright=1.0):
    t = t_arr(d)
    parts = [(1.0, 1.0, 2.2), (2.0, 0.5, 3.0), (2.76, 0.32 * bright, 4.0), (5.4, 0.18 * bright, 6.5), (8.93, 0.08 * bright, 9.0)]
    y = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * k) for r, a, k in parts)
    y *= np.minimum(1, t / 0.002)
    return norm(reverb(stereo(y, 0.004), IR_HALL, 0.3), 0.6)


def sfx_riser(d=1.4):
    t = t_arr(d)
    n = len(t)
    x = rng.standard_normal(n)
    y = sweep_filter(x, 300, 9000, "band", 2.2) * (t / d) ** 2.2
    f = 180 * 2 ** (t / d * 2)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2 * 0.35
    y = y + tone
    return norm(reverb(stereo(y, 0.005), IR_HALL, 0.25), 0.7)


def sfx_ticks(d, rate0=8, rate1=28):
    n = int(d * SR)
    y = np.zeros(n)
    t, i = 0.0, 0
    click = sfx_click(0.03)[:, 0]
    while t < d - 0.03:
        k = int(t * SR)
        y[k:k + len(click)] += click[: n - k] * (0.6 + 0.4 * (i % 2))
        rate = rate0 + (rate1 - rate0) * np.sin(np.pi * t / d)
        t += 1.0 / rate
        i += 1
    return norm(stereo(bp(y, 1500, 9000)), 0.35)


def sfx_cash():
    a = sfx_bell(1568, 1.2, 1.4)
    b = sfx_bell(2093, 1.4, 1.4)
    out = np.zeros((len(b) + int(0.09 * SR), 2))
    out[: len(a)] += a
    out[int(0.09 * SR):] += b
    out[: int(0.05 * SR)] += sfx_click(0.05)[: int(0.05 * SR)] * 1.2
    return norm(out, 0.6)


def sfx_shimmer(d=1.8):
    out = np.zeros((int(d * SR) + SR * 2, 2))
    notes = [84, 88, 91, 95, 96, 100]
    for i, m in enumerate(notes):
        b = sfx_bell(midi(m), 1.6, 0.6) * (0.9 - i * 0.08)
        k = int(i * 0.07 * SR)
        out[k:k + len(b)] += b
    return norm(out, 0.5)


def sfx_alert():
    a = sfx_pop(520, 0.16)
    b = sfx_pop(520, 0.16)
    out = np.zeros((len(a) + int(0.14 * SR), 2))
    out[: len(a)] += a
    out[int(0.14 * SR):] += b
    return out


# ---------------------------------------------------------------- MUSIC
BPM = 100
BEAT = 60 / BPM
BAR = BEAT * 4
CHORDS = {  # voicing (midi), bass root
    "F": ([53, 57, 60, 64], 41), "G": ([55, 59, 62, 67], 43),
    "Em": ([52, 55, 59, 62], 40), "Am": ([57, 60, 64, 67], 45),
    "C": ([48, 55, 60, 64], 36), "Dm": ([50, 57, 60, 65], 38),
}
PROG = ["F", "G", "Em", "Am"]


def inst_kick():
    t = t_arr(0.45)
    f = 45 + 95 * np.exp(-t * 30)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    y += hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 300) * 0.25
    return np.tanh(y * 1.3) * 0.9


def inst_clap():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 900, 4200)
    e = np.zeros(n)
    for k in (0, 0.011, 0.022):
        e += (t >= k) * np.exp(-(t - k).clip(0) * 140) * 0.6
    e += (t >= 0.03) * np.exp(-(t - 0.03).clip(0) * 18)
    return x * e * 0.55


def inst_hat(open_=False):
    d = 0.32 if open_ else 0.06
    t = t_arr(d)
    x = hp(rng.standard_normal(len(t)), 7500, 4)
    return x * np.exp(-t * (11 if open_ else 70)) * 0.3


def inst_pluck(f, d=0.5):
    t = t_arr(d)
    saw = 2 * ((f * t) % 1) - 1
    sq = np.sign(np.sin(2 * np.pi * f * 1.003 * t)) * 0.4
    x = saw + sq
    # decaying cutoff
    y = sweep_filter(x, 5200, 500, "low", 0.9, 128)
    return y * env_adsr(len(t), 0.002, d * 0.8, 0.0, d * 0.2) * 0.35


def inst_pad(notes, d):
    t = t_arr(d)
    y = np.zeros(len(t))
    for m in notes:
        f = midi(m)
        for det in (-0.12, 0.0, 0.11):
            fr = f * 2 ** (det / 12)
            y += 2 * ((fr * t + rng.random()) % 1) - 1
    y = lp(y / (len(notes) * 3), 1400, 2)
    return y * env_adsr(len(t), 0.35, 0.2, 0.85, 0.6) * 0.5


def inst_bass(f, d):
    t = t_arr(d)
    y = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    y += 0.15 * lp(2 * ((f * t) % 1) - 1, 400)
    return np.tanh(y * 1.2) * env_adsr(len(t), 0.004, 0.25, 0.65, 0.06) * 0.5


def place(buf, x, t, gain=1.0):
    k = int(round(t * SR))
    if k >= len(buf):
        return
    x = stereo(x) if x.ndim == 1 else x
    m = min(len(x), len(buf) - k)
    if k < 0:
        x = x[-k:]
        m = min(len(x), len(buf))
        k = 0
    buf[k:k + m] += x[:m] * gain


def build_music():
    drums = np.zeros((N + SR * 4, 2))
    keys = np.zeros_like(drums)
    pads = np.zeros_like(drums)
    bass = np.zeros_like(drums)
    kick, clap = inst_kick(), inst_clap()
    hat_c, hat_o = inst_hat(), inst_hat(True)

    # --- intro / hook (0 -> salah): tension on Am, half-time, opening filter
    t0 = 0.0
    intro_end = cues["salah"]
    nbars = int(np.ceil(intro_end / BAR))
    for b in range(nbars):
        bt = t0 + b * BAR
        place(pads, inst_pad(CHORDS["Am"][0] if b % 2 == 0 else CHORDS["F"][0], BAR + 0.4), bt, 0.9)
        for s in range(16):
            tt = bt + s * BEAT / 4
            if tt >= intro_end - 0.05:
                break
            notes = (CHORDS["Am"] if b % 2 == 0 else CHORDS["F"])[0]
            pat = [0, 2, 1, 3, 2, 1, 3, 2]
            place(keys, inst_pluck(midi(notes[pat[s % 8]] + 12), 0.32), tt, 0.5 + 0.5 * (tt / intro_end))
            if s % 2 == 1:
                place(drums, hat_c, tt, 0.5)
        place(drums, kick, bt, 0.8)
        if bt + 2 * BEAT < intro_end:
            place(drums, kick, bt + 2.5 * BEAT, 0.6)
    keys[: int(intro_end * SR)] = sweep_filter(keys[: int(intro_end * SR)], 900, 8000, "low", 0.8, 512)

    # --- main groove: from intro cue to close
    g0, g1 = cues["intro"] - BEAT / 2, cues["close"]
    bars = int(np.ceil((g1 - g0) / BAR))
    arp = [0, 1, 2, 3, 2, 1, 2, 3, 0, 1, 2, 3, 3, 2, 1, 2]
    for b in range(bars):
        bt = g0 + b * BAR
        ch = PROG[b % 4]
        notes, root = CHORDS[ch]
        section_lift = 1.0 if b >= 2 else 0.75
        place(pads, inst_pad(notes, BAR + 0.3), bt, 0.75)
        # bass: root on 1, octave pickup
        place(bass, inst_bass(midi(root), BEAT * 1.5), bt, 1.0)
        place(bass, inst_bass(midi(root), BEAT * 0.5), bt + BEAT * 1.5, 0.8)
        place(bass, inst_bass(midi(root), BEAT * 1.0), bt + BEAT * 2.5, 0.9)
        place(bass, inst_bass(midi(root + 12), BEAT * 0.5), bt + BEAT * 3.5, 0.7)
        for s in range(16):
            tt = bt + s * BEAT / 4 + (0.018 if s % 2 else 0)  # light swing
            if tt >= g1:
                break
            place(keys, inst_pluck(midi(notes[arp[s]] + 12), 0.28), tt, 0.42 * section_lift)
            place(drums, hat_c, tt, 0.35 if s % 2 else 0.55)
            if s in (0, 6, 8):
                place(drums, kick, tt, 0.85)
            if s in (4, 12):
                place(drums, clap, tt, 0.55)
            if s == 14 and b % 2 == 1:
                place(drums, hat_o, tt, 0.4)
    # cut groove sharply at close (riser + logo hit take over)
    cut = int((g1 - 0.02) * SR)
    fade = int(0.04 * SR)
    for buf in (drums, keys, bass):
        buf[cut:cut + fade] *= np.linspace(1, 0, fade)[:, None]
        buf[cut + fade:] = 0
    pads[cut + fade * 6:] = 0
    pads[cut:cut + fade * 6] *= np.linspace(1, 0, fade * 6)[:, None]

    # --- closing: big resolved chord + soft bells
    lt = cues["logo"]
    place(pads, inst_pad([48, 55, 59, 64, 67, 71], 4.6), lt, 1.3)
    place(bass, inst_bass(midi(36), 3.0), lt, 1.0)
    for i, m in enumerate([72, 76, 79, 83]):
        place(keys, inst_pluck(midi(m), 1.2), lt + 0.6 + i * BEAT / 2, 0.45)

    keys = reverb(keys, IR_HALL, 0.32)
    keys = keys + 0.3 * np.roll(keys, int(BEAT * 0.75 * SR), 0)[:, ::-1]  # ping-pong-ish delay
    pads = reverb(pads, IR_HALL, 0.4)
    drums = reverb(drums, IR_ROOM, 0.12)
    bass = lp(bass, 900)
    mix = drums * 0.8 + keys * 0.55 + pads * 0.45 + bass * 0.75
    return mix[:N]


def build_sfx():
    buf = np.zeros((N + SR * 4, 2))
    C = cues
    W = sfx_whoosh()
    Wd = sfx_swoosh_down()
    P_hi, P_mid, P_lo = sfx_pop(1200), sfx_pop(880), sfx_pop(660)
    CL = sfx_click()
    events = [
        # hook
        (sfx_impact(1.6, big=False), C["hook"], 0.55),
        (sfx_whoosh(0.9, 200, 3000, 1.2), C["hook"] + 0.1, 0.7),
        (P_mid, C["hookL2"], 0.45),
        (Wd, C["hookL3"] - 0.05, 0.4),
        (P_hi, C["hookQ"], 0.5),
        (CL, C["hookL3"] + 0.12, 0.6),
        (sfx_riser(C["salah"] - C["hookDim"]), C["hookDim"], 0.55),
        (sfx_impact(2.4, big=True), C["salah"], 1.0),
        (W, C["hookOut"], 0.6),
        # intro
        (sfx_bell(midi(81), 2.0), C["intro"] + 0.1, 0.55),
        (P_mid, C["tile1"], 0.4), (P_mid, C["tile2"], 0.4), (P_hi, C["tile3"], 0.4), (P_hi, C["tile4"], 0.4),
        # k1
        (W, C["k1"] - 0.3, 0.55), (P_lo, C["k1Title"] - 0.6, 0.35),
        (CL, C["k1Dep"] + 0.2, 0.5), (CL, C["k1Dep"] + 0.35, 0.4),
        (sfx_whoosh(1.0, 600, 2400, 3.0), C["k1DP"], 0.25),
        (CL, C["k1Ten"] + 0.1, 0.45), (CL, C["k1Ten"] + 0.42, 0.45), (CL, C["k1Ten"] + 0.74, 0.45),
        (P_mid, C["k1Out"], 0.45), (P_lo, C["k1Bank"], 0.35),
        # k2
        (W, C["k2"] - 0.3, 0.55), (P_mid, C["k2Odo"], 0.4),
        (sfx_ticks(C["k2OdoEnd"] - C["k2OdoRun"]), C["k2OdoRun"], 0.6),
        (sfx_bell(midi(84), 1.8), C["k2OdoEnd"], 0.5),
        (P_lo, C["k2Items"] + 0.25, 0.35), (P_mid, C["k2Items"] + 0.47, 0.35),
        (P_mid, C["k2Items"] + 0.69, 0.35), (P_hi, C["k2Items"] + 0.91, 0.35),
        (P_mid, C["k2Standby"], 0.4), (sfx_alert(), C["k2Apa"], 0.35),
        # k3
        (W, C["k3"] - 0.3, 0.55), (P_mid, C["k3Title"], 0.4), (P_hi, C["k3Ins"], 0.4),
        (sfx_whoosh(0.8, 400, 3500, 2.0), C["k3Renew"], 0.4), (P_hi, C["k3Tahun"], 0.35),
        (sfx_alert(), C["k3Beban"], 0.4), (sfx_bell(midi(79), 1.4), C["k3Tip"], 0.35),
        # k4
        (W, C["k4"] - 0.3, 0.55), (Wd, C["k4Title"] - 0.2, 0.35),
        (P_lo, C["k4Minyak"], 0.4), (P_mid, C["k4Tol"], 0.4), (P_hi, C["k4Semua"], 0.4),
        (sfx_cash(), C["k4Kira"], 0.55),
        # cta
        (W, C["cta"] - 0.3, 0.55), (sfx_whoosh(0.7, 250, 2000, 1.4), C["cta"] + 0.05, 0.4),
        (P_mid, C["ctaForm"], 0.5), (CL, C["ctaIsi"], 0.8), (P_hi, C["ctaIsi"] + 0.05, 0.3),
        (P_lo, C["ctaBawah"] - 0.2, 0.3), (P_mid, C["ctaBawah"] - 0.1, 0.3), (P_hi, C["ctaBawah"], 0.3),
        # closing
        (sfx_riser(0.9), C["close"] - 0.75, 0.5),
        (sfx_whoosh(0.6, 300, 6000, 1.0), C["close"] - 0.05, 0.55),
        (sfx_impact(2.6, big=True), C["logo"], 0.75),
        (sfx_shimmer(), C["shine"], 0.55),
        (P_hi, C["gA"], 0.3), (P_hi, C["gZ"], 0.35),
    ]
    for x, t, g in events:
        place(buf, x, t, g)
    return buf[:N]


def lufs_like(x):
    """Rough loudness (RMS dBFS over voiced frames) for relative balancing."""
    m = x.mean(1) if x.ndim == 2 else x
    h = SR // 10
    r = np.sqrt((m[: len(m) // h * h].reshape(-1, h) ** 2).mean(1) + 1e-12)
    r = r[r > r.max() * 0.05]
    return 20 * np.log10(np.mean(r))


music = build_music()
sfx = build_sfx()
voice = np.zeros((N, 2))
voice[: min(len(vo), N)] = vo[:N]

# ducking envelope from the voice (smoothed RMS)
vm = np.abs(voice.mean(1))
h = int(0.02 * SR)
venv = np.sqrt(np.convolve(vm ** 2, np.ones(h) / h, "same"))
venv = venv / (venv.max() + 1e-9)
active = (venv > 0.04).astype(float)
k = np.exp(-np.arange(int(0.35 * SR)) / (0.08 * SR))
active = np.minimum(1, signal.fftconvolve(active, k / k.sum() * 6, "full")[:N])
duck_db = -7.0 * active
duck = 10 ** (duck_db / 20)

# levels: music sits ~ 16 dB under voice, then ducks further while speaking
vl = lufs_like(voice)
music *= 10 ** ((vl - 5.0 - lufs_like(music)) / 20)
music *= duck[:, None]
sfx *= 10 ** ((vl - 9.0 - lufs_like(sfx[sfx.any(1)] if sfx.any() else sfx)) / 20) if sfx.any() else 1

# make sure the music tail fades out by END
fo = int(1.6 * SR)
music[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
sfx[-int(0.3 * SR):] *= np.linspace(1, 0, int(0.3 * SR))[:, None]

mix = voice + music + sfx
# gentle bus glue + safety limiter
mix = np.tanh(mix * 1.05) / np.tanh(1.05)
peak = np.abs(mix).max()
if peak > 0.97:
    mix *= 0.97 / peak
sf.write(sys.argv[3], mix.astype(np.float32), SR, subtype="PCM_24")
if stems:
    os.makedirs(stems, exist_ok=True)
    sf.write(f"{stems}/music.wav", music.astype(np.float32), SR)
    sf.write(f"{stems}/sfx.wav", sfx.astype(np.float32), SR)
print("mix written", sys.argv[3], f"{N / SR:.2f}s", "peak", round(float(np.abs(mix).max()), 3))
