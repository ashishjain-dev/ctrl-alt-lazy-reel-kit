"""Brand settings: colours, fonts, handle, frame. Loaded from brand.yaml, merged over neutral defaults."""
import os
import yaml

DEFAULTS = {
    "handle": "@your.handle",
    "label": "SHORTS",                 # small label in the top band, e.g. "CLAUDE CODE", "PYTHON TIPS"
    "colors": {
        "bg_top": "#1a1622", "bg_bottom": "#0c0e16",
        "fg": "#f6f6fa", "muted": "#a0a0af", "accent": "#e8805c",
        "highlight": "#fcce4a", "good": "#7ad696", "bad": "#f06056",
        "panel": "#22222e", "ink": "#121216", "info": "#82aaf0",
    },
    "fonts": {                          # file paths or file names; searched in common font folders
        "display": ["Inter-Black.otf", "Inter-ExtraBold.otf", "DejaVuSans-Bold.ttf"],
        "bold": ["Inter-Bold.otf", "DejaVuSans-Bold.ttf"],
        "regular": ["Inter-Regular.otf", "DejaVuSans.ttf"],
        "mono": ["JetBrainsMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"],
    },
    "frame": {
        "progress_bar": True,
        "watermark": True,
        "accent_bar": True,             # thin accent bar at the very top
        "safe_top": 280, "safe_bottom": 1440, "safe_right": 850,   # Instagram/TikTok UI overlays
    },
    "music": {"bpm": 92, "mood": "chill", "volume": 0.55},
}

FONT_DIRS = [
    "/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
    os.path.expanduser("~/.local/share/fonts"), "/Library/Fonts", "/System/Library/Fonts",
    os.path.expanduser("~/Library/Fonts"), "C:/Windows/Fonts",
]
_found = {}


def find_font(names):
    """Return the first existing font file among `names` (paths or bare file names)."""
    if isinstance(names, str):
        names = [names]
    for n in names:
        if n in _found:
            return _found[n]
        if os.path.isfile(os.path.expanduser(n)):
            _found[n] = os.path.expanduser(n)
            return _found[n]
        extra = os.environ.get("REELKIT_FONT_DIR")
        for d in ([extra] if extra else []) + FONT_DIRS:
            if not os.path.isdir(d):
                continue
            for root, _, files in os.walk(d):
                if n in files:
                    _found[n] = os.path.join(root, n)
                    return _found[n]
    raise FileNotFoundError(
        f"None of these fonts were found: {names}. Install Inter + DejaVu "
        "(Debian/Ubuntu: apt install fonts-inter fonts-dejavu-core; macOS: brew install --cask font-inter), "
        "set REELKIT_FONT_DIR, or put full paths in brand.yaml > fonts.")


def hex2rgb(h):
    if isinstance(h, (list, tuple)):
        return tuple(int(v) for v in h[:3])
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _merge(a, b):
    out = dict(a)
    for k, v in (b or {}).items():
        out[k] = _merge(a[k], v) if isinstance(v, dict) and isinstance(a.get(k), dict) else v
    return out


class Brand:
    def __init__(self, data=None):
        d = _merge(DEFAULTS, data or {})
        self.raw = d
        self.handle = d["handle"]
        self.label = d["label"]
        self.c = {k: hex2rgb(v) for k, v in d["colors"].items()}
        self.fonts = {k: find_font(v) for k, v in d["fonts"].items()}
        self.frame = d["frame"]
        self.music = d["music"]

    @classmethod
    def load(cls, path=None):
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return cls(yaml.safe_load(f) or {})
        return cls()
