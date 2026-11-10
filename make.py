"""Usage: python3 make.py specs/<ep>.json outdir  -> outdir/episode.mp4 (1080x1920, ~16MB)"""
import sys,os,subprocess,shutil
root=os.path.dirname(os.path.abspath(__file__)); spec=os.path.abspath(sys.argv[1]); out=os.path.abspath(sys.argv[2]); os.makedirs(out,exist_ok=True)
models=os.path.join(root,"models")
for f,u in (("kokoro.onnx","https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"),("voices.bin","https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin")):
    p=os.path.join(models,f)
    if not os.path.exists(p) or os.path.getsize(p)<1e6: os.makedirs(models,exist_ok=True); subprocess.check_call(["curl","-sSL","-o",p,u])
    if not os.path.exists(os.path.join(out,f)): os.symlink(p,os.path.join(out,f))
for c in ("c1","c2","c3","c4","d1","d2","d3"):
    d=os.path.join(out,c+".png")
    if not os.path.exists(d): os.symlink(os.path.join(root,"assets",c+".png"),d)
env=dict(os.environ,SPEC=spec)
for s in ("tts.py","audio.py","video.py"):
    a=["python3",os.path.join(root,s)]+(["render"] if s=="video.py" else [])
    subprocess.check_call(a,cwd=out,env=env)
subprocess.check_call(["ffmpeg","-y","-loglevel","error","-i",os.path.join(out,"episode.mp4"),"-c:v","libx264","-crf","27","-maxrate","5M","-bufsize","10M","-preset","medium","-c:a","copy","-movflags","+faststart",os.path.join(out,"final.mp4")])
print("OK",os.path.join(out,"final.mp4"))
