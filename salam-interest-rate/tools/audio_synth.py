"""Synthesise the background music bed and every sound effect for the
Salam Automobile interest-rate video, then mix them with the edited
voiceover into one master track (assets/audio/master.wav).

All sounds are generated here from scratch (royalty free). Deterministic:
fixed RNG seeds.

usage: python3 tools/audio_synth.py <vo_final.wav> <out_dir>
"""
import sys, os, json
import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
TOTAL = 62.5
BPM = 96.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)


def t_arr(d):
    return np.arange(int(d * SR)) / SR


def place(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= buf.shape[0]:
        return
    if sig.ndim == 1:
        sig = np.stack([sig, sig], 1)
    n = min(len(sig), buf.shape[0] - i)
    buf[i:i + n] += sig[:n] * gain


def env_adsr(n, a, d, s, r, sustain_len):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    s_n = max(0, int(sustain_len * SR) - a_n - d_n)
    e = np.concatenate([
        np.linspace(0, 1, max(a_n, 1)),
        np.linspace(1, s, max(d_n, 1)),
        np.full(s_n, s),
        np.linspace(s, 0, max(r_n, 1)),
    ])
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)))
    return e[:n]


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lp(x, fc, order=2):
    sos = butter(order, fc, btype="low", fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)


def hp(x, fc, order=2):
    sos = butter(order, fc, btype="high", fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)


def bp(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)


def reverb_ir(dur=2.2, decay=0.55, seed=3):
    r = np.random.default_rng(seed)
    t = t_arr(dur)
    ir = np.stack([r.standard_normal(len(t)), r.standard_normal(len(t))], 1)
    ir *= np.exp(-t / decay)[:, None]
    ir = lp(ir, 6000)
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(0, keepdims=True))


IR = reverb_ir()


def reverb(x, wet=0.25):
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    y = np.stack([fftconvolve(x[:, 0], IR[:, 0])[: len(x)], fftconvolve(x[:, 1], IR[:, 1])[: len(x)]], 1)
    return x * (1 - wet) + y * wet


def shaped_noise(dur, centers, width_oct=0.9, seed=1):
    """Noise whose spectral centre follows `centers` (array of Hz per frame)."""
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    hop, win = 256, 1024
    frames = n // hop + 4
    cen = np.interp(np.linspace(0, 1, frames), np.linspace(0, 1, len(centers)), centers)
    freqs = np.fft.rfftfreq(win, 1 / SR)
    out = np.zeros(frames * hop + win)
    w = np.hanning(win)
    lf = np.log2(np.maximum(freqs, 20))
    for k in range(frames):
        mag = np.exp(-0.5 * ((lf - np.log2(cen[k])) / width_oct) ** 2)
        spec = mag * np.exp(1j * r.uniform(0, 2 * np.pi, len(freqs)))
        out[k * hop:k * hop + win] += np.fft.irfft(spec) * w
    out = out[:n]
    return out / (np.abs(out).max() + 1e-9)


# ----------------------------------------------------------------- SFX
def sfx_whoosh(dur=0.55, f0=500, f1=5000, seed=11):
    cen = np.geomspace(f0, f1, 60) if f1 > f0 else np.geomspace(f0, f1, 60)
    cen = np.concatenate([cen, cen[::-1][:30]])
    x = shaped_noise(dur, cen, 0.7, seed)
    t = t_arr(dur)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.6
    x = x * e
    # stereo pan sweep
    pan = np.linspace(-0.6, 0.6, len(x))
    st = np.stack([x * np.sqrt(0.5 - pan / 2), x * np.sqrt(0.5 + pan / 2)], 1)
    return reverb(st, 0.2) * 0.9


def sfx_pop(f=820, dur=0.12):
    t = t_arr(dur)
    fr = f * (1 + 0.6 * np.exp(-t / 0.012))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = np.sin(ph) * np.exp(-t / 0.035)
    x += 0.25 * np.sin(2 * ph) * np.exp(-t / 0.02)
    return reverb(x * 0.8, 0.15)


def sfx_tick(f=2400, dur=0.05):
    t = t_arr(dur)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.008)
    x += hp(rng.standard_normal(len(t)), 3000) * np.exp(-t / 0.004) * 0.3
    return x * 0.6


def sfx_ding(f=1318.5, dur=1.6):
    t = t_arr(dur)
    x = np.zeros_like(t)
    for mult, amp, dec in [(1, 1, 0.6), (2.0, 0.35, 0.35), (3.01, 0.18, 0.22), (4.2, 0.08, 0.12)]:
        x += amp * np.sin(2 * np.pi * f * mult * t) * np.exp(-t / dec)
    x *= np.minimum(1, t / 0.003)
    return reverb(x * 0.45, 0.3)


def sfx_stamp(dur=0.6):
    t = t_arr(dur)
    fr = 50 + 70 * np.exp(-t / 0.03)
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.12)
    n = bp(rng.standard_normal(len(t)), 800, 4000) * np.exp(-t / 0.025)
    x = np.tanh((x + 0.6 * n) * 1.6)
    return reverb(x * 0.75, 0.18)


def sfx_impact(dur=2.5):
    t = t_arr(dur)
    fr = 38 + 60 * np.exp(-t / 0.06)
    sub = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.7)
    n = lp(rng.standard_normal(len(t)), 1800) * np.exp(-t / 0.18)
    x = np.tanh((sub + 0.35 * n) * 1.4)
    return reverb(x * 0.8, 0.35)


def sfx_riser(dur=1.4, seed=21):
    cen = np.geomspace(250, 7000, 80)
    x = shaped_noise(dur, cen, 0.6, seed)
    t = t_arr(dur)
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(200, 900, len(t))) / SR) * 0.25
    e = (t / dur) ** 2.2
    y = (x * 0.8 + tone) * e
    y[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    return reverb(y * 0.7, 0.3)


def sfx_shimmer(dur=1.8, seed=31):
    r = np.random.default_rng(seed)
    t = t_arr(dur)
    x = np.zeros((len(t), 2))
    notes = [88, 91, 93, 95, 98, 100, 103]
    for i in range(18):
        st = 0.05 + i * 0.055
        f = midi(notes[i % len(notes)] + 12 * (i % 2 == 0) * 0)
        seg = t_arr(0.9)
        s = np.sin(2 * np.pi * f * seg) * np.exp(-seg / 0.25) * np.minimum(1, seg / 0.004)
        pan = r.uniform(-0.8, 0.8)
        place(x, np.stack([s * (1 - pan) / 2, s * (1 + pan) / 2], 1), st, 0.18)
    return reverb(x, 0.45)


def sfx_tap():
    t = t_arr(0.08)
    x = np.sin(2 * np.pi * 1600 * t) * np.exp(-t / 0.01) + 0.6 * np.sin(2 * np.pi * 300 * t) * np.exp(-t / 0.02)
    return reverb(x * 0.6, 0.1)


def sfx_scan(dur=1.4):
    t = t_arr(dur)
    f = 700 + 500 * np.sin(np.pi * t / dur)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t))
    e = np.sin(np.pi * t / dur) ** 1.5
    return reverb(x * e * 0.18, 0.3)


def sfx_counter(dur=0.6, step=0.045):
    x = np.zeros(int((dur + 0.1) * SR))
    k = 0
    while k * step < dur:
        place_mono(x, sfx_tick(2000 + 40 * k, 0.03), k * step, 0.55)
        k += 1
    return x


def place_mono(buf, sig, at, gain=1.0):
    i = int(at * SR)
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n] * gain


# ----------------------------------------------------------------- MUSIC
def additive(f, dur, harm=8, tilt=1.4, detune=0.0):
    t = t_arr(dur)
    x = np.zeros_like(t)
    for k in range(1, harm + 1):
        if f * k > 9000:
            break
        x += np.sin(2 * np.pi * f * (1 + detune) * k * t + k * 0.7) / k ** tilt
    return x


CHORDS = [  # one chord per bar (midi notes) Fmaj7, G6, Em7, Am9
    [53, 57, 60, 64],
    [55, 59, 62, 64],
    [52, 55, 59, 62],
    [57, 60, 64, 67, 71],
]
ROOTS = [41, 43, 40, 45]


def music(total=TOTAL):
    n = int(total * SR)
    pad = np.zeros((n, 2))
    pluck = np.zeros((n, 2))
    bass = np.zeros(n)
    drums = np.zeros((n, 2))
    kick_env = np.zeros(n)
    nbars = int(np.ceil(total / BAR)) + 1
    END_GROOVE = 55.625  # last groove beat, then the logo swell
    for b in range(nbars):
        t0 = b * BAR
        if t0 >= total:
            break
        ch = CHORDS[b % 4]
        # ---------------- pad (whole song, swells at end)
        if t0 < END_GROOVE:
            d = BAR + 0.8
            for i, m in enumerate(ch):
                for dt, p in [(-0.0035, -0.5), (0.0035, 0.5)]:
                    v = additive(midi(m), d, harm=10, tilt=1.6, detune=dt)
                    e = env_adsr(len(v), 0.35, 0.3, 0.75, 0.8, BAR)
                    v = v * e * 0.055
                    place(pad, np.stack([v * (1 - p) / 2 * 1.4, v * (1 + p) / 2 * 1.4], 1), t0)
        # ---------------- bass
        groove = 2.5 <= t0 + BAR and t0 < END_GROOVE
        if groove and t0 >= 0:
            pattern = [(0, 1.4), (1.5, 0.45), (2.0, 0.9), (3.5, 0.45)]
            for beat, ln in pattern:
                st = t0 + beat * BEAT
                if st >= END_GROOVE or (12.1 <= st < 12.5):
                    continue
                f = midi(ROOTS[b % 4] - 12 + (12 if beat == 3.5 else 0))
                d = ln * BEAT
                tt = t_arr(d + 0.08)
                v = np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) + 0.12 * np.sin(6 * np.pi * f * tt)
                v *= env_adsr(len(tt), 0.008, 0.1, 0.8, 0.07, d)
                place_mono(bass, np.tanh(v * 1.3) * 0.32, st)
        # ---------------- pluck arpeggio (8ths)
        if t0 < END_GROOVE:
            arp = sorted(ch)
            seq = [arp[0] + 12, arp[2] + 12, arp[1] + 12, arp[3] + 12, arp[2] + 12, arp[1] + 24, arp[3] + 12, arp[2] + 12]
            for k, m in enumerate(seq):
                st = t0 + k * BEAT / 2
                if st >= END_GROOVE or (12.1 <= st < 12.5):
                    continue
                tt = t_arr(0.5)
                v = additive(midi(m), 0.5, harm=5, tilt=1.8) * np.exp(-tt / 0.16) * np.minimum(1, tt / 0.003)
                pan = 0.35 if k % 2 else -0.35
                g = 0.05 if t0 < 5 else 0.065
                place(pluck, np.stack([v * (1 - pan) / 2, v * (1 + pan) / 2], 1) * 2, st, g)
        # ---------------- drums
        for beat in range(4):
            st = t0 + beat * BEAT
            if st >= END_GROOVE or (12.1 <= st < 12.5):
                continue
            # kick on 1 and 3 (+ "and of 3" in main section)
            kicks = [0, 2] if st < 5 else [0, 2, 2.5]
            for kb in kicks:
                if kb >= beat and kb < beat + 1:
                    ks = t0 + kb * BEAT
                    if ks >= END_GROOVE or (12.1 <= ks < 12.5):
                        continue
                    tt = t_arr(0.45)
                    fr = 45 + 85 * np.exp(-tt / 0.035)
                    v = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt / 0.18)
                    v += hp(rng.standard_normal(len(tt)), 2000) * np.exp(-tt / 0.003) * 0.15
                    g = 0.55 if st >= 5 else 0.38
                    place(drums, np.tanh(v * 1.5) * g, ks)
                    ke = np.exp(-t_arr(0.35) / 0.12)
                    place_mono(kick_env, ke, ks)
            # clap on 2 and 4 from bar 2
            if beat in (1, 3) and st >= 5:
                tt = t_arr(0.3)
                nz = bp(rng.standard_normal(len(tt)), 900, 6000)
                e = np.exp(-tt / 0.06) * (1 + 0.6 * ((tt > 0.01) & (tt < 0.02)))
                v = nz * e * 0.16 + np.sin(2 * np.pi * 190 * tt) * np.exp(-tt / 0.03) * 0.08
                place(drums, reverb(v, 0.35), st)
            # hats on 8ths from the title
            for half in (0, 0.5):
                hs = st + half * BEAT
                if hs < 12.5 or hs >= END_GROOVE:
                    continue
                tt = t_arr(0.08)
                v = hp(rng.standard_normal(len(tt)), 7500) * np.exp(-tt / (0.022 if half else 0.012))
                pan = 0.25
                g = 0.07 if half else 0.04
                place(drums, np.stack([v * (1 - pan) / 2, v * (1 + pan) / 2], 1) * 2, hs, g)

    # ---------------- outro swell: Am9 -> F(add9) sustained
    swell = np.zeros((n, 2))
    for i, m in enumerate([45, 57, 60, 64, 67, 71, 76]):
        st = 55.625
        d = total - st
        for dt, p in [(-0.004, -0.6), (0.004, 0.6)]:
            v = additive(midi(m), d, harm=10, tilt=1.6, detune=dt)
            e = env_adsr(len(v), 0.08, 1.2, 0.55, 3.0, d - 3.0)
            v = v * e * (0.06 if m > 50 else 0.12)
            place(swell, np.stack([v * (1 - p) / 2 * 1.5, v * (1 + p) / 2 * 1.5], 1), st)

    # sidechain duck pad/bass by kick
    duck = 1 - 0.45 * np.clip(kick_env, 0, 1)
    pad *= duck[:, None]
    bass *= duck
    pad = lp(pad, 3200)
    mix = reverb(pad, 0.35) + reverb(pluck, 0.3) + np.stack([bass, bass], 1) + drums + reverb(swell, 0.45)
    # gentle intro filter: first 2.5 s darker
    fade = np.clip(t_arr(total)[: n] / 0.4, 0, 1)
    mix *= fade[:, None]
    mix = np.tanh(mix * 1.1)
    return mix / (np.abs(mix).max() + 1e-9) * 0.89


# ----------------------------------------------------------------- CUES
def cues():
    W = sfx_whoosh
    return [
        # (time, sound, gain)
        (0.00, sfx_impact(), 0.55),
        (0.05, W(0.5, 6000, 600, 12), 0.35),
        (0.30, sfx_pop(700), 0.35),
        (1.00, W(0.55, 400, 4000, 13), 0.30),
        (3.25, sfx_pop(900), 0.40),
        (4.10, sfx_tick(), 0.55),
        (5.05, sfx_tick(2600), 0.55),
        (6.05, sfx_tick(2800), 0.55),
        (6.80, W(0.5, 500, 5000, 14), 0.35),
        (7.70, sfx_counter(0.55), 0.45),
        (8.30, sfx_pop(620), 0.45),
        (9.58, sfx_counter(0.55), 0.45),
        (10.2, sfx_pop(980), 0.45),
        (10.55, sfx_stamp(), 0.70),
        (11.30, sfx_riser(1.25), 0.40),
        (12.55, sfx_impact(), 0.60),
        (12.55, W(0.6, 5000, 400, 15), 0.30),
        (13.10, sfx_shimmer(), 0.35),
        (15.95, W(0.55, 400, 5000, 16), 0.35),
        (16.25, sfx_pop(760), 0.35),
        (18.55, sfx_stamp(), 0.55),
        (19.50, sfx_stamp(), 0.55),
        (20.35, sfx_ding(), 0.45),
        (21.62, W(0.55, 400, 5000, 17), 0.35),
        (22.05, sfx_pop(760), 0.35),
        (24.80, sfx_pop(880), 0.40),
        (25.55, sfx_scan(2.2), 0.65),
        (27.95, sfx_stamp(), 0.50),
        (28.05, sfx_ding(1568), 0.40),
        (28.85, W(0.6, 400, 6000, 18), 0.38),
        (29.20, sfx_impact(), 0.45),
        (30.58, sfx_pop(1000), 0.45),
        (30.66, sfx_tick(2000), 0.35),
        (30.75, sfx_tick(2250), 0.35),
        (30.84, sfx_tick(2500), 0.35),
        (30.93, sfx_tick(2750), 0.35),
        (31.02, sfx_tick(3000), 0.35),
        (31.85, W(0.45, 3000, 500, 25), 0.25),
        (32.35, sfx_pop(820), 0.45),
        (34.55, sfx_pop(870), 0.45),
        (36.55, sfx_pop(920), 0.45),
        (39.85, sfx_pop(980), 0.45),
        (41.75, sfx_pop(1040), 0.45),
        (44.90, W(0.55, 400, 5000, 19), 0.35),
        (45.40, sfx_pop(700), 0.35),
        (46.25, sfx_tick(2200), 0.45),
        (46.60, sfx_tick(2500), 0.45),
        (46.95, sfx_tick(2800), 0.45),
        (48.85, sfx_ding(1318.5), 0.40),
        (50.30, W(0.55, 400, 5000, 20), 0.38),
        (50.70, sfx_pop(760), 0.38),
        (52.40, sfx_shimmer(1.2, 33), 0.25),
        (54.62, sfx_tap(), 0.85),
        (54.65, sfx_ding(2093), 0.25),
        (54.70, sfx_riser(0.95, 22), 0.45),
        (55.62, W(0.7, 300, 6000, 23), 0.40),
        (55.66, sfx_impact(), 0.60),
        (56.25, W(0.8, 600, 3000, 24), 0.30),
        (56.60, sfx_shimmer(2.2, 35), 0.40),
        (57.35, sfx_pop(660), 0.30),
        (58.33, sfx_pop(880), 0.40),
        (59.00, sfx_pop(1100), 0.40),
        (59.40, sfx_ding(1760), 0.35),
        (60.20, sfx_shimmer(1.8, 36), 0.25),
    ]


def main():
    vo_path, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    n = int(TOTAL * SR)
    mus = music()
    sf.write(os.path.join(out, "music.wav"), mus, SR)
    fx = np.zeros((n, 2))
    for at, s, g in cues():
        place(fx, s, at, g)
    sf.write(os.path.join(out, "sfx.wav"), np.clip(fx, -1, 1), SR)
    print("music+sfx written")


if __name__ == "__main__":
    main()
