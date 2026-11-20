"""The thirsty crow, painted in the Fish-Scale Folk style (custom element file, full screen).

Used from scenes.yaml as  {type: custom, file: crow_scene.py, args: {phase: pebbles, dur: 6.5}}.
draw(ctx, t, args) is a pure function of t (seconds since the element started).

The story world is drawn once in world coordinates (a 1080 x 1920 frame: sky, sun, tree, village, ground,
pot) and each story beat looks at it through its own camera, so the background follows the script:
  arrive   wide shot, heat haze, the crow flies in            (camera: whole frame)
  pebbles  closer on the pot, the crow drops 4 pebbles, water rises
  drink    close-up on the pot, the crow drinks
  fly      wide again, the crow flies off towards the sun
Leave the bottom-right corner (x > 760, y 950..1250) free for the narrator.
"""
import math

from reelkit.art.folk import INDIGO, INK, LEAF, PAPER, PINK, TURM, VERM
from reelkit.art.painter import closed, fill_pattern, tile

CLAY = (176, 92, 52)
WATER = (70, 120, 190)
STONE = (150, 150, 160)
GROUND_Y = 1080
POT = (500, 1190)                     # pot centre x, base y (world)
PILE = (690, 1190)
CAMERAS = {                            # zoom, world point placed at the frame centre (540, 960)
    "arrive": (1.0, 540, 960),
    "pebbles": (1.3, 600, 1010),
    "drink": (1.75, 560, 970),
    "fly": (1.0, 540, 960),
}


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


class Cam:
    """World -> screen transform for one shot; every drawing call goes through it."""

    def __init__(self, ctx, zoom, cx, cy):
        self.ctx, self.c, self.z, self.cx, self.cy = ctx, ctx.c, zoom, cx, cy

    def p(self, x, y):
        return 540 + (x - self.cx) * self.z, 960 + (y - self.cy) * self.z

    def pts(self, pts):
        return [self.p(x, y) for x, y in pts]

    def dbl(self, sp, w=6):
        self.c.line(closed(sp), INK, w * self.z)
        self.c.line(closed(sp), PAPER, w * self.z * 0.4)

    def poly(self, pts, fill, pattern=None, pcol=INK, size=26, w=6, outline=True):
        sp = self.pts(pts)
        self.c.poly(sp, fill)
        if pattern:
            fill_pattern(self.ctx.im, sp, tile(pattern, pcol, None, max(8, int(size * self.z)), 2.2))
        if outline:
            self.dbl(sp, w)

    def line(self, pts, col, w):
        self.c.line(self.pts(pts), col, w * self.z)

    def ell(self, x, y, rx, ry, fill, w=3):
        (a, b), (c2, d) = self.p(x - rx, y - ry), self.p(x + rx, y + ry)
        self.c.ell([a, b, c2, d], fill=fill, outline=INK, width=w * self.z)


def blob(x, y, rx, ry, n=18):
    return [(x + rx * math.cos(2 * math.pi * i / n), y + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def pot_shape(cx, base, k=1.25):
    """Clay pot: a narrow neck on a round belly."""
    cy, rx, ry = base - 110 * k, 125 * k, 105 * k
    right = [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in [math.radians(d) for d in range(-60, 61, 10)]]
    left = [(cx - rx * math.cos(a), cy + ry * math.sin(a)) for a in [math.radians(d) for d in range(60, -61, -10)]]
    return ([(cx - 60 * k, base - 250 * k), (cx + 60 * k, base - 250 * k), (cx + 64 * k, base - 215 * k)] + right +
            [(cx + 50 * k, base), (cx - 50 * k, base)] + left + [(cx - 64 * k, base - 215 * k)])


def world(cam, t, phase, level, pebbles_in):
    """Everything except the crow, in world coordinates."""
    if phase in ("arrive", "pebbles"):            # heat haze on a hot day
        for k in range(4):
            y = 360 + k * 90
            cam.line([(x, y + 10 * math.sin(x / 60 + t * 2 + k)) for x in range(60, 1020, 30)], (226, 196, 150), 3)
    sx, sy, r = 820, 560, 100                      # sun with a face
    rays = [(sx + (r + (58 if i % 2 == 0 else 18)) * math.cos(i * math.pi / 14 + t * 0.15),
             sy + (r + (58 if i % 2 == 0 else 18)) * math.sin(i * math.pi / 14 + t * 0.15)) for i in range(28)]
    cam.poly(rays, VERM, w=5)
    cam.ell(sx, sy, r, r, TURM, 6)
    for side in (-1, 1):
        ex = sx + side * 34
        cam.poly([(ex - 20, sy - 12), (ex, sy - 24), (ex + 20, sy - 12), (ex, sy)], PAPER, w=3)
        cam.ell(ex, sy - 12, 5, 5, INK, 1)
    cam.line([(sx - 28, sy + 28), (sx, sy + 42), (sx + 28, sy + 28)], INK, 4)
    for k, hx in enumerate((640, 790, 940)):       # village on the horizon
        cam.poly([(hx - 60, GROUND_Y), (hx - 60, GROUND_Y - 80), (hx + 60, GROUND_Y - 80), (hx + 60, GROUND_Y)],
                 PINK if k % 2 else TURM, "dots", INK, 18, 4)
        cam.poly([(hx - 80, GROUND_Y - 78), (hx, GROUND_Y - 150), (hx + 80, GROUND_Y - 78)], VERM, "hatch", INK, 16, 4)
        cam.poly([(hx - 14, GROUND_Y), (hx - 14, GROUND_Y - 44), (hx + 14, GROUND_Y - 44), (hx + 14, GROUND_Y)], INDIGO, w=3)
    ground = ([(-300, 2400), (-300, GROUND_Y)] + [(x, GROUND_Y + 18 * math.sin(x / 170)) for x in range(-300, 1400, 50)]
              + [(1400, 2400)])
    cam.poly(ground, (214, 168, 96), "dots", INK, 24, 6)
    for k in range(9):                             # grass tufts
        gx, gy = 80 + k * 120, GROUND_Y + 120 + (k % 3) * 70
        for dx, top in ((-12, -30), (0, -38), (12, -28)):
            cam.line([(gx + dx, gy), (gx + dx * 0.5, gy + top)], LEAF, 5)
    cam.poly([(150, GROUND_Y + 40), (220, GROUND_Y + 40), (205, 700), (172, 700)], (120, 70, 40), "hatch", INK, 16, 5)
    for cx, cy, rx in ((190, 620, 170), (90, 720, 110), (300, 720, 115), (190, 500, 110)):
        cam.poly(blob(cx, cy, rx, rx * 0.8), LEAF, "scales", TURM, 26, 6)
    pcx, base = POT                                # pot, with a window showing the water level
    cam.poly(pot_shape(pcx, base), (176, 92, 52), "scales", TURM, 28, 7)
    win = [(pcx - 85, base - 250), (pcx + 85, base - 250), (pcx + 85, base - 40), (pcx - 85, base - 40)]
    cam.poly(win, (250, 244, 228), outline=False)
    wy = base - 40 - 210 * level
    cam.poly([(pcx - 85, wy), (pcx + 85, wy), (pcx + 85, base - 40), (pcx - 85, base - 40)], WATER, "waves", PAPER, 26,
             outline=False)
    for k in range(pebbles_in):
        cam.ell(pcx - 54 + k * 36, base - 58, 16, 12, STONE)
    cam.dbl(cam.pts(win), 4)
    for k in range(max(0, 4 - pebbles_in)):        # pebble pile
        cam.ell(PILE[0] + k * 38, PILE[1] - 10, 18, 13, STONE)


def crow(cam, x, y, flap, happy=False, beak_down=0.0, face=-1):
    f = face
    body = [(x - 70 * f, y + 6), (x - 20 * f, y - 34), (x + 40 * f, y - 30), (x + 62 * f, y), (x + 20 * f, y + 30), (x - 40 * f, y + 26)]
    cam.poly(body, (36, 34, 40), "scales", (90, 90, 104), 22, 5)
    cam.poly([(x - 66 * f, y + 4), (x - 120 * f, y - 16), (x - 112 * f, y + 30)], INDIGO, "hatch", PAPER, 14, 4)
    hx, hy = x + 66 * f, y - 30
    cam.ell(hx, hy, 30, 28, (36, 34, 40), 5)
    cam.poly([(hx + 22 * f, hy - 6), (hx + 70 * math.cos(beak_down) * f, hy + 70 * math.sin(beak_down) + 2), (hx + 22 * f, hy + 10)],
             TURM, w=3)
    cam.poly([(hx - 14, hy - 8), (hx, hy - 16), (hx + 14, hy - 8), (hx, hy)], PAPER, w=2)
    if happy:
        cam.line([(hx - 8, hy - 6), (hx, hy - 12), (hx + 8, hy - 6)], INK, 3)
    else:
        cam.ell(hx + 3 * f, hy - 8, 4, 4, INK, 1)
    cam.poly([(x - 10 * f, y - 20), (x + 26 * f, y - 22), (x - 30 * f, y - 20 - 70 * flap)], LEAF, "dots", TURM, 12, 4)
    for k in (-1, 1):
        cam.line([(x + 10 * k, y + 28), (x + 14 * k, y + 52)], INK, 4)


def draw(ctx, t, args):
    phase = args.get("phase", "arrive")
    u = t / float(args.get("dur", 6.0))
    zoom, cx, cy = CAMERAS.get(phase, CAMERAS["arrive"])
    cam = Cam(ctx, zoom * (1 + 0.03 * u), cx, cy)   # slow push-in during every beat
    if phase == "arrive":
        level, n_in = 0.15, 0
    elif phase == "pebbles":
        n_in = 0 if u <= 0.12 else min(4, int((u - 0.12) / 0.2) + 1)
        level = 0.15 + 0.6 * ease((u - 0.12) / 0.8)
    elif phase == "drink":
        n_in, level = 4, 0.75 - 0.2 * ease((u - 0.3) / 0.6)
    else:
        n_in, level = 4, 0.55
    world(cam, t, phase, level, n_in)
    flap = math.sin(t * 16)
    pcx, base = POT
    perch, top = pcx + 80, base - 330              # where the crow sits on the rim
    if phase == "arrive":
        e = ease(u / 0.8)
        crow(cam, 1150 - (1150 - perch) * e, 420 + (top - 420) * e + 20 * math.sin(t * 3) * (1 - e), flap if e < 1 else 0.05)
    elif phase == "pebbles":
        k, lu = int(u / 0.2), (u % 0.2) / 0.2
        px = PILE[0] + 40
        if lu < 0.5:                               # hop to the pile
            x, y = perch + (px - perch) * ease(lu * 2), top + (PILE[1] - 90 - top) * math.sin(math.pi * lu)
        else:                                      # carry a pebble back and drop it in
            x, y = px + (perch - px) * ease((lu - 0.5) * 2), top + (PILE[1] - 90 - top) * math.sin(math.pi * (lu - 0.5)) * 0.5
        crow(cam, x, y, flap)
        if k < 4 and 0.5 < lu < 0.95:
            cam.ell(x - 40, y + 38, 16, 12, STONE)
    elif phase == "drink":
        crow(cam, perch, top, 0.05, happy=u > 0.6, beak_down=1.1 if u < 0.7 else 0.3)
    else:
        e = ease(u / 0.9)
        crow(cam, perch + (880 - perch) * e, top - 560 * e, flap, happy=True, face=1 if e > 0.05 else -1)
