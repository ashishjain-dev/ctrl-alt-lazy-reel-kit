#!/usr/bin/env node
// Turn a scenes.yaml (same file the Pillow engine reads) into public/reel.json for Remotion.
//   node scripts/prep.mjs ../../examples/text-reel/scenes.yaml [--brand path] [--no-audio]
// Copies recorded voices (vo_<key>.wav + vo.json) into public/vo/ and, if Python + the Pillow
// engine are available, builds the music + SFX track into public/audio.wav with `reelkit audio`.
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import yaml from "js-yaml";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");
const PUB = path.join(ROOT, "public");
const WPS = 2.75, LINE_PAD = 0.35;

const args = process.argv.slice(2);
const scenesPath = args.find((a) => !a.startsWith("--"));
if (!scenesPath) {
  console.error("usage: node scripts/prep.mjs <scenes.yaml> [--brand brand.yaml] [--no-audio]");
  process.exit(1);
}
const opt = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : undefined; };
const abs = path.resolve(scenesPath);
const base = path.dirname(abs);
const doc = yaml.load(fs.readFileSync(abs, "utf8")) || {};
const meta = doc.meta || {};
const fps = meta.fps || 60;

// ---- brand: neutral defaults, then brand.yaml ----
const DEFAULT_BRAND = {
  handle: "@your.handle", label: "SHORTS",
  colors: { bg_top: "#1a1622", bg_bottom: "#0c0e16", fg: "#f6f6fa", muted: "#a0a0af", accent: "#e8805c",
    highlight: "#fcce4a", good: "#7ad696", bad: "#f06056", panel: "#22222e", ink: "#121216", info: "#82aaf0" },
  frame: { progress_bar: true, watermark: true, accent_bar: true, safe_top: 280, safe_bottom: 1440, safe_right: 850 },
  web_fonts: { display: "Inter, 'DejaVu Sans', 'Noto Color Emoji', sans-serif", mono: "'JetBrains Mono', 'DejaVu Sans Mono', monospace" },
  characters: {},
};
const merge = (a, b) => {
  const o = { ...a };
  for (const [k, v] of Object.entries(b || {})) o[k] = v && typeof v === "object" && !Array.isArray(v) && typeof a[k] === "object" ? merge(a[k], v) : v;
  return o;
};
const brandPath = opt("--brand") || (doc.brand ? path.resolve(base, doc.brand) : null);
const brand = merge(DEFAULT_BRAND, brandPath && fs.existsSync(brandPath) ? yaml.load(fs.readFileSync(brandPath, "utf8")) : {});

brand.characters = { ...(brand.characters || {}), ...(doc.characters || {}) };

// ---- characters: resolve presets / named characters to {base, look} (mirrors characters.py) ----
const BUILTIN = ["person", "bot", "blob"];
const PRESETS = { dev: { base: "person", headphones: true, shirt_icon: "</>" } };
const resolveChar = (who) => {
  let name = who, spec = {}, n = 0;
  while (!BUILTIN.includes(name)) {
    const nxt = { ...(PRESETS[name] || {}), ...(brand.characters[name] || {}) };
    if (!Object.keys(nxt).length || n++ > 5) throw new Error(`unknown character '${who}' (built-in: ${BUILTIN.join(", ")}, dev, or brand.yaml > characters)`);
    spec = { ...nxt, ...spec };
    name = nxt.base || "person";
  }
  if (BUILTIN.includes(who) && brand.characters[who]) spec = { ...brand.characters[who], ...spec };
  delete spec.base;
  if (typeof spec.hair === "string" && spec.hair.startsWith("#")) { spec.hair_color = spec.hair; delete spec.hair; }
  if (spec.phones) { spec.accent = spec.phones; delete spec.phones; }
  return { base: name, look: spec };
};
const withChar = (e) => { const r = resolveChar(e.who || "person"); return { ...e, _base: r.base, _look: { ...r.look, ...(e.look || {}) } }; };

// ---- voices ----
const audioCfg = doc.audio || {};
const voPath = path.resolve(base, audioCfg.voices || "vo.json");
const vo = fs.existsSync(voPath) ? JSON.parse(fs.readFileSync(voPath, "utf8")) : { env: {}, dur: {} };
fs.mkdirSync(path.join(PUB, "vo"), { recursive: true });

// ---- timing (mirrors engines/pillow/reelkit/timeline.py) ----
let t = 0;
const scenes = (doc.scenes || []).map((s) => {
  const lines = [];
  let lt = s.dialogue_at ?? 0.4;
  const gap = s.gap ?? LINE_PAD;
  for (const d of s.dialogue || []) {
    const hasVoice = d.voice && vo.dur[d.voice] !== undefined;
    const dur = hasVoice ? vo.dur[d.voice] : Math.max(0.9, String(d.text || "").split(/\s+/).length / WPS + 0.25);
    lt = d.at ?? lt;
    let audio = null;
    if (hasVoice) {
      const src = path.join(path.dirname(voPath), `vo_${d.voice}.wav`);
      if (fs.existsSync(src)) { fs.copyFileSync(src, path.join(PUB, "vo", `vo_${d.voice}.wav`)); audio = `vo/vo_${d.voice}.wav`; }
    }
    lines.push({ who: "narrator", ...d, start: lt, dur, env: hasVoice ? vo.env[d.voice] : null, audio });
    lt += dur + (d.gap ?? gap);
  }
  const need = lines.length ? lines[lines.length - 1].start + lines[lines.length - 1].dur + (s.tail ?? 0.6) : 0;
  const dur = s.dur ?? Math.max(need, 1.0);
  const out = { ...s, start: t, dur, lines, cast: (s.cast || []).map(withChar),
    elements: (s.elements || []).map((e) => (e.type === "character" ? withChar(e) : e)) };
  t += dur;
  // images: copy next to public/
  for (const e of out.elements || []) {
    if ((e.type === "image" || e.type === "photo") && e.src && !/^https?:/.test(e.src)) {
      const src = path.resolve(base, e.src);
      const name = `img_${path.basename(src)}`;
      fs.copyFileSync(src, path.join(PUB, name));
      e.src = name;
    }
  }
  return out;
});

// ---- music + sfx via the Pillow engine (optional) ----
let audioFile = null;
if (!args.includes("--no-audio")) {
  const py = process.env.PYTHON || (process.platform === "win32" ? "python" : "python3");
  try {
    execFileSync(py, ["-m", "reelkit", "audio", abs, "-o", path.join(PUB, "audio.wav"), ...(brandPath ? ["--brand", brandPath] : [])],
      { cwd: path.resolve(ROOT, "..", "pillow"), stdio: "inherit" });
    audioFile = "audio.wav";
  } catch {
    console.warn("! music/SFX skipped (needs Python + `pip install -r requirements.txt`). Voices still play.");
  }
}

const reel = { title: meta.title || "reel", fps, width: (meta.size || [1080, 1920])[0], height: (meta.size || [1080, 1920])[1],
  total: t, brand, scenes, cover: doc.cover && doc.cover.character ? { ...doc.cover, character: withChar(doc.cover.character) } : (doc.cover || null), audio: audioFile, voicesInMix: !!audioFile };
fs.writeFileSync(path.join(PUB, "reel.json"), JSON.stringify(reel, null, 1));
console.log(`public/reel.json: ${scenes.length} scenes, ${t.toFixed(2)} s @ ${fps} fps`);
