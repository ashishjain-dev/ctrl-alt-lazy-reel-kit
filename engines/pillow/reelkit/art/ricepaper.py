"""Rice Paper: inspired by East Asian ink-wash painting. Grey washes that darken where they overlap,
dry-brush streaks, soft ink bleed, rooftops fading into mist. The only colour is vermilion (sun and
a seal). The cut is an ink splatter plus one fast brush arc."""
import math

from .painter import Painter, paper_texture, soft_poly

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


    def reel_overlay(self):
        pass                      # the seal belongs to scenes (overlay(L) with L["seal"])

    def overlay(self, L):
        # red seal, bottom right of the sky
        x, y = (70, 1300) if L else (70, 1700)
        soft_poly(self.im, [(x, y), (x + 90, y), (x + 90, y + 90), (x, y + 90)], VERM, 0.92, 0.6)
        seal = str(L.get("seal", "")) if L else ""
        self.c.text((x + 45, y + 32), seal[:2], 34, "display", PAPER)
        self.c.text((x + 45, y + 64), seal[2:4], 34, "display", PAPER)
