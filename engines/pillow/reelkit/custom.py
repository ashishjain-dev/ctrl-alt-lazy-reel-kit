"""Custom art written per video (usually by Claude at runtime) and plugged into the engine.

Two hooks:

1. A custom element (backgrounds, props, whole illustrated scenes):
       scenes.yaml:  - {type: custom, file: crow_scene.py, at: 0, args: {water: 0.3}}
       crow_scene.py:
           def draw(ctx, t, args):        # t = seconds since the element's `at`
               ctx.c.poly(...)            # draw with output-pixel coordinates (1080 x 1920)

2. A custom character (talks, lip-syncs and changes mood like the built-ins):
       scenes.yaml:  characters: {dadi: {file: dadi.py, sari: "#e8805c"}}
       dadi.py:
           def draw(c, x, y, s, mood, t, talk, opts):   # (x, y) = feet, s = scale, talk = mouth 0..1
               ...

Files are loaded from the folder of scenes.yaml (or brand.yaml for characters defined there).
They can import the helpers: `from reelkit.art.painter import fill_pattern, tile, soft_poly, ...`.
Every frame must be a pure function of t (no state carried between frames): frames render in
parallel and out of order.
"""
import importlib.util
import os

from . import art
from .art import painter as P
from .draw import K

_MODS = {}


def load(path):
    path = os.path.abspath(path)
    mt = os.path.getmtime(path)
    hit = _MODS.get(path)
    if hit and hit[0] == mt:
        return hit[1]
    name = "reelkit_custom_" + os.path.splitext(os.path.basename(path))[0].replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "draw"):
        raise AttributeError(f"{path} must define draw(...)")
    _MODS[path] = (mt, mod)
    return mod


class Ctx:
    """What a custom element's draw() gets."""

    def __init__(self, c, im, el):
        self.c, self.im, self.brand = c, im, c.b
        self.K = K
        self.W, self.H = 1080, 1920
        self.base = el.get("_base", ".")
        self.style = el.get("style") or c.b.raw.get("_style") or "flat"
        cls = art.style_class(self.style)
        self.painter = cls(c, im)          # reuse the style's own parts: ctx.painter.background({}) etc.
        self.pal = dict(cls.pal)            # the style's palette (ink, hero, sun, ...)
        self.colors = c.b.c                 # brand colours, already set to the style's colours
        # drawing helpers
        self.fill_pattern, self.tile, self.soft_poly = P.fill_pattern, P.tile, P.soft_poly
        self.shadow_poly, self.dashed, self.paper_texture = P.shadow_poly, P.dashed, P.paper_texture
        self.local, self.closed = P.local, P.closed

    def path(self, rel):
        return rel if os.path.isabs(rel) else os.path.join(self.base, rel)


def draw_element(c, im, el, t):
    path = el["file"] if os.path.isabs(el["file"]) else os.path.join(el.get("_base", "."), el["file"])
    mod = load(path)
    ctx = Ctx(c, im, el)
    ctx.painter.t = t
    ctx.t = t
    mod.draw(ctx, t, el.get("args", {}) or {})


def character_fn(path):
    """Wrap a custom character file as a character draw function."""
    def fn(c, x, y, s, mood="neutral", t=0.0, talk=0.0, opts=None):
        load(path).draw(c, x, y, s, mood, t, talk, opts or {})
    return fn


def resolve_files(chars, base):
    """Make `file:` paths in a characters dict absolute (relative to `base`)."""
    out = {}
    for name, spec in (chars or {}).items():
        spec = dict(spec or {})
        if spec.get("file") and not os.path.isabs(spec["file"]):
            spec["file"] = os.path.join(base, spec["file"])
        out[name] = spec
    return out
