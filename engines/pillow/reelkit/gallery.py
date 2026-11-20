"""Character gallery: one sheet that shows every built-in character, look option and mood,
plus the named characters in brand.yaml. Skills show it so people can pick a cast visually."""
from PIL import Image

from . import characters
from .brand import Brand
from .draw import K, Cv, make_bg

CELL_W, CELL_H = 300, 400

LOOKS = [
    ("person", {}, "person"),
    ("person", {"hair": "long", "hair_color": "#6b3e26", "skin": "#c68c64", "shirt": "#e8805c"}, "hair: long"),
    ("person", {"hair": "curly", "hair_color": "#1e1a1a", "skin": "#8d5a3b", "shirt": "#7a6cf0"}, "hair: curly"),
    ("person", {"hair": "bun", "hair_color": "#d9a441", "shirt": "#f0b84a", "glasses": True}, "bun + glasses"),
    ("person", {"hair": "spiky", "hair_color": "#e04f5f", "shirt": "#2f3a56", "skin": "#ffd9b8"}, "hair: spiky"),
    ("person", {"hair": "bald", "beard": True, "hair_color": "#4a3426", "skin": "#b47a55", "shirt": "#3fa796", "shirt_icon": "FIT"}, "bald + beard"),
    ("person", {"hat": "cap", "accent": "#2f7de1", "shirt": "#f2f2f2", "shirt_icon": "$"}, "hat: cap"),
    ("person", {"hat": "beanie", "accent": "#e8805c", "hair": "long", "shirt": "#41506b"}, "hat: beanie"),
    ("dev", {}, "dev (preset)"),
    ("bot", {}, "bot"),
    ("blob", {}, "blob"),
    ("blob", {"body": "#ffb36b", "belly": "#ffe2c4", "sprout": False}, "blob (recolour)"),
]


def gallery(out, brand_path=None, moods=True):
    brand = Brand.load(brand_path)
    named = [(n, {}, n) for n in brand.raw.get("characters", {}) if n not in ("person", "bot", "blob", "dev")]
    rows_spec = [LOOKS + named]
    if moods:
        for who in ("person", "bot", "blob"):
            rows_spec.append([(who, {}, m) for m in characters.MOODS if not (who == "person" and m in ("error", "love"))])
    cols = 6
    cells = [cell for row in rows_spec for cell in (row + [None] * ((-len(row)) % cols))]
    rows = len(cells) // cols
    W, H = cols * CELL_W, rows * CELL_H
    im = make_bg(brand, W, H)
    c = Cv(im, brand)
    for i, cell in enumerate(cells):
        if not cell:
            continue
        who, look, label = cell
        cx, top = (i % cols) * CELL_W + CELL_W / 2, (i // cols) * CELL_H
        mood = label if label in characters.MOODS else "happy" if who != "bot" else "neutral"
        characters.draw(c, who, cx, top + CELL_H - 70, 0.42, mood, 0.4, 0, brand.raw.get("characters", {}), look)
        c.text((cx, top + CELL_H - 32), label, 24, "bold", brand.c["fg"])
    im.resize((W, H), Image.LANCZOS).save(out)
    return out


_ = K
