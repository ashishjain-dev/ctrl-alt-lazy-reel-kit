"""Cyan Plan: inspired by engineering blueprints. Cyanotype blue with a grid, white line-work only,
dimension lines, callouts, dashed paths, a target reticle and a title block. Impacts are concentric
rings with tick marks."""
from ..draw import K
from .painter import Painter, closed, paper_texture

BLUE = (22, 66, 140)
LINE = (232, 242, 255)
FAINT = (88, 130, 196)


class CyanPlan(Painter):
    name = "cyan-plan"
    pal = dict(Painter.pal, ink=LINE, string=LINE, text=LINE)
    brand = {"bg_top": BLUE, "bg_bottom": (16, 52, 116), "fg": LINE, "muted": (170, 196, 236), "accent": LINE,
             "highlight": (255, 214, 120), "panel": (30, 84, 168), "ink": (10, 30, 70), "good": LINE,
             "bad": (255, 200, 170), "sub_bg": (10, 36, 84), "sub_fg": LINE}

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


    def reel_overlay(self):
        self.c.line(closed([(20, 20), (1060, 20), (1060, 1900), (20, 1900)]), LINE, 3)

    def overlay(self, L):
        # title block, top-left (inside the safe zone)
        x0, y0, x1, y1 = 70, 250 if L else 120, 520, 250 + 150 if L else 270
        self.ln(closed([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), 3)
        self.ln([(x0, y0 + 50), (x1, y0 + 50)], 2)
        self.ln([(x0 + 220, y0 + 50), (x0 + 220, y1)], 2)
        self.mono((x0 + 16, y0 + 25), "PROJECT: " + str(L.get("project", "UNTITLED")).upper(), 24)
        self.mono((x0 + 16, y0 + 80), "SHEET 1 / 1", 20)
        self.mono((x0 + 16, y0 + 115), "SCALE 1:20", 20)
        self.mono((x0 + 236, y0 + 80), str(L.get("note", "")).upper()[:16], 20)
        self.mono((x0 + 236, y0 + 115), "REV A", 20)
        self.c.line(closed([(20, 20), (1060, 20), (1060, 1900), (20, 1900)]), LINE, 3)


_ = K
