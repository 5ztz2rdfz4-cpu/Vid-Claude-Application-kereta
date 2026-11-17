#!/usr/bin/env bash
# Two-pass loudness master to TikTok level (-14 LUFS, -1 dBTP).
# Usage: scripts/master_audio.sh <premaster.wav> <out.wav>
set -euo pipefail
IN="$1"; OUT="$2"
J=$(ffmpeg -hide_banner -i "$IN" -af loudnorm=I=-14:TP=-1.0:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
MI=$(echo "$J" | python3 -I -c "import json,sys;d=json.load(sys.stdin);print(f\"measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}\")")
ffmpeg -v error -y -i "$IN" -af "loudnorm=I=-14:TP=-1.0:LRA=9:$MI:linear=true" -ar 48000 -c:a pcm_s16le "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
