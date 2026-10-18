#!/bin/bash
# Usage: build_v3.sh <name> <seconds>   (reads v3_<name>.html + cues_v3_<name>.json, writes out/v3_<name>.mp4)
set -e
R=$(cd "$(dirname "$0")" && pwd); F=${FONTSOURCE:-$R/../fontpkg/node_modules/@fontsource}
n=$1; d=$2; mkdir -p $R/out
python3 $R/make_video.py $R/v3_$n.html $F $R/out/v3_${n}_silent.mp4 $d
python3 $R/make_beat.py $R/cues_v3_$n.json $R/out/v3_$n.wav
ffmpeg -y -loglevel error -i $R/out/v3_${n}_silent.mp4 -i $R/out/v3_$n.wav -af "loudnorm=I=-14:TP=-1.0:LRA=11" -ar 48000 -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart $R/out/v3_$n.mp4
echo built $n
