"""Render a vertical clip stitched from one or more film segments (trailer, highlights).
Usage: render_clip.py <doc dir> <spec.json>
spec: {"name":..., "segments":[[a,b],...], "frame":"frames/x.png", "end":"frames/y.png", "tail":3.5, optional "film":"a.mp4", "film_offset":140}"""
import json, sys, re, subprocess, pathlib
D = pathlib.Path(sys.argv[1]); S = json.load(open(sys.argv[2]))
cues = json.load(open(D / "cues_fixed.json"))
GOLD = r"{\c&H6ACFF0&}"; WHITE = r"{\c&HF1EADC&}"
def hl(t):
    t = t.replace("{", "(").replace("}", ")")
    return re.sub(r"((?:Rs |\$)?\d[\d,.]*(?:%| lakh| trillion| billion| tonnes| grams| times)?)", lambda m: GOLD + m.group(1) + WHITE, t)
def ts(x):
    return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
lines = []; off = 0.0
for a, b in S["segments"]:
    for c in cues:
        s, e = max(c["s"], a), min(c["e"], b)
        if e - s >= 0.3: lines.append(f"Dialogue: 0,{ts(s-a+off)},{ts(e-a+off)},Cap,,0,0,0,,{hl(c['t'])}")
    off += b - a
dur = off; tail = S.get("tail", 3.0); total = dur + tail
out = D / "clips"; out.mkdir(exist_ok=True)
assf = out / f"{S['name']}.ass"
assf.write_text("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,IBM Plex Sans,50,&H00DCEAF1,&H00FFFFFF,&H00070505,&H64070505,-1,0,0,0,100,100,0,0,1,3,0,8,90,150,1195,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(lines) + "\n")
parts = []; k = len(S["segments"])
for i, (a, b) in enumerate(S["segments"]):
    d = b - a
    j = i + 2
    parts.append(f"[{j}:v]setpts=PTS-STARTPTS,crop=1920:812:0:128,scale=1080:457,fade=t=in:st=0:d=0.15,fade=t=out:st={d-0.15}:d=0.15[v{i}];"
                 f"[{j}:a]asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.12,afade=t=out:st={d-0.25}:d=0.25[a{i}];")
fc = "".join(parts) + "".join(f"[v{i}][a{i}]" for i in range(k)) + f"concat=n={k}:v=1:a=1[vc][ac];"
fc += (f"[vc]tpad=stop_mode=clone:stop_duration={tail}[v];[0:v][v]overlay=0:700:shortest=1[b];"
       f"color=c=0xF0CF6A:s=1080x6:r=24:d={total}[bar];[b][bar]overlay=x='-1080+1080*min(t/{dur}\\,1)':y=1159:shortest=1[c];"
       f"[c]ass={assf}[d];[1:v]format=rgba[e];[d][e]overlay=0:0:enable='gte(t,{dur})'[vo];"
       f"[ac]apad=pad_dur={tail},loudnorm=I=-14:TP=-1.0:LRA=11,aresample=48000[ao]")
segin = []
FILM = D / S.get("film", "film.mp4"); OFF = float(S.get("film_offset", 0))  # partial film: file time 0 = film time OFF
for a, b in S["segments"]: segin += ["-ss", str(a - OFF), "-t", str(b - a), "-i", str(FILM)]
cmd = ["ffmpeg", "-y", "-loglevel", "error",
       "-loop", "1", "-framerate", "24", "-i", str(D / S["frame"]), "-loop", "1", "-framerate", "24", "-i", str(D / S["end"])] + segin + [
       "-filter_complex", fc, "-map", "[vo]", "-map", "[ao]", "-t", str(total), "-r", "24",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
       "-movflags", "+faststart", str(out / f"{S['name']}.mp4")]
subprocess.run(cmd, check=True)
print(S["name"], round(total, 1))
