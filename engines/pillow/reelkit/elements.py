"""Scene elements. Each element is a dict from scenes.yaml with a `type` and an `at` time (seconds
from scene start). Every draw function gets (c, im, el, t) where t is the scene-local time.

Colours accept brand keys (fg, muted, accent, highlight, good, bad, panel, ink, info) or "#rrggbb".
Text marked with *stars* is highlighted (headline, text, bubble).
"""
import math
import os

from PIL import Image

from . import characters
from .brand import hex2rgb
from .draw import K, back_out, clamp, lerp, pop, smooth, soft_shadow


def col(c, v, default="fg"):
    if v is None:
        v = default
    if isinstance(v, str) and v in c.b.c:
        return c.b.c[v]
    return hex2rgb(v)


def _rich_line(c, x, y, line, size, kind, fill, hl_bg, hl_fg, anchor="m"):
    """Draw one line where *segments* are highlighted. anchor: l | m | r (horizontal)."""
    parts = line.split("*")
    widths = [c.tw(p, size, kind) for p in parts]
    total = sum(widths)
    cx = {"l": x, "m": x - total / 2, "r": x - total}[anchor]
    for i, (p, w) in enumerate(zip(parts, widths)):
        if not p:
            continue
        if i % 2 == 1:
            pad = size * 0.16
            c.rr([cx - pad, y - size * 0.62, cx + w + pad, y + size * 0.62], size * 0.18, fill=hl_bg)
            c.text((cx, y), p, size, kind, hl_fg, "lm")
        else:
            c.text((cx, y), p, size, kind, fill, "lm")
        cx += w


def headline(c, im, el, t):
    u = pop(t, el.get("at", 0), 0.35)
    if u is None:
        return
    size = el.get("size", 78)
    kind = el.get("font", "display")
    maxw = el.get("w", 920)
    lines = c.wrap(el["text"], size, kind, maxw)
    lh = size * 1.28
    y0 = el.get("y", 430) - (len(lines) - 1) * lh / 2 + (1 - u) * 60
    for i, ln in enumerate(lines):
        _rich_line(c, el.get("x", 540), y0 + i * lh, ln, size, kind, col(c, el.get("color")),
                   col(c, el.get("highlight"), "highlight"), c.b.c["ink"], el.get("align", "m"))


def text(c, im, el, t):
    u = pop(t, el.get("at", 0), 0.3)
    if u is None:
        return
    size = el.get("size", 54)
    kind = el.get("font", "bold")
    lines = c.wrap(el["text"], size, kind, el.get("w", 940))
    lh = size * 1.3
    for i, ln in enumerate(lines):
        _rich_line(c, el.get("x", 540), el.get("y", 800) + i * lh + (1 - u) * 50, ln, size, kind,
                   col(c, el.get("color")), col(c, el.get("highlight"), "highlight"), c.b.c["ink"],
                   el.get("align", "m"))


def terminal(c, im, el, t):
    """Typed terminal. Line prefixes: '$ ' prompt (good), '! ' error (bad), '+ ' added (good),
    '- ' removed (bad), '# ' comment (muted). cps: 0 shows all lines at once."""
    t0 = el.get("at", 0)
    u = pop(t, t0, 0.3)
    if u is None:
        return
    x, y, w = el.get("x", 70), el.get("y", 620), el.get("w", 940)
    size = el.get("size", 38)
    lines = el.get("lines", [])
    lh = size * 1.45
    h = el.get("h", 110 + lh * max(len(lines), 1))
    y += (1 - u) * 60
    soft_shadow(im, [x, y, x + w, y + h], 26)
    c.rr([x, y, x + w, y + h], 26, fill=(12, 12, 16), outline=(60, 60, 76), width=3)
    for i, cc in enumerate([(240, 96, 86), (252, 206, 74), (122, 214, 150)]):
        c.ell([x + 30 + i * 36, y + 26, x + 52 + i * 36, y + 48], fill=cc)
    if el.get("title"):
        c.text((x + w / 2, y + 37), el["title"], 26, "mono", c.b.c["muted"])
    cps = el.get("cps", 26)
    tt = (t - t0 - 0.25) * cps if cps else 1e9
    used = 0
    for i, ln in enumerate(lines):
        n = len(ln)
        if tt < used:
            break
        shown = ln[:int(tt - used)] if tt - used < n else ln
        used += n + el.get("line_pause", 6)
        fill = c.b.c["fg"]
        pre = ln[:2]
        if pre == "$ ":
            fill = c.b.c["good"]
        elif pre in ("! ", "- "):
            fill = c.b.c["bad"]
        elif pre == "+ ":
            fill = c.b.c["good"]
        elif pre == "# ":
            fill = c.b.c["muted"]
        ly = y + 92 + i * lh
        c.text((x + 36, ly), shown, size, "mono", fill, "lm")
        if shown != ln or i == len(lines) - 1:
            if int(t * 2.5) % 2 == 0:
                cx = x + 40 + c.tw(shown, size, "mono")
                c.rr([cx, ly - size * 0.45, cx + size * 0.5, ly + size * 0.45], 3, fill=c.b.c["fg"])
            if shown != ln:
                break


def bubble(c, im, el, t):
    u = pop(t, el.get("at", 0), 0.3)
    if u is None:
        return
    size = el.get("size", 46)
    x, w = el.get("x", 80), el.get("w", 760)
    lines = c.wrap(el["text"], size, "bold", w - 72)
    lh = size * 1.28
    h = 72 + lh * len(lines) + (size * 0.7 if el.get("who") else 0)
    y = el.get("y", 700) + (1 - u) * 40
    accent = col(c, el.get("color"), "accent")
    c.rr([x, y, x + w, y + h], 34, fill=c.b.c["panel"], outline=accent, width=4)
    tx = el.get("tail_x", x + 90)
    if el.get("tail", "down") == "down":
        c.poly([(tx - 24, y + h - 2), (tx + 24, y + h - 2), (tx, y + h + 40)], c.b.c["panel"])
        c.line([(tx - 24, y + h + 1), (tx, y + h + 40), (tx + 24, y + h + 1)], accent, 4)
    yy = y + 36
    if el.get("who"):
        c.text((x + 36, yy + 4), el["who"], size * 0.66, "bold", accent, "lm")
        yy += size * 0.8
    for i, ln in enumerate(lines):
        _rich_line(c, x + 36, yy + lh * i + lh / 2, ln, size, "bold", c.b.c["fg"],
                   c.b.c["highlight"], c.b.c["ink"], "l")


def sticker(c, im, el, t):
    u = pop(t, el.get("at", 0), 0.35)
    if u is None:
        return
    size = el.get("size", 42)
    f = c.f("display", size)
    lines = str(el["text"]).split("\n")
    from PIL import ImageDraw
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = max(tmp.textlength(ln, font=f) for ln in lines)
    lh = int(size * 1.22 * K)
    w, h = int(tw + 56 * K), lh * len(lines) + int(40 * K)
    s = Image.new("RGBA", (w + int(30 * K), h + int(30 * K)), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.rounded_rectangle([int(22 * K), int(22 * K), int(22 * K) + w, int(22 * K) + h], int(14 * K), fill=(0, 0, 0, 150))
    d.rounded_rectangle([int(14 * K), int(14 * K), int(14 * K) + w, int(14 * K) + h], int(14 * K),
                        fill=col(c, el.get("color"), "highlight"))
    for i, ln in enumerate(lines):
        d.text((int(42 * K), int(34 * K) + i * lh), ln, font=f, fill=col(c, el.get("text_color"), "ink"))
    sc = max(0.05, u)
    s = s.rotate(el.get("angle", -6), expand=True, resample=Image.BICUBIC)
    if sc != 1:
        s = s.resize((max(1, int(s.width * sc)), max(1, int(s.height * sc))), Image.BICUBIC)
    im.paste(s, (int(el.get("x", 540) * K - s.width / 2), int(el.get("y", 1100) * K - s.height / 2)), s)


def pill(c, im, el, t):
    u = pop(t, el.get("at", 0), 0.3)
    if u is None:
        return
    size = el.get("size", 44)
    w = c.tw(el["text"], size, "bold") + 64
    h = size * 1.75
    x, y = el.get("x", 540), el.get("y", 900) + (1 - u) * 40
    fill = col(c, el.get("color"), "accent")
    c.rr([x - w / 2, y - h / 2, x + w / 2, y + h / 2], h / 2, fill=fill)
    c.text((x, y), el["text"], size, "bold", col(c, el.get("text_color"), "ink"))


def checklist(c, im, el, t):
    """Items appear one by one every `step` seconds, each with a tick."""
    t0, step = el.get("at", 0), el.get("step", 0.6)
    size = el.get("size", 48)
    x, y = el.get("x", 110), el.get("y", 700)
    for i, item in enumerate(el.get("items", [])):
        u = pop(t, t0 + i * step, 0.3)
        if u is None:
            break
        yy = y + i * size * 1.9
        xx = x - (1 - u) * 80
        mark_col = col(c, el.get("color"), "good")
        c.rr([xx, yy - size * 0.55, xx + size * 1.1, yy + size * 0.55], 14, fill=mark_col)
        c.text((xx + size * 0.55, yy), el.get("mark", "✓"), size * 0.8, "bold", c.b.c["ink"])
        _rich_line(c, xx + size * 1.5, yy, item, size, "bold", c.b.c["fg"], c.b.c["highlight"], c.b.c["ink"], "l")


def stamp(c, im, el, t):
    t0 = el.get("at", 0)
    if t < t0:
        return
    u = clamp((t - t0) / 0.22)
    sc = lerp(2.2, 1.0, u)
    size = el.get("size", 120) * sc
    txt = el.get("text", "NOPE")
    w = c.tw(txt, size, "display") + 80 * sc
    h = size * 1.4
    x, y = el.get("x", 540), el.get("y", 900)
    from PIL import ImageDraw
    lay = Image.new("RGBA", (int(w * K) + 40, int(h * K) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cc = col(c, el.get("color"), "bad")
    a = int(255 * u)
    d.rounded_rectangle([20, 20, 20 + int(w * K), 20 + int(h * K)], int(20 * K), outline=cc + (a,), width=int(12 * K * sc))
    d.text((20 + w * K / 2, 20 + h * K / 2), txt, font=c.f("display", size), fill=cc + (a,), anchor="mm")
    lay = lay.rotate(el.get("angle", 12), expand=True, resample=Image.BICUBIC)
    im.paste(lay, (int(x * K - lay.width / 2), int(y * K - lay.height / 2)), lay)


_IMG = {}


def image(c, im, el, t):
    u = pop(t, el.get("at", 0), 0.3)
    if u is None:
        return
    src = el["src"]
    if not os.path.isabs(src):
        src = os.path.join(el.get("_base", "."), src)
    key = (src, el.get("w", 600))
    if key not in _IMG:
        img = Image.open(src).convert("RGBA")
        w = int(el.get("w", 600) * K)
        _IMG[key] = img.resize((w, int(img.height * w / img.width)), Image.LANCZOS)
    img = _IMG[key]
    x, y = el.get("x", 540), el.get("y", 900) + (1 - u) * 50
    im.paste(img, (int(x * K - img.width / 2), int(y * K - img.height / 2)), img)


def character(c, im, el, t):
    if t < el.get("at", 0):
        return
    if el.get("until") is not None and t >= el["until"]:
        return
    u = smooth((t - el.get("at", 0)) / 0.35) if el.get("enter", True) else 1
    x = el.get("x", 540)
    if el.get("enter_from"):
        x = lerp(el["enter_from"], x, back_out(u))
    talk = el.get("_talk", lambda tt: 0.0)(t)
    characters.draw(c, el.get("who", "person"), x, el.get("y", 1420), el.get("scale", 1.0),
                    el.get("_mood_at", lambda tt: el.get("mood", "neutral"))(t), t, talk,
                    c.b.raw.get("characters", {}), el.get("look"))


def progress_ring(c, im, el, t):
    """Countdown / loading ring: fills from `at` over `dur` seconds."""
    t0, dur = el.get("at", 0), el.get("dur", 2.0)
    if t < t0:
        return
    u = clamp((t - t0) / dur)
    x, y, r = el.get("x", 540), el.get("y", 900), el.get("r", 120)
    c.arc([x - r, y - r, x + r, y + r], 0, 360, c.b.c["panel"], 26)
    c.arc([x - r, y - r, x + r, y + r], -90, -90 + 360 * u, col(c, el.get("color"), "accent"), 26)
    c.text((x, y), el.get("text", f"{int(u * 100)}%"), r * 0.5, "display")


def stat(c, im, el, t):
    """Big number that counts up: value "73%", "$1,200", "3x"; label under it."""
    t0 = el.get("at", 0)
    u = pop(t, t0, 0.35)
    if u is None:
        return
    import re
    val = str(el.get("value", "100%"))
    m = re.search(r"[\d][\d,]*\.?\d*", val)
    shown = val
    if m and el.get("count_up", True):
        num = float(m.group().replace(",", ""))
        k = smooth((t - t0) / el.get("count_dur", 0.9))
        dec = len(m.group().split(".")[1]) if "." in m.group() else 0
        cur = num * k
        txt = f"{cur:,.{dec}f}" if "," in m.group() else f"{cur:.{dec}f}"
        shown = val[:m.start()] + txt + val[m.end():]
    x, y = el.get("x", 540), el.get("y", 860)
    size = el.get("size", 220)
    c.text((x, y + (1 - u) * 60), shown, size, "display", col(c, el.get("color"), "accent"))
    if el.get("label"):
        lsize = el.get("label_size", 50)
        for i, ln in enumerate(c.wrap(el["label"], lsize, "bold", el.get("w", 900))):
            _rich_line(c, x, y + size * 0.75 + i * lsize * 1.3 + (1 - u) * 60, ln, lsize, "bold", c.b.c["fg"],
                       c.b.c["highlight"], c.b.c["ink"], "m")


def quote(c, im, el, t):
    u = pop(t, el.get("at", 0), 0.35)
    if u is None:
        return
    size = el.get("size", 56)
    x, w = el.get("x", 90), el.get("w", 900)
    lines = c.wrap(el["text"], size, "bold", w - 120)
    lh = size * 1.3
    h = 150 + lh * len(lines) + (70 if el.get("author") else 0)
    y = el.get("y", 640) + (1 - u) * 50
    accent = col(c, el.get("color"), "accent")
    soft_shadow(im, [x, y, x + w, y + h], 30)
    c.rr([x, y, x + w, y + h], 30, fill=c.b.c["panel"])
    c.rr([x, y, x + 14, y + h], 7, fill=accent)
    c.text((x + 70, y + 70), "\u201c", size * 2.4, "display", accent, "lm")
    for i, ln in enumerate(lines):
        _rich_line(c, x + 70, y + 120 + lh * i + lh / 2, ln, size, "bold", c.b.c["fg"], c.b.c["highlight"], c.b.c["ink"], "l")
    if el.get("author"):
        c.text((x + 70, y + h - 50), "\u2014 " + el["author"], size * 0.62, "bold", c.b.c["muted"], "lm")


def split(c, im, el, t):
    """Two columns: myth vs fact, before vs after, don't vs do. Right side appears `step` s after left."""
    t0, step = el.get("at", 0), el.get("step", 1.2)
    y = el.get("y", 640)
    h = el.get("h", 480)
    size = el.get("size", 46)
    sides = [("left", 70, el.get("left", {}), "bad", "\u00d7"), ("right", 555, el.get("right", {}), "good", "\u2713")]
    for i, (_, x, side, dcol, mark) in enumerate(sides):
        u = pop(t, t0 + i * step, 0.35)
        if u is None:
            continue
        cc = col(c, side.get("color"), dcol)
        yy = y + (1 - u) * 60
        c.rr([x, yy, x + 455, yy + h], 30, fill=c.b.c["panel"], outline=cc, width=5)
        c.rr([x, yy, x + 455, yy + 96], 30, fill=cc)
        c.rr([x, yy + 60, x + 455, yy + 96], 0, fill=cc)
        c.text((x + 227, yy + 50), side.get("title", "BEFORE" if i == 0 else "AFTER"), 46, "display", c.b.c["ink"])
        ty = yy + 150
        for ln in c.wrap(side.get("text", ""), size, "bold", 390):
            _rich_line(c, x + 32, ty, ln, size, "bold", c.b.c["fg"], c.b.c["highlight"], c.b.c["ink"], "l")
            ty += size * 1.3
        for it in side.get("items", []):
            c.text((x + 44, ty), mark, size, "display", cc)
            for j, ln in enumerate(c.wrap(it, size * 0.9, "bold", 340)):
                _rich_line(c, x + 84, ty + j * size * 1.15, ln, size * 0.9, "bold", c.b.c["fg"], c.b.c["highlight"], c.b.c["ink"], "l")
            ty += size * 1.15 * len(c.wrap(it, size * 0.9, "bold", 340)) + size * 0.5
    if el.get("vs", True) and pop(t, t0 + step, 0.3) is not None:
        c.ell([540 - 52, y + h / 2 - 52, 540 + 52, y + h / 2 + 52], fill=c.b.c["highlight"])
        c.text((540, y + h / 2), el.get("vs_text", "VS"), 40, "display", c.b.c["ink"])


_PHOTO = {}


def photo(c, im, el, t):
    """Photo in a rounded frame with a slow zoom/pan (Ken Burns). zoom: [start, end] over `dur` s."""
    t0 = el.get("at", 0)
    u = pop(t, t0, 0.35)
    if u is None:
        return
    src = el["src"]
    if not os.path.isabs(src):
        src = os.path.join(el.get("_base", "."), src)
    if src not in _PHOTO:
        _PHOTO[src] = Image.open(src).convert("RGB")
    img = _PHOTO[src]
    w, h = el.get("w", 940), el.get("h", 700)
    x, y = el.get("x", 540) - w / 2, el.get("y", 860) - h / 2 + (1 - u) * 50
    z0, z1 = el.get("zoom", [1.0, 1.15])
    z = lerp(z0, z1, (t - t0) / el.get("dur", 5.0))
    ar = w / h
    cw = min(img.width, img.height * ar) / z
    ch = cw / ar
    px, py = el.get("pan", [0.5, 0.5])
    cx = (img.width - cw) * px
    cy = (img.height - ch) * py
    crop = img.resize((int(w * K), int(h * K)), Image.LANCZOS, box=(cx, cy, cx + cw, cy + ch))
    mask = Image.new("L", crop.size, 0)
    from PIL import ImageDraw
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, crop.width - 1, crop.height - 1], int(el.get("radius", 30) * K), fill=255)
    soft_shadow(im, [x, y, x + w, y + h], el.get("radius", 30))
    im.paste(crop, (int(x * K), int(y * K)), mask)
    if el.get("caption"):
        pill(c, im, {"text": el["caption"], "x": x + w / 2, "y": y + h - 60, "at": t0, "color": el.get("color"), "size": 40}, t)


def numbered(c, im, el, t):
    """Top-N list. countdown: true shows N..1 (best last). Items appear every `step` s."""
    t0, step = el.get("at", 0), el.get("step", 1.0)
    items = el.get("items", [])
    size = el.get("size", 50)
    x, y = el.get("x", 90), el.get("y", 620)
    gap = el.get("gap", size * 2.4)
    n = len(items)
    for i, it in enumerate(items):
        u = pop(t, t0 + i * step, 0.3)
        if u is None:
            break
        num = n - i if el.get("countdown", False) else i + 1
        yy = y + i * gap
        xx = x - (1 - u) * 80
        cc = col(c, el.get("color"), "accent")
        c.rr([xx, yy - size * 0.85, xx + size * 1.7, yy + size * 0.85], 22, fill=cc)
        c.text((xx + size * 0.85, yy), str(num), size * 1.1, "display", c.b.c["ink"])
        lines = c.wrap(it, size, "bold", 900 - size * 2.2 - (x - 60))
        for j, ln in enumerate(lines):
            _rich_line(c, xx + size * 2.2, yy + (j - (len(lines) - 1) / 2) * size * 1.2, ln, size, "bold",
                       c.b.c["fg"], c.b.c["highlight"], c.b.c["ink"], "l")


def emoji_el(c, im, el, t):
    """A big emoji that pops (and optionally bounces). Needs a colour emoji font (see reelkit check)."""
    from . import emoji as E
    t0 = el.get("at", 0)
    u = pop(t, t0, 0.4)
    if u is None:
        return
    size = el.get("size", 200) * max(0.05, u)
    bounce = abs(math.sin((t - t0) * 4)) * 24 if el.get("bounce", False) else 0
    g = E.glyph(el.get("char", "\U0001F525"), size * K)
    if g is None:
        return
    g = g.rotate(el.get("angle", 0), expand=True, resample=Image.BICUBIC)
    im.paste(g, (int(el.get("x", 540) * K - g.width / 2), int((el.get("y", 900) - bounce) * K - g.height / 2)), g)


def subtitle(c, im, text_, t_line, brand_y=1340, dur=None, max_lines=2):
    """Burned-in subtitle used by dialogue lines. Long lines are shown 2 lines at a time,
    paged by how far into the line we are (pages get time in proportion to their length)."""
    size = 50
    lines = c.wrap(text_, size, "bold", 860)
    if dur and len(lines) > max_lines:
        pages = [lines[i:i + max_lines] for i in range(0, len(lines), max_lines)]
        weights = [sum(len(x) for x in pg) for pg in pages]
        u, acc = max(0.0, t_line) / dur * sum(weights), 0
        lines = pages[-1]
        for pg, w in zip(pages, weights):
            acc += w
            if u < acc:
                lines = pg
                break
    lh = size * 1.25
    h = lh * len(lines) + 40
    y0 = brand_y - h
    w = max(c.tw(ln.replace("*", ""), size, "bold") for ln in lines) + 60
    c.rr([540 - w / 2, y0, 540 + w / 2, y0 + h], 22, fill=(0, 0, 0))
    for i, ln in enumerate(lines):
        _rich_line(c, 540, y0 + 20 + lh * i + lh / 2, ln, size, "bold", c.b.c["fg"],
                   c.b.c["highlight"], c.b.c["ink"], "m")


TYPES = {
    "headline": headline, "text": text, "terminal": terminal, "bubble": bubble, "sticker": sticker,
    "pill": pill, "checklist": checklist, "stamp": stamp, "image": image, "character": character,
    "progress_ring": progress_ring, "stat": stat, "quote": quote, "split": split, "photo": photo,
    "list": numbered, "emoji": emoji_el,
}


def draw(c, im, el, t):
    fn = TYPES.get(el.get("type"))
    if fn is None:
        raise ValueError(f"unknown element type '{el.get('type')}'. Known: {sorted(TYPES)}")
    if el.get("until") is not None and t >= el["until"] and el["type"] != "character":
        return
    fn(c, im, el, t)

