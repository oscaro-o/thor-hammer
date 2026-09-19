#!/usr/bin/env python3
"""
Render og.png (1200x630) for the social preview.

This is the *offline* path. The primary path is og.html — open it in a browser
and click the button. This script exists so the image can be regenerated in CI
or from a terminal without a browser.

    pip install pillow
    python tools/make-og.py

Fonts: Georgia + Microsoft YaHei on Windows. On macOS/Linux it falls back to
whatever serif/sans it can find, so the result may differ slightly.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H, PAD = 1200, 630, 72
PAPER, INK, INK2, LINE, ACCENT, MUTED = (
    "#f7f4ef", "#191713", "#4c463d", "#e2dbcf", "#a8542a", "#4a443a"
)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.pardir, "og.png")

FONT_DIRS = ["C:/Windows/Fonts", "/System/Library/Fonts", "/usr/share/fonts/truetype"]
SERIF = ["georgia.ttf", "DejaVuSerif.ttf", "Times New Roman.ttf"]
SERIF_B = ["georgiab.ttf", "DejaVuSerif-Bold.ttf", "Times New Roman Bold.ttf"]
SANS_B = ["segoeuib.ttf", "msyhbd.ttc", "DejaVuSans-Bold.ttf", "Arial Bold.ttf"]


def find(names):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    raise SystemExit("no usable font found — edit FONT_DIRS in this script")


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.truetype(path, size, index=0)


def tracked(draw, text, xy, fnt, spacing, fill):
    """draw text with manual letter-spacing"""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill, anchor="ls")
        x += draw.textlength(ch, font=fnt) + spacing
    return x


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and draw.textlength(trial, font=fnt) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

f_kick = font(find(SANS_B), 24)
f_title = font(find(SERIF_B), 76)
f_sub = font(find(SERIF), 33)
f_q = font(find(SERIF), 34)

# inset hairline border
d.rectangle([16, 16, W - 17, H - 17], outline=LINE, width=2)

# hammer mark, top right — head on the left, handle out to the right,
# handle vertically centred on the head
mx, my = W - PAD - 96, 58
d.rectangle([mx, my, mx + 34, my + 42], fill=INK)          # head
d.rectangle([mx, my, mx + 11, my + 42], fill=ACCENT)       # head, leading face
d.rectangle([mx + 14, my + 15, mx + 92, my + 27], fill=MUTED)  # handle

# kicker
tracked(d, "A SHORT GAME ABOUT THE PRICE OF SKILL", (PAD, 88), f_kick, 3.6, ACCENT)

# rule
d.line([(PAD, 126), (W - PAD, 126)], fill=LINE, width=2)

# title — shrink until it fits the column (Georgia Bold is wider than it looks)
TITLE = "Everyone Got Thor's Hammer"
t_size = 76
while t_size > 40:
    f_title = font(find(SERIF_B), t_size)
    if d.textlength(TITLE, font=f_title) <= W - PAD * 2:
        break
    t_size -= 2

d.text((PAD, 244), TITLE, font=f_title, fill=INK, anchor="ls")
d.text((PAD, 312), "One morning, everyone on earth woke up holding it.",
       font=f_sub, fill=INK2, anchor="ls")

# question block, anchored to the bottom
QUESTION = "So: what is your hammer \u2014 and what does only your eye know?"
q_pad, q_lh = 46, 52
q_lines = wrap(d, QUESTION, f_q, W - PAD * 2 - q_pad * 2)
block_h = q_pad * 2 + len(q_lines) * q_lh - 14
block_bottom = H - 68
block_top = block_bottom - block_h

d.rounded_rectangle([PAD, block_top, W - PAD, block_bottom], radius=6, fill=INK)
for i, ln in enumerate(q_lines):
    d.text((PAD + q_pad, block_top + q_pad + 32 + i * q_lh), ln,
           font=f_q, fill="#f2ece2", anchor="ls")

img.save(OUT, "PNG", optimize=True)
print(f"wrote {os.path.relpath(OUT)}  {W}x{H}  {os.path.getsize(OUT):,} bytes")
