"""Cut the product bottle out of its white studio background -> transparent PNG."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
src = Image.open("assets/img/source-bottle.webp").convert("RGB")
w, h = src.size
mask_img = src.copy()
# flood-fill the background from the edges with a magenta key
for seed in [(0,0),(w-1,0),(0,h-1),(w-1,h-1),(w//2,0),(w//2,h-1),(0,h//2),(w-1,h//2),(150,500),(850,500)]:
    ImageDraw.floodfill(mask_img, seed, (255,0,255), thresh=22)
a = np.array(mask_img)
bg = (a[...,0]==255)&(a[...,1]==0)&(a[...,2]==255)
alpha = np.where(bg, 0, 255).astype(np.uint8)
alpha_img = Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
out = src.convert("RGBA"); out.putalpha(alpha_img)
bbox = out.getbbox(); out = out.crop(bbox)
out.save("assets/img/bottle-cutout.png")
print("bbox", bbox, out.size)
