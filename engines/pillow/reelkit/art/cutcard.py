"""Cut Card: inspired by layered paper cut-out animation. Coloured card with soft drop shadows and thin
white cut edges, wavy paper sky strips, stacked cloud strips, stop motion at 12 fps with a tiny jitter.
The cut is a paper starburst."""
import math

from .painter import Painter, closed, local, paper_texture, shadow_poly

SKY = [(150, 206, 232), (176, 220, 238), (204, 232, 240), (238, 222, 200), (246, 200, 170)]
EDGE = (255, 255, 255)
CARD = {"hero": (232, 74, 60), "hero2": (255, 196, 64), "face": (86, 170, 110), "rival": (70, 110, 200),
        "rival2": (255, 238, 200), "roof": [(214, 120, 104), (122, 150, 196), (236, 186, 110), (150, 120, 170), (110, 170, 150)],
        "tank": (90, 120, 170), "sun": (255, 214, 92), "cloud": (255, 255, 255), "bird": (60, 60, 80),
        "bg": [(240, 110, 140), (110, 190, 140), (140, 120, 220)], "marigold": (255, 170, 40)}


class CutCard(Painter):
    name = "cut-card"
    fps = 12
    jitter = 1.6
    brand = {"bg_top": SKY[0], "bg_bottom": SKY[-1], "fg": (40, 40, 56), "muted": (90, 96, 120),
             "accent": CARD["hero"], "highlight": CARD["hero2"], "panel": (255, 250, 240), "ink": (40, 40, 56),
             "good": (60, 150, 100), "bad": CARD["hero"], "sub_bg": (255, 252, 244), "sub_fg": (40, 40, 56)}

    def card(self, pts, col, depth=1.0, seed=0):
        p = self.j(pts, self.t, seed=seed)
        shadow_poly(self.im, p, (8 * depth, 12 * depth), 0.35, 5 * depth)
        self.c.poly(p, col)
        self.c.line(closed(p), EDGE, 2.5)

    def paint(self, L):
        self.t = L.get("t", 0)
        super().paint(L)

    def background(self, L):
        self.t = getattr(self, "t", 0)
        self.im.paste(paper_texture(self.im.width, self.im.height, SKY[0], 5, seed=31))
        for k, col in enumerate(SKY[1:]):                      # wavy paper strips, lower = warmer
            base = 380 + k * 300
            pts = [(-20, 1940)] + [(x, base + 26 * math.sin(x / 140 + k * 1.7)) for x in range(-20, 1121, 40)] + [(1100, 1940)]
            shadow_poly(self.im, pts, (0, -6), 0.18, 6)
            self.c.poly(pts, col)
        for cx, cy, s in ((230, 560, 1.0), (820, 820, 0.8), (380, 1060, 0.7)):   # stacked cloud strips
            for layer in range(2):
                yy = cy + layer * 34 * s
                bumps = [(cx + (i - 2) * 70 * s, yy) for i in range(5)]
                pts = [(cx - 190 * s, yy + 40 * s)]
                for bx, by in bumps:
                    pts += [(bx + 40 * s * math.cos(q), by - 40 * s * abs(math.sin(q))) for q in [math.pi - j * 0.4 for j in range(9)]]
                pts += [(cx + 190 * s, yy + 40 * s)]
                self.card(pts, (255, 255, 255) if layer else (236, 244, 250), 0.6, seed=int(cx) + layer)

    def sun(self, L):
        x, y, r = L["sun"]
        pts = [(x + (r + (16 if i % 2 else 0)) * math.cos(i * math.pi / 12), y + (r + (16 if i % 2 else 0)) * math.sin(i * math.pi / 12)) for i in range(24)]
        self.card(pts, CARD["sun"], 0.8, 1)

    def bg_kites(self, L):
        for i, (pts, role, size) in enumerate(L["bg_kites"]):
            self.c.line([pts[2], (pts[2][0] + size * 0.5, pts[2][1] + size * 3)], (90, 90, 110), 1.5)
            self.card(pts, CARD["bg"][i % 3], 0.5, 10 + i)

    def skyline(self, L):
        sk = L["skyline"]
        for i, b in enumerate(sk["blocks"]):
            self.card(b, CARD["roof"][i % 5], 1.2, 20 + i)
        for i, w in enumerate(sk["windows"]):
            self.card(w, (255, 236, 180), 0.4, 40 + i)
        x0, y0, x1, y1 = sk["tank"]
        self.card([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], CARD["tank"], 1.0, 60)
        self.c.line(self.j(sk["antenna"], self.t, seed=61), (60, 60, 80), 6)
        for bar in sk["antenna_bars"]:
            self.c.line(bar, (60, 60, 80), 5)
        self.c.line(sk["toran"], (60, 60, 80), 2)
        for k, (x, y) in enumerate(sk["toran"][1:-1]):
            petals = [(x + 12 * math.cos(q), y + 10 + 12 * math.sin(q)) for q in [j * 0.7 for j in range(9)]]
            self.card(petals, CARD["marigold"] if k % 2 else (240, 100, 60), 0.3, 70 + k)

    def birds(self, L):
        for i, (x, y, flap) in enumerate(L["birds"]):
            wy = 18 * flap
            self.card([(x - 26, y - wy), (x, y + 4), (x + 26, y - wy), (x, y - 6)], CARD["bird"], 0.4, 80 + i)

    def strings(self, L):
        for seg in L["rival_string"]:
            self.c.line(seg, (70, 70, 90), 2)
        self.c.line(L["hero_string"], (70, 70, 90), 2.5)

    def rival(self, L):
        t, r, b, l = L["rival"]
        mid = ((l[0] + r[0]) / 2, (l[1] + r[1]) / 2)
        self.card(L["rival"], CARD["rival2"], 1.0, 90)
        self.card([t, r, mid, l], CARD["rival"], 0.3, 91)
        self.card([b, (b[0] - 18, b[1] + 34), (b[0] + 18, b[1] + 34)], CARD["rival"], 0.5, 92)

    def tail(self, L):
        pts = [L["hero"][2]] + L["tail"]
        for i in range(1, len(pts)):
            x, y = pts[i]
            s = 16 - i * 0.7
            self.card([(x - s, y - s * 0.6), (x, y - s * 0.1), (x + s, y - s * 0.6), (x + s * 0.6, y + s * 0.5), (x - s * 0.6, y + s * 0.5)],
                      CARD["hero2"] if i % 2 else CARD["hero"], 0.4, 100 + i)

    def hero(self, L):
        self.card(L["hero"], CARD["hero"], 1.4, 120)
        c, a, k = L["hero_c"], L["hero_angle"], L["hero_s"]
        inner = [local(c, a, 0, -84 * k), local(c, a, 78 * k, 0), local(c, a, 0, 112 * k), local(c, a, -78 * k, 0)]
        self.card(inner, CARD["hero2"], 0.5, 121)

    def hero_face(self, L):
        c, a, k = L["hero_c"], L["hero_angle"], L["hero_s"]
        Lp = lambda x, y: local(c, a, x * k, y * k)  # noqa: E731
        for sx in (-1, 1):
            self.card([Lp(sx * 14, -40), Lp(sx * 36, -86), Lp(sx * 32, -36)], (255, 240, 220), 0.4, 130 + sx)
        head = [Lp(-52, -30), Lp(0, -54), Lp(52, -30), Lp(44, 48), Lp(0, 70), Lp(-44, 48)]
        self.card(head, CARD["face"], 0.6, 133)
        for sx in (-1, 1):
            ex, ey = Lp(sx * 22, -8)
            self.card([(ex + 14 * math.cos(q), ey + 11 * math.sin(q)) for q in [j * 0.7 for j in range(9)]], (255, 255, 255), 0.2, 134 + sx)
            self.c.ell([ex - 5, ey - 5, ex + 5, ey + 5], fill=(30, 30, 40))
        self.card([Lp(-26, 30), Lp(26, 30), Lp(0, 50)], (200, 50, 50), 0.2, 137)

    def burst(self, L):
        u = L["burst"]
        if u is None:
            return
        x, y = L["cut_pt"]
        g = min(1, u / 0.25) * (1 - 0.3 * max(0, u - 0.5))
        for k, (col, rm) in enumerate(((CARD["hero2"], 1.0), ((255, 255, 255), 0.6), (CARD["hero"], 0.32))):
            r = (80 + 220 * g) * rm
            pts = [(x + (r if i % 2 == 0 else r * 0.55) * math.cos(i * math.pi / 9 + k * 0.2),
                    y + (r if i % 2 == 0 else r * 0.55) * math.sin(i * math.pi / 9 + k * 0.2)) for i in range(18)]
            if u < 0.85:
                self.card(pts, col, 1.0 - 0.3 * k, 140 + k)

    def shout(self, L):
        if not L["shout"]:
            return
        u = min(1.0, L["shout_t"] / 0.25)
        x, y = L["shout_xy"]
        jx, jy = self.j([(0, 0)], self.t, 2)[0]
        size = 112 * (0.5 + 0.5 * u)
        from ..draw import K
        f = self.c.f("display", size)
        self.c.d.text(((x + 8 + jx) * K, (y + 12 + jy) * K), "Kaipoche!", font=f, anchor="mm", fill=(0, 0, 0, 90),
                      stroke_width=int(10 * K), stroke_fill=(120, 120, 130))
        self.c.d.text(((x + jx) * K, (y + jy) * K), "Kaipoche!", font=f, anchor="mm", fill=CARD["hero"],
                      stroke_width=int(10 * K), stroke_fill=EDGE)
