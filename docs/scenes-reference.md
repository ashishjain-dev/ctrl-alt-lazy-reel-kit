# scenes.yaml reference

One file describes a whole video. Both engines read it: **Pillow** (`reelkit render`) and **Remotion + Three.js** (`npm run prep` + `npm run render`).
Coordinates are output pixels on a 1080×1920 canvas. Times are seconds from the start of the scene.

```yaml
meta:
  title: my-reel          # used for file names
  fps: 60                 # 30 or 60
  size: [1080, 1920]      # 9:16
  clean: false            # true = no label / handle / progress bar / fades (e.g. single Style Drop clips)
brand: ../brand.yaml      # optional, relative to this file (see brand.example.yaml)
style: mud-wall           # optional art style for the whole reel (Pillow engine): fish-scale-folk, rice-paper,
                          # mud-wall, cyan-plan, cut-card. Re-skins background, colours, border, subtitles

audio:
  music: {mood: chill, bpm: 92, volume: 0.55, drums_from: 0}   # mood: chill | upbeat | tense | none
  sfx: true               # auto sound effects from the elements (whoosh, blips, typing, hits)
  duck: 0.35              # music level under voices (0..1)
  voices: vo.json         # written by `reelkit voices split|tts`
  tts:                    # only for `reelkit voices tts`
    provider: elevenlabs  # elevenlabs | openai | say (macOS) | espeak (Linux); default: first one available
    voices: {narrator: "<voice id or name>", maya: "<id>", bot: "<id>", default: "<id>"}
    model: eleven_multilingual_v2      # optional (openai: gpt-4o-mini-tts)
    instructions: "warm, upbeat"       # optional, openai only

characters:               # optional: named characters for this video (same format as brand.yaml > characters)
  maya: {base: person, hair: long, hair_color: "#6b3e26", skin: "#c68c64", shirt: "#e8805c", glasses: true}

cover:                    # `reelkit cover scenes.yaml` / `npm run cover`
  headline: "Your tests are *lying*"
  sub: "one flag fixes it"
  tag: "#07"
  character: {who: bot, mood: smug, x: 740, y: 1560, scale: 0.95}
  glow: accent

scenes:
  - name: hook
    dur: 3.0              # optional when the scene has dialogue (computed from the lines)
    glow: bad             # coloured glow behind the scene (brand colour key or #hex)
    glow_at: [540, 900]
    punch: [1.2]          # extra punch-in zooms (scene start always punches)
    shake: [1.2]          # camera shakes (stamps shake automatically)
    whoosh: true          # whoosh into this scene
    sfx: [{at: 2.0, kind: ding}]   # extra sound effects: whoosh, whoosh_soft, blip, pop, hit, ding, typing
    elements: [...]       # see below
    cast: [...]           # characters that take part in the dialogue
    dialogue: [...]
```

## Text markup

`*word*` highlights a word with the brand `highlight` colour. Works in headline, text, bubble, checklist, subtitles and covers, also across line wraps. `\n` forces a line break.

## Elements

Every element has `type`, `at` (start, default 0), optional `until` (hide after) and optional `sfx` (`none` to silence it).

| type | keys (defaults) | notes |
|---|---|---|
| `headline` | text, x 540, y 430, size 78, w 920, color fg, align m | pops in; wraps to `w` |
| `text` | text, x 540, y 800, size 54, w 940, font bold, color | |
| `terminal` | lines[], x 70, y 620, w 940, size 38, title, cps 26, line_pause 6 | types out; prefixes `$ ` `+ ` green, `! ` `- ` red, `# ` grey; `cps: 0` shows all |
| `bubble` | text, who, x 80, y 700, w 760, size 46, color accent, tail down/none, tail_x | chat bubble |
| `sticker` | text, x 540, y 1100, angle -6, size 42, color highlight | the "send this to…" share sticker |
| `pill` | text, x 540, y 900, size 44, color accent | |
| `checklist` | items[], x 110, y 700, step 0.6, size 48, mark ✓, color good | items appear one by one |
| `stamp` | text, x 540, y 900, angle 12, size 120, color bad | slams in, shakes the camera |
| `image` | src (relative path), x 540, y 900, w 600 | PNG/JPG; logos and screenshots you own |
| `character` | who, mood, x 540, y 1420 (feet), scale 1, enter_from, look {…} | character without dialogue; `look` overrides its options for this one appearance |
| `progress_ring` | x, y, r 120, dur 2, text, color accent | loading / countdown |
| `stat` | value ("73%", "$1,200", "3x"), label, x 540, y 860, size 220, count_up true, count_dur 0.9, color accent | big number that counts up |
| `quote` | text, author, x 90, y 640, w 900, size 56, color accent | quote card (don't invent quotes for real people) |
| `split` | left {title, text, items[], color}, right {…}, y 640, h 480, step 1.2, size 46, vs true, vs_text | myth vs fact, before vs after, don't vs do |
| `photo` | src, x 540, y 860, w 940, h 700, zoom [1.0, 1.15], pan [0.5, 0.5], dur 5, radius 30, caption | photo with slow zoom (Ken Burns); use photos you own or have rights to |
| `list` | items[], x 90, y 620, step 1.0, size 50, gap, countdown false, color accent | numbered top-N list (`countdown: true` shows N..1) |
| `emoji` | char "🔥", x 540, y 900, size 200, angle 0, bounce false | big emoji; needs a colour emoji font on the machine |
| `scene` | name kite, style (default: the reel's `style`, else flat), at, offset | a full-frame animated hero scene painted in an art style (Pillow engine) |
| `custom` | file (a .py next to scenes.yaml), at, until, args {…}, style | art written for this video: `draw(ctx, t, args)`. See [custom-art.md](custom-art.md) |

Emoji also work inline in any text (`"Payday 💸"`). Pillow needs a colour emoji font (Noto Color Emoji on Linux, built in on macOS/Windows); `reelkit check` tells you. Remotion uses the system emoji font the same way.

## Characters and dialogue

Built-in, original characters (drawn from code, nothing to license). See them all: `reelkit characters -o characters.png` or [img/characters.jpg](img/characters.jpg).

| who | what | look options |
|---|---|---|
| `person` | customizable human | `hair` short/long/curly/bun/spiky/bald, `hair_color`, `skin`, `shirt`, `pants`, `accent` (hat/headphones), `hat` none/cap/beanie, `glasses`, `headphones`, `beard`, `shirt_icon` (short text), `cheeks` |
| `bot` | monitor-head robot | `body`, `screen`, `eyes`, `trim` |
| `blob` | round jelly mascot | `body`, `belly`, `sprout` |
| `dev` | preset: person + headphones + `</>` shirt | same as person |

Moods: `neutral happy sad shocked angry deadpan smug think wink` (+ `error love` for bot and blob).
Name your own in `brand.yaml > characters` (or a `characters:` block in scenes.yaml) with a `base:` and any options, then use the name as `who`. A character can also be its own drawing file: `dadi: {file: dadi.py}` with `draw(c, x, y, s, mood, t, talk, opts)`; it gets lip sync, moods and reactions like the built-ins ([custom-art.md](custom-art.md)). Pillow draws them flat 2D; Remotion draws the same looks in 3D.

```yaml
cast:
  - {who: dev, x: 300, y: 1170, scale: 0.78, mood: neutral}
  - {who: bot, x: 790, y: 1170, scale: 0.72}
dialogue_at: 0.4          # first line starts here
gap: 0.35                 # silence between lines
tail: 0.6                 # hold after the last line
dialogue:
  - {who: narrator, voice: n1, text: "Monday, 9 AM."}
  - {who: dev, voice: d1, text: "Can you review my PR?", mood: happy}
  - {who: bot, voice: b1, text: "I did. *Delete it.*", mood: deadpan, react: {dev: shocked}}
  - {who: dev, text: "No voice file? Timing is estimated.", at: 5.0, gap: 0.5, subtitle: true}
```

- `who: narrator` (or any name not in `cast`) is a voice-over: subtitles and audio, no character on screen.
- `voice` is the clip key in `vo.json`. With a voice the line lasts exactly as long as the clip and the mouth follows its loudness (lip sync). Without one, timing is estimated at ~165 wpm and the mouth moves on a pattern.
- `mood` changes the speaker's face from that line on. `react` changes other characters' faces.
- Subtitles are burned in above the bottom safe zone, two lines at a time; long lines page through as they are spoken.

## Style Drop (one scene, many art styles)

A `style_drop:` block replaces `scenes:` with generated cards: a title, a numbered list of styles on the left, a 9:16 card on the right that wipes to the next style every `card_dur` seconds, then an outro of moving tiles and a CTA. Pillow engine only for now. See `skills/style-drop/SKILL.md` and `examples/style-drop-kite/`.

```yaml
style_drop:
  scene: kite                       # built-in hero scene (5 s, cut at 2.0 s)
  # file: my_scene.py               # or your own scene file, painted per style (then also: impact, clip_dur)
  styles: [fish-scale-folk, rice-paper, mud-wall, cyan-plan, cut-card]
  title: ["5 kite styles", "one Makar Sankranti cut"]
  card_dur: 2.0
  clip_offset: 1.05                 # clip time at the start of each card
  wipe: 0.28
  outro: 3.0
  cta: "COMMENT 'KITE'\nFOR THE PROMPTS"
  bg: "#f4ecdc"                     # also: ink, accent, muted
```

## Safe zones (Instagram / TikTok / Shorts)

The app UI covers the top ~230 px and the bottom ~480 px, plus a column of buttons on the right. Keep important things inside **y 280–1440** and **left of x ≈ 850**. The frame's label, handle and progress bar sit just above `safe_top`.
