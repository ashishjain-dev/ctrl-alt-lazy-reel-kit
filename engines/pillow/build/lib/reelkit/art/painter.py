"""Painter = an art style. It decides how every part of a hero scene looks; the scene decides where things are.

Subclass Painter and override the parts you want; anything not overridden falls back to a clean flat look.
Draw order: background → sun → bg kites → skyline → birds → rival string → rival → hero string → tail → hero
→ hero face → burst → shout → overlay (border, texture).
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

    def sun(self, L):
        x, y, r = L["sun"]
        self.c.ell([x - r, y - r, x + r, y + r], fill=self.P("sun"))

    def bg_kites(self, L):
        for pts, role, size in L["bg_kites"]:
            self.c.line([pts[2], (pts[2][0] + size * 0.5, pts[2][1] + size * 3)], self.P("string"), 1.5)
            self.shape(pts, self.P(role))

    def skyline(self, L):
        sk = L["skyline"]
        for i, b in enumerate(sk["blocks"]):
            self.shape(b, self.P("roof" if i % 2 else "roof2"))
        for w in sk["windows"]:
            self.shape(w, self.P("sky_bottom"))
        x0, y0, x1, y1 = sk["tank"]
        self.c.rr([x0, y0, x1, y1], 14, fill=self.P("tank"))
        self.c.line(sk["antenna"], self.P("ink"), 6)
        for bar in sk["antenna_bars"]:
            self.c.line(bar, self.P("ink"), 5)
        self.c.line(sk["toran"], self.P("string"), 2)
        for i, (x, y) in enumerate(sk["toran"][1:-1]):
            self.c.ell([x - 11, y - 2, x + 11, y + 20], fill=self.P("marigold"))

    def birds(self, L):
        for x, y, flap in L["birds"]:
            wy = 14 * flap
            self.c.line([(x - 22, y - wy), (x, y), (x + 22, y - wy)], self.P("bird"), 5)

    def strings(self, L):
        for seg in L["rival_string"]:
            self.c.line(seg, self.P("string"), 2.5)
        self.c.line(L["hero_string"], self.P("string"), 3)

    def rival(self, L):
        t, r, b, l = L["rival"]
        mid = ((l[0] + r[0]) / 2, (l[1] + r[1]) / 2)
        self.shape([t, r, mid, l], self.P("rival"))
        self.shape([l, mid, r, b], self.P("rival2"))
        self.c.poly([b, (b[0] - 18, b[1] + 34), (b[0] + 18, b[1] + 34)], self.P("rival"))
        self.c.line(closed(L["rival"]), self.P("ink"), 3)

    def tail(self, L):
        pts = [L["hero"][2]] + L["tail"]
        for i in range(len(pts) - 1):
            self.c.line([pts[i], pts[i + 1]], self.P("tail" if i % 2 else "tail2"), 16 - i * 0.7)

    def hero(self, L):
        self.shape(L["hero"], self.P("hero"), self.P("ink"), 5)

    def hero_face(self, L):
        """Dragon face painted on the hero kite, in kite-local coordinates."""
        c, a = L["hero_c"], L["hero_angle"]
        k = L["hero_s"]
        Lp = lambda x, y: local(c, a, x * k, y * k)  # noqa: E731
        ink, h2 = self.P("ink"), self.P("hero2")
        for sx in (-1, 1):   # horns
            self.c.poly([Lp(sx * 22, -60), Lp(sx * 46, -96), Lp(sx * 40, -54)], h2)
        for sx in (-1, 1):   # almond eyes
            ex = sx * 38
            eye = [Lp(ex - 26, -14), Lp(ex, -30), Lp(ex + 26, -14), Lp(ex, 2)]
            self.c.poly(eye, (250, 246, 236))
            self.c.line(closed(eye), ink, 3)
            px, py = Lp(ex + sx * 4, -14)
            self.c.ell([px - 8, py - 8, px + 8, py + 8], fill=ink)
        for sx in (-1, 1):   # nostrils
            nx, ny = Lp(sx * 12, 26)
            self.c.ell([nx - 5, ny - 5, nx + 5, ny + 5], fill=ink)
        teeth = [Lp(-40 + i * 10, 52 + (8 if i % 2 else 0)) for i in range(9)]
        self.c.line(teeth, ink, 3)
        for sx in (-1, 1):   # whiskers
            self.c.line([Lp(sx * 30, 34), Lp(sx * 70, 40), Lp(sx * 86, 64)], h2, 4)

    def burst(self, L):
        u = L["burst"]
        if u is None:
            return
        x, y = L["cut_pt"]
        r = 40 + 220 * min(1, u / 0.35)
        fade = max(0.0, 1 - u / 0.9)
        n = 12
        pts = []
        for i in range(2 * n):
            rr = r if i % 2 == 0 else r * 0.45
            a = math.pi * i / n + u * 0.8
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        if fade > 0:
            self.c.poly(pts, self.P("burst2"))
            self.c.ell([x - r * 0.3, y - r * 0.3, x + r * 0.3, y + r * 0.3], fill=self.P("burst"))
        self.sparkles(L)

    def sparkles(self, L):
        u = L["burst"]
        x, y = L["cut_pt"]
        for i in range(14):
            a = i * 2.39996
            d = 60 + 380 * u
            sx, sy = x + math.cos(a) * d, y + math.sin(a) * d + 120 * u * u
            s = 10 * (1 - u)
            if s > 1:
                self.c.poly([(sx, sy - s), (sx + s * 0.6, sy), (sx, sy + s), (sx - s * 0.6, sy)], self.P("burst"))

    def shout(self, L):
        if not L["shout"]:
            return
        u = min(1.0, L["shout_t"] / 0.25)
        size = 120 * (0.4 + 0.6 * u) * (1 + 0.06 * math.sin(L["shout_t"] * 9))
        self.text_shout("Kaipoche!", L["shout_xy"], size)

    def text_shout(self, s, xy, size, fill=None, stroke=None, kind="display", sw=8):
        f = self.c.f(kind, size)
        self.c.d.text((int(xy[0] * K), int(xy[1] * K)), s, font=f, fill=fill or self.P("text"), anchor="mm",
                      stroke_width=int(sw * K), stroke_fill=stroke or self.P("ink"))

    def overlay(self, L):
        pass

    # ---------- whole frame ----------
    def paint(self, L):
        for part in (self.background, self.sun, self.bg_kites, self.skyline, self.birds, self.strings,
                     self.rival, self.tail, self.hero, self.hero_face, self.burst, self.shout, self.overlay):
            part(L)


def blur_layer(im, radius):
    return im.filter(ImageFilter.GaussianBlur(radius * K))
