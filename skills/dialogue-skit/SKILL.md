---
name: dialogue-skit
description: Make a short animated comedy skit (9:16 MP4) where two characters talk, with real or TTS voices, lip sync, burned-in subtitles, music and SFX. Use for meme-style reels, relatable-pain skits and shareable dialogue videos, not for step-by-step tutorials (use text-reel for those).
---

# Dialogue skit

Two built-in original characters, **dev** (headphones, t-shirt) and **bot** (monitor-head robot), act out a short script. Voices come from the user's recordings or ElevenLabs; without voices the skit still renders with estimated timing, so the script can be checked before anyone records anything.

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
- **Hook**: the first spoken line or headline lands in the first second. No setup monologue.
- **Dialogue**: 4–8 lines, 20–35 s. Every line either escalates or twists; the last line is the punchline or loops back to the first line (loops get rewatched). Keep each line under ~12 words so subtitles stay on 1–2 lines.
- **Moods per line** (`neutral happy sad shocked angry deadpan smug think`, bot also `error love`) and `react:` beats where the listener's face is the joke.
- **Share sticker** ("send this to your PM/team lead/…") placed mid-video, and a cover headline.
- Voice plan: who records what, or which ElevenLabs voices. Assumptions listed at the end.

Keep it kind: punch at situations and tools, not at real named people, employers or clients.

## 4. Build scenes.yaml and check timing without voices

Start from `examples/dialogue-skit/scenes.yaml`. Put each character in `cast` (feet at y≈1170 leaves room for subtitles), lines in `dialogue`, one `headline` per scene.

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
**c) ElevenLabs TTS** (costs credits; ask before running):
```bash
export ELEVENLABS_API_KEY=...        # never write the key into a file in the repo
# scenes.yaml: audio: {tts_voices: {dev: "<voice id>", bot: "<voice id>"}}
reelkit voices tts my-skit/scenes.yaml               # only generates lines that don't have a clip yet
```
This writes `vo_<key>.wav` + `vo.json` next to `scenes.yaml`. Re-run `reelkit timing`: lines now say `[voice]` and the scene lengths follow the real audio. Lip sync uses each clip's loudness.

## 6. Render

**Pillow:** `reelkit render my-skit/scenes.yaml -o my-skit.mp4` and `reelkit cover my-skit/scenes.yaml -o cover.png`
**Remotion:** `cd engines/remotion && npm install && npm run prep -- ../../my-skit/scenes.yaml && npm run render -- ../../my-skit.mp4`

Music ducks under the voices automatically (`audio.duck`). Check a few stills before the full render (faces not hidden by stickers, subtitles not covering mouths, nothing below y 1440).

## 7. Deliver

The MP4, the cover, the caption (first ~125 characters = the hook; end with the share prompt) and assumptions. Commit `scenes.yaml` and `vo.json`; keep audio/video files out of git and keep the original voice recordings somewhere safe.
