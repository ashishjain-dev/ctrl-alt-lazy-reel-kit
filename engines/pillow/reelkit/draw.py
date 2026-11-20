"""Drawing primitives on a supersampled canvas. Scene coordinates are always output pixels (1080x1920)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

K = 2  # supersampling factor; frames are drawn at K x and downsampled (smooth edges)
_FC = {}


def font(path, size):
    key = (path, int(size * K))
    if key not in _FC:
        _FC[key] = ImageFont.truetype(path, max(1, int(size * K)))
    return _FC[key]


# ---------- easing ----------
def clamp(u):
    return max(0.0, min(1.0, u))


def lerp(a, b, u):
    return a + (b - a) * clamp(u)


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def back_out(u, c1=1.70158):
    u = clamp(u)
    c3 = c1 + 1
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2


def pop(t, t0, dur=0.3):
    """0 before t0, springs to 1 with overshoot. Returns None if not started yet."""
    if t < t0:
        return None
    return back_out((t - t0) / dur)


def mix(c1, c2, u):
    return tuple(int(lerp(a, b, u)) for a, b in zip(c1, c2))


class Cv:
    """Thin wrapper over ImageDraw that takes output-pixel coordinates."""

    def __init__(self, im, brand):
        self.im = im
        self.d = ImageDraw.Draw(im)
        self.b = brand

    @staticmethod
    def S(v):
        return [int(x * K) for x in v]

    def rr(self, box, r, fill=None, outline=None, width=0):
        x0, y0, x1, y1 = box
        if x1 <= x0 or y1 <= y0:
            return
        self.d.rounded_rectangle(self.S(box), int(r * K), fill=fill, outline=outline, width=int(width * K))

    def ell(self, box, fill=None, outline=None, width=0):
        self.d.ellipse(self.S(box), fill=fill, outline=outline, width=int(width * K))

    def arc(self, box, a0, a1, fill, width):
        self.d.arc(self.S(box), a0, a1, fill=fill, width=int(width * K))

    def line(self, pts, fill, width):
        self.d.line([(int(x * K), int(y * K)) for x, y in pts], fill=fill, width=max(1, int(width * K)), joint="curve")

    def poly(self, pts, fill, outline=None):
        self.d.polygon([(int(x * K), int(y * K)) for x, y in pts], fill=fill, outline=outline)

    def f(self, kind, size):
        return font(self.b.fonts.get(kind, kind), size)

    def text(self, xy, s, size, kind="display", fill=None, anchor="mm"):
        self.d.text((int(xy[0] * K), int(xy[1] * K)), s, font=self.f(kind, size),
                    fill=fill or self.b.c["fg"], anchor=anchor)

    def tw(self, s, size, kind="display"):
        return self.d.textlength(s, font=self.f(kind, size)) / K

    def fit(self, s, size, kind, maxw, minsize=24):
        while size > minsize and self.tw(s, size, kind) > maxw:
            size -= 2
        return size

    def wrap(self, s, size, kind, maxw):
        """Greedy word wrap; explicit '\\n' always breaks."""
        out = []
        for para in str(s).split("\n"):
            cur = ""
            for w in para.split(" "):
                nxt = (cur + " " + w).strip()
                if cur and self.tw(nxt.replace("*", ""), size, kind) > maxw:
                    out.append(cur)
                    cur = w
                else:
                    cur = nxt
            out.append(cur)
        # keep *highlights* intact across line breaks: close on one line, reopen on the next
        fixed, open_ = [], False
        for ln in out:
            if open_:
                ln = "*" + ln
            open_ = ln.count("*") % 2 == 1
            fixed.append(ln + "*" if open_ else ln)
        return fixed


def make_bg(brand, W, H):
    top, bot = brand.c["bg_top"], brand.c["bg_bottom"]
    g = Image.new("RGB", (1, 256))
    for y in range(256):
        g.putpixel((0, y), mix(top, bot, y / 255))
    return g.resize((W * K, H * K), Image.BICUBIC)


_GLOW = {}


def glow(im, col, cx, cy, rad=420, strength=0.42):
    key = (col, rad, strength)
    if key not in _GLOW:
        size = int(rad * 2 * K)
        m = Image.radial_gradient("L").resize((size, size), Image.BICUBIC)
        m = m.point(lambda v: int(255 * strength * max(0.0, 1 - v / 180) ** 2))
        _GLOW[key] = (Image.new("RGB", (size, size), col), m)
    img, m = _GLOW[key]
    im.paste(img, (int(cx * K - img.width / 2), int(cy * K - img.height / 2)), m)


def soft_shadow(im, box, r=24, off=(0, 14), alpha=140, blur=18):
    x0, y0, x1, y1 = [v * K for v in box]
    pad = blur * K * 2
    w, h = int(x1 - x0 + pad * 2), int(y1 - y0 + pad * 2)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([pad, pad, w - pad, h - pad], int(r * K), fill=alpha)
    m = m.filter(ImageFilter.GaussianBlur(blur * K / 2))
    im.paste((0, 0, 0), (int(x0 - pad + off[0] * K), int(y0 - pad + off[1] * K)), m)
