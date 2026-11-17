"""Split the Salam Automobile logo PNG (white bg) into transparent animation layers."""
import sys
import numpy as np
from PIL import Image

src, outdir = sys.argv[1], sys.argv[2]
im = np.array(Image.open(src).convert("RGB")).astype(np.float32)
R, G, B = im[..., 0], im[..., 1], im[..., 2]
H, W = R.shape

# sample colours
dmask = (im.max(axis=2) < 70)
gmask = ((R - B) > 80) & (B < 120)
dark_fg = im[dmask].mean(axis=0)
gold_B = np.median(B[gmask])
print("dark", dark_fg, "goldB", gold_B)

ratio = (R - B) / (255 - B + 1e-3)
is_gold = (ratio > 0.32) & ((255 - B) > 6)
alpha_gold = np.clip((255 - B) / (255 - gold_B), 0, 1)
alpha_dark = np.clip((255 - G) / (255 - dark_fg[1]), 0, 1)
alpha = np.where(is_gold, alpha_gold, alpha_dark)
alpha[(im.min(axis=2) > 246)] = 0
a3 = np.maximum(alpha[..., None], 1e-3)
col_gold = np.clip((im - (1 - a3) * 255) / a3, 0, 255)
col = np.where(is_gold[..., None], col_gold, dark_fg[None, None, :])

# crop box with margin
y0, y1, x0, x1 = 280, 985, 105, 1150
def save(name, mask, color=None):
    rgba = np.zeros((H, W, 4), np.float32)
    rgba[..., :3] = col if color is None else color
    rgba[..., 3] = alpha * 255 * mask
    Image.fromarray(rgba[y0:y1, x0:x1].astype(np.uint8), "RGBA").save(f"{outdir}/{name}.png", optimize=True)

yy = np.arange(H)[:, None] * np.ones((1, W))
band_mark = (yy < 700)
band_salam = (yy >= 700) & (yy < 845)
band_auto = (yy >= 845) & (yy < 925)
band_tag = (yy >= 925)
g = is_gold.astype(np.float32)
d = 1 - g
save("logo_full", np.ones((H, W)))
save("mark_gold", band_mark * g)
save("mark_dark", band_mark * d)
save("word_salam", band_salam)
save("word_auto_text", band_auto * d)
save("word_auto_lines", band_auto * g)
save("word_tag", band_tag)
# light versions for dark backgrounds
cream = np.array([245, 240, 230], np.float32)[None, None, :]
light_col = np.where(is_gold[..., None], col_gold, cream)
def save_light(name, mask):
    rgba = np.zeros((H, W, 4), np.float32)
    rgba[..., :3] = light_col
    rgba[..., 3] = alpha * 255 * mask
    crop = rgba[y0:y1, x0:x1]
    Image.fromarray(crop.astype(np.uint8), "RGBA").save(f"{outdir}/{name}.png", optimize=True)
save_light("logo_light_full", np.ones((H, W)))
# mark only, tight crop, light
rgba = np.zeros((H, W, 4), np.float32); rgba[..., :3] = light_col; rgba[..., 3] = alpha * 255 * band_mark
Image.fromarray(rgba[290:690, 195:1115].astype(np.uint8), "RGBA").save(f"{outdir}/mark_light.png", optimize=True)
print("crop", x1 - x0, y1 - y0)
