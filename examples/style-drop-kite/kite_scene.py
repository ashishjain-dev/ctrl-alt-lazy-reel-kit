"""Kite scene for the Style Drop example: a dragon kite cuts a rival kite at Makar Sankranti.

A custom scene file like any other (see docs/custom-art.md): the engine calls draw(ctx, t, args) once per
frame and per style, with ctx.style set. The geometry lives in kite_art/layout.py and each style's painting
in kite_art/<style>.py. Your own scene can be one short file; this one is bigger because it is hand-tuned.
"""
import importlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from kite_art import layout  # noqa: E402

MODULES = {"fish-scale-folk": "folk", "rice-paper": "ricepaper", "mud-wall": "mudwall",
           "cyan-plan": "cyanplan", "cut-card": "cutcard"}
DUR, CUT_T = layout.DUR, layout.CUT_T


def draw(ctx, t, args):
    style = ctx.style if ctx.style in MODULES else "fish-scale-folk"
    Kite = importlib.import_module("kite_art." + MODULES[style]).Kite
    if Kite.fps:                                   # stepped styles (mud-wall 8 fps, cut-card 12 fps)
        t = math.floor(t * Kite.fps) / Kite.fps
    Kite(ctx.c, ctx.im).paint(layout.layout(t + float(args.get("offset", 0))))
