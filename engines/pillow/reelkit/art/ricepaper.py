"""Rice Paper: inspired by East Asian ink-wash painting. Grey washes that darken where they overlap,
dry-brush streaks, soft ink bleed, rooftops fading into mist. The only colour is vermilion (sun and
a seal). The cut is an ink splatter plus one fast brush arc."""
import math
import random

from PIL import Image, ImageDraw

from ..draw import K
from .painter import Painter, local, paper_texture, soft_poly

PAPER = (236, 231, 218)
INK = (22, 22, 26)
VERM = (196, 48, 36)


class RicePaper(Painter):
    name = "rice-paper"
    pal = dict(Painter.pal, ink=INK, string=(60, 60, 64), text=INK)
    brand = {"bg_top": PAPER, "bg_bottom": PAPER, "fg": INK, "muted": (110, 108, 104), "accent": VERM,
             "highlight": (200, 196, 186), "panel": (222, 216, 202), "ink": INK, "good": (70, 70, 74),
             "bad": VERM, "sub_bg": (32, 32, 36), "sub_fg": PAPER}

    def wash(self, pts, a=0.25, blur=3):
        soft_poly(self.im, pts, INK, a, blur)

    def stroke(self, pts, w, a=0.85, blur=0.6):
        soft_poly(self.im, pts, INK, a, blur, width=w)

    def background(self, L):
        self.im.paste(paper_texture(self.im.width, self.im.height, PAPER, 6, fibres=900, seed=8))
        # far misty peaks
        for k, (base, amp, a) in enumerate(((980, 160, 0.10), (1120, 120, 0.14))):
            pts = [(-20, 1920)] + [(x, base - amp * abs(math.sin(x / (210 + 60 * k) + k))) for x in range(-20, 1120, 40)] + [(1100, 1920)]
            self.wash(pts, a, 14)

    def sun(self, L):
        x, y, r = L["sun"]
        soft_poly(self.im, [(x + r * math.cos(a / 20 * math.pi), y + r * math.sin(a / 20 * math.pi)) for a in range(40)], VERM, 0.9, 1.2)

    def bg_kites(self, L):
        for pts, role, size in L["bg_kites"]:
            self.wash(pts, 0.35, 1.5)
            self.stroke([pts[2], (pts[2][0] + size * 0.5, pts[2][1] + size * 3)], 1.2, 0.4, 0)

    def skyline(self, L):
        sk = L["skyline"]
        for i, b in enumerate(sk["blocks"]):
            self.wash(b, 0.30 + 0.08 * (i % 3), 6)          # overlapping washes get darker
            top = b[1][1]
            self.stroke([(b[1][0] + 6, top), (b[2][0] - 6, top + 4)], 6, 0.7, 1)
        for w in sk["windows"]:
            self.wash(w, 0.45, 2)
        x0, y0, x1, y1 = sk["tank"]
        self.wash([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 0.55, 2)
        self.stroke([(x0, y0), (x1, y0)], 6, 0.9)
        self.stroke(sk["antenna"], 5, 0.85)
        for bar in sk["antenna_bars"]:
            self.stroke(bar, 4, 0.8)
        self.stroke(sk["toran"], 2, 0.5)
        for x, y in sk["toran"][1:-1]:
            self.wash([(x - 9, y), (x + 9, y), (x + 9, y + 16), (x - 9, y + 16)], 0.6, 2)
        # dry-brush streaks across the roofs
        rnd = random.Random(4)
        for _ in range(9):
            y = rnd.uniform(1480, 1880)
            x = rnd.uniform(-50, 700)
            self.stroke([(x, y), (x + rnd.uniform(200, 420), y + rnd.uniform(-8, 8))], rnd.uniform(3, 9), 0.25, 0.4)

    def birds(self, L):
        for x, y, flap in L["birds"]:
            wy = 16 * flap
            self.stroke([(x - 26, y - wy), (x - 8, y - 2), (x, y + 2)], 5, 0.9)
            self.stroke([(x, y + 2), (x + 10, y - 2), (x + 26, y - wy)], 5, 0.9)

    def strings(self, L):
        for seg in L["rival_string"]:
            self.stroke(seg, 2, 0.6, 0)
        self.stroke(L["hero_string"], 2.5, 0.7, 0)

    def rival(self, L):
        t, r, b, l = L["rival"]
        mid = ((l[0] + r[0]) / 2, (l[1] + r[1]) / 2)
        self.wash([t, r, mid, l], 0.6, 1.5)
        self.wash([l, mid, r, b], 0.22, 1.5)
        self.stroke([t, r, b, l, t], 3, 0.85)

    def tail(self, L):
        pts = [L["hero"][2]] + L["tail"]
        for i in range(len(pts) - 1):            # tapering brush stroke
            self.stroke([pts[i], pts[i + 1]], max(2, 14 - i), 0.8, 0.8)

    def hero(self, L):
        self.wash(L["hero"], 0.18, 2)
        h = L["hero"]
        self.stroke([h[0], h[1], h[2]], 7, 0.95, 0.8)        # two confident brush strokes for the frame
        self.stroke([h[2], h[3], h[0]], 5, 0.85, 0.8)
        self.stroke([h[0], h[2]], 3, 0.6, 0.5)
        self.stroke([h[1], h[3]], 3, 0.6, 0.5)

    def hero_face(self, L):
        c, a, k = L["hero_c"], L["hero_angle"], L["hero_s"]
        Lp = lambda x, y: local(c, a, x * k, y * k)  # noqa: E731
        for sx in (-1, 1):
            self.stroke([Lp(sx * 18, -40), Lp(sx * 34, -70), Lp(sx * 46, -86)], 5, 0.9)      # horns
            self.stroke([Lp(sx * 36, -16), Lp(sx * 22, -22), Lp(sx * 8, -14)], 5, 0.95)      # brows
            ex, ey = Lp(sx * 22, -8)
            soft_poly(self.im, [(ex + 7 * math.cos(q), ey + 7 * math.sin(q)) for q in [i * 0.63 for i in range(10)]], INK, 0.95, 0.5)
            self.stroke([Lp(sx * 26, 30), Lp(sx * 60, 36), Lp(sx * 84, 60), Lp(sx * 92, 90)], 3, 0.7)  # whiskers
        self.stroke([Lp(-28, 40), Lp(-10, 50), Lp(10, 50), Lp(28, 40)], 5, 0.9)
        self.stroke([Lp(-8, 14), Lp(-4, 20)], 4, 0.9)                                                  # nostrils
        self.stroke([Lp(8, 14), Lp(4, 20)], 4, 0.9)
        for i in range(5):                                                                              # teeth
            self.stroke([Lp(-20 + i * 10, 44), Lp(-16 + i * 10, 52)], 3, 0.8)
        self.wash([Lp(0, -80), Lp(64, -10), Lp(0, 90), Lp(-64, -10)], 0.10, 6)

    def burst(self, L):
        u = L["burst"]
        if u is None:
            return
        x, y = L["cut_pt"]
        rnd = random.Random(9)
        g = min(1, u / 0.15)
        for i in range(26):                       # ink splatter: blobs flung outward
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(10, 260) * g
            r = rnd.uniform(5, 30) * (1 - 0.5 * d / 260)
            bx, by = x + math.cos(a) * d, y + math.sin(a) * d
            soft_poly(self.im, [(bx + r * math.cos(q), by + r * math.sin(q)) for q in [j * 0.7 for j in range(9)]], INK, 0.9, 0.8)
        if u < 0.5:                                # one fast brush arc
            arc = [(x + 170 * math.cos(q), y + 170 * math.sin(q)) for q in [math.pi * (0.9 + 0.08 * j) for j in range(int(2 + 14 * min(1, u / 0.2)))]]
            if len(arc) > 1:
                self.stroke(arc, 14, 0.9, 1)

    def shout(self, L):
        if not L["shout"]:
            return
        u = min(1.0, L["shout_t"] / 0.3)
        a = int(255 * u)
        f = self.c.f("display", 104)
        x, y = L["shout_xy"]
        lay = Image.new("L", (int(900 * K), int(200 * K)), 0)
        ImageDraw.Draw(lay).text((lay.width // 2, lay.height // 2), "Kaipoche!", font=f, fill=a, anchor="mm")
        self.im.paste(INK, (int(x * K - lay.width / 2), int(y * K - lay.height / 2)), lay)

    def reel_overlay(self):
        pass                      # the KITE seal belongs to the kite scene only

    def overlay(self, L):
        # red seal, bottom right of the sky
        x, y = (70, 1300) if L else (70, 1700)
        soft_poly(self.im, [(x, y), (x + 90, y), (x + 90, y + 90), (x, y + 90)], VERM, 0.92, 0.6)
        self.c.text((x + 45, y + 32), "KI", 34, "display", PAPER)
        self.c.text((x + 45, y + 64), "TE", 34, "display", PAPER)
