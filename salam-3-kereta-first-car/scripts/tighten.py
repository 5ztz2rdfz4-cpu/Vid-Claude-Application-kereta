# Shorten pauses > 0.4s down to 0.3s; output tightened VO + time map
import subprocess, re, json, sys, numpy as np, wave
src, out, mapf = sys.argv[1:4]
log = subprocess.run(['ffmpeg','-v','info','-i',src,'-af','silencedetect=n=-38dB:d=0.25','-f','null','-'],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',log)]; en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',log)]
w=wave.open(src); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)
keep=0.30; segs=[]; cur=0.0
for s,e in zip(st,en):
    if e-s>0.4 and e<59.0:
        cut_s=s+keep/2; cut_e=e-keep/2
        segs.append((cur,cut_s)); cur=cut_e
segs.append((cur,59.45))
pieces=[]; fade=int(0.01*sr); m=[]; t=0
for s,e in segs:
    p=a[int(s*sr):int(e*sr)].copy(); p[:fade]*=np.linspace(0,1,fade); p[-fade:]*=np.linspace(1,0,fade)
    pieces.append(p); m.append([s,e,t]); t+=e-s
o=np.concatenate(pieces); o=o/np.abs(o).max()*0.89*32767
ww=wave.open(out,'wb'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(sr); ww.writeframes(o.astype(np.int16).tobytes())
json.dump(m,open(mapf,'w')); print('new len',t)
