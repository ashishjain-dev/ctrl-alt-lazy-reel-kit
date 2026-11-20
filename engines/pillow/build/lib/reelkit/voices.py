"""Voice tools for dialogue skits.

split : cut one recorded/TTS dialogue file into vo_<key>.wav clips + vo.json (durations + 60 Hz
        lip-sync envelope). Keys are the `voice:` names used in scenes.yaml.
tts   : generate every line that has a `voice:` key. Providers: elevenlabs (ELEVENLABS_API_KEY),
        openai (OPENAI_API_KEY), say (macOS, free, offline), espeak (espeak-ng, free, offline).
        scenes.yaml: audio: {tts: {provider: openai, voices: {narrator: alloy, coach: onyx}}}
script: print the spoken lines, for recording yourself or pasting into a TTS tool.
"""
import json
import os
import shutil
import subprocess
import sys
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


def _tts_cfg(tl):
    a = tl.raw.get("audio", {}) or {}
    cfg = dict(a.get("tts", {}) or {})
    cfg.setdefault("voices", a.get("tts_voices", {}) or {})
    return cfg


def _is_robot(tl, who):
    from . import characters
    try:
        fn, _ = characters.resolve(who, tl.raw.get("characters") or {})
        return fn is characters.bot
    except ValueError:
        return False


def _http(url, body, headers):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def _synth(provider, text, voice, cfg, out_base):
    """Write speech for `text` and return the path of the audio file."""
    if provider == "elevenlabs":
        key = os.environ.get("ELEVENLABS_API_KEY") or sys.exit("Set ELEVENLABS_API_KEY first (never commit it).")
        if not voice:
            sys.exit("ElevenLabs needs a voice id per speaker: audio.tts.voices: {narrator: <id>, ...}")
        data = _http(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
                     {"text": text, "model_id": cfg.get("model", "eleven_multilingual_v2")},
                     {"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
        path = out_base + ".mp3"
        open(path, "wb").write(data)
    elif provider == "openai":
        key = os.environ.get("OPENAI_API_KEY") or sys.exit("Set OPENAI_API_KEY first (never commit it).")
        body = {"model": cfg.get("model", "gpt-4o-mini-tts"), "voice": voice or "alloy", "input": text, "response_format": "mp3"}
        if cfg.get("instructions"):
            body["instructions"] = cfg["instructions"]       # e.g. "warm, upbeat, a little sarcastic"
        data = _http("https://api.openai.com/v1/audio/speech", body,
                     {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        path = out_base + ".mp3"
        open(path, "wb").write(data)
    elif provider == "say":                                     # macOS built-in, free, offline
        path = out_base + ".aiff"
        cmd = ["say", "-o", path] + (["-v", voice] if voice else []) + [text]
        subprocess.run(cmd, check=True)
    elif provider == "espeak":                                  # Linux/Windows, free, offline, robotic
        path = out_base + ".wav"
        exe = shutil.which("espeak-ng") or shutil.which("espeak") or sys.exit("Install espeak-ng first.")
        subprocess.run([exe, "-v", voice or "en-us", "-s", str(cfg.get("wpm", 165)), "-w", path, text], check=True)
    else:
        sys.exit(f"unknown TTS provider '{provider}': use elevenlabs | openai | say | espeak")
    return path


def tts(tl, provider=None, force=False):
    """Generate every dialogue/narration line that has a `voice:` key and no clip yet."""
    cfg = _tts_cfg(tl)
    provider = provider or cfg.get("provider") or ("elevenlabs" if os.environ.get("ELEVENLABS_API_KEY") else
                                                   "openai" if os.environ.get("OPENAI_API_KEY") else
                                                   "say" if shutil.which("say") else "espeak")
    folder = tl.vo_dir
    done = _load_vo(folder)["dur"]
    n = 0
    for s in tl.scenes:
        for ln in s.lines:
            if not ln.voice or (ln.voice in done and not force):
                continue
            voice = (cfg.get("voices") or {}).get(ln.who) or (cfg.get("voices") or {}).get("default")
            raw = _synth(provider, ln.text.replace("*", ""), voice, cfg, os.path.join(folder, f"vo_{ln.voice}_src"))
            wav = os.path.join(folder, f".tts_{ln.voice}.wav")
            subprocess.run([FF, "-y", "-loglevel", "error", "-i", raw, "-ac", "1", "-ar", str(SR), wav], check=True)
            d = add_clip(folder, ln.voice, read_wav(wav), robot=_is_robot(tl, ln.who))
            os.remove(wav)
            n += 1
            print(f"{provider} {ln.voice} ({ln.who}): {d}s")
    print(f"{n} line(s) generated with {provider}" if n else "all lines already have voices (use --force to redo)")


def script(tl):
    """Printable script: one line per spoken line, ready to paste into a TTS tool or read aloud."""
    out = []
    for s in tl.scenes:
        for ln in s.lines:
            out.append(f"[{ln.voice or '-'}] {ln.who.upper()}: {ln.text.replace('*', '')}")
    out.append("")
    out.append("Record with ~1 s of silence between lines, then:")
    out.append("  reelkit voices gaps recording.mp3")
    keys = " ".join(f"{ln.voice}=START-END" for s in tl.scenes for ln in s.lines if ln.voice)
    out.append(f"  reelkit voices split recording.mp3 {keys} --dir <folder of scenes.yaml>")
    return "\n".join(out)
