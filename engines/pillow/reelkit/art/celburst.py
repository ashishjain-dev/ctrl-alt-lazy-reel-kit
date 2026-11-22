"""Cel Burst: inspired by TV-anime cel shading (the animated-epic look). Saturated gradient skies with
huge cumulus clouds, bold ink outlines, two-tone cel shading with a hard shadow edge, lens flares, sun
rays and speed lines. Drawn on twos (12 fps).

Characters: `Character` builds an anime-style bust (face, eyes, brows, beard, hair, jewellery hooks) from
a few numbers, so a character stays the same from shot to shot. It supports lip sync (`talk`) and
blinking. Hair, clothes and jewellery are passed in as unit-space shapes and callbacks: see
docs/custom-art.md.
"""
import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from ..draw import K
from .painter import Painter, soft_poly

INK = (28, 22, 30)
SKY = [(0, (38, 86, 196)), (900, (104, 156, 238)), (1500, (255, 210, 170)), (1920, (255, 170, 110))]


# ---------- geometry ----------
def cr(pts, n=8, closed_=True):
    """Catmull-Rom smoothing through pts."""
    out = []
    m = len(pts)
    rng = range(m) if closed_ else range(m - 1)
    for i in rng:
        p0 = pts[(i - 1) % m] if closed_ or i > 0 else pts[0]
        p1, p2 = pts[i], pts[(i + 1) % m]
        p3 = pts[(i + 2) % m] if closed_ or i + 2 < m else pts[-1]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    if not closed_:
        out.append(pts[-1])
    return out


def ell(cx, cy, rx, ry, rot=0.0, n=40, a0=0.0, a1=2 * math.pi):
    c, s = math.cos(rot), math.sin(rot)
    return [(cx + rx * math.cos(a) * c - ry * math.sin(a) * s, cy + rx * math.cos(a) * s + ry * math.sin(a) * c)
            for a in (a0 + (a1 - a0) * i / n for i in range(n + (0 if a1 - a0 >= 2 * math.pi - 1e-6 else 1)))]


def T(pts, cx, cy, s, flip=False):
    """Unit coordinates -> pixels."""
    return [(cx + (-x if flip else x) * s, cy + y * s) for x, y in pts]


def mirror(half):
    """Right half (top to bottom) -> closed shape."""
    return half + [(-x, y) for x, y in reversed(half[1:-1])]



class CelBurst(Painter):
    name = "cel-burst"
    fps = 12                        # anime "on twos"
    jitter = 0.0
    pal = dict(Painter.pal, ink=INK, string=INK, hero=(230, 60, 60), hero2=(255, 200, 60), rival=(60, 110, 220),
               rival2=(255, 255, 255), tail=(255, 200, 60), tail2=(230, 60, 60), bird=INK, burst=(255, 255, 255),
               burst2=(255, 210, 80), text=(255, 255, 255), sun=(255, 236, 160))
    brand = {"bg_top": SKY[0][1], "bg_bottom": SKY[-1][1], "fg": (255, 255, 255), "muted": (220, 230, 250),
             "accent": (255, 200, 60), "highlight": (230, 60, 60), "panel": (255, 255, 255), "ink": INK,
             "good": (60, 180, 110), "bad": (230, 60, 60), "sub_bg": INK, "sub_fg": (255, 255, 255)}

    def background(self, L):
        self.sky_gradient(L.get("sky", SKY) if L else SKY)
        self.cloud([(200, 640, 120), (350, 560, 160), (520, 610, 130), (300, 720, 100), (460, 720, 110)],
                   lit=(255, 250, 240), shadow=(190, 180, 230))
        self.cloud([(780, 360, 90), (900, 310, 120), (1020, 360, 100)], lit=(255, 252, 246), shadow=(170, 170, 230))

    # ---------- cel primitives ----------
    def mask(self, pts):
        m = Image.new("L", self.im.size, 0)
        ImageDraw.Draw(m).polygon([(x * K, y * K) for x, y in pts], fill=255)
        return m

    def fill(self, pts, col, line=INK, w=5):
        self.c.poly(pts, col)
        if line and w:
            self.c.line(pts + [pts[0]], line, w)

    def shade(self, base, shadow, col):
        """Paint `shadow` only where it overlaps `base` (hard cel edge)."""
        m = ImageChops.multiply(self.mask(base), self.mask(shadow))
        self.im.paste(col, (0, 0), m)

    def outline(self, pts, w=5, col=INK):
        self.c.line(pts + [pts[0]], col, w)

    def glow(self, cx, cy, r, col, a=0.5):
        lay = Image.new("L", self.im.size, 0)
        ImageDraw.Draw(lay).ellipse([(cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K], fill=int(255 * a))
        lay = lay.filter(ImageFilter.GaussianBlur(r * K * 0.45))
        self.im.paste(col, (0, 0), lay)

    # ---------- sky ----------
    def sky_gradient(self, stops):
        """stops: [(y, colour), ...] top to bottom."""
        g = Image.new("RGB", (1, 1920))
        for y in range(1920):
            for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
                if y0 <= y <= y1:
                    u = (y - y0) / max(1, y1 - y0)
                    g.putpixel((0, y), tuple(int(a + (b - a) * u) for a, b in zip(c0, c1)))
                    break
            else:
                g.putpixel((0, y), stops[-1][1] if y > stops[-1][0] else stops[0][1])
        self.im.paste(g.resize(self.im.size, Image.BICUBIC))

    def cloud(self, blobs, lit=(255, 255, 255), shadow=(170, 160, 220), rim=None, line=True, off=(-24, -55)):
        """Cumulus from circles (cx, cy, r): flat lit colour, hard shadow on the underside, ink outline."""
        xs = [b[0] - b[2] for b in blobs] + [b[0] + b[2] for b in blobs]
        ys = [b[1] - b[2] for b in blobs] + [b[1] + b[2] for b in blobs]
        pad = 20
        x0, y0, x1, y1 = int((min(xs) - pad) * K), int((min(ys) - pad) * K), int((max(xs) + pad) * K), int((max(ys) + pad) * K)
        w, h = x1 - x0, y1 - y0
        U = Image.new("L", (w, h), 0)
        S = Image.new("L", (w, h), 0)
        du, ds = ImageDraw.Draw(U), ImageDraw.Draw(S)
        for cx, cy, r in blobs:
            du.ellipse([(cx - r) * K - x0, (cy - r) * K - y0, (cx + r) * K - x0, (cy + r) * K - y0], fill=255)
            ox, oy = off
            ds.ellipse([(cx - r + ox) * K - x0, (cy - r + oy) * K - y0, (cx + r + ox) * K - x0, (cy + r + oy) * K - y0], fill=255)
        crop = self.im.crop((x0, y0, x1, y1))
        crop.paste(shadow, (0, 0), U)
        lit_m = ImageChops.multiply(U, S)
        crop.paste(lit, (0, 0), lit_m)
        if rim:
            rim_m = ImageChops.subtract(lit_m, ImageChops.multiply(U, S.transform(S.size, Image.AFFINE, (1, 0, 10 * K, 0, 1, 14 * K))))
            crop.paste(rim, (0, 0), rim_m)
        if line:
            edge = ImageChops.subtract(U.filter(ImageFilter.MaxFilter(7)), U)
            crop.paste(INK, (0, 0), edge)
        self.im.paste(crop, (x0, y0))

    def flare(self, x, y, toward=(540, 960), col=(255, 240, 200)):
        self.glow(x, y, 220, col, 0.85)
        self.glow(x, y, 80, (255, 255, 255), 1.0)
        dx, dy = toward[0] - x, toward[1] - y
        for f, r, a in ((0.35, 34, 0.35), (0.6, 18, 0.45), (0.85, 60, 0.18), (1.25, 26, 0.3)):
            self.glow(x + dx * f, y + dy * f, r, col, a)

    def rays(self, x, y, n=18, length=1400, col=(255, 236, 190), a=0.18, width=0.05):
        lay = Image.new("L", self.im.size, 0)
        d = ImageDraw.Draw(lay)
        for k in range(n):
            ang = 2 * math.pi * k / n + 0.1
            d.polygon([(x * K, y * K), ((x + length * math.cos(ang - width)) * K, (y + length * math.sin(ang - width)) * K),
                       ((x + length * math.cos(ang + width)) * K, (y + length * math.sin(ang + width)) * K)], fill=int(255 * a))
        self.im.paste(col, (0, 0), lay.filter(ImageFilter.GaussianBlur(6 * K)))

    def speed_lines(self, cx, cy, n=60, r0=520, r1=1400, col=(255, 255, 255), seed=3):
        rnd = random.Random(seed)
        for _ in range(n):
            a = rnd.uniform(0, 2 * math.pi)
            ra = rnd.uniform(r0, r0 + 200)
            w = rnd.uniform(2, 7)
            self.c.line([(cx + ra * math.cos(a), cy + ra * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], col, w)



    def impact(self, u, x=540, y=960):
        """The big moment, u = seconds since impact: 3 black/white flash frames, one red frame, then a flare."""
        f = int(u * 12)
        if f < 3:
            self.im.paste((0, 0, 0) if f % 2 == 0 else (255, 255, 255), (0, 0, self.im.width, self.im.height))
        elif f == 3:
            self.im.paste((220, 30, 40), (0, 0, self.im.width, self.im.height))
        elif u < 1.2:
            self.flare(x, y)


# ---------- characters ----------
FACE_R = [(0.97, -0.55), (1.0, -0.05), (0.97, 0.4), (0.86, 0.85), (0.62, 1.22), (0.3, 1.48), (0.0, 1.56)]


def face_outline(jaw=1.0):
    arc = [(0.97 * math.sin(a), -0.55 - 0.95 * math.cos(a)) for a in [i * math.pi / 16 for i in range(8)]]
    low = [(x * (1 if y < 0.4 else 1 - 0.08 * (1 - jaw)), y * (1 if y < 0.4 else jaw)) for x, y in FACE_R]
    right = arc + low
    return cr(right + [(-x, y) for x, y in reversed(right[1:-1])], 6)


class Character:
    """A reusable anime-style bust. Keep these numbers to keep the character the same across shots."""

    def __init__(self, skin, skin_sh, hair, hair_sh, hair_hi, iris, eyes="open", fem=False, jaw=1.0,
                 brow=0.0, beard=None, beard_sh=None, look=(0.0, 0.0), mouth="calm", tilak=None, blush=True, fringe=0.3):
        self.__dict__.update(locals())
        del self.__dict__["self"]

    # parts in unit space: s = half face width, origin at eye-line centre
    def draw(self, p, cx, cy, s, body=None, hair_back=None, hair_front=None, jewels=None, light=1, talk=None, blink=False):
        """Draw on a CelBurst painter `p`. s = half face width (px); (cx, cy) = centre of the eye line.
        talk: 0..1 mouth opening for lip sync (None = the character's resting mouth). blink: eyes shut this frame."""
        c = p.c
        w = max(3, s * 0.035)
        U = lambda pts: T(pts, cx, cy, s)  # noqa: E731

        if hair_back:
            hb = U(hair_back)
            p.fill(hb, self.hair, INK, w)
            p.shade(hb, U([(0.2 * light, -3), (4, -3), (4, 6), (0.2 * light, 6)]), self.hair_sh)
            p.outline(hb, w)
        # neck
        neck = U([(-0.42, 0.9), (0.42, 0.9), (0.5, 2.3), (-0.5, 2.3)])
        p.fill(neck, self.skin, INK, w)
        p.shade(neck, U(ell(0, 1.3, 1.0, 0.55)), self.skin_sh)
        p.shade(neck, U([(0.18 * light, 0.9), (2, 0.9), (2, 2.4), (0.18 * light, 2.4)]), self.skin_sh)
        p.outline(neck, w)
        if body:
            body(p, cx, cy, s, w)
        # ears
        for sx in (-1, 1):
            ear = U([(sx * 0.9, 0.05), (sx * 1.13, -0.02), (sx * 1.18, 0.3), (sx * 1.05, 0.62), (sx * 0.88, 0.62)])
            ear = cr(ear, 5)
            p.fill(ear, self.skin if sx < 0 else self.skin_sh, INK, w)
        # face
        fo = U(face_outline(self.jaw))
        p.fill(fo, self.skin, None, 0)
        p.shade(fo, U([(0.58 * light, -2), (2, -2), (2, 2), (0.42 * light, 2), (0.62 * light, 0.6)]), self.skin_sh)
        if self.fringe:
            p.shade(fo, U(ell(0, -0.7, 1.3, self.fringe)), self.skin_sh)    # shadow under the fringe
        if self.blush:
            for sx in (-1, 1):
                soft_poly(p.im, U(ell(sx * 0.55, 0.62, 0.2, 0.09)), (240, 120, 120), 0.35, s * 0.04)
        if self.beard:
            bd = U(cr([(-0.98, 0.35), (-1.02, 1.0), (-0.8, 1.9), (-0.4, 2.6), (0.0, 2.95), (0.4, 2.6), (0.8, 1.9), (1.02, 1.0), (0.98, 0.35),
                       (0.8, 0.8), (0.5, 1.2), (0.25, 1.3), (0.0, 1.32), (-0.25, 1.3), (-0.5, 1.2), (-0.8, 0.8)], 6))
        p.outline(fo, w)
        # features
        self._eyes(p, U, s, w, blink)
        for sx in (-1, 1):                                              # brows
            b = [(sx * 0.18, -0.18 + self.brow), (sx * 0.42, -0.27), (sx * 0.7, -0.22)]
            c.line(U(cr(b, 6, False)), self.hair_sh if not self.beard else (230, 230, 236), w * (1.5 if not self.fem else 1.0))
        c.line(U([(0.06, 0.62), (0.0, 0.8), (0.09, 0.83)]), (150, 90, 70), w * 0.6)    # nose
        if talk is not None and talk > 0.08 and not self.beard:
            m = U(ell(0, 1.1, 0.13 + 0.03 * talk, 0.03 + 0.1 * talk))
            p.fill(m, (150, 50, 60), INK, w * 0.6)
        elif self.beard:
            pass
        elif self.mouth == "smile":
            c.line(U(cr([(-0.22, 1.05), (0, 1.13), (0.22, 1.05)], 6, False)), (130, 60, 60), w * 0.8)
        elif self.mouth == "open":
            m = U(cr([(-0.17, 1.03), (0.17, 1.03), (0.08, 1.18), (-0.08, 1.18)], 5))
            p.fill(m, (150, 50, 60), INK, w * 0.6)
        else:
            c.line(U(cr([(-0.16, 1.08), (0, 1.1), (0.16, 1.07)], 6, False)), (130, 60, 60), w * 0.8)
        if self.fem:
            lip = U(ell(0, 1.14, 0.08, 0.035))
            p.fill(lip, (210, 90, 100), None, 0)
        if self.tilak:
            kind, col = self.tilak
            if kind == "dot":
                p.fill(U(ell(0, -0.32, 0.06, 0.06)), col, INK, w * 0.5)
            else:
                p.fill(U([(-0.04, -0.5), (0.04, -0.5), (0.02, -0.2), (-0.02, -0.2)]), col, None, 0)
        if self.beard:
            p.fill(bd, self.beard, INK, w)
            p.shade(bd, U([(0.15 * light, 0), (2, 0), (2, 3), (0.15 * light, 3)]), self.beard_sh)
            for k in range(-3, 4):                                    # strands
                c.line(U(cr([(k * 0.16, 1.3), (k * 0.15, 2.0), (k * 0.09, 2.5)], 5, False)), self.beard_sh, w * 0.6)
            mus = U(cr([(0, 0.9), (0.3, 0.92), (0.55, 1.1), (0.62, 1.45), (0.4, 1.15), (0.0, 1.02), (-0.4, 1.15), (-0.62, 1.45), (-0.55, 1.1), (-0.3, 0.92)], 5))
            p.fill(mus, self.beard, INK, w * 0.8)
            c.line(U(cr([(-0.14, 1.2), (0, 1.22), (0.14, 1.2)], 6, False)), (130, 60, 60), w * 0.8)
            p.outline(bd, w)
        if hair_front:
            for lock in hair_front:
                hf = U(cr(lock, 5))
                p.fill(hf, self.hair, None, 0)
                p.shade(hf, U([(0.3 * light, -3), (3, -3), (3, 3), (0.3 * light, 3)]), self.hair_sh)
                p.outline(hf, w)
            ring = U(cr([(-0.7, -1.02), (-0.3, -1.25), (0.2, -1.27), (0.6, -1.1)], 6, False))
            c.line(ring, self.hair_hi, w * 2.2)
        if jewels:
            jewels(p, U, s, w)

    def _eyes(self, p, U, s, w, blink=False):
        c = p.c
        lx, ly = self.look
        for sx in (-1, 1):
            ex = sx * 0.42
            if self.eyes == "closed" or blink:
                c.line(U(cr([(ex - 0.22, 0.2), (ex, 0.29), (ex + 0.22, 0.2)], 6, False)), INK, w * 1.6)
                for k in (-1, 0, 1):
                    c.line(U([(ex + sx * 0.2 + k * 0.0, 0.21), (ex + sx * 0.3, 0.27 + 0.05 * k)]), INK, w * 0.8)
                continue
            top = [(ex - sx * 0.25, 0.22), (ex - sx * 0.08, 0.06), (ex + sx * 0.12, 0.06), (ex + sx * 0.27, 0.15)]
            bot = [(ex + sx * 0.25, 0.22), (ex + sx * 0.05, 0.36), (ex - sx * 0.15, 0.34)]
            alm = U(cr(top + bot, 6))
            p.fill(alm, (252, 250, 248), None, 0)
            ix, iy = ex + lx * 0.06, 0.21 + ly * 0.05
            iris = U(ell(ix, iy, 0.13, 0.17))
            p.shade(alm, iris, self.iris)
            dark = tuple(int(v * 0.55) for v in self.iris)
            p.shade(alm, U(ell(ix, iy - 0.06, 0.13, 0.11)), dark)
            p.shade(alm, U(ell(ix, iy, 0.06, 0.08)), (20, 14, 20))
            p.fill(U(ell(ix - 0.05, iy - 0.06, 0.04, 0.04)), (255, 255, 255), None, 0)
            p.fill(U(ell(ix + 0.05, iy + 0.07, 0.02, 0.02)), (255, 255, 255), None, 0)
            c.line(U(cr(top, 6, False)), INK, w * (1.9 if self.fem else 1.6))       # heavy upper lid
            c.line(U([top[-1], (ex + sx * 0.33, 0.1)]), INK, w * (1.4 if self.fem else 0.9))   # outer flick
            c.line(U(cr(bot[:2], 4, False)), INK, w * 0.5)
