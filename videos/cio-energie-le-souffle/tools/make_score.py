"""CIO Énergie — « Le Souffle »: score + sound design, synthesized (numpy only, deterministic).

Writes assets/audio/score.wav (44.1 kHz stereo, 45 s). Run from the project root:
    python3 tools/make_score.py
Timeline follows the shooting script (D minor -> D major at the drop, 120 BPM from 0:10).
"""
import os
import wave

import numpy as np

SR = 44100
DUR = 45.0
N = int(DUR * SR)
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "audio", "score.wav")
rng = np.random.default_rng(45)
T = np.arange(N) / SR

L = np.zeros(N)
R = np.zeros(N)


def note(name):
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    pitch, octave = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[pitch] + 12 * (octave - 4)) / 12)


def seg(t0, t1):
    a, b = int(t0 * SR), min(N, int(t1 * SR))
    return a, b, np.arange(b - a) / SR


def add(sig, t0, pan=0.0, gain=1.0):
    a = int(t0 * SR)
    sig = sig[: max(0, N - a)]
    lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    L[a:a + len(sig)] += sig * gain * lg * 1.414
    R[a:a + len(sig)] += sig * gain * rg * 1.414


def fft_filter(x, lo=None, hi=None):
    """Static brick-ish band filter in the frequency domain (with soft edges)."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if hi:
        m *= 1 / (1 + (f / hi) ** 4)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * m, n)


def sweep_filter(x, f0, f1, lo=False, chunk=0.04):
    """Time-varying low-pass (or high-pass) via overlapping static FFT chunks."""
    n = len(x)
    out = np.zeros(n)
    hop = int(chunk * SR)
    win = np.hanning(2 * hop)
    for s in range(0, n, hop):
        e = min(n, s + 2 * hop)
        p = s / n
        fc = f0 * (f1 / f0) ** p
        blk = x[s:e] * win[: e - s]
        out[s:e] += fft_filter(blk, lo=fc if lo else None, hi=None if lo else fc)
    return out


def reverb(x, seconds=3.0, mix=0.35, damp=4000):
    ir_n = int(seconds * SR)
    t = np.arange(ir_n) / SR
    ir = rng.standard_normal(ir_n) * np.exp(-t * 6.9 / seconds)
    ir = fft_filter(ir, hi=damp)
    ir /= np.sqrt(np.sum(ir ** 2))
    n = len(x) + ir_n
    size = 1 << (n - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:n]
    dry = np.concatenate([x, np.zeros(ir_n)])
    return (1 - mix) * dry + mix * wet * (np.max(np.abs(x)) / (np.max(np.abs(wet)) + 1e-9))


def saw(freq, t, detune=0.0):
    ph = (freq * (1 + detune)) * t
    return 2 * (ph - np.floor(ph + 0.5))


def env(n, a, r, hold=None):
    e = np.ones(n)
    A, Rr = int(a * SR), int(r * SR)
    e[:A] = np.linspace(0, 1, A) if A else 1
    if Rr:
        e[-Rr:] *= np.linspace(1, 0, Rr)
    return e


# ---------------------------------------------------------------- 0:00 breath (huge) ----
def breath(dur, f0, f1, gain, inhale=True):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    x = sweep_filter(x, f0, f1, lo=False)
    x = fft_filter(x, lo=180)
    shape = np.sin(np.linspace(0, np.pi, n)) ** (1.4 if inhale else 0.8)
    return x * shape * gain


b1 = breath(1.8, 600, 3200, 1.0)
add(reverb(b1, 1.6, 0.25), 0.8, gain=0.55)
a, b, t = seg(0.8, 3.0)
add(np.sin(2 * np.pi * 30 * t) * np.sin(np.pi * t / 2.2) ** 2, 0.8, gain=0.35)

# exhale -> wind (filter opens 200 Hz -> 8 kHz)
a, b, t = seg(2.6, 29.0)
wind = rng.standard_normal(b - a)
wind = sweep_filter(wind, 200, 8000, chunk=0.05) * 0.5 + fft_filter(rng.standard_normal(b - a), lo=150, hi=900) * 0.6
gust = 0.55 + 0.45 * np.sin(2 * np.pi * 0.23 * t) * np.sin(2 * np.pi * 0.07 * t + 1)
wenv = np.clip(t / 0.6, 0, 1) * np.where(t < 3.0, 1.0, 0.45) * np.clip((26.4 - t) / 3, 0.25, 1)
add(wind * gust * wenv, 2.6, pan=-0.2, gain=0.32)
add(np.roll(wind, 1800) * gust * wenv, 2.6, pan=0.25, gain=0.28)


# ---------------------------------------------------------------- percussion helpers ----
def taiko(gain=1.0, verb=4.0):
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * np.cumsum(55 + 60 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.35)
    skin = fft_filter(rng.standard_normal(n), hi=1200) * np.exp(-t / 0.03) * 0.6
    return reverb((body + skin) * gain, verb, 0.35, 2500)


def metal_hit():
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    parts = [(220, 1), (523, 0.6), (871, 0.45), (1310, 0.3), (2040, 0.2)]
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / (0.9 - 0.12 * k)) for k, (f, a) in enumerate(parts))
    x += fft_filter(rng.standard_normal(n), lo=2000) * np.exp(-t / 0.015) * 0.6
    return reverb(x, 2.2, 0.3)


add(taiko(1.0, 4.0), 4.0, gain=0.9)

# blade doppler swoosh 6.4 -> 7.6
a, b, t = seg(6.4, 7.7)
pitch = 140 * np.exp(-((t - 0.6) ** 2) / 0.08) + 60
sw = np.sin(2 * np.pi * np.cumsum(pitch) / SR) * 0.6 + fft_filter(rng.standard_normal(b - a), lo=80, hi=700) * 0.9
sw *= np.exp(-((t - 0.6) ** 2) / 0.09)
add(sw, 6.4, pan=-0.6, gain=0.55)
add(np.roll(sw, 2200), 6.4, pan=0.6, gain=0.45)

# ---------------------------------------------------------------- cellos (D minor drone) ----
a, b, t = seg(6.0, 29.05)
cel = sum(saw(note(n), t, d) for n, d in [("D2", 0), ("D2", 0.004), ("A2", -0.003), ("D3", 0.002)])
cel = fft_filter(cel, hi=900) * (1 + 0.15 * np.sin(2 * np.pi * 5.2 * t))
cenv = np.clip(t / 2.5, 0, 1) * (0.5 + 0.5 * np.clip((t - 4) / 19, 0, 1))
add(reverb(cel * cenv, 2.5, 0.3)[: b - a], 6.0, gain=0.11)

# ---------------------------------------------------------------- 120 BPM pulse 10 -> 29 ----
BEAT = 0.5
for k in range(int((29.0 - 10.0) / BEAT)):
    t0 = 10.0 + k * BEAT
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    kick = np.sin(2 * np.pi * np.cumsum(36.7 + 90 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.22)
    grow = 0.6 + 0.4 * (k / 38)
    add(kick, t0, gain=0.55 * grow)
    # eighth sub pulse
    tt = np.arange(int(0.22 * SR)) / SR
    add(np.sin(2 * np.pi * 36.7 * tt) * np.sin(np.pi * tt / 0.22) ** 2, t0 + 0.25, gain=0.22 * grow)
for t0 in (10.0, 11.0, 12.0, 13.0):
    add(metal_hit(), t0, pan=(t0 - 11.5) / 3, gain=0.35)

# ---------------------------------------------------------------- 14 -> 20 arpeggio + choir ----
arp = ["D4", "F4", "A4", "D5", "A4", "F4", "D5", "F5"]
for k in range(int(6.0 / 0.125)):
    t0 = 14.0 + k * 0.125
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    f = note(arp[k % len(arp)])
    tone = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t / 0.12)
    add(tone, t0, pan=0.6 if k % 2 else -0.6, gain=0.09 * min(1, k / 12 + 0.3))


def choir(t0, t1, chord, gain, attack=1.8):
    a, b, t = seg(t0, t1)
    x = np.zeros(b - a)
    for i, nme in enumerate(chord):
        f = note(nme)
        vib = 1 + 0.004 * np.sin(2 * np.pi * (5 + i * 0.3) * t + i)
        for d in (-0.003, 0.0, 0.003):
            x += np.sin(2 * np.pi * np.cumsum(f * vib * (1 + d)) / SR)
    x = fft_filter(x, lo=200, hi=2600)
    e = np.clip(t / attack, 0, 1) * np.clip((t1 - t0 - t) / 0.4, 0, 1)
    add(reverb(x * e, 3.0, 0.45)[: b - a], t0, gain=gain)


choir(14.0, 29.05, ["D4", "F4", "A4"], 0.035)

# ---------------------------------------------------------------- 20 -> 25 water + taiko roll ----
a, b, t = seg(20.0, 25.2)
water = fft_filter(rng.standard_normal(b - a), lo=60, hi=500)
add(water * np.clip(t / 0.5, 0, 1) * np.clip((5.2 - t) / 0.6, 0, 1), 20.0, gain=0.4)
for k in range(16):
    add(taiko(0.25 + 0.75 * (k / 15), 1.5), 24.0 + k * 0.0625, gain=0.35)

# ---------------------------------------------------------------- 22 -> 29 braam ----
a, b, t = seg(22.0, 29.05)
br = sum(saw(note(n), t, d) for n, d in [("D2", 0), ("D2", 0.006), ("A2", -0.005), ("A2", 0.004), ("D3", 0)])
br = sweep_filter(br, 250, 2600)
br *= np.clip(t / 6.5, 0, 1) ** 2
add(br, 22.0, gain=0.07)

# ---------------------------------------------------------------- 25 -> 29 riser ----
a, b, t = seg(25.0, 29.05)
p = t / 4.05
ris = sweep_filter(rng.standard_normal(b - a), 100, 12000, lo=True) * p ** 2
shep = sum(np.sin(2 * np.pi * np.cumsum(f0 * 2 ** (p * 1.5)) / SR) for f0 in (110, 220, 440)) * p ** 2.5
add(ris, 25.0, gain=0.35)
add(shep, 25.0, gain=0.06)

# ---------------------------------------------------------------- 29.0 implosion, silence ----
a, b, t = seg(28.9, 29.25)
imp = fft_filter(rng.standard_normal(b - a), lo=1500)[::-1] * (t / t[-1]) ** 3
add(imp, 28.9, gain=0.5)
# hard cut: silence 29.25 -> 30.6, only a soft human breath
fade = int(0.012 * SR)
cut_a, cut_b = int(29.25 * SR), int(30.6 * SR)
L[cut_a - fade:cut_a] *= np.linspace(1, 0, fade)
R[cut_a - fade:cut_a] *= np.linspace(1, 0, fade)
L[cut_a:cut_b] = 0
R[cut_a:cut_b] = 0
add(breath(0.9, 500, 1600, 0.12), 29.6)

# ---------------------------------------------------------------- 30.6 DROP + D major tutti ----
a, b, t = seg(30.6, 33.6)
drop = np.sin(2 * np.pi * np.cumsum(30 + 50 * np.exp(-t / 0.5)) / SR) * np.exp(-t / 1.6)
add(drop, 30.6, gain=0.9)
n = int(3.5 * SR)
tt = np.arange(n) / SR
boom = fft_filter(rng.standard_normal(n), hi=700) * np.exp(-tt / 0.25) * 2 + rng.standard_normal(n) * np.exp(-tt / 0.03) * 0.5
add(reverb(boom, 3.5, 0.4), 30.6, gain=0.5)
a, b, t = seg(30.6, 39.5)
tut = sum(saw(note(nm), t, d) for nm, d in [("D2", 0), ("A2", 0.003), ("D3", -0.002), ("F#3", 0.003), ("A3", -0.003), ("D4", 0.002), ("F#4", 0)])
tut = sweep_filter(tut, 3500, 900)
tenv = np.minimum(1, t / 0.05) * np.exp(-t / 3.5) * 0.8 + 0.2 * np.clip((8.9 - t) / 2, 0, 1)
add(reverb(tut * tenv, 3.0, 0.35)[: b - a], 30.6, gain=0.06)
choir(30.6, 39.5, ["D4", "F#4", "A4", "D5"], 0.05, attack=0.15)

# ---------------------------------------------------------------- 35 -> 39 piano theme ----
theme = [("A4", 35.2), ("D5", 35.7), ("E5", 36.2), ("F#5", 36.7), ("A5", 37.5), ("F#5", 38.2)]
for nm, t0 in theme:
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    f = note(nm)
    tone = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.3) + 0.15 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.15))
    add(reverb(tone * np.exp(-t / 0.9) * np.minimum(1, t / 0.004), 2.5, 0.4), t0, pan=0.15, gain=0.12)
add(breath(0.7, 700, 2400, 0.25, inhale=False), 36.0, pan=-0.3)  # the child's breath

# ---------------------------------------------------------------- 39.2 sonic logo ----
add(breath(0.45, 900, 3000, 0.18), 39.15)
for nm, t0, g in [("D4", 39.6, 1.0), ("A4", 39.85, 0.9), ("D5", 40.1, 1.15)]:
    n = int(4.0 * SR)
    t = np.arange(n) / SR
    f = note(nm)
    bell = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (1.6 / m)) for m, a in [(1, 1), (2, 0.5), (3.01, 0.25), (4.2, 0.12)])
    add(reverb(bell * np.minimum(1, t / 0.003), 4.0, 0.45), t0, gain=0.16 * g)
a, b, t = seg(40.1, 44.5)
add(np.sin(2 * np.pi * note("D1") * t) * np.exp(-t / 1.6) * np.minimum(1, t / 0.02), 40.1, gain=0.5)

# final wind breath
a, b, t = seg(42.5, 45.0)
add(fft_filter(rng.standard_normal(b - a), lo=200, hi=2500) * np.sin(np.pi * t / 2.5) ** 2, 42.5, gain=0.12)

# ---------------------------------------------------------------- master ----
mix = np.stack([L, R], axis=1)
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.89
mix[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))[:, None]
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("score.wav", f"{len(mix) / SR:.2f}s")
