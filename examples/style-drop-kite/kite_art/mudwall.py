"""The kite scene painted in MudWall (engine style: reelkit/art/mudwall.py)."""
import math  # noqa: F401
import random  # noqa: F401

from PIL import Image, ImageDraw  # noqa: F401

from reelkit.art.painter import closed, dashed, fill_pattern, local, paper_texture, shadow_poly, soft_poly, tile  # noqa: F401
from reelkit.draw import K  # noqa: F401
from reelkit.art.mudwall import *  # noqa: F401,F403  (the style's colours, helpers and class)
from reelkit.art.mudwall import MudWall

from .base import KiteBase


class Kite(KiteBase, MudWall):
    def sun(self, L):
        x, y, r = L["sun"]
        self.c.ell([x - r * 0.7, y - r * 0.7, x + r * 0.7, y + r * 0.7], outline=WHITE, width=5)
        for i in range(16):
            a = i * math.pi / 8 + self.t * 0.2
            self.ln([(x + r * 0.85 * math.cos(a), y + r * 0.85 * math.sin(a)), (x + r * 1.35 * math.cos(a), y + r * 1.35 * math.sin(a))], 4, i)
        for k in range(3):
            rr = r * (0.18 + 0.15 * k)
            self.c.ell([x - rr, y - rr, x + rr, y + rr], outline=WHITE, width=2)

    def bg_kites(self, L):
        for i, (pts, role, size) in enumerate(L["bg_kites"]):
            self.tri(pts, fill=False, seed=i)
            self.ln([pts[0], pts[2]], 2, i)
            self.ln([pts[2], (pts[2][0] + size * 0.5, pts[2][1] + size * 3)], 1.5, i)

    def skyline(self, L):
        sk = L["skyline"]
        for i, b in enumerate(sk["blocks"]):
            (x0, _), (_, top), (x1, _) = b[0], b[1], b[2]
            self.ln([(x0, 1930), (x0, top), (x1, top), (x1, 1930)], 4, i)
            n = max(3, int((x1 - x0) / 34))
            for k in range(n):                                   # triangle chain along the roof line
                a, bb = x0 + (x1 - x0) * k / n, x0 + (x1 - x0) * (k + 1) / n
                self.tri([(a, top + 4), (bb, top + 4), ((a + bb) / 2, top + 30)], seed=i * 10 + k)
        for i, w in enumerate(sk["windows"]):
            (x0, y0), (x1, _), (_, y1) = w[0], w[1], w[2]
            self.tri([(x0, y1), (x1, y1), ((x0 + x1) / 2, y0)], fill=False, seed=i)
        x0, y0, x1, y1 = sk["tank"]
        self.ln([(x0, y1), (x0, y0), (x1, y0), (x1, y1), (x0, y1)], 4, 7)
        for k in range(4):
            yy = y0 + 20 + k * 28
            self.ln([(x0 + 10, yy), (x1 - 10, yy)], 2, k)
        self.ln(sk["antenna"], 4, 3)
        for bar in sk["antenna_bars"]:
            self.ln(bar, 3, 4)
        self.ln(sk["toran"], 2, 5)
        for x, y in sk["toran"][1:-1]:
            self.c.ell([x - 6, y + 2, x + 6, y + 14], fill=WHITE)
        # people on the roofs, flying kites and cheering
        roof = sk["blocks"]
        spots = [(roof[1], 0.45, False), (roof[2], 0.3, True), (roof[3], 0.6, True)]
        cheer = self.t >= 2.2
        for k, (b, f, up) in enumerate(spots):
            x = b[1][0] + (b[2][0] - b[1][0]) * f
            self.person(x, b[1][1] - 2, 0.85, up and cheer, seed=20 + k)

    def birds(self, L):
        for i, (x, y, flap) in enumerate(L["birds"]):
            self.tri([(x - 10, y), (x + 14, y), (x + 2, y + 10)], seed=i)
            for k in range(4):                                      # line-fan wings
                self.ln([(x, y), (x - 26 + k * 8, y - 18 - 14 * flap)], 2, i + k)

    def strings(self, L):
        for seg in L["rival_string"]:
            self.ln(seg, 2, 30)
        self.ln(L["hero_string"], 2.5, 31)

    def rival(self, L):
        t, r, b, l = L["rival"]
        self.tri(L["rival"], fill=False, seed=40)
        self.tri([t, r, l], seed=41)
        self.tri([b, (b[0] - 16, b[1] + 30), (b[0] + 16, b[1] + 30)], seed=42)

    def tail(self, L):
        pts = [L["hero"][2]] + L["tail"]
        for i in range(1, len(pts)):
            x, y = pts[i]
            s = 12 - i * 0.6
            self.tri([(x - s, y - s), (x + s, y - s), (x, y + s)], seed=50 + i)

    def hero(self, L):
        h = L["hero"]
        self.tri(h, fill=False, seed=60)
        c, a, k = L["hero_c"], L["hero_angle"], L["hero_s"]
        inner = [local(c, a, 0, -70 * k), local(c, a, 64 * k, 0), local(c, a, 0, 96 * k), local(c, a, -64 * k, 0)]
        self.tri(inner, fill=False, seed=61)
        for i, (px, py) in enumerate(h):          # dotted corners
            self.c.ell([px - 7, py - 7, px + 7, py + 7], fill=WHITE)

    def hero_face(self, L):
        c, a, k = L["hero_c"], L["hero_angle"], L["hero_s"]
        Lp = lambda x, y: local(c, a, x * k, y * k)  # noqa: E731
        for sx in (-1, 1):
            self.tri([Lp(sx * 14, -36), Lp(sx * 34, -74), Lp(sx * 30, -32)], seed=70 + sx)        # horns
            ex, ey = Lp(sx * 22, -8)
            self.c.ell([ex - 9, ey - 9, ex + 9, ey + 9], fill=WHITE)
            self.ln([Lp(sx * 18, 34), Lp(sx * 52, 26), Lp(sx * 70, 44)], 2.5, 72 + sx)               # whiskers
        self.tri([Lp(-24, 30), Lp(24, 30), Lp(0, 52)], seed=74)                                          # mouth
        for i in range(5):
            x, y = Lp(-30 + i * 15, 66)
            self.c.ell([x - 3, y - 3, x + 3, y + 3], fill=WHITE)

    def burst(self, L):
        u = L["burst"]
        if u is None:
            return
        x, y = L["cut_pt"]
        for ring in range(3):                       # rings of dots expanding out
            r = 40 + 260 * min(1, u / 0.6) * (0.45 + 0.3 * ring)
            n = 12 + ring * 6
            dot = max(2, 9 - ring * 2) * (1 - 0.6 * u)
            for i in range(n):
                q = 2 * math.pi * i / n + ring * 0.2
                px, py = x + r * math.cos(q), y + r * math.sin(q)
                self.c.ell([px - dot, py - dot, px + dot, py + dot], fill=WHITE)

    def shout(self, L):
        if not L["shout"]:
            return
        u = min(1.0, L["shout_t"] / 0.25)
        x, y = L["shout_xy"]
        jx, jy = self.j([(0, 0)], self.t, 3)[0]
        self.c.text((x + jx, y + jy), "Kaipoche!", 110 * (0.5 + 0.5 * u), "display", WHITE)
