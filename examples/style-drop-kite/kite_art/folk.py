"""The kite scene painted in FishScaleFolk (engine style: reelkit/art/folk.py)."""
import math  # noqa: F401
import random  # noqa: F401

from PIL import Image, ImageDraw  # noqa: F401

from reelkit.art.painter import closed, dashed, fill_pattern, local, paper_texture, shadow_poly, soft_poly, tile  # noqa: F401
from reelkit.draw import K  # noqa: F401
from reelkit.art.folk import *  # noqa: F401,F403  (the style's colours, helpers and class)
from reelkit.art.folk import FishScaleFolk

from .base import KiteBase


class Kite(KiteBase, FishScaleFolk):
    def sun(self, L):
        cx, cy, r = L["sun"]
        rays = []
        for i in range(32):
            a = math.pi * i / 16
            rr = r + (46 if i % 2 == 0 else 14)
            rays.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        self.c.poly(rays, VERM)
        self.dbl(rays, 5)
        self.c.ell([cx - r, cy - r, cx + r, cy + r], fill=TURM)
        self.c.ell([cx - r, cy - r, cx + r, cy + r], outline=INK, width=6)
        self.c.ell([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], outline=PAPER, width=3)
        for sx in (-1, 1):                     # fish eyes + smile
            ex = cx + sx * 28
            eye = [(ex - 18, cy - 10), (ex, cy - 22), (ex + 18, cy - 10), (ex, cy + 2)]
            self.c.poly(eye, PAPER)
            self.c.line(closed(eye), INK, 3)
            self.c.ell([ex - 5, cy - 15, ex + 5, cy - 5], fill=INK)
        self.c.arc([cx - 26, cy - 4, cx + 26, cy + 40], 20, 160, INK, 4)

    def bg_kites(self, L):
        for i, (pts, role, size) in enumerate(L["bg_kites"]):
            self.c.line([pts[2], (pts[2][0] + size * 0.5, pts[2][1] + size * 3)], INK, 1.6)
            self.folk_shape(pts, self.P(role), "dots", PAPER, 4, 18)

    def skyline(self, L):
        sk = L["skyline"]
        fills = [(INDIGO, "hatch", PAPER), (LEAF, "dots", PAPER), (TURM, "scales", INK), (PINK, "cross", INK)]
        for i, b in enumerate(sk["blocks"]):
            f, pat, pc = fills[i % len(fills)]
            self.folk_shape(b, f, pat, pc, 7, 30)
        for i, w in enumerate(sk["windows"]):
            self.folk_shape(w, TURM if i % 2 else PAPER, None, INK, 5)
            mx = (w[0][0] + w[1][0]) / 2
            self.c.line([(mx, w[0][1]), (mx, w[2][1])], INK, 3)
        x0, y0, x1, y1 = sk["tank"]
        tank = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        self.folk_shape(tank, VERM, "scales", TURM, 6, 26)
        self.c.line(sk["antenna"], INK, 7)
        for bar in sk["antenna_bars"]:
            self.c.line(bar, INK, 6)
        self.c.line(sk["toran"], INK, 3)
        for i, (x, y) in enumerate(sk["toran"][1:-1]):     # marigolds: turmeric petals, vermilion heart
            self.c.ell([x - 14, y - 2, x + 14, y + 26], fill=TURM if i % 2 else VERM)
            self.c.ell([x - 14, y - 2, x + 14, y + 26], outline=INK, width=3)
            self.c.ell([x - 5, y + 7, x + 5, y + 17], fill=INK)

    def birds(self, L):
        for i, (x, y, flap) in enumerate(L["birds"]):
            body = [(x - 30, y), (x - 6, y - 14), (x + 24, y - 6), (x + 34, y + 2), (x + 14, y + 12), (x - 12, y + 10)]
            self.c.poly(body, LEAF if i % 2 else INDIGO)
            self.dbl(body, 4)
            wing = [(x - 8, y - 6), (x + 6, y - 6 - 34 * flap), (x + 16, y - 4)]
            self.c.poly(wing, TURM)
            self.c.line(closed(wing), INK, 3)
            self.c.ell([x + 18, y - 6, x + 26, y + 2], fill=INK)
            self.c.poly([(x - 30, y), (x - 50, y - 12), (x - 46, y + 12)], VERM)

    def strings(self, L):
        for seg in L["rival_string"]:
            self.c.line(seg, INK, 3)
        self.c.line(L["hero_string"], INK, 3.5)

    def rival(self, L):
        t, r, b, l = L["rival"]
        mid = ((l[0] + r[0]) / 2, (l[1] + r[1]) / 2)
        top = [t, r, mid, l]
        bot = [l, mid, r, b]
        self.c.poly(top, INDIGO)
        fill_pattern(self.im, top, tile("dots", PAPER, None, 20, 2))
        self.c.poly(bot, TURM)
        fill_pattern(self.im, bot, tile("hatch", INK, None, 20, 2))
        tri = [b, (b[0] - 20, b[1] + 38), (b[0] + 20, b[1] + 38)]
        self.c.poly(tri, VERM)
        self.c.line(closed(tri), INK, 3)
        self.c.line([l, r], INK, 4)
        self.dbl(L["rival"], 6)

    def tail(self, L):
        pts = [L["hero"][2]] + L["tail"]
        for i in range(len(pts) - 1):
            w = 22 - i * 1.1
            self.c.line([pts[i], pts[i + 1]], INK, w + 8)
        for i in range(len(pts) - 1):
            w = 22 - i * 1.1
            self.c.line([pts[i], pts[i + 1]], TURM if i % 2 else VERM, w)
        for (x, y) in pts[1::2]:                                 # bows on the tail
            self.c.ell([x - 6, y - 6, x + 6, y + 6], fill=LEAF)

    def hero(self, L):
        self.c.poly(L["hero"], VERM)
        fill_pattern(self.im, L["hero"], tile("scales", TURM, None, 30, 2.6))
        # inner diamond panel for the face
        c, a = L["hero_c"], L["hero_angle"]
        k = L["hero_s"]
        inner = [local(c, a, 0, -84 * k), local(c, a, 78 * k, 0), local(c, a, 0, 112 * k), local(c, a, -78 * k, 0)]
        self.c.poly(inner, PAPER)
        self.c.line(closed(inner), INK, 4)
        self.dbl(L["hero"], 8)

    def hero_face(self, L):
        c, a = L["hero_c"], L["hero_angle"]
        k = L["hero_s"]
        Lp = lambda x, y: local(c, a, x * k, y * k)  # noqa: E731
        for sx in (-1, 1):   # horns
            horn = [Lp(sx * 16, -46), Lp(sx * 40, -92), Lp(sx * 34, -40)]
            self.c.poly(horn, TURM)
            self.c.line(closed(horn), INK, 3)
        head = [Lp(-56, -30), Lp(0, -56), Lp(56, -30), Lp(48, 50), Lp(0, 74), Lp(-48, 50)]
        self.c.poly(head, LEAF)
        fill_pattern(self.im, head, tile("dots", TURM, None, 16, 2))
        self.c.line(closed(head), INK, 4)
        for sx in (-1, 1):   # almond fish eyes
            ex = sx * 24
            eye = [Lp(ex - 18, -12), Lp(ex, -26), Lp(ex + 18, -12), Lp(ex, 0)]
            self.c.poly(eye, PAPER)
            self.c.line(closed(eye), INK, 3)
            px, py = Lp(ex + sx * 3, -13)
            self.c.ell([px - 6, py - 6, px + 6, py + 6], fill=INK)
        for sx in (-1, 1):
            nx, ny = Lp(sx * 10, 18)
            self.c.ell([nx - 4, ny - 4, nx + 4, ny + 4], fill=INK)
        mouth = [Lp(-30, 38), Lp(0, 52), Lp(30, 38)]
        self.c.poly(mouth, VERM)
        self.c.line(closed(mouth), INK, 3)
        teeth = [Lp(-24 + i * 8, 40 + (8 if i % 2 else 2)) for i in range(7)]
        self.c.line(teeth, PAPER, 3)
        for sx in (-1, 1):   # curling whiskers
            pts = [Lp(sx * (40 + 6 * k), 30 + 9 * k + 6 * math.sin(k)) for k in range(7)]
            self.c.line(pts, INK, 4)

    def burst(self, L):
        u = L["burst"]
        if u is None:
            return
        x, y = L["cut_pt"]
        grow = min(1, u / 0.3)
        for k, (col, rmul, n, rot) in enumerate(((VERM, 1.0, 12, 0.0), (TURM, 0.66, 10, 0.3), (PAPER, 0.3, 8, 0.1))):
            r = (120 + 200 * grow) * rmul * (1 - 0.25 * max(0, u - 0.5))
            pts = [(x + (r if i % 2 == 0 else r * 0.5) * math.cos(math.pi * i / n + rot + u),
                    y + (r if i % 2 == 0 else r * 0.5) * math.sin(math.pi * i / n + rot + u)) for i in range(2 * n)]
            if u < 0.85:
                self.c.poly(pts, col)
                self.dbl(pts, 5)
        self.sparkles(L)

    def shout(self, L):
        if not L["shout"]:
            return
        u = min(1.0, L["shout_t"] / 0.25)
        size = 118 * (0.4 + 0.6 * u) * (1 + 0.05 * math.sin(L["shout_t"] * 9))
        f = self.c.f("display", size)
        xy = (L["shout_xy"][0] * K, L["shout_xy"][1] * K)
        self.c.d.text(xy, "Kaipoche!", font=f, anchor="mm", fill=VERM, stroke_width=int(14 * K), stroke_fill=INK)
        self.c.d.text(xy, "Kaipoche!", font=f, anchor="mm", fill=VERM, stroke_width=int(6 * K), stroke_fill=PAPER)
