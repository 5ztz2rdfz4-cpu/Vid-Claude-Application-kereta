"""Cut the Bezza press photo out of its light studio background -> assets/img/bezza_cut.png"""
import sys, numpy as np
from PIL import Image, ImageFilter
from collections import deque
src, out, prev = sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None
im = Image.open(src).convert('RGB')
im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
A = np.asarray(im).astype(np.float32); H, W, _ = A.shape
lum = A.mean(2); sat = A.max(2) - A.min(2)
cand = (lum > 196) & (sat < 22)
bg = np.zeros((H, W), bool); q = deque()
for y in range(H):
    for x in range(W):
        if (y in (0, H - 1) or x in (0, W - 1)) and cand[y, x]: bg[y, x] = True; q.append((y, x))
while q:
    y, x = q.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < H and 0 <= nx < W and cand[ny, nx] and not bg[ny, nx]:
            bg[ny, nx] = True; q.append((ny, nx))
yy = np.arange(H)[:, None]
low = yy > H * 0.70
# below the sills: light floor between the wheels is background too; grey floor = shadow
floor = low & (sat < 18) & (lum > 120)
# relaxed flood fill through the floor, seeded from known background (tyres stay dark, so rims survive)
q = deque(zip(*np.where(bg & low)))
while q:
    y, x = q.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < H and 0 <= nx < W and floor[ny, nx] and not bg[ny, nx]:
            bg[ny, nx] = True; q.append((ny, nx))
car = ~bg
a = np.asarray(Image.fromarray((car * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
sh = low & bg & (lum < 232)
sh_a = np.clip((232 - lum) / 60, 0, 0.6) * sh
a2 = np.maximum(a, sh_a)
rgb = np.where((sh & (a < 0.5))[..., None], 0, A)
o = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a2 * 255]).astype(np.uint8))
o = o.crop(o.getchannel('A').point(lambda v: 255 if v > 10 else 0).getbbox())
o.save(out); print(o.size)
if prev:
    b = Image.new('RGBA', o.size, (14, 15, 19, 255)); b.alpha_composite(o); b.convert('RGB').save(prev)
