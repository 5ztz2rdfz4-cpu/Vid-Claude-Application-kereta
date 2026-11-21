"""Synthesises the background music bed and the UI sound effects (no third-party samples).
Usage: python3 tools/make_audio.py assets
"""
import sys, wave
import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"
SR = 44100
rng = np.random.default_rng(7)


def write(name, x, stereo=None):
    x = np.asarray(x, np.float64)
    if stereo is None:
        st = np.stack([x, x], 1)
    else:
        st = stereo
    peak = np.abs(st).max() + 1e-9
    st = st / peak * 0.89
    data = (st * 32767).astype(np.int16)
    with wave.open(f"{OUT}/{name}", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data.tobytes())


def t_(d):
    return np.arange(int(d * SR)) / SR


def env_adsr(n, a=0.01, d=0.1, s=0.6, r=0.2):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = max(na, 1)
    e[:na] = np.linspace(0, 1, na)
    e[na:na + nd] = np.linspace(1, s, len(e[na:na + nd]))
    if nr > 0:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def lp_fft(x, fc, slope=2.0):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** (2 * slope)) ** 0.5
    return np.fft.irfft(X, len(x))


def hp_fft(x, fc, slope=2.0):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-6
    X *= 1 / (1 + (fc / f) ** (2 * slope)) ** 0.5
    return np.fft.irfft(X, len(x))


def bp_sweep_noise(d, f0, f1, q=3.0):
    """Noise through a time-varying band-pass (STFT-ish, blockwise)."""
    n = int(d * SR); noise = rng.standard_normal(n)
    out = np.zeros(n); blk = 1024; win = np.hanning(blk * 2)
    for s in range(0, n, blk):
        seg = noise[max(s - blk, 0): s + blk]
        if len(seg) < 2 * blk:
            seg = np.pad(seg, (0, 2 * blk - len(seg)))
        p = min(s / n, 1)
        fc = f0 * (f1 / f0) ** p
        X = np.fft.rfft(seg * win); f = np.fft.rfftfreq(2 * blk, 1 / SR)
        bw = fc / q
        X *= np.exp(-0.5 * ((f - fc) / bw) ** 2)
        y = np.fft.irfft(X)
        o0 = max(s - blk, 0)
        out[o0:o0 + 2 * blk][: len(out[o0:o0 + 2 * blk])] += y[: len(out[o0:o0 + 2 * blk])]
    return out


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- SFX
def sfx_whoosh(d=0.7, f0=300, f1=4200):
    x = bp_sweep_noise(d, f0, f1, 2.2)
    n = len(x); e = np.sin(np.linspace(0, np.pi, n)) ** 1.6
    x = x * e
    pan = np.linspace(-0.6, 0.6, n)
    return np.stack([x * (1 - pan) / 2 + x * 0.25, x * (1 + pan) / 2 + x * 0.25], 1)


def sfx_pop():
    t = t_(0.16); f = 900 * np.exp(-t * 30) + 380
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 28) + 0.15 * np.sin(2 * ph) * np.exp(-t * 40)


def sfx_click():
    t = t_(0.05)
    x = np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 160) + 0.4 * rng.standard_normal(len(t)) * np.exp(-t * 400)
    return hp_fft(x, 900)


def sfx_tick():
    t = t_(0.035)
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 220)


def sfx_ding(base=1318.5):
    t = t_(1.1); x = np.zeros_like(t)
    for k, (m, a, dec) in enumerate([(1, 1, 4.5), (2.76, 0.35, 7), (5.4, 0.18, 11), (1.5, 0.25, 6)]):
        x += a * np.sin(2 * np.pi * base * m * t) * np.exp(-t * dec)
    x[:60] *= np.linspace(0, 1, 60)
    return x


def sfx_impact():
    t = t_(1.4)
    f = 110 * np.exp(-t * 6) + 42
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    nz = lp_fft(rng.standard_normal(len(t)), 1800) * np.exp(-t * 14) * 0.7
    x = np.tanh((body + nz) * 1.6)
    return x


def sfx_riser(d=0.9):
    t = t_(d)
    nz = bp_sweep_noise(d, 400, 7000, 1.5) * (t / d) ** 2
    f = 220 * (8 ** (t / d))
    tone = 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2
    x = nz / (np.abs(nz).max() + 1e-9) + tone
    x[-200:] *= np.linspace(1, 0, 200)
    return x


def sfx_buzz():
    t = t_(0.32)
    sq = np.sign(np.sin(2 * np.pi * 155 * t)) * 0.5 + np.sin(2 * np.pi * 155 * t)
    x = lp_fft(sq, 1400) * env_adsr(len(t), 0.005, 0.05, 0.7, 0.12)
    t2 = t_(0.12)
    return np.concatenate([x[: int(0.13 * SR)] * 0.8, np.zeros(int(0.03 * SR)), x[: int(0.16 * SR)]])


def sfx_shimmer(d=2.2):
    t = t_(d); x = np.zeros_like(t)
    notes = [81, 84, 88, 91, 93, 96, 100]
    for i, m in enumerate(notes):
        st = int(i * 0.07 * SR)
        tt = t[: len(t) - st]
        x[st:] += 0.4 * np.sin(2 * np.pi * mtof(m) * tt) * np.exp(-tt * 3.0)
    air = hp_fft(rng.standard_normal(len(t)), 6000) * np.exp(-t * 2.2) * 0.12
    x = x + air
    x[:100] *= np.linspace(0, 1, 100)
    return x


def sfx_stamp():
    t = t_(0.35)
    thump = np.sin(2 * np.pi * (90 * np.exp(-t * 18) + 60) * t) * np.exp(-t * 16)
    nz = lp_fft(rng.standard_normal(len(t)), 2500) * np.exp(-t * 35) * 0.6
    return np.tanh((thump + nz) * 1.4)


# ---------------------------------------------------------------- MUSIC
def music(total=62.6, bpm=100):
    n = int(total * SR); L = np.zeros(n); R = np.zeros(n)
    beat = 60 / bpm; bar = beat * 4
    # Am  F  C  G  (i - VI - III - VII), warm & confident
    prog = [[57, 60, 64, 69], [53, 57, 60, 65], [55, 60, 64, 67], [55, 59, 62, 67]]
    roots = [45, 41, 48, 43]

    def add(buf, x, at, gain=1.0):
        s = int(at * SR)
        if s >= n: return
        e = min(n, s + len(x)); buf[s:e] += x[: e - s] * gain

    nbars = int(total / bar) + 1
    for b in range(nbars):
        t0 = b * bar; ci = b % 4
        # pad: detuned saw stack, low-passed
        d = bar + 0.3; tt = t_(d); pad = np.zeros_like(tt)
        for m in prog[ci]:
            for det in (-0.08, 0.08):
                f = mtof(m) * 2 ** (det / 12)
                pad += 2 * ((tt * f) % 1) - 1
        pad = lp_fft(pad, 1100) * env_adsr(len(tt), 0.35, 0.3, 0.8, 0.45) * 0.05
        add(L, pad, t0); add(R, pad, t0)
        # sub bass, eighths pattern on the root
        for k, off in enumerate([0, 1.5, 2, 3, 3.5]):
            bt = t_(beat * 0.9); f = mtof(roots[ci])
            bs = (np.sin(2 * np.pi * f * bt) + 0.3 * np.sin(4 * np.pi * f * bt)) * env_adsr(len(bt), 0.005, 0.12, 0.55, 0.08) * 0.22
            add(L, bs, t0 + off * beat); add(R, bs, t0 + off * beat)
        # pluck arpeggio, 16ths, from bar 1
        if b >= 1:
            arp = prog[ci] + [prog[ci][1] + 12]
            for s16 in range(16):
                if s16 % 3 == 2: continue
                m = arp[(s16 * 3) % len(arp)] + 12
                pt = t_(0.22); f = mtof(m)
                pl = (np.sin(2 * np.pi * f * pt) + 0.4 * np.sin(4 * np.pi * f * pt)) * np.exp(-pt * 16) * 0.05
                pan = 0.3 if s16 % 2 else -0.3
                add(L, pl * (1 - pan), t0 + s16 * beat / 4); add(R, pl * (1 + pan), t0 + s16 * beat / 4)
        # drums from bar 2 (soft four on the floor + offbeat hats + clap on 2 & 4)
        if b >= 2:
            for q in range(4):
                kt = t_(0.35)
                kick = np.sin(2 * np.pi * (55 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 9) * 0.38
                add(L, kick, t0 + q * beat); add(R, kick, t0 + q * beat)
                ht = t_(0.06)
                hat = hp_fft(rng.standard_normal(len(ht)), 7000) * np.exp(-ht * 70) * 0.06
                add(L, hat * 0.8, t0 + (q + 0.5) * beat); add(R, hat, t0 + (q + 0.5) * beat)
                if q in (1, 3):
                    ct = t_(0.18)
                    clap = lp_fft(hp_fft(rng.standard_normal(len(ct)), 900), 5000) * np.exp(-ct * 22) * 0.10
                    add(L, clap, t0 + q * beat); add(R, clap, t0 + q * beat)
    # end: fade from 60.8s
    fade_s = int(60.8 * SR)
    fe = np.ones(n); fe[fade_s:] = np.linspace(1, 0, n - fade_s) ** 1.5
    fi = np.ones(n); fi[: int(0.4 * SR)] = np.linspace(0.2, 1, int(0.4 * SR))
    L *= fe * fi; R *= fe * fi
    st = np.stack([L, R], 1)
    st = np.tanh(st * 1.3)
    return st


if __name__ == "__main__":
    write("sfx/whoosh.wav", None, sfx_whoosh())
    write("sfx/whoosh_big.wav", None, sfx_whoosh(1.1, 150, 6000))
    write("sfx/pop.wav", sfx_pop())
    write("sfx/click.wav", sfx_click())
    write("sfx/tick.wav", sfx_tick())
    write("sfx/ding.wav", sfx_ding())
    write("sfx/impact.wav", sfx_impact())
    write("sfx/riser.wav", sfx_riser())
    write("sfx/buzz.wav", sfx_buzz())
    write("sfx/shimmer.wav", sfx_shimmer())
    write("sfx/stamp.wav", sfx_stamp())
    write("bgm.wav", None, music())
    print("ok")
