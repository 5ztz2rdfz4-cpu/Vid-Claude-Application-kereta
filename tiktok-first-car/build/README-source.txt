# 1) HDR (HLG) iPhone 4K -> SDR 1080x1920 30fps
ffmpeg -i IMG_7473.MOV -map 0:v:0 -map 0:a:0 \
  -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=1080:1920:flags=lanczos,fps=30" \
  -c:v libx264 -preset veryfast -crf 16 -c:a aac -b:a 192k source_1080.mp4
# 2) Voice clean-up + loudness (-14 LUFS for TikTok)
ffmpeg -i source_1080.mp4 -map 0:v -map 0:a -c:v copy \
  -af "highpass=f=80,afftdn=nf=-28,acompressor=threshold=-20dB:ratio=3:attack=10:release=150:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=9" \
  -c:a aac -b:a 192k -ar 48000 assets/video/aroll.mp4
