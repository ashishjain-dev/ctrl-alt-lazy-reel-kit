import React from "react";
import { AbsoluteFill } from "remotion";
import { Character3D } from "./Character3D";
import { Rich, col } from "./elements";
import type { Reel } from "./types";

export const CoverStill: React.FC<{ reel: Reel }> = ({ reel }) => {
  const b = reel.brand;
  const c = reel.cover ?? { headline: reel.title };
  const glow = col(b, c.glow, "accent");
  const ch = c.character;
  return (
    <AbsoluteFill style={{ background: `linear-gradient(${b.colors.bg_top}, ${b.colors.bg_bottom})` }}>
      <div style={{ position: "absolute", left: 20, top: 630, width: 1040, height: 1040, borderRadius: "50%",
        background: `radial-gradient(circle, ${glow}66 0%, ${glow}00 70%)` }} />
      {b.frame.accent_bar ? <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: 10, background: b.colors.accent }} /> : null}
      {c.tag ? <div style={{ position: "absolute", left: 70, top: 450, padding: "6px 24px", borderRadius: 20, background: b.colors.accent,
        color: b.colors.ink, font: `900 44px ${b.web_fonts.display}` }}>{c.tag}</div> : null}
      <div style={{ position: "absolute", left: 70, right: 70, top: (c.y ?? 640) - 64, color: b.colors.fg,
        font: `900 ${c.size ?? 104}px/1.22 ${b.web_fonts.display}` }}>
        <Rich text={c.headline} b={b} />
        {c.sub ? <div style={{ font: `700 50px ${b.web_fonts.display}`, color: b.colors.muted, marginTop: 24 }}>{c.sub}</div> : null}
      </div>
      {ch ? <Character3D who={ch.who ?? "bot"} x={ch.x ?? 740} y={ch.y ?? 1560} scale={ch.scale ?? 0.95} mood={ch.mood ?? "smug"} t={0.4} talk={0}
        colors={b.characters?.[ch.who ?? "bot"]} /> : null}
      {b.handle ? <div style={{ position: "absolute", left: 0, right: 0, top: 1590, textAlign: "center", color: b.colors.muted,
        font: `700 34px ${b.web_fonts.display}` }}>{b.handle}</div> : null}
    </AbsoluteFill>
  );
};
