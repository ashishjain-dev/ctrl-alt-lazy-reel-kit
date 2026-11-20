"""Colour emoji for the Pillow engine, via the system's colour emoji font:
Noto Color Emoji (Linux: apt install fonts-noto-color-emoji), Apple Color Emoji (macOS) or Segoe UI Emoji (Windows).
Without one, emoji are skipped and `reelkit check` says so. (The Remotion engine always has emoji.)
"""
import os
import re

from PIL import Image, ImageDraw, ImageFont

from .brand import find_font

_RANGES = (r"\U0001F000-\U0001FAFF☀-⛿✀-➿⬀-⯿⌀-⏿"
           r"〰〽㊗㊙©®‼⁉™ℹ↔-↪")
# a cluster: emoji (+ variation selector / skin tone) joined by ZWJ, or a flag pair
EMOJI_RE = re.compile(rf"(?:[\U0001F1E6-\U0001F1FF]{{2}})|(?:[{_RANGES}][️\U0001F3FB-\U0001F3FF]?"
                      rf"(?:‍[{_RANGES}][️\U0001F3FB-\U0001F3FF]?)*)")
# glyphs the text fonts already have; keep them as text
TEXT_SAFE = set("✓✔✗✘×→←↑↓★☆•©®™")

_FONT = False
_CACHE = {}


def emoji_font():
    global _FONT
    if _FONT is False:
        _FONT = None
        try:
            path = find_font([os.environ.get("REELKIT_EMOJI_FONT", "") or "NotoColorEmoji.ttf",
                              "NotoColorEmoji.ttf", "Apple Color Emoji.ttc", "seguiemj.ttf"])
        except FileNotFoundError:
            return None
        for size in (109, 160, 137, 96, 64, 128):   # bitmap emoji fonts only load at their strike sizes
            try:
                _FONT = ImageFont.truetype(path, size)
                break
            except OSError:
                continue
    return _FONT


def split(s):
    """[(is_emoji, text)] runs."""
    out, i = [], 0
    for m in EMOJI_RE.finditer(s):
        if m.group() in TEXT_SAFE:
            continue
        if m.start() > i:
            out.append((False, s[i:m.start()]))
        out.append((True, m.group()))
        i = m.end()
    if i < len(s):
        out.append((False, s[i:]))
    return out


def has_emoji(s):
    return any(e for e, _ in split(s))


def glyph(cluster, px):
    """RGBA image of one emoji cluster, px tall (supersampled pixels). None if no emoji font."""
    key = (cluster, int(px))
    if key in _CACHE:
        return _CACHE[key]
    f = emoji_font()
    if f is None:
        _CACHE[key] = None
        return None
    big = Image.new("RGBA", (int(f.size * 2.4), int(f.size * 1.6)), (0, 0, 0, 0))
    ImageDraw.Draw(big).text((int(f.size * 0.2), int(f.size * 0.2)), cluster, font=f, embedded_color=True)
    bb = big.getbbox()
    if not bb:
        _CACHE[key] = None
        return None
    g = big.crop(bb)
    g = g.resize((max(1, int(g.width * px / g.height)), int(px)), Image.LANCZOS)
    _CACHE[key] = g
    return g
