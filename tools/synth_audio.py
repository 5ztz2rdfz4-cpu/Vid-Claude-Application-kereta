import numpy as np, wave, sys, os
SR=48000
out=sys.argv[1]
def save(name,x,st=False):
    x=np.asarray(x,np.float32)
    if not st: x=np.stack([x,x],1)
    pk=np.max(np.abs(x))+1e-9; x=x/pk*0.89
    with wave.open(os.path.join(out,name),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
        w.writeframes((x*32767).astype(np.int16).tobytes())
rng=np.random.default_rng(7)
def t(d): return np.arange(int(d*SR))/SR
def env(n,a,r):
    e=np.ones(n);A=int(a*SR);R=int(r*SR)
    if A: e[:A]=np.linspace(0,1,A)
    if R: e[-R:]*=np.linspace(1,0,R)**2
    return e
def lp(x,c):  # one-pole lowpass, c array or scalar (Hz)
    c=np.broadcast_to(np.asarray(c,float),x.shape); a=1-np.exp(-2*np.pi*c/SR)
    y=np.empty_like(x);s=0.
    for i in range(len(x)): s+=a[i]*(x[i]-s); y[i]=s
    return y
def bp(x,c): return lp(x,c*1.6)-lp(x,c*0.6)
# ---------- SFX ----------
d=0.6;n=int(d*SR);tt=t(d);noise=rng.standard_normal(n)
c=300+3500*np.sin(np.pi*tt/d)**2
save('whoosh.wav',bp(noise,c)*np.sin(np.pi*tt/d)**1.5)
d=0.35;tt=t(d);noise=rng.standard_normal(len(tt))
save('swish.wav',bp(noise,2000+4000*tt/d)*np.sin(np.pi*tt/d)**2)
d=0.12;tt=t(d);f=900*np.exp(-tt*30)+300
save('pop.wav',np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*35))
d=0.05;tt=t(d);save('tick.wav',(np.sin(2*np.pi*2400*tt)+0.5*rng.standard_normal(len(tt)))*np.exp(-tt*120))
d=1.6;tt=t(d);noise=rng.standard_normal(len(tt))
saw=((tt*(120+600*(tt/d)**2))%1)*2-1
r=bp(noise,500+5000*(tt/d)**2)*0.8+lp(saw,1500)*0.4
save('riser.wav',r*(tt/d)**2*env(len(tt),0,0.03))
d=1.4;tt=t(d);f=55+120*np.exp(-tt*18)
boom=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*3.2)
crack=lp(rng.standard_normal(len(tt)),3000)*np.exp(-tt*25)*0.6
save('impact.wav',np.tanh(1.6*(boom+crack)))
d=1.2;tt=t(d)
ding=sum(a*np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,a,k in [(1318,1,4),(2637,.4,6),(3951,.2,9),(1975,.25,5)])
save('ding.wav',ding*env(len(tt),0.003,0.05))
d=0.25;tt=t(d);save('stamp.wav',np.tanh(3*(np.sin(2*np.pi*np.cumsum(140*np.exp(-tt*8)+40)/SR)*np.exp(-tt*14)+0.5*lp(rng.standard_normal(len(tt)),2500)*np.exp(-tt*40))))
# ---------- MUSIC ----------
BPM=112;beat=60/BPM;L=52.0;N=int(L*SR);mix=np.zeros((N,2))
def add(sig,start,pan=0.0,g=1.0):
    i=int(start*SR);j=min(N,i+len(sig))
    if i>=N: return
    s=sig[:j-i]*g; mix[i:j,0]+=s*(1-pan)*0.5*2**0.5; mix[i:j,1]+=s*(1+pan)*0.5*2**0.5
kt=t(0.4);kick=np.sin(2*np.pi*np.cumsum(50+110*np.exp(-kt*28))/SR)*np.exp(-kt*7);kick=np.tanh(2*kick)
ht=t(0.06);hat=bp(rng.standard_normal(len(ht)),8000)*np.exp(-ht*70)
ct=t(0.25);clap=bp(rng.standard_normal(len(ct)),1500)*(np.exp(-ct*22)+0.4*np.exp(-((ct-0.012)%0.011)*300)*(ct<0.035))
def mtof(m): return 440*2**((m-69)/12)
prog=[(57,[57,60,64]),(53,[53,57,60]),(48,[52,55,60]),(55,[55,59,62])]  # Am F C G
bars=int(L/(4*beat))+1
for b in range(bars):
    t0=b*4*beat;root,ch=prog[b%4]
    intro=t0<5.0; outro=t0>47.5
    for k in range(4):
        tb=t0+k*beat
        if not intro or k in (0,2): add(kick,tb,0,0.9 if not intro else 0.5)
        if k in (1,3) and not intro: add(clap,tb,0.05,0.35)
        for h in (0,0.5):
            add(hat,tb+h*beat,0.3,0.12 if h==0 else 0.18)
    # bass: 8ths
    bt=t(beat*0.48)
    for e in range(8):
        f=mtof(root-24+(12 if e%4==3 else 0))
        s=np.sin(2*np.pi*f*bt)+0.3*np.sin(4*np.pi*f*bt); s*=env(len(bt),0.005,0.05)
        add(np.tanh(1.5*s),t0+e*beat/2,0,0.32)
    # pad
    pt=t(4*beat)
    pad=sum(np.sign(np.sin(2*np.pi*mtof(m)*pt*(1+dt)))*0.5+np.sin(2*np.pi*mtof(m+12)*pt) for m in ch for dt in (-0.003,0.003))
    pad=lp(pad*env(len(pt),0.3,0.4),1400 if not intro else 700)
    add(pad,t0,0,0.05)
    # pluck arp 16ths
    at_=t(beat/4*0.9)
    notes=[ch[0]+12,ch[1]+12,ch[2]+12,ch[1]+24]
    if not intro:
        for e in range(16):
            f=mtof(notes[e%4]); s=(((at_*f)%1)*2-1); s=lp(s*np.exp(-at_*18),2500)
            add(s,t0+e*beat/4,(-0.4 if e%2 else 0.4),0.09)
# master: fade in/out
fade=np.ones(N);fi=int(0.3*SR);fade[:fi]=np.linspace(0,1,fi);fo=int(3*SR);fade[-fo:]=np.linspace(1,0,fo)
mix*=fade[:,None]; mix=np.tanh(mix*1.2)
save('music.wav',mix,st=True)
print('ok')
