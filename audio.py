import numpy as np, soundfile as sf, json
from scipy.signal import butter, lfilter, resample_poly
TL=json.load(open("timeline.json")); sh=TL["shots"]; T=TL["total"]+0.6
sr=44100; N=int(T*sr); rng=np.random.default_rng(11)
def tt(d): return np.arange(int(d*sr))/sr
def put(buf,x,at,g=1.0):
    i=int(at*sr); e=min(N,i+len(x))
    if 0<=i<N: buf[i:e]+=x[:e-i]*g
def lp(x,f,o=2): b,a=butter(o,f/(sr/2),'low'); return lfilter(b,a,x)
def hp(x,f,o=2): b,a=butter(o,f/(sr/2),'high'); return lfilter(b,a,x)
def bandp(x,c): b,a=butter(2,[c*0.7/(sr/2),min(0.99,c*1.3/(sr/2))],'band'); return lfilter(b,a,x)
def kick(): t=tt(0.3); f=45+95*np.exp(-t*28); return np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-t*9)
def clap(): t=tt(0.22); return hp(rng.standard_normal(len(t)),900)*np.exp(-t*22)*0.8
def hat(o=False): t=tt(0.25 if o else 0.05); return hp(rng.standard_normal(len(t)),7000)*np.exp(-t*(18 if o else 90))*0.35
def bass(f,d): t=tt(d); x=lp(np.sign(np.sin(2*np.pi*f*t))*0.6+np.sin(2*np.pi*f*t),320); return x*np.minimum(1,t*80)*np.exp(-t*3.5)*0.9
def pluck(f,d=0.3): t=tt(d); x=sum(np.sin(2*np.pi*f*k*t)/k for k in (1,2,3)); return lp(x,3500)*np.exp(-t*9)*0.5
def whoosh(d=0.5,up=True):
    t=tt(d); n=rng.standard_normal(len(t)); y=np.zeros_like(n); ch=8; seg=len(t)//ch
    for i in range(ch): y[i*seg:(i+1)*seg]=bandp(n[i*seg:(i+1)*seg],300+(i if up else ch-i)*900)
    return y*np.sin(np.pi*np.minimum(1,t/d))**2*0.9
def impact(d=1.2): t=tt(d); return (np.sin(2*np.pi*(38+60*np.exp(-t*12))*t)*np.exp(-t*3.2)+lp(rng.standard_normal(len(t)),2500)*np.exp(-t*6)*0.6)*1.1
def riser(d=2.3): t=tt(d); f=180+1400*(t/d)**2; return (np.sin(2*np.pi*np.cumsum(f)/sr)*0.35+hp(rng.standard_normal(len(t)),2500)*(t/d)**2*0.5)*(t/d)**1.5
def ding(f=1320,d=0.9): t=tt(d); return (np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*2.01*t))*np.exp(-t*4.5)*0.5
def tick(): t=tt(0.04); return hp(rng.standard_normal(len(t)),3000)*np.exp(-t*120)*0.8
def boom(): t=tt(0.9); return (np.sin(2*np.pi*(55+90*np.exp(-t*9))*t)*np.exp(-t*4)+lp(rng.standard_normal(len(t)),900)*np.exp(-t*8)*0.5)*1.2
def scratch():
    t=tt(0.55); f=3800*np.exp(-t*4.5)+200; n=rng.standard_normal(len(t)); y=np.zeros_like(n); seg=len(t)//14
    for i in range(14): y[i*seg:(i+1)*seg]=bandp(n[i*seg:(i+1)*seg],max(250,3800*np.exp(-(i/14)*2.6)))
    return y*(0.6+0.4*np.sign(np.sin(2*np.pi*11*t)))*np.exp(-t*2.2)*1.3
def crickets(d=1.2):
    t=tt(d); x=np.zeros(len(t))
    for g in (0.05,0.55):
        for k in range(5):
            tt0=int((g+k*0.075)*sr); seg=tt(0.04); x[tt0:tt0+len(seg)]+=np.sin(2*np.pi*4300*seg)*np.hanning(len(seg))*0.35
    return x
def trombone():
    out=np.zeros(int(2.4*sr)); pos=0.0
    for f0,f1,dd in ((233,220,0.42),(220,208,0.42),(208,196,0.42),(196,160,1.1)):
        t=tt(dd); f=np.linspace(f0,f1,len(t))+ (6*np.sin(2*np.pi*5.5*t) if dd>1 else 0)
        ph=2*np.pi*np.cumsum(f)/sr; x=lp(2*((ph/(2*np.pi))%1)-1+0.5*np.sin(ph),1500)*np.minimum(1,t*30)*np.exp(-t*0.8)*0.6
        i=int(pos*sr); out[i:i+len(x)]+=x[:len(out)-i]; pos+=dd
    return out*0.9
music=np.zeros(N); sfx=np.zeros(N); voice=np.zeros(N)
hook=sh[0]; 
put(sfx,impact(1.0),0.0,0.9); put(sfx,riser(hook["end"]-0.1),0.1,0.8)
for k in range(5): put(sfx,tick(),0.45*k+0.2,0.9)
put(sfx,whoosh(0.4,True),1.0,0.5); put(sfx,impact(1.4),hook["end"],1.0)
# breakdown windows: title card + stamp hold
off=[]
for s in sh:
    if s["kind"] in("title","freeze"): off.append((s["start"],s["end"]))
    if s["kind"]=="stamp": off.append((s["stamp_at"],s["end"]))
    if s["kind"]=="end": pass
endcard=[s for s in sh if s["kind"]=="end"][0]
def on(t): 
    if t<hook["end"]: return False
    return not any(a<=t<b for a,b in off) and t<endcard["end"]-0.5
beat=0.46; bars=[55.0,43.65,65.41,49.0]; notes=[220,261.63,329.63,392,329.63,261.63,293.66,349.23]
i=0
while hook["end"]+i*beat<endcard["end"]:
    tm=hook["end"]+i*beat; bi=int(i//4)
    if on(tm):
        if i%2==0 or i%4==3: put(music,kick(),tm,0.95)
        if i%4 in (1,3): put(music,clap(),tm,0.7)
        put(music,hat(),tm,0.35); put(music,hat(),tm+beat/2,0.6)
        put(music,bass(bars[bi%4],beat*0.95),tm,0.9)
        put(music,pluck(notes[i%8]*(2 if bi%2 else 1)),tm,0.5); put(music,pluck(notes[(i+3)%8]),tm+beat/2,0.35)
    i+=1
for a,b in off:
    t=tt(b-a); put(music,lp(np.sin(2*np.pi*110*t)+np.sin(2*np.pi*164.8*t),600)*np.minimum(1,t*10)*0.3,a)
dur=TL["dur"]; DUR_=dur
for s in sh:
    if s["start"]>0: put(sfx,whoosh(0.28,s["start"]*7%2<1),s["start"]-0.17,0.5)
    if s["kind"]=="title": put(sfx,ding(1318),s["start"]+0.1,0.8); put(sfx,ding(988),s["start"]+0.4,0.8)
    if s["kind"]=="stamp": put(sfx,impact(1.2),s["stamp_at"],1.0)
    if s["kind"]=="panic": put(sfx,boom(),s["start"]+0.05,0.6)
    if s["kind"]=="freeze": put(sfx,scratch(),s["start"],0.9); put(sfx,crickets(),s["start"]+0.45,0.8)
    if s["kind"]=="sad": put(sfx,trombone(),s["voice_at"]+DUR_[s["voice"]]-0.1,0.55)
    if s["kind"]=="end": put(sfx,impact(1.5),s["start"],0.9); put(sfx,ding(1568,1.2),s["start"]+0.15,0.9); put(sfx,ding(2093,1.2),s["start"]+0.35,0.7)
    if s["voice"] if "voice" in s else None:
        n=s["voice"]; a,sr0=sf.read(f"{n}.wav"); a=a/np.max(np.abs(a))*0.9
        if sr0!=sr: a=resample_poly(a,sr,sr0)
        put(voice,a,s["voice_at"],1.0)
        if n in("max2","tia2","off2"): put(sfx,boom(),s["voice_at"]+dur[n]+0.05,0.45)
env=np.abs(voice); w=int(0.12*sr); env=np.convolve(env,np.ones(w)/w,'same'); m=np.clip(env*6,0,1)
mix=music*0.5*(1-0.62*m)+sfx*0.55*(1-0.35*m)+voice
fo=int(1.8*sr); f=np.ones(N); f[-fo:]=np.linspace(1,0,fo); mix*=f
mix=np.tanh(mix*1.2)/np.tanh(1.2); mix=mix/np.max(np.abs(mix))*0.92
sf.write("mix.wav",mix.astype(np.float32),sr); print("ok",T)
