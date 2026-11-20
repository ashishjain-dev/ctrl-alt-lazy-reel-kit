# scenes.yaml reference

One file describes a whole video. Both engines read it: **Pillow** (`reelkit render`) and **Remotion + Three.js** (`npm run prep` + `npm run render`).
Coordinates are output pixels on a 1080×1920 canvas. Times are seconds from the start of the scene.

```yaml
meta:
  title: my-reel          # used for file names
  fps: 60                 # 30 or 60
  size: [1080, 1920]      # 9:16
brand: ../brand.yaml      # optional, relative to this file (see brand.example.yaml)

audio:
  music: {mood: chill, bpm: 92, volume: 0.55, drums_from: 0}   # mood: chill | upbeat | tense | none
  sfx: true               # auto sound effects from the elements (whoosh, blips, typing, hits)
  duck: 0.35              # music level under voices (0..1)
  voices: vo.json         # written by `reelkit voices split|tts`
  tts_voices: {dev: "<elevenlabs voice id>", bot: "<elevenlabs voice id>"}   # only for `voices tts`

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
| `character` | who dev/bot, mood, x 540, y 1420 (feet), scale 1, enter_from | static character (no dialogue) |
| `progress_ring` | x, y, r 120, dur 2, text, color accent | loading / countdown |

## Characters and dialogue

Built-in, original characters: **dev** (headphones, t-shirt) and **bot** (monitor-head robot). Moods:
`neutral happy sad shocked angry deadpan smug think` (+ `error love` for bot). Recolour them in `brand.yaml > characters`.
Pillow draws them flat 2D; Remotion draws them in 3D with Three.js. Same names, moods and colours.

```yaml
cast:
  - {who: dev, x: 300, y: 1170, scale: 0.78, mood: neutral}
  - {who: bot, x: 790, y: 1170, scale: 0.72}
dialogue_at: 0.4          # first line starts here
gap: 0.35                 # silence between lines
tail: 0.6                 # hold after the last line
dialogue:
  - {who: dev, voice: d1, text: "Can you review my PR?", mood: happy}
  - {who: bot, voice: b1, text: "I did. *Delete it.*", mood: deadpan, react: {dev: shocked}}
  - {who: dev, text: "No voice file? Timing is estimated.", at: 5.0, gap: 0.5, subtitle: true}
```

- `voice` is the clip key in `vo.json`. With a voice the line lasts exactly as long as the clip and the mouth follows its loudness (lip sync). Without one, timing is estimated at ~165 wpm and the mouth moves on a pattern.
- `mood` changes the speaker's face from that line on. `react` changes other characters' faces.
- Subtitles are burned in above the bottom safe zone.

## Safe zones (Instagram / TikTok / Shorts)

The app UI covers the top ~230 px and the bottom ~480 px, plus a column of buttons on the right. Keep important things inside **y 280–1440** and **left of x ≈ 850**. The frame's label, handle and progress bar sit just above `safe_top`.
