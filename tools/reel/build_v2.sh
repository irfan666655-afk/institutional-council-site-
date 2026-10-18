#!/bin/bash
set -e
R=$(cd "$(dirname "$0")" && pwd); F=${FONTSOURCE:?set FONTSOURCE to node_modules/@fontsource}
n=$1; d=$2
python3 $R/make_video.py $R/v2_$n.html $F $R/out/v2_${n}_silent.mp4 $d
python3 $R/make_score.py $R/cues_v2_$n.json $R/out/v2_$n.wav
ffmpeg -y -loglevel error -i $R/out/v2_${n}_silent.mp4 -i $R/out/v2_$n.wav -af "loudnorm=I=-14:TP=-1.0:LRA=11" -ar 48000 -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart $R/out/v2_$n.mp4
echo built $n
