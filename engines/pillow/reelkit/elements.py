"""Scene elements. Each element is a dict from scenes.yaml with a `type` and an `at` time (seconds
from scene start). Every draw function gets (c, im, el, t) where t is the scene-local time.

Colours accept brand keys (fg, muted, accent, highlight, good, bad, panel, ink, info) or "#rrggbb".
Text marked with *stars* is highlighted (headline, text, bubble).
"""
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
    characters.draw(c, el.get("who", "dev"), x, el.get("y", 1420), el.get("scale", 1.0),
                    el.get("_mood_at", lambda tt: el.get("mood", "neutral"))(t), t, talk,
                    c.b.raw.get("characters", {}).get(el.get("who", "dev")))


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


def subtitle(c, im, text_, t_line, brand_y=1340):
    """Burned-in subtitle used by dialogue lines."""
    size = 50
    lines = c.wrap(text_, size, "bold", 860)
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
    "progress_ring": progress_ring,
}


def draw(c, im, el, t):
    fn = TYPES.get(el.get("type"))
    if fn is None:
        raise ValueError(f"unknown element type '{el.get('type')}'. Known: {sorted(TYPES)}")
    if el.get("until") is not None and t >= el["until"] and el["type"] != "character":
        return
    fn(c, im, el, t)

