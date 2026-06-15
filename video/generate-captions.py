"""Composite verbatim captions onto each frame. Helvetica, semi-transparent box, bottom center. 1920x1080."""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(__file__)
FRAMES, OUT = os.path.join(HERE, "frames"), os.path.join(HERE, "composites")
os.makedirs(OUT, exist_ok=True)

CAPTIONS = {
    "hook": "Paste any smart contract into Sentinel, and seconds later you get this. A security grade.",
    "audit": "It runs two engines at once: Slither for static analysis, and an AI model for the logic bugs static tools miss. Here it caught a critical one — funds the owner could drain.",
    "onchain": "The verdict doesn't sit in a database. It's written to Mantle, hashed so the grade is tamper-proof and anyone can verify it.",
    "registry": "Every contract it has graded lives in one on-chain registry. Pass or fail, A through F, read straight from the chain.",
    "dev": "Each verdict binds to the agent's ERC-8004 identity. One call — isAttestedSafe — lets your contract refuse to trust an agent that never passed.",
    "cta": "Sentinel. The safety layer for on-chain agents.",
}

W = 1920
FONT_SZ = 46
LINE_H = 60
MARGIN = 220   # side margin for text wrapping
PAD = 28


def font(sz):
    for p in ["/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


F = font(FONT_SZ)


def wrap(draw, text, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=F) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


for key, text in CAPTIONS.items():
    src = os.path.join(FRAMES, key + ".png")
    if not os.path.exists(src):
        print("MISSING frame:", key); continue
    img = Image.open(src).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    lines = wrap(d, text, W - 2 * MARGIN)
    th = len(lines) * LINE_H
    box_w = max(d.textlength(ln, font=F) for ln in lines) + 2 * PAD
    box_h = th + 2 * PAD - (LINE_H - FONT_SZ)
    bx0 = (W - box_w) / 2
    by1 = img.size[1] - 70
    by0 = by1 - box_h
    d.rounded_rectangle([bx0, by0, bx0 + box_w, by1], radius=16, fill=(0, 0, 0, 165))
    y = by0 + PAD
    for ln in lines:
        lw = d.textlength(ln, font=F)
        d.text(((W - lw) / 2, y), ln, font=F, fill=(245, 247, 250, 255))
        y += LINE_H
    Image.alpha_composite(img, overlay).convert("RGB").save(os.path.join(OUT, key + ".png"))
    print("composited:", key, f"({len(lines)} lines)")
print("captions done")
