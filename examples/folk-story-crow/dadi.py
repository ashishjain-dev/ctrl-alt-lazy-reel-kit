"""Dadi: a grandmother storyteller painted in the Fish-Scale Folk style (custom character file).

Used from scenes.yaml as   characters: {dadi: {file: dadi.py}}   and then like any character
(cast, dialogue, moods, lip sync). Signature: draw(c, x, y, s, mood, t, talk, opts).
(x, y) = bottom centre (feet), s = scale, talk = mouth opening 0..1.
Options (opts): sari, sari2, blouse, skin, hair - colours as "#rrggbb".
"""
import math

from reelkit.art.folk import INDIGO, INK, LEAF, PAPER, TURM, VERM
from reelkit.art.painter import closed, fill_pattern, tile
from reelkit.brand import hex2rgb


def _col(opts, key, default):
    return hex2rgb(opts[key]) if key in opts else default


def draw(c, x, y, s, mood="neutral", t=0.0, talk=0.0, opts=None):
    opts = opts or {}
    sari = _col(opts, "sari", VERM)
    sari2 = _col(opts, "sari2", TURM)
    blouse = _col(opts, "blouse", INDIGO)
    skin = _col(opts, "skin", (198, 140, 100))
    hair = _col(opts, "hair", (222, 216, 204))
    S = lambda v: v * s  # noqa: E731
    sway = math.sin(t * 1.6) * S(4)
    y = y + math.sin(t * 2.0) * S(3)

    def P(px, py):
        return (x + S(px) + sway * (1 - py / 700), y - S(py))

    def dbl(pts, w=6):
        c.line(closed(pts), INK, S(w))
        c.line(closed(pts), PAPER, S(w) * 0.4)

    def shape(pts, fill, pattern=None, pcol=INK, size=26, w=6):
        c.poly(pts, fill)
        if pattern:
            fill_pattern(c.im, pts, tile(pattern, pcol, None, max(8, int(size * s * 1.6)), 2))
        dbl(pts, w)

    # sari skirt with a patterned border
    skirt = [P(-140, 0), P(140, 0), P(92, 300), P(-92, 300)]
    shape(skirt, sari, "scales", sari2, 30)
    band = [P(-140, 0), P(140, 0), P(134, 34), P(-134, 34)]
    shape(band, sari2, "dots", INK, 16, 4)
    # blouse / torso
    torso = [P(-92, 296), P(92, 296), P(84, 430), P(-84, 430)]
    shape(torso, blouse, "dots", PAPER, 20)
    # arms (one hand to the chin when thinking, both open when shocked or happy)
    up = {"shocked": 70, "happy": 40}.get(mood, 0)
    for side in (-1, 1):
        sh = P(side * 88, 420)
        if mood == "think" and side > 0:
            hand = P(36, 470)
        else:
            hand = P(side * (120 + up * 0.4), 300 + up)
        c.line([sh, hand], INK, S(30))
        c.line([sh, hand], skin, S(22))
        c.ell([hand[0] - S(16), hand[1] - S(16), hand[0] + S(16), hand[1] + S(16)], fill=skin, outline=INK, width=S(4))
        for k in range(3):   # bangles
            bx = sh[0] + (hand[0] - sh[0]) * (0.7 + k * 0.06)
            by = sh[1] + (hand[1] - sh[1]) * (0.7 + k * 0.06)
            c.ell([bx - S(9), by - S(9), bx + S(9), by + S(9)], outline=TURM if k % 2 else LEAF, width=S(4))
    # pallu: the sari end draped over the left shoulder
    pallu = [P(-96, 440), P(-40, 450), P(70, 300), P(20, 290)]
    shape(pallu, sari, "hatch", sari2, 18, 5)
    # neck + head
    neck = [P(-22, 430), P(22, 430), P(20, 470), P(-20, 470)]
    c.poly(neck, skin)
    hx, hy = P(0, 560)
    r = S(96)
    c.ell([hx - r - S(20), hy - r - S(10), hx + r + S(20), hy + r * 0.2], fill=hair)              # hair behind
    bx, by = P(0, 680)
    c.ell([bx - S(44), by - S(40), bx + S(44), by + S(40)], fill=hair, outline=INK, width=S(5))    # bun
    c.ell([hx - r, hy - r, hx + r, hy + r], fill=skin)
    c.ell([hx - r, hy - r, hx + r, hy + r], outline=INK, width=S(6))
    c.ell([hx - r + S(6), hy - r + S(6), hx + r - S(6), hy + r - S(6)], outline=PAPER, width=S(2.4))
    cap = [P(-98, 560), P(-80, 620), P(0, 652), P(80, 620), P(98, 560), P(60, 590), P(0, 600), P(-60, 590)]
    shape(cap, hair, "waves", INK, 22, 4)
    # earrings + bindi
    for side in (-1, 1):
        ex, ey = P(side * 96, 520)
        c.ell([ex - S(10), ey - S(10), ex + S(10), ey + S(10)], fill=TURM, outline=INK, width=S(3))
    bx, by = P(0, 598)
    c.ell([bx - S(8), by - S(8), bx + S(8), by + S(8)], fill=VERM)
    # almond fish eyes behind round glasses
    blink = 0.15 if (t % 4.1) < 0.12 else 1.0
    for side in (-1, 1):
        ex, ey = P(side * 38, 568)
        if mood in ("happy", "smug"):
            c.arc([ex - S(20), ey - S(10), ex + S(20), ey + S(16)], 200, 340, INK, S(5))
        else:
            big = 1.3 if mood == "shocked" else 1.0
            eye = [(ex - S(22) * big, ey), (ex, ey - S(12) * big * blink), (ex + S(22) * big, ey), (ex, ey + S(10) * big * blink)]
            c.poly(eye, PAPER)
            c.line(closed(eye), INK, S(3))
            px = ex + (S(6) if mood == "think" else 0)
            c.ell([px - S(6), ey - S(6) * blink, px + S(6), ey + S(6) * blink], fill=INK)
        c.ell([ex - S(30), ey - S(28), ex + S(30), ey + S(28)], outline=INK, width=S(4))
        if mood == "sad":
            c.line([(ex - side * S(22), ey - S(30)), (ex + side * S(14), ey - S(40))], INK, S(4))
    gx0, gy = P(-8, 570)
    gx1, _ = P(8, 570)
    c.line([(gx0, gy), (gx1, gy)], INK, S(4))
    nx, ny = P(0, 545)
    c.line([(nx, ny - S(14)), (nx + S(6), ny), (nx - S(2), ny + S(4))], INK, S(3))
    # mouth: lip sync while talking, otherwise by mood
    mx, my = P(0, 510)
    if talk > 0.05:
        h = S(6 + 26 * talk)
        mouth = [(mx - S(20), my), (mx, my - h * 0.4), (mx + S(20), my), (mx, my + h)]
        c.poly(mouth, (120, 30, 36))
        c.line(closed(mouth), INK, S(3))
    elif mood in ("happy", "smug"):
        c.arc([mx - S(22), my - S(18), mx + S(22), my + S(12)], 20, 160, INK, S(5))
    elif mood == "shocked":
        c.ell([mx - S(11), my - S(8), mx + S(11), my + S(16)], fill=(120, 30, 36), outline=INK, width=S(3))
    elif mood == "sad":
        c.arc([mx - S(18), my, mx + S(18), my + S(20)], 200, 340, INK, S(4))
    else:
        c.line([(mx - S(14), my + S(2)), (mx + S(14), my + S(2))], INK, S(4))
    # necklace
    for k in range(9):
        a = math.pi * (0.15 + 0.7 * k / 8)
        px, py = hx + math.cos(a) * S(70), hy + r + S(14) + math.sin(a) * S(22)
        c.ell([px - S(6), py - S(6), px + S(6), py + S(6)], fill=TURM if k % 2 else VERM, outline=INK, width=S(2))
