"""Geometry of the kite scene: a dragon kite cuts a rival kite above Makar Sankranti rooftops.

5 seconds. The cut always lands at CUT_T = 2.0 s, so every style lines up in a Style Drop.
`layout(t)` is a pure function of time that returns plain geometry (points, angles).
The style modules next to this file decide how each part looks; the geometry never changes between styles.
"""
import math
import random

W, H = 1080, 1920
DUR = 5.0
CUT_T = 2.0
HERO_W, HERO_H = 300, 375          # hero kite size (px); faces are drawn at HERO_W / 200 scale
RIVAL_W, RIVAL_H = 220, 280
SUN = (850, 1180, 90)              # late-afternoon sun low over the roofs (x, y, r)
HAND = (170, 1770)                 # where the hero string starts (a hand on the roof, mostly below the UI line)
RIVAL_ANCHOR = (1190, 1660)        # rival string runs off-screen to the right


def _cr(p0, p1, p2, p3, u):
    """Catmull-Rom between p1 and p2."""
    u2, u3 = u * u, u * u * u
    return tuple(0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u2 + (-a + 3 * b - 3 * c + d) * u3)
                 for a, b, c, d in zip(p0, p1, p2, p3))


def _path(keys, t):
    t = max(keys[0][0], min(keys[-1][0], t))
    for i in range(len(keys) - 1):
        if keys[i][0] <= t <= keys[i + 1][0]:
            u = (t - keys[i][0]) / (keys[i + 1][0] - keys[i][0])
            p0 = keys[max(0, i - 1)][1:]
            p3 = keys[min(len(keys) - 1, i + 2)][1:]
            return _cr(p0, keys[i][1:], keys[i + 1][1:], p3, u)
    return keys[-1][1:]


HERO_KEYS = [(0.0, 280, 980), (0.8, 380, 700), (1.4, 560, 600), (2.0, 790, 690), (2.5, 830, 860),
             (3.1, 720, 640), (3.7, 560, 640), (4.3, 660, 560), (5.0, 590, 600), (5.6, 540, 640)]


def hero_pos(t):
    return _path(HERO_KEYS, t)


def rival_state(t):
    """(x, y, angle, scale) of the rival patang."""
    if t <= CUT_T:
        u = t / CUT_T
        e = u * u * (3 - 2 * u)
        x = 900 + (580 - 900) * e + 10 * math.sin(t * 3.1)
        y = 560 + (720 - 560) * e + 12 * math.sin(t * 2.3)
        return x, y, 0.12 * math.sin(t * 2.6), 1.0
    d = t - CUT_T
    x = 580 + 110 * d + 26 * math.sin(d * 3.2)
    y = 720 + 80 * d ** 1.3
    return x, y, 3.6 * d + 0.4 * math.sin(d * 5), max(0.55, 1 - 0.09 * d)


def diamond(cx, cy, w, h, ang):
    """Kite diamond: top, right, bottom, left (bottom is longer, like a real patang)."""
    pts = [(0, -h * 0.42), (w / 2, 0), (0, h * 0.58), (-w / 2, 0)]
    cs, sn = math.cos(ang), math.sin(ang)
    return [(cx + px * cs - py * sn, cy + px * sn + py * cs) for px, py in pts]


def _string(a, b, sag=0.06, n=16):
    """Slightly sagging string from a to b."""
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0)
    out = []
    for i in range(n + 1):
        u = i / n
        out.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + sag * L * 4 * u * (1 - u)))
    return out


def _intersect(p, p2, q, q2):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = p, p2, q, q2
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        return None
    tt = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return x1 + tt * (x2 - x1), y1 + tt * (y2 - y1)


def cut_point():
    hx, hy = hero_pos(CUT_T)
    rx, ry, ra, _ = rival_state(CUT_T)
    hb = diamond(hx, hy, HERO_W, HERO_H, 0)[2]
    rb = diamond(rx, ry, RIVAL_W, RIVAL_H, ra)[2]
    p = _intersect(HAND, hb, rb, RIVAL_ANCHOR)
    return p or ((hb[0] + rb[0]) / 2, (hb[1] + rb[1]) / 2)


CUT_PT = cut_point()

# background kites: (x, y, size, colour role, phase)
BG_KITES = [(150, 440, 64, "bgk1", 0.0), (330, 330, 46, "bgk2", 1.3), (930, 330, 56, "bgk3", 2.1),
            (990, 960, 44, "bgk1", 0.7), (100, 780, 50, "bgk3", 2.8), (740, 400, 38, "bgk2", 1.9)]

_rnd = random.Random(11)
BIRDS = [(260 + _rnd.uniform(-110, 110), 1250 + _rnd.uniform(-50, 40), _rnd.uniform(0, 6.28)) for _ in range(7)]


def skyline():
    """Rooftop blocks (polygons) along the bottom, plus fixtures. Static."""
    blocks = []
    x = -20
    rnd = random.Random(5)
    while x < W + 20:
        w = rnd.randint(150, 260)
        top = rnd.randint(1430, 1560)
        blocks.append([(x, H), (x, top), (x + w, top), (x + w, H)])
        x += w - 4
    def roof_top(x):
        for b in blocks:
            if b[1][0] <= x <= b[2][0]:
                return b[1][1]
        return 1500
    ty = roof_top(775)
    tank = (700, ty - 130, 850, ty)        # water tank box standing on a roof (x0, y0, x1, y1)
    ay = roof_top(280)
    antenna = [(280, ay), (280, 1300)]
    windows = []
    for b in blocks:                       # one or two small windows per block
        (x0, _), (_, top), (x1, _) = b[0], b[1], b[2]
        for k in range(1 + (x1 - x0 > 200)):
            wx = x0 + 40 + k * 100
            if wx + 50 < x1 - 20:
                windows.append([(wx, top + 70), (wx + 50, top + 70), (wx + 50, top + 150), (wx, top + 150)])
    antenna_bars = [[(235, 1330), (325, 1330)], [(245, 1362), (315, 1362)]]
    toran = _string((280, 1318), (700, 1342), sag=0.07, n=13)   # marigold string between antenna and tank
    return {"blocks": blocks, "windows": windows, "tank": tank, "antenna": antenna, "antenna_bars": antenna_bars, "toran": toran}


SKYLINE = skyline()


def layout(t):
    """All geometry at time t (seconds)."""
    hx, hy = hero_pos(t)
    vx = hero_pos(t + 0.05)[0] - hx
    hang = max(-0.5, min(0.5, vx * 0.012)) + 0.05 * math.sin(t * 4)
    hero = diamond(hx, hy, HERO_W, HERO_H, hang)
    # tail: hangs from the bottom tip and trails the motion a little (still a pure function of t)
    tail = []
    bx, by = hero[2]
    for i in range(12):
        tt = t - 0.05 * (i + 1)
        px, py = hero_pos(tt)
        tail.append((bx + 0.35 * (px - hx) + 10 * math.sin(tt * 7 + i * 0.6), by + 0.35 * (py - hy) + 24 * (i + 1)))
    rx, ry, ra, rs = rival_state(t)
    rival = diamond(rx, ry, RIVAL_W * rs, RIVAL_H * rs, ra)
    hero_string = _string(HAND, hero[2], 0.05)
    cut = t >= CUT_T
    if not cut:
        rival_string = [_string(rival[2], RIVAL_ANCHOR, 0.04)]
    else:
        d = t - CUT_T
        # upper piece follows the falling kite; lower piece sags and drops away
        tip = (rival[2][0] + 30 * math.sin(d * 4), rival[2][1] + 160 + 40 * d)
        low_start = (CUT_PT[0] + 40 * d, CUT_PT[1] + 260 * d * d)
        rival_string = [_string(rival[2], tip, 0.1, 8), _string(low_start, RIVAL_ANCHOR, 0.08 + 0.05 * min(d, 1), 12)]
    # birds: idle near the roofs, scatter away from the cut after CUT_T
    birds = []
    for bx, by, ph in BIRDS:
        if t < CUT_T:
            birds.append((bx + 6 * math.sin(t * 2 + ph), by + 4 * math.sin(t * 3 + ph), math.sin(t * 14 + ph)))
        else:
            d = t - CUT_T
            ang = -math.pi / 2 - 0.9 + 0.5 * math.sin(ph * 3)       # up and to the left, fanning out
            sp = 260 + 60 * math.sin(ph)
            birds.append((bx + math.cos(ang) * sp * d, by + math.sin(ang) * sp * d, math.sin(t * 22 + ph)))
    bg = []
    for x, y, s, role, ph in BG_KITES:
        bg.append((diamond(x + 8 * math.sin(t * 1.5 + ph), y + 6 * math.sin(t * 1.2 + ph), s, s * 1.25, 0.15 * math.sin(t + ph)), role, s))
    burst = (t - CUT_T) if 0 <= t - CUT_T < 0.9 else None
    return {"t": t, "hero": hero, "hero_c": (hx, hy), "hero_angle": hang, "hero_s": HERO_W / 200, "sun": SUN, "tail": tail, "hero_string": hero_string,
            "rival": rival, "rival_c": (rx, ry), "rival_angle": ra, "rival_scale": rs, "rival_string": rival_string, "cut": cut,
            "birds": birds, "bg_kites": bg, "burst": burst, "cut_pt": CUT_PT, "skyline": SKYLINE,
            "shout": t >= CUT_T + 0.25, "shout_t": t - CUT_T - 0.25, "shout_xy": (540, 330),
            "project": "Kaipoche", "note": "Makar Sankranti", "seal": "KITE"}
