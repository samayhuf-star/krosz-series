"""Usage: R2_ACCOUNT=.. R2_KEY=.. R2_SECRET=.. python3 r2up.py file.mp4 key.mp4  (bucket krosz-reels, public url printed)"""
import sys,os,boto3
from botocore.config import Config
s=boto3.client("s3",endpoint_url=f"https://{os.environ['R2_ACCOUNT']}.r2.cloudflarestorage.com",aws_access_key_id=os.environ["R2_KEY"],aws_secret_access_key=os.environ["R2_SECRET"],region_name="auto",config=Config(signature_version="s3v4",s3={"addressing_style":"path"}))
s.upload_file(sys.argv[1],"krosz-reels",sys.argv[2],ExtraArgs={"ContentType":"video/mp4"})
print("https://pub-7415f286d54c432b8b7f2c1e744dd1e5.r2.dev/"+sys.argv[2])
