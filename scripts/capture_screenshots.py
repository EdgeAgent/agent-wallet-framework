from PIL import Image, ImageDraw, ImageFont
import os
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT=os.path.join(BASE,"docs/screenshots"); os.makedirs(OUT,exist_ok=True)
def render(title,src,dst):
    lines=open(src).read().strip().splitlines()
    try: f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",20); fh=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",22)
    except: f=fh=ImageFont.load_default()
    W=1100; H=80+28*len(lines)+20; im=Image.new("RGB",(W,H),(11,18,32)); d=ImageDraw.Draw(im); d.text((30,25),title,font=fh,fill=(45,212,191))
    for i,l in enumerate(lines): d.text((30,70+28*i),l[:105],font=f,fill=(230,235,245))
    im.save(dst); open(dst.replace(".png",".txt"),"w").write(open(src).read())
render("AGENT WALLET — FUND, SAVE, GET PAID, SUBSCRIBE","/tmp/wallet-demo.txt",f"{OUT}/fund-save-subscribe.png")
render("AGENT WALLET — OVER-CAP SPEND BLOCKED","/tmp/wallet-blocked.txt",f"{OUT}/blocked-spend.png")
print("screenshots done")
