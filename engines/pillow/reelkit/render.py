"""Frame renderer + ffmpeg encode."""
import math
import multiprocessing as mp
import os
import subprocess
import sys

from PIL import Image, ImageDraw

from . import elements
from .brand import Brand
from .draw import K, Cv, glow, make_bg
from .timeline import Timeline

FF = os.environ.get("FFMPEG", "ffmpeg")
_S = {}  # per-process state: timeline, brand, background


def init(scenes_path, brand_path=None):
    tl = Timeline(scenes_path)
    brand = Brand.load(brand_path or tl.brand_path)
    from .custom import resolve_files
    bp = brand_path or tl.brand_path
    bdir = os.path.dirname(os.path.abspath(bp)) if bp else tl.base
    brand.raw["characters"] = {**resolve_files(brand.raw.get("characters"), bdir),
                               **resolve_files(tl.raw.get("characters"), tl.base)}
    style = tl.raw.get("style") or (tl.raw.get("meta") or {}).get("style")
    painter = None
    if style:                           # art-style preset for the whole reel: colours, background, overlay
        from .art import style_class
        painter = style_class(style)
        brand.c.update(painter.brand)
        brand.raw["_style"] = style
    _S.update(tl=tl, brand=brand, bg=make_bg(brand, tl.W, tl.H), painter=painter)


def _frame_overlay(out, brand, t, total, W):
    d = ImageDraw.Draw(out)
    fr = brand.frame
    from .draw import font
    if fr.get("accent_bar", True):
        d.rectangle([0, 0, W, 10], fill=brand.c["accent"])
    top = fr.get("safe_top", 280)
    if brand.label:
        f = font(brand.fonts["bold"], 28)
        f = f.font_variant(size=28)
        w = d.textlength(brand.label, font=f)
        d.rounded_rectangle([60, top - 64, 60 + w + 40, top - 22], 21, fill=brand.c["panel"])
        d.text((80, top - 43), brand.label, font=f, fill=brand.c["accent"], anchor="lm")
    if fr.get("watermark", True) and brand.handle:
        f = font(brand.fonts["bold"], 32).font_variant(size=32)
        d.text((W - 60, top - 43), brand.handle, font=f, fill=brand.c["muted"], anchor="rm")
    if fr.get("progress_bar", True):
        d.rounded_rectangle([60, top - 6, W - 60, top + 6], 6, fill=(50, 50, 62))
        d.rounded_rectangle([60, top - 6, 60 + int((W - 120) * min(1, t / total)), top + 6], 6, fill=brand.c["accent"])


def render_frame(i):
    tl, brand = _S["tl"], _S["brand"]
    W, H = tl.W, tl.H
    t = i / tl.fps
    s = tl.scene_at(t)
    lt = t - s.start
    im = _S["bg"].copy()
    c = Cv(im, brand)
    painter = _S.get("painter")
    pt = painter(c, im) if painter else None
    if pt:
        pt.t = t
        pt.reel_background()
    if s.glow:
        glow(im, elements.col(c, s.glow), *(s.raw.get("glow_at", [540, 900])))
    for el in s.elements:
        elements.draw(c, im, el, lt)
    if pt:
        pt.reel_overlay()
    ln = s.line_at(lt)
    if ln and ln.subtitle and ln.text:
        elements.subtitle(c, im, ln.text, lt - ln.start, brand.frame.get("safe_bottom", 1440) - 40, ln.dur)
    # camera: punch-in on scene start / marked beats, shake on hits
    z = 1.0
    for tp in s.punch:
        if lt >= tp:
            z = max(z, 1.0 + 0.05 * math.exp(-(lt - tp) * 7))
    sx = sy = 0.0
    for ts in s.shakes:
        if 0 <= lt - ts < 0.35:
            e = math.exp(-(lt - ts) * 14)
            sx += 18 * e * math.sin((lt - ts) * 95)
            sy += 12 * e * math.cos((lt - ts) * 80)
    if sx or sy:
        z = max(z, 1.035)
    cw, ch = W * K / z, H * K / z
    cx = min(max(W * K / 2 + sx * K, cw / 2), W * K - cw / 2)
    cy = min(max(H * K / 2 + sy * K, ch / 2), H * K - ch / 2)
    out = im.resize((W, H), Image.LANCZOS, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
    meta = tl.raw.get("meta", {}) or {}
    if meta.get("clean"):              # clean clip: no label/handle/progress bar, no fades (Style Drop clips)
        return out.tobytes()
    _frame_overlay(out, brand, t, tl.total, W)
    if t < 0.08 or t > tl.total - 0.25:
        k = min(1, t / 0.08) if t < 0.08 else max(0, (tl.total - t) / 0.25)
        out = Image.blend(Image.new("RGB", (W, H), brand.c["bg_bottom"]), out, k)
    return out.tobytes()


def stills(scenes_path, out_prefix, times=None, brand_path=None):
    init(scenes_path, brand_path)
    tl = _S["tl"]
    if not times:
        times = []
        for s in tl.scenes:   # middle + near the end of every scene
            times += [round(s.start + s.dur * 0.5, 2), round(s.end - 0.15, 2)]
    paths = []
    for ts in times:
        p = f"{out_prefix}_{ts:05.2f}.png"
        Image.frombytes("RGB", (tl.W, tl.H), render_frame(int(ts * tl.fps))).save(p)
        paths.append(p)
    return paths


def contact_sheet(paths, out, cols=4, thumb=270):
    ims = [Image.open(p) for p in paths]
    th = int(thumb * 1920 / 1080)
    rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (cols * thumb, rows * th), (0, 0, 0))
    for k, im in enumerate(ims):
        sheet.paste(im.resize((thumb, th), Image.LANCZOS), ((k % cols) * thumb, (k // cols) * th))
    sheet.save(out)
    return out


def video(scenes_path, out, brand_path=None, workers=None, crf=18, preset="medium"):
    init(scenes_path, brand_path)
    tl = _S["tl"]
    n = int(tl.total * tl.fps)
    ff = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{tl.W}x{tl.H}", "-r", str(tl.fps), "-i", "-", "-c:v", "libx264",
                           "-preset", preset, "-crf", str(crf), "-tune", "animation", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    workers = workers or max(1, min(8, (os.cpu_count() or 2)))
    if workers == 1 or sys.platform == "win32":
        it = map(render_frame, range(n))
        pool = None
    else:
        pool = mp.get_context("spawn" if sys.platform == "darwin" else "fork").Pool(
            workers, initializer=init, initargs=(scenes_path, brand_path))
        it = pool.imap(render_frame, range(n), chunksize=6)
    for k, buf in enumerate(it):
        ff.stdin.write(buf)
        if k % 300 == 0:
            print(f"  frame {k}/{n}", flush=True)
    if pool:
        pool.close()
        pool.join()
    ff.stdin.close()
    ff.wait()
    if ff.returncode:
        raise RuntimeError("ffmpeg failed")
    return tl
