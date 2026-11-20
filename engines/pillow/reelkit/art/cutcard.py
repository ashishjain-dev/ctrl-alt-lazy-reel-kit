"""Cut Card: inspired by layered paper cut-out animation. Coloured card with soft drop shadows and thin
white cut edges, wavy paper sky strips, stacked cloud strips, stop motion at 12 fps with a tiny jitter.
The cut is a paper starburst."""
import math

from .painter import Painter, closed, paper_texture, shadow_poly

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

