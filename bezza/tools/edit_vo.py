"""Tighten the voice-over: drop unneeded lines, compress pauses, light speed-up.
Writes assets/vo.wav and assets/words_edit.json (word timings in output time)."""
import numpy as np, json, subprocess, sys, wave
SRC_WAV, WORDS, OUT_DIR = sys.argv[1], sys.argv[2], sys.argv[3]
SR = 48000
TEMPO = 1.08
CUTS = [(20.95, 27.0), (55.80, 56.74)]          # "dan ini antara sebab..." / "untuk maklumat"
MAX_GAP, KEEP_GAP = 0.28, 0.16

raw = subprocess.run(["ffmpeg","-v","error","-i",SRC_WAV,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout
a = np.frombuffer(raw, np.float32).copy(); dur = len(a)/SR
# silence map (20ms frames, -40 dB)
fr = int(0.02*SR); n = len(a)//fr
db = 20*np.log10(np.sqrt((a[:n*fr].reshape(n,fr)**2).mean(1))+1e-9)
sil = db < -40
gaps=[]; i=0
while i<n:
    if sil[i]:
        j=i
        while j<n and sil[j]: j+=1
        s,e=i*0.02,j*0.02
        if e-s>MAX_GAP and s>0.05: gaps.append((s+KEEP_GAP/2, e-KEEP_GAP/2))
        i=j
    else: i+=1
removes = sorted(CUTS+gaps)
# merge
merged=[]
for s,e in removes:
    if merged and s<=merged[-1][1]: merged[-1]=(merged[-1][0],max(e,merged[-1][1]))
    else: merged.append((s,e))
keeps=[]; t=0
for s,e in merged:
    if s>t: keeps.append((t,s))
    t=max(t,e)
keeps.append((t,dur-0.3))
# concat with 8ms crossfade-ish fades
xf=int(0.008*SR); parts=[]
for s,e in keeps:
    seg=a[int(s*SR):int(e*SR)].copy()
    if len(seg)>2*xf:
        seg[:xf]*=np.linspace(0,1,xf); seg[-xf:]*=np.linspace(1,0,xf)
    parts.append(seg)
out=np.concatenate(parts)
def mapt(t):
    acc=0
    for s,e in keeps:
        if t<s: return acc/TEMPO
        if t<=e: return (acc+t-s)/TEMPO
        acc+=e-s
    return acc/TEMPO
tmp=OUT_DIR+"/_vo_cat.f32"; out.astype(np.float32).tofile(tmp)
subprocess.run(["ffmpeg","-v","error","-y","-f","f32le","-ar",str(SR),"-ac","1","-i",tmp,
  "-af",f"highpass=f=80,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,atempo={TEMPO},loudnorm=I=-15:TP=-1.5:LRA=7",
  "-ar",str(SR),"-ac","2",OUT_DIR+"/vo.wav"],check=True)
W=json.load(open(WORDS)); res=[]
for w in W:
    mid=(w['s']+w['e'])/2
    if any(s<=mid<=e for s,e in CUTS): continue
    res.append(dict(w=w['w'],s=round(mapt(w['s']),3),e=round(mapt(w['e']),3),os=w['s']))
json.dump(res,open(OUT_DIR+"/words_edit.json","w"),ensure_ascii=False,indent=0)
print("keeps",len(keeps),"out dur", round(len(out)/SR/TEMPO,2))
