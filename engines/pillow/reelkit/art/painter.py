"""Painter = an art style: its surface (background), frame (overlay), colours for whole reels (`brand`),
palette (`pal`), time step (`fps`, `jitter`) and drawing helpers.

Custom scene and character files (see reelkit/custom.py) get the active style's painter as ctx.painter
and use it plus the helpers below. examples/style-drop-kite/kite_art shows a full scene painted in 5 styles.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from ..draw import K


def local(center, ang, x, y):
    cs, sn = math.cos(ang), math.sin(ang)
    return center[0] + x * cs - y * sn, center[1] + x * sn + y * cs


def closed(pts):
    return list(pts) + [pts[0]]


_TILES = {}


def tile(kind, col, bg=None, size=36, width=3):
    """Pattern tile (RGBA, supersampled). kinds: scales, dots, hatch, cross, waves, grid."""
    key = (kind, col, bg, size, width)
    if key in _TILES:
        return _TILES[key]
    s = int(size * K)
    im = Image.new("RGBA", (s, s), (bg + (255,)) if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = max(1, int(width * K))
    if kind == "scales":
        r = s // 2
        for ox, oy in ((0, 0), (r, r), (-r, r), (s, 0), (0, s), (s, s)):
            d.arc([ox - r, oy - r, ox + r, oy + r], 0, 180, fill=col, width=w)
    elif kind == "dots":
        r = max(2, s // 9)
        for ox, oy in ((s // 4, s // 4), (3 * s // 4, 3 * s // 4)):
            d.ellipse([ox - r, oy - r, ox + r, oy + r], fill=col)
    elif kind == "hatch":
        for o in range(-s, 2 * s, s // 3):
            d.line([(o, 0), (o + s, s)], fill=col, width=w)
    elif kind == "cross":
        for o in range(-s, 2 * s, s // 3):
            d.line([(o, 0), (o + s, s)], fill=col, width=w)
            d.line([(o + s, 0), (o, s)], fill=col, width=w)
    elif kind == "waves":
        pts = [(x, s // 2 + int(s * 0.18 * math.sin(x / s * 2 * math.pi))) for x in range(0, s + 1, 2)]
        d.line(pts, fill=col, width=w)
    elif kind == "grid":
        d.line([(0, 0), (s, 0)], fill=col, width=w)
        d.line([(0, 0), (0, s)], fill=col, width=w)
    _TILES[key] = im
    return im


def fill_pattern(im, pts, pattern_tile):
    """Fill polygon `pts` (output px) with a repeating tile, clipped to the polygon."""
    xs, ys = [p[0] * K for p in pts], [p[1] * K for p in pts]
    x0, y0 = int(max(0, min(xs))), int(max(0, min(ys)))
    x1, y1 = int(min(im.width, max(xs) + 1)), int(min(im.height, max(ys) + 1))
    if x1 <= x0 or y1 <= y0:
        return
    w, h = x1 - x0, y1 - y0
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in zip(xs, ys)], fill=255)
    tw, th = pattern_tile.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for ty in range(-(y0 % th), h, th):
        for tx in range(-(x0 % tw), w, tw):
            layer.paste(pattern_tile, (tx, ty), pattern_tile)
    alpha = Image.fromarray(np.minimum(np.array(layer.split()[3]), np.array(mask)))
    im.paste(layer.convert("RGB"), (x0, y0), alpha)


_NOISE = {}


def paper_texture(w, h, base, amount=10, fibres=0, seed=3):
    key = (w, h, base, amount, fibres, seed)
    if key not in _NOISE:
        rng = np.random.default_rng(seed)
        small = rng.normal(0, 1, (h // 4, w // 4))
        n = np.array(Image.fromarray(((small - small.min()) / (np.ptp(small) + 1e-9) * 255).astype("uint8"))
                     .resize((w, h), Image.BICUBIC), dtype=np.float32) / 255 - 0.5
        fine = rng.normal(0, 0.5, (h, w)).astype(np.float32) * 0.4
        arr = np.array(base, dtype=np.float32)[None, None, :] + (n[..., None] * amount * 2 + fine[..., None] * amount)
        img = Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))
        if fibres:
            d = ImageDraw.Draw(img)
            fr = np.random.default_rng(seed + 1)
            for _ in range(fibres):
                x, y = fr.uniform(0, w), fr.uniform(0, h)
                a, L = fr.uniform(0, math.pi), fr.uniform(20, 70) * K
                c = tuple(int(v - 18) for v in base)
                d.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=c, width=1)
        _NOISE[key] = img
    return _NOISE[key]


def _bbox(pts, pad, im):
    xs, ys = [p[0] * K for p in pts], [p[1] * K for p in pts]
    x0, y0 = int(max(0, min(xs) - pad)), int(max(0, min(ys) - pad))
    x1, y1 = int(min(im.width, max(xs) + pad + 1)), int(min(im.height, max(ys) + pad + 1))
    return x0, y0, x1, y1, xs, ys


def soft_poly(im, pts, col, alpha=0.5, blur=0, width=0):
    """Translucent (optionally blurred) polygon or polyline (width>0): washes, shadows, glows."""
    pad = blur * K * 3 + width * K
    x0, y0, x1, y1, xs, ys = _bbox(pts, pad, im)
    if x1 <= x0 or y1 <= y0:
        return
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    d = ImageDraw.Draw(m)
    q = [(x - x0, y - y0) for x, y in zip(xs, ys)]
    if width:
        d.line(q, fill=int(255 * alpha), width=int(width * K), joint="curve")
    else:
        d.polygon(q, fill=int(255 * alpha))
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur * K))
    im.paste(col, (x0, y0, x1, y1), m)


def shadow_poly(im, pts, off=(10, 14), alpha=0.45, blur=6):
    soft_poly(im, [(x + off[0], y + off[1]) for x, y in pts], (0, 0, 0), alpha, blur)


def dashed(c, pts, col, width, dash=18, gap=12):
    """Dashed polyline (output px)."""
    on, left = True, dash
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        pos = 0.0
        while pos < L:
            step = min(left, L - pos)
            a, b = pos / L, (pos + step) / L
            if on:
                c.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], col, width)
            pos += step
            left -= step
            if left <= 1e-6:
                on = not on
                left = dash if on else gap


class Painter:
    name = "flat"
    fps = None            # e.g. 12 for stop motion: time is stepped to this rate
    jitter = 0.0          # px of per-step wobble (stop motion / hand-made feel)
    pal = {
        "sky_top": (110, 170, 230), "sky_bottom": (255, 205, 150), "sun": (255, 214, 102),
        "ink": (25, 25, 32), "roof": (120, 90, 110), "roof2": (150, 110, 120), "tank": (90, 110, 160),
        "hero": (214, 58, 38), "hero2": (236, 170, 30), "rival": (60, 120, 200), "rival2": (250, 250, 250),
        "tail": (236, 170, 30), "tail2": (214, 58, 38), "string": (40, 40, 50), "bird": (40, 40, 50),
        "bgk1": (230, 90, 120), "bgk2": (90, 180, 120), "bgk3": (120, 110, 220),
        "marigold": (245, 160, 20), "burst": (255, 240, 160), "burst2": (255, 120, 60), "text": (255, 255, 255),
    }

    # colours used when this style is applied to a whole reel (`style:` in scenes.yaml)
    brand = {}

    def __init__(self, c, im):
        self.c, self.im = c, im
        self.t = 0.0

    def reel_background(self):
        """Background for any reel using this style (no scene geometry)."""
        self.background({})

    def reel_overlay(self):
        self.overlay({})

    # ---------- helpers ----------
    def P(self, k):
        return self.pal[k]

    def j(self, pts, t, amt=None, seed=0):
        """Hand-made wobble: shift points a little, changing every stepped frame."""
        a = self.jitter if amt is None else amt
        if not a:
            return pts
        st = int(round(t * (self.fps or 30)))
        return [(x + a * math.sin(st * 12.9898 + i * 78.233 + seed), y + a * math.cos(st * 39.346 + i * 11.135 + seed))
                for i, (x, y) in enumerate(pts)]

    def shape(self, pts, fill, outline=None, width=0):
        self.c.poly(pts, fill)
        if outline:
            self.c.line(closed(pts), outline, width)

    # ---------- parts ----------
    def background(self, L):
        top, bot = self.P("sky_top"), self.P("sky_bottom")
        g = Image.new("RGB", (1, 256))
        for y in range(256):
            u = y / 255
            g.putpixel((0, y), tuple(int(a + (b - a) * u) for a, b in zip(top, bot)))
        self.im.paste(g.resize(self.im.size, Image.BICUBIC))


    def overlay(self, L):
        pass

    # ---------- whole frame ----------


def blur_layer(im, radius):
    return im.filter(ImageFilter.GaussianBlur(radius * K))
