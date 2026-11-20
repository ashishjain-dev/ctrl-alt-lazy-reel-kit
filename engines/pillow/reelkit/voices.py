"""Voice tools for dialogue skits.

split : cut one recorded/TTS dialogue file into vo_<key>.wav clips + vo.json (durations + 60 Hz
        lip-sync envelope). Keys are the `voice:` names used in scenes.yaml.
tts   : (optional) generate every dialogue line with ElevenLabs. Needs ELEVENLABS_API_KEY and
        `audio.tts_voices: {dev: <voice_id>, bot: <voice_id>}` in scenes.yaml. Costs credits.
"""
import json
import os
import subprocess
import urllib.request

import numpy as np

from .audio import read_wav, write_wav

FF = os.environ.get("FFMPEG", "ffmpeg")
SR = 48000


def _tighten(x, keep):
    hop = SR // 100
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + hop] ** 2)) + 1e-9) for i in range(0, len(x), hop)])
    quiet = db < db.max() - 32
    out, i, n = [], 0, len(quiet)
    while i < n:
        j = i
        while j < n and quiet[j] == quiet[i]:
            j += 1
        seg = x[i * hop:j * hop]
        if quiet[i] and 0 < i and j < n and (j - i) * hop > 0.2 * SR:
            k = int(keep * SR)
            seg = np.concatenate([seg[:k // 2], seg[-(k - k // 2):]])
        out.append(seg)
        i = j
    return np.concatenate(out)


def envelope(x, fps=60):
    hop = SR // fps
    env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop + 1, hop)] or [0.0])
    env = env / (env.max() + 1e-9)
    return [round(float(v), 3) for v in env]


def _load_vo(folder):
    p = os.path.join(folder, "vo.json")
    return json.load(open(p)) if os.path.exists(p) else {"env": {}, "dur": {}}


def _save_vo(folder, vo):
    json.dump(vo, open(os.path.join(folder, "vo.json"), "w"))


def add_clip(folder, key, x, robot=False):
    if robot:   # light band-limit so a robot voice sounds a bit "speaker-ish"
        tmp = os.path.join(folder, f".tmp_{key}.wav")
        write_wav(tmp, x, stereo=False)
        out = os.path.join(folder, f".tmp2_{key}.wav")
        subprocess.run([FF, "-y", "-loglevel", "error", "-i", tmp, "-af", "highpass=f=180,lowpass=f=7000",
                        "-ar", str(SR), "-ac", "1", out], check=True)
        x = read_wav(out)
        os.remove(tmp)
        os.remove(out)
    write_wav(os.path.join(folder, f"vo_{key}.wav"), x, stereo=False)
    vo = _load_vo(folder)
    vo["env"][key] = envelope(x)
    vo["dur"][key] = round(len(x) / SR, 3)
    _save_vo(folder, vo)
    return vo["dur"][key]


def split(src, specs, folder=".", tighten=None, tempo=1.0, robot_prefix=None):
    """specs: ["a1=0-1.66", "b1=1.9-3.2"]. Keys starting with robot_prefix get the speaker filter."""
    for s in specs:
        key, rng = s.split("=")
        a, b = map(float, rng.split("-"))
        af = f"afade=t=in:d=0.01,afade=t=out:st={max(0, b - a - 0.02):.3f}:d=0.02"
        if tempo != 1.0:
            af += f",atempo={tempo}"
        tmp = os.path.join(folder, f".cut_{key}.wav")
        subprocess.run([FF, "-y", "-loglevel", "error", "-ss", str(a), "-to", str(b), "-i", src, "-ac", "1",
                        "-ar", str(SR), "-af", af, tmp], check=True)
        x = read_wav(tmp)
        os.remove(tmp)
        if tighten:
            x = _tighten(x, tighten)
        d = add_clip(folder, key, x, robot=bool(robot_prefix and key.startswith(robot_prefix)))
        print(f"{key}: {a:.2f}-{b:.2f}s -> vo_{key}.wav ({d}s)")


def silences(src, db=-35, min_dur=0.25):
    """Print the silent gaps in a dialogue file, to find cut points."""
    r = subprocess.run([FF, "-i", src, "-af", f"silencedetect=n={db}dB:d={min_dur}", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [ln for ln in r.stderr.splitlines() if "silence_" in ln]


def tts_elevenlabs(tl, model="eleven_multilingual_v2", only_missing=True, robot_who=("bot",)):
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise SystemExit("Set ELEVENLABS_API_KEY first (never commit it).")
    voices = (tl.raw.get("audio", {}) or {}).get("tts_voices", {})
    folder = tl.vo_dir
    done = _load_vo(folder)["dur"]
    for s in tl.scenes:
        for ln in s.lines:
            if not ln.voice or (only_missing and ln.voice in done):
                continue
            vid = voices.get(ln.who)
            if not vid:
                raise SystemExit(f"audio.tts_voices has no voice id for '{ln.who}'")
            req = urllib.request.Request(
                f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
                data=json.dumps({"text": ln.text.replace("*", ""), "model_id": model}).encode(),
                headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
            mp3 = os.path.join(folder, f"vo_{ln.voice}.mp3")
            with urllib.request.urlopen(req, timeout=60) as r, open(mp3, "wb") as f:
                f.write(r.read())
            wav = os.path.join(folder, f".tts_{ln.voice}.wav")
            subprocess.run([FF, "-y", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), wav], check=True)
            d = add_clip(folder, ln.voice, read_wav(wav), robot=ln.who in robot_who)
            os.remove(wav)
            print(f"tts {ln.voice} ({ln.who}): {d}s")
