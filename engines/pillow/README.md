# reelkit (Pillow engine, default)

Pure Python: **Pillow** draws every frame at 2× and downsamples, **numpy** makes the music, SFX and lip-sync envelopes, **ffmpeg** encodes. No animation framework, no browser.

```bash
pip install -e engines/pillow     # gives you the `reelkit` command (or run `python -m reelkit` from this folder)
reelkit check                     # deps, ffmpeg, fonts
reelkit --help
```

| Module | What it does |
|---|---|
| `timeline.py` | scenes.yaml → absolute timeline (scenes, dialogue timing from voice clips, camera beats, SFX events) |
| `render.py` | frame renderer (camera punch-ins/shakes, frame overlay), stills + contact sheet, multiprocess encode |
| `elements.py` | headline, text, terminal, bubble, sticker, pill, checklist, stamp, image, character, progress_ring, subtitles |
| `characters.py` | the two built-in characters (`dev`, `bot`); register your own in `CHARACTERS` |
| `audio.py` | generated music (chill / upbeat / tense), SFX, voice placement, ducking |
| `voices.py` | split a dialogue file into clips + lip-sync envelope; optional ElevenLabs TTS |
| `covers.py` | cover PNG + 3:4 profile-grid preview |
| `brand.py` | brand.yaml loading, font lookup |

Requirements: Python 3.9+, ffmpeg 6+ with libx264, and fonts (Inter + DejaVu by default; any TTF/OTF works via `brand.yaml > fonts`). Speed: about 1 minute per 15 s of 60 fps video on 2 cores; `--preview` is faster, `--workers N` uses more cores.

Add an element type: write `def my_el(c, im, el, t)` in `elements.py` and add it to `TYPES`. `c` is a `Cv` (draw with output-pixel coordinates), `t` is scene-local time.
