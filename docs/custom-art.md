# Custom art at runtime

The engine handles timing, voices, lip sync, subtitles, music, safe zones and export. Anything it can't
draw (a storyteller in a folk style, a crow and a pot, a product, a village) Claude writes for the video
as a small Python file. The file lives next to `scenes.yaml`, so the next episode reuses it and looks the same.

Working example: [`examples/folk-story-crow/`](../examples/folk-story-crow/): `dadi.py` (a storyteller
character) and `crow_scene.py` (the story pictures), both in Fish-Scale Folk.

## 1. Custom element: pictures, backgrounds, props, whole scenes

```yaml
elements:
  - {type: custom, file: crow_scene.py, at: 0, args: {phase: pebbles, dur: 6.5}}
```
```python
def draw(ctx, t, args):          # t = seconds since `at`
    ctx.c.poly([(100, 300), (980, 300), (980, 860), (100, 860)], (246, 234, 206))
```

What `ctx` gives you:

| | |
|---|---|
| `ctx.c` | the canvas. Coordinates are output pixels (1080 × 1920): `poly(pts, fill)`, `line(pts, col, width)`, `ell(box, fill, outline, width)`, `arc(box, a0, a1, col, width)`, `rr(box, radius, fill, outline, width)`, `text(xy, s, size, kind, fill, anchor)`, `tw(s, size, kind)` |
| `ctx.im` | the supersampled image (for `fill_pattern`, `soft_poly`, pasting) |
| `ctx.style`, `ctx.painter`, `ctx.pal` | the style name, an instance of the style's painter (reuse its parts: `ctx.painter.background({})`, `ctx.painter.overlay({})`) and its palette |
| `ctx.colors` | brand colours (already the style's colours when `style:` is set) |
| helpers | `ctx.fill_pattern(im, pts, ctx.tile("scales"/"dots"/"hatch"/"cross"/"waves"/"grid", col, None, size, width))`, `ctx.soft_poly(im, pts, col, alpha, blur, width=0)` (washes, glows, brush strokes), `ctx.shadow_poly(im, pts, off, alpha, blur)`, `ctx.dashed(c, pts, col, width)`, `ctx.paper_texture(w, h, base, amount, fibres)`, `ctx.local(center, angle, x, y)`, `ctx.closed(pts)` |
| `ctx.path("file.png")` | a path next to scenes.yaml (for images) |

A custom element draws in the order it appears in `elements`: put backgrounds first.

### Story backgrounds come from the script

For a narrated story or explainer, every beat of the script gets a **full-screen** background that shows
what the narration says, in the reel's style. Nothing is reused from the examples unless the script asks for it.

1. Split the script into beats (one per scene in scenes.yaml): *crow arrives → drops pebbles → drinks → flies off*.
2. Draw the story's world once, in world coordinates, as one custom file (`story_scene.py`): the place,
   the props, the animated subject.
3. Give each beat its own **shot** of that world: a wide shot, a close-up, a different spot, a different
   time of day. Pass it as `args: {phase: ..., dur: ...}` and pick a camera (zoom + centre) per phase,
   with a slow push-in. A new location in the script means a new part of the world (or a second file).
4. Leave room for the narrator (a corner, e.g. x > 760, y 950–1250) and for subtitles (y 1240–1400).
5. Put the custom background first in each scene's `elements`; the cast stands in front of it automatically.

`examples/folk-story-crow/crow_scene.py` shows the pattern (a `Cam` class, one world, four shots).

## 2. Custom character: talks, lip-syncs, changes mood

```yaml
characters:
  dadi: {file: dadi.py, sari: "#e8805c"}      # extra keys reach draw() as opts
scenes:
  - cast: [{who: dadi, x: 540, y: 1262, scale: 0.56, mood: happy}]
    dialogue: [{who: dadi, voice: d1, text: "Once upon a time..."}]
```
```python
def draw(c, x, y, s, mood, t, talk, opts):    # (x, y) = feet, s = scale, talk = mouth 0..1
    ...
```
Support at least the moods `neutral happy sad shocked think`; draw the mouth open by `talk` when it is
above ~0.05 (that is the lip sync). Put shared characters in `brand.yaml > characters` so every video in a
series uses the same file.

## 3. Custom Style Drop scene

```yaml
style_drop:
  file: my_scene.py        # the scene, painted once per style
  impact: 2.0              # the big moment, same in every style
  clip_dur: 5.0
  styles: [fish-scale-folk, mud-wall, cut-card]
```
The file's `draw(ctx, t, args)` is called once per style with `ctx.style` set; branch on it and paint each
style from its [style guide](style-guides.md). Start with `ctx.painter.background({})` and end with
`ctx.painter.overlay({})` to get each style's surface and frame for free.

## Rules (they keep renders correct)

1. **Pure function of `t`.** No state between frames, no `random` without a fixed seed: frames render in
   parallel and out of order. Derive everything (positions, water level, which pebble is in the air) from `t`.
2. **Follow the style guide** for the style in use: surface, palette, line, fill, figures, motion, impact.
   Stepped styles (`mud-wall` 8 fps, `cut-card` 12 fps) step `t` the same way: `t = int(t * fps) / fps`.
3. **Safe zone:** keep important things in y 280–1440 and x < 850. Leave room above y≈1240 when there are subtitles.
4. **One idea per picture**, readable at phone size: big shapes, strong contrast, few details.
5. **Original only:** no logos, brands, copyrighted characters, or real people.
6. **Performance:** cache anything that doesn't change (textures, static backgrounds) in module-level
   variables. A frame should take well under a second.

## Workflow

1. Write the file(s) from the request and the style guide.
2. Check frames: `reelkit stills scenes.yaml -o stills/f --at 0.5 2.0 4.0` and look at the contact sheet.
   Fix overlaps, empty areas, unreadable parts, anything off-style. Repeat.
3. Render: `reelkit render scenes.yaml -o video.mp4`.
4. Keep the files in the project so the next video reuses them.
