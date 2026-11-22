"""Gold Court: inspired by court miniature painting. A lapis sky band with gold scroll clouds over a pale
wash, rolling green hills with round dotted trees, a river of little woven waves, jewel-flat colours,
burnished gold and pearl-white dots, hairline outlines, elegant figures in profile with one large eye,
and a red border with a gold vine. The impact is a ring of gold rays.

Figures: `figure()` draws a standing person in profile (a lady in ghagra, choli and a sheer veil, or a
man in a flared jama, sash and turban) from a few colours, facing left or right, optionally holding a
lotus. `deer()`, `round_tree()`, `pavilion()`, `hills()`, `river()` and `sun()` are ready motifs.
"""
import math
import random

from PIL import Image, ImageDraw

from ..draw import K
from .painter import Painter, closed, soft_poly

LINE = (70, 40, 30)
GOLD, GOLD_D = (214, 170, 70), (170, 122, 40)
LAPIS = (32, 56, 140)
RED = (180, 36, 36)
PEARL = (250, 246, 236)
SKIN = (238, 196, 160)
HAIR = (30, 24, 28)
GREEN, GREEN_D = (96, 150, 86), (58, 108, 64)
MARBLE = (246, 240, 228)
WASH = [(0, (232, 222, 190)), (1200, (240, 226, 196)), (1920, (226, 214, 170))]
HAIRLINE = 2.2


def cr(pts, n=8, closed_=True):
    """Catmull-Rom smoothing through pts."""
    out, m = [], len(pts)
    for i in (range(m) if closed_ else range(m - 1)):
        p0 = pts[(i - 1) % m] if closed_ or i > 0 else pts[0]
        p1, p2 = pts[i], pts[(i + 1) % m]
        p3 = pts[(i + 2) % m] if closed_ or i + 2 < m else pts[-1]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    if not closed_:
        out.append(pts[-1])
    return out


def ell(cx, cy, rx, ry, rot=0.0, n=40, a0=0.0, a1=2 * math.pi):
    c, s = math.cos(rot), math.sin(rot)
    full = a1 - a0 >= 2 * math.pi - 1e-6
    return [(cx + rx * math.cos(a) * c - ry * math.sin(a) * s, cy + rx * math.cos(a) * s + ry * math.sin(a) * c)
            for a in (a0 + (a1 - a0) * i / n for i in range(n + (0 if full else 1)))]


class GoldCourt(Painter):
    name = "gold-court"
    fps = 0
    jitter = 0.0
    pal = dict(Painter.pal, ink=LINE, string=LINE, hero=RED, hero2=GOLD, rival=LAPIS, rival2=PEARL, tail=GOLD,
               tail2=RED, bird=LINE, burst=GOLD, burst2=PEARL, text=RED, sun=GOLD)
    brand = {"bg_top": WASH[0][1], "bg_bottom": WASH[-1][1], "fg": LINE, "muted": (130, 100, 80), "accent": RED,
             "highlight": GOLD, "panel": MARBLE, "ink": LINE, "good": GREEN_D, "bad": RED, "sub_bg": LAPIS, "sub_fg": PEARL}

    # ---------- primitives ----------
    def fill(self, pts, col, w=HAIRLINE, line=LINE):
        self.c.poly(pts, col)
        if line and w:
            self.c.line(closed(pts), line, w)

    def dots(self, pts, col=PEARL, r=3):
        for x, y in pts:
            self.c.ell([x - r, y - r, x + r, y + r], fill=col)

    def glow(self, cx, cy, r, col, a=0.5):
        from PIL import ImageFilter
        lay = Image.new("L", self.im.size, 0)
        ImageDraw.Draw(lay).ellipse([(cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K], fill=int(255 * a))
        self.im.paste(col, (0, 0), lay.filter(ImageFilter.GaussianBlur(r * K * 0.45)))

    def wash(self, stops=WASH):
        g = Image.new("RGB", (1, 1920))
        for y in range(1920):
            for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
                if y0 <= y <= y1:
                    u = (y - y0) / max(1, y1 - y0)
                    g.putpixel((0, y), tuple(int(a + (b - a) * u) for a, b in zip(c0, c1)))
                    break
        self.im.paste(g.resize(self.im.size, Image.BICUBIC))

    # ---------- surface + frame ----------
    def background(self, L):
        self.wash()
        self.lapis_band(L.get("band", 320) if L else 320)

    def lapis_band(self, h=320, seed=9):
        curve = [(x, h + 22 * math.sin(x / 70)) for x in range(0, 1081, 20)]
        self.fill([(0, 0), (1080, 0)] + list(reversed(curve)), LAPIS, 0, None)
        self.c.line(curve, GOLD, 4)
        for x, y, s in ((200, 0.47, 1.0), (520, 0.69, 0.8), (840, 0.4, 1.1), (360, 0.28, 0.6), (960, 0.8, 0.6)):
            self.scroll_cloud(x, y * h, s)
        rnd = random.Random(seed)
        for _ in range(40):
            self.dots([(rnd.uniform(40, 1040), rnd.uniform(50, h - 20))], (250, 230, 160), 2)

    def overlay(self, L):
        """Red border with a gold vine and a hairline inner rule."""
        b = 40
        for box in ([(0, 0), (1080, 0), (1080, b), (0, b)], [(0, 1920 - b), (1080, 1920 - b), (1080, 1920), (0, 1920)],
                    [(0, 0), (b, 0), (b, 1920), (0, 1920)], [(1080 - b, 0), (1080, 0), (1080, 1920), (1080 - b, 1920)]):
            self.c.poly(box, RED)
        for horiz, fixed in ((True, b / 2), (True, 1920 - b / 2), (False, b / 2), (False, 1080 - b / 2)):
            n = 1080 if horiz else 1920
            pts = [((t, fixed + 8 * math.sin(t / 22)) if horiz else (fixed + 8 * math.sin(t / 22), t)) for t in range(0, n + 1, 6)]
            self.c.line(pts, GOLD, 2.4)
            for t in range(11, n, 69):
                px, py = (t, fixed + 8 * math.sin(t / 22)) if horiz else (fixed + 8 * math.sin(t / 22), t)
                self.c.poly(ell(px, py - (6 if horiz else 0), 6, 3.5, 0.6, n=12), GOLD)
        self.c.line(closed([(b, b), (1080 - b, b), (1080 - b, 1920 - b), (b, 1920 - b)]), GOLD, 3)
        self.c.line(closed([(b + 8, b + 8), (1072 - b, b + 8), (1072 - b, 1912 - b), (b + 8, 1912 - b)]), LINE, 1.6)

    # ---------- motifs ----------
    def scroll_cloud(self, x, y, s=1.0, col=GOLD):
        path = [(x - 90 * s, y), (x - 40 * s, y - 18 * s), (x + 20 * s, y + 6 * s), (x + 80 * s, y - 10 * s)]
        self.c.line(cr(path, 8, False), col, 4 * s + 1)
        for cx, cy, d in ((x - 90 * s, y, -1), (x + 80 * s, y - 10 * s, 1)):
            self.c.line([(cx + d * (16 - 2 * k) * s * math.cos(k * 0.7), cy + (16 - 2 * k) * s * math.sin(k * 0.7)) for k in range(8)], col, 3 * s + 1)

    def sun(self, x, y, r=60, rays=True):
        self.glow(x, y, r * 2.5, (255, 230, 150), 0.5)
        if rays:
            for k in range(24):
                a = 2 * math.pi * k / 24
                r1 = r * (1.85 if k % 2 else 2.25)
                self.c.line([(x + r * 1.15 * math.cos(a), y + r * 1.15 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], GOLD, 3)
        self.fill(ell(x, y, r, r), GOLD)
        self.fill(ell(x, y, r * 0.73, r * 0.73), (236, 196, 90), 1.4)

    def gold_rays(self, x, y, u, n=32):
        """The impact: gold rays spreading from (x, y); u = 0..1."""
        r0, r1 = 40 + 200 * u, 200 + 1200 * u
        for k in range(n):
            a = 2 * math.pi * k / n + 0.05
            self.c.poly([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a - 0.04), y + r1 * math.sin(a - 0.04)),
                         (x + r1 * math.cos(a + 0.04), y + r1 * math.sin(a + 0.04))], GOLD if k % 2 else (240, 210, 120))

    def birds(self, flock):
        for x, y, s in flock:
            self.c.line([(x - 26 * s, y - 10 * s), (x, y), (x + 26 * s, y - 12 * s)], LINE, 5)
            self.c.line([(x - 24 * s, y - 9 * s), (x, y), (x + 24 * s, y - 11 * s)], PEARL, 2.5)

    def round_tree(self, x, y, r, seed=0):
        rnd = random.Random(seed)
        self.c.line([(x, y + r * 0.6), (x, y + r * 1.8)], (110, 70, 40), 6)
        self.fill(ell(x, y, r, r * 1.05), GREEN_D)
        for _ in range(int(r * 0.9)):
            a, rr = rnd.uniform(0, 2 * math.pi), r * math.sqrt(rnd.uniform(0.05, 0.9))
            self.dots([(x + rr * math.cos(a), y + rr * math.sin(a))], (150, 200, 120), 2.5)
        self.dots([(x + r * math.cos(2 * math.pi * k / 28), y + r * 1.05 * math.sin(2 * math.pi * k / 28)) for k in range(28)], (170, 210, 130), 3)

    def hills(self, base, col, amp=(40, 120), seed=1):
        rnd = random.Random(seed)
        pts, x = [(0, base)], 0
        while x < 1080:
            x += rnd.uniform(140, 260)
            pts.append((min(x, 1080), base - rnd.uniform(*amp)))
        self.fill([(0, 1920)] + cr(pts, 6, False) + [(1080, 1920)], col)

    def river(self, y0, y1, col=(150, 180, 200)):
        self.fill(cr([(0, y0), (400, y0 - 20), (800, y0 + 10), (1080, y0 - 10)], 6, False) + [(1080, y1), (0, y1 + 10)], col)
        for row in range(int((y1 - y0 - 20) / 20)):
            y = y0 + 15 + row * 20
            for x in range(10 + (row % 2) * 20, 1080, 40):
                self.c.line(cr([(x, y), (x + 10, y - 6), (x + 20, y)], 4, False), (240, 246, 250), 2)

    def pavilion(self, x0=40, x1=360, top=900, floor=1440, inside=RED):
        for x in (x0 + 20, (x0 + x1) / 2 + 10, x1 - 40):
            self.fill([(x, top + 120), (x + 26, top + 120), (x + 26, floor), (x, floor)], MARBLE)
        cols = [x0 + 20, (x0 + x1) / 2 + 10, x1 - 40]
        for a, b in ((cols[0] + 26, cols[1]), (cols[1] + 26, cols[2])):
            self.fill([(a, floor), (a, top + 200)] + [((a + b) / 2 + (b - a) / 2 * math.cos(t), top + 200 - 60 * math.sin(t) + 10 * abs(math.sin(4 * t)))
                                                    for t in [math.pi - i * math.pi / 30 for i in range(31)]] + [(b, floor)], inside)
        self.fill([(x0, top + 80), (x1 + 30, top + 80), (x1 + 30, top + 120), (x0, top + 120)], MARBLE)
        cx, r = (x0 + x1 + 30) / 2, (x1 - x0) * 0.47
        self.fill([(x0 + 30, top + 80)] + [(cx - r * math.cos(t), top + 80 - r * 1.13 * math.sin(t) ** 0.8) for t in [i * math.pi / 30 for i in range(31)]] + [(x1, top + 80)], MARBLE)
        self.c.line([(cx, top - r * 0.6), (cx, top - r * 1.1)], GOLD, 5)
        self.fill(ell(cx, top - r * 0.75, 14, 14), GOLD)

    def deer(self, x, y, s, facing=1, col=(196, 130, 70)):
        U = lambda pts: [(x + facing * px * s, y + py * s) for px, py in pts]  # noqa: E731
        for lx in (-0.8, -0.5, 0.6, 0.85):
            self.c.line(U([(lx, 0.2), (lx - 0.05, 1.5)]), LINE, 5)
            self.c.line(U([(lx, 0.2), (lx - 0.05, 1.5)]), col, 3)
        self.fill(U(cr([(-1.1, -0.2), (0.0, -0.45), (1.0, -0.3), (1.15, 0.2), (0.2, 0.45), (-1.0, 0.35)], 5)), col)
        self.dots(U([(-0.8 + 0.3 * k, -0.1 + 0.15 * (k % 2)) for k in range(6)]), PEARL, 3)
        self.fill(U([(0.7, -0.3), (1.3, -1.3), (1.6, -1.2), (1.1, -0.05)]), col)
        self.fill(U(cr([(1.3, -1.4), (1.7, -1.55), (2.15, -1.3), (1.7, -1.1)], 4)), col)
        self.dots(U([(1.68, -1.38)]), HAIR, 3)
        for d in (-0.1, 0.1):
            self.c.line(U([(1.5 + d, -1.5), (1.4 + d, -2.1), (1.2 + d, -2.4)]), LINE, 3)
            self.c.line(U([(1.42 + d, -1.95), (1.65 + d, -2.2)]), LINE, 3)

    # ---------- figures ----------
    def profile_head(self, U, hy, skin=SKIN, hair=HAIR, male=False, beard=None):
        """Profile head facing +x, centre (0, hy) in unit space; one large almond eye, straight nose."""
        H = lambda pts: U([(px, py + hy) for px, py in pts])  # noqa: E731
        self.fill(H(cr([(-0.55, 0.5), (-0.85, 0.0), (-0.55, -0.85), (0.0, -1.05), (0.42, -0.94), (0.6, -0.55), (0.66, -0.3), (0.8, -0.08),
                        (0.98, 0.14), (0.8, 0.2), (0.82, 0.3), (0.72, 0.36), (0.79, 0.43), (0.7, 0.52), (0.74, 0.64), (0.5, 0.8), (0.05, 0.7)], 3)), skin)
        self.fill(H(cr([(0.4, -0.97), (0.22, -0.6), (0.02, -0.3), (-0.06, 0.25), (-0.3, 0.6), (-0.66, 0.52), (-0.9, 0.0), (-0.58, -0.9), (0.0, -1.1)], 4)), hair)
        self.fill(H(cr([(0.3, -0.12), (0.5, -0.22), (0.7, -0.17), (0.5, -0.04)], 5)), PEARL, 1.6)
        self.c.poly(H(ell(0.56, -0.13, 0.065, 0.07, n=16)), HAIR)
        self.c.line(H(cr([(0.26, -0.34), (0.48, -0.4), (0.66, -0.3)], 5, False)), HAIR, 3)
        self.c.line(H([(0.3, -0.12), (0.18, -0.09)]), HAIR, 2.5)
        if beard:
            self.fill(H(cr([(0.05, 0.3), (0.45, 0.42), (0.72, 0.5), (0.76, 0.68), (0.5, 0.95), (0.1, 0.8)], 4)), beard)
        elif male:
            self.c.line(H(cr([(0.62, 0.3), (0.76, 0.28), (0.86, 0.33)], 4, False)), HAIR, 3)    # moustache
        else:
            self.c.poly(H(ell(0.76, 0.38, 0.05, 0.03, n=12)), (200, 60, 70))
        return H

    def figure(self, x, y, s, facing=1, male=False, dress=RED, top=(40, 110, 90), veil=(250, 220, 120), turban=(250, 246, 236),
               skin=SKIN, hair=HAIR, beard=None, lotus=False, jewels=True):
        """A standing figure in profile. (x, y) = feet, s = head half-height (px), facing 1 = right, -1 = left."""
        f = facing
        U = lambda pts: [(x + f * px * s, y + py * s) for px, py in pts]  # noqa: E731
        hy = -13.6
        if not male:                                                      # braid down the back
            self.fill(U([(-0.6, hy + 0.4), (-0.95, hy + 2.5), (-1.0, hy + 6.0), (-0.7, hy + 6.4), (-0.55, hy + 2.5), (-0.3, hy + 0.6)]), hair)
            self.fill(U(ell(-0.85, hy + 6.6, 0.18, 0.3, n=16)), RED)
        sk = U(cr([(-1.3, -8.6), (1.1, -8.6), (2.3, -4.0), (3.4, 0.0), (-3.2, 0.0), (-2.4, -4.0)], 5))
        self.fill(sk, dress)
        pleat = tuple(min(255, v + 30) for v in dress)
        for k in range(-6, 7):
            self.c.line(U([(k * 0.19, -8.5), (k * 0.52, -0.25)]), pleat, 2.5)
            if k % 2 == 0:
                self.dots(U([(k * (0.19 + 0.33 * u), -8.5 + 8.25 * u) for u in (0.15, 0.3, 0.45, 0.6, 0.75, 0.9)]), GOLD, 2.6)
        self.fill(U([(-3.2, -0.5), (3.4, -0.5), (3.4, 0.0), (-3.2, 0.0)]), GOLD)
        self.dots(U([(-3.0 + k * 0.33, -0.25) for k in range(20)]), RED if dress != RED else PEARL, 2)
        self.fill(U([(1.6, 0.0), (2.4, -0.1), (2.6, 0.12), (1.6, 0.15)]), (220, 90, 80) if not male else (120, 60, 40))
        torso_col = dress if male else skin
        self.fill(U(cr([(-0.6, hy + 1.6), (0.45, hy + 1.6), (0.9, hy + 3.0), (1.05, hy + 4.0), (0.9, -8.4), (-1.1, -8.4), (-1.1, hy + 3.5), (-0.9, hy + 2.4)], 5)), torso_col)
        if male:
            self.fill(U([(-0.95, -9.0), (1.0, -9.0), (1.05, -8.5), (-1.0, -8.5)]), top)            # patka sash
            self.fill(U([(0.6, -8.6), (1.0, -8.6), (1.25, -5.0), (0.8, -5.0)]), top)
            self.dots(U([(0.85 + 0.05 * k, -8.2 + 0.6 * k) for k in range(6)]), GOLD, 2.4)
        else:
            self.fill(U([(-1.2, -8.9), (1.0, -8.9), (1.1, -8.45), (-1.25, -8.45)]), GOLD)
            self.fill(U(cr([(-1.0, hy + 2.8), (0.6, hy + 2.6), (1.15, hy + 3.4), (1.0, hy + 4.4), (-1.15, hy + 4.5)], 5)), top)
            self.dots(U([(-0.8 + k * 0.3, hy + 3.4 + 0.3 * (k % 2)) for k in range(7)]), GOLD, 2.4)
        self.fill(U(cr([(-0.1, hy + 0.4), (0.42, hy + 0.55), (0.5, hy + 1.5), (0.7, hy + 1.95), (-0.7, hy + 1.95), (-0.4, hy + 1.4)], 4)), skin)
        H = self.profile_head(U, hy, skin, hair, male, beard)
        if male:                                                           # turban with a gold band and a plume
            self.fill(H(cr([(-0.75, -0.3), (-0.95, -0.9), (-0.5, -1.45), (0.2, -1.5), (0.6, -1.1), (0.55, -0.6), (0.2, -0.75), (-0.3, -0.6)], 5)), turban)
            for k in range(3):
                self.c.line(H(cr([(-0.8 + k * 0.1, -0.5 - k * 0.25), (-0.1, -0.85 - k * 0.2), (0.5, -0.8 - k * 0.15)], 4, False)), GOLD_D, 2)
            self.c.line(H([(0.1, -1.45), (0.35, -2.0), (0.6, -2.1)]), GOLD, 3)
        if jewels:
            if not male:
                nath = H(ell(0.84, 0.3, 0.1, 0.13, a0=-1.4, a1=2.4, n=20))
                self.c.line(nath, GOLD, 2.4)
                self.dots(nath[::7], PEARL, 2.4)
                self.c.poly(H(ell(0.56, -0.62, 0.035, 0.035, n=10)), RED)
            self.fill(H(ell(0.02, 0.38, 0.1, 0.12, n=16)), GOLD, 1.4)
            self.dots(H([(0.02 + 0.12 * math.cos(a), 0.38 + 0.15 * math.sin(a)) for a in [i * 0.7 for i in range(9)]]), PEARL, 2.4)
            self.dots(U([(0.55 * math.cos(a), hy + 1.95 + 0.45 * math.sin(a)) for a in [math.pi * (0.1 + 0.8 * k / 8) for k in range(9)]]), PEARL, 3.2)
        arm_col = dress if male else skin
        self.fill(U(cr([(0.3, hy + 2.2), (0.6, hy + 3.4), (1.2, hy + 4.4), (1.9, hy + 3.8), (2.0, hy + 3.45), (1.25, hy + 3.8), (0.95, hy + 2.9), (0.8, hy + 2.1)], 4)), arm_col)
        self.fill(U(ell(1.95, hy + 3.65, 0.18, 0.15, n=12)), skin, 1.4)
        if lotus:
            self.c.line(U([(2.0, hy + 3.7), (2.4, hy + 2.6)]), GREEN_D, 3)
            for k in range(7):
                a = -math.pi / 2 + (k - 3) * 0.32
                self.fill(U([(2.4 + 0.1 * math.cos(a), hy + 2.6 + 0.1 * math.sin(a)), (2.4 + 0.55 * math.cos(a - 0.15), hy + 2.6 + 0.55 * math.sin(a - 0.15)),
                             (2.4 + 0.75 * math.cos(a), hy + 2.6 + 0.75 * math.sin(a)), (2.4 + 0.55 * math.cos(a + 0.15), hy + 2.6 + 0.55 * math.sin(a + 0.15))]), (240, 150, 170), 1.4)
        if not male and veil:                                              # sheer odhni over head and back
            v = U(cr([(0.42, hy - 1.15), (-0.6, hy - 1.05), (-1.15, hy + 0.5), (-1.6, hy + 4.0), (-2.2, hy + 8.0), (-1.4, hy + 8.2), (-0.7, hy + 4.0),
                      (0.1, hy + 1.6), (0.3, hy + 0.0), (0.6, hy - 0.6)], 5))
            soft_poly(self.im, v, veil, 0.45)
            self.c.line(closed(v), GOLD_D, 2)
            self.dots(U(cr([(0.42, hy - 1.15), (-0.6, hy - 1.05), (-1.15, hy + 0.5), (-1.6, hy + 4.0), (-2.2, hy + 8.0)], 6, False)[::2]), GOLD, 2.6)
