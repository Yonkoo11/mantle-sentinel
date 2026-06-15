"""CTA end card (clip 6) — branded close. 1920x1080."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1920, 1080
BG = (10, 12, 16)
TEXT = (238, 241, 246)
MUTED = (152, 162, 176)
MINT = (94, 240, 198)
OUT = os.path.join(os.path.dirname(__file__), "frames", "cta.png")


def f(sz, mono=False):
    cands = (["/System/Library/Fonts/SFNSMono.ttf", "/System/Library/Fonts/Menlo.ttc"] if mono
             else ["/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf"])
    for p in cands:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), BG)
# ambient mint glow center-top
glow = Image.new("RGB", (W, H), BG)
gd = ImageDraw.Draw(glow)
gd.ellipse([W // 2 - 520, -260, W // 2 + 520, 520], fill=(16, 44, 36))
img = Image.blend(img, glow, 0.55)
d = ImageDraw.Draw(img)

# shield mark
cx = W // 2
sx, sy, ss = cx - 30, 360, 60
d.polygon([(sx + ss / 2, sy), (sx + ss, sy + ss * 0.28), (sx + ss, sy + ss * 0.62),
           (sx + ss / 2, sy + ss), (sx, sy + ss * 0.62), (sx, sy + ss * 0.28)], fill=MINT)
d.line([(sx + ss * 0.32, sy + ss * 0.52), (sx + ss * 0.46, sy + ss * 0.66), (sx + ss * 0.72, sy + ss * 0.34)],
       fill=(6, 23, 18), width=5, joint="curve")


def center(txt, y, font, fill):
    w = d.textlength(txt, font=font)
    d.text((cx - w / 2, y), txt, font=font, fill=fill)


center("Sentinel", 470, f(96), TEXT)
center("The safety layer for on-chain agents.", 600, f(40), MUTED)
center("yonkoo11.github.io/mantle-sentinel", 720, f(34, mono=True), MINT)

img.save(OUT)
print("wrote", OUT)
