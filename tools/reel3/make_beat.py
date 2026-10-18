"""Original beat-driven score for Gold Council reels (v3). Every sound is synthesized here, nothing sampled.

Usage: make_beat.py cues.json out.wav

Cue sheet:
  dur        total seconds
  bpm        tempo (100 = 2.4 s per bar, scene cuts land on bar lines)
  seed       random seed
  sections   [[start, end, kind]] with kind in intro | drop | break | outro
               intro: muffled half-time groove under the hook
               drop : full trap groove, 808, plucks, sidechained pad
               break: no kick, pad + hats + heartbeat, tension
               outro: pad tail only
  hits       [t, ...]      impact + sub drop (use on frame 0 and on big reveals)
  risers     [[a, b], ...] noise + pitch riser ending at b
  stutters   [t, ...]      glitch stutter
  counter    [[a, b], ...] rising tick counter
  typing     [[n, start, dur], ...]
  stamp      [t, ...]      rubber-stamp thud
  chime      [t, ...]      closing chime
  tapestop   t             pitch-down of the whole mix from t to the end
"""
import json, sys, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

cue = json.load(open(sys.argv[1]))
SR = 44100
DUR = float(cue["dur"]); N = int(SR * DUR); T = np.arange(N) / SR
BPM = float(cue.get("bpm", 100)); BEAT = 60 / BPM; STEP = BEAT / 4
rng = np.random.default_rng(cue.get("seed", 11))
midi = lambda m: 440.0 * 2 ** ((m - 69) / 12)

bus = {k: np.zeros((N, 2)) for k in ("drums", "bass", "music", "fx")}
def place(name, sig, at, gain=1.0, pan=0.0):
    i = int(round(at * SR))
    if i >= N or i + len(sig) <= 0: return
    s = sig * gain
    if i < 0: s = s[-i:]; i = 0
    j = min(N, i + len(s)); s = s[: j - i]
    bus[name][i:j, 0] += s * np.sqrt((1 - pan) / 2) * 1.414
    bus[name][i:j, 1] += s * np.sqrt((1 + pan) / 2) * 1.414

def filt(x, kind, f, order=2):
    f = np.atleast_1d(f) / (SR / 2); f = np.clip(f, 1e-4, 0.999)
    return sosfilt(butter(order, f if len(f) > 1 else f[0], kind, output="sos"), x, axis=0)
def env(n, a, d):
    x = np.arange(n) / SR; return np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / d)
IR = None
def reverb(x, mix=0.25):
    global IR
    if IR is None:
        n = int(SR * 2.2); IR = filt(rng.standard_normal(n) * np.exp(-np.arange(n) / (SR * 0.45)), "low", 4500)
        IR /= np.sqrt((IR ** 2).sum())
    ir = IR if x.ndim == 1 else IR[:, None]
    return x * (1 - mix) + fftconvolve(x, ir, axes=0)[: len(x)] * mix * 1.6

def kind_at(t):
    for a, b, k in cue["sections"]:
        if a <= t < b: return k
    return None

# ---------- instruments ----------
def kick(punch=1.0):
    n = int(SR * 0.42); x = np.arange(n) / SR
    f = 48 + 170 * np.exp(-x / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.16)
    click = filt(rng.standard_normal(n), "high", 2500) * env(n, 0.0003, 0.004) * 0.6
    return np.tanh((body + click) * 1.6 * punch)
def clap():
    n = int(SR * 0.35); s = np.zeros(n); x = rng.standard_normal(n)
    for k, d in enumerate((0, 0.011, 0.022)):
        i = int(d * SR); s[i:] += x[: n - i] * env(n - i, 0.0005, 0.012 if k < 2 else 0.09)
    return reverb(filt(s, "band", [900, 5000]) * 0.9, 0.3)
def hat(open_=False):
    n = int(SR * (0.32 if open_ else 0.05))
    return filt(rng.standard_normal(n), "high", 7000) * env(n, 0.0003, 0.09 if open_ else 0.013) * 0.55
def b808(note, length):
    n = int(SR * length); x = np.arange(n) / SR
    f = midi(note) * (1 + 0.6 * np.exp(-x / 0.02))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, length * 0.7)
    return np.tanh(s * 2.4) * 0.8   # saturation gives harmonics that phone speakers can play
def pluck(note, length=0.35):
    n = int(SR * length); x = np.arange(n) / SR; f = midi(note)
    s = (2 * ((f * x) % 1) - 1) * 0.5 + np.sin(2 * np.pi * f * x)
    return filt(s * env(n, 0.002, 0.11), "low", 3200) * 0.35
def padchord(notes, length):
    n = int(SR * length); x = np.arange(n) / SR; s = np.zeros(n)
    for m in notes:
        for det in (-0.08, 0.0, 0.08):
            f = midi(m) * (1 + det / 100); s += (2 * ((f * x + rng.random()) % 1) - 1)
    s = filt(s / (len(notes) * 3), "low", 1400)
    a = np.minimum(1, x / 0.25) * np.minimum(1, (length - x) / 0.2).clip(0)
    return s * a
def impact():
    n = int(SR * 2.0); x = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-x / 0.5) + 28) / SR) * env(n, 0.002, 0.7)
    boom = filt(rng.standard_normal(n), "low", 500) * env(n, 0.001, 0.25) * 1.4
    return reverb(np.tanh((sub + boom) * 1.5), 0.35)
def riser(length):
    n = int(SR * length); x = np.arange(n) / SR; k = x / length
    noise = rng.standard_normal(n); out = np.zeros(n); seg = 2048
    for i in range(0, n, seg):
        c = 400 + 9000 * k[min(i, n - 1)] ** 2
        out[i:i + seg] = filt(noise[i:i + seg + 0], "band", [c * 0.7, c * 1.3])[: len(out[i:i + seg])]
    tone = np.sin(2 * np.pi * np.cumsum(220 + 880 * k ** 2) / SR) * 0.25
    return (out * 1.5 + tone) * k ** 2
def tick(freq, gain):
    n = int(SR * 0.03)
    return (rng.standard_normal(n) * 0.5 + np.sin(2 * np.pi * freq * np.arange(n) / SR)) * env(n, 0.0005, 0.006) * gain
def key_click():
    n = int(SR * 0.02); return filt(rng.standard_normal(n), "low", 5000) * env(n, 0.0003, 0.004) * 0.5
def chime():
    n = int(SR * 2.0); x = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * midi(m) * x) * g for m, g in ((74, .5), (81, .3), (86, .2)))
    return reverb(s * env(n, 0.003, 0.6), 0.45) * 0.4

# ---------- arrangement ----------
CHORDS = [(38, (62, 65, 69)), (34, (62, 65, 70)), (31, (62, 67, 70)), (33, (61, 64, 69))]   # Dm Bb Gm A
KICK_STEPS = {0, 7, 10}; CLAP_STEPS = {4, 12}
side = np.ones(N)    # sidechain envelope from kicks
n_steps = int(DUR / STEP) + 1
for s in range(n_steps):
    t = s * STEP; k = kind_at(t)
    if k is None: continue
    bar, step = divmod(s, 16); root, tones = CHORDS[bar % 4]
    if step == 0 and k in ("intro", "drop", "break", "outro"):
        place("music", padchord(tones, 4 * BEAT + 0.3), t, 0.55 if k != "drop" else 0.45)
        if k == "break": place("bass", b808(root, 4 * BEAT) * 0.6, t)
    if k == "intro":
        if step in (0, 8): place("drums", kick(0.8), t, 0.8)
        if step == 8: place("drums", clap(), t, 0.35)
        if step % 4 == 2: place("drums", hat(), t, 0.5, 0.2)
        if step in (0,): place("bass", b808(root, 2 * BEAT), t, 0.7)
    elif k == "drop":
        if step in KICK_STEPS: place("drums", kick(), t, 1.0)
        if step in CLAP_STEPS: place("drums", clap(), t, 0.75)
        roll = step >= 12 and bar % 2 == 1
        if step % 2 == 0 or roll: place("drums", hat(), t + (0.012 if step % 4 == 2 else 0), 0.55 if step % 4 else 0.7, 0.25)
        if step == 14 and bar % 2 == 0: place("drums", hat(True), t, 0.35, -0.2)
        if step in KICK_STEPS: place("bass", b808(root + (12 if step == 10 and bar % 2 else 0), 3 * STEP + 0.05), t, 0.9)
        if step % 2 == 0: place("music", pluck(tones[(step // 2) % 3] + (12 if step >= 8 else 0)), t, 0.5, 0.3 if step % 4 else -0.3)
    elif k == "break":
        if step % 4 == 2: place("drums", hat(), t, 0.35, 0.2)
        if step in (0, 3): place("drums", kick(0.6), t, 0.55)          # heartbeat
    if k in ("intro", "drop") and step in KICK_STEPS | ({0, 8} if k == "intro" else set()):
        i = int(t * SR); n = min(N - i, int(SR * 0.22))
        if n > 0: side[i:i + n] = np.minimum(side[i:i + n], 0.45 + 0.55 * (np.arange(n) / n) ** 0.6)

for t in cue.get("hits", []): place("fx", impact(), t, 0.9)
for a, b in cue.get("risers", []): place("fx", riser(b - a), a, 0.45)
for a, b in cue.get("counter", []):
    t = a
    while t < b: place("fx", tick(1500 + 2500 * (t - a) / (b - a), 0.12), t); t += 0.05
for n_, s_, d_ in cue.get("typing", []):
    for c in range(n_): place("fx", key_click(), s_ + d_ * c / n_ + rng.uniform(0, 0.01), 0.9, rng.uniform(-.3, .3))
for t in cue.get("stamp", []): place("fx", reverb(kick(1.4), 0.25), t, 0.9)
for t in cue.get("chime", []): place("fx", chime(), t, 1.0)
for t in cue.get("stutters", []):
    pass  # applied after mix

# ---------- mix ----------
drums = bus["drums"]; bass = bus["bass"] * side[:, None]; music = reverb(bus["music"], 0.3) * side[:, None]
fx = bus["fx"]
# intro: muffle drums + music so the drop feels like a door opening
intro_mask = np.zeros(N)
for a, b, k in cue["sections"]:
    if k == "intro": intro_mask[int(a * SR): int(b * SR)] = 1
if intro_mask.any():
    muff = filt(drums + music, "low", 900)
    mix_dm = (drums + music) * (1 - intro_mask[:, None]) + muff * intro_mask[:, None] * 1.3
else:
    mix_dm = drums + music
mix = mix_dm + bass * 0.9 + fx
for t in cue.get("stutters", []):
    i = int(t * SR); seg = int(STEP / 2 * SR)
    if i + seg * 4 < N:
        piece = mix[i:i + seg].copy()
        for r in range(4): mix[i + r * seg: i + (r + 1) * seg] = piece * (1 - r * 0.15)
ts = cue.get("tapestop")
if ts is not None:
    i = int(ts * SR); n = N - i
    if n > 0:
        speed = np.linspace(1, 0.15, n); pos = i + np.cumsum(speed)
        pos = np.clip(pos, 0, N - 1)
        for ch in range(2): mix[i:, ch] = np.interp(pos, np.arange(N), mix[:, ch])
mix = np.tanh(mix * 0.9)
mix *= np.clip(T / 0.01, 0, 1)[:, None] * np.clip((DUR - T) / 0.35, 0, 1)[:, None]
mix *= 0.92 / np.max(np.abs(mix))
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", sys.argv[2])
