"""Split the Salam Automobile logo into transparent parts for the closing animation."""
import sys, numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
# Coverage alpha per brand colour, so pixels keep their true colour on any background
lum = im.mean(2)
mx0, mn0 = im.max(2), im.min(2)
is_gold = ((mx0 - mn0) / np.maximum(mx0, 1) > 0.18) & (mx0 > 110)
GOLD_LUM, DARK_LUM = 150.0, 34.0
cov = np.where(is_gold, (255 - lum) / (255 - GOLD_LUM), (255 - lum) / (255 - DARK_LUM))
alpha = np.clip((cov - 0.04) / 0.96, 0, 1)
a = np.maximum(alpha, 1e-3)[..., None]
rgb = np.clip(255 - (255 - im) / a, 0, 255)
# fully-opaque core pixels keep their original colour exactly
rgb = np.where(alpha[..., None] >= 0.999, im, rgb)
rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)
def rows(mask):
    r = np.where(mask.any(1))[0]; return r
mask = alpha > 0.15
# horizontal bands with content
r = mask.any(1); bands = []; i = 0
while i < len(r):
    if r[i]:
        j = i
        while j < len(r) and r[j]: j += 1
        bands.append((i, j)); i = j
    else: i += 1
print("bands", bands)
def save(name, y0, y1, img=rgba):
    sub = mask[y0:y1]; cols = np.where(sub.any(0))[0]
    x0, x1 = cols[0], cols[-1] + 1
    pad = 6
    crop = img[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad]
    Image.fromarray(crop).save(f"{out}/{name}.png")
    print(name, crop.shape, "x", x0, "y", y0)
# gold vs charcoal separation (by saturation of unmultiplied colour)
gold = is_gold
def layer(sel):
    o = rgba.copy(); o[..., 3] = np.where(sel, o[..., 3], 0); return o
gold_l, dark_l = layer(gold), layer(~gold)
# light version: charcoal -> off-white (for dark backgrounds)
light = rgba.copy(); light[~gold, :3] = (245, 242, 236)
H, W = mask.shape
# Full-width crops share the same x-origin so parts stay registered
def save_full(name, y0, y1, img):
    Image.fromarray(img[y0 - 6:y1 + 6, 100:W - 100]).save(f"{out}/{name}.png")
(e0, e1), (s0, s1), (m0, m1), (t0, t1) = bands
save_full("logo-emblem-gold", e0, e1, gold_l)
save_full("logo-emblem-dark", e0, e1, dark_l)
save_full("logo-salam", s0, s1, rgba)
save_full("logo-auto-text", m0, m1, dark_l)
save_full("logo-auto-lines", m0, m1, gold_l)
save_full("logo-tagline", t0, t1, rgba)
Image.fromarray(rgba[e0 - 10:t1 + 10, 100:W - 100]).save(f"{out}/logo-full.png")
Image.fromarray(light[e0 - 10:e1 + 6, 100:W - 100]).save(f"{out}/logo-emblem-light.png")
print("crop x 100..", W - 100, "emblem rows", e0, e1)
