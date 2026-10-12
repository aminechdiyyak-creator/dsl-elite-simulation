"""Revolut explainer (concept): music + UI sound design, synthesized (numpy only, deterministic).

Writes assets/audio/score.wav (44.1 kHz stereo, 29 s). Run from the project root:
    python3 tools/make_score.py
"""
import os
import wave

import numpy as np

SR = 44100
DUR = 29.0
N = int(DUR * SR)
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "audio", "score.wav")
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)
BPM = 116
BEAT = 60 / BPM
GROOVE_START = 3.2


def note(name):
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    return 440.0 * 2 ** ((names[name[:-1]] + 12 * (int(name[-1]) - 4)) / 12)


def add(sig, t0, pan=0.0, gain=1.0):
    a = int(t0 * SR)
    if a >= N:
        return
    sig = sig[: N - a]
    lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    L[a:a + len(sig)] += sig * gain * lg * 1.414
    R[a:a + len(sig)] += sig * gain * rg * 1.414


def tt(d):
    return np.arange(int(d * SR)) / SR


def fft_filter(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if hi:
        m /= 1 + (f / hi) ** 4
    if lo:
        m /= 1 + (lo / np.maximum(f, 1e-3)) ** 4
    return np.fft.irfft(X * m, len(x))


def reverb(x, seconds=1.2, mix=0.25):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = fft_filter(rng.standard_normal(n) * np.exp(-t * 6.9 / seconds), hi=6000)
    ir /= np.sqrt(np.sum(ir ** 2))
    size = 1 << (len(x) + n - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x) + n]
    dry = np.concatenate([x, np.zeros(n)])
    return (1 - mix) * dry + mix * wet * np.max(np.abs(x)) / (np.max(np.abs(wet)) + 1e-9)


# ------------------------------------------------------------------ instruments ----
def kick():
    t = tt(0.4)
    return np.sin(2 * np.pi * np.cumsum(48 + 120 * np.exp(-t / 0.035)) / SR) * np.exp(-t / 0.16)


def hat(open_=False):
    t = tt(0.25 if open_ else 0.06)
    return fft_filter(rng.standard_normal(len(t)), lo=7000) * np.exp(-t / (0.08 if open_ else 0.015))


def clap():
    t = tt(0.3)
    x = fft_filter(rng.standard_normal(len(t)), lo=900, hi=5000)
    e = sum(np.exp(-np.maximum(t - d, 0) / 0.012) * (t >= d) for d in (0, 0.012, 0.024)) + np.exp(-t / 0.12) * 0.6
    return x * e


def pluck(f, d=0.35, bright=1.0):
    t = tt(d)
    x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / (0.08 * bright)) + 0.25 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.05)
    return x * np.exp(-t / (d / 3)) * np.minimum(1, t / 0.003)


def bass(f, d):
    t = tt(d)
    ph = f * t
    sw = 2 * (ph - np.floor(ph + 0.5))
    x = fft_filter(sw, hi=420) + 0.6 * np.sin(2 * np.pi * f * t)
    return x * np.minimum(1, t / 0.005) * np.clip((d - t) / 0.03, 0, 1)


def pad(chord, d):
    t = tt(d)
    x = sum(np.sin(2 * np.pi * note(n) * (1 + dt) * t) for n in chord for dt in (-0.004, 0, 0.004))
    return fft_filter(x, hi=2400) * np.clip(t / 0.4, 0, 1) * np.clip((d - t) / 0.4, 0, 1)


# ------------------------------------------------------------------ groove 3.2 -> 26.0 ----
chords = [["A3", "C4", "E4", "G4"], ["F3", "A3", "C4", "E4"], ["C4", "E4", "G4", "B4"], ["G3", "B3", "D4", "F#4"]]
roots = ["A1", "F1", "C2", "G1"]
bar = BEAT * 4
n_bars = int((26.0 - GROOVE_START) / bar)
for b in range(n_bars):
    t0 = GROOVE_START + b * bar
    ch = chords[b % 4]
    add(pad(ch, bar), t0, gain=0.035)
    for k in range(4):
        tk = t0 + k * BEAT
        add(kick(), tk, gain=0.55)
        add(hat(), tk + BEAT / 2, pan=0.3, gain=0.18)
        add(hat(), tk + BEAT * 0.75, pan=-0.3, gain=0.08)
        if k in (1, 3):
            add(clap(), tk, gain=0.22)
        add(bass(note(roots[b % 4]) * (2 if k == 2 else 1), BEAT * 0.45), tk + BEAT / 2, gain=0.22)
    # plucky arpeggio, 16ths
    for s in range(16):
        nm = ch[(s * 3) % 4]
        f = note(nm) * (2 if s % 8 >= 4 else 1)
        add(pluck(f, 0.22), t0 + s * BEAT / 4, pan=0.5 if s % 2 else -0.5, gain=0.045)

# ------------------------------------------------------------------ intro 0 -> 3.2 ----
t = tt(3.2)
rise = fft_filter(rng.standard_normal(len(t)), lo=500) * (t / 3.2) ** 3
add(rise, 0.0, gain=0.25)
add(pad(["A3", "E4", "A4"], 3.2) * 1.0, 0.0, gain=0.05)
for i, nm in enumerate(["A4", "C5", "E5", "A5"]):
    add(reverb(pluck(note(nm), 0.6), 1.5, 0.35), 0.6 + i * 0.55, gain=0.08)

# ------------------------------------------------------------------ UI sound design ----
def whoosh(d=0.6, f0=300, f1=3000):
    t = tt(d)
    p = t / d
    x = rng.standard_normal(len(t))
    out = np.zeros(len(t))
    seg = int(0.03 * SR)
    for s in range(0, len(t), seg):
        fc = f0 * (f1 / f0) ** (s / len(t))
        out[s:s + seg] = fft_filter(x[s:s + seg + 512], lo=fc * 0.6, hi=fc * 1.6)[: len(out[s:s + seg])]
    return out * np.sin(np.pi * p) ** 2


def tap():
    t = tt(0.05)
    return np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.008) + fft_filter(rng.standard_normal(len(t)), lo=3000) * np.exp(-t / 0.004) * 0.4


def ding(f=1318.5):
    t = tt(1.0)
    x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (0.45 / m)) for m, a in [(1, 1), (2.01, 0.35), (3, 0.15)])
    return reverb(x * np.minimum(1, t / 0.002), 1.0, 0.3)


def impact():
    t = tt(1.4)
    sub = np.sin(2 * np.pi * np.cumsum(40 + 80 * np.exp(-t / 0.08)) / SR) * np.exp(-t / 0.5)
    return reverb(sub + fft_filter(rng.standard_normal(len(t)), hi=1200) * np.exp(-t / 0.06), 1.4, 0.3)


def coin(f):
    t = tt(0.4)
    return (np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t / 0.09)


def lock_click():
    t = tt(0.12)
    return fft_filter(rng.standard_normal(len(t)), lo=1500, hi=6000) * np.exp(-t / 0.01) + np.sin(2 * np.pi * 220 * t) * np.exp(-t / 0.03) * 0.8


add(whoosh(0.8, 200, 4000), 0.05, gain=0.35)          # card spins in
add(impact(), 3.2, gain=0.6)                          # groove drop
for tc in (4.6, 5.2, 5.8):                            # sign-up taps
    add(tap(), tc, gain=0.35)
add(ding(1760), 6.2, gain=0.25)                       # account ready
add(whoosh(0.5, 400, 2500), 6.8, gain=0.25)
add(ding(2093), 8.0, gain=0.3)                        # contactless chime
add(ding(1318.5), 8.45, gain=0.35)                    # notification
add(whoosh(0.5, 400, 2500), 10.6, gain=0.25)
for i, tc in enumerate(np.arange(11.6, 13.4, 0.18)):  # currency flips
    add(coin(1800 + (i % 3) * 300), tc, pan=(-0.5 if i % 2 else 0.5), gain=0.12)
add(whoosh(0.5, 400, 2500), 14.6, gain=0.25)
add(lock_click(), 16.3, gain=0.5)                     # card frozen
add(ding(987.8), 16.35, gain=0.18)
add(whoosh(0.5, 400, 2500), 18.6, gain=0.25)
for i, tc in enumerate((19.4, 19.7, 20.0, 20.3)):     # budget segments
    add(pluck(note(["E5", "G5", "B5", "E6"][i]), 0.3), tc, gain=0.09)
add(whoosh(0.5, 400, 2500), 22.4, gain=0.25)
t = tt(2.0)
add(np.sin(2 * np.pi * np.cumsum(400 * 2 ** (t * 1.2)) / SR) * (t / 2) ** 2 * 0.5, 22.8, gain=0.12)  # chart riser
add(impact(), 26.0, gain=0.7)                         # end card
add(reverb(pad(["C4", "E4", "G4", "B4", "D5"], 2.8), 2.0, 0.4), 26.0, gain=0.07)
add(ding(1567.98), 26.05, gain=0.25)

# ------------------------------------------------------------------ master ----
mix = np.stack([L, R], axis=1)
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.89
fade = int(0.6 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("score.wav", f"{len(mix) / SR:.2f}s")
