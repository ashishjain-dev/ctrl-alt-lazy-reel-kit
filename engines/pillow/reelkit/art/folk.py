"""Fish-Scale Folk: inspired by Mithila folk painting. Handmade paper, double ink outlines with a paper
gap, flat vermilion / turmeric / leaf / indigo, fish-scale, dot and hatch fills, almond eyes, a rayed sun
with a face, and a red border of yellow triangles. The cut is a red and yellow star burst."""
from PIL import Image

from ..draw import K
from .painter import Painter, closed, fill_pattern, paper_texture, tile

PAPER = (241, 227, 196)
INK = (34, 24, 20)
VERM = (205, 52, 34)
TURM = (232, 166, 28)
LEAF = (62, 132, 70)
INDIGO = (44, 60, 128)
PINK = (222, 118, 136)


class FishScaleFolk(Painter):
    name = "fish-scale-folk"
    pal = dict(Painter.pal, ink=INK, string=INK, hero=VERM, hero2=TURM, rival=INDIGO, rival2=TURM,
               tail=TURM, tail2=VERM, bird=INK, bgk1=VERM, bgk2=LEAF, bgk3=INDIGO, marigold=TURM,
               burst=TURM, burst2=VERM, text=VERM, sun=TURM)
    brand = {"bg_top": PAPER, "bg_bottom": PAPER, "fg": INK, "muted": (120, 96, 80), "accent": VERM,
             "highlight": TURM, "panel": (232, 214, 178), "ink": INK, "good": LEAF, "bad": VERM,
             "sub_bg": INK, "sub_fg": PAPER}

    def dbl(self, pts, w=7, is_closed=True):
        """Mithila double outline: thick ink, a paper-coloured gap, thin ink inside."""
        p = closed(pts) if is_closed else pts
        self.c.line(p, INK, w)
        self.c.line(p, PAPER, w * 0.42)

    def folk_shape(self, pts, fill, pattern=None, pcol=INK, w=7, psize=34):
        self.c.poly(pts, fill)
        if pattern:
            fill_pattern(self.im, pts, tile(pattern, pcol, None, psize, 2.4))
        self.dbl(pts, w)

    def background(self, L):
        self.im.paste(paper_texture(self.im.width, self.im.height, PAPER, 9, fibres=400))


    def overlay(self, L):
        """Red border with yellow triangles, double-lined."""
        W, H, b = 1080, 1920, 34
        for box in ([0, 0, W, b], [0, H - b, W, H], [0, 0, b, H], [W - b, 0, W, H]):
            self.c.d.rectangle([int(v * K) for v in box], fill=VERM)
        n = 24
        for i in range(n):                    # top and bottom rows of triangles
            x0, x1 = i * W / n, (i + 1) * W / n
            self.c.poly([(x0, 0), (x1, 0), ((x0 + x1) / 2, b)], TURM)
            self.c.poly([(x0, H), (x1, H), ((x0 + x1) / 2, H - b)], TURM)
        m = 42
        for i in range(m):                    # left and right
            y0, y1 = i * H / m, (i + 1) * H / m
            self.c.poly([(0, y0), (0, y1), (b, (y0 + y1) / 2)], TURM)
            self.c.poly([(W, y0), (W, y1), (W - b, (y0 + y1) / 2)], TURM)
        self.c.line(closed([(b, b), (W - b, b), (W - b, H - b), (b, H - b)]), INK, 6)
        self.c.line(closed([(b + 8, b + 8), (W - b - 8, b + 8), (W - b - 8, H - b - 8), (b + 8, H - b - 8)]), INK, 2.5)


_ = Image
