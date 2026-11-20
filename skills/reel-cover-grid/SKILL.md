---
name: reel-cover-grid
description: Make a 9:16 reel cover image and preview how it looks on the Instagram profile grid (3:4 crop) next to existing covers. Use when someone needs a cover/thumbnail for a reel or short, or wants to check that their grid looks consistent.
---

# Reel cover + grid preview

Engine: https://github.com/ashishjain-dev/ctrl-alt-lazy-reel-kit (`pip install -e engines/pillow && reelkit check`).

## Ask which engine (once per project)

> **(a) Pillow** (default, flat 2D character) or **(b) Remotion + Three.js** (3D character; needs Node 18+ and `npm install` in `engines/remotion`; Remotion needs a paid licence for larger companies, see remotion.dev/license)?

## 1. Plan the cover (confirm with the user)

- **Headline ≤ 7 words**, one `*highlighted*` word. It should promise the payoff or name the pain, not describe the video ("Your tests are *lying*", not "Testing tips part 3").
- Optional `sub` line (≤ 6 words), `tag` (series number), and a character with a mood that matches the headline.
- Keep text inside **y 390–1530**: Instagram shows a 3:4 centre crop (1080×1440) on the profile grid, and the full 9:16 only in the feed.

## 2. Make it

Put a `cover:` block in the reel's `scenes.yaml` (or a standalone `cover.yaml` with the same keys plus `brand:`):
```yaml
cover:
  headline: "Your commits say *fix*. Fix *what?*"
  sub: "a 10-second habit"
  tag: "#01"
  character: {who: bot, mood: deadpan}     # optional: x, y (feet), scale
  glow: accent
```
```bash
reelkit cover my-reel/scenes.yaml -o cover.png                       # Pillow
cd engines/remotion && npm run prep -- ../../my-reel/scenes.yaml --no-audio && npm run cover -- ../../cover.png   # Remotion
```

## 3. Grid preview

Pass the new cover first, then the user's latest covers (newest first), so the preview matches the profile order:
```bash
reelkit grid cover.png prev1.png prev2.png prev3.png prev4.png prev5.png -o grid.png
```
Check: is the headline readable at thumbnail size (~360 px wide)? Does it stand out from its neighbours while keeping the series look (same background, same font, same accent)? Does the 3:4 crop cut anything? Fix and re-render.

## 4. Deliver

`cover.png` (upload as the reel cover) and `grid.png` (preview only), plus a one-line note on what you checked.
