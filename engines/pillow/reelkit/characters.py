"""Two neutral, original characters you can recolour in brand.yaml > characters.

    dev  - rounded head, short flat hair, headphones, t-shirt. Moods below.
    bot  - monitor-head robot with pixel eyes and an antenna.

Both take: (c: Cv, x, y, scale, mood, t, talk) where (x, y) is the bottom-centre (feet) point,
`talk` is 0..1 mouth opening (lip sync), and `t` is the local time (for blinks and idle bob).
Moods: neutral, happy, sad, shocked, angry, deadpan, smug, think (dev); bot also has: error, love.
Replace or add characters by registering a function in CHARACTERS.
"""
import math

from .brand import hex2rgb

INK = (20, 20, 26)
WHITE = (250, 250, 252)

DEV_DEFAULT = {"skin": "#f1c7a3", "hair": "#3a2a24", "shirt": "#3fa796", "phones": "#e8805c", "pants": "#2c3450"}
BOT_DEFAULT = {"body": "#c9d2e0", "screen": "#141a26", "eyes": "#7af0c8", "trim": "#5a6a86"}


def _cols(defaults, over):
    d = dict(defaults)
    d.update(over or {})
    return {k: hex2rgb(v) for k, v in d.items()}


def _blink(t, seed=0.0):
    ph = (t + seed) % 3.7
    return 0.12 if ph < 0.12 else 1.0


def dev(c, x, y, s, mood="neutral", t=0.0, talk=0.0, colors=None):
    col = _cols(DEV_DEFAULT, colors)
    bob = math.sin(t * 2.2) * 4 * s
    y = y + bob
    S = lambda v: v * s  # noqa: E731
    # legs + body
    c.rr([x - S(70), y - S(150), x - S(16), y], S(20), fill=col["pants"])
    c.rr([x + S(16), y - S(150), x + S(70), y], S(20), fill=col["pants"])
    c.rr([x - S(120), y - S(360), x + S(120), y - S(120)], S(60), fill=col["shirt"])
    c.text((x, y - S(250)), "</>", S(56), "mono", INK)
    # arms
    arm_up = {"shocked": -60, "happy": -30, "angry": -10}.get(mood, 20)
    for sx in (-1, 1):
        ax = x + sx * S(118)
        c.line([(ax, y - S(320)), (ax + sx * S(40), y - S(220) + S(arm_up))], col["shirt"], S(40))
        c.ell([ax + sx * S(40) - S(24), y - S(244) + S(arm_up), ax + sx * S(40) + S(24), y - S(196) + S(arm_up)], fill=col["skin"])
    # head
    hx0, hy0, hx1, hy1 = x - S(165), y - S(700), x + S(165), y - S(345)
    c.rr([hx0, hy0, hx1, hy1], S(120), fill=col["skin"])
    # flat hair cap with a side fringe
    c.rr([hx0 - S(4), hy0 - S(16), hx1 + S(4), hy0 + S(95)], S(70), fill=col["hair"])
    c.poly([(hx0 + S(40), hy0 + S(80)), (x + S(60), hy0 + S(80)), (hx0 + S(40), hy0 + S(150))], col["hair"])
    # headphones
    c.arc([hx0 - S(26), hy0 - S(46), hx1 + S(26), hy1 - S(60)], 190, 350, col["phones"], S(26))
    for sx in (-1, 1):
        ex = x + sx * S(170)
        c.rr([ex - S(34), y - S(560), ex + S(34), y - S(450)], S(26), fill=col["phones"])
    # face
    ey, my = y - S(530), y - S(430)
    bl = _blink(t)
    for sx in (-1, 1):
        ex = x + sx * S(62)
        if mood in ("happy", "smug"):
            c.arc([ex - S(26), ey - S(18), ex + S(26), ey + S(30)], 200, 340, INK, S(10))
        elif mood == "deadpan":
            c.line([(ex - S(28), ey), (ex + S(28), ey)], INK, S(10))
            c.ell([ex - S(10), ey, ex + S(10), ey + S(18)], fill=INK)
        elif mood == "shocked":
            c.ell([ex - S(32), ey - S(36), ex + S(32), ey + S(36)], fill=WHITE, outline=INK, width=S(5))
            c.ell([ex - S(11), ey - S(11), ex + S(11), ey + S(11)], fill=INK)
        else:
            h = S(22) * bl
            c.ell([ex - S(18), ey - h, ex + S(18), ey + h], fill=INK)
        # brows
        if mood == "angry":
            c.line([(ex - sx * S(34), ey - S(60)), (ex + sx * S(30), ey - S(40))], INK, S(10))
        elif mood == "sad":
            c.line([(ex - sx * S(34), ey - S(40)), (ex + sx * S(30), ey - S(58))], INK, S(10))
        elif mood == "think":
            c.line([(ex - S(30), ey - S(52 + sx * 8)), (ex + S(30), ey - S(52 - sx * 8))], INK, S(9))
    # cheeks
    if mood in ("happy", "smug"):
        for sx in (-1, 1):
            c.ell([x + sx * S(110) - S(24), my - S(40), x + sx * S(110) + S(24), my - S(14)], fill=(240, 150, 140))
    # mouth: talk overrides
    if talk > 0.05:
        h = S(10 + 46 * talk)
        c.rr([x - S(34), my - h / 2, x + S(34), my + h / 2], min(S(30), h / 2), fill=(90, 30, 40))
    elif mood == "happy":
        c.arc([x - S(46), my - S(40), x + S(46), my + S(26)], 20, 160, INK, S(10))
    elif mood == "smug":
        c.arc([x - S(20), my - S(30), x + S(56), my + S(14)], 20, 140, INK, S(9))
    elif mood == "sad":
        c.arc([x - S(40), my, x + S(40), my + S(50)], 200, 340, INK, S(10))
    elif mood == "shocked":
        c.ell([x - S(24), my - S(20), x + S(24), my + S(34)], fill=(90, 30, 40))
    elif mood == "think":
        c.line([(x - S(14), my + S(6)), (x + S(30), my - S(4))], INK, S(9))
    else:
        c.line([(x - S(30), my), (x + S(30), my)], INK, S(10))


def bot(c, x, y, s, mood="neutral", t=0.0, talk=0.0, colors=None):
    col = _cols(BOT_DEFAULT, colors)
    hover = math.sin(t * 2.6) * 10 * s
    y = y + hover
    S = lambda v: v * s  # noqa: E731
    # shadow + hover base
    c.ell([x - S(90), y - S(14) - hover, x + S(90), y + S(14) - hover], fill=(0, 0, 0))
    c.rr([x - S(55), y - S(90), x + S(55), y - S(40)], S(24), fill=col["trim"])
    # body
    c.rr([x - S(110), y - S(300), x + S(110), y - S(80)], S(50), fill=col["body"])
    c.ell([x - S(26), y - S(220), x + S(26), y - S(168)], fill=col["eyes"])
    # arms
    wave = math.sin(t * 6) * 20 if mood in ("happy", "love") else 0
    for sx in (-1, 1):
        ax = x + sx * S(110)
        c.line([(ax, y - S(250)), (ax + sx * S(60), y - S(180) - S(wave if sx > 0 else 0))], col["trim"], S(22))
        c.ell([ax + sx * S(60) - S(22), y - S(202) - S(wave if sx > 0 else 0),
               ax + sx * S(60) + S(22), y - S(158) - S(wave if sx > 0 else 0)], fill=col["body"])
    # neck + monitor head
    c.rr([x - S(30), y - S(340), x + S(30), y - S(290)], S(10), fill=col["trim"])
    hx0, hy0, hx1, hy1 = x - S(190), y - S(640), x + S(190), y - S(330)
    c.rr([hx0, hy0, hx1, hy1], S(56), fill=col["body"])
    c.rr([hx0 + S(26), hy0 + S(26), hx1 - S(26), hy1 - S(26)], S(36), fill=col["screen"])
    # antenna
    c.line([(x, hy0), (x, hy0 - S(70))], col["trim"], S(12))
    pulse = 0.5 + 0.5 * math.sin(t * 5)
    c.ell([x - S(22), hy0 - S(104), x + S(22), hy0 - S(60)], fill=tuple(int(v * (0.7 + 0.3 * pulse)) for v in col["eyes"]))
    # pixel face
    e = col["eyes"] if mood != "error" else (240, 96, 86)
    ey, my = y - S(510), y - S(415)
    bl = _blink(t, 1.3)
    for sx in (-1, 1):
        ex = x + sx * S(72)
        if mood == "happy":
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
        else:
            h = S(34) * bl
            c.rr([ex - S(22), ey - h / 2, ex + S(22), ey + h / 2], S(10), fill=e)
    if talk > 0.05:
        bars = 7
        for i in range(bars):
            hh = S(8 + 40 * talk * (0.5 + 0.5 * math.sin(t * 30 + i * 1.7)))
            bx = x - S(70) + i * S(20)
            c.rr([bx, my - hh / 2, bx + S(12), my + hh / 2], S(4), fill=e)
    elif mood in ("happy", "love"):
        c.arc([x - S(50), my - S(36), x + S(50), my + S(20)], 20, 160, e, S(10))
    elif mood == "sad":
        c.arc([x - S(40), my, x + S(40), my + S(40)], 200, 340, e, S(10))
    elif mood == "shocked":
        c.ell([x - S(20), my - S(16), x + S(20), my + S(24)], outline=e, width=S(8))
    else:
        c.rr([x - S(44), my - S(5), x + S(44), my + S(5)], S(4), fill=e)


CHARACTERS = {"dev": dev, "bot": bot}
MOODS = ["neutral", "happy", "sad", "shocked", "angry", "deadpan", "smug", "think", "error", "love"]


def draw(c, who, x, y, scale=1.0, mood="neutral", t=0.0, talk=0.0, colors=None):
    if who not in CHARACTERS:
        raise ValueError(f"unknown character '{who}'. Known: {sorted(CHARACTERS)}")
    CHARACTERS[who](c, x, y, scale, mood, t, talk, colors)
