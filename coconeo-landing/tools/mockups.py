"""Generate product mockups for the Coco Neo landing page from the bottle cutout.

Run from the coconeo-landing folder:  python3 tools/mockups.py
Outputs go to assets/img/mockups/ as .webp (web) files.
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

random.seed(7)
OUT = "assets/img/mockups/"
BOTTLE = Image.open("assets/img/bottle-cutout.png").convert("RGBA")

# Brand palette (sampled from the Coco Neo label)
ESPRESSO = (26, 13, 6)
BROWN = (84, 48, 24)
GREEN = (61, 122, 38)
LEAF = (93, 163, 53)
CREAM = (250, 245, 228)
OIL = (223, 215, 136)
GOLD = (196, 155, 62)
WHITE = (255, 255, 255)

F = "/usr/share/fonts/opentype/inter/"
def font(weight, size):
    return ImageFont.truetype(F + {"black": "Inter-Black.otf", "bold": "Inter-Bold.otf",
                                    "semi": "Inter-SemiBold.otf", "reg": "Inter-Regular.otf"}[weight], size)


def gradient(size, top, bottom):
    w, h = size
    t = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(top)[None, None, :] * (1 - t) + np.array(bottom)[None, None, :] * t)
    arr = np.repeat(arr, w, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def radial_glow(canvas, center, radius, color, strength=0.55):
    w, h = canvas.size
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt((xx - center[0]) ** 2 + (yy - center[1]) ** 2) / radius
    a = np.clip(1 - d, 0, 1) ** 2 * 255 * strength
    layer = Image.new("RGBA", (w, h), color + (0,))
    layer.putalpha(Image.fromarray(a.astype(np.uint8)))
    canvas.alpha_composite(layer)


def grain(canvas, amount=6):
    w, h = canvas.size
    n = np.random.default_rng(3).normal(0, amount, (h, w, 1))
    arr = np.array(canvas).astype(np.int16)
    arr[..., :3] = np.clip(arr[..., :3] + n, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def bottle(height):
    r = height / BOTTLE.height
    return BOTTLE.resize((int(BOTTLE.width * r), height), Image.LANCZOS)


def place_bottle(canvas, b, x, floor_y, shadow=True, reflect=0.0):
    """Paste bottle with its base on floor_y, a soft contact shadow and optional reflection."""
    if shadow:
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(sh)
        cx = x + b.width // 2
        d.ellipse([cx - b.width * 0.62, floor_y - 14, cx + b.width * 0.62, floor_y + 16], fill=(40, 20, 5, 120))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    if reflect:
        rf = b.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, b.width, int(b.height * 0.35)))
        a = np.array(rf.split()[3]).astype(np.float32)
        fade = np.linspace(reflect, 0, rf.height)[:, None]
        rf.putalpha(Image.fromarray((a * fade).astype(np.uint8)))
        canvas.alpha_composite(rf, (x, floor_y))
    canvas.alpha_composite(b, (x, floor_y - b.height))


def coconut_half(size, rot=0):
    """Draw a split coconut half (fibrous shell + white meat) on its own layer."""
    s = size
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, s - 1, s - 1], fill=(92, 52, 26))
    for _ in range(int(s * 1.4)):  # fibres
        a = random.uniform(0, 2 * math.pi)
        r1 = random.uniform(0.40, 0.5) * s
        x1, y1 = s / 2 + math.cos(a) * r1, s / 2 + math.sin(a) * r1
        x2, y2 = x1 + random.uniform(-6, 6), y1 + random.uniform(-6, 6)
        d.line([x1, y1, x2, y2], fill=random.choice([(120, 72, 38), (70, 38, 18), (140, 90, 50)]), width=2)
    m = s * 0.09
    d.ellipse([m, m, s - m, s - m], fill=(250, 248, 240))
    m2 = s * 0.2
    d.ellipse([m2, m2, s - m2, s - m2], fill=(236, 232, 218))
    hl = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse([s * 0.22, s * 0.18, s * 0.55, s * 0.42], fill=(255, 255, 255, 120))
    im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(s * 0.05)))
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)


def whole_coconut(size):
    s = size
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, s * 0.05, s - 1, s - 1], fill=(104, 62, 32))
    for _ in range(int(s * 3)):
        x, y = random.uniform(s * .1, s * .9), random.uniform(s * .15, s * .9)
        if (x - s / 2) ** 2 + (y - s * .52) ** 2 < (s * .44) ** 2:
            d.line([x, y, x + random.uniform(-9, 9), y + random.uniform(-3, 9)],
                   fill=random.choice([(130, 82, 44), (78, 44, 20), (150, 100, 58)]), width=2)
    for cx in (0.4, 0.5, 0.6):  # the three "eyes"
        d.ellipse([s * cx - s * .03, s * .2, s * cx + s * .03, s * .26], fill=(40, 20, 8))
    return im


def leaf(length, angle, color=LEAF):
    """A stylised palm frond: a spine with tapered leaflets."""
    L = length
    im = Image.new("RGBA", (L * 2, L * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = L, L
    for i in range(0, 26):
        t = i / 26
        px, py = cx + t * L * 0.95, cy - math.sin(t * math.pi * 0.6) * L * 0.18
        ll = L * 0.28 * math.sin(math.pi * min(1, t * 1.15)) + 6
        for side in (-1, 1):
            ex = px + ll * 0.45
            ey = py + side * ll
            d.polygon([(px, py), (ex, ey), (px + 9, py)], fill=color + (235,))
    d.line([(cx, cy)] + [(cx + t / 20 * L * 0.95, cy - math.sin(t / 20 * math.pi * 0.6) * L * 0.18) for t in range(21)],
           fill=(50, 95, 30, 255), width=4)
    return im.rotate(angle, expand=False, resample=Image.BICUBIC)


def pill(d, xy, text, fnt, fill, color):
    x, y = xy
    tw = d.textlength(text, font=fnt)
    h = fnt.size + 22
    d.rounded_rectangle([x, y, x + tw + 40, y + h], radius=h // 2, fill=fill)
    d.text((x + 20, y + 10), text, font=fnt, fill=color)
    return tw + 40


def save(img, name, size=None):
    img = grain(img, 3)
    if size:
        img = img.resize(size, Image.LANCZOS)
    img.convert("RGB").save(OUT + name, "WEBP", quality=86, method=6)
    print("wrote", name, img.size)


# 1. HERO — bottle on cream with coconuts and palm fronds --------------------
def hero():
    W = H = 1400
    c = gradient((W, H), (253, 249, 236), (240, 228, 196))
    radial_glow(c, (W // 2, H * 0.42), 620, (255, 236, 160), 0.7)
    for (x, y, L, a) in [(-180, -120, 620, -25), (760, -200, 640, 200), (-240, 760, 560, 20)]:
        lf = leaf(L, a)
        c.alpha_composite(lf.filter(ImageFilter.GaussianBlur(1)), (x, y))
    floor = int(H * 0.86)
    d = ImageDraw.Draw(c)
    d.ellipse([W * 0.12, floor - 30, W * 0.88, floor + 60], fill=(232, 216, 178, 255))
    c = c.filter(ImageFilter.GaussianBlur(0.5))
    place_bottle(c, bottle(1060), W // 2 - bottle(1060).width // 2, floor)
    for (sz, x, rot) in [(300, 830, 18), (250, 270, -30)]:
        ch = coconut_half(sz, rot)
        sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([x, floor - 24, x + ch.width, floor + 22], fill=(40, 20, 5, 110))
        c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
        c.alpha_composite(ch, (x, floor - ch.height + 30))
    wc = whole_coconut(230)
    c.alpha_composite(wc, (160, floor - 210))
    save(c, "hero.webp", (1200, 1200))


# 2. LIFESTYLE — wooden kitchen counter, bowl of oil --------------------------
def lifestyle():
    W = H = 1400
    c = gradient((W, H), (238, 228, 205), (214, 197, 160))  # wall
    radial_glow(c, (W * 0.3, H * 0.25), 700, (255, 245, 210), 0.8)
    # window light bars
    lt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lt)
    for i in range(4):
        ld.polygon([(120 + i * 170, 0), (220 + i * 170, 0), (520 + i * 170, 900), (420 + i * 170, 900)], fill=(255, 250, 225, 40))
    c.alpha_composite(lt.filter(ImageFilter.GaussianBlur(30)))
    # wooden counter
    top = int(H * 0.68)
    wood = np.zeros((H - top, W, 3), np.float32)
    yy, xx = np.mgrid[0:H - top, 0:W]
    grainline = np.sin(xx / 38 + np.sin(yy / 23) * 2.2) * 0.5 + np.sin(xx / 7 + yy / 50) * 0.2
    base = np.array([150, 98, 58], np.float32)
    wood = base + grainline[..., None] * 16 - (yy[..., None] / (H - top)) * 30
    wood_img = Image.fromarray(np.clip(wood, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    c.alpha_composite(wood_img, (0, top))
    d = ImageDraw.Draw(c)
    d.rectangle([0, top, W, top + 6], fill=(110, 70, 40, 255))
    floor = top + 220
    # small wooden bowl of oil
    bowl = Image.new("RGBA", (360, 170), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bowl)
    bd.pieslice([0, -150, 360, 170], 0, 180, fill=(120, 74, 40))
    bd.ellipse([10, 0, 350, 60], fill=(95, 58, 30))
    bd.ellipse([24, 8, 336, 54], fill=(232, 212, 120))
    bd.ellipse([80, 16, 190, 34], fill=(255, 246, 200))
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([780, floor - 20, 1140, floor + 24], fill=(40, 20, 5, 120))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    c.alpha_composite(bowl, (780, floor - 165))
    b = bottle(980)
    place_bottle(c, b, 360, floor, reflect=0.18)
    c.alpha_composite(coconut_half(230, 40), (1010, floor - 330))
    c.alpha_composite(leaf(420, 160, (78, 140, 46)), (820, -120))
    # curry leaves sprig
    for i in range(7):
        x, y = 160 + i * 34, floor - 40 + (i % 2) * 18
        d.ellipse([x, y, x + 46, y + 20], fill=(58, 112, 40, 255))
    save(c, "lifestyle.webp", (1200, 1200))


# 3/4. COMBO PACKS -------------------------------------------------------------
def combo(n, name, tag):
    W = H = 1400
    c = gradient((W, H), (246, 240, 224), (229, 214, 178))
    radial_glow(c, (W // 2, H * 0.45), 680, (255, 238, 170), 0.6)
    floor = int(H * 0.88)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([W * 0.08, floor - 40, W * 0.92, floor + 30], 40, fill=(222, 204, 160, 255))
    hts = {2: [920, 920], 3: [820, 900, 820]}[n]
    bs = [bottle(h) for h in hts]
    gap = -40 if n == 3 else 30
    total = sum(b.width for b in bs) + gap * (n - 1)
    x = W // 2 - total // 2
    order = list(range(n)) if n == 2 else [0, 2, 1]
    xs = []
    for b in bs:
        xs.append(x); x += b.width + gap
    for i in order:
        place_bottle(c, bs[i], xs[i], floor)
    # badge
    d = ImageDraw.Draw(c)
    d.ellipse([1040, 90, 1320, 370], fill=GREEN + (255,))
    d.ellipse([1056, 106, 1304, 354], outline=(255, 255, 255, 180), width=3)
    f1, f2 = font("black", 70), font("bold", 30)
    t = f"PACK OF {n}"
    d.text((1180, 200), f"{n} L", font=f1, fill=WHITE, anchor="mm")
    d.text((1180, 262), tag, font=f2, fill=WHITE, anchor="mm")
    d.text((110, 110), t, font=font("black", 64), fill=ESPRESSO)
    d.text((112, 188), "Family value combo", font=font("semi", 34), fill=BROWN)
    save(c, name, (1200, 1200))


# 5. INFOGRAPHIC — benefits callouts around the bottle ------------------------
def infographic():
    W = H = 1400
    c = gradient((W, H), (24, 52, 18), (14, 32, 10))
    radial_glow(c, (W // 2, H * 0.52), 640, (120, 170, 60), 0.35)
    floor = int(H * 0.93)
    b = bottle(1080)
    place_bottle(c, b, W // 2 - b.width // 2, floor)
    d = ImageDraw.Draw(c)
    d.text((W // 2, 70), "WHAT'S INSIDE EVERY BOTTLE", font=font("black", 50), fill=CREAM, anchor="mm")
    d.text((W // 2, 126), "Pure. Natural. Made in Kerala.", font=font("semi", 30), fill=OIL, anchor="mm")
    calls = [
        ("100% Pure", "Single-ingredient\ncoconut oil", (90, 300), "L"),
        ("0 mg", "Cholesterol\nper 100 g", (90, 640), "L"),
        ("No", "Preservatives\nadded", (90, 980), "L"),
        ("ISO", "22000:2018\ncertified unit", (1310, 300), "R"),
        ("FSSAI", "Licensed\nmanufacturer", (1310, 640), "R"),
        ("Kerala", "Coconuts from\nGod's own country", (1310, 980), "R"),
    ]
    for big, small, (x, y), side in calls:
        anchor = "la" if side == "L" else "ra"
        d.text((x, y), big, font=font("black", 62), fill=OIL, anchor=anchor)
        d.multiline_text((x, y + 80), small, font=font("semi", 30), fill=CREAM, anchor=anchor,
                         align="left" if side == "L" else "right", spacing=8)
        lx0 = x + 340 if side == "L" else x - 340
        lx1 = W // 2 - 150 if side == "L" else W // 2 + 150
        d.line([(lx0, y + 40), (lx1, y + 40)], fill=(223, 215, 136, 150), width=3)
        d.ellipse([lx1 - 9, y + 31, lx1 + 9, y + 49], fill=OIL)
    save(c, "infographic.webp", (1200, 1200))


# 6. LABEL CLOSE-UP — the trust facts on the pack -----------------------------
def label_closeup():
    src = Image.open("assets/img/source-bottle.webp").convert("RGBA")
    crop = src.crop((395, 470, 605, 890)).resize((630, 1260), Image.LANCZOS)
    W, H = 1400, 1400
    c = gradient((W, H), (250, 246, 232), (236, 226, 198))
    card = Image.new("RGBA", (crop.width + 40, crop.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle([0, 0, card.width - 1, card.height - 1], 28, fill=(255, 255, 255, 255))
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([90, 90, 90 + card.width, 90 + card.height], 28, fill=(60, 30, 10, 70))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)), (8, 18))
    c.alpha_composite(card, (90, 70))
    c.alpha_composite(crop, (110, 90))
    d = ImageDraw.Draw(c)
    x = 830
    d.text((x, 160), "Read the", font=font("semi", 44), fill=BROWN)
    d.text((x, 214), "label.", font=font("black", 96), fill=ESPRESSO)
    d.text((x, 330), "Nothing to hide.", font=font("semi", 40), fill=GREEN)
    y = 450
    for t in ["0 mg cholesterol", "No preservatives", "ISO 22000:2018", "FSSAI licensed", "Made in Kerala"]:
        d.ellipse([x, y + 8, x + 30, y + 38], fill=GREEN + (255,))
        d.line([(x + 8, y + 23), (x + 14, y + 30), (x + 23, y + 15)], fill=WHITE, width=4)
        d.text((x + 50, y), t, font=font("semi", 36), fill=ESPRESSO)
        y += 76
    save(c, "label-closeup.webp", (1200, 1200))


# 7. SOCIAL / OG image (1200x630) ---------------------------------------------
def og():
    W, H = 1200, 630
    c = gradient((W, H), (253, 249, 236), (238, 224, 188))
    radial_glow(c, (880, 320), 420, (255, 236, 160), 0.7)
    b = bottle(590)
    place_bottle(c, b, 880 - b.width // 2, 615)
    c.alpha_composite(coconut_half(170, 20), (980, 440))
    d = ImageDraw.Draw(c)
    d.text((70, 150), "COCO", font=font("black", 80), fill=ESPRESSO)
    d.text((70, 235), "NEO", font=font("black", 150), fill=ESPRESSO)
    d.text((74, 410), "Cold pressed coconut oil", font=font("semi", 38), fill=BROWN)
    pill(d, (74, 480), "100% pure · Made in Kerala", font("bold", 28), GREEN + (255,), WHITE)
    save(c, "og-image.webp")


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    combo(2, "combo-2.webp", "2 BOTTLES"); combo(3, "combo-3.webp", "3 BOTTLES")
    infographic(); label_closeup(); og()
