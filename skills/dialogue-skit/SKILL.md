---
name: dialogue-skit
description: Make a short animated skit or story (9:16 MP4) where characters talk, for any niche, with your own recorded voices or AI voices, lip sync, burned-in subtitles, music and SFX. Use for comedy, relatable-pain memes, mini stories and shareable dialogue videos, not step-by-step tutorials (use text-reel for those).
---

# Dialogue skit

Characters act out a short script. Pick the cast from `docs/img/characters.jpg` (or `reelkit characters -o characters.png`): **person** (customizable hair, skin, outfit, hat, glasses, beard, shirt icon), **bot** (robot), **blob** (cute mascot), **dev** (person with headphones and a `</>` shirt), or named characters saved in `brand.yaml > characters`. Voices come from the user's recordings, ElevenLabs, OpenAI or a free built-in voice; without voices the skit still renders with estimated timing, so the script can be checked before anyone records anything.

Engine: https://github.com/ashishjain-dev/ctrl-alt-lazy-reel-kit (see `docs/scenes-reference.md` for every key).

## 1. Get the engine (once)

```bash
git clone --depth 1 https://github.com/ashishjain-dev/ctrl-alt-lazy-reel-kit && cd ctrl-alt-lazy-reel-kit
pip install -e engines/pillow && reelkit check
```

## 2. Ask which engine (always ask, once per project)

> Which render engine?
> **(a) Pillow + ffmpeg** (default): Python only, flat 2D characters, fastest.
> **(b) Remotion + Three.js** (optional): 3D characters and smoother motion. Needs Node 18+, `npm install` and a headless Chrome. Remotion is free for individuals and small teams; larger companies need a paid Remotion licence (check remotion.dev/license).

No answer → (a).

## 3. Write the script, confirm before voices or rendering

Show the user, and wait for a go-ahead:
- **Premise** in one line, and who the audience is (the joke must land for them without context).
- **Cast**: which characters, and their look if custom (save it in `brand.yaml > characters` for a series). If the built-ins can't do the look (a grandmother in a sari, a chef, a character painted in an art style), Claude writes the character as a file (`characters: {dadi: {file: dadi.py}}`) following `docs/custom-art.md` and the style's section in `docs/style-guides.md`; it lip-syncs and changes mood like the built-ins.
- **Setting** (optional): a background or props drawn for the skit (an office, a kitchen) as a `custom` element.
- **Hook**: the first spoken line or headline lands in the first second. No setup monologue.
- **Dialogue**: 4–8 lines, 20–35 s. Every line either escalates or twists; the last line is the punchline or loops back to the first line (loops get rewatched). Keep each line under ~12 words so subtitles stay on 1–2 lines.
- **Moods per line** (`neutral happy sad shocked angry deadpan smug think`, bot also `error love`) and `react:` beats where the listener's face is the joke.
- **Share sticker** ("send this to your PM/team lead/…") placed mid-video, and a cover headline.
- Voice plan: who records what, or which ElevenLabs voices. Assumptions listed at the end.

Keep it kind: punch at situations and tools, not at real named people, employers or clients.

## 4. Build scenes.yaml and check timing without voices

Start from `examples/dialogue-skit/scenes.yaml`. Put each character in `cast` (feet at y≈1170 leaves room for subtitles), lines in `dialogue`, one `headline` per scene. A `narrator` line (no character) works for setup text like "Monday, 9 AM".

```bash
reelkit timing  my-skit/scenes.yaml            # every line with start/end, marked [estimate]
reelkit stills  my-skit/scenes.yaml -o /tmp/st/f
```

## 5. Voices

Each dialogue line gets a `voice:` key (e.g. `d1`, `b1`). Three ways to fill them:

**a) One recorded/TTS dialogue file** (best for natural pacing; leave ~1 s of silence between lines):
```bash
reelkit voices gaps  dialogue.mp3                        # find the silent gaps
reelkit voices split dialogue.mp3 d1=0-1.6 b1=2.4-4.1 d2=4.9-6.0 --dir my-skit --robot b
#   --robot b   : keys starting with "b" get a light speaker filter (robot voice)
#   --tighten 0.12 : shorten long pauses inside a line;  --tempo 1.05 : speed up without pitch change (keep ≤1.1)
```
**b) One file per line**: name them anything and split each with a single range (`d1=0-99`).
**c) AI voices** (paid ones cost credits; ask before running):
```bash
export ELEVENLABS_API_KEY=...   # or OPENAI_API_KEY=...; never write keys into a file in the repo
# scenes.yaml:
#   audio:
#     tts: {provider: elevenlabs, voices: {maya: "<voice id>", bot: "<voice id>", narrator: "<voice id>"}}
#     (openai voices are names like alloy, onyx, nova; add `instructions: "dry, sarcastic"` for tone)
reelkit voices tts my-skit/scenes.yaml               # only lines without a clip yet; --force to redo
reelkit voices tts my-skit/scenes.yaml --provider say  # free macOS voice (espeak on Linux), fine for drafts
```
**Recording yourself?** `reelkit voices script my-skit/scenes.yaml` prints every line with its key, ready to read or paste into the ElevenLabs Dialogue editor.

This writes `vo_<key>.wav` + `vo.json` next to `scenes.yaml`. Re-run `reelkit timing`: lines now say `[voice]` and the scene lengths follow the real audio. Lip sync uses each clip's loudness.

## 6. Render

**Pillow:** `reelkit render my-skit/scenes.yaml -o my-skit.mp4` and `reelkit cover my-skit/scenes.yaml -o cover.png`
**Remotion:** `cd engines/remotion && npm install && npm run prep -- ../../my-skit/scenes.yaml && npm run render -- ../../my-skit.mp4` (characters are 3D here, same looks and moods)

Music ducks under the voices automatically (`audio.duck`). Check a few stills before the full render (faces not hidden by stickers, subtitles not covering mouths, nothing below y 1440).

## 7. Deliver

The MP4, the cover, the caption (first ~125 characters = the hook; end with the share prompt) and assumptions. Commit `scenes.yaml` and `vo.json`; keep audio/video files out of git and keep the original voice recordings somewhere safe.
