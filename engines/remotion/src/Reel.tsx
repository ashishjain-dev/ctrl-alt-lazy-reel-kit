import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Character3D } from "./Character3D";
import { Rich, TYPES, col } from "./elements";
import type { Brand, Line, Reel, Scene } from "./types";

const talkAt = (lines: Line[], who: string, t: number) => {
  for (const ln of lines) {
    if (ln.who !== who || t < ln.start || t >= ln.start + ln.dur) continue;
    if (ln.env) return Math.min(1, (ln.env[Math.min(Math.floor((t - ln.start) * 60), ln.env.length - 1)] ?? 0) * 1.4);
    const u = t - ln.start;
    return 0.35 + 0.35 * Math.abs(Math.sin(u * 11)) * (0.6 + 0.4 * Math.sin(u * 3.1));
  }
  return 0;
};

const moodAt = (lines: Line[], who: string, base: string, t: number) => {
  let m = base;
  for (const ln of lines) {
    if (ln.start > t) break;
    if (ln.who === who && ln.mood) m = ln.mood;
    if (ln.react && ln.react[who]) m = ln.react[who];
  }
  return m;
};

export const Frame: React.FC<{ b: Brand; t: number; total: number }> = ({ b, t, total }) => {
  const top = b.frame.safe_top;
  return (
    <>
      {b.frame.accent_bar ? <div style={{ position: "absolute", left: 0, top: 0, right: 0, height: 10, background: b.colors.accent }} /> : null}
      {b.label ? (
        <div style={{ position: "absolute", left: 60, top: top - 64, height: 42, padding: "0 20px", borderRadius: 21, background: b.colors.panel,
          color: b.colors.accent, font: `700 28px ${b.web_fonts.display}`, display: "flex", alignItems: "center" }}>{b.label}</div>
      ) : null}
      {b.frame.watermark && b.handle ? (
        <div style={{ position: "absolute", right: 60, top: top - 64, height: 42, display: "flex", alignItems: "center",
          color: b.colors.muted, font: `700 32px ${b.web_fonts.display}` }}>{b.handle}</div>
      ) : null}
      {b.frame.progress_bar ? (
        <div style={{ position: "absolute", left: 60, right: 60, top: top - 6, height: 12, borderRadius: 6, background: "#32323e" }}>
          <div style={{ width: `${Math.min(1, t / total) * 100}%`, height: "100%", borderRadius: 6, background: b.colors.accent }} />
        </div>
      ) : null}
    </>
  );
};

const SceneView: React.FC<{ s: Scene; b: Brand; t: number }> = ({ s, b, t }) => {
  const line = s.lines.find((ln) => t >= ln.start && t < ln.start + ln.dur + 0.15);
  // camera: punch-in on scene start + marked beats, shake on stamps / `shake:` times
  const punches = [0, ...(s.punch ?? []), ...(s.elements ?? []).filter((e) => e.type === "stamp").map((e) => e.at ?? 0)];
  const shakes = [...(s.shake ?? []), ...(s.elements ?? []).filter((e) => e.type === "stamp").map((e) => (e.at ?? 0) + 0.18)];
  let z = 1, sx = 0, sy = 0;
  for (const p of punches) if (t >= p) z = Math.max(z, 1 + 0.05 * Math.exp(-(t - p) * 7));
  for (const k of shakes) {
    const d = t - k;
    if (d >= 0 && d < 0.35) { const e = Math.exp(-d * 14); sx += 18 * e * Math.sin(d * 95); sy += 12 * e * Math.cos(d * 80); }
  }
  const glow = s.glow ? col(b, s.glow) : null;
  const [gx, gy] = s.glow_at ?? [540, 900];
  return (
    <AbsoluteFill style={{ transform: `translate(${sx}px, ${sy}px) scale(${z})` }}>
      {glow ? <div style={{ position: "absolute", left: gx - 520, top: gy - 520, width: 1040, height: 1040, borderRadius: "50%",
        background: `radial-gradient(circle, ${glow}55 0%, ${glow}00 70%)` }} /> : null}
      {(s.cast ?? []).map((c, i) => (
        <Character3D key={`c${i}`} who={c.who ?? "dev"} x={c.x ?? 540} y={c.y ?? 1420} scale={c.scale ?? 1}
          mood={moodAt(s.lines, c.who ?? "dev", c.mood ?? "neutral", t)} t={t} talk={talkAt(s.lines, c.who ?? "dev", t)}
          colors={b.characters?.[c.who ?? "dev"]} />
      ))}
      {(s.elements ?? []).map((el, i) => {
        if (el.until !== undefined && t >= el.until) return null;
        if (el.type === "character") {
          if (t < (el.at ?? 0)) return null;
          return <Character3D key={i} who={el.who ?? "dev"} x={el.x ?? 540} y={el.y ?? 1420} scale={el.scale ?? 1}
            mood={el.mood ?? "neutral"} t={t} talk={0} colors={b.characters?.[el.who ?? "dev"]} />;
        }
        const C = TYPES[el.type];
        return C ? <C key={i} el={el} t={t} b={b} /> : null;
      })}
      {line && line.subtitle !== false && line.text ? (
        <div style={{ position: "absolute", left: 110, right: 110, top: b.frame.safe_bottom - 40, transform: "translateY(-100%)", textAlign: "center" }}>
          <span style={{ background: "#000", color: b.colors.fg, padding: "14px 28px", borderRadius: 22, lineHeight: 1.6,
            font: `700 50px/1.6 ${b.web_fonts.display}`, boxDecorationBreak: "clone", WebkitBoxDecorationBreak: "clone" }}>
            <Rich text={line.text} b={b} />
          </span>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

export const ReelVideo: React.FC<{ reel: Reel }> = ({ reel }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const b = reel.brand;
  const s = reel.scenes.find((x) => t >= x.start && t < x.start + x.dur) ?? reel.scenes[reel.scenes.length - 1];
  const fade = Math.min(1, t / 0.08, Math.max(0, (reel.total - t) / 0.25));
  return (
    <AbsoluteFill style={{ background: `linear-gradient(${b.colors.bg_top}, ${b.colors.bg_bottom})`, overflow: "hidden" }}>
      <SceneView s={s} b={b} t={t - s.start} />
      <Frame b={b} t={t} total={reel.total} />
      <AbsoluteFill style={{ background: b.colors.bg_bottom, opacity: 1 - fade }} />
      {reel.audio ? <Audio src={staticFile(reel.audio)} /> : null}
      {!reel.voicesInMix
        ? reel.scenes.flatMap((sc) => sc.lines.filter((ln) => ln.audio).map((ln, i) => (
            <Sequence key={`${sc.name}${i}`} from={Math.round((sc.start + ln.start) * fps)}>
              <Audio src={staticFile(ln.audio as string)} />
            </Sequence>
          )))
        : null}
    </AbsoluteFill>
  );
};
