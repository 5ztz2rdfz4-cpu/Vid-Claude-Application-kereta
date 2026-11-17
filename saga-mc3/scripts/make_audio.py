"""Synthesise background music + sound effects and mix them with the edited voiceover.

Usage: python3 scripts/make_audio.py <vo_edit.wav> <out_dir>
Writes <out_dir>/bgm.wav, <out_dir>/sfx.wav and <out_dir>/final_premaster.wav
"""
import sys, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 60.0
N = int(SR * DUR)
rng = np.random.default_rng(42)


# ---------------------------------------------------------------- utils
def load_wav(p):
    w = wave.open(p)
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    a = a.reshape(-1, w.getnchannels()).mean(axis=1)
    assert w.getframerate() == SR
    return a


def save_wav(p, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    w = wave.open(p, "wb")
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, f1, f2, o=2):
    return sosfilt(butter(o, [f1, f2], "band", fs=SR, output="sos"), x, axis=0)


def t_(d):
    return np.arange(int(d * SR)) / SR


def place(bus, sig, t, gain=1.0):
    i = int(t * SR)
    if sig.ndim == 1:
        sig = np.stack([sig, sig], 1)
    j = min(len(bus), i + len(sig))
    if j > i:
        bus[i:j] += sig[: j - i] * gain


def pan(sig, p):  # p -1..1
    l = np.cos((p + 1) * np.pi / 4); r = np.sin((p + 1) * np.pi / 4)
    return np.stack([sig * l, sig * r], 1)


def reverb_ir(d=1.8, seed=1):
    r = np.random.default_rng(seed)
    t = t_(d)
    env = np.exp(-t * 6.9 / d)
    ir = np.stack([r.standard_normal(len(t)) * env, r.standard_normal(len(t)) * env], 1)
    ir = lp(ir, 6000)
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(axis=0).mean())


IR = reverb_ir()


def reverb(x, wet=0.25):
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    y = np.stack([fftconvolve(x[:, 0], IR[:, 0])[: len(x)], fftconvolve(x[:, 1], IR[:, 1])[: len(x)]], 1)
    return x + y * wet


def note(n):  # midi -> hz
    return 440.0 * 2 ** ((n - 69) / 12)


def saw(f, t, nh=18, detune=0.0):
    out = np.zeros_like(t)
    ff = f * 2 ** (detune / 1200)
    for k in range(1, nh + 1):
        if ff * k > 12000:
            break
        out += np.sin(2 * np.pi * ff * k * t + k * 0.7) / k
    return out


def adsr(n, a, d, s, r, sustain_len):
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    S = max(0, int(sustain_len * SR) - A - D)
    env = np.concatenate([np.linspace(0, 1, A, endpoint=False), np.linspace(1, s, D, endpoint=False), np.full(S, s), np.linspace(s, 0, R)])
    return env[:n] if len(env) >= n else np.pad(env, (0, n - len(env)))


# ---------------------------------------------------------------- music
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT
# A minor: Am - F - C - G (two bars each)
CHORDS = [[57, 60, 64, 71], [53, 57, 60, 64], [48, 55, 60, 64], [55, 59, 62, 67]]
ROOTS = [45, 41, 48, 43]
CLOSE_T = 52.75


def drums_kick():
    t = t_(0.42)
    f = 46 + 120 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    k = np.sin(ph) * np.exp(-t * 7.5)
    k[: int(0.004 * SR)] += rng.standard_normal(int(0.004 * SR)) * 0.25
    return np.tanh(k * 1.6) * 0.9


def drums_clap():
    t = t_(0.3)
    n = rng.standard_normal(len(t))
    env = np.zeros_like(t)
    for o in (0, 0.011, 0.022):
        i = int(o * SR)
        env[i:] += np.exp(-(t[: len(t) - i]) * (90 if o < 0.02 else 18))
    return bp(n * env, 900, 3200) * 0.6


def drums_hat(open_=False):
    t = t_(0.22 if open_ else 0.06)
    n = rng.standard_normal(len(t))
    return hp(n, 7000, 4) * np.exp(-t * (14 if open_ else 70)) * 0.35


def make_music(vo):
    L = np.zeros((N, 2), np.float32)
    drums = np.zeros((N, 2), np.float32)
    bass = np.zeros(N, np.float32)
    pad = np.zeros((N, 2), np.float32)
    pluck = np.zeros((N, 2), np.float32)
    kick, clap, hat, ohat = drums_kick(), drums_clap(), drums_hat(), drums_hat(True)
    sidechain = np.ones(N, np.float32)
    kick_times = []

    nbars = int(CLOSE_T / BAR) + 1
    for b in range(nbars):
        bt = b * BAR
        if bt >= CLOSE_T:
            break
        ci = (b // 2) % 4
        chord, root = CHORDS[ci], ROOTS[ci]
        sec_full = 27.3 <= bt < 52.3 or bt < 5.2
        sec_mid = 18.9 <= bt < 27.3
        # ---- drums
        for beat in range(4):
            tb = bt + beat * BEAT
            if tb >= 52.35:
                continue
            place(drums, kick, tb, 0.85 if (sec_full or sec_mid or beat % 2 == 0) else 0.0)
            if sec_full or sec_mid or beat % 2 == 0:
                kick_times.append(tb)
            if beat in (1, 3) and (sec_full or sec_mid):
                place(drums, pan(reverb(clap, 0.3)[:, 0], 0.0), tb, 0.55 if sec_full else 0.4)
            for s16 in range(4):
                th = tb + s16 * BEAT / 4
                if th >= 52.35:
                    continue
                g = 0.30 if s16 == 2 else 0.14
                place(drums, pan(ohat if s16 == 2 and sec_full else hat, 0.25), th, g)
        # ---- bass: offbeat 8ths
        for e in range(8):
            te = bt + e * BEAT / 2
            if te >= 52.35:
                continue
            tt = t_(BEAT / 2)
            f = note(root - 12 + (12 if e in (3, 7) else 0))
            s = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt)
            s *= adsr(len(tt), 0.005, 0.12, 0.55, 0.05, BEAT / 2 - 0.05)
            i = int(te * SR)
            j = min(N, i + len(s)); bass[i:j] += (np.tanh(s * 1.4) * (0.55 if e % 2 else 0.4))[: j - i]
        # ---- pad (per chord: 2 bars)
        if b % 2 == 0:
            d = 2 * BAR
            tt = t_(d + 0.8)
            env = adsr(len(tt), 0.35, 0.6, 0.8, 0.8, d)
            for k, n_ in enumerate(chord):
                vL = saw(note(n_), tt, detune=-7 + k) * env
                vR = saw(note(n_), tt, detune=7 - k) * env
                place(pad, np.stack([vL, vR], 1) * 0.06, bt)
        # ---- pluck arpeggio 16ths
        arp = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[3] + 12, chord[2] + 24, chord[3] + 12, chord[1] + 12, chord[2] + 12]
        if bt >= 5.2:
            for s16 in range(16):
                ts = bt + s16 * BEAT / 4
                if ts >= 52.35:
                    continue
                n_ = arp[s16 % 8]
                tt = t_(0.32)
                f = note(n_)
                s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(6 * np.pi * f * tt) / 3 + 0.12 * np.sin(10 * np.pi * f * tt)) * np.exp(-tt * 13)
                g = 0.16 if s16 % 4 == 0 else 0.10
                place(pluck, pan(s, -0.35 if s16 % 2 else 0.35), ts, g)

    # sidechain from kick
    for kt in kick_times:
        i = int(kt * SR)
        tt = t_(0.32)
        env = 1 - 0.55 * np.exp(-tt * 10)
        j = min(N, i + len(env)); sidechain[i:j] = np.minimum(sidechain[i:j], env[: j - i])

    pad = lp(pad, 2600)
    # pluck stereo delay (dotted 8th)
    dly = int(0.75 * BEAT * SR)
    pl = pluck.copy()
    for k in range(1, 4):
        pl[dly * k :, 0 if k % 2 else 1] += pluck[: -dly * k, 0 if k % 2 else 1] * (0.35 ** k)
    pluck = lp(pl, 5200)

    # ---- closing section: Fmaj9 -> C(add9) pad + bell arpeggio
    tt = t_(DUR - CLOSE_T + 0.2)
    env = adsr(len(tt), 0.25, 1.0, 0.85, 2.0, DUR - CLOSE_T - 2.0)
    for chord_, t0, dd in (([53, 57, 60, 64, 67], CLOSE_T, 2.4), ([48, 55, 60, 64, 62 + 12], CLOSE_T + 2.4, DUR - CLOSE_T - 2.4)):
        ttt = t_(dd + 1.5)
        e2 = adsr(len(ttt), 0.08 if t0 == CLOSE_T else 0.5, 0.8, 0.8, 1.5, dd)
        for k, n_ in enumerate(chord_):
            place(pad, np.stack([saw(note(n_), ttt, detune=-6 + k) * e2, saw(note(n_), ttt, detune=6 - k) * e2], 1) * 0.04, t0)
        place(bass_st := np.zeros((N, 2), np.float32), np.sin(2 * np.pi * note(chord_[0]) * ttt) * e2 * 0.18, t0)
        L += bass_st
    bells = [76, 79, 84, 88, 84, 79, 76, 72]
    for i_, n_ in enumerate(bells):
        tb = CLOSE_T + 0.25 + i_ * 0.55
        tt = t_(1.8)
        f = note(n_)
        s = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 4) + 0.2 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 8)) * np.exp(-tt * 2.6)
        place(pluck, pan(s, -0.4 + 0.1 * i_), tb, 0.10)

    sc = sidechain[:, None]
    music = drums * 0.9 + (pad * sc) + np.stack([bass * sidechain, bass * sidechain], 1) * 0.55 + pluck * (0.6 + 0.4 * sc) + L
    music = hp(music, 38)
    music = reverb(music, 0.12)
    # master fade out
    fo = int(2.2 * SR)
    music[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    # gentle intro fade (very short so the hook hits immediately)
    music[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
    return music


# ---------------------------------------------------------------- sfx
def whoosh(d=0.6, f0=400, f1=4000, p0=-0.6, p1=0.6):
    t = t_(d)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    bands = np.geomspace(f0, f1, 7)
    for k, fc in enumerate(bands):
        c = (k + 0.5) / len(bands)
        env = np.exp(-((t / d - c * 0.75 - 0.1) ** 2) / 0.02)
        out += bp(n, fc * 0.7, min(fc * 1.4, 20000)) * env
    out *= np.sin(np.pi * t / d) ** 0.8
    p = np.linspace(p0, p1, len(t))
    l = np.cos((p + 1) * np.pi / 4); r = np.sin((p + 1) * np.pi / 4)
    st = np.stack([out * l, out * r], 1)
    return reverb(st / np.abs(st).max(), 0.25)


def impact(d=1.6, f=52):
    t = t_(d)
    fr = f + 70 * np.exp(-t * 18)
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 3.2)
    nz = lp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 14) * 0.6
    cl = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 90) * 0.4
    x = np.tanh((s + nz + cl) * 1.5)
    return reverb(x / np.abs(x).max(), 0.35)


def pop(f=700):
    t = t_(0.14)
    fr = f * (1 + 0.8 * np.exp(-t * 60))
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 32)
    s[: int(0.002 * SR)] += 0.3
    return reverb(s / np.abs(s).max(), 0.15)


def tick(f=2400):
    t = t_(0.06)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 90) + hp(rng.standard_normal(len(t)), 5000) * np.exp(-t * 200) * 0.4
    return reverb(s / np.abs(s).max(), 0.12)


def ding(f=1318.5):
    t = t_(1.6)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 3) + 0.5 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 5)
         + 0.25 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 7) + 0.6 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 4))
    s[: int(0.003 * SR)] *= np.linspace(0, 1, int(0.003 * SR))
    return reverb(s / np.abs(s).max(), 0.35)


def shimmer(d=1.1):
    t = t_(d)
    out = np.zeros_like(t)
    for k, f in enumerate([2093, 2637, 3136, 3951, 4186]):
        on = k * 0.09
        e = np.where(t > on, np.exp(-(t - on) * 4.5), 0)
        out += np.sin(2 * np.pi * f * t) * e
    out *= (0.75 + 0.25 * np.sin(2 * np.pi * 9 * t))
    return reverb(pan(out / np.abs(out).max(), 0.0)[:, 0], 0.5)


def riser(d=1.4):
    t = t_(d)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    for k, fc in enumerate(np.geomspace(300, 8000, 10)):
        c = k / 9
        env = np.clip((t / d - c * 0.85) * 6, 0, 1) * np.clip(1 - (t / d - c * 0.85 - 0.25) * 4, 0, 1)
        out += bp(n, fc * 0.75, min(fc * 1.35, 20000)) * env
    sw = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / d) ** 2) / SR) * 0.25
    out = (out / np.abs(out).max() + sw) * (t / d) ** 1.6
    return reverb(out / np.abs(out).max(), 0.3)


def stamp():
    t = t_(0.5)
    th = np.sin(2 * np.pi * np.cumsum(80 + 120 * np.exp(-t * 40)) / SR) * np.exp(-t * 12)
    sl = bp(rng.standard_normal(len(t)), 900, 4000) * np.exp(-t * 35)
    x = np.tanh((th + sl * 0.8) * 2)
    return reverb(x / np.abs(x).max(), 0.2)


def make_sfx():
    bus = np.zeros((N, 2), np.float32)
    W = whoosh()
    Ws = whoosh(0.4, 600, 6000, 0.7, -0.7)
    Wb = whoosh(0.75, 250, 3500, 0.8, -0.8)
    cues = [
        (0.0, Wb, 0.55), (0.02, impact(1.4, 48), 0.45),
        (1.14, impact(), 0.70), (1.14, Ws, 0.3),
        (2.40, tick(1800), 0.25),
        (3.22, pop(650), 0.42), (3.42, tick(2000), 0.25), (3.58, pop(820), 0.42),
        (4.40, stamp(), 0.65),
        (5.12, W, 0.45),
        (5.65, pop(560), 0.3), (5.83, pop(640), 0.3), (6.01, pop(720), 0.3),
        (8.48, tick(), 0.32), (9.78, tick(2600), 0.32),
        (11.70, Ws, 0.25), (12.05, tick(1600), 0.22), (12.23, tick(1800), 0.22), (12.41, tick(2000), 0.22), (12.59, tick(2200), 0.25),
        (15.48, tick(2600), 0.32),
        (17.62, Ws, 0.28), (17.90, pop(700), 0.35),
        (18.82, W, 0.42), (19.20, Wb, 0.3), (19.55, impact(1.2, 60), 0.45),
        (21.98, tick(2200), 0.32), (23.02, tick(2600), 0.32),
        (23.72, W, 0.4), (23.95, shimmer(1.0), 0.18),
        (26.0, Ws, 0.25), (26.45, pop(620), 0.35), (26.65, pop(760), 0.35),
        (27.15, Wb, 0.6), (27.50, impact(1.2, 55), 0.4),
        (28.70, pop(600), 0.3), (30.20, riser(0.9), 0.18),
        (31.90, pop(640), 0.3), (32.30, shimmer(1.2), 0.12),
        (35.28, ding(1318.5), 0.38),
        (35.80, W, 0.42), (36.05, impact(1.0, 58), 0.3),
        (38.40, pop(620), 0.38), (39.22, pop(760), 0.38),
        (39.95, pop(560), 0.28), (40.20, shimmer(1.2), 0.12), (41.85, pop(820), 0.3),
        (43.10, ding(1568), 0.38),
        (43.80, W, 0.42), (44.0, Wb, 0.25),
        (47.10, tick(2200), 0.28), (49.50, tick(2600), 0.28),
        (50.95, pop(520), 0.5), (51.0, shimmer(0.9), 0.14), (51.72, tick(3000), 0.4),
        (51.25, riser(1.4), 0.35),
        (52.45, Wb, 0.62), (52.95, impact(2.0, 44), 0.65),
        (54.02, shimmer(1.3), 0.3),
        (54.18, pop(880), 0.3), (54.64, pop(1040), 0.3),
        (56.05, pop(700), 0.32),
    ]
    for t0, s, g in cues:
        place(bus, s, t0, g)
    return bus


# ---------------------------------------------------------------- mix
def main():
    vo_path, out = sys.argv[1], sys.argv[2]
    vo = load_wav(vo_path)
    vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
    music = make_music(vo)
    sfx = make_sfx()

    # ducking from VO envelope
    win = int(0.03 * SR)
    env = np.sqrt(np.convolve(vo ** 2, np.ones(win) / win, mode="same"))
    active = (env > 0.02).astype(np.float32)
    # attack 40ms / release 350ms smoothing
    a_att, a_rel = np.exp(-1 / (0.04 * SR)), np.exp(-1 / (0.35 * SR))
    g = np.zeros(N, np.float32); prev = 0.0
    # vectorised-ish smoothing in chunks
    for i in range(0, N, 64):
        tgt = active[i:i + 64].max()
        coef = a_att if tgt > prev else a_rel
        prev = tgt + (prev - tgt) * coef ** 64
        g[i:i + 64] = prev
    duck = 1 - 0.42 * g

    music = music / (np.sqrt((music ** 2).mean()) + 1e-9) * 0.075
    music *= duck[:, None]
    # music a little louder on the closing logo (no VO after 57.9)
    sfx = sfx / (np.abs(sfx).max() + 1e-9) * 0.55

    vo_st = np.stack([vo, vo], 1) * 0.92
    mix = vo_st + music + sfx
    save_wav(f"{out}/bgm.wav", music / np.abs(music).max() * 0.9)
    save_wav(f"{out}/sfx.wav", sfx)
    save_wav(f"{out}/final_premaster.wav", mix / max(1.0, np.abs(mix).max()) * 0.95)
    print("done; mix peak", float(np.abs(mix).max()))


if __name__ == "__main__":
    main()
