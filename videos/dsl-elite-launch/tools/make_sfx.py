"""Synthesize the launch-cinematic sound design (deterministic, numpy only).

Writes 48 kHz stereo 16-bit WAV stems into assets/sfx/. Run from the project root:
    python3 tools/make_sfx.py
"""
import os
import wave

import numpy as np

SR = 48000
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "sfx")
rng = np.random.default_rng(20261007)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def onepole_lp(x, cutoff):
    """One-pole low-pass; cutoff may be a scalar or a per-sample array."""
    c = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    a = np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def bandpass(x, freq, q=6.0):
    """Biquad band-pass with per-sample centre frequency (RBJ cookbook)."""
    f = np.broadcast_to(np.asarray(freq, dtype=float), x.shape)
    y = np.zeros_like(x)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(len(x)):
        w0 = 2 * np.pi * f[i] / SR
        alpha = np.sin(w0) / (2 * q)
        b0, a0 = alpha, 1 + alpha
        a1, a2 = -2 * np.cos(w0), 1 - alpha
        yi = (b0 * x[i] - b0 * x2 - a1 * y1 - a2 * y2) / a0
        x2, x1 = x1, x[i]
        y2, y1 = y1, yi
        y[i] = yi
    return y


def reverb(x, tail=2.5, mix=0.35):
    """Small Schroeder-style reverb: parallel combs + extended length for the tail."""
    pad = np.concatenate([x, np.zeros(int(tail * SR))])
    out = np.zeros_like(pad)
    for d_ms, g in [(29.7, 0.84), (37.1, 0.82), (41.1, 0.8), (43.7, 0.78)]:
        d = int(d_ms * SR / 1000)
        buf = pad.copy()
        for i in range(d, len(buf)):
            buf[i] += g * buf[i - d]
        out += buf
    out = onepole_lp(out / 4, 5000)
    return (1 - mix) * pad + mix * out / (np.max(np.abs(out)) + 1e-9) * np.max(np.abs(x))


def env_adsr(n, a, d, s, r, sustain=0.6):
    e = np.zeros(n)
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    S = max(0, n - A - D - R)
    e[:A] = np.linspace(0, 1, A, endpoint=False)
    e[A:A + D] = np.linspace(1, sustain, D, endpoint=False)
    e[A + D:A + D + S] = sustain
    e[A + D + S:] = np.linspace(sustain, 0, n - (A + D + S))
    return e


def stereo(x, width_ms=9.0):
    d = int(width_ms * SR / 1000)
    left = x
    right = np.concatenate([np.zeros(d), x[:-d]]) if d else x
    return np.stack([left, right], axis=1)


def write(name, x, peak=0.89):
    if x.ndim == 1:
        x = stereo(x)
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    fade = int(0.01 * SR)
    x[-fade:] *= np.linspace(1, 0, fade)[:, None]
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    print(f"{name}: {len(x) / SR:.2f}s")


# --- drone: deep space rumble that swells into the collapse, cut by the impact ---------
def drone():
    dur = 13.5
    t = t_axis(dur)
    sub = np.sin(2 * np.pi * 38 * t) + 0.6 * np.sin(2 * np.pi * 38.6 * t) + 0.35 * np.sin(2 * np.pi * 57 * t)
    rumble = onepole_lp(rng.standard_normal(len(t)), 120) * 6
    body = sub + rumble
    swell = np.clip(t / 2.0, 0, 1) ** 2 * (0.55 + 0.45 * np.clip((t - 2) / 5.9, 0, 1) ** 1.5)
    cut = np.where(t < 7.95, 1.0, 0.18 * np.exp(-(t - 7.95) / 3.0))
    pad_t = np.clip(t - 8.0, 0, None)
    chord = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(110, 0.5), (164.8, 0.35), (220, 0.3), (261.6, 0.18)])
    pad = chord * np.clip(pad_t / 1.5, 0, 1) * np.where(t > 8.0, 1, 0) * 0.35
    pad *= np.clip((13.5 - t) / 1.2, 0, 1)
    return body * swell * cut + onepole_lp(pad, 1800)


# --- HUD blips: one per typed line, double alarm on "ANOMALIE" --------------------------
def blips(times, alarm_at):
    dur = 4.0
    out = np.zeros(int(dur * SR))
    def beep(at, f, length=0.07, amp=0.5):
        n = int(length * SR)
        tt = np.arange(n) / SR
        b = np.sign(np.sin(2 * np.pi * f * tt)) * 0.4 + np.sin(2 * np.pi * f * tt)
        b *= np.exp(-tt / (length / 3)) * amp
        i = int(at * SR)
        out[i:i + n] += b[: len(out) - i]
    for at in times:
        beep(at, 1320)
    for k in range(2):
        beep(alarm_at + k * 0.16, 880, 0.12, 0.7)
    return onepole_lp(out, 6000)


# --- riser: band-passed noise sweeping up + accelerating tremolo tone ------------------
def riser(dur=2.35):
    t = t_axis(dur)
    p = t / dur
    noise = bandpass(rng.standard_normal(len(t)), 300 + 5200 * p ** 2, q=3.5)
    freq = 160 * (8 ** p)
    tone = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    trem = 0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(4 + 26 * p ** 2) / SR)
    return (noise * 0.9 + tone * trem * 0.35) * p ** 2.2


# --- implosion: reversed noise swell sucked into the singularity -----------------------
def implode(dur=0.75):
    t = t_axis(dur)
    burst = rng.standard_normal(len(t)) * np.exp(-t / 0.18)
    burst = bandpass(burst, 2500, q=1.2)
    return burst[::-1]


# --- impact: sub drop + noise crack + reverb tail ---------------------------------------
def impact():
    dur = 2.6
    t = t_axis(dur)
    sub = np.sin(2 * np.pi * np.cumsum(28 + 70 * np.exp(-t / 0.18)) / SR) * np.exp(-t / 1.1)
    crack = onepole_lp(rng.standard_normal(len(t)), 900) * np.exp(-t / 0.12) * 4
    snap = rng.standard_normal(len(t)) * np.exp(-t / 0.02) * 0.6
    return reverb(sub * 1.2 + crack + snap, tail=2.2, mix=0.3)


# --- shimmer: sparkling high partials as the logo resolves -----------------------------
def shimmer():
    dur = 2.6
    t = t_axis(dur)
    out = np.zeros(len(t))
    for k, f in enumerate([1568, 2093, 2637, 3136, 3951, 4186, 5274]):
        at = 0.05 + k * 0.09
        tt = np.clip(t - at, 0, None)
        out += np.sin(2 * np.pi * f * t) * np.exp(-tt / 0.9) * (t >= at) * (0.6 - k * 0.05)
    air = bandpass(rng.standard_normal(len(t)), 7000, q=2) * np.exp(-t / 0.7) * 0.5
    return reverb(out + air, tail=1.2, mix=0.4)


# --- whoosh: short swept noise for the subtitle -----------------------------------------
def whoosh(dur=0.9):
    t = t_axis(dur)
    p = t / dur
    n = bandpass(rng.standard_normal(len(t)), 400 + 3000 * np.sin(np.pi * p), q=2)
    return n * np.sin(np.pi * p) ** 2


# --- start: two-note game confirm chime -------------------------------------------------
def start_chime():
    dur = 1.4
    t = t_axis(dur)
    out = np.zeros(len(t))
    for at, f in [(0.0, 880), (0.12, 1318.5)]:
        tt = np.clip(t - at, 0, None)
        tone = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
        out += tone * np.exp(-tt / 0.35) * (t >= at)
    return reverb(out, tail=0.8, mix=0.3)


if __name__ == "__main__":
    write("drone.wav", drone(), peak=0.8)
    write("hud-blips.wav", blips([0.0, 0.8, 1.6], alarm_at=2.35), peak=0.5)
    write("riser.wav", riser(), peak=0.75)
    write("implode.wav", implode(), peak=0.7)
    write("impact.wav", impact(), peak=0.95)
    write("shimmer.wav", shimmer(), peak=0.45)
    write("whoosh.wav", whoosh(), peak=0.5)
    write("start.wav", start_chime(), peak=0.55)
