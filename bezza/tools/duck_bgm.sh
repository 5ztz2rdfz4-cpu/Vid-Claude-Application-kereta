#!/usr/bin/env bash
# Side-chain duck the music bed under the voice-over -> assets/bgm_ducked.wav
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -v error -y -i assets/bgm.wav -i assets/vo.wav -filter_complex \
 "[1:a]apad=whole_dur=62.6,volume=1.0[sc];[0:a]equalizer=f=2500:t=q:w=1.2:g=-4[m];\
  [m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=450:makeup=1[d]" \
 -map "[d]" -ar 44100 assets/bgm_ducked.wav
