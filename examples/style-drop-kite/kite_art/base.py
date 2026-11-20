"""Kite painting shared by every style: the default (flat) look of each part of the kite scene and the
draw order. Each style module overrides the parts it paints differently."""
import math



from reelkit.art.painter import Painter, closed, local  # noqa: F401
from reelkit.draw import K


class KiteBase(Painter):
    def sun(self, L):
        x, y, r = L["sun"]
        self.c.ell([x - r, y - r, x + r, y + r], fill=self.P("sun"))

    def bg_kites(self, L):
        for pts, role, size in L["bg_kites"]:
            self.c.line([pts[2], (pts[2][0] + size * 0.5, pts[2][1] + size * 3)], self.P("string"), 1.5)
            self.shape(pts, self.P(role))

    def skyline(self, L):
        sk = L["skyline"]
        for i, b in enumerate(sk["blocks"]):
            self.shape(b, self.P("roof" if i % 2 else "roof2"))
        for w in sk["windows"]:
            self.shape(w, self.P("sky_bottom"))
        x0, y0, x1, y1 = sk["tank"]
        self.c.rr([x0, y0, x1, y1], 14, fill=self.P("tank"))
        self.c.line(sk["antenna"], self.P("ink"), 6)
        for bar in sk["antenna_bars"]:
            self.c.line(bar, self.P("ink"), 5)
        self.c.line(sk["toran"], self.P("string"), 2)
        for i, (x, y) in enumerate(sk["toran"][1:-1]):
            self.c.ell([x - 11, y - 2, x + 11, y + 20], fill=self.P("marigold"))

    def birds(self, L):
        for x, y, flap in L["birds"]:
            wy = 14 * flap
            self.c.line([(x - 22, y - wy), (x, y), (x + 22, y - wy)], self.P("bird"), 5)

    def strings(self, L):
        for seg in L["rival_string"]:
            self.c.line(seg, self.P("string"), 2.5)
        self.c.line(L["hero_string"], self.P("string"), 3)

    def rival(self, L):
        t, r, b, l = L["rival"]
        mid = ((l[0] + r[0]) / 2, (l[1] + r[1]) / 2)
        self.shape([t, r, mid, l], self.P("rival"))
        self.shape([l, mid, r, b], self.P("rival2"))
        self.c.poly([b, (b[0] - 18, b[1] + 34), (b[0] + 18, b[1] + 34)], self.P("rival"))
        self.c.line(closed(L["rival"]), self.P("ink"), 3)

    def tail(self, L):
        pts = [L["hero"][2]] + L["tail"]
        for i in range(len(pts) - 1):
            self.c.line([pts[i], pts[i + 1]], self.P("tail" if i % 2 else "tail2"), 16 - i * 0.7)

    def hero(self, L):
        self.shape(L["hero"], self.P("hero"), self.P("ink"), 5)

    def hero_face(self, L):
        """Dragon face painted on the hero kite, in kite-local coordinates."""
        c, a = L["hero_c"], L["hero_angle"]
        k = L["hero_s"]
        Lp = lambda x, y: local(c, a, x * k, y * k)  # noqa: E731
        ink, h2 = self.P("ink"), self.P("hero2")
        for sx in (-1, 1):   # horns
            self.c.poly([Lp(sx * 22, -60), Lp(sx * 46, -96), Lp(sx * 40, -54)], h2)
        for sx in (-1, 1):   # almond eyes
            ex = sx * 38
            eye = [Lp(ex - 26, -14), Lp(ex, -30), Lp(ex + 26, -14), Lp(ex, 2)]
            self.c.poly(eye, (250, 246, 236))
            self.c.line(closed(eye), ink, 3)
            px, py = Lp(ex + sx * 4, -14)
            self.c.ell([px - 8, py - 8, px + 8, py + 8], fill=ink)
        for sx in (-1, 1):   # nostrils
            nx, ny = Lp(sx * 12, 26)
            self.c.ell([nx - 5, ny - 5, nx + 5, ny + 5], fill=ink)
        teeth = [Lp(-40 + i * 10, 52 + (8 if i % 2 else 0)) for i in range(9)]
        self.c.line(teeth, ink, 3)
        for sx in (-1, 1):   # whiskers
            self.c.line([Lp(sx * 30, 34), Lp(sx * 70, 40), Lp(sx * 86, 64)], h2, 4)

    def burst(self, L):
        u = L["burst"]
        if u is None:
            return
        x, y = L["cut_pt"]
        r = 40 + 220 * min(1, u / 0.35)
        fade = max(0.0, 1 - u / 0.9)
        n = 12
        pts = []
        for i in range(2 * n):
            rr = r if i % 2 == 0 else r * 0.45
            a = math.pi * i / n + u * 0.8
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        if fade > 0:
            self.c.poly(pts, self.P("burst2"))
            self.c.ell([x - r * 0.3, y - r * 0.3, x + r * 0.3, y + r * 0.3], fill=self.P("burst"))
        self.sparkles(L)

    def sparkles(self, L):
        u = L["burst"]
        x, y = L["cut_pt"]
        for i in range(14):
            a = i * 2.39996
            d = 60 + 380 * u
            sx, sy = x + math.cos(a) * d, y + math.sin(a) * d + 120 * u * u
            s = 10 * (1 - u)
            if s > 1:
                self.c.poly([(sx, sy - s), (sx + s * 0.6, sy), (sx, sy + s), (sx - s * 0.6, sy)], self.P("burst"))

    def shout(self, L):
        if not L["shout"]:
            return
        u = min(1.0, L["shout_t"] / 0.25)
        size = 120 * (0.4 + 0.6 * u) * (1 + 0.06 * math.sin(L["shout_t"] * 9))
        self.text_shout("Kaipoche!", L["shout_xy"], size)

    def text_shout(self, s, xy, size, fill=None, stroke=None, kind="display", sw=8):
        f = self.c.f(kind, size)
        self.c.d.text((int(xy[0] * K), int(xy[1] * K)), s, font=f, fill=fill or self.P("text"), anchor="mm",
                      stroke_width=int(sw * K), stroke_fill=stroke or self.P("ink"))

    def paint(self, L):
        self.t = L.get("t", 0)
        for part in (self.background, self.sun, self.bg_kites, self.skyline, self.birds, self.strings,
                     self.rival, self.tail, self.hero, self.hero_face, self.burst, self.shout, self.overlay):
            part(L)
