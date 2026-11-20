---
name: make-video
description: Start here to make any short vertical video (Instagram Reel, YouTube Short, TikTok) for any topic or niche. Asks what the video is about, whether there is a script (or writes one), how the audio should work (music only, own voice, or AI voice), which characters to use and which render engine, then builds it with the ctrl-alt-lazy-reel-kit engine.
---

# Make a video

The front door for https://github.com/ashishjain-dev/ctrl-alt-lazy-reel-kit. Works for any niche: tech, fitness, food, finance, education, small business, travel, motivation, comedy. Collect the answers below, confirm a plan, then hand off to the right skill (`reel-planner`, `text-reel`, `dialogue-skit`, `reel-cover-grid`) or follow their steps directly if they aren't installed.

## 0. Get the engine (once)

```bash
git clone --depth 1 https://github.com/ashishjain-dev/ctrl-alt-lazy-reel-kit && cd ctrl-alt-lazy-reel-kit
pip install -e engines/pillow        # in a venv, or add --break-system-packages
reelkit check                        # ffmpeg, fonts, emoji font, which text-to-speech options exist here
```

## 1. Ask, in at most two rounds

Use your multiple-choice question tool if you have one; otherwise ask in one short message. Skip anything the user already told you. Suggest a sensible default for each so a "you decide" answer works.

**Round 1: the video**
1. **Topic and goal**: what is it about, and what should a viewer do after (save, share, follow, buy, comment)?
2. **Audience**: who is it for, and how much do they already know? Which language?
3. **Format** (pick one, or "you decide"):
   - *Tip / tutorial*: headlines, steps, checklist, terminal for code → `text-reel`
   - *Narrated explainer*: a voice-over over visuals (stats, myth vs fact, lists, photos) → `text-reel` with `narrator` lines
   - *Character skit*: two or more characters talking, comedy or story → `dialogue-skit`
   - *Top-N / countdown*, *myth vs fact*, *before / after*, *quote / story* → `text-reel` with `list`, `split`, `quote`
   - *Style Drop*: one short animated scene in several art styles, "which one wins?" → `style-drop`
4. **Length**: 15–30 s (default 25 s) for reach, up to 60 s for a real tutorial.
5. **Script**: do they have one? If yes, ask them to paste it and keep their words (fix only timing and clarity, and say what you changed). If not, Claude writes it (step 2).

**Round 2: look and sound**
6. **Audio** (pick one):
   - *Music + sound effects only* (no voice; text carries the story). Default for tips.
   - *My own voice*: Claude prints the lines (`reelkit voices script`), they record, then `reelkit voices split` cuts the recording.
   - *AI voice*: ElevenLabs (`ELEVENLABS_API_KEY`), OpenAI (`OPENAI_API_KEY`), or the free built-in voice (macOS `say`, `espeak-ng` on Linux, robotic). Mention that the paid ones cost credits.
   - Music mood: `chill`, `upbeat`, `tense`, or `none`.
7. **Characters**: show `docs/img/characters.jpg` (or run `reelkit characters -o characters.png`) and ask:
   - none (text-only video), or
   - built-ins: `person` (customizable), `bot` (robot), `blob` (cute mascot), `dev` (person with headphones and a `</>` shirt), or
   - a custom person: hair (short, long, curly, bun, spiky, bald), hair colour, skin tone, shirt/pants colours, hat (none, cap, beanie), glasses, headphones, beard, a short shirt icon ("FIT", "$"). Save them under a name in `brand.yaml > characters` so every video in the series reuses them.
   - **a character drawn for them** (a grandmother in a sari, a chef, a Warli farmer, a character painted in the chosen art style): Claude writes it as a small file that talks and lip-syncs like the built-ins. See `docs/custom-art.md`.
7b. **Pictures the story needs** (a crow and a pot, a product, a kitchen, a village): Claude can draw them for this video as a custom element, in the chosen art style. Ask what must be shown; keep it to a few clear pictures.
   - Moods available: neutral, happy, sad, shocked, angry, deadpan, smug, think, wink (+ error, love for bot/blob).
8. **Art style** (optional, Pillow engine): keep the clean default, or re-skin the whole video with `style:` fish-scale-folk (folk painting), rice-paper (ink wash), mud-wall (white on mud wall art), cyan-plan (blueprint) or cut-card (paper cut-out). See `docs/img/style-drop-kite.jpg`.
9. **Brand**: their handle, a small top label (e.g. "MONEY TIPS"), and 1–2 brand colours, or keep the defaults. Write `brand.yaml` from `brand.example.yaml`.
10. **Engine**:
   > **(a) Pillow + ffmpeg** (default): Python only, flat 2D characters, renders anywhere.
   > **(b) Remotion + Three.js** (optional): smoother motion, 3D characters. Needs Node 18+, `npm install` and a headless Chrome. Remotion is free for individuals and small teams; larger companies need a paid licence (remotion.dev/license).

## 2. Write the script (when they don't have one)

Follow `reel-planner`: check facts for anything factual (health, money, law, tech) against reliable current sources and keep claims modest; never invent statistics or quotes; give 3–5 ranked hooks (the payoff or the pain within 2 s, no greetings); a beat sheet with timings; one idea per screen; lines under ~12 words; a share or save prompt in the middle; a cover headline; a caption. For health, money or legal topics add a one-line "not professional advice" note in the caption, not on screen.

## 3. Confirm the plan

Show one compact plan: format, hook, beat sheet with times, spoken lines (if any), characters and moods, audio choice, engine, cover headline, caption, and the assumptions you made. Wait for an explicit go-ahead before generating voices (they can cost money) or rendering.

## 4. Build

- Copy the closest example as a starting point: `examples/folk-story-crow` (narrated story, custom storyteller + pictures in an art style), `examples/text-reel` (tutorial), `examples/fitness-myths` (narrated myth vs fact with a character), `examples/money-tip` (stat, list, quote), `examples/dialogue-skit` (two characters talking).
- Every key is in `docs/scenes-reference.md`. Custom characters and pictures: follow `docs/custom-art.md` and the style's section in `docs/style-guides.md`, save the files next to scenes.yaml (they are reused by the next episode), and check them with `reelkit stills` before rendering. `examples/folk-story-crow` is a full narrated story built this way. Narration lines use `who: narrator` (no character on screen). Give every spoken line a `voice:` key (n1, n2… or a1, b1…).
- Voices: `reelkit voices tts scenes.yaml --provider …`, or the record → `voices gaps` → `voices split` flow. Then `reelkit timing scenes.yaml`: lines should say `[voice]`.
- Check: `reelkit stills scenes.yaml -o stills/f` and look at the contact sheet: nothing clipped or overlapping, subtitles not covering faces, content inside y 280–1440 and left of x≈850, emoji showing (if not, install a colour emoji font or drop them).
- Render: `reelkit render scenes.yaml -o video.mp4` and `reelkit cover scenes.yaml -o cover.png` (Remotion: `cd engines/remotion && npm install && npm run prep -- <scenes.yaml> && npm run render -- <out.mp4> && npm run cover -- <cover.png>`).

## 5. Deliver

The MP4, the cover, the caption, and one line listing what you assumed. Offer the next natural step: a series (same characters and brand, next topic) or a grid check with `reel-cover-grid`. Keep media files out of git; `scenes.yaml`, `brand.yaml` and `vo.json` are the source.
