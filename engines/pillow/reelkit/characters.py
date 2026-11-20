"""Built-in, original characters. All are drawn from code, so there is nothing to license.

    person  - a customizable human: hair, hat, glasses, headphones, beard, shirt icon, colours
    bot     - monitor-head robot with pixel eyes and an antenna
    blob    - round jelly mascot with big eyes (good for kids, food, wellness, finance...)
    dev     - preset: person with headphones and a </> shirt

Every character takes (c: Cv, x, y, scale, mood, t, talk, opts). (x, y) is the bottom-centre (feet),
`talk` is mouth opening 0..1 (lip sync), `t` is local time (blinks, idle motion), `opts` the look.
Moods: neutral, happy, sad, shocked, angry, deadpan, smug, think, wink (+ error, love for bot/blob).

Named characters live in brand.yaml so a whole series reuses them:
    characters:
      maya: {base: person, hair: long, hair_color: "#5a3524", skin: "#c68c64", shirt: "#e8805c", glasses: true}
      coach: {base: person, hair: bald, beard: true, shirt_icon: "FIT"}
    ...then `who: maya` in scenes.yaml.
"""
import math

from .brand import hex2rgb

INK = (20, 20, 26)
WHITE = (250, 250, 252)
MOUTH = (90, 30, 40)

PERSON_DEFAULT = {
    "skin": "#f1c7a3", "hair_color": "#3a2a24", "shirt": "#3fa796", "pants": "#2c3450", "accent": "#e8805c",
    "hair": "short",          # short | long | curly | bun | spiky | bald
    "hat": "none",            # none | cap | beanie
    "glasses": False, "headphones": False, "beard": False,
    "shirt_icon": "",         # short text on the shirt, e.g. "</>", "FIT", "$"
    "cheeks": True,
}
BOT_DEFAULT = {"body": "#c9d2e0", "screen": "#141a26", "eyes": "#7af0c8", "trim": "#5a6a86"}
BLOB_DEFAULT = {"body": "#8fd0ff", "belly": "#d9f0ff", "accent": "#ff8fa3", "sprout": True}
PRESETS = {
    "dev": {"base": "person", "headphones": True, "shirt_icon": "</>"},
}
MOODS = ["neutral", "happy", "sad", "shocked", "angry", "deadpan", "smug", "think", "wink", "error", "love"]
COLOR_KEYS = {"skin", "hair_color", "shirt", "pants", "accent", "body", "screen", "eyes", "trim", "belly"}


def _opts(defaults, over):
    d = dict(defaults)
    d.update({k: v for k, v in (over or {}).items() if k != "base"})
    # backwards-compatible names
    if "hair" in d and isinstance(d["hair"], str) and d["hair"].startswith("#"):
        d["hair_color"], d["hair"] = d["hair"], defaults.get("hair", "short")
    if "phones" in d:
        d["accent"] = d.pop("phones")
    return {k: (hex2rgb(v) if k in COLOR_KEYS else v) for k, v in d.items()}


def _blink(t, seed=0.0):
    return 0.12 if (t + seed) % 3.7 < 0.12 else 1.0


def _face(c, x, ey, my, s, mood, t, talk, eye_col=INK, eye_dx=62, cheeks=True, mouth_w=34):
    """Shared cartoon face: eyes at ey, mouth at my, spacing eye_dx (unscaled)."""
    S = lambda v: v * s  # noqa: E731
    bl = _blink(t)
    for sx in (-1, 1):
        ex = x + sx * S(eye_dx)
        if mood in ("happy", "smug", "love") or (mood == "wink" and sx > 0):
            c.arc([ex - S(26), ey - S(18), ex + S(26), ey + S(30)], 200, 340, eye_col, S(10))
        elif mood == "deadpan":
            c.line([(ex - S(28), ey), (ex + S(28), ey)], eye_col, S(10))
            c.ell([ex - S(10), ey, ex + S(10), ey + S(18)], fill=eye_col)
        elif mood == "shocked":
            c.ell([ex - S(32), ey - S(36), ex + S(32), ey + S(36)], fill=WHITE, outline=eye_col, width=S(5))
            c.ell([ex - S(11), ey - S(11), ex + S(11), ey + S(11)], fill=eye_col)
        else:
            h = S(22) * bl
            c.ell([ex - S(18), ey - h, ex + S(18), ey + h], fill=eye_col)
            c.ell([ex - S(4), ey - h * 0.6, ex + S(6), ey - h * 0.15], fill=WHITE)
        if mood == "angry":
            c.line([(ex - sx * S(34), ey - S(60)), (ex + sx * S(30), ey - S(40))], eye_col, S(10))
        elif mood == "sad":
            c.line([(ex - sx * S(34), ey - S(40)), (ex + sx * S(30), ey - S(58))], eye_col, S(10))
        elif mood == "think":
            c.line([(ex - S(30), ey - S(52 + sx * 8)), (ex + S(30), ey - S(52 - sx * 8))], eye_col, S(9))
    if cheeks and mood in ("happy", "smug", "love", "wink"):
        for sx in (-1, 1):
            c.ell([x + sx * S(eye_dx + 48) - S(24), my - S(40), x + sx * S(eye_dx + 48) + S(24), my - S(14)], fill=(240, 150, 140))
    if talk > 0.05:
        h = S(10 + 46 * talk)
        c.rr([x - S(mouth_w), my - h / 2, x + S(mouth_w), my + h / 2], min(S(30), h / 2), fill=MOUTH)
    elif mood in ("happy", "love", "wink"):
        c.arc([x - S(46), my - S(40), x + S(46), my + S(26)], 20, 160, eye_col, S(10))
    elif mood == "smug":
        c.arc([x - S(20), my - S(30), x + S(56), my + S(14)], 20, 140, eye_col, S(9))
    elif mood == "sad":
        c.arc([x - S(40), my, x + S(40), my + S(50)], 200, 340, eye_col, S(10))
    elif mood == "shocked":
        c.ell([x - S(24), my - S(20), x + S(24), my + S(34)], fill=MOUTH)
    elif mood == "think":
        c.line([(x - S(14), my + S(6)), (x + S(30), my - S(4))], eye_col, S(9))
    else:
        c.line([(x - S(30), my), (x + S(30), my)], eye_col, S(10))


def person(c, x, y, s, mood="neutral", t=0.0, talk=0.0, opts=None):
    o = _opts(PERSON_DEFAULT, opts)
    y = y + math.sin(t * 2.2) * 4 * s
    S = lambda v: v * s  # noqa: E731
    skin, hc, acc = o["skin"], o["hair_color"], o["accent"]
    # long hair falls behind the body
    hx0, hy0, hx1, hy1 = x - S(165), y - S(700), x + S(165), y - S(345)
    if o["hair"] == "long":
        c.rr([hx0 - S(14), hy0 + S(40), hx1 + S(14), y - S(250)], S(110), fill=hc)
    # legs + body
    c.rr([x - S(70), y - S(150), x - S(16), y], S(20), fill=o["pants"])
    c.rr([x + S(16), y - S(150), x + S(70), y], S(20), fill=o["pants"])
    c.rr([x - S(120), y - S(360), x + S(120), y - S(120)], S(60), fill=o["shirt"])
    if o["shirt_icon"]:
        size = S(56) if len(o["shirt_icon"]) <= 3 else S(40)
        c.text((x, y - S(250)), o["shirt_icon"], size, "display", INK)
    arm = {"shocked": -60, "happy": -30, "angry": -10, "think": -40}.get(mood, 20)
    for sx in (-1, 1):
        ax = x + sx * S(118)
        a = arm if not (mood == "think" and sx < 0) else 20
        c.line([(ax, y - S(320)), (ax + sx * S(40), y - S(220) + S(a))], o["shirt"], S(40))
        c.ell([ax + sx * S(40) - S(24), y - S(244) + S(a), ax + sx * S(40) + S(24), y - S(196) + S(a)], fill=skin)
    # head
    c.rr([hx0, hy0, hx1, hy1], S(120), fill=skin)
    for sx in (-1, 1):  # ears
        c.ell([x + sx * S(165) - S(22), y - S(560), x + sx * S(165) + S(22), y - S(500)], fill=skin)
    hair = o["hair"]
    if hair in ("short", "long", "bun"):
        c.rr([hx0 - S(4), hy0 - S(16), hx1 + S(4), hy0 + S(95)], S(70), fill=hc)
        c.poly([(hx0 + S(40), hy0 + S(80)), (x + S(60), hy0 + S(80)), (hx0 + S(40), hy0 + S(150))], hc)
        if hair == "long":
            for sx in (-1, 1):
                c.rr([x + sx * S(150) - S(32), hy0 + S(40), x + sx * S(150) + S(32), y - S(420)], S(30), fill=hc)
        if hair == "bun":
            c.ell([x - S(70), hy0 - S(110), x + S(70), hy0 + S(20)], fill=hc)
    elif hair == "curly":
        for i in range(9):
            a = math.pi * (0.05 + 0.9 * i / 8)
            cx, cy = x - math.cos(a) * S(150), hy0 + S(70) - math.sin(a) * S(80)
            c.ell([cx - S(52), cy - S(52), cx + S(52), cy + S(52)], fill=hc)
    elif hair == "spiky":
        pts = [(hx0, hy0 + S(90))]
        for i in range(6):
            px = hx0 + S(330) * i / 6
            pts += [(px, hy0 + S(10)), (px + S(27), hy0 - S(50))]
        pts += [(hx1, hy0 + S(10)), (hx1, hy0 + S(90))]
        c.poly(pts, hc)
    if o["hat"] == "cap":
        c.rr([hx0 - S(6), hy0 - S(30), hx1 + S(6), hy0 + S(80)], S(80), fill=acc)
        c.rr([x - S(20), hy0 + S(50), hx1 + S(90), hy0 + S(90)], S(20), fill=acc)
    elif o["hat"] == "beanie":
        c.rr([hx0 - S(8), hy0 - S(40), hx1 + S(8), hy0 + S(90)], S(90), fill=acc)
        c.rr([hx0 - S(12), hy0 + S(50), hx1 + S(12), hy0 + S(100)], S(20), fill=tuple(int(v * 0.8) for v in acc))
        c.ell([x - S(30), hy0 - S(80), x + S(30), hy0 - S(20)], fill=acc)
    if o["headphones"]:
        c.arc([hx0 - S(26), hy0 - S(46), hx1 + S(26), hy1 - S(60)], 190, 350, acc, S(26))
        for sx in (-1, 1):
            ex = x + sx * S(170)
            c.rr([ex - S(34), y - S(560), ex + S(34), y - S(450)], S(26), fill=acc)
    ey, my = y - S(530), y - S(430)
    if o["beard"]:
        c.rr([hx0 + S(20), my - S(50), hx1 - S(20), hy1 + S(20)], S(110), fill=hc)
        c.rr([x - S(60), my - S(26), x + S(60), my + S(26)], S(26), fill=skin)
    _face(c, x, ey, my, s, mood, t, talk, INK, 62, o["cheeks"])
    if o["glasses"]:
        for sx in (-1, 1):
            ex = x + sx * S(62)
            c.rr([ex - S(48), ey - S(38), ex + S(48), ey + S(38)], S(16), outline=INK, width=S(8))
        c.line([(x - S(14), ey - S(6)), (x + S(14), ey - S(6))], INK, S(8))


def bot(c, x, y, s, mood="neutral", t=0.0, talk=0.0, opts=None):
    col = _opts(BOT_DEFAULT, opts)
    hover = math.sin(t * 2.6) * 10 * s
    y = y + hover
    S = lambda v: v * s  # noqa: E731
    c.ell([x - S(90), y - S(14) - hover, x + S(90), y + S(14) - hover], fill=(0, 0, 0))
    c.rr([x - S(55), y - S(90), x + S(55), y - S(40)], S(24), fill=col["trim"])
    c.rr([x - S(110), y - S(300), x + S(110), y - S(80)], S(50), fill=col["body"])
    c.ell([x - S(26), y - S(220), x + S(26), y - S(168)], fill=col["eyes"])
    wave = math.sin(t * 6) * 20 if mood in ("happy", "love") else 0
    for sx in (-1, 1):
        ax = x + sx * S(110)
        w = S(wave) if sx > 0 else 0
        c.line([(ax, y - S(250)), (ax + sx * S(60), y - S(180) - w)], col["trim"], S(22))
        c.ell([ax + sx * S(60) - S(22), y - S(202) - w, ax + sx * S(60) + S(22), y - S(158) - w], fill=col["body"])
    c.rr([x - S(30), y - S(340), x + S(30), y - S(290)], S(10), fill=col["trim"])
    hx0, hy0, hx1, hy1 = x - S(190), y - S(640), x + S(190), y - S(330)
    c.rr([hx0, hy0, hx1, hy1], S(56), fill=col["body"])
    c.rr([hx0 + S(26), hy0 + S(26), hx1 - S(26), hy1 - S(26)], S(36), fill=col["screen"])
    c.line([(x, hy0), (x, hy0 - S(70))], col["trim"], S(12))
    pulse = 0.5 + 0.5 * math.sin(t * 5)
    c.ell([x - S(22), hy0 - S(104), x + S(22), hy0 - S(60)], fill=tuple(int(v * (0.7 + 0.3 * pulse)) for v in col["eyes"]))
    e = col["eyes"] if mood != "error" else (240, 96, 86)
    ey, my = y - S(510), y - S(415)
    bl = _blink(t, 1.3)
    for sx in (-1, 1):
        ex = x + sx * S(72)
        if mood in ("happy", "smug") or (mood == "wink" and sx > 0):
            c.arc([ex - S(30), ey - S(20), ex + S(30), ey + S(36)], 200, 340, e, S(14))
        elif mood == "love":
            c.ell([ex - S(26), ey - S(22), ex - S(2), ey + S(2)], fill=e)
            c.ell([ex + S(2), ey - S(22), ex + S(26), ey + S(2)], fill=e)
            c.poly([(ex - S(26), ey - S(6)), (ex + S(26), ey - S(6)), (ex, ey + S(26))], e)
        elif mood == "error":
            c.line([(ex - S(22), ey - S(22)), (ex + S(22), ey + S(22))], e, S(12))
            c.line([(ex - S(22), ey + S(22)), (ex + S(22), ey - S(22))], e, S(12))
        elif mood == "deadpan":
            c.rr([ex - S(30), ey - S(4), ex + S(30), ey + S(10)], S(4), fill=e)
        elif mood == "shocked":
            c.ell([ex - S(34), ey - S(34), ex + S(34), ey + S(34)], outline=e, width=S(10))
        elif mood == "sad":
            c.rr([ex - S(24), ey - S(10), ex + S(24), ey + S(26) * bl], S(10), fill=e)
            c.line([(ex - sx * S(30), ey - S(24)), (ex + sx * S(26), ey - S(40))], e, S(8))
        elif mood == "angry":
            c.rr([ex - S(24), ey - S(10), ex + S(24), ey + S(26)], S(8), fill=e)
            c.line([(ex - sx * S(30), ey - S(40)), (ex + sx * S(26), ey - S(20))], e, S(9))
        elif mood == "think":
            c.rr([ex - S(22), ey - S(12) + sx * S(8), ex + S(22), ey + S(12) + sx * S(8)], S(8), fill=e)
        else:
            h = S(34) * bl
            c.rr([ex - S(22), ey - h / 2, ex + S(22), ey + h / 2], S(10), fill=e)
    if talk > 0.05:
        for i in range(7):
            hh = S(8 + 40 * talk * (0.5 + 0.5 * math.sin(t * 30 + i * 1.7)))
            bx = x - S(70) + i * S(20)
            c.rr([bx, my - hh / 2, bx + S(12), my + hh / 2], S(4), fill=e)
    elif mood in ("happy", "love", "wink"):
        c.arc([x - S(50), my - S(36), x + S(50), my + S(20)], 20, 160, e, S(10))
    elif mood == "sad":
        c.arc([x - S(40), my, x + S(40), my + S(40)], 200, 340, e, S(10))
    elif mood == "shocked":
        c.ell([x - S(20), my - S(16), x + S(20), my + S(24)], outline=e, width=S(8))
    else:
        c.rr([x - S(44), my - S(5), x + S(44), my + S(5)], S(4), fill=e)


def blob(c, x, y, s, mood="neutral", t=0.0, talk=0.0, opts=None):
    o = _opts(BLOB_DEFAULT, opts)
    S = lambda v: v * s  # noqa: E731
    sq = 1 + 0.04 * math.sin(t * 3.2)                 # idle squash and stretch
    if mood in ("happy", "love"):
        sq = 1 + 0.08 * abs(math.sin(t * 6))
    w, h = S(230) / sq ** 0.5, S(250) * sq
    c.ell([x - S(150), y - S(16), x + S(150), y + S(16)], fill=(0, 0, 0))
    for sx in (-1, 1):  # feet
        c.ell([x + sx * S(70) - S(46), y - S(40), x + sx * S(70) + S(46), y + S(4)], fill=tuple(int(v * 0.8) for v in o["body"]))
    cy = y - h - S(20)
    c.ell([x - w, cy - h, x + w, cy + h], fill=o["body"])
    c.ell([x - w * 0.62, cy - h * 0.1, x + w * 0.62, cy + h * 0.85], fill=o["belly"])
    c.ell([x - w * 0.75, cy - h * 0.8, x - w * 0.45, cy - h * 0.5], fill=(255, 255, 255))  # shine
    if o["sprout"]:
        top = cy - h
        c.line([(x, top + S(10)), (x + S(6), top - S(50))], (90, 170, 110), S(10))
        c.ell([x + S(6), top - S(80), x + S(70), top - S(40)], fill=(110, 200, 120))
        c.ell([x - S(56), top - S(70), x + S(8), top - S(34)], fill=(110, 200, 120))
    if mood == "error":
        mood = "shocked"
    _face(c, x, cy - S(20), cy + S(80), s * 1.05, mood, t, talk, INK, 70, True, 30)
    for sx in (-1, 1):  # little arms
        ax = x + sx * w * 0.98
        lift = S(60) if mood in ("happy", "shocked", "love") else 0
        c.line([(ax, cy + S(40)), (ax + sx * S(50), cy + S(90) - lift)], o["body"], S(30))


CHARACTERS = {"person": person, "bot": bot, "blob": blob}


def resolve(who, brand_chars=None):
    """Return (draw_fn, opts) for a character name: built-in, preset, or named in brand.yaml."""
    brand_chars = brand_chars or {}
    spec = {}
    name = who
    seen = 0
    while name not in CHARACTERS:
        nxt = ({**PRESETS.get(name, {}), **brand_chars.get(name, {})}) or None
        if not nxt or seen > 5:
            raise ValueError(f"unknown character '{who}'. Built-in: {sorted(CHARACTERS)} + presets {sorted(PRESETS)}; "
                             "or define it under brand.yaml > characters with a `base:`")
        spec = {**nxt, **spec}
        name = nxt.get("base", "person")
        seen += 1
    # brand.yaml may also recolour a built-in directly (characters: {bot: {...}})
    if who in CHARACTERS and who in brand_chars:
        spec = {**brand_chars[who], **spec}
    return CHARACTERS[name], spec


def draw(c, who, x, y, scale=1.0, mood="neutral", t=0.0, talk=0.0, brand_chars=None, look=None):
    fn, opts = resolve(who, brand_chars)
    if look:
        opts = {**opts, **look}
    fn(c, x, y, scale, mood, t, talk, opts)
