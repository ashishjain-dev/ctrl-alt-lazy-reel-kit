"""reelkit CLI.

  python -m reelkit render  scenes.yaml -o reel.mp4 [--brand brand.yaml] [--preview] [--no-audio]
  python -m reelkit stills  scenes.yaml -o stills/f [--at 1.2 3.4]   # PNGs + contact sheet
  python -m reelkit audio   scenes.yaml -o audio.wav
  python -m reelkit timing  scenes.yaml                              # scene + dialogue timing table
  python -m reelkit cover   scenes.yaml -o cover.png                 # uses the `cover:` block
  python -m reelkit grid    new.png older1.png older2.png -o grid.png
  python -m reelkit voices split dialogue.mp3 a1=0-1.6 b1=1.9-3.2 [--dir ep/] [--tighten 0.12] [--tempo 1.05] [--robot b]
  python -m reelkit voices gaps  dialogue.mp3
  python -m reelkit voices tts   scenes.yaml                         # ElevenLabs, needs ELEVENLABS_API_KEY
  python -m reelkit check                                            # python deps, ffmpeg, fonts
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

FF = os.environ.get("FFMPEG", "ffmpeg")


def cmd_check(_):
    ok = True
    for mod in ("PIL", "numpy", "yaml"):
        try:
            __import__(mod)
            print(f"ok   python: {mod}")
        except ImportError:
            ok = False
            print(f"MISSING python: {mod}  ->  pip install -r requirements.txt")
    if shutil.which(FF):
        print("ok   " + subprocess.run([FF, "-version"], capture_output=True, text=True).stdout.splitlines()[0])
    else:
        ok = False
        print("MISSING ffmpeg -> brew install ffmpeg | sudo apt install ffmpeg | winget install ffmpeg")
    try:
        from .brand import Brand
        b = Brand()
        for k, v in b.fonts.items():
            print(f"ok   font {k}: {v}")
    except FileNotFoundError as e:
        ok = False
        print("MISSING fonts:", e)
    sys.exit(0 if ok else 1)


def cmd_render(a):
    from . import audio, render
    from .brand import Brand
    out = os.path.abspath(a.out)
    with tempfile.TemporaryDirectory() as tmp:
        vid = os.path.join(tmp, "video.mp4")
        print("rendering video ...")
        tl = render.video(a.scenes, vid, a.brand, a.workers, crf=28 if a.preview else 18,
                          preset="veryfast" if a.preview else "medium")
        if a.no_audio:
            shutil.move(vid, out)
        else:
            wav = os.path.join(tmp, "audio.wav")
            audio.build(tl, wav, Brand.load(a.brand or tl.brand_path))
            subprocess.run([FF, "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a",
                            "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
                            "-shortest", "-movflags", "+faststart", out], check=True)
    print(f"done {out}  ({tl.total:.1f}s)")


def cmd_stills(a):
    from . import render
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    paths = render.stills(a.scenes, a.out, a.at, a.brand)
    sheet = render.contact_sheet(paths, a.out + "_sheet.png")
    print("\n".join(paths))
    print("contact sheet:", sheet)


def cmd_audio(a):
    from . import audio
    from .brand import Brand
    from .timeline import Timeline
    tl = Timeline(a.scenes)
    audio.build(tl, a.out, Brand.load(a.brand or tl.brand_path))
    print("done", a.out)


def cmd_timing(a):
    from .timeline import Timeline
    tl = Timeline(a.scenes)
    for s in tl.scenes:
        print(f"{s.start:6.2f}-{s.end:6.2f}  {s.name}")
        for ln in s.lines:
            src = "voice" if ln.env else "estimate"
            print(f"        {s.start + ln.start:6.2f}-{s.start + ln.end:6.2f}  {ln.who:>4}: {ln.text}  [{src}]")
    print(f"total {tl.total:.2f}s")
    if tl.total > 90:
        print("WARN: over 90 s; Instagram reels perform best well under a minute")


def cmd_cover(a):
    from . import covers
    print(covers.from_yaml(a.scenes, a.out, a.brand))


def cmd_grid(a):
    from . import covers
    print(covers.grid(a.images, a.out))


def cmd_voices(a):
    from . import voices
    if a.action == "split":
        os.makedirs(a.dir, exist_ok=True)
        voices.split(a.src, a.specs, a.dir, a.tighten, a.tempo, a.robot)
    elif a.action == "gaps":
        print("\n".join(voices.silences(a.src)))
    elif a.action == "tts":
        from .timeline import Timeline
        voices.tts_elevenlabs(Timeline(a.src))


def main(argv=None):
    p = argparse.ArgumentParser(prog="reelkit", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("render"); s.add_argument("scenes"); s.add_argument("-o", "--out", default="reel.mp4")
    s.add_argument("--brand"); s.add_argument("--preview", action="store_true"); s.add_argument("--no-audio", action="store_true")
    s.add_argument("--workers", type=int)
    s.set_defaults(fn=cmd_render)
    s = sub.add_parser("stills"); s.add_argument("scenes"); s.add_argument("-o", "--out", default="stills/f")
    s.add_argument("--at", type=float, nargs="*"); s.add_argument("--brand"); s.set_defaults(fn=cmd_stills)
    s = sub.add_parser("audio"); s.add_argument("scenes"); s.add_argument("-o", "--out", default="audio.wav")
    s.add_argument("--brand"); s.set_defaults(fn=cmd_audio)
    s = sub.add_parser("timing"); s.add_argument("scenes"); s.set_defaults(fn=cmd_timing)
    s = sub.add_parser("cover"); s.add_argument("scenes"); s.add_argument("-o", "--out", default="cover.png")
    s.add_argument("--brand"); s.set_defaults(fn=cmd_cover)
    s = sub.add_parser("grid"); s.add_argument("images", nargs="+"); s.add_argument("-o", "--out", default="grid.png")
    s.set_defaults(fn=cmd_grid)
    s = sub.add_parser("voices"); s.add_argument("action", choices=["split", "gaps", "tts"]); s.add_argument("src")
    s.add_argument("specs", nargs="*"); s.add_argument("--dir", default="."); s.add_argument("--tighten", type=float)
    s.add_argument("--tempo", type=float, default=1.0); s.add_argument("--robot", help="key prefix that gets the robot filter")
    s.set_defaults(fn=cmd_voices)
    s = sub.add_parser("check"); s.set_defaults(fn=cmd_check)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
