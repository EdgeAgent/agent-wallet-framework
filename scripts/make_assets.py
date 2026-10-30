from PIL import Image, ImageDraw, ImageFont
import os
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT=os.path.join(BASE,"docs/assets"); os.makedirs(OUT,exist_ok=True)
def font(sz,bold=False):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",sz)
    except: return ImageFont.load_default()
def wallet_icon(d,cx,cy,s,color):
    d.rounded_rectangle([cx-s,cy-s*0.7,cx+s,cy+s*0.7],radius=18,outline=color,width=6)
    d.line([(cx-s*0.4,cy-s*0.2),(cx+s*0.5,cy-s*0.2)],fill=color,width=6)
    d.ellipse([cx+s*0.15,cy-s*0.05,cx+s*0.45,cy+s*0.25],outline=color,width=5)
def icon(path,size):
    im=Image.new("RGB",(size,size),(11,18,32)); d=ImageDraw.Draw(im); d.ellipse([size//2-size*0.42,size//2-size*0.42,size//2+size*0.42,size//2+size*0.42],fill=(20,40,70)); wallet_icon(d,size//2,size//2,size*0.24,(45,212,191)); d.text((size//2,size*0.82),"WALLET",font=font(size//11,True),fill=(255,255,255),anchor="mm"); im.save(path)
def hero():
    im=Image.new("RGB",(1200,400),(11,18,32)); d=ImageDraw.Draw(im); d.rectangle([0,340,1200,400],fill=(45,212,191)); wallet_icon(d,110,170,70,(45,212,191))
    d.text((220,120),"AGENT WALLET",font=font(84,True),fill=(255,255,255)); d.text((220,230),"Fund it. Save it. Get paid. Spend gated.",font=font(40,True),fill=(45,212,191)); d.text((220,290),"Subscriptions, products, and services — only with approval, caps, and a kill switch.",font=font(26),fill=(200,210,230)); d.text((30,358),"No real money in the skeleton  •  Provider stubs only  •  No keys in code",font=font(24,True),fill=(11,18,32)); im.save(f"{OUT}/hero.png")
def flow(path,title,boxes,sub):
    W,H=1400,460; im=Image.new("RGB",(W,H),(245,247,250)); d=ImageDraw.Draw(im); d.text((40,30),title,font=font(36,True),fill=(11,18,32)); d.text((40,75),sub,font=font(22),fill=(80,90,110))
    n=len(boxes); bw=170; gap=(W-80-(bw*n))//(n-1) if n>1 else 0; y=180
    for i,b in enumerate(boxes):
        x=40+i*(bw+gap); d.rounded_rectangle([x,y,x+bw,300],radius=18,fill=(11,18,32)); d.text((x+bw//2,240),b,font=font(20,True),fill=(255,255,255),anchor="mm")
        if i<n-1: d.polygon([(x+bw+5,240),(x+bw+gap-5,225),(x+bw+gap-5,255)],fill=(45,212,191))
    d.rectangle([40,340,W-40,410],fill=(251,191,36)); d.text((W//2,375),"GATE  •  unapproved / over-cap / non-allowlisted / killed = BLOCKED",font=font(22,True),fill=(11,18,32),anchor="mm"); im.save(path)
icon(f"{OUT}/icon.png",512); icon(f"{OUT}/favicon.png",64); hero()
flow(f"{OUT}/workflow.png","HOW MONEY MOVES — SAFELY",["FUND","SAVE","GET PAID","ASK","APPROVE","SPEND","RECEIPT"],"Fund, save, and get paid in. Agent asks, you approve, then it spends — with a receipt.")
flow(f"{OUT}/architecture.png","ARCHITECTURE",["CLI","LEDGER","GATE","CAPS","SUBS","SAVINGS","RECEIPTS"],"Ledger only. Providers are stubs. Real payment happens in your own provider / bank app.")
print("assets done")
