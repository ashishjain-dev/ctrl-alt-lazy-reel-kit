"""Mud Wall: inspired by Warli wall painting. Rice-paste white on red-brown mud; everything is built from
circles, triangles and lines (hourglass people, triangle huts, line-fan birds); a triangle-chain border.
Lines wobble at 8 fps like a hand redrawing them. The cut is a ring of dots."""
import math

from .painter import Painter, closed, local, paper_texture

MUD = (146, 70, 46)
WHITE = (246, 238, 224)


class MudWall(Painter):
    name = "mud-wall"
    fps = 8
    jitter = 2.2
    pal = dict(Painter.pal, ink=WHITE, string=WHITE, text=WHITE)
    brand = {"bg_top": MUD, "bg_bottom": (126, 58, 38), "fg": WHITE, "muted": (232, 200, 180), "accent": WHITE,
             "highlight": (246, 214, 150), "panel": (118, 52, 34), "ink": (60, 26, 16), "good": WHITE,
             "bad": (255, 220, 200), "sub_bg": (90, 38, 24), "sub_fg": WHITE}

    def ln(self, pts, w=4, seed=0):
        self.c.line(self.j(pts, self.t, seed=seed), WHITE, w)

    def tri(self, pts, fill=True, seed=0):
        p = self.j(pts, self.t, seed=seed)
        if fill:
            self.c.poly(p, WHITE)
        else:
            self.c.line(closed(p), WHITE, 3.5)

    def person(self, x, y, s=1.0, arms_up=False, seed=0):
        """Warli figure: two triangles meeting at the waist, circle head, stick limbs. (x, y) = feet."""
        S = lambda v: v * s  # noqa: E731
        waist = (x, y - S(60))
        self.tri([(x - S(22), y - S(28)), (x + S(22), y - S(28)), waist], seed=seed)                    # hips
        self.tri([(x - S(26), y - S(100)), (x + S(26), y - S(100)), waist], seed=seed + 1)              # chest
        hx, hy = x, y - S(118)
        self.c.ell([hx - S(14), hy - S(14), hx + S(14), hy + S(14)], fill=WHITE)
        self.ln([(x - S(12), y - S(28)), (x - S(20), y)], 3.5, seed)                                    # legs
        self.ln([(x + S(12), y - S(28)), (x + S(22), y)], 3.5, seed + 1)
        if arms_up:
            self.ln([(x - S(24), y - S(98)), (x - S(40), y - S(140))], 3.5, seed + 2)
            self.ln([(x + S(24), y - S(98)), (x + S(44), y - S(138))], 3.5, seed + 3)
        else:
            self.ln([(x - S(24), y - S(98)), (x - S(40), y - S(66))], 3.5, seed + 2)
            self.ln([(x + S(24), y - S(98)), (x + S(40), y - S(66))], 3.5, seed + 3)

    def paint(self, L):
        self.t = L.get("t", 0)
        super().paint(L)

    def background(self, L):
        self.im.paste(paper_texture(self.im.width, self.im.height, MUD, 16, fibres=200, seed=12))

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

    def overlay(self, L):
        W, H, b = 1080, 1920, 30
        for i in range(27):                          # triangle chain border, top and bottom
            x0, x1 = i * W / 27, (i + 1) * W / 27
            self.c.poly([(x0, 8), (x1, 8), ((x0 + x1) / 2, b)], WHITE)
            self.c.poly([(x0, H - 8), (x1, H - 8), ((x0 + x1) / 2, H - b)], WHITE)
        for i in range(48):
            y0, y1 = i * H / 48, (i + 1) * H / 48
            self.c.poly([(8, y0), (8, y1), (b, (y0 + y1) / 2)], WHITE)
            self.c.poly([(W - 8, y0), (W - 8, y1), (W - b, (y0 + y1) / 2)], WHITE)

    def reel_overlay(self):
        self.t = 0
        self.overlay({})
