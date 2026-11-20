"""Turn scenes.yaml into an absolute timeline: scene start/end, dialogue line timing, camera moves
and the sound-effect events that audio.py turns into sound. Video and audio read the same timeline,
so they never drift apart.
"""
import json
import math
import os

import yaml

WPS = 2.75          # words per second when no voice file exists (~165 wpm, close to TTS dialogue)
LINE_PAD = 0.35     # default silence between dialogue lines


class Line:
    def __init__(self, d, start, dur, env):
        self.who = d.get("who", "narrator")
        self.text = d.get("text", "")
        self.mood = d.get("mood")
        self.react = d.get("react", {}) or {}
        self.voice = d.get("voice")
        self.subtitle = d.get("subtitle", True)
        self.start, self.dur, self.env = start, dur, env

    @property
    def end(self):
        return self.start + self.dur

    def talk(self, t):
        """Mouth opening 0..1 at scene-local time t."""
        if not (self.start <= t < self.end):
            return 0.0
        if self.env:
            i = int((t - self.start) * 60)
            return min(1.0, self.env[min(i, len(self.env) - 1)] * 1.4)
        return 0.35 + 0.35 * abs(math.sin((t - self.start) * 11)) * (0.6 + 0.4 * math.sin((t - self.start) * 3.1))


class Scene:
    def __init__(self, d, start, base, vo):
        self.name = d.get("name", f"scene{start:.1f}")
        self.raw = d
        self.glow = d.get("glow")
        self.elements = [dict(e, _base=base) for e in d.get("elements", [])]
        self.lines = []
        t = d.get("dialogue_at", 0.4)
        gap = d.get("gap", LINE_PAD)
        for ld in d.get("dialogue", []) or []:
            key = ld.get("voice")
            if key and key in vo.get("dur", {}):
                dur, env = vo["dur"][key], vo["env"].get(key)
            else:
                dur, env = max(0.9, len(str(ld.get("text", "")).split()) / WPS + 0.25), None
            t = ld.get("at", t)
            self.lines.append(Line(ld, t, dur, env))
            t += dur + ld.get("gap", gap)
        need = (self.lines[-1].end + d.get("tail", 0.6)) if self.lines else 0
        self.dur = float(d.get("dur", max(need, 1.0)))
        self.start = start
        self.end = start + self.dur
        # cast -> character elements wired to the dialogue
        for cd in d.get("cast", []) or []:
            el = dict(cd, type="character")
            who = el.get("who", "person")
            mine = [ln for ln in self.lines if ln.who == who]
            el["_talk"] = (lambda ls: lambda tt: max([ln.talk(tt) for ln in ls] or [0.0]))(mine)
            el["_mood_at"] = self._mood_fn(who, el.get("mood", "neutral"))
            self.elements.insert(0, el)
        self.shakes = list(d.get("shake", []))
        self.punch = ([] if d.get("no_punch") else [0.0]) + list(d.get("punch", []))
        for e in self.elements:
            if e.get("type") == "stamp":
                self.shakes.append(e.get("at", 0) + 0.18)
                self.punch.append(e.get("at", 0))

    def _mood_fn(self, who, base):
        lines = self.lines

        def f(t):
            mood = base
            for ln in lines:
                if ln.start > t:
                    break
                if ln.who == who and ln.mood:
                    mood = ln.mood
                if who in ln.react:
                    mood = ln.react[who]
            return mood
        return f

    def line_at(self, t):
        for ln in self.lines:
            if ln.start <= t < ln.end + 0.15:
                return ln
        return None


class Timeline:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.base = os.path.dirname(self.path)
        with open(self.path, encoding="utf-8") as f:
            self.raw = yaml.safe_load(f) or {}
        meta = self.raw.get("meta", {}) or {}
        self.fps = int(meta.get("fps", 60))
        self.W, self.H = meta.get("size", [1080, 1920])
        self.title = meta.get("title", "reel")
        vo_path = os.path.join(self.base, (self.raw.get("audio", {}) or {}).get("voices", "vo.json"))
        self.vo = json.load(open(vo_path)) if os.path.exists(vo_path) else {"env": {}, "dur": {}}
        self.vo_dir = os.path.dirname(vo_path)
        if self.raw.get("style_drop"):          # one scene in N art styles -> generated card scenes
            from .art.drop import build_scenes
            self.raw["scenes"] = build_scenes(self.raw["style_drop"]) + list(self.raw.get("scenes") or [])
            self.raw.setdefault("meta", {}).setdefault("clean", True)
        self.scenes = []
        t = 0.0
        for sd in self.raw.get("scenes", []):
            s = Scene(sd, t, self.base, self.vo)
            self.scenes.append(s)
            t = s.end
        if not self.scenes:
            raise ValueError("scenes.yaml has no scenes")
        self.total = t
        bp = self.raw.get("brand")
        self.brand_path = os.path.join(self.base, bp) if bp else None

    def scene_at(self, t):
        for s in self.scenes:
            if s.start <= t < s.end:
                return s
        return self.scenes[-1]

    def events(self):
        """Sound-effect events: (time, kind, extra)."""
        ev = []
        for i, s in enumerate(self.scenes):
            if i > 0 and s.raw.get("whoosh", True):
                ev.append((s.start - 0.12, "whoosh", {}))
            for e in s.elements:
                kind = e.get("sfx", _DEFAULT_SFX.get(e.get("type")))
                at = s.start + e.get("at", 0)
                if e.get("type") == "terminal" and e.get("cps", 26):
                    n = sum(len(x) for x in e.get("lines", []))
                    ev.append((at + 0.25, "typing", {"n": min(n, 400), "cps": e.get("cps", 26)}))
                elif e.get("type") in ("checklist", "list"):
                    for k in range(len(e.get("items", []))):
                        ev.append((at + k * e.get("step", 0.6 if e["type"] == "checklist" else 1.0), "blip", {"f": 700 + k * 90}))
                elif e.get("type") == "split":
                    ev.append((at, "pop", {}))
                    ev.append((at + e.get("step", 1.2), "ding", {}))
                elif kind and kind != "none":
                    ev.append((at, kind, {}))
            for x in s.raw.get("sfx", []) or []:     # explicit: [{at: 1.2, kind: hit}]
                ev.append((s.start + x["at"], x.get("kind", "blip"), x))
        return sorted(ev, key=lambda e: e[0])

    def voice_clips(self):
        """(absolute start, wav path) for every dialogue line that has a recorded voice."""
        out = []
        for s in self.scenes:
            for ln in s.lines:
                if ln.voice:
                    p = os.path.join(self.vo_dir, f"vo_{ln.voice}.wav")
                    if os.path.exists(p):
                        out.append((s.start + ln.start, p))
        return out


_DEFAULT_SFX = {"headline": "whoosh_soft", "text": "blip", "bubble": "blip", "sticker": "pop",
                "pill": "blip", "stamp": "hit", "image": "pop", "character": None, "progress_ring": None,
                "stat": "ding", "quote": "whoosh_soft", "photo": "whoosh_soft", "emoji": "pop"}
