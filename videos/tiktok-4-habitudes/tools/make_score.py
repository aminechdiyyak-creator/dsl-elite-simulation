"""TikTok "4 habitudes": dreamy half-time beat + transition FX, synthesized (numpy only, deterministic).

Writes assets/audio/score.wav (44.1 kHz stereo, 15 s). Run from the project root:
    python3 tools/make_score.py
"""
import os
import wave

import numpy as np

SR = 44100
DUR = 15.0
N = int(DUR * SR)
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "audio", "score.wav")
rng = np.random.default_rng(4)
L = np.zeros(N)
R = np.zeros(N)
BPM = 120
BEAT = 60 / BPM


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



def bell(f, d=1.6):
    t = tt(d)
    x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (0.7 / m)) for m, a in [(1, 1), (2.0, 0.3), (3.01, 0.12), (4.2, 0.05)])
    return x * np.minimum(1, t / 0.004)


def snare():
    t = tt(0.35)
    x = fft_filter(rng.standard_normal(len(t)), lo=1200, hi=7000) * np.exp(-t / 0.07)
    return x + 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)


def sub808(f, d):
    t = tt(d)
    x = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.5 * np.exp(-t / 0.03))) / SR)
    return np.tanh(1.6 * x) * np.exp(-t / (d * 0.6)) * np.minimum(1, t / 0.004)


def whoosh(d=0.6, f0=300, f1=3000):
    t = tt(d)
    x = rng.standard_normal(len(t))
    out = np.zeros(len(t))
    seg = int(0.03 * SR)
    for s in range(0, len(t), seg):
        fc = f0 * (f1 / f0) ** (s / len(t))
        out[s:s + seg] = fft_filter(x[s:s + seg + 512], lo=fc * 0.6, hi=fc * 1.6)[: len(out[s:s + seg])]
    return out * (t / d) ** 2


def pop():
    t = tt(0.08)
    return np.sin(2 * np.pi * np.cumsum(900 * np.exp(-t / 0.02) + 300) / SR) * np.exp(-t / 0.02)


def impact():
    t = tt(1.2)
    sub = np.sin(2 * np.pi * np.cumsum(38 + 90 * np.exp(-t / 0.06)) / SR) * np.exp(-t / 0.45)
    return reverb(sub + fft_filter(rng.standard_normal(len(t)), hi=900) * np.exp(-t / 0.05) * 0.6, 1.2, 0.3)


# chords: Fmaj7 - Em7 - Dm7 - Cmaj7 (one bar = 2 s)
chords = [["F3", "A3", "C4", "E4"], ["E3", "G3", "B3", "D4"], ["D3", "F3", "A3", "C4"], ["C3", "E3", "G3", "B3"]]
roots = ["F1", "E1", "D1", "C2"]
melody = [("C5", 0), ("E5", 0.75), ("A5", 1.5), ("G5", 2.0), ("E5", 2.75), ("D5", 3.5),
          ("F5", 4.0), ("E5", 4.75), ("C5", 5.5), ("B4", 6.0), ("G4", 6.75), ("E5", 7.25)]
bar = BEAT * 4

# intro (0-3 s): pad + bell motif, filtered, building to the first cut
add(reverb(pad(chords[0], 3.0), 1.8, 0.4), 0.0, gain=0.06)
for nm, t0 in melody[:4]:
    add(reverb(bell(note(nm)), 1.8, 0.45), t0 * 0.75 + 0.1, pan=0.2, gain=0.07)
for k in range(6):
    add(hat(), k * BEAT + BEAT / 2, pan=0.3, gain=0.05 + 0.02 * k)
add(whoosh(1.0, 300, 6000), 2.0, gain=0.3)

# beat (3-15 s): half-time trap-pop
for b in range(6):
    t0 = 3.0 + b * bar
    ch = chords[b % 4]
    add(reverb(pad(ch, bar), 1.6, 0.35), t0, gain=0.055)
    add(sub808(note(roots[b % 4]) * 2, 1.4), t0, gain=0.32)
    add(sub808(note(roots[b % 4]) * 2, 0.6), t0 + BEAT * 2.5, gain=0.22)
    add(kick(), t0, gain=0.5)
    add(kick(), t0 + BEAT * 2.5, gain=0.35)
    add(snare(), t0 + BEAT * 2, gain=0.28)
    for h in range(16):
        g = 0.07 if h % 2 == 0 else 0.04
        if b % 2 == 1 and h in (13, 14, 15):  # hat roll into the next bar
            for r in range(3):
                add(hat(), t0 + h * BEAT / 4 + r * BEAT / 12, pan=0.25, gain=0.05)
        else:
            add(hat(), t0 + h * BEAT / 4, pan=0.25 if h % 2 else -0.25, gain=g)
    for nm, tm in melody:
        if tm < 4 * (b % 2 + 1) and tm >= 4 * (b % 2):
            add(reverb(bell(note(nm)), 1.6, 0.4), t0 + (tm - 4 * (b % 2)) * 0.5, pan=-0.15, gain=0.06)

# transitions on every cut + soft pops for each tile
for S in (3.0, 6.0, 9.0, 12.0):
    add(impact(), S, gain=0.45)
    if S > 3.0:
        add(whoosh(0.5, 400, 5000), S - 0.5, gain=0.22)
    for ti in range(4):
        add(pop(), S + ti * 0.25, pan=(-0.4 if ti % 2 == 0 else 0.4), gain=0.14)
    add(bell(note("E6"), 0.8), S + 1.0, gain=0.05)

# vinyl crackle bed
cr = np.zeros(N)
idx = rng.integers(0, N, 900)
cr[idx] = rng.standard_normal(900) * 0.5
cr = fft_filter(cr, lo=1500) + fft_filter(rng.standard_normal(N), lo=200, hi=3000) * 0.015
add(cr, 0.0, gain=0.25)

# ------------------------------------------------------------------ master ----
mix = np.stack([L, R], axis=1)
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.89
fade = int(0.8 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("score.wav", f"{len(mix) / SR:.2f}s")
