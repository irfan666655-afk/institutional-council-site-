"""Synthesize an original 18 s soundtrack for the Escape the Matrix reel: drone score, pulse beat, SFX synced to the cuts."""
import numpy as np, wave, sys

SR, DUR = 48000, 18.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def place(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if i >= N: return
    s = sig[: j - i] * gain
    L[i:j] += s * np.sqrt((1 - pan) / 2) * 1.414
    R[i:j] += s * np.sqrt((1 + pan) / 2) * 1.414

def env(n, a, d):  # attack / exponential decay, in seconds
    x = np.arange(n) / SR
    return np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / d)

def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.zeros_like(x); acc = 0.0
    for k in range(len(x)):
        acc = (1 - a) * x[k] + a * acc; y[k] = acc
    return y

def reverb(x, secs=1.6, mix=0.25):
    ir = rng.standard_normal(int(SR * secs)) * np.exp(-np.arange(int(SR * secs)) / (SR * secs / 5))
    ir = lowpass(ir, 2500)
    ir /= np.abs(ir).sum() / 4
    m = len(x) + len(ir) - 1; nfft = 1 << (m - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
    return x * (1 - mix) + wet * mix

midi = lambda m: 440 * 2 ** ((m - 69) / 12)

# ---------- 1. Drone score (D minor) ----------
def pad(freqs, amp):
    s = np.zeros(N)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ph = rng.uniform(0, 2 * np.pi)
            s += np.sin(2 * np.pi * f * (1 + det / 100) * t + ph) + 0.35 * np.sin(2 * np.pi * 2 * f * t + ph)
    return s * amp / (len(freqs) * 3)

swell = np.clip(t / 2.5, 0, 1) * np.clip((DUR - t) / 1.2, 0, 1)
drone = pad([midi(38), midi(45)], 0.22)                               # D2 + A2
drone += pad([midi(50), midi(53)], 0.07) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 6 - 1.5))  # D3 F3, breathing
lift = np.clip((t - 11.8) / 0.4, 0, 1)                                 # chord darkens to Bb at the flashes
drone += pad([midi(46), midi(53)], 0.10) * lift * np.clip((14.4 - t) / 0.3, 0, 1)
drone += pad([midi(38), midi(45), midi(50), midi(57)], 0.12) * np.clip((t - 14.5) / 0.4, 0, 1)  # full chord on the title
sub = np.sin(2 * np.pi * midi(26) * t) * 0.16 * np.clip((t - 2.6) / 2, 0, 1)
music = (drone + sub) * swell
music = reverb(music, 2.2, 0.3)
L += music; R += music * 0.97

# ---------- 2. Pulse beat (heartbeat kick, 100 BPM) ----------
def kick(f0=120, f1=42, length=0.45, gain=1.0):
    n = int(SR * length); x = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-x / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.13) * gain

beat = 0.6
bt = 2.6
while bt < 14.3:
    g = 0.45 if bt < 8.6 else 0.6
    place(kick(), bt, g); place(kick(), bt + 0.18, g * 0.55)           # lub-dub
    bt += beat * (2 if bt < 8.6 else 1)

# ticking clock 8.6 to 11.8
def tick(freq=3200, gain=0.12):
    n = int(SR * 0.03)
    return (rng.standard_normal(n) * 0.5 + np.sin(2 * np.pi * freq * np.arange(n) / SR)) * env(n, 0.0005, 0.006) * gain
tt, k = 8.6, 0
while tt < 11.75:
    place(tick(3400 if k % 2 == 0 else 2600), tt, pan=0.3 if k % 2 == 0 else -0.3); tt += beat / 2; k += 1

# ---------- 3. SFX ----------
def click(gain=0.09):
    n = int(SR * 0.02)
    return lowpass(rng.standard_normal(n), 5000) * env(n, 0.0003, 0.004) * gain * 3
def typing(text_len, start, dur):
    for c in range(text_len):
        place(click(0.08 + 0.04 * rng.random()), start + dur * c / text_len + rng.uniform(0, 0.01), pan=rng.uniform(-0.3, 0.3))
typing(15, 0.2, 1.0)          # INCOMING SIGNAL
typing(32, 3.2, 1.3)          # The night money lost its anchor.
typing(38, 8.7, 1.4)          # Since then, the ruler keeps shrinking.

def glitch(length=0.12, gain=0.35):
    n = int(SR * length); x = rng.standard_normal(n)
    hold = 40; x = np.repeat(x[::hold], hold)[:n]                    # bit-crush
    gate = (np.sin(2 * np.pi * 55 * np.arange(n) / SR) > 0).astype(float)
    return x * gate * env(n, 0.001, length / 2.5) * gain
for c in [2.6, 5.6, 8.6, 11.8, 14.4]:
    place(glitch(), c - 0.05, pan=0.2); place(glitch(0.08, 0.25), c, pan=-0.2)
place(glitch(0.1, 0.22), 2.62); place(glitch(0.06, 0.2), 2.85)        # date jitter

def beep(f, length, gain):
    n = int(SR * length); x = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * 2 * f * x)) * env(n, 0.003, length / 3) * gain
for k in range(9):                                                     # decrypt progress blips
    place(beep(1200 + k * 90, 0.05, 0.06), 0.5 + k * 0.19)
place(beep(midi(86), 0.5, 0.18), 2.2); place(beep(midi(93), 0.6, 0.12), 2.3)   # "signal decrypted" chime

def whoosh(length, f_from, f_to, gain):
    n = int(SR * length); x = rng.standard_normal(n)
    cut = np.linspace(f_from, f_to, n); y = np.zeros(n); acc = 0.0
    for k in range(n):
        a = np.exp(-2 * np.pi * cut[k] / SR); acc = (1 - a) * x[k] + a * acc; y[k] = acc
    shape = np.sin(np.pi * np.arange(n) / n) ** 1.5
    return y * shape * gain * 2.5
place(whoosh(0.45, 400, 4000, 0.18), 6.45, pan=-0.4)                   # strike-through slash
def impact(gain=1.0, tail=1.2):
    n = int(SR * tail)
    boom = kick(90, 30, tail, 1.0)
    noise = lowpass(rng.standard_normal(n), 600) * env(n, 0.001, 0.18) * 1.8
    return reverb(boom + noise, 1.5, 0.35) * gain
place(impact(0.9), 7.0)                                                # NEVER REVERSED stamp

n = int(SR * 2.0); x = np.arange(n) / SR                               # ruler shrink: falling tone
fall = np.sin(2 * np.pi * np.cumsum(np.linspace(660, 165, n)) / SR) * np.sin(np.pi * x / 2.0) * 0.12
place(reverb(fall, 1.0, 0.3), 9.4, pan=0.1)

for c in [11.8, 12.65, 13.5]:                                          # three flash hits
    place(impact(0.75, 0.9), c)
place(whoosh(0.85, 200, 9000, 0.22), 13.55)                             # riser into title
place(impact(1.15, 2.2), 14.45)                                        # title hit
for i in range(6):                                                     # MATRIX letters lock
    place(beep(midi(74 + [0, 3, 5, 7, 10, 12][i]), 0.09, 0.1), 15.1 + i * 0.16, pan=-0.5 + i * 0.2)
place(glitch(0.2, 0.3), 16.1)
place(reverb(beep(midi(62), 1.6, 0.16) + beep(midi(69), 1.6, 0.1), 2.0, 0.4), 16.4)  # closing tone

# ---------- master ----------
mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.1) / np.tanh(1.1)                                # soft clip
mix *= 0.89 / np.max(np.abs(mix))
fade = np.clip((DUR - t) / 0.6, 0, 1)[:, None]; mix *= fade
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote", sys.argv[1])
