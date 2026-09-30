#!/bin/sh
# Renders both language versions and muxes them with the soundtrack.
set -e
cd "$(dirname "$0")"
FF=${FFMPEG:-ffmpeg}
python3 music.py out/music.wav
for L in it en; do
  FFMPEG=$FF node render.mjs $L out/video_${L}_noaudio.mp4
  $FF -hide_banner -loglevel error -y -i out/video_${L}_noaudio.mp4 -i out/music.wav -map 0:v -map 1:a \
    -c:v libx264 -preset slow -crf 21 -maxrate 14M -bufsize 28M -pix_fmt yuv420p \
    -af loudnorm=I=-14:TP=-1.5:LRA=7 -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart \
    out/3DT_Infraplan_Menorca_reel_45s_$(echo $L | tr a-z A-Z).mp4
done
