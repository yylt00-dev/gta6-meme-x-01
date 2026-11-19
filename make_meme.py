#!/usr/bin/env python3
"""Build the gta6-meme-x-01 meme from the generated base art.

Takes base-art.png (an AI-generated GTA 6 launch-week scene with the
make.fun ghost mascot in it, no text), crops off its letterbox bars,
works two small labels into the scene itself ("$100" on the monitor's
price tag, "make.fun" on the laptop screen), then re-frames it as a
classic square meme with crisp caption bars top and bottom so the joke
stays readable when the picture is shrunk to 480x480.

Deterministic: same input, same output. Run: python3 make_meme.py
"""

from PIL import Image, ImageDraw, ImageFont

REPO = __file__.rsplit("/", 1)[0]
BASE = f"{REPO}/base-art.png"
OUT = f"{REPO}/meme.png"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CANVAS = 1024
BAR_BG = (13, 13, 26)          # deep navy, matches the room's night light
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NEON_PINK = (255, 93, 162)     # the price tag's neon outline colour
SCREEN_INK = (4, 51, 58)       # dark teal "UI text" on the laptop screen

TOP_TEXT = "WAITED 13 YEARS FOR GTA 6"
BOTTOM_LINES = ["MY AI AGENT DIDN'T WAIT.", "IT GETS PAID ON make.fun"]


def font(size):
    return ImageFont.truetype(FONT, size)


def fit_font(draw, text, max_width, start):
    """Largest bold font, from `start` down, whose text fits max_width."""
    size = start
    while size > 10:
        f = font(size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 2
    return font(size)


def centred(draw, cx, y, text, f, fill, stroke=0, stroke_fill=BLACK):
    w = draw.textlength(text, font=f)
    draw.text((cx - w / 2, y), text, font=f, fill=fill,
              stroke_width=stroke, stroke_fill=stroke_fill)
    return f.size


def scene_band(img):
    """First/last row that is not the solid letterbox bar colour."""
    px = img.load()
    w, h = img.size
    top_colour = px[4, 4]
    bot_colour = px[4, h - 5]

    def differs(p, c):
        return sum(abs(p[i] - c[i]) for i in range(3)) > 60

    top = 0
    for y in range(h):
        hits = sum(1 for x in range(0, w, 16) if differs(px[x, y], top_colour))
        if hits > (w / 16) * 0.05:
            top = y
            break
    bottom = h
    for y in range(h - 1, -1, -1):
        hits = sum(1 for x in range(0, w, 16) if differs(px[x, y], bot_colour))
        if hits > (w / 16) * 0.05:
            bottom = y + 1
            break
    return top, bottom


def main():
    art = Image.open(BASE).convert("RGB")
    W, H = art.size
    top, bottom = scene_band(art)
    scene = art.crop((0, top, W, bottom))

    # Work the labels into the scene at the spots the art left blank.
    # Fractions are of the ORIGINAL frame; convert into scene coords.
    def scene_xy(fx, fy):
        return fx * W, fy * H - top

    d = ImageDraw.Draw(scene)
    # "$100" inside the neon price tag on the monitor.
    tx, ty = scene_xy(0.328, 0.578)
    f_tag = fit_font(d, "$100", 0.17 * W, int(0.075 * H))
    centred(d, tx, ty - f_tag.size / 2, "$100", f_tag, NEON_PINK)
    # "make.fun" as the UI on the little laptop's screen, tilted with it.
    lx, ly = scene_xy(0.178, 0.706)
    f_lap = fit_font(d, "make.fun", 0.085 * W, int(0.034 * H))
    label = Image.new("RGBA", (int(0.11 * W), int(0.05 * H)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(label)
    lw = ld.textlength("make.fun", font=f_lap)
    ld.text(((label.width - lw) / 2, (label.height - f_lap.size) / 2),
            "make.fun", font=f_lap, fill=SCREEN_INK + (255,))
    label = label.rotate(9, expand=True, resample=Image.BICUBIC)
    scene.paste(label, (int(lx - label.width / 2), int(ly - label.height / 2)),
                label)

    # Re-frame: scene full-width on a square canvas, caption bars around it.
    scene = scene.resize((CANVAS, int(CANVAS * scene.height / scene.width)),
                         Image.LANCZOS)
    canvas = Image.new("RGB", (CANVAS, CANVAS), BAR_BG)
    y0 = (CANVAS - scene.height) // 2
    canvas.paste(scene, (0, y0))
    d = ImageDraw.Draw(canvas)

    # Top caption, centred in the top bar.
    f_top = fit_font(d, TOP_TEXT, CANVAS - 64, 84)
    centred(d, CANVAS / 2, (y0 - f_top.size) / 2 - 6, TOP_TEXT, f_top,
            WHITE, stroke=5)

    # Bottom caption, two lines centred in the bottom bar.
    bar_top = y0 + scene.height
    bar_h = CANVAS - bar_top
    f_bot = fit_font(d, BOTTOM_LINES[0], CANVAS - 64, 66)
    line_h = f_bot.size + 14
    y = bar_top + (bar_h - line_h * len(BOTTOM_LINES)) / 2 - 4
    for line in BOTTOM_LINES:
        centred(d, CANVAS / 2, y, line, f_bot, WHITE, stroke=5)
        y += line_h

    canvas.save(OUT)
    print(f"wrote {OUT} ({canvas.size[0]}x{canvas.size[1]})")


if __name__ == "__main__":
    main()
