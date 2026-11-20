"""Art styles (painters) and hero scenes for Style Drop reels.

    from reelkit.art import draw_scene
    draw_scene(c, im, "kite", "fish-scale-folk", t)

A scene module exposes DUR, CUT_T and layout(t). A style is a Painter subclass (see painter.py).
"""
import math

from . import kite
from .cutcard import CutCard
from .cyanplan import CyanPlan
from .folk import FishScaleFolk
from .mudwall import MudWall
from .painter import Painter
from .ricepaper import RicePaper

SCENES = {"kite": kite}
STYLES = {"flat": Painter, "fish-scale-folk": FishScaleFolk, "rice-paper": RicePaper, "mud-wall": MudWall,
          "cyan-plan": CyanPlan, "cut-card": CutCard}


def style_class(name):
    if name not in STYLES:
        raise ValueError(f"unknown style '{name}'. Known: {sorted(STYLES)}")
    return STYLES[name]


def draw_scene(c, im, scene, style, t):
    sc = SCENES[scene]
    P = style_class(style)
    if P.fps:                      # stepped time for stop-motion / hand-made styles
        t = math.floor(t * P.fps) / P.fps
    P(c, im).paint(sc.layout(t))
