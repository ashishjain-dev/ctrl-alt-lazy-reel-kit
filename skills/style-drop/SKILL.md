---
name: style-drop
description: Make a "Style Drop" reel - one short hero scene (for example a dragon kite cutting a rival kite at Makar Sankranti) drawn in several art styles (folk painting, ink wash, wall art, blueprint, paper cut-out...) and cut into one 9:16 reel with a numbered list, card wipes and a comment CTA. Also use it to add a new art style or a new hero scene to ctrl-alt-lazy-reel-kit.
---

# Style Drop

One 5-second hero scene, N art styles, one reel. Viewers compare the looks, so the scene stays identical and only the painting changes. Built on https://github.com/ashishjain-dev/ctrl-alt-lazy-reel-kit (Pillow engine; the Remotion engine doesn't render art styles yet).

```bash
git clone --depth 1 https://github.com/ashishjain-dev/ctrl-alt-lazy-reel-kit && cd ctrl-alt-lazy-reel-kit
pip install -e engines/pillow && reelkit check
```

## Built-in pieces

**Hero scene `kite`** (5 s, the cut always at 2.0 s): a dragon kite swoops in over Makar Sankranti rooftops, its string crosses a rival patang's string and cuts it at 2.0 s; the rival spins away, birds scatter, "Kaipoche!" pops up, the dragon kite does a victory loop.

**Styles** (each is original code, inspired by a traditional or familiar art form):

| style | look |
|---|---|
| `fish-scale-folk` | handmade paper, double ink outlines with a paper gap, vermilion / turmeric / leaf / indigo, fish-scale and dot fills, a sun with a face, triangle border |
| `rice-paper` | grey ink washes that darken where they overlap, dry-brush streaks, misty hills, vermilion sun and seal only; ink splatter + brush arc at the cut |
| `mud-wall` | white on red-brown mud, everything from circles, triangles and lines, hourglass people cheering on the roofs, 8 fps wobble, rings of dots at the cut |
| `cyan-plan` | blueprint: grid, white line-work, dimensions, callouts, dashed flight path, "STRING LOCK" reticle that turns into "CUT T+2.00s", title block |
| `cut-card` | layered paper with soft shadows and white cut edges, wavy paper sky, stacked clouds, 12 fps stop motion, paper starburst |

## 1. Ask (one round), then confirm a plan

- **Scene**: the built-in kite, or the user's own subject (their product, a dragon, a chai cup…). For their own subject, write one custom scene file (step 5) that paints every chosen style. Keep it one clear action with one peak moment at a fixed time, shapes that read in every style, and something viewers recognise instantly.
- **Styles**: which ones and how many (3–10). Each card is ~2 s, so 5 styles ≈ 13 s with the outro, 10 ≈ 23 s.
- **Title** (two short lines), **CTA keyword** ("COMMENT 'KITE' FOR THE PROMPTS"), **music mood** (`upbeat` default).
- Show the plan (scene, styles in order, title, CTA, length) and wait for a go-ahead before rendering.

## 2. Check the look first (fast)

For every style, look at the moments that matter before rendering anything long:
```bash
# examples/style-drop-kite/clip.yaml renders one style; change its `style:` line
reelkit stills examples/style-drop-kite/clip.yaml -o stills/folk --at 0.6 2.0 2.15 4.0
```
Check: the cut is readable at 2.0 s, nothing important outside y 280–1440 / x < 850, text not covering the kites, each style clearly different from the others.

## 3. Build the reel

```yaml
# scenes.yaml
meta: {title: kite-style-drop, fps: 30}
audio: {music: {mood: upbeat, volume: 0.5}}
style_drop:
  scene: kite
  styles: [fish-scale-folk, rice-paper, mud-wall, cyan-plan, cut-card]
  title: ["5 kite styles", "one Makar Sankranti cut"]
  card_dur: 2.0
  clip_offset: 1.05        # so the cut lands 0.95 s into every card
  outro: 3.0
  cta: "COMMENT 'KITE'\nFOR THE PROMPTS"
  bg: "#f4ecdc"            # optional: ink, accent, muted colours too
```
```bash
reelkit stills scenes.yaml -o stills/drop        # title, list, a card mid-wipe, the outro
reelkit render scenes.yaml -o style-drop.mp4
reelkit render examples/style-drop-kite/clip.yaml -o clip-folk.mp4   # optional: each style as its own 5 s clip
```
Sound: generated music, a whoosh into each card and a hit on each cut. Add a voiceover (style names as they appear) with `dialogue` lines and `reelkit voices` if wanted.

**Use a style on any reel:** `style: mud-wall` at the top of any scenes.yaml re-skins the whole video (background, colours, border, subtitles), and `{type: scene, name: kite, style: rice-paper}` drops the hero scene into any reel.

## 4. Add a new style

Create `engines/pillow/reelkit/art/<name>.py` with a `Painter` subclass and register it in `art/__init__.py > STYLES` (and a display name in `art/drop.py > NAMES`). Override only what changes: `background, sun, bg_kites, skyline, birds, strings, rival, tail, hero, hero_face, burst, shout, overlay`; set `fps` (e.g. 8 or 12) and `jitter` for a hand-made, stepped look; set `brand` colours so the style also works as a whole-reel preset. Helpers in `painter.py`: `fill_pattern` + `tile` (scales, dots, hatch, cross, waves, grid), `soft_poly` (washes, glows, brush strokes), `shadow_poly`, `dashed`, `paper_texture`, `local` (draw in kite coordinates).

Full style guides for all ten styles (surface, palette, line, fill, figures, motion, impact, text, frame, avoid): `docs/style-guides.md`. Five more styles, ready to build:
- **Lamp Leather**: translucent dyed-leather puppets on a cotton screen lit by a flickering oil lamp; punched dot holes glowing, carved outlines, control rods running off the bottom, a soft shadow, a lamp flare at the cut.
- **Temple Glass**: every shape a mosaic of jewel-coloured glass in dark lead lines inside an arched window with iron bars; light glows through; a white-gold glass star at the cut.
- **Cel Burst**: TV-anime cel shading, saturated sky and towering clouds, two-tone hard shadows, bold lines, speed lines on the swoop, a 3-frame black/white impact flash then a red frame at the cut.
- **Wave Block**: woodblock print, deep blue gradient sky, red sun, horizontal mist bands, flat muted colours, black key lines, roofs as stylised tile waves, wood grain over everything, a vertical cartouche with a red seal.
- **Gold Court**: court miniature painting, lapis sky band with gold scroll clouds, rolling green hills with round dotted trees, jewel-flat colours, hairline outlines, burnished gold details with pearl dots, a red border with a gold vine, gold rays at the cut.

Check each new style with `reelkit stills` at 0.6, 2.0 and 4.0 s before adding it to a drop.

## 5. The user's own scene (no engine changes)

Write one file and point the drop at it:
```yaml
style_drop:
  file: chai_scene.py       # draw(ctx, t, args); ctx.style says which style to paint
  impact: 2.0               # the big moment, same time in every style
  clip_dur: 5.0
  styles: [fish-scale-folk, mud-wall, cyan-plan]
```
Branch on `ctx.style` and paint each style from its section in `docs/style-guides.md`; start with `ctx.painter.background({})` and end with `ctx.painter.overlay({})` for each style's surface and frame. Keep it a pure function of `t` with one clear action that peaks at `impact`. Rules and helpers: `docs/custom-art.md`. Check every style with `reelkit stills` (clip.yaml with `{type: custom, file: chai_scene.py, style: mud-wall}`) before building the drop.

## 6. Add a new built-in hero scene

Only for scenes many people will reuse. Create `engines/pillow/reelkit/art/<scene>.py` with `DUR`, `CUT_T` and `layout(t)` and register it in `art/__init__.py > SCENES`. Rules: `layout(t)` is a pure function of time (no state between frames), the peak moment is at a fixed `CUT_T`, geometry only (where things are), never colours. Reusing the kite's keys (`hero`, `rival`, `skyline`, `burst`...) lets every existing style paint it at once; new keys need new painter methods in each style.

## 7. Deliver

The reel MP4, a cover (`reelkit cover`), a caption that asks people to pick their favourite style (comments), the CTA keyword, and the list of styles used. Never write real people's names or brands into a scene.
