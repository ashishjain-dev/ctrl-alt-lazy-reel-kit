"""Style Drop: one hero scene shown in N art styles, cut into one reel.

scenes.yaml:
    style_drop:
      file: kite_scene.py      # the scene, drawn by a file next to scenes.yaml: draw(ctx, t, args), ctx.style = style
      impact: 2.0              # the big moment (s), same in every style
      clip_dur: 5.0
      styles: [fish-scale-folk, rice-paper, mud-wall, cyan-plan, cut-card]
      title: ["5 Kite", "art styles"]
      card_dur: 2.0          # seconds per style card
      clip_offset: 1.05      # clip time shown at the start of each card (impact lands at 2.0 - 1.05 = 0.95 s in)
      outro: 3.0
      cta: "COMMENT 'KITE' FOR THE PROMPTS"
      bg: "#f4ecdc"

Layout: title on top, numbered list of styles on the left (each name appears with its card), a 9:16
card on the right that wipes to the next style every `card_dur`, then an outro of moving tiles + CTA.
"""
import math

from PIL import Image, ImageDraw

from ..brand import hex2rgb
from ..draw import K, Cv, smooth
from . import STYLES

CARD = (470, 440, 1010, 1400)          # x0, y0, x1, y1 (9:16, 540 x 960)
NAMES = {"fish-scale-folk": "Fish-Scale Folk", "rice-paper": "Rice Paper", "mud-wall": "Mud Wall",
         "cyan-plan": "Cyan Plan", "cut-card": "Cut Card", "cel-burst": "Cel Burst",
         "gold-court": "Gold Court", "flat": "Flat"}


def label(style):
    return NAMES.get(style, style.replace("-", " ").title())


def build_scenes(cfg):
    """Expand a style_drop block into ordinary scenes (so audio, timing and stills all just work)."""
    styles = cfg.get("styles") or [s for s in STYLES if s != "flat"]
    cd = float(cfg.get("card_dur", 2.0))
    off = float(cfg.get("clip_offset", 1.05))
    if not cfg.get("file"):
        raise ValueError("style_drop needs `file:` (a scene file next to scenes.yaml, see docs/custom-art.md) and `impact:`")
    cut_in = float(cfg.get("impact", 2.0)) - off
    scenes = []
    for i, st in enumerate(styles):
        scenes.append({"name": f"card{i + 1}", "dur": cd, "no_punch": True, "whoosh": i > 0,
                       "punch": [cut_in], "sfx": [{"at": cut_in, "kind": "hit", "gain": 0.35}],
                       "elements": [{"type": "drop_frame", "i": i, "styles": styles, "cfg": cfg, "sfx": "none"}]})
    scenes.append({"name": "outro", "dur": float(cfg.get("outro", 3.0)), "no_punch": True,
                   "sfx": [{"at": 0.2, "kind": "ding"}],
                   "elements": [{"type": "drop_outro", "styles": styles, "cfg": cfg, "sfx": "none"}]})
    return scenes


def _bg(c, im, cfg):
    col = hex2rgb(cfg.get("bg", "#f4ecdc"))
    im.paste(col, (0, 0, im.width, im.height))
    return col


def _render_style(scene, style, t, w, h):
    """Render the scene file in a style at full size, return it scaled to w x h (supersampled px)."""
    big = Image.new("RGB", (1080 * K, 1920 * K))
    from ..brand import Brand
    b = Brand()
    from ..custom import draw_element
    from . import style_class
    b.c.update(style_class(style).brand)
    draw_element(Cv(big, b), big, {**scene, "style": style}, t)
    return big.resize((int(w * K), int(h * K)), Image.LANCZOS)


def _scene_ref(cfg):
    return {"file": cfg["file"], "_base": cfg.get("_base", "."), "args": cfg.get("args", {})}


def _rounded(img, r):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, img.width - 1, img.height - 1], int(r * K), fill=255)
    return m


def drop_frame(c, im, el, t):
    cfg, styles, i = el["cfg"], el["styles"], el["i"]
    ink = hex2rgb(cfg.get("ink", "#1d1a17"))
    accent = hex2rgb(cfg.get("accent", "#d6452c"))
    muted = hex2rgb(cfg.get("muted", "#9c9284"))
    _bg(c, im, cfg)
    title = cfg.get("title", [f"{len(styles)} art styles", "one scene"])
    c.text((540, 300), title[0], 96, "display", ink)
    if len(title) > 1:
        c.text((540, 385), title[1], 50, "bold", accent)
    # numbered list
    for k, st in enumerate(styles):
        if k > i:
            break
        y = 520 + k * 96
        a = smooth(t / 0.3) if k == i else 1.0
        active = k == i
        x = 70 - (1 - a) * 40
        if active:
            w = c.tw(f"{k + 1}  {label(st)}", 40, "bold") + 40
            c.rr([x - 14, y - 34, x - 14 + w, y + 34], 34, fill=accent)
        col = (255, 255, 255) if active else (ink if k < i else muted)
        c.text((x + 6, y), f"{k + 1}", 40, "display", col, "lm")
        c.text((x + 52, y), label(st), 36 if not active else 38, "bold", col, "lm")
    # card with wipe from the previous style
    x0, y0, x1, y1 = CARD
    w, h = x1 - x0, y1 - y0
    scene = _scene_ref(cfg)
    off = float(cfg.get("clip_offset", 1.05))
    cur = _render_style(scene, styles[i], off + t, w, h)
    wipe = float(cfg.get("wipe", 0.28))
    if i > 0 and t < wipe:
        prev = _render_style(scene, styles[i - 1], off + float(cfg.get("card_dur", 2.0)) + t, w, h)
        u = smooth(t / wipe)
        edge = int(cur.width * u * 1.3)
        mask = Image.new("L", cur.size, 0)
        ImageDraw.Draw(mask).polygon([(0, 0), (edge, 0), (edge - cur.width * 0.3, cur.height), (0, cur.height)], fill=255)
        prev.paste(cur, (0, 0), mask)
        cur = prev
    sh = Image.new("L", (cur.width, cur.height), 0)
    ImageDraw.Draw(sh).rounded_rectangle([0, 0, cur.width - 1, cur.height - 1], int(26 * K), fill=110)
    im.paste((0, 0, 0), (int((x0 + 10) * K), int((y0 + 16) * K)), sh)
    im.paste(cur, (int(x0 * K), int(y0 * K)), _rounded(cur, 26))
    c.rr([x0 - 4, y0 - 4, x1 + 4, y1 + 4], 30, outline=ink, width=6)
    # step counter under the card
    c.text(((x0 + x1) / 2, y1 + 50), f"{i + 1} / {len(styles)}", 30, "bold", muted)


def drop_outro(c, im, el, t):
    cfg, styles = el["cfg"], el["styles"]
    ink = hex2rgb(cfg.get("ink", "#1d1a17"))
    accent = hex2rgb(cfg.get("accent", "#d6452c"))
    _bg(c, im, cfg)
    scene = _scene_ref(cfg)
    tw, th = 300, 533
    cols = 3
    n = len(styles)
    for k in range(n + (cols - n % cols) % cols + cols):          # a moving wall of tiles, wraps vertically
        st = styles[k % n]
        col, row = k % cols, k // cols
        x = 40 + col * (tw + 30)
        y = 160 + row * (th + 30) - 90 * t - (col % 2) * 140
        if y > 1920 or y + th < 0:
            continue
        clip_t = (2.0 + t * 0.9 + k * 0.37) % float(cfg.get("clip_dur", 5.0))
        tile = _render_style(scene, st, clip_t, tw, th)
        im.paste(tile, (int(x * K), int(y * K)), _rounded(tile, 20))
    # darken a band and put the CTA on it
    band = Image.new("L", (im.width, int(520 * K)), int(170 * smooth(t / 0.4)))
    im.paste((20, 18, 16), (0, int(700 * K)), band)
    cta = cfg.get("cta", "COMMENT 'STYLE' FOR THE PROMPTS")
    lines = cta.split("\n") if "\n" in cta else _split2(cta)
    u = smooth((t - 0.2) / 0.4)
    if u > 0:
        for j, ln in enumerate(lines):
            size = 92 if j == 0 else 64
            c.text((540, 880 + j * 120 + (1 - u) * 40), ln, size, "display", (255, 255, 255) if j else accent)
    _ = ink, math


def _split2(s):
    words = s.split()
    if len(words) < 3:
        return [s]
    return [" ".join(words[:2]), " ".join(words[2:])]
