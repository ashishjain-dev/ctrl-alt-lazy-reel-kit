"""Mud Wall: inspired by Warli wall painting. Rice-paste white on red-brown mud; everything is built from
circles, triangles and lines (hourglass people, triangle huts, line-fan birds); a triangle-chain border.
Lines wobble at 8 fps like a hand redrawing them. The cut is a ring of dots."""
from .painter import Painter, closed, paper_texture

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


    def background(self, L):
        self.im.paste(paper_texture(self.im.width, self.im.height, MUD, 16, fibres=200, seed=12))


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
