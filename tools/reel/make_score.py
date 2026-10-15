"""Original synthesized score + SFX for a Gold Council reel, driven by a JSON cue sheet. Usage: make_score.py cues.json out.wav"""
import numpy as np, wave, sys, json

cue = json.load(open(sys.argv[1]))
SR, DUR = 48000, float(cue["dur"])
N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.default_rng(cue.get("seed", 7))
L = np.zeros(N); R = np.zeros(N)
midi = lambda m: 440 * 2 ** ((m - 69) / 12)

def place(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if i >= N or j <= i: return
    s = sig[: j - i] * gain
    L[i:j] += s * np.sqrt((1 - pan) / 2) * 1.414; R[i:j] += s * np.sqrt((1 + pan) / 2) * 1.414
def env(n, a, d):
    x = np.arange(n) / SR; return np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / d)
def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.zeros_like(x); acc = 0.0
    for k in range(len(x)): acc = (1 - a) * x[k] + a * acc; y[k] = acc
    return y
def fftconv(x, ir):
    m = len(x) + len(ir) - 1; n = 1 << (m - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]
IR = {}
def reverb(x, secs=1.6, mix=0.25):
    if secs not in IR:
        ir = rng.standard_normal(int(SR * secs)) * np.exp(-np.arange(int(SR * secs)) / (SR * secs / 5))
        ir = lowpass(ir, 2500); IR[secs] = ir / (np.abs(ir).sum() / 4)
    return x * (1 - mix) + fftconv(x, IR[secs]) * mix

# drone
def pad(freqs, amp):
    s = np.zeros(N)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ph = rng.uniform(0, 2 * np.pi)
            s += np.sin(2 * np.pi * f * (1 + det / 100) * t + ph) + 0.35 * np.sin(2 * np.pi * 2 * f * t + ph)
    return s * amp / (len(freqs) * 3)
swell = np.clip(t / 2.5, 0, 1) * np.clip((DUR - t) / 1.2, 0, 1)
music = pad([midi(38), midi(45)], 0.22) + pad([midi(50), midi(53)], 0.07) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 6 - 1.5))
for a, b in cue.get("dark", []):   # Bb colour
    music += pad([midi(46), midi(53)], 0.10) * np.clip((t - a) / 0.4, 0, 1) * np.clip((b - t) / 0.3, 0, 1)
fc = cue.get("full_chord")
if fc is not None: music += pad([midi(38), midi(45), midi(50), midi(57)], 0.12) * np.clip((t - fc) / 0.4, 0, 1)
music += np.sin(2 * np.pi * midi(26) * t) * 0.16 * np.clip((t - cue["heartbeat"][0]) / 2, 0, 1)
music = reverb(music * swell, 2.2, 0.3); L += music; R += music * 0.97

def kick(f0=120, f1=42, length=0.45):
    n = int(SR * length); x = np.arange(n) / SR; f = f1 + (f0 - f1) * np.exp(-x / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.13)
hb0, hb1, fast = cue["heartbeat"][0], cue["heartbeat"][1], cue.get("heartbeat_fast", 1e9)
bt = hb0
while bt < hb1:
    g = 0.45 if bt < fast else 0.6
    place(kick(), bt, g); place(kick(), bt + 0.18, g * 0.55); bt += 0.6 * (2 if bt < fast else 1)

def tick(freq, gain=0.12):
    n = int(SR * 0.03)
    return (rng.standard_normal(n) * 0.5 + np.sin(2 * np.pi * freq * np.arange(n) / SR)) * env(n, 0.0005, 0.006) * gain
for a, b in cue.get("clock", []):
    tt, k = a, 0
    while tt < b: place(tick(3400 if k % 2 == 0 else 2600), tt, pan=0.3 if k % 2 == 0 else -0.3); tt += 0.3; k += 1
for a, b in cue.get("counter", []):          # rapid rising ticks
    tt = a
    while tt < b: place(tick(1500 + 2500 * (tt - a) / (b - a), 0.09), tt); tt += 0.05

def click(gain):
    n = int(SR * 0.02); return lowpass(rng.standard_normal(n), 5000) * env(n, 0.0003, 0.004) * gain * 3
for n_, s_, d_ in cue.get("typing", []):
    for c in range(n_): place(click(0.08 + 0.04 * rng.random()), s_ + d_ * c / n_ + rng.uniform(0, 0.01), pan=rng.uniform(-0.3, 0.3))

def glitch(length=0.12, gain=0.35):
    n = int(SR * length); x = rng.standard_normal(n); x = np.repeat(x[::40], 40)[:n]
    gate = (np.sin(2 * np.pi * 55 * np.arange(n) / SR) > 0).astype(float)
    return x * gate * env(n, 0.001, length / 2.5) * gain
for c in cue["cuts"]: place(glitch(), c - 0.05, pan=0.2); place(glitch(0.08, 0.25), c, pan=-0.2)
for c in cue.get("glitches", []): place(glitch(0.1, 0.24), c)

def beep(f, length, gain):
    n = int(SR * length); x = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * 2 * f * x)) * env(n, 0.003, length / 3) * gain
pb = cue.get("progress")
if pb:
    a, b = pb
    for k in range(9): place(beep(1200 + k * 90, 0.05, 0.06), a + k * (b - a) / 9)
for c in cue.get("chimes", []): place(beep(midi(86), 0.5, 0.18), c); place(beep(midi(93), 0.6, 0.12), c + 0.1)
for c, m, ln, g in cue.get("blips", []): place(beep(midi(m), ln, g), c)

def whoosh(length, f_from, f_to, gain):
    n = int(SR * length); x = rng.standard_normal(n); cut = np.linspace(f_from, f_to, n); y = np.zeros(n); acc = 0.0
    for k in range(n): a = np.exp(-2 * np.pi * cut[k] / SR); acc = (1 - a) * x[k] + a * acc; y[k] = acc
    return y * np.sin(np.pi * np.arange(n) / n) ** 1.5 * gain * 2.5
for c, ln, f0, f1, g in cue.get("whooshes", []): place(whoosh(ln, f0, f1, g), c, pan=-0.3)
def impact(gain=1.0, tail=1.2):
    n = int(SR * tail)
    noise = lowpass(rng.standard_normal(n), 600) * env(n, 0.001, 0.18) * 1.8
    return reverb(kick(90, 30, tail) + noise, 1.5, 0.35) * gain
for c, g, tl in cue.get("impacts", []): place(impact(g, tl), c)
for c, ln, f0, f1 in cue.get("falls", []):
    n = int(SR * ln); x = np.arange(n) / SR
    place(reverb(np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f1, n)) / SR) * np.sin(np.pi * x / ln) * 0.12, 1.0, 0.3), c, pan=0.1)
for c in cue.get("closing", []):
    place(reverb(beep(midi(62), 1.6, 0.16) + beep(midi(69), 1.6, 0.1), 2.0, 0.4), c)

mix = np.stack([L, R], 1); mix = np.tanh(mix * 1.1) / np.tanh(1.1); mix *= 0.89 / np.max(np.abs(mix))
mix *= np.clip((DUR - t) / 0.6, 0, 1)[:, None]
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", sys.argv[2])
