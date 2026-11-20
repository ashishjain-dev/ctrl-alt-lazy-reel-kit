"""The thirsty crow, painted in the Fish-Scale Folk style (custom element file).

Used from scenes.yaml as  {type: custom, file: crow_scene.py, args: {phase: pebbles, dur: 6}}.
draw(ctx, t, args) is a pure function of t (seconds since the element started).
Phases: arrive (crow flies to the pot), pebbles (drops 4 pebbles, water rises),
drink (crow drinks, happy), fly (crow flies off, pot full).
Everything sits in a framed panel at the top of the frame (y 300..860), above the narrator.
"""
import math

from reelkit.art.folk import INDIGO, INK, LEAF, PAPER, TURM, VERM
from reelkit.art.painter import closed, fill_pattern, tile

PANEL = (90, 300, 990, 860)
CLAY = (176, 92, 52)
WATER = (70, 120, 190)
POT = (640, 760)          # pot centre (x, base y)


def dbl(c, pts, w=6):
    c.line(closed(pts), INK, w)
    c.line(closed(pts), PAPER, w * 0.4)


def shape(ctx, pts, fill, pattern=None, pcol=INK, size=26, w=6):
    ctx.c.poly(pts, fill)
    if pattern:
        fill_pattern(ctx.im, pts, tile(pattern, pcol, None, size, 2.2))
    dbl(ctx.c, pts, w)


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def pot_shape(cx, base):
    """Clay pot: a narrow neck on a round belly (output px)."""
    cy, rx, ry = base - 110, 125, 105
    right = [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in [math.radians(d) for d in range(-60, 61, 10)]]
    left = [(cx - rx * math.cos(a), cy + ry * math.sin(a)) for a in [math.radians(d) for d in range(60, -61, -10)]]
    return ([(cx - 60, base - 250), (cx + 60, base - 250), (cx + 64, base - 215)] + right +
            [(cx + 50, base), (cx - 50, base)] + left + [(cx - 64, base - 215)])


def crow(ctx, x, y, flap, happy=False, beak_down=0.0, face=1):
    c = ctx.c
    f = face
    body = [(x - 70 * f, y + 6), (x - 20 * f, y - 34), (x + 40 * f, y - 30), (x + 62 * f, y), (x + 20 * f, y + 30), (x - 40 * f, y + 26)]
    shape(ctx, body, (36, 34, 40), "scales", (90, 90, 104), 22, 5)
    tail = [(x - 66 * f, y + 4), (x - 120 * f, y - 16), (x - 112 * f, y + 30)]
    shape(ctx, tail, INDIGO, "hatch", PAPER, 14, 4)
    hx, hy = x + 66 * f, y - 30
    c.ell([hx - 30, hy - 28, hx + 30, hy + 28], fill=(36, 34, 40), outline=INK, width=5)
    a = beak_down
    beak = [(hx + 22 * f, hy - 6), (hx + (70 * math.cos(a)) * f, hy + 70 * math.sin(a) + 2), (hx + 22 * f, hy + 10)]
    shape(ctx, beak, TURM, None, INK, 10, 3)
    eye = [(hx - 14, hy - 8), (hx, hy - 16), (hx + 14, hy - 8), (hx, hy)]
    c.poly(eye, PAPER)
    c.line(closed(eye), INK, 2)
    if happy:
        c.arc([hx - 8, hy - 14, hx + 8, hy - 2], 200, 340, INK, 3)
    else:
        c.ell([hx - 4 + 3 * f, hy - 12, hx + 4 + 3 * f, hy - 4], fill=INK)
    wing = [(x - 10 * f, y - 20), (x + 26 * f, y - 22), (x - 30 * f, y - 20 - 70 * flap)]
    shape(ctx, wing, LEAF, "dots", TURM, 12, 4)
    for k in (-1, 1):                         # legs
        c.line([(x + 10 * k, y + 28), (x + 14 * k, y + 52)], INK, 4)


def draw(ctx, t, args):
    c = ctx.c
    phase = args.get("phase", "arrive")
    dur = float(args.get("dur", 6.0))
    u = t / dur
    x0, y0, x1, y1 = PANEL
    # panel: a painting inside the frame
    panel = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    c.poly(panel, (246, 234, 206))
    # sun, tree, ground
    sx, sy = 230, 380
    rays = [(sx + (64 if i % 2 == 0 else 42) * math.cos(i * math.pi / 10 + t * 0.3), sy + (64 if i % 2 == 0 else 42) * math.sin(i * math.pi / 10 + t * 0.3)) for i in range(20)]
    shape(ctx, rays, VERM, None, INK, 10, 4)
    c.ell([sx - 34, sy - 34, sx + 34, sy + 34], fill=TURM, outline=INK, width=4)
    ground = [(x0, 790), (x1, 770), (x1, y1), (x0, y1)]
    shape(ctx, ground, (214, 168, 96), "dots", INK, 22, 5)
    trunk = [(170, 790), (210, 790), (205, 560), (178, 560)]
    shape(ctx, trunk, (120, 70, 40), "hatch", INK, 14, 4)
    for k, (cx, cy, r) in enumerate(((190, 520, 90), (130, 580, 60), (255, 585, 62))):
        leaf = [(cx + r * math.cos(a), cy + r * 0.8 * math.sin(a)) for a in [j * 0.39 for j in range(17)]]
        shape(ctx, leaf, LEAF, "scales", TURM, 22, 5)
    # pot with a window showing the water level
    if phase == "arrive":
        level = 0.18
    elif phase == "pebbles":
        level = 0.18 + 0.6 * ease((u - 0.12) / 0.8)
    else:
        level = 0.8
    if phase == "drink":
        level = 0.8 - 0.25 * ease((u - 0.3) / 0.6)
    pcx, base = POT
    pot = pot_shape(pcx, base)
    shape(ctx, pot, CLAY, "scales", TURM, 26, 6)
    win = [(pcx - 70, base - 200), (pcx + 70, base - 200), (pcx + 70, base - 30), (pcx - 70, base - 30)]
    c.poly(win, (250, 244, 228))
    wy = base - 30 - 170 * level
    water = [(pcx - 70, wy), (pcx + 70, wy), (pcx + 70, base - 30), (pcx - 70, base - 30)]
    c.poly(water, WATER)
    fill_pattern(ctx.im, water, tile("waves", PAPER, None, 26, 2))
    # pebbles already in the pot
    n_in = 0 if phase == "arrive" else (min(4, int((u - 0.12) / 0.2) + 1) if phase == "pebbles" and u > 0.12 else (4 if phase != "pebbles" else 0))
    for k in range(n_in):
        px = pcx - 45 + k * 30
        c.ell([px - 14, base - 54, px + 14, base - 32], fill=(150, 150, 160), outline=INK, width=3)
    dbl(c, win, 4)
    # pebble pile next to the pot
    for k in range(max(0, 4 - n_in)):
        px = 820 + k * 34
        c.ell([px - 16, 760, px + 16, 784], fill=(150, 150, 160), outline=INK, width=3)
    # the crow
    flap = math.sin(t * 16)
    if phase == "arrive":
        e = ease(u / 0.8)
        x = 1040 - 320 * e
        y = 420 + 160 * e + 20 * math.sin(t * 3)
        crow(ctx, x, y, flap if e < 1 else 0.1, face=-1)
    elif phase == "pebbles":
        k = int(u / 0.2)
        local_u = (u % 0.2) / 0.2
        if local_u < 0.5:          # fly to the pile
            x = 760 + 100 * ease(local_u * 2)
            y = 560 + 120 * math.sin(math.pi * local_u * 2)
        else:                      # carry the pebble back and drop it
            x = 860 - 100 * ease((local_u - 0.5) * 2)
            y = 560 + 120 * math.sin(math.pi * (local_u - 0.5) * 2) * 0.4
        crow(ctx, x, y, flap, face=-1)
        if k < 4 and 0.5 < local_u < 0.95:
            c.ell([x - 30 - 12, y + 30 - 10, x - 30 + 12, y + 30 + 10], fill=(150, 150, 160), outline=INK, width=3)
    elif phase == "drink":
        crow(ctx, pcx + 60, base - 290, 0.05, happy=u > 0.6, beak_down=1.0 if u < 0.7 else 0.3, face=-1)
    else:
        e = ease(u / 0.9)
        crow(ctx, pcx + 60 - 400 * e, base - 290 - 110 * e, flap, happy=True, face=-1)
    # frame of the painting
    dbl(c, panel, 8)
    inner = [(x0 + 14, y0 + 14), (x1 - 14, y0 + 14), (x1 - 14, y1 - 14), (x0 + 14, y1 - 14)]
    c.line(closed(inner), INK, 2)
    _ = VERM
