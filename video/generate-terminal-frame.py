"""Generate the on-chain proof frame (clip 3) — a clean dark terminal showing the real attestation
write + a cast read-back. ASCII only (Pillow can't render emojis). 1920x1080."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1920, 1080
BG = (10, 12, 16)
PANEL = (15, 19, 26)
LINE = (30, 36, 46)
MUTED = (152, 162, 176)
TEXT = (238, 241, 246)
MINT = (94, 240, 198)
RED = (240, 103, 107)
GREEN = (87, 198, 148)
FAINT = (95, 104, 120)

OUT = os.path.join(os.path.dirname(__file__), "frames", "03-onchain.png")


def font(sz, bold=False):
    for p in ([
        "/System/Library/Fonts/SFNSMono.ttf",
        "/Library/Fonts/JetBrainsMono-Regular.ttf",
    ] if not bold else []) + [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        "/System/Library/Fonts/Courier.ttc",
    ]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# ambient mint glow top-right
glow = Image.new("RGB", (W, H), BG)
gd = ImageDraw.Draw(glow)
gd.ellipse([W - 700, -300, W + 200, 500], fill=(16, 40, 33))
img = Image.blend(img, glow, 0.5)
d = ImageDraw.Draw(img)

# terminal panel
px, py, pw, ph = 360, 250, 1200, 580
d.rounded_rectangle([px, py, px + pw, py + ph], radius=16, fill=PANEL, outline=LINE, width=1)
# title bar dots
for i, c in enumerate([(240, 103, 107), (232, 179, 65), (87, 198, 148)]):
    d.ellipse([px + 26 + i * 26, py + 24, px + 38 + i * 26, py + 36], fill=c)
d.text((px + 120, py + 22), "sentinel — on-chain attestation", font=font(20), fill=FAINT)
d.line([px, py + 58, px + pw, py + 58], fill=LINE, width=1)

fb = font(26)
x0, y = px + 40, py + 90
lh = 44


def line(segs, yy):
    cx = x0
    for txt, col in segs:
        d.text((cx, yy), txt, font=fb, fill=col)
        cx += d.textlength(txt, font=fb)


line([("$ ", MINT), ("sentinel audit ", TEXT), ("0x469C…dF25 ", MUTED), ("--attest", MINT)], y); y += lh
line([("  VERDICT  ", FAINT), ("FAIL", RED), ("   1 high   grade ", MUTED), ("D", RED)], y); y += lh
line([("  report   ", FAINT), ("0x4b6cbda…  keccak256(report)", MUTED)], y); y += lh
line([("  writing verdict to Mantle Sepolia…", FAINT)], y); y += lh
line([("  registry tx   ", FAINT), ("0x3c5212…  CONFIRMED", GREEN)], y); y += lh
line([("  erc-8004      ", FAINT), ("giveFeedback(agent #186)  CONFIRMED", GREEN)], y); y += int(lh * 1.4)
line([("$ ", MINT), ("cast call ", TEXT), ("0xbCE17E7… ", MUTED), ('"isAttestedSafe(address)"', TEXT)], y); y += lh
line([("  ", FAINT), ("false", RED), ("   # anyone can verify, on-chain", FAINT)], y)

# caption strip handled by the captioner; leave headline here
d.text((px, py - 70), "The verdict is written to the chain.", font=font(40), fill=TEXT)

img.save(OUT)
print("wrote", OUT)
