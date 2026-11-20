---
name: text-reel
description: Make a 9:16 tip, tutorial or narrated explainer video (Instagram Reels, YouTube Shorts, TikTok) for any niche, as an MP4 with animated headlines, stats, lists, myth-vs-fact cards, photos, emoji, optional characters and voice-over, original music and SFX, plus a cover. Use when someone wants a short explainer, tip, list or tutorial video from a topic or script.
---

# Text reel

Produces one ready-to-post vertical video (1080×1920, 30/60 fps, H.264 + AAC at -14 LUFS) and a cover PNG from a `scenes.yaml` script, using the engine in this repo: https://github.com/ashishjain-dev/ctrl-alt-lazy-reel-kit

## 1. Get the engine (once per machine/session)

```bash
git clone --depth 1 https://github.com/ashishjain-dev/ctrl-alt-lazy-reel-kit
cd ctrl-alt-lazy-reel-kit
pip install -e engines/pillow        # add --break-system-packages on a managed system Python, or use a venv
reelkit check                        # python deps, ffmpeg, fonts; follow its hints for anything MISSING
```

## 2. Ask which engine (always ask, once per project)

Ask the user exactly this, then remember the answer for the rest of the session:

> Which render engine?
> **(a) Pillow + ffmpeg** (default): Python only, flat 2D characters, renders anywhere, ~1 min for a 30 s reel.
> **(b) Remotion + Three.js** (optional): smoother motion and 3D characters. Needs Node 18+, `npm install` (~250 MB) and a headless Chrome. Remotion is free for individuals and small teams, but companies above a few people need a paid Remotion company licence (check remotion.dev/license).

No answer → use (a). Both engines read the same `scenes.yaml`, so switching later costs nothing.

## 3. Plan, then confirm before rendering

Write the plan in chat and wait for an explicit go-ahead before rendering:
- **Topic + the one idea** the viewer leaves with. Verify every factual claim (numbers, health, money, law, versions, commands) against reliable current sources before it goes on screen; keep claims modest.
- **Hook options** (3–5, ranked): the first frame must state the payoff or the pain within 2 s. No greetings, no "in this video".
- **Scene outline with timings**: hook (≤3 s) → pain/setup → the fix (one idea per screen) → payoff → CTA. 15–45 s total. Leave ≥2 s per line of on-screen text so it can be read on first watch.
- **Cover headline** (≤7 words, one highlighted word) and a **caption draft**: the first ~125 characters carry the hook, then a save/share prompt, 3–5 specific hashtags.
- Assumptions you made, listed at the end.

If the user has a `reel-planner` skill, use it for this step.

## 4. Write scenes.yaml

Start from the closest example: `examples/text-reel` (tech tip with a terminal), `examples/fitness-myths` (narrated myth vs fact with a character), `examples/money-tip` (stat, top-3 list, quote). Full schema: `docs/scenes-reference.md`.

Pick elements by what the scene says:
- a claim → `headline`; a number → `stat` (counts up); steps → `list` or `checklist`; myth vs fact / before vs after → `split`; a saying → `quote`; a product, dish or place → `photo` (slow zoom) or `image`; code or commands → `terminal`; the punchline → one `stamp` or `sticker`; a reaction → `emoji` or a `character` with a mood.
- Voice-over: `dialogue` lines with `who: narrator` and a `voice:` key. Subtitles are burned in and paged two lines at a time.
- Characters (optional): show `docs/img/characters.jpg` and let the user pick `person` (customizable), `bot`, `blob` or `dev`, or define a named one in `brand.yaml > characters`.

Rules that keep reels watchable:
- Headline at y≈430 on every scene; content between y 280 and 1440 and left of x≈850 (app UI covers the rest). Leave room above y≈1180 when there are subtitles.
- One idea per screen, ≥2 s per line of text, something changes every 1.5–2 s.
- Use `*word*` for the single most important word, not whole sentences. Emoji need a colour emoji font (`reelkit check`).
- Brand: copy `brand.example.yaml` to `brand.yaml` and set handle, label, colours, characters. Reference it with `brand: brand.yaml`.

## 5. Check stills, then render

**Pillow:**
```bash
reelkit timing  my-reel/scenes.yaml                     # scene timings
reelkit stills  my-reel/scenes.yaml -o /tmp/st/f        # PNGs + /tmp/st/f_sheet.png contact sheet
reelkit render  my-reel/scenes.yaml -o my-reel.mp4 --preview   # fast low-quality pass (optional)
reelkit render  my-reel/scenes.yaml -o my-reel.mp4
reelkit cover   my-reel/scenes.yaml -o my-reel-cover.png
```
**Remotion + Three.js:**
```bash
cd engines/remotion && npm install
npm run prep -- ../../my-reel/scenes.yaml               # writes public/reel.json (+ music/SFX if Python is set up)
npx remotion still Reel /tmp/f.png --frame=120          # spot-check frames
npm run render -- ../../my-reel.mp4
npm run cover -- ../../my-reel-cover.png
```
If Remotion can't download Chrome (offline/locked-down machine), pass `--browser-executable=/path/to/chrome`; on servers without a GPU add `--gl=swangle`.

**Always look at the stills/contact sheet before the full render**: clipped or overlapping text, bad line breaks, missing glyphs (fonts have no emoji: use ✓ × → instead), anything outside the safe zone. Fix and re-check.

## 6. Deliver

Send the MP4 and the cover, the final caption (add a one-line "not professional advice" note for health, money or legal topics), and a one-line note of anything you assumed. Media files don't belong in git; commit only `scenes.yaml`, `brand.yaml` and `vo.json`.
