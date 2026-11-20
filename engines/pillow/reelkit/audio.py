"""Original music + sound effects, generated with numpy (no samples, no licensing questions).

Music moods: chill (Am-F-C-G lo-fi), upbeat (C-G-Am-F, brighter), tense (minor pulse), none.
SFX kinds: whoosh, whoosh_soft, blip, pop, hit, typing, ding, none.
Voice clips (vo_<key>.wav) are placed on the dialogue timeline and the music ducks under them.
"""
import wave

import numpy as np

SR = 48000

MOODS = {
    "chill": {"bpm": 92, "chords": [[57, 60, 64], [53, 57, 60], [48, 52, 55, 60], [55, 59, 62]],
              "bass": [45, 41, 36, 43], "mel": [76, 72, 74, 71]},
    "upbeat": {"bpm": 112, "chords": [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]],
               "bass": [48, 43, 45, 41], "mel": [79, 74, 76, 72]},
    "tense": {"bpm": 100, "chords": [[57, 60, 64], [57, 60, 65], [56, 59, 64], [57, 60, 64]],
              "bass": [45, 45, 44, 45], "mel": [69, 70, 68, 69]},
}


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


class Mixer:
    def __init__(self, dur, seed=7):
        self.n = int(SR * dur) + SR
        self.dur = dur
        self.mus = np.zeros(self.n)
        self.sfx = np.zeros(self.n)
        self.vo = np.zeros(self.n)
        self.rng = np.random.default_rng(seed)

    def add(self, buf, sig, t, g=1.0):
        i = int(max(0, t) * SR)
        j = min(self.n, i + len(sig))
        if i < self.n:
            buf[i:j] += g * sig[:j - i]

    # ---------- instruments ----------
    def _env(self, n, a=0.005, r=None):
        e = np.ones(n)
        ai = max(1, int(a * SR))
        e[:ai] = np.linspace(0, 1, ai)
        if r:
            e *= np.exp(-np.arange(n) / (r * SR))
        return e

    def kick(self):
        n = int(0.35 * SR); tt = np.arange(n) / SR
        f = 50 + 90 * np.exp(-tt * 30)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)

    def snare(self):
        n = int(0.25 * SR); tt = np.arange(n) / SR
        return (self.rng.standard_normal(n) * 0.7 + 0.4 * np.sin(2 * np.pi * 190 * tt)) * np.exp(-tt * 18)

    def hat(self):
        n = int(0.06 * SR)
        x = np.diff(self.rng.standard_normal(n), prepend=0)
        return x * np.exp(-np.arange(n) / SR * 70) * 0.5

    def note(self, f, dur, kind="pad"):
        n = int(dur * SR); tt = np.arange(n) / SR
        if kind == "pad":
            x = sum(np.sin(2 * np.pi * f * k * tt + 0.3 * np.sin(2 * np.pi * 0.3 * tt)) / k ** 1.6 for k in (1, 2, 3))
            e = np.minimum(1, tt / 0.25) * np.minimum(1, np.maximum(0, dur - tt) / 0.4)
        else:
            x = np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)
            e = self._env(n, 0.004, 0.35 if kind == "bass" else 0.18)
        return x * e

    def music(self, mood="chill", bpm=None, volume=0.55, drums_from=0.0):
        if mood in (None, "none"):
            return
        m = MOODS.get(mood, MOODS["chill"])
        beat = 60 / (bpm or m["bpm"])
        bar = 4 * beat
        t, b = 0.0, 0
        while t < self.dur:
            ci = b % 4
            for note in m["chords"][ci]:
                self.add(self.mus, self.note(hz(note), bar), t, 0.055)
            self.add(self.mus, self.note(hz(m["bass"][ci]), beat * 1.5, "bass"), t, 0.22)
            self.add(self.mus, self.note(hz(m["bass"][ci]), beat * 1.5, "bass"), t + 2 * beat, 0.18)
            if b >= 1:
                self.add(self.mus, self.note(hz(m["mel"][ci]), 0.4, "pluck"), t + beat * 1.5, 0.06)
                self.add(self.mus, self.note(hz(m["mel"][ci] - 3), 0.4, "pluck"), t + beat * 3, 0.05)
            for k in range(4):
                bt = t + k * beat
                if bt < drums_from:
                    continue
                if k in (0, 2) or (k == 3 and b % 2):
                    self.add(self.mus, self.kick(), bt + (beat / 2 if k == 3 else 0), 0.55)
                if k in (1, 3):
                    self.add(self.mus, self.snare(), bt, 0.18)
                self.add(self.mus, self.hat(), bt, 0.12)
                self.add(self.mus, self.hat(), bt + beat / 2, 0.07)
            t += bar
            b += 1
        end = int(self.dur * SR)
        fo = int(1.2 * SR)
        self.mus[end - fo:end] *= np.linspace(1, 0, fo)
        self.mus[end:] = 0
        self.mus *= volume / (np.max(np.abs(self.mus)) + 1e-9)

    # ---------- sfx ----------
    def click(self):
        n = int(0.03 * SR); tt = np.arange(n) / SR
        return (self.rng.standard_normal(n) * np.exp(-tt * 260)
                + 0.4 * np.sin(2 * np.pi * (1800 + self.rng.uniform(-300, 300)) * tt) * np.exp(-tt * 400))

    def blip(self, f=880):
        n = int(0.09 * SR); tt = np.arange(n) / SR
        return np.sin(2 * np.pi * f * tt) * np.exp(-tt * 35)

    def pop(self):
        n = int(0.12 * SR); tt = np.arange(n) / SR
        f = 400 + 900 * np.exp(-tt * 40)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 30)

    def ding(self):
        n = int(0.8 * SR); tt = np.arange(n) / SR
        return (np.sin(2 * np.pi * 1318 * tt) + 0.5 * np.sin(2 * np.pi * 1975 * tt)) * np.exp(-tt * 5)

    def whoosh(self, length=0.35):
        n = int(length * SR)
        x = self.rng.standard_normal(n)
        # low-pass whose cutoff rises: one-pole filter with a moving coefficient
        a = np.linspace(0.03, 0.25, n)
        out = np.zeros(n); acc = 0.0
        for i in range(n):
            acc += a[i] * (x[i] - acc)
            out[i] = acc
        return out * np.sin(np.pi * np.arange(n) / n) * 3.5

    def hit(self):
        n = int(0.5 * SR); tt = np.arange(n) / SR
        return (np.sin(2 * np.pi * (60 + 120 * np.exp(-tt * 25)) * tt)
                + self.rng.standard_normal(n) * 0.3 * np.exp(-tt * 20)) * np.exp(-tt * 6)

    def event(self, t, kind, extra):
        g = extra.get("gain")
        if kind == "whoosh":
            self.add(self.sfx, self.whoosh(), t, g or 0.35)
        elif kind == "whoosh_soft":
            self.add(self.sfx, self.whoosh(0.25), t, g or 0.18)
        elif kind == "blip":
            self.add(self.sfx, self.blip(extra.get("f", 880)), t, g or 0.22)
        elif kind == "pop":
            self.add(self.sfx, self.pop(), t, g or 0.3)
        elif kind == "ding":
            self.add(self.sfx, self.ding(), t, g or 0.25)
        elif kind == "hit":
            self.add(self.sfx, self.hit(), t, g or 0.55)
        elif kind == "typing":
            cps = extra.get("cps", 26)
            for i in range(0, extra.get("n", 20), 2):      # every second char keeps it from buzzing
                self.add(self.sfx, self.click(), t + i / cps + self.rng.uniform(-0.01, 0.01), self.rng.uniform(0.16, 0.26))

    def voice(self, t, path):
        x = read_wav(path)
        self.add(self.vo, x, t, 1.0)

    def mixdown(self, duck=0.35):
        vo_env = np.convolve(np.abs(self.vo), np.ones(SR // 20) / (SR // 20), mode="same")
        vo_env = np.clip(vo_env * 12, 0, 1)
        mus = self.mus * (1 - (1 - duck) * vo_env)
        mix = mus + self.sfx * 0.9 + self.vo * 1.1
        mix = np.tanh(mix * 1.1) * 0.9
        mix /= max(1.0, np.max(np.abs(mix)) / 0.95)
        return mix[:int(self.dur * SR)]


def read_wav(path):
    with wave.open(path, "rb") as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype={2: np.int16, 4: np.int32}[sw]).astype(np.float64)
    x /= float(2 ** (8 * sw - 1))
    if ch > 1:
        x = x.reshape(-1, ch).mean(1)
    if sr != SR:   # linear resample is fine for speech clips
        x = np.interp(np.arange(0, len(x) * SR / sr) * sr / SR, np.arange(len(x)), x)
    return x


def write_wav(path, x, sr=SR, stereo=True):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    if stereo:
        pcm = np.stack([pcm, pcm], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2 if stereo else 1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def build(tl, out_wav, brand):
    a = tl.raw.get("audio", {}) or {}
    m = Mixer(tl.total)
    mus = dict(brand.music)
    mus.update(a.get("music", {}) or {})
    m.music(mus.get("mood", "chill"), mus.get("bpm"), mus.get("volume", 0.55), mus.get("drums_from", 0.0))
    if a.get("sfx", True):
        for t, kind, extra in tl.events():
            m.event(t, kind, extra)
    for t, p in tl.voice_clips():
        m.voice(t, p)
    write_wav(out_wav, m.mixdown(a.get("duck", 0.35)))
    return out_wav
