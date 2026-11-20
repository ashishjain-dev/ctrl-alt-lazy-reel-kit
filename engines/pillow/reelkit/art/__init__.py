"""Art styles: each style is a Painter subclass that knows a surface (background), a frame (overlay),
colours for a whole reel (`brand`), a time step (`fps`, `jitter`) and drawing helpers in its own manner.

Scenes are not part of the engine: every picture is drawn for its video by a custom file
(see reelkit/custom.py, docs/custom-art.md and docs/style-guides.md). examples/style-drop-kite and
examples/folk-story-crow show how.
"""
from .cutcard import CutCard
from .cyanplan import CyanPlan
from .folk import FishScaleFolk
from .mudwall import MudWall
from .painter import Painter
from .ricepaper import RicePaper

STYLES = {"flat": Painter, "fish-scale-folk": FishScaleFolk, "rice-paper": RicePaper, "mud-wall": MudWall,
          "cyan-plan": CyanPlan, "cut-card": CutCard}


def style_class(name):
    if name not in STYLES:
        raise ValueError(f"unknown style '{name}'. Built in: {sorted(STYLES)}. Other styles (see docs/style-guides.md) "
                         "are drawn by custom files, not set with `style:`")
    return STYLES[name]
