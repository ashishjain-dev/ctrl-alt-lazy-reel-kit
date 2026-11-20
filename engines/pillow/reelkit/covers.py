"""Covers (1080x1920) + profile-grid preview.

Cover spec (in scenes.yaml under `cover:` or in its own cover.yaml):
    headline: "Your tests are *lying*"   # *word* = highlighted
    sub: "one command fixes it"           # optional
    tag: "#12"                            # optional corner tag (episode number)
    character: {who: bot, mood: smug}     # optional
    glow: accent

Instagram's profile grid shows a 3:4 centre crop of a 9:16 cover (it used to be 1:1),
so keep the headline inside y 390..1530. `grid` draws that crop so you can check it.
"""
import os

import yaml
from PIL import Image, ImageDraw

from . import characters, elements
from .brand import Brand
from .draw import K, Cv, glow, make_bg

W, H = 1080, 1920
GRID_CROP = (0, 240, 1080, 1680)      # 3:4 centre crop (1080x1440)


def cover(spec, brand, out):
    im = make_bg(brand, W, H)
    c = Cv(im, brand)
    glow(im, elements.col(c, spec.get("glow", "accent")), 540, 1150, 520, 0.5)
    if spec.get("tag"):
        c.rr([70, 450, 70 + c.tw(spec["tag"], 44, "display") + 50, 520], 20, fill=brand.c["accent"])
        c.text((95, 485), spec["tag"], 44, "display", brand.c["ink"], "lm")
    size = spec.get("size", 104)
    lines = c.wrap(spec["headline"], size, "display", 940)
    lh = size * 1.22
    y0 = spec.get("y", 640)
    for i, ln in enumerate(lines):
        elements._rich_line(c, 70, y0 + i * lh, ln, size, "display", brand.c["fg"],
                            brand.c["highlight"], brand.c["ink"], "l")
    yb = y0 + len(lines) * lh
    if spec.get("sub"):
        c.text((70, yb + 20), spec["sub"], 50, "bold", brand.c["muted"], "lm")
    ch = spec.get("character")
    if ch:
        characters.draw(c, ch.get("who", "bot"), ch.get("x", 740), ch.get("y", 1560), ch.get("scale", 0.95),
                        ch.get("mood", "smug"), 0.4, 0, brand.raw.get("characters", {}).get(ch.get("who", "bot")))
    out_im = im.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(out_im)
    if brand.frame.get("accent_bar", True):
        d.rectangle([0, 0, W, 10], fill=brand.c["accent"])
    if brand.handle:
        from .draw import font
        f = font(brand.fonts["bold"], 34).font_variant(size=34)
        d.text((540, 1610), brand.handle, font=f, fill=brand.c["muted"], anchor="mm")
    out_im.save(out)
    return out


def grid(paths, out, cols=3, thumb=360, show_crop=True):
    """Profile-grid preview: newest first (pass paths newest first), 3:4 crops."""
    tw, th = thumb, int(thumb * 4 / 3)
    rows = (len(paths) + cols - 1) // cols
    g = Image.new("RGB", (cols * tw + (cols - 1) * 4, rows * th + (rows - 1) * 4), (255, 255, 255))
    for k, p in enumerate(paths):
        im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
        crop = im.crop(GRID_CROP) if show_crop else im
        g.paste(crop.resize((tw, th), Image.LANCZOS), ((k % cols) * (tw + 4), (k // cols) * (th + 4)))
    g.save(out)
    return out


def from_yaml(path, out, brand_path=None):
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f) or {}
    spec = d.get("cover", d)
    base = os.path.dirname(os.path.abspath(path))
    bp = brand_path or (os.path.join(base, d["brand"]) if d.get("brand") else None)
    return cover(spec, Brand.load(bp), out)


_ = K  # re-exported for users who draw custom covers
