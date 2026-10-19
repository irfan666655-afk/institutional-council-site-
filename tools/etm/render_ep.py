"""Render one vertical episode. Usage: render_ep.py <doc dir> <ep number> [preview_seconds]"""
import json, sys, re, subprocess, pathlib
D = pathlib.Path(sys.argv[1]); n = int(sys.argv[2]); preview = float(sys.argv[3]) if len(sys.argv) > 3 else None
EPS = {e["ep"]: e for e in json.load(open(D / "episodes.json"))}
e = EPS[n]; a, b = e["a"], e["b"]
if n == 4: a = 342.5; b = 515.6                      # skip the title card so the episode stays under 3:00
TAIL = 3.0
cues = json.load(open(D / "cues_fixed.json"))
GOLD = r"{\c&H6ACFF0&}"; WHITE = r"{\c&HF1EADC&}"
def hl(t):
    t = t.replace("{", "(").replace("}", ")")
    return re.sub(r"((?:Rs |\$)?\d[\d,.]*(?:%| lakh| trillion| billion| tonnes| grams| times)?)", lambda m: GOLD + m.group(1) + WHITE, t)
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"
lines = []
for c in cues:
    s, t_end = max(c["s"], a), min(c["e"], b)
    if t_end - s < 0.3: continue
    lines.append(f"Dialogue: 0,{ts(s - a)},{ts(t_end - a)},Cap,,0,0,0,,{hl(c['t'])}")
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,IBM Plex Sans,48,&H00DCEAF1,&H00FFFFFF,&H00070505,&H64070505,-1,0,0,0,100,100,0,0,1,3,0,8,90,150,1195,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(lines) + "\n"
out = D / "eps"; out.mkdir(exist_ok=True)
assf = out / f"ep{n:02d}.ass"; assf.write_text(ass)
dur = b - a; total = dur + TAIL
fc = (f"[0:v]crop=1920:812:0:128,scale=1080:457,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={TAIL}[v];"
      f"[1:v][v]overlay=0:700:shortest=1[b];"
      f"color=c=0xF0CF6A:s=1080x6:r=24:d={total}[bar];"
      f"[b][bar]overlay=x='-1080+1080*min(t/{dur}\\,1)':y=1159:shortest=1[c];"
      f"[c]ass={assf}[d];"
      f"[2:v]format=rgba[e];"
      f"[d][e]overlay=0:0:enable='gte(t,{dur})'[vo];"
      f"[0:a]asetpts=PTS-STARTPTS,afade=t=out:st={dur-0.8}:d=0.8,apad=pad_dur={TAIL},loudnorm=I=-14:TP=-1.0:LRA=11,aresample=48000[ao]")
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-t", str(dur), "-i", str(D / "film.mp4"),
       "-loop", "1", "-framerate", "24", "-i", str(D / "frames" / f"frame_{n:02d}.png"),
       "-loop", "1", "-framerate", "24", "-i", str(D / "frames" / f"end_{n:02d}.png"),
       "-filter_complex", fc, "-map", "[vo]", "-map", "[ao]", "-t", str(total), "-r", "24"]
if preview is not None:
    cmd = cmd[:4] + [] + cmd[4:]
    png = out / f"ep{n:02d}_{preview:06.1f}.png"
    cmd = [x for x in cmd]
    cmd += ["-ss", str(preview), "-frames:v", "1", str(png)]
    i = cmd.index("-map", ); cmd = cmd[:i] + ["-map", "[vo]"] + cmd[i+4:]
else:
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-profile:v", "high",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out / f"ep{n:02d}.mp4")]
subprocess.run(cmd, check=True)
print("ep", n, round(total, 1), "s")
