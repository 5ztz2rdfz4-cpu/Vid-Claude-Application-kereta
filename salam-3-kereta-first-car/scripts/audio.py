# Builds the full soundtrack: synthesized BGM + synthesized SFX + processed VO, with ducking.
import numpy as np, wave, sys

SR = 48000
DUR = 60.0
N = int(SR * DUR)
rng = np.random.default_rng(7)

def load_mono(path):
    w = wave.open(path)
    assert w.getframerate() == SR
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getnchannels() == 2:
        a = a.reshape(-1, 2).mean(1)
    return a

def t_(d): return np.arange(int(d * SR)) / SR

def lp(x, fc):  # one-pole lowpass (fc scalar or array)
    fc = np.broadcast_to(np.asarray(fc, np.float32), x.shape)
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); z = 0.0
    for i in range(len(x)):
        z += a[i] * (x[i] - z); y[i] = z
    return y

def lp_fast(x, fc, passes=2):
    from scipy.signal import butter, lfilter
    b, a = butter(passes, fc / (SR / 2), 'low'); return lfilter(b, a, x)
def hp_fast(x, fc, order=2):
    from scipy.signal import butter, lfilter
    b, a = butter(order, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def bp_fast(x, lo, hi, order=2):
    from scipy.signal import butter, lfilter
    b, a = butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band'); return lfilter(b, a, x)

def midi(n): return 440.0 * 2 ** ((n - 69) / 12)

# ------------------------------------------------------------------ BGM
BPM = 104; BEAT = 60 / BPM; BAR = BEAT * 4
L = np.zeros(N); R = np.zeros(N)
def add(buf, sig, t0, g=1.0):
    i = int(t0 * SR)
    if i >= N: return
    j = min(N, i + len(sig)); buf[i:j] += sig[: j - i] * g
def add_st(sig, t0, g=1.0, pan=0.0):
    add(L, sig, t0, g * np.cos((pan + 1) * np.pi / 4) * 1.414)
    add(R, sig, t0, g * np.sin((pan + 1) * np.pi / 4) * 1.414)

# progression Am – F – C – G (voicings around A3)
CH = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 55, 60, 64], [55, 59, 62, 67]]
ROOT = [45, 41, 48, 43]

def saw(f, d):
    t = t_(d); ph = (f * t) % 1.0; return 2 * ph - 1

def pad_chord(notes, d):
    s = np.zeros(int(d * SR))
    for n in notes:
        for det in (-0.09, 0.0, 0.09):
            s += saw(midi(n + det), d)
    s = lp_fast(s, 1100, 2) / (len(notes) * 3)
    env = np.minimum(1, t_(d) / 0.5) * np.minimum(1, (d - t_(d)) / 0.35)
    return s * env

def pluck(f, d=0.45):
    t = t_(d)
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t))
    return s * np.exp(-t * 9) * np.minimum(1, t / 0.003)

def kick():
    t = t_(0.42); f = 48 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7.5) + 0.25 * rng.standard_normal(len(t)) * np.exp(-t * 180)

def hat(open_=False):
    d = 0.18 if open_ else 0.05; t = t_(d)
    return hp_fast(rng.standard_normal(len(t)), 7000) * np.exp(-t * (18 if open_ else 70))

def clap():
    t = t_(0.25); n = bp_fast(rng.standard_normal(len(t)), 900, 2600)
    env = np.exp(-t * 22) * (1 + 0.6 * (np.sin(2 * np.pi * 90 * t) > 0) * (t < 0.03))
    return n * env

def bass(f, d):
    t = t_(d); s = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t)
    return s * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.05)

K, H, HO, C = kick(), hat(), hat(True), clap()
music_end = 53.95
nbars = int(np.ceil(music_end / BAR)) + 1
for b in range(nbars):
    t0 = b * BAR
    if t0 >= music_end: break
    ci = b % 4
    add_st(pad_chord(CH[ci], BAR + 0.3), t0, 0.16)
    # arpeggio (8ths)
    arp = [CH[ci][0] + 12, CH[ci][2] + 12, CH[ci][1] + 12, CH[ci][3] + 12]
    for k in range(8):
        tt = t0 + k * BEAT / 2
        if tt >= music_end: break
        n = arp[k % 4] + (12 if k in (3, 7) else 0)
        p = pluck(midi(n))
        add_st(p, tt, 0.085, pan=-0.35 if k % 2 else 0.35)
        add_st(p, tt + BEAT * 0.75, 0.03, pan=0.6 if k % 2 else -0.6)  # dotted-8th echo
    full = t0 >= 3.4
    breakdown = 43.4 <= t0 < 44.5
    for q in range(4):
        tq = t0 + q * BEAT
        if tq >= music_end - 0.05: break
        if full and not breakdown:
            add_st(K, tq, 0.55)
            add_st(H, tq + BEAT / 2, 0.10, pan=0.25)
            if q in (1, 3): add_st(C, tq, 0.16, pan=-0.1)
        elif q == 0:
            add_st(K, tq, 0.4)
        if full:
            add_st(bass(midi(ROOT[ci] - 12), BEAT * 0.9), tq, 0.32)

# master fade before closing: riser handled by SFX; tail chord for closing
tail = pad_chord([57, 60, 64, 69, 72], 6.2)
add_st(tail, 53.95, 0.5)
add_st(bass(midi(33), 4.0) * np.exp(-t_(4.0) * 0.8), 53.95, 0.35)
# gentle bell arpeggio over logo
for k, n in enumerate([69, 72, 76, 81]):
    add_st(pluck(midi(n), 1.6) * 0.9, 54.0 + k * 0.29, 0.16, pan=(-0.4 + 0.27 * k))
bgm = np.stack([L, R], 1)
# fade out end
fo = int(1.2 * SR); bgm[-fo:] *= np.linspace(1, 0, fo)[:, None]

# ------------------------------------------------------------------ SFX
S = np.zeros((N, 2))
def sfx(sig, t0, g=1.0, pan=0.0):
    i = int(t0 * SR); j = min(N, i + len(sig))
    if i < 0 or i >= N: return
    S[i:j, 0] += sig[: j - i] * g * np.cos((pan + 1) * np.pi / 4) * 1.414
    S[i:j, 1] += sig[: j - i] * g * np.sin((pan + 1) * np.pi / 4) * 1.414

def whoosh(d=0.55, f0=400, f1=4000, peak=0.6):
    t = t_(d); n = rng.standard_normal(len(t))
    fc = f0 + (f1 - f0) * np.sin(np.pi * np.minimum(1, t / d)) ** 1.5
    out = hp_fast(lp(lp(n, fc), fc), 150)
    env = np.where(t / d < peak, (t / d / peak) ** 2, ((1 - t / d) / (1 - peak)) ** 1.5)
    return out * env / (np.abs(out).max() + 1e-9)

def pop(f=900):
    t = t_(0.09); fr = f * (1 + 1.2 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 40)

def click():
    t = t_(0.03); return (np.sin(2 * np.pi * 2400 * t) * 0.6 + bp_fast(rng.standard_normal(len(t)), 2000, 6000)) * np.exp(-t * 200)

def ding(f=1318.5, d=1.0):
    t = t_(d); s = 0
    for m, a, dec in [(1, 1, 3), (2.76, .35, 5), (5.4, .15, 8), (2, .25, 4)]:
        s = s + a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * dec)
    return s * np.minimum(1, t / 0.002) * 0.6

def impact(d=1.2):
    t = t_(d); f = 38 + 70 * np.exp(-t * 12)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    nz = lp_fast(rng.standard_normal(len(t)), 1800) * np.exp(-t * 14) * 0.8
    return body + nz

def riser(d=1.0):
    t = t_(d); f = 300 + 2200 * (t / d) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    n = hp_fast(rng.standard_normal(len(t)), 1500) * 0.5
    return (tone + n) * (t / d) ** 2.2

def shimmer(d=1.4):
    s = np.zeros(int(d * SR))
    for k, f in enumerate([2093, 2637, 3136, 3951, 4186]):
        x = ding(f, d - k * 0.06) * 0.35; i = int(k * 0.06 * SR); s[i:i + len(x)] += x
    return s

def tick_roll(t0, d, n):
    for k in range(n):
        sfx(click(), t0 + d * (k / n) ** 0.7, 0.28, pan=0.1)

W = whoosh(); Wl = whoosh(0.9, 250, 3000, 0.7); Ws = whoosh(0.4, 900, 6000, 0.5)
for t in [0.02, 3.08, 6.55, 49.95]: sfx(W, t, 0.42, pan=-0.2)
for t in [11.15, 24.37, 33.43, 43.53]: sfx(Wl, t, 0.5, pan=0.2)       # gold slash
for t in [12.42, 25.72, 35.24, 50.2]: sfx(Ws, t, 0.25)                # photo slide
sfx(Wl, 53.3, 0.55)                                                   # circle wipe
sfx(riser(0.95), 52.5, 0.35)
sfx(impact(), 3.96, 0.75)                                             # big "3"
sfx(impact(1.8), 53.95, 0.7)                                          # closing boom
sfx(impact(0.6) * 0.6, 54.3, 0.45)                                    # A drops
sfx(Ws, 54.0, 0.35, pan=-0.4)                                         # S swish
for t, f in [(0.02, 820), (0.2, 900), (0.38, 980), (1.42, 820), (2.8, 1000), (3.0, 1100),
             (4.6, 820), (4.84, 920), (5.08, 1020), (6.96, 860), (7.3, 760),
             (15.7, 880), (17.62, 980), (29.3, 880), (30.56, 980), (37.4, 880), (38.95, 940), (40.6, 980),
             (44.6, 760), (44.9, 860), (45.5, 820), (45.8, 920), (46.1, 1020),
             (50.3, 760), (52.9, 1046), (53.4, 1175)]:
    sfx(pop(f), t, 0.32)
tick_roll(8.6, 0.65, 10); tick_roll(10.0, 0.55, 8)
sfx(ding(1318.5, 0.9), 9.3, 0.22); sfx(ding(1568, 0.9), 10.6, 0.22)
for t in [20.0, 21.26, 32.86, 43.2]:
    sfx(click(), t, 0.5); sfx(ding(1760, 0.6), t + 0.01, 0.12)
for t in [47.68, 48.14, 48.6]: sfx(click(), t, 0.3)
sfx(click(), 51.3, 0.7); sfx(pop(600), 51.32, 0.4)                     # tap
for t, f in [(54.76, 1046), (55.1, 1175), (55.86, 1318)]: sfx(pop(f), t, 0.25)
sfx(shimmer(), 56.3, 0.35)

# ------------------------------------------------------------------ VO + ducking
vo = load_mono(sys.argv[1]); out = sys.argv[2]
V = np.zeros(N); V[: min(N, len(vo))] = vo[:N]
# envelope for ducking
env = np.sqrt(np.maximum(lp_fast(V ** 2, 6), 0))
env = np.clip(env / (env.max() * 0.25), 0, 1)
env = lp_fast(env, 3)
duck = 1 - 0.55 * np.clip(env, 0, 1)
bgm *= duck[:, None]

tt = np.arange(N) / SR
gcurve = np.interp(tt, [0, 3.3, 3.6, 53.6, 54.0, 60], [0.5, 0.5, 0.36, 0.36, 0.95, 0.95])
bgm = bgm * gcurve[:, None]
mix = bgm + S * 0.8 + np.stack([V, V], 1) * 1.0
k = max(1e-6, np.abs(mix).max()) / 0.95
mix /= k
np.save(out + '.stems.npy', np.stack([bgm / k, S * 0.8 / k, np.stack([V, V], 1) / k]).astype(np.float32))
wv = wave.open(out, 'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
wv.writeframes((mix * 32767).astype(np.int16).tobytes()); wv.close()
print('ok', out)
