import soundfile as sf, json
from kokoro_onnx import Kokoro
k=Kokoro("kokoro.onnx","voices.bin")
V={"max":("am_adam",1.12),"tia":("af_heart",1.14),"off":("am_michael",1.0),"cp":("bm_george",1.08)}
SPEC=json.load(open(__import__("os").environ["SPEC"]))
LINES=SPEC["lines"]
dur={}; shown={}
for i,w,t,disp in LINES:
    v,s=V[w]; a,sr=k.create(t,voice=v,speed=s,lang="en-gb" if v.startswith("b") else "en-us"); sf.write(f"{i}.wav",a,sr); dur[i]=len(a)/sr; shown[i]=disp
# shots: kind,img,voice,role,cam,extra
PLAN=[("hook","c1","cp1","MAX, THE FILTER ENTHUSIAST","hookcam",0.1),
("talk","c2","tia1","TIA, THE FRIEND WHO WARNED HIM","push",0.0),
("talk","c1","max1","MAX","push",0.0),
("talk","c2","tia2","TIA","punch",0.0),
("talk","d3","max2","MAX","pull",0.05),
("freeze","d3",None,"","freeze",1.25),
("title","c3",None,"","title",1.35),
("talk","c3","off1","OFFICER DEADPAN","push",0.0),
("talk","c1","max3","MAX","pull",0.0),
("talk","c3","off2","OFFICER DEADPAN","punch",0.1),
("panic","c1","max4","MAX, PANICKING","panic",0.0),
("stamp","c3","off3","OFFICER DEADPAN","push",1.05),
("sad","d1","max5","MAX, 5 MINUTES LATER","pull",0.45),
("talk","d2","tia3","TIA","push",0.0),
("talk","c4","cp2","CAPTAIN PASSPORT","punch",0.35),
("end","c4",None,"","end",3.8)]
T=0.0; shots=[]
for kind,img,vo,role,cam,extra in PLAN:
    st=T
    if vo: va=st+0.1; end=va+dur[vo]+0.18+extra
    else: va=None; end=st+extra
    s=dict(kind=kind,img=img,voice=vo,role=role,cam=cam,start=st,end=end,voice_at=va); 
    if kind=="stamp": s["stamp_at"]=va+dur[vo]+0.1
    shots.append(s); T=end
json.dump(dict(shots=shots,dur=dur,shown=shown,total=T),open("timeline.json","w"),indent=1); print(round(T,2)); 
for s in shots: print(s["kind"],round(s["start"],2),round(s["end"],2),s["voice"])
