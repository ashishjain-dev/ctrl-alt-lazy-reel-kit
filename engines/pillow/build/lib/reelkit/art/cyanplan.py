"""Cyan Plan: inspired by engineering blueprints. Cyanotype blue with a grid, white line-work only,
dimension lines, callouts, the dragon kite's dashed flight path, a STRING LOCK reticle on the rival that
becomes "CUT T+2.00s", and a title block. The cut is concentric rings with tick marks."""
import math

from ..draw import K
from .painter import Painter, closed, dashed, local, paper_texture, soft_poly

BLUE = (22, 66, 140)
LINE = (232, 242, 255)
FAINT = (88, 130, 196)


class CyanPlan(Painter):
    name = "cyan-plan"
    pal = dict(Painter.pal, ink=LINE, string=LINE, text=LINE)
    brand = {"bg_top": BLUE, "bg_bottom": (16, 52, 116), "fg": LINE, "muted": (170, 196, 236), "accent": LINE,
             "highlight": (255, 214, 120), "panel": (30, 84, 168), "ink": (10, 30, 70), "good": LINE,
             "bad": (255, 200, 170), "sub_bg": (10, 36, 84), "sub_fg": LINE}
    _paths = None

    def ln(self, pts, w=3, col=LINE):
        self.c.line(pts, col, w)

    def mono(self, xy, s, size=24, anchor="lm", col=LINE):
        self.c.text(xy, s, size, "mono", col, anchor)

    def background(self, L):
        self.im.paste(paper_texture(self.im.width, self.im.height, BLUE, 7, fibres=0, seed=21))
        for x in range(0, 1081, 30):
            self.ln([(x, 0), (x, 1920)], 2.2 if x % 150 == 0 else 1, FAINT)
        for y in range(0, 1921, 30):
            self.ln([(0, y), (1080, y)], 2.2 if y % 150 == 0 else 1, FAINT)

    def sun(self, L):
        x, y, r = L["sun"]
        self.c.ell([x - r, y - r, x + r, y + r], outline=LINE, width=3)
        self.ln([(x - r - 30, y), (x + r + 30, y)], 1.5)
        self.ln([(x, y - r - 30), (x, y + r + 30)], 1.5)
        self.mono((x + r + 14, y - r - 10), "SUN  Ø 180", 20)

    def bg_kites(self, L):
        for pts, role, size in L["bg_kites"]:
            self.ln(closed(pts), 1.6, FAINT)
            self.ln([pts[0], pts[2]], 1, FAINT)

    def skyline(self, L):
        sk = L["skyline"]
        for i, b in enumerate(sk["blocks"]):
            self.ln(b, 3)
            (x0, _), (_, top), (x1, _) = b[0], b[1], b[2]
            for yy in range(int(top) + 24, 1920, 24):                # section hatch
                self.ln([(x0 + 4, yy), (x0 + 30, yy - 24)], 1, FAINT)
        for w in sk["windows"]:
            self.ln(closed(w), 2)
        x0, y0, x1, y1 = sk["tank"]
        self.ln(closed([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), 3)
        self.ln([(x0, y0 - 24), (x1, y0 - 24)], 1.5)
        self.ln([(x0, y0 - 34), (x0, y0 - 14)], 1.5)
        self.ln([(x1, y0 - 34), (x1, y0 - 14)], 1.5)
        self.mono(((x0 + x1) / 2, y0 - 44), "TANK 1.5 m", 20, "mm")
        self.ln(sk["antenna"], 3)
        for bar in sk["antenna_bars"]:
            self.ln(bar, 2)
        self.ln(sk["toran"], 2)
        for x, y in sk["toran"][1:-1]:
            self.c.ell([x - 6, y + 2, x + 6, y + 14], outline=LINE, width=2)

    def birds(self, L):
        for x, y, flap in L["birds"]:
            wy = 12 * flap
            self.ln([(x - 20, y - wy), (x, y), (x + 20, y - wy)], 2.5)

    def strings(self, L):
        # dashed design path of the dragon kite
        if CyanPlan._paths is None:
            from . import kite
            CyanPlan._paths = [kite.hero_pos(i * 0.1) for i in range(51)]
        dashed(self.c, CyanPlan._paths, FAINT, 2.5, 14, 10)
        for seg in L["rival_string"]:
            self.ln(seg, 2)
        self.ln(L["hero_string"], 2.5)
        if L["hero_string"]:
            x, y = L["hero_string"][len(L["hero_string"]) // 3]
            self.mono((x + 16, y), "MANJA  0.6 mm", 20)

    def rival(self, L):
        self.ln(closed(L["rival"]), 3)
        t, r, b, l = L["rival"]
        self.ln([l, r], 2)
        self.ln([t, b], 2)
        rx, ry = L["rival_c"]
        tt = L["t"]
        # reticle: locks on before the cut, then reads CUT
        rr = 120 + 20 * math.sin(tt * 6) if not L["cut"] else 120
        self.c.ell([rx - rr, ry - rr, rx + rr, ry + rr], outline=LINE, width=2)
        for q in range(4):
            a = q * math.pi / 2 + (0 if L["cut"] else tt)
            self.ln([(rx + rr * math.cos(a), ry + rr * math.sin(a)), (rx + (rr + 26) * math.cos(a), ry + (rr + 26) * math.sin(a))], 3)
        label = "STRING LOCK" if not L["cut"] else "CUT  T+2.00s"
        self.mono((rx, ry - rr - 28), label, 24, "mm", (255, 214, 120) if L["cut"] else LINE)

    def tail(self, L):
        pts = [L["hero"][2]] + L["tail"]
        self.ln(pts, 3)
        for x, y in pts[1::2]:
            self.ln([(x - 8, y), (x + 8, y)], 2)

    def hero(self, L):
        h = L["hero"]
        self.ln(closed(h), 4)
        self.ln([h[0], h[2]], 2)
        self.ln([h[1], h[3]], 2)
        # dimension line below the kite: span of the cross spar
        xl, xr = min(h[1][0], h[3][0]), max(h[1][0], h[3][0])
        yd = h[2][1] + 30
        self.ln([(xl, yd), (xr, yd)], 1.5)
        self.ln([(xl, yd - 12), (xl, yd + 12)], 1.5)
        self.ln([(xr, yd - 12), (xr, yd + 12)], 1.5)
        self.mono(((xl + xr) / 2 + 70, yd + 22), "W = 0.75 m", 20, "lm")
        cx, cy = h[3]
        self.ln([(cx, cy), (cx - 40, cy - 90), (cx - 60, cy - 90)], 1.5)
        self.mono((cx - 64, cy - 90), "DRAGON KITE MK-I", 22, "rm")

    def hero_face(self, L):
        c, a, k = L["hero_c"], L["hero_angle"], L["hero_s"]
        Lp = lambda x, y: local(c, a, x * k, y * k)  # noqa: E731
        head = [Lp(-50, -28), Lp(0, -52), Lp(50, -28), Lp(42, 46), Lp(0, 66), Lp(-42, 46)]
        self.ln(closed(head), 2.5)
        for sx in (-1, 1):
            self.ln([Lp(sx * 16, -42), Lp(sx * 36, -84), Lp(sx * 32, -38)], 2.5)
            ex, ey = Lp(sx * 22, -8)
            self.c.ell([ex - 10, ey - 10, ex + 10, ey + 10], outline=LINE, width=2)
            self.c.ell([ex - 3, ey - 3, ex + 3, ey + 3], fill=LINE)
        self.ln([Lp(-24, 36), Lp(0, 46), Lp(24, 36)], 2.5)

    def burst(self, L):
        u = L["burst"]
        if u is None:
            return
        x, y = L["cut_pt"]
        for k in range(3):
            r = (30 + 230 * min(1, u / 0.5)) * (0.4 + 0.3 * k)
            self.c.ell([x - r, y - r, x + r, y + r], outline=LINE, width=3 - k * 0.6)
        R = 40 + 260 * min(1, u / 0.5)
        for i in range(24):
            q = i * math.pi / 12
            self.ln([(x + R * math.cos(q), y + R * math.sin(q)), (x + (R + 18) * math.cos(q), y + (R + 18) * math.sin(q))], 2)
        if u < 0.25:
            soft_poly(self.im, [(x + 60 * math.cos(q), y + 60 * math.sin(q)) for q in [j * 0.63 for j in range(10)]], LINE, 0.9 - 3 * u, 4)
        self.mono((x + 30, y + 40), "IMPACT", 22)

    def shout(self, L):
        if not L["shout"]:
            return
        x, y = 780, L["shout_xy"][1]
        n = min(10, int(L["shout_t"] * 30))                 # typed in like a drawing note
        self.mono((x, y), "KAIPOCHE!"[:n], 64, "mm")

    def reel_overlay(self):
        self.c.line(closed([(20, 20), (1060, 20), (1060, 1900), (20, 1900)]), LINE, 3)

    def overlay(self, L):
        # title block, top-left (inside the safe zone)
        x0, y0, x1, y1 = 70, 250 if L else 120, 520, 250 + 150 if L else 270
        self.ln(closed([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), 3)
        self.ln([(x0, y0 + 50), (x1, y0 + 50)], 2)
        self.ln([(x0 + 220, y0 + 50), (x0 + 220, y1)], 2)
        self.mono((x0 + 16, y0 + 25), "PROJECT: KAIPOCHE", 24)
        self.mono((x0 + 16, y0 + 80), "SHEET 1 / 1", 20)
        self.mono((x0 + 16, y0 + 115), "SCALE 1:20", 20)
        self.mono((x0 + 236, y0 + 80), "MAKAR SANKRANTI", 20)
        self.mono((x0 + 236, y0 + 115), "REV A", 20)
        self.c.line(closed([(20, 20), (1060, 20), (1060, 1900), (20, 1900)]), LINE, 3)


_ = K
