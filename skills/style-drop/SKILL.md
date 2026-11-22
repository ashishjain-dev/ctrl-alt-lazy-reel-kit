---
name: style-drop
description: Make a "Style Drop" reel - one short animated scene from the user's own idea (their product, an animal, a festival moment...) drawn in several art styles (folk painting, ink wash, wall art, blueprint, paper cut-out...) and cut into one 9:16 reel with a numbered list, card wipes and a comment CTA. Also use it to add a new art style to ctrl-alt-lazy-reel-kit.
---

# Style Drop

One short scene, N art styles, one reel. Viewers compare the looks, so the scene stays identical and only the painting changes. The scene always comes from the user's idea: Claude draws it as one scene file for this video. Built on https://github.com/ashishjain-dev/ctrl-alt-lazy-reel-kit (Pillow engine; the Remotion engine doesn't render art styles yet).

```bash
git clone --depth 1 https://github.com/ashishjain-dev/ctrl-alt-lazy-reel-kit && cd ctrl-alt-lazy-reel-kit
pip install -e engines/pillow && reelkit check
```

## Styles

| style | look |
|---|---|
| `fish-scale-folk` | handmade paper, double ink outlines with a paper gap, vermilion / turmeric / leaf / indigo, fish-scale and dot fills, triangle border |
| `rice-paper` | grey ink washes that darken where they overlap, dry-brush strokes, misty hills, vermilion as the only colour |
| `mud-wall` | white on red-brown mud, everything from circles, triangles and lines, 8 fps wobble |
| `cyan-plan` | blueprint: grid, white line-work, dimensions, callouts, dashed paths, a target reticle, title block |
| `cut-card` | layered paper with soft shadows and white cut edges, wavy paper sky, 12 fps stop motion |
| `cel-burst` | anime cel shading: saturated sky, huge clouds, bold ink, two-tone hard shadows, speed lines, flash impact, 12 fps |
| `gold-court` | court miniature: lapis band with gold scroll clouds, pale wash, dotted round trees, hairlines, red border with gold vine |

Full guides (surface, palette, line, fill, figures, motion, impact, text, frame, avoid) for these seven and three more (Lamp Leather, Temple Glass, Wave Block): `docs/style-guides.md`. The scene file can paint the three extra styles from their guides.

## 1. Ask (one round), then confirm a plan

- **Scene**: what should happen? One clear action with one peak moment (the "impact") at a fixed time, about 5 s long, with shapes that read in every style and a subject viewers recognise at once. Examples: a chai cup tips over a laptop; a cricket ball smashes a stadium light; the user's product drops into frame and opens.
- **Styles**: which ones and how many (3–10). Each card is ~2 s, so 5 styles ≈ 13 s with the outro, 10 ≈ 23 s.
- **Title** (two short lines), **CTA keyword** ("COMMENT 'CHAI' FOR THE PROMPTS"), **music mood** (`upbeat` default).
- Show the plan (scene beats with times, styles in order, title, CTA, length) and wait for a go-ahead.

## 2. Write the scene file

One file next to `scenes.yaml`, e.g. `chai_scene.py`:
```python
def draw(ctx, t, args):          # called once per frame and per style; ctx.style says which style
    ctx.painter.background({})   # the style's surface
    ...                          # the scene, painted per the style's guide (branch on ctx.style)
    ctx.painter.overlay({})      # the style's frame
```
- Keep the geometry (where things are at time `t`) in one function and paint it per style, so every style shows the same moment.
- Pure function of `t`; the impact at a fixed time; stepped styles step `t` (`mud-wall` 8 fps, `cut-card` and `cel-burst` 12 fps).
- Rules, helpers and checks: `docs/custom-art.md`. A complete, hand-tuned example: `examples/style-drop-kite/` (`kite_scene.py` + `kite_art/`: geometry in `layout.py`, one module per style). Learn the pattern from it; don't reuse the kite unless the user asks for kites.

## 3. Check the look first (fast)

```yaml
# clip.yaml: one style, one clip
meta: {title: clip, fps: 30, clean: true}
scenes:
  - name: clip
    dur: 5
    no_punch: true
    elements: [{type: custom, file: chai_scene.py, style: mud-wall}]
```
```bash
reelkit stills clip.yaml -o stills/mud --at 0.6 2.0 2.15 4.0
```
Check every style: the impact is readable, nothing important outside y 280–1440 / x < 850, no text covering the subject, each style clearly different from the others and true to its guide.

## 4. Build the reel

```yaml
meta: {title: chai-style-drop, fps: 30}
audio: {music: {mood: upbeat, volume: 0.5}}
style_drop:
  file: chai_scene.py
  impact: 2.0              # seconds into the clip
  clip_dur: 5.0
  styles: [fish-scale-folk, rice-paper, mud-wall, cyan-plan, cut-card]
  title: ["5 chai styles", "one Monday morning"]
  card_dur: 2.0
  clip_offset: 1.05        # so the impact lands 0.95 s into every card
  outro: 3.0
  cta: "COMMENT 'CHAI'\nFOR THE PROMPTS"
  bg: "#f4ecdc"            # optional: ink, accent, muted colours too
```
```bash
reelkit stills scenes.yaml -o stills/drop        # title, list, a card mid-wipe, the outro
reelkit render scenes.yaml -o style-drop.mp4
reelkit render clip.yaml -o clip-mud.mp4          # optional: each style as its own 5 s clip
```
Sound: generated music, a whoosh into each card and a hit on each impact. Add a voiceover (style names as they appear) with `dialogue` lines and `reelkit voices` if wanted.

**A style on any reel:** `style: mud-wall` at the top of any scenes.yaml re-skins the whole video (background, colours, border, subtitles).

## 5. Add a new built-in style

Create `engines/pillow/reelkit/art/<name>.py` with a `Painter` subclass (its `background`, `overlay`, `brand` colours for whole reels, `pal`, `fps`, `jitter` and helper methods) and register it in `art/__init__.py > STYLES` plus a display name in `art/drop.py > NAMES`. Write its guide in `docs/style-guides.md`. Helpers in `painter.py`: `fill_pattern` + `tile`, `soft_poly`, `shadow_poly`, `dashed`, `paper_texture`, `local`, `closed`.

## 6. Deliver

The reel MP4, a cover (`reelkit cover`), a caption that asks people to pick their favourite style (comments), the CTA keyword, and the list of styles used. Keep the scene file in the project so a follow-up drop reuses it. Never put real people's names, brands or logos into a scene.
