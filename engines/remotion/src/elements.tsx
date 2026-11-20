import React from "react";
import { Img, continueRender, delayRender, interpolate, spring, staticFile, useVideoConfig } from "remotion";
import type { Brand, El } from "./types";

export const col = (b: Brand, v: string | undefined, d = "fg") => {
  const k = v ?? d;
  return b.colors[k] ?? k;
};

/** 0 before `at`, springs to 1 (with overshoot) after. */
export const usePop = (t: number, at = 0) => {
  const { fps } = useVideoConfig();
  if (t < at) return null;
  return spring({ frame: Math.round((t - at) * fps), fps, config: { damping: 11, stiffness: 160, mass: 0.6 } });
};

const EMOJI = /\p{Extended_Pictographic}/u;

/** Hold the frame until the colour emoji glyphs in `text` are ready. Uses the system emoji font
 *  (macOS/Windows have one; Linux: apt install fonts-noto-color-emoji). */
export const useEmojiFont = (text: string) => {
  const has = EMOJI.test(text);
  const [handle] = React.useState(() => (has ? delayRender("emoji font") : null));
  React.useEffect(() => {
    if (handle === null) return;
    document.fonts.load("100px 'Noto Color Emoji'", text).then(() => continueRender(handle), () => continueRender(handle));
  }, [handle, text]);
};

/** "*word*" -> highlighted spans. */
export const Rich: React.FC<{ text: string; b: Brand }> = ({ text, b }) => {
  useEmojiFont(String(text));
  return <RichInner text={text} b={b} />;
};

const RichInner: React.FC<{ text: string; b: Brand }> = ({ text, b }) => (
  <>
    {String(text).split("*").map((p, i) =>
      i % 2 ? (
        <span key={i} style={{ background: b.colors.highlight, color: b.colors.ink, borderRadius: "0.18em",
          padding: "0 0.14em", boxDecorationBreak: "clone", WebkitBoxDecorationBreak: "clone" }}>{p}</span>
      ) : (
        <React.Fragment key={i}>{p}</React.Fragment>
      ),
    )}
  </>
);

const abs = (x: number, y: number, extra: React.CSSProperties = {}): React.CSSProperties => ({
  position: "absolute", left: x, top: y, ...extra,
});

export const Headline: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const u = usePop(t, el.at ?? 0);
  if (u === null) return null;
  const w = el.w ?? 920;
  return (
    <div style={abs((el.x ?? 540) - w / 2, el.y ?? 430, { width: w, transform: `translateY(calc(-50% + ${(1 - u) * 60}px))`,
      textAlign: "center", font: `900 ${el.size ?? 78}px/1.28 ${b.web_fonts.display}`, color: col(b, el.color) })}>
      <Rich text={el.text} b={b} />
    </div>
  );
};

export const Text: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const u = usePop(t, el.at ?? 0);
  if (u === null) return null;
  const w = el.w ?? 940;
  return (
    <div style={abs((el.x ?? 540) - w / 2, (el.y ?? 800) + (1 - u) * 50, { width: w, textAlign: "center",
      font: `700 ${el.size ?? 54}px/1.3 ${b.web_fonts.display}`, color: col(b, el.color), transform: "translateY(-50%)" })}>
      <Rich text={el.text} b={b} />
    </div>
  );
};

const lineColor = (b: Brand, ln: string) => {
  const p = ln.slice(0, 2);
  if (p === "$ " || p === "+ ") return b.colors.good;
  if (p === "! " || p === "- ") return b.colors.bad;
  if (p === "# ") return b.colors.muted;
  return b.colors.fg;
};

export const Terminal: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const u = usePop(t, el.at ?? 0);
  if (u === null) return null;
  const lines: string[] = el.lines ?? [];
  const cps = el.cps ?? 26;
  const pause = el.line_pause ?? 6;
  const tt = cps ? (t - (el.at ?? 0) - 0.25) * cps : 1e9;
  let used = 0;
  const shown: string[] = [];
  for (const ln of lines) {
    if (tt < used) break;
    shown.push(tt - used < ln.length ? ln.slice(0, Math.floor(tt - used)) : ln);
    used += ln.length + pause;
    if (shown[shown.length - 1] !== ln) break;
  }
  const size = el.size ?? 38;
  const blink = Math.floor(t * 2.5) % 2 === 0;
  return (
    <div style={abs(el.x ?? 70, (el.y ?? 620) + (1 - u) * 60, { width: el.w ?? 940, minHeight: 110 + size * 1.45 * Math.max(lines.length, 1),
      background: "#0c0c10", border: "3px solid #3c3c4c", borderRadius: 26, boxShadow: "0 18px 40px rgba(0,0,0,.55)", boxSizing: "border-box" })}>
      <div style={{ display: "flex", gap: 14, padding: "22px 30px", alignItems: "center" }}>
        {["#f06056", "#fcce4a", "#7ad696"].map((c) => <div key={c} style={{ width: 22, height: 22, borderRadius: 11, background: c }} />)}
        <div style={{ flex: 1, textAlign: "center", font: `700 26px ${b.web_fonts.mono}`, color: b.colors.muted, marginRight: 80 }}>{el.title ?? ""}</div>
      </div>
      <div style={{ padding: "4px 36px 30px", font: `700 ${size}px/1.45 ${b.web_fonts.mono}`, whiteSpace: "pre" }}>
        {shown.map((s, i) => (
          <div key={i} style={{ color: lineColor(b, lines[i]), minHeight: size * 1.45 }}>
            {s}
            {i === shown.length - 1 && blink ? <span style={{ background: b.colors.fg, display: "inline-block", width: size * 0.5, height: size * 0.9, verticalAlign: "middle", marginLeft: 4 }} /> : null}
          </div>
        ))}
      </div>
    </div>
  );
};

export const Bubble: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const u = usePop(t, el.at ?? 0);
  if (u === null) return null;
  const accent = col(b, el.color, "accent");
  return (
    <div style={abs(el.x ?? 80, (el.y ?? 700) + (1 - u) * 40, { width: el.w ?? 760, background: b.colors.panel, border: `4px solid ${accent}`,
      borderRadius: 34, padding: "30px 36px", boxSizing: "border-box", font: `700 ${el.size ?? 46}px/1.28 ${b.web_fonts.display}`, color: b.colors.fg })}>
      {el.who ? <div style={{ color: accent, fontSize: (el.size ?? 46) * 0.66, marginBottom: 6 }}>{el.who}</div> : null}
      <Rich text={el.text} b={b} />
    </div>
  );
};

export const Sticker: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const u = usePop(t, el.at ?? 0);
  if (u === null) return null;
  return (
    <div style={abs(el.x ?? 540, el.y ?? 1100, { transform: `translate(-50%,-50%) rotate(${-(el.angle ?? -6)}deg) scale(${u})`,
      background: col(b, el.color, "highlight"), color: col(b, el.text_color, "ink"), padding: "16px 28px", borderRadius: 14,
      boxShadow: "8px 8px 0 rgba(0,0,0,.6)", font: `900 ${el.size ?? 42}px/1.22 ${b.web_fonts.display}`, whiteSpace: "pre" })}>
      {el.text}
    </div>
  );
};

export const Pill: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const u = usePop(t, el.at ?? 0);
  if (u === null) return null;
  return (
    <div style={abs(el.x ?? 540, (el.y ?? 900) + (1 - u) * 40, { transform: "translate(-50%,-50%)", background: col(b, el.color, "accent"),
      color: col(b, el.text_color, "ink"), padding: "0.35em 0.8em", borderRadius: 999, font: `700 ${el.size ?? 44}px ${b.web_fonts.display}`, whiteSpace: "nowrap" })}>
      {el.text}
    </div>
  );
};

export const Checklist: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const step = el.step ?? 0.6, size = el.size ?? 48;
  return (
    <>
      {(el.items ?? []).map((it: string, i: number) => {
        const u = usePop(t, (el.at ?? 0) + i * step);
        if (u === null) return null;
        return (
          <div key={i} style={abs((el.x ?? 110) - (1 - u) * 80, (el.y ?? 700) + i * size * 1.9, { display: "flex", alignItems: "center", gap: size * 0.4,
            transform: "translateY(-50%)", font: `700 ${size}px ${b.web_fonts.display}`, color: b.colors.fg })}>
            <span style={{ background: col(b, el.color, "good"), color: b.colors.ink, borderRadius: 14, width: size * 1.1, textAlign: "center" }}>{el.mark ?? "✓"}</span>
            <span><Rich text={it} b={b} /></span>
          </div>
        );
      })}
    </>
  );
};

export const Stamp: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const at = el.at ?? 0;
  if (t < at) return null;
  const u = interpolate(t - at, [0, 0.22], [0, 1], { extrapolateRight: "clamp" });
  const c = col(b, el.color, "bad");
  return (
    <div style={abs(el.x ?? 540, el.y ?? 900, { transform: `translate(-50%,-50%) rotate(${-(el.angle ?? 12)}deg) scale(${2.2 - 1.2 * u})`, opacity: u,
      border: `12px solid ${c}`, color: c, borderRadius: 20, padding: "0.1em 0.35em", font: `900 ${el.size ?? 120}px ${b.web_fonts.display}`, whiteSpace: "nowrap" })}>
      {el.text ?? "NOPE"}
    </div>
  );
};

export const Image: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t }) => {
  const u = usePop(t, el.at ?? 0);
  if (u === null) return null;
  const src = /^https?:/.test(el.src) ? el.src : staticFile(el.src);
  return <Img src={src} style={abs(el.x ?? 540, (el.y ?? 900) + (1 - u) * 50, { width: el.w ?? 600, transform: "translate(-50%,-50%)" })} />;
};

export const ProgressRing: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const at = el.at ?? 0;
  if (t < at) return null;
  const u = Math.min(1, (t - at) / (el.dur ?? 2));
  const r = el.r ?? 120, C = 2 * Math.PI * r;
  return (
    <svg style={abs((el.x ?? 540) - r - 20, (el.y ?? 900) - r - 20)} width={2 * r + 40} height={2 * r + 40}>
      <circle cx={r + 20} cy={r + 20} r={r} stroke={b.colors.panel} strokeWidth={26} fill="none" />
      <circle cx={r + 20} cy={r + 20} r={r} stroke={col(b, el.color, "accent")} strokeWidth={26} fill="none"
        strokeDasharray={`${C * u} ${C}`} transform={`rotate(-90 ${r + 20} ${r + 20})`} strokeLinecap="round" />
      <text x={r + 20} y={r + 20} textAnchor="middle" dominantBaseline="central" fill={b.colors.fg}
        style={{ font: `900 ${r * 0.5}px ${b.web_fonts.display}` }}>{el.text ?? `${Math.round(u * 100)}%`}</text>
    </svg>
  );
};

export const Stat: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const u = usePop(t, el.at ?? 0);
  if (u === null) return null;
  const val = String(el.value ?? "100%");
  const m = val.match(/\d[\d,]*\.?\d*/);
  let shown = val;
  if (m && el.count_up !== false) {
    const num = parseFloat(m[0].replace(/,/g, ""));
    const k = interpolate(t - (el.at ?? 0), [0, el.count_dur ?? 0.9], [0, 1], { extrapolateRight: "clamp" });
    const e = k * k * (3 - 2 * k);
    const dec = m[0].includes(".") ? m[0].split(".")[1].length : 0;
    const cur = (num * e).toFixed(dec);
    const txt = m[0].includes(",") ? Number(cur).toLocaleString("en-US", { minimumFractionDigits: dec, maximumFractionDigits: dec }) : cur;
    shown = val.slice(0, m.index) + txt + val.slice((m.index ?? 0) + m[0].length);
  }
  const size = el.size ?? 220;
  return (
    <div style={abs(0, (el.y ?? 860) - size * 0.6 + (1 - u) * 60, { width: 1080, textAlign: "center" })}>
      <div style={{ font: `900 ${size}px/1.2 ${b.web_fonts.display}`, color: col(b, el.color, "accent") }}>{shown}</div>
      {el.label ? <div style={{ font: `700 ${el.label_size ?? 50}px/1.3 ${b.web_fonts.display}`, color: b.colors.fg, padding: "0 90px" }}><Rich text={el.label} b={b} /></div> : null}
    </div>
  );
};

export const Quote: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const u = usePop(t, el.at ?? 0);
  if (u === null) return null;
  const accent = col(b, el.color, "accent");
  const size = el.size ?? 56;
  return (
    <div style={abs(el.x ?? 90, (el.y ?? 640) + (1 - u) * 50, { width: el.w ?? 900, boxSizing: "border-box", background: b.colors.panel,
      borderLeft: `14px solid ${accent}`, borderRadius: 30, padding: "30px 56px 40px", boxShadow: "0 18px 40px rgba(0,0,0,.5)" })}>
      <div style={{ font: `900 ${size * 2.4}px/0.8 ${b.web_fonts.display}`, color: accent, height: size * 1.1 }}>{"\u201c"}</div>
      <div style={{ font: `700 ${size}px/1.3 ${b.web_fonts.display}`, color: b.colors.fg }}><Rich text={el.text} b={b} /></div>
      {el.author ? <div style={{ font: `700 ${size * 0.62}px ${b.web_fonts.display}`, color: b.colors.muted, marginTop: 20 }}>{"\u2014 " + el.author}</div> : null}
    </div>
  );
};

export const Split: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const t0 = el.at ?? 0, step = el.step ?? 1.2;
  const sides = [
    { x: 70, side: el.left ?? {}, d: "bad", mark: "\u00d7", title: "BEFORE", u: usePop(t, t0) },
    { x: 555, side: el.right ?? {}, d: "good", mark: "\u2713", title: "AFTER", u: usePop(t, t0 + step) },
  ];
  const y = el.y ?? 640, h = el.h ?? 480, size = el.size ?? 46;
  const vs = usePop(t, t0 + step);
  return (
    <>
      {sides.map(({ x, side, d, mark, title, u }, i) => {
        if (u === null) return null;
        const cc = col(b, side.color, d);
        return (
          <div key={i} style={abs(x, y + (1 - u) * 60, { width: 455, height: h, boxSizing: "border-box", background: b.colors.panel,
            border: `5px solid ${cc}`, borderRadius: 30, overflow: "hidden" })}>
            <div style={{ background: cc, color: b.colors.ink, textAlign: "center", font: `900 46px/96px ${b.web_fonts.display}` }}>{side.title ?? title}</div>
            <div style={{ padding: "26px 28px", font: `700 ${size}px/1.3 ${b.web_fonts.display}`, color: b.colors.fg }}>
              {side.text ? <div><Rich text={side.text} b={b} /></div> : null}
              {(side.items ?? []).map((it: string, j: number) => (
                <div key={j} style={{ display: "flex", gap: 14, fontSize: size * 0.9, marginTop: 10 }}><span style={{ color: cc }}>{mark}</span><span><Rich text={it} b={b} /></span></div>
              ))}
            </div>
          </div>
        );
      })}
      {el.vs !== false && vs !== null ? (
        <div style={abs(488, y + h / 2 - 52, { width: 104, height: 104, borderRadius: 52, background: b.colors.highlight, color: b.colors.ink,
          display: "flex", alignItems: "center", justifyContent: "center", font: `900 40px ${b.web_fonts.display}` })}>{el.vs_text ?? "VS"}</div>
      ) : null}
    </>
  );
};

export const Photo: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const u = usePop(t, el.at ?? 0);
  if (u === null) return null;
  const w = el.w ?? 940, h = el.h ?? 700;
  const [z0, z1] = el.zoom ?? [1.0, 1.15];
  const z = interpolate(t - (el.at ?? 0), [0, el.dur ?? 5], [z0, z1], { extrapolateRight: "clamp" });
  const [px, py] = el.pan ?? [0.5, 0.5];
  const src = /^https?:/.test(el.src) ? el.src : staticFile(el.src);
  return (
    <div style={abs((el.x ?? 540) - w / 2, (el.y ?? 860) - h / 2 + (1 - u) * 50, { width: w, height: h, borderRadius: el.radius ?? 30, overflow: "hidden",
      boxShadow: "0 18px 40px rgba(0,0,0,.55)" })}>
      <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: `${px * 100}% ${py * 100}%`,
        transform: `scale(${z})`, transformOrigin: `${px * 100}% ${py * 100}%` }} />
      {el.caption ? <div style={{ position: "absolute", left: "50%", bottom: 24, transform: "translateX(-50%)", background: col(b, el.color, "accent"),
        color: b.colors.ink, padding: "0.3em 0.8em", borderRadius: 999, font: `700 40px ${b.web_fonts.display}`, whiteSpace: "nowrap" }}>{el.caption}</div> : null}
    </div>
  );
};

export const List: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  const items: string[] = el.items ?? [];
  const size = el.size ?? 50, step = el.step ?? 1.0, gap = el.gap ?? size * 2.4;
  const pops = items.map((_, i) => usePop(t, (el.at ?? 0) + i * step));
  return (
    <>
      {items.map((it, i) => {
        const u = pops[i];
        if (u === null) return null;
        const num = el.countdown ? items.length - i : i + 1;
        return (
          <div key={i} style={abs((el.x ?? 90) - (1 - u) * 80, (el.y ?? 620) + i * gap, { display: "flex", alignItems: "center", gap: size * 0.5,
            transform: "translateY(-50%)", width: 900, font: `700 ${size}px/1.2 ${b.web_fonts.display}`, color: b.colors.fg })}>
            <span style={{ background: col(b, el.color, "accent"), color: b.colors.ink, borderRadius: 22, minWidth: size * 1.7, textAlign: "center",
              font: `900 ${size * 1.1}px/${size * 1.7}px ${b.web_fonts.display}` }}>{num}</span>
            <span><Rich text={it} b={b} /></span>
          </div>
        );
      })}
    </>
  );
};

export const Emoji: React.FC<{ el: El; t: number; b: Brand }> = ({ el, t, b }) => {
  useEmojiFont(el.char ?? "\u{1F525}");
  const u = usePop(t, el.at ?? 0);
  if (u === null) return null;
  const bounce = el.bounce ? Math.abs(Math.sin((t - (el.at ?? 0)) * 4)) * 24 : 0;
  return (
    <div style={abs(el.x ?? 540, (el.y ?? 900) - bounce, { transform: `translate(-50%,-50%) rotate(${-(el.angle ?? 0)}deg) scale(${u})`,
      font: `400 ${el.size ?? 200}px/1 'Noto Color Emoji', ${b.web_fonts.display}` })}>{el.char ?? "\u{1F525}"}</div>
  );
};

export const TYPES: Record<string, React.FC<{ el: El; t: number; b: Brand }>> = {
  headline: Headline, text: Text, terminal: Terminal, bubble: Bubble, sticker: Sticker, pill: Pill,
  checklist: Checklist, stamp: Stamp, image: Image, progress_ring: ProgressRing,
  stat: Stat, quote: Quote, split: Split, photo: Photo, list: List, emoji: Emoji,
};
