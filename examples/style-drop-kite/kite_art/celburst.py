"""The kite scene painted in CelBurst (engine style: reelkit/art/celburst.py)."""
import math

from reelkit.art.celburst import INK, CelBurst, ell
from reelkit.art.painter import local
from reelkit.draw import K

from .base import KiteBase

HERO, HERO_SH, HERO2 = (232, 56, 60), (170, 30, 50), (255, 206, 70)
RIVAL, RIVAL_SH = (60, 110, 230), (36, 70, 170)
ROOFS = [((250, 160, 120), (200, 110, 100)), ((140, 170, 230), (100, 120, 190)), ((250, 220, 150), (210, 170, 110))]


def right_of(pts, cx):
    """A big box covering everything right of x = cx (the side in shadow)."""
    return [(cx, -4000), (cx + 8000, -4000), (cx + 8000, 8000), (cx, 8000)]


class Kite(KiteBase, CelBurst):
    def cel(self, pts, col, sh, w=5):
        cx = sum(p[0] for p in pts) / len(pts)
        self.fill(pts, col, None, 0)
        self.shade(pts, right_of(pts, cx), sh)
        self.outline(pts, w)

    def sun(self, L):
        x, y, r = L["sun"]
        self.rays(x, y, 20, 1300, (255, 240, 200), 0.14)
        self.glow(x, y, r * 2.2, (255, 240, 200), 0.7)
        self.fill(ell(x, y, r, r), (255, 250, 230), INK, 4)

    def bg_kites(self, L):
        for i, (pts, role, size) in enumerate(L["bg_kites"]):
            self.c.line([pts[2], (pts[2][0] + size * 0.5, pts[2][1] + size * 3)], INK, 1.5)
            self.cel(pts, [(255, 120, 160), (120, 210, 150), (170, 140, 250)][i % 3], [(200, 80, 120), (80, 160, 110), (120, 100, 200)][i % 3], 3)

    def skyline(self, L):
        sk = L["skyline"]
        for i, b in enumerate(sk["blocks"]):
            col, sh = ROOFS[i % 3]
            self.cel(b, col, sh)
        for w in sk["windows"]:
            self.fill(w, (255, 236, 170), INK, 3)
        x0, y0, x1, y1 = sk["tank"]
        self.cel([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], (120, 150, 200), (90, 110, 160))
        self.c.line(sk["antenna"], INK, 6)
        for bar in sk["antenna_bars"]:
            self.c.line(bar, INK, 5)
        self.c.line(sk["toran"], INK, 2)
        for x, y in sk["toran"][1:-1]:
            self.fill(ell(x, y + 9, 11, 11, n=14), (255, 170, 40), INK, 2)

    def birds(self, L):
        for x, y, flap in L["birds"]:
            wy = 14 * flap
            self.c.line([(x - 24, y - wy), (x, y), (x + 24, y - wy)], INK, 6)

    def rival(self, L):
        t, r, b, l = L["rival"]
        mid = ((l[0] + r[0]) / 2, (l[1] + r[1]) / 2)
        self.cel([t, r, mid, l], RIVAL, RIVAL_SH)
        self.cel([l, mid, r, b], (255, 255, 255), (200, 210, 240))
        self.fill([b, (b[0] - 18, b[1] + 34), (b[0] + 18, b[1] + 34)], RIVAL, INK, 3)

    def tail(self, L):
        pts = [L["hero"][2]] + L["tail"]
        for i in range(len(pts) - 1):
            self.c.line([pts[i], pts[i + 1]], INK, 20 - i * 0.7)
            self.c.line([pts[i], pts[i + 1]], HERO2 if i % 2 else HERO, 14 - i * 0.7)

    def hero(self, L):
        self.cel(L["hero"], HERO, HERO_SH, 6)

    def hero_face(self, L):
        c, a, k = L["hero_c"], L["hero_angle"], L["hero_s"]
        Lp = lambda x, y: local(c, a, x * k, y * k)  # noqa: E731
        for sx in (-1, 1):
            self.fill([Lp(sx * 22, -60), Lp(sx * 48, -100), Lp(sx * 40, -54)], HERO2, INK, 3)
        for sx in (-1, 1):                        # anime eyes: white, big iris, two highlights
            ex = sx * 38
            eye = [Lp(ex - 28, -10), Lp(ex - 10, -32), Lp(ex + 24, -26), Lp(ex + 28, -6), Lp(ex, 6)]
            self.fill(eye, (255, 255, 255), INK, 4)
            px, py = Lp(ex + sx * 2, -12)
            self.fill(ell(px, py, 12, 15, n=16), (255, 190, 40), INK, 2)
            self.fill(ell(px, py, 5, 7, n=10), INK, None, 0)
            self.fill(ell(px - 5, py - 6, 4, 4, n=8), (255, 255, 255), None, 0)
        mouth = [Lp(-36, 40), Lp(36, 40), Lp(20, 62), Lp(-20, 62)]
        self.fill(mouth, (140, 20, 40), INK, 3)
        for sx in (-1, 1):
            self.c.line([Lp(sx * 30, 34), Lp(sx * 70, 40), Lp(sx * 86, 64)], HERO2, 5)

    def burst(self, L):
        u = L["burst"]
        if u is None:
            return
        x, y = L["cut_pt"]
        if u < 0.34:                               # 3 black/white frames, then a red one (impact())
            self.impact(u, x, y)
            return
        self.speed_lines(x, y, n=60, r0=160 + 300 * u, r1=1600, col=(255, 255, 255), seed=int(u * 12))
        if u < 1.0:
            self.flare(x, y, toward=(540, 1400))

    def shout(self, L):
        if not L["shout"]:
            return
        u = min(1.0, L["shout_t"] / 0.2)
        x, y = L["shout_xy"]
        size = 130 * (0.6 + 0.4 * u)
        f = self.c.f("display", size)
        self.c.d.text(((x + 10) * K, (y + 12) * K), "Kaipoche!", font=f, anchor="mm", fill=INK, stroke_width=int(12 * K), stroke_fill=INK)
        self.c.d.text((x * K, y * K), "Kaipoche!", font=f, anchor="mm", fill=HERO2, stroke_width=int(10 * K), stroke_fill=INK)
        _ = math
