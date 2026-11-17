import numpy as np, sys
from PIL import Image, ImageFilter
src, out = sys.argv[1], sys.argv[2]
I = Image.open(src).convert('RGB'); im = np.asarray(I).astype(np.float32)
r,g,b = im[...,0],im[...,1],im[...,2]
mn = np.minimum(np.minimum(r,g),b); mx=np.maximum(np.maximum(r,g),b); sat=mx-mn
gold_core = sat>45
gm = Image.fromarray((gold_core*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))
near_gold = np.asarray(gm)>0
GOLD = np.array([200,160,98],np.float32)
a_gold = np.clip((255-b)/(255-GOLD[2]),0,1)*near_gold
a_dark = np.clip((255-mn)/(255-32),0,1)*(~near_gold)
a_all = np.maximum(a_gold, a_dark)
def save(a, rgb, box, name):
    x0,y0,x1,y1 = box
    if rgb.ndim==1: rgb = np.broadcast_to(rgb, im.shape)
    o = np.dstack([rgb, a*255])[y0:y1,x0:x1]
    Image.fromarray(np.clip(o,0,255).astype(np.uint8),'RGBA').save(f'{out}/{name}.png')
gold_rgb = np.where(gold_core[...,None], im, GOLD)
icon=(190,280,1120,700); salam=(110,700,1150,830); auto=(110,840,1150,915); tag=(140,935,1110,975)
save(a_gold, gold_rgb, icon,'icon_gold')
save(a_dark, np.array([28,30,36.]), icon,'icon_dark')
save(a_dark, np.array([245,240,230.]), icon,'icon_light')
save(a_all, np.where(near_gold[...,None], gold_rgb, np.array([28,30,36.])), icon,'icon_full')
save(a_dark, np.array([28,30,36.]), salam,'salam')
save(a_dark, np.array([40,42,48.]), auto,'automobile')
save(a_gold, gold_rgb, auto,'auto_lines')
save(a_dark, np.array([70,70,76.]), tag,'tagline')
