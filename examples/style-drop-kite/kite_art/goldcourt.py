"""The kite scene painted in GoldCourt (engine style: reelkit/art/goldcourt.py)."""
import math

from reelkit.art.goldcourt import GOLD, GOLD_D, GREEN, LAPIS, LINE, MARBLE, PEARL, RED, GoldCourt, ell
from reelkit.art.painter import local
from reelkit.draw import K

from .base import KiteBase

JEWELS = [(40, 120, 100), (180, 60, 110), (60, 90, 170)]


class Kite(KiteBase, GoldCourt):
    def background(self, L):
        GoldCourt.background(self, L)
        self.hills(1320, (170, 190, 130), seed=3)
        self.hills(1400, (130, 170, 100), seed=4)
        for i, (x, y, r) in enumerate(((110, 1250, 30), (980, 1270, 34), (860, 1300, 24))):
            self.round_tree(x, y, r, i)

    def sun(self, L):
        x, y, r = L["sun"]
        self.sun_disc = (x, y, r)
        GoldCourt.sun(self, x, y, r)

    def bg_kites(self, L):
        for i, (pts, role, size) in enumerate(L["bg_kites"]):
            self.c.line([pts[2], (pts[2][0] + size * 0.5, pts[2][1] + size * 3)], LINE, 1.4)
            self.fill(pts, JEWELS[i % 3])
            self.dots(pts, GOLD, 3)

    def skyline(self, L):
        sk = L["skyline"]
        for i, b in enumerate(sk["blocks"]):        # marble havelis, a little dome on some
            self.fill(b, MARBLE if i % 2 else (240, 226, 206))
            (x0, _), (_, top), (x1, _) = b[0], b[1], b[2]
            self.c.line([(x0 + 4, top + 14), (x1 - 4, top + 14)], GOLD, 3)
            if i % 3 == 0:
                cx, r = (x0 + x1) / 2, min(60, (x1 - x0) * 0.3)
                self.fill([(cx - r, top)] + [(cx - r * math.cos(a), top - r * 1.1 * math.sin(a) ** 0.8) for a in [j * math.pi / 20 for j in range(21)]] + [(cx + r, top)], MARBLE)
                self.c.line([(cx, top - r * 1.1), (cx, top - r * 1.5)], GOLD, 4)
        for w in sk["windows"]:                      # cusped arches
            (x0, y0), (x1, _), (_, y1) = w[0], w[1], w[2]
            self.fill([(x0, y1), (x0, y0 + 10)] + [((x0 + x1) / 2 + (x1 - x0) / 2 * math.cos(a), y0 + 10 - 10 * math.sin(a)) for a in [math.pi - j * math.pi / 8 for j in range(9)]] + [(x1, y1)], RED, 1.4)
        x0, y0, x1, y1 = sk["tank"]
        self.fill([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], MARBLE)
        self.c.line(sk["toran"], LINE, 2)
        for x, y in sk["toran"][1:-1]:
            self.fill(ell(x, y + 9, 9, 11, n=12), (236, 150, 40), 1.4)

    def birds(self, L):
        self.birds_flock = [(x, y, 0.9) for x, y, flap in L["birds"]]
        GoldCourt.birds(self, self.birds_flock)

    def strings(self, L):
        for seg in L["rival_string"]:
            self.c.line(seg, LINE, 1.6)
        self.c.line(L["hero_string"], LINE, 2)

    def rival(self, L):
        t, r, b, l = L["rival"]
        mid = ((l[0] + r[0]) / 2, (l[1] + r[1]) / 2)
        self.fill([t, r, mid, l], LAPIS)
        self.fill([l, mid, r, b], PEARL)
        self.dots([t, r, b, l], GOLD, 4)
        self.fill([b, (b[0] - 16, b[1] + 30), (b[0] + 16, b[1] + 30)], LAPIS)

    def tail(self, L):
        pts = [L["hero"][2]] + L["tail"]
        for i in range(len(pts) - 1):
            self.c.line([pts[i], pts[i + 1]], GOLD if i % 2 else RED, 10 - i * 0.4)
        self.dots(pts[1::2], PEARL, 3)

    def hero(self, L):
        self.fill(L["hero"], RED)
        c, a, k = L["hero_c"], L["hero_angle"], L["hero_s"]
        inner = [local(c, a, 0, -84 * k), local(c, a, 78 * k, 0), local(c, a, 0, 112 * k), local(c, a, -78 * k, 0)]
        self.fill(inner, (196, 60, 50), 1.6, GOLD)
        edge = []
        for p, q in zip(L["hero"], L["hero"][1:] + L["hero"][:1]):
            edge += [(p[0] + (q[0] - p[0]) * u / 8, p[1] + (q[1] - p[1]) * u / 8) for u in range(8)]
        self.dots(edge, GOLD, 3.4)

    def hero_face(self, L):
        c, a, k = L["hero_c"], L["hero_angle"], L["hero_s"]
        Lp = lambda x, y: local(c, a, x * k, y * k)  # noqa: E731
        for sx in (-1, 1):
            eye = [Lp(sx * 38 - 26, -14), Lp(sx * 38, -28), Lp(sx * 38 + 26, -14), Lp(sx * 38, -2)]
            self.fill(eye, PEARL, 1.6)
            px, py = Lp(sx * 40, -14)
            self.c.ell([px - 7, py - 7, px + 7, py + 7], fill=(30, 24, 28))
            self.c.line([Lp(sx * 14, -40), Lp(sx * 38, -48), Lp(sx * 62, -38)], (30, 24, 28), 3)
        self.c.line([Lp(-30, 44), Lp(0, 52), Lp(30, 44)], GOLD, 4)
        for sx in (-1, 1):
            self.c.line([Lp(sx * 30, 30), Lp(sx * 70, 36), Lp(sx * 84, 60)], GOLD, 3)

    def burst(self, L):
        u = L["burst"]
        if u is None:
            return
        x, y = L["cut_pt"]
        if u < 0.9:
            self.gold_rays(x, y, min(1.0, u / 0.5))
            self.fill(ell(x, y, 34 + 40 * min(1, u / 0.3), 34 + 40 * min(1, u / 0.3)), GOLD)

    def shout(self, L):
        if not L["shout"]:
            return
        u = min(1.0, L["shout_t"] / 0.3)
        x, y = L["shout_xy"]
        f = self.c.f("display", 104 * (0.7 + 0.3 * u))
        self.c.d.text((x * K, y * K), "Kaipoche!", font=f, anchor="mm", fill=RED, stroke_width=int(6 * K), stroke_fill=GOLD)
        _ = GOLD_D, GREEN
