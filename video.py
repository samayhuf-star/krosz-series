import sys, math, json, subprocess, os, random, numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
TL=json.load(open("timeline.json")); SH=TL["shots"]; DUR=TL["dur"]; SHOWN=TL["shown"]; TOTAL=TL["total"]+0.6
SPEC=json.load(open(os.environ["SPEC"]))
FP="/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
def logo(d,cx,cy,s,word=True,wcol=(255,255,255)):
    k=s/64.0; x0=cx-32*k; y0=cy-32*k
    P=lambda x,y:(x0+x*k,y0+y*k)
    d.rounded_rectangle([x0+2*k,y0+2*k,x0+62*k,y0+62*k],radius=int(15*k),fill=NAVY+(255,),outline=(255,255,255,40),width=max(1,int(k)))
    w=max(2,int(3.4*k))
    d.line([P(50,14),P(18,28.5)],fill=BLUE,width=w); d.line([P(30,36.5),P(39.5,27)],fill=BLUE,width=w)
    d.line([P(50,14),P(40.5,49.5),P(30,36.5),P(50,14)],fill=BLUE,width=w,joint="curve")
def font(s): return ImageFont.truetype(FP,s)
ACC=(96,168,255); BLUE=(46,122,244); NAVY=(11,20,31); RED=(255,64,64); WHITE=(255,255,255)
K=1080/864
FACE={"c1":(370,400),"c2":(410,430),"c3":(470,520),"c4":(500,600),"d1":(450,390),"d2":(460,420),"d3":(470,370)}
MOUTH={"c1":(415,440,100,62,True),"c2":(405,482,72,54,True),"c3":(485,575,64,48,False),"c4":(505,668,92,62,False),"d1":(470,437,68,52,False),"d2":(455,495,78,52,True),"d3":(465,418,64,48,True)}
env={}
for n in DUR:
    a,s=sf.read(f"{n}.wav"); hop=s//FPS; e=np.array([np.sqrt(np.mean(a[i:i+hop]**2)) for i in range(0,len(a),hop)])
    env[n]=np.clip(e/(np.percentile(e,90)+1e-6),0,1)
BASE={}
for c in FACE: BASE[c]=Image.open(f"{c}.png").convert("RGB").resize((W,H),Image.LANCZOS).filter(ImageFilter.UnsharpMask(2,70,2))
def blurdark(c,r,k): return Image.eval(BASE[c].filter(ImageFilter.GaussianBlur(r)),lambda v:int(v*k))
BG_TITLE=blurdark("c3",16,0.45); BG_END=blurdark("c4",18,0.5)
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def lerp(a,b,t): return a+(b-a)*t
def shot_at(t):
    for s in SH:
        if s["start"]<=t<s["end"]: return s
    return SH[-1]
def vstate(s,t):
    if not s["voice"] or s["kind"]=="hook": return 0
    n=s["voice"]; lt=t-s["voice_at"]
    if lt<0 or lt>DUR[n]: return 0
    return float(env[n][min(int(lt*FPS),len(env[n])-1)])
def draw_mouth(im,c,m,t):
    cx,cy,w,hm,teeth=MOUTH[c]; cx*=K; cy*=K; w*=K; hm*=K
    h=max(6,hm*(0.25+0.75*m)*(0.9+0.1*math.sin(t*50))); ww=w*(0.85+0.2*m)
    L=Image.new("RGBA",im.size,(0,0,0,0)); d=ImageDraw.Draw(L)
    d.ellipse([cx-ww/2,cy-h*0.45,cx+ww/2,cy+h*0.65],fill=(64,16,26,255)); d.ellipse([cx-ww*0.32,cy+h*0.12,cx+ww*0.32,cy+h*0.62],fill=(214,96,108,255))
    if teeth: d.rounded_rectangle([cx-ww*0.36,cy-h*0.45,cx+ww*0.36,cy-h*0.45+h*0.18],radius=6,fill=(250,248,244,255))
    L=L.filter(ImageFilter.GaussianBlur(1.6)); im.paste(L,(0,0),L)
def pill(d,x,y,text,f,fill,fg,pad=34):
    w=d.textlength(text,font=f); d.rounded_rectangle([x-w/2-pad,y-f.size*0.85,x+w/2+pad,y+f.size*0.85],radius=int(f.size),fill=fill); d.text((x,y),text,font=f,fill=fg,anchor="mm")
def big(d,lines,y,size,t0,t,cols=None,shake=0):
    f=font(size); lh=int(size*1.2)
    for i,s in enumerate(lines):
        p=ease((t-t0-i*0.12)/0.2)
        if p<=0: continue
        x=W/2+math.sin(t*90+i)*shake; yy=y+i*lh+(1-p)*60; col=cols[i] if cols else WHITE
        d.text((x+5,yy+6),s,font=f,fill=(0,0,0),anchor="mm"); d.text((x,yy),s,font=f,fill=col,anchor="mm")
def subs(im,s,t):
    if not s["voice"] or s["kind"]=="hook" and False: return
    n=s["voice"]; lt=t-s["voice_at"]
    if lt<-0.05 or lt>DUR[n]+0.2: return
    words=SHOWN[n].split(); d=ImageDraw.Draw(im,"RGBA"); f=font(66); lines=[[]]
    for w in words:
        c=" ".join(lines[-1]+[w])
        if d.textlength(c,font=f)>900 and lines[-1]: lines.append([w])
        else: lines[-1].append(w)
    idx=min(len(words)-1,max(0,int(lt/DUR[n]*len(words)))); k=0; y=1290
    for ln in lines:
        x=(W-d.textlength(" ".join(ln),font=f))/2
        for w in ln:
            for ox,oy in ((-3,-3),(3,-3),(-3,3),(3,3),(0,5)): d.text((x+ox,y+oy),w,font=f,fill=(0,0,0))
            d.text((x,y),w,font=f,fill=ACC if k==idx else WHITE); x+=d.textlength(w+" ",font=f); k+=1
        y+=84
def speed_lines(im,t0,t,n=34,col=(255,255,255)):
    p=(t-t0)/0.28
    if p<0 or p>1: return
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L); cx,cy=W/2,900; a=int(150*(1-p))
    for i in range(n):
        ang=i/n*2*math.pi+(i%3)*0.03; r0=380+300*p; r1=r0+700
        d.polygon([(cx+math.cos(ang-0.012)*r0,cy+math.sin(ang-0.012)*r0),(cx+math.cos(ang+0.012)*r0,cy+math.sin(ang+0.012)*r0),(cx+math.cos(ang)*r1,cy+math.sin(ang)*r1)],fill=col+(a,))
    im.paste(L,(0,0),L)
def sparkles(im,t,seed=3):
    r=random.Random(seed); d=ImageDraw.Draw(im,"RGBA")
    for i in range(16):
        x,y=r.randint(60,1020),r.randint(300,1200); ph=r.random()*6; a=0.5+0.5*math.sin(t*5+ph); s=int(14+26*a)
        d.polygon([(x,y-s),(x+s*0.25,y-s*0.25),(x+s,y),(x+s*0.25,y+s*0.25),(x,y+s),(x-s*0.25,y+s*0.25),(x-s,y),(x-s*0.25,y-s*0.25)],fill=(255,236,150,int(220*a)))
def rain(im,t):
    r=random.Random(5); d=ImageDraw.Draw(im,"RGBA")
    for i in range(70):
        x=r.randint(0,W); sp=r.randint(900,1500); y=((t*sp+r.randint(0,H))%(H+200))-100; d.line([(x,y),(x-12,y+50)],fill=(190,210,255,90),width=3)
ANN=SPEC["ann"]
def camera(s,lt,p):
    img=s["img"]; fx,fy=FACE[img]; bx,by=432,720; c=s["cam"]; e=ease(p)
    if c=="push": z=1.06+0.44*e; f=(lerp(bx,fx,e),lerp(by,fy,e))
    elif c=="pull": z=1.52-0.44*e; f=(lerp(fx,bx,e),lerp(fy,by,e))
    elif c=="punch":
        if p<0.5: z=1.08+0.1*p; f=(bx,by)
        else: z=1.7+0.15*(p-0.5); f=(fx,fy-20)
    elif c=="panic": z=1.4; f=(fx,fy)
    elif c=="hookcam": z=1.1+0.5*ease(lt/(s["end"]-s["start"])); f=(lerp(bx,fx,e),lerp(by,fy,e))
    elif c=="freeze": z=1.55+0.04*lt; f=(fx,fy)
    else: z=1.12; f=(bx,by)
    z+=0.07*math.exp(-lt*12); return z,f[0]*K,f[1]*K
def render_scene(t):
    s=shot_at(t); k=s["kind"]; lt=t-s["start"]; dur=s["end"]-s["start"]; p=lt/dur; c=s["img"]; m=vstate(s,t)
    if k=="title": base=BG_TITLE.copy()
    elif k=="end": base=BG_END.copy()
    else: base=BASE[c].copy()
    if k=="hook": base=Image.eval(base,lambda v:int(v*0.72))
    if m>0.1 and k in("talk","panic","stamp","sad"): draw_mouth(base,c,m,t)
    if k=="panic":
        d=ImageDraw.Draw(base)
        for j,(sx,sy) in enumerate(((330,430),(640,400),(700,560))):
            yy=sy+((t*260+j*110)%150); d.polygon([(sx,yy-34),(sx-20,yy+10),(sx+20,yy+10)],fill=(130,205,255)); d.ellipse([sx-20,yy-6,sx+20,yy+34],fill=(130,205,255))
    z,fx,fy=camera(s,lt,p); rot=1.2*math.sin(t*2.3); jx=10*math.sin(t*1.3+s["start"]); jy=8*math.cos(t*1.7)
    if k=="panic": rot+=2.8*math.sin(t*38); jx+=18*math.sin(t*61); jy+=14*math.cos(t*53)
    if k=="stamp" and t>=s["stamp_at"]:
        q=t-s["stamp_at"]; sh=26*math.exp(-q*8); jx+=sh*math.sin(q*140); jy+=sh*math.cos(q*113)
    if k=="freeze": rot=0; jx=jy=0
    cx=min(max(fx+jx,540/z),W-540/z); cy=min(max(fy+jy,960/z),H-960/z)
    th=math.radians(rot); cth,sth=math.cos(th),math.sin(th); a=cth/z; b=-sth/z; d_=sth/z; e=cth/z
    im=base.transform((W,H),Image.AFFINE,(a,b,cx-(a*540+b*960),d_,e,cy-(d_*540+e*960)),resample=Image.BICUBIC)
    d=ImageDraw.Draw(im,"RGBA")
    if k=="hook":
        pass
        if lt<1.0: big(d,[SPEC["hook"][0]],420,70,0,lt); big(d,[SPEC["hook"][1]],600,SPEC.get("hook_size",150),0.1,lt,[RED])
        elif lt<2.2: big(d,[SPEC["hook"][2]],420,70,1.0,lt); big(d,[SPEC["hook"][3]],610,SPEC.get("hook_size",150),1.1,lt,[ACC],shake=(6 if lt<1.5 else 0))
        if lt>2.0:
            q=ease((lt-2.0)/0.25); d.rectangle([0,1160,W,1250],fill=(20,20,28,235)); d.rectangle([0,1160,230*q,1250],fill=(220,30,40,255)); d.text((115*q,1205),"BREAKING",font=font(34),fill=WHITE,anchor="mm")
            tx=SPEC["ticker"]
            f=font(36); w=d.textlength(tx,font=f); off=-((lt*200)%w)+250
            d.text((off,1205),tx,font=f,fill=WHITE,anchor="lm"); d.text((off+w,1205),tx,font=f,fill=WHITE,anchor="lm"); d.rectangle([0,1160,230,1250],fill=(220,30,40,255)); d.text((115,1205),"BREAKING",font=font(34),fill=WHITE,anchor="mm")
        if lt<0.3: speed_lines(im,0,lt,col=RED)
    elif k=="title":
        big(d,SPEC["title"],700,160,0.0,lt,[WHITE,ACC],shake=(5 if lt<0.4 else 0))
        if lt>0.6: pill(d,540,1050,SPEC["title_sub"],font(46),(255,255,255,235),(20,20,40))
    elif k=="freeze":
        if lt>0.05:
            r=int(330*ease(lt/0.25)); d.ellipse([540-r,840-r,540+r,840+r],outline=(255,50,50,255),width=14)
            pill(d,540,330,SPEC["freeze"],font(42),(255,50,50,240),WHITE)
            d.line([(540,390),(540,500)],fill=(255,50,50,255),width=10); d.polygon([(540,540),(515,490),(565,490)],fill=(255,50,50,255))
        if lt>0.5: d.text((540,1450),"*crickets*",font=font(54),fill=(255,255,255,int(230*min(1,(lt-0.5)*4))),anchor="mm")
    elif k=="end":
        logo(d,540,380,150); d.text((540,520),"Krosz.",font=font(84),fill=(255,255,255),anchor="mm"); big(d,["Check the visa"],690,92,0.1,lt); big(d,["BEFORE","the ticket."],830,128,0.4,lt,[ACC,ACC])
        sc=1+0.04*math.sin(lt*6); pp=ease((lt-1.0)/0.4)
        if pp>0: pill(d,540,1170,"krosz.com",font(int(92*sc*pp)+1),BLUE+(255,),(255,255,255),pad=64)
        if lt>1.8: pill(d,540,1360,SPEC["teaser"],font(34),(255,255,255,230),(20,20,40))
        if lt>2.2: d.text((540,1450),"Visa rules vary by country. AI-generated animation.",font=font(28),fill=(215,225,245),anchor="mm")
    else:
        pass
        if k=="sad": rain(im,t)
        if lt>0.12 and s["role"]:
            q=ease((lt-0.12)/0.25); role=s["role"]; f=font(28); wr=d.textlength(role,font=f)
            xx=50-(1-q)*500; d.rounded_rectangle([xx,170,xx+wr+70,232],radius=31,fill=(0,0,0,170)); d.ellipse([xx+20,191,xx+40,211],fill=ACC); d.text((xx+52,201),role,font=f,fill=WHITE,anchor="lm")
        n=s["voice"]
        if n in ANN and lt>0.7:
            txt=ANN[n]+("."*(int(t*4)%4) if n=="max1" else "")
            pill(d,540,330,txt,font(46),(255,255,255,238),(20,20,40))
        if k=="panic":
            pu=1+0.1*math.sin(t*24); big(d,["!!"],400,int(190*pu),0.1,lt,[RED],shake=8)
            ov=Image.new("RGBA",(W,H),(255,30,30,int(40+30*math.sin(t*14)))); im.paste(ov,(0,0),ov); speed_lines(im,s["start"],t,col=RED)
        if k=="stamp" and t>=s["stamp_at"]:
            q=t-s["stamp_at"]; sc=0.85*(1+2.2*max(0,1-q/0.12))
            Lh=Image.new("RGBA",(900,420),(0,0,0,0)); dd=ImageDraw.Draw(Lh)
            dd.rounded_rectangle([10,10,890,410],30,outline=(235,40,50),width=16); dd.text((450,130),SPEC["stamp"][0],font=font(120),fill=(235,40,50),anchor="mm"); dd.text((450,285),SPEC["stamp"][1],font=font(120),fill=(235,40,50),anchor="mm")
            Lh=Lh.rotate(-10,expand=True); Lh=Lh.resize((int(Lh.width*sc),int(Lh.height*sc))); im.paste(Lh,(int(W/2-Lh.width/2),int(1000-Lh.height/2)),Lh)
            speed_lines(im,s["stamp_at"],t)
            if q<0.06: fl=Image.new("RGBA",(W,H),(255,255,255,150)); im.paste(fl,(0,0),fl)
        subs(im,s,t)
    return im,s,lt
rng=np.random.default_rng(1); GR=[rng.normal(0,3.5,(H,W,1)).astype(np.float32) for _ in range(6)]
yy,xx=np.mgrid[0:H,0:W]; VG=(1-0.48*(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.65))**2)).clip(0.3,1)[...,None].astype(np.float32)
def frame(t):
    im,s,lt=render_scene(t)
    if s["start"]>0 and lt<0.1:  # zoom-blur cut
        z=im.transform((W,H),Image.AFFINE,(0.93,0,W*0.035,0,0.93,H*0.035),resample=Image.BILINEAR); im=Image.blend(im,z,0.5)
    small=im.resize((270,480)).filter(ImageFilter.GaussianBlur(4)).resize((W,H),Image.BILINEAR)
    arr=np.asarray(im,dtype=np.float32)+0.16*np.asarray(small,dtype=np.float32)
    if s["start"]>0 and lt<0.12:
        f=1-lt/0.12; arr=arr+60*f; sh=int(14*f); arr[:,:,0]=np.roll(arr[:,:,0],sh,1); arr[:,:,2]=np.roll(arr[:,:,2],-sh,1)
    if s["kind"]=="sad": arr=arr*np.array([0.82,0.92,1.12],dtype=np.float32)
    if s["kind"]=="freeze": g=arr.mean(2,keepdims=True); arr=0.55*arr+0.45*g
    arr=arr*VG+GR[int(t*FPS)%6]; arr[:,:,0]*=1.03; arr[:,:,2]*=1.02
    out=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)); d=ImageDraw.Draw(out)
    d.rounded_rectangle([46,52,262,116],32,fill=NAVY); logo(d,80,84,46); d.text((112,84),"Krosz.",font=font(30),fill=(255,255,255),anchor="lm"); return out
def render_chunk(args):
    i0,i1,path=args
    p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","30","-i","-","-c:v","libx264","-crf","24","-preset","veryfast","-pix_fmt","yuv420p","-g","30",path],stdin=subprocess.PIPE)
    for i in range(i0,i1): p.stdin.write(frame(i/FPS).tobytes())
    p.stdin.close(); assert p.wait()==0; return path
if __name__=="__main__":
    if sys.argv[1]=="stills":
        for t in [float(x) for x in sys.argv[2:]]: frame(t).save(f"w_{t:g}.png")
    else:
        from multiprocessing import Pool
        n=int(TOTAL*FPS); nc=max(2,(os.cpu_count() or 2)); step=-(-n//(nc*2)); jobs=[(i,min(n,i+step),f"chunk_{i//step:02d}.mp4") for i in range(0,n,step)]
        with Pool(nc) as pool: files=pool.map(render_chunk,jobs)
        open("list.txt","w").write("".join(f"file '{f}'\n" for f in files))
        subprocess.check_call(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i","list.txt","-c","copy","video_only.mp4"])
        subprocess.check_call(["ffmpeg","-y","-loglevel","error","-i","video_only.mp4","-i","mix.wav","-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart","episode.mp4"]); print("done")
