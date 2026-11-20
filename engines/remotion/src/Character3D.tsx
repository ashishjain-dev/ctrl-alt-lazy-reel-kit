// 3D versions of the built-in characters (person, bot, blob), built from Three.js primitives so there
// are no model files to license. Same names, moods and colour keys as the Pillow engine.
import { ThreeCanvas } from "@remotion/three";
import React from "react";
import * as THREE from "three";

const PERSON = { skin: "#f1c7a3", hair_color: "#3a2a24", shirt: "#3fa796", pants: "#2c3450", accent: "#e8805c",
  hair: "short", hat: "none", glasses: false, headphones: false, beard: false } as Record<string, any>;
const BLOB = { body: "#8fd0ff", belly: "#d9f0ff", accent: "#ff8fa3", sprout: true } as Record<string, any>;
const BOT = { body: "#c9d2e0", screen: "#141a26", eyes: "#7af0c8", trim: "#5a6a86" };

type P = { mood: string; t: number; talk: number; colors?: Record<string, string> };

const Eye: React.FC<{ x: number; y: number; z: number; mood: string; color: string; blink: number; flat?: boolean }> = ({ x, y, z, mood, color, blink, flat }) => {
  const mat = flat ? <meshBasicMaterial color={color} /> : <meshStandardMaterial color={color} roughness={0.4} />;
  if (mood === "happy" || mood === "smug" || mood === "love")
    return <mesh position={[x, y - 0.02, z]} rotation={[0, 0, 0]}><torusGeometry args={[0.09, 0.025, 8, 24, Math.PI]} />{mat}</mesh>;
  if (mood === "deadpan")
    return <mesh position={[x, y, z]}><boxGeometry args={[0.2, 0.04, 0.02]} />{mat}</mesh>;
  if (mood === "error")
    return (
      <group position={[x, y, z]}>
        <mesh rotation={[0, 0, Math.PI / 4]}><boxGeometry args={[0.2, 0.04, 0.02]} /><meshBasicMaterial color="#f06056" /></mesh>
        <mesh rotation={[0, 0, -Math.PI / 4]}><boxGeometry args={[0.2, 0.04, 0.02]} /><meshBasicMaterial color="#f06056" /></mesh>
      </group>
    );
  const s = mood === "shocked" ? 1.5 : 1;
  return <mesh position={[x, y, z]} scale={[s, s * blink, s]}><sphereGeometry args={[0.07, 16, 16]} />{mat}</mesh>;
};

const blinkAt = (t: number, seed = 0) => (((t + seed) % 3.7) < 0.12 ? 0.15 : 1);

export const Person3D: React.FC<P> = ({ mood, t, talk, colors }) => {
  const c = { ...PERSON, ...(colors || {}) };
  const bob = Math.sin(t * 2.2) * 0.03;
  const arm = mood === "shocked" ? 1.2 : mood === "happy" ? 0.6 : 0.15;
  const bl = blinkAt(t);
  const hair = c.hair as string;
  const capOn = hair !== "bald" && hair !== "curly" && hair !== "spiky";
  return (
    <group position={[0, -1.1 + bob, 0]} rotation={[0, Math.sin(t * 0.8) * 0.15, 0]}>
      {[-0.22, 0.22].map((x) => <mesh key={x} position={[x, 0.35, 0]}><cylinderGeometry args={[0.13, 0.13, 0.7, 16]} /><meshStandardMaterial color={c.pants} /></mesh>)}
      <mesh position={[0, 1.05, 0]}><capsuleGeometry args={[0.42, 0.45, 8, 24]} /><meshStandardMaterial color={c.shirt} /></mesh>
      {[-1, 1].map((sx) => (
        <mesh key={sx} position={[sx * 0.55, 1.15, 0]} rotation={[0, 0, sx * arm]}><capsuleGeometry args={[0.1, 0.45, 6, 12]} /><meshStandardMaterial color={c.shirt} /></mesh>
      ))}
      <group position={[0, 2.05, 0]}>
        <mesh scale={[1.08, 0.98, 1]}><sphereGeometry args={[0.62, 48, 48]} /><meshStandardMaterial color={c.skin} roughness={0.7} /></mesh>
        {capOn ? <mesh position={[0, 0.12, -0.02]} scale={[1.12, 0.9, 1.06]}><sphereGeometry args={[0.6, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2.1]} /><meshStandardMaterial color={c.hair_color} /></mesh> : null}
        {hair === "long" ? <mesh position={[0, -0.25, -0.18]} scale={[1.15, 1.2, 0.8]}><sphereGeometry args={[0.6, 32, 32]} /><meshStandardMaterial color={c.hair_color} /></mesh> : null}
        {hair === "bun" ? <mesh position={[0, 0.72, -0.1]}><sphereGeometry args={[0.24, 24, 24]} /><meshStandardMaterial color={c.hair_color} /></mesh> : null}
        {hair === "curly" ? Array.from({ length: 11 }, (_, i) => {
          const a = Math.PI * (0.05 + 0.9 * (i / 10));
          return <mesh key={i} position={[-Math.cos(a) * 0.6, 0.25 + Math.sin(a) * 0.38, -0.05]}><sphereGeometry args={[0.2, 16, 16]} /><meshStandardMaterial color={c.hair_color} /></mesh>;
        }) : null}
        {hair === "spiky" ? Array.from({ length: 7 }, (_, i) => (
          <mesh key={i} position={[-0.5 + i * 0.167, 0.6, -0.05]} rotation={[0, 0, (i - 3) * -0.18]}><coneGeometry args={[0.13, 0.42, 12]} /><meshStandardMaterial color={c.hair_color} /></mesh>
        )) : null}
        {c.hat === "cap" ? (
          <group position={[0, 0.3, 0]}>
            <mesh scale={[1.12, 0.8, 1.1]}><sphereGeometry args={[0.6, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2]} /><meshStandardMaterial color={c.accent} /></mesh>
            <mesh position={[0, 0.02, 0.62]} rotation={[0.25, 0, 0]}><boxGeometry args={[0.8, 0.05, 0.45]} /><meshStandardMaterial color={c.accent} /></mesh>
          </group>
        ) : null}
        {c.hat === "beanie" ? (
          <group position={[0, 0.26, 0]}>
            <mesh scale={[1.14, 0.95, 1.12]}><sphereGeometry args={[0.6, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2]} /><meshStandardMaterial color={c.accent} /></mesh>
            <mesh position={[0, 0.62, 0]}><sphereGeometry args={[0.13, 16, 16]} /><meshStandardMaterial color={c.accent} /></mesh>
          </group>
        ) : null}
        {c.headphones ? (
          <>
            <mesh position={[0, 0.05, 0]}><torusGeometry args={[0.7, 0.05, 12, 48, Math.PI]} /><meshStandardMaterial color={c.accent} /></mesh>
            {[-1, 1].map((sx) => <mesh key={sx} position={[sx * 0.68, 0, 0]} rotation={[0, 0, Math.PI / 2]}><cylinderGeometry args={[0.17, 0.17, 0.14, 24]} /><meshStandardMaterial color={c.accent} /></mesh>)}
          </>
        ) : null}
        {c.beard ? <mesh position={[0, -0.32, 0.22]} scale={[1, 0.8, 0.8]}><sphereGeometry args={[0.45, 32, 32, 0, Math.PI * 2, Math.PI / 2.2, Math.PI / 2]} /><meshStandardMaterial color={c.hair_color} /></mesh> : null}
        <Eye x={-0.22} y={0.02} z={0.58} mood={mood} color="#141418" blink={bl} />
        <Eye x={0.22} y={0.02} z={0.58} mood={mood === "wink" ? "happy" : mood} color="#141418" blink={bl} />
        {c.glasses ? [-1, 1].map((sx) => (
          <mesh key={sx} position={[sx * 0.22, 0.02, 0.67]}><torusGeometry args={[0.13, 0.025, 8, 32]} /><meshStandardMaterial color="#141418" /></mesh>
        )) : null}
        {mood === "angry" || mood === "sad" ? [-1, 1].map((sx) => (
          <mesh key={sx} position={[sx * 0.22, 0.17, 0.6]} rotation={[0, 0, sx * (mood === "angry" ? -0.35 : 0.35)]}><boxGeometry args={[0.18, 0.035, 0.02]} /><meshBasicMaterial color="#141418" /></mesh>
        )) : null}
        <mesh position={[0, -0.25, 0.57]} scale={[1, talk > 0.05 ? 0.4 + 2.2 * talk : mood === "shocked" ? 1.8 : 0.35, 1]}>
          <sphereGeometry args={[0.07, 16, 16]} /><meshStandardMaterial color={talk > 0.05 || mood === "shocked" ? "#5a1e28" : "#141418"} />
        </mesh>
      </group>
    </group>
  );
};

export const Blob3D: React.FC<P> = ({ mood, t, talk, colors }) => {
  const c = { ...BLOB, ...(colors || {}) };
  const sq = mood === "happy" || mood === "love" ? 1 + 0.08 * Math.abs(Math.sin(t * 6)) : 1 + 0.04 * Math.sin(t * 3.2);
  const bl = blinkAt(t, 0.7);
  return (
    <group position={[0, -1.05, 0]} rotation={[0, Math.sin(t * 0.8) * 0.2, 0]}>
      {[-1, 1].map((sx) => <mesh key={sx} position={[sx * 0.35, 0.1, 0.1]} scale={[1, 0.5, 1.2]}><sphereGeometry args={[0.22, 16, 16]} /><meshStandardMaterial color={c.body} /></mesh>)}
      <group position={[0, 1.15 * sq, 0]} scale={[1 / Math.sqrt(sq), sq, 1 / Math.sqrt(sq)]}>
        <mesh><sphereGeometry args={[1.05, 48, 48]} /><meshStandardMaterial color={c.body} roughness={0.35} /></mesh>
        <mesh position={[0, -0.25, 0.55]} scale={[1, 1, 0.6]}><sphereGeometry args={[0.72, 32, 32]} /><meshStandardMaterial color={c.belly} /></mesh>
      </group>
      {c.sprout ? (
        <group position={[0, 2.2 * sq, 0]}>
          <mesh position={[0, 0.12, 0]}><cylinderGeometry args={[0.03, 0.03, 0.3, 8]} /><meshStandardMaterial color="#5aaa6e" /></mesh>
          {[-1, 1].map((sx) => <mesh key={sx} position={[sx * 0.16, 0.3, 0]} rotation={[0, 0, sx * -0.6]} scale={[1, 0.5, 0.3]}><sphereGeometry args={[0.18, 16, 16]} /><meshStandardMaterial color="#6ec878" /></mesh>)}
        </group>
      ) : null}
      <group position={[0, 1.35 * sq, 0.98]}>
        <Eye x={-0.3} y={0} z={0} mood={mood === "error" ? "shocked" : mood} color="#141418" blink={bl} />
        <Eye x={0.3} y={0} z={0} mood={mood === "wink" ? "happy" : mood === "error" ? "shocked" : mood} color="#141418" blink={bl} />
        <mesh position={[0, -0.3, 0.02]} scale={[1.3, talk > 0.05 ? 0.4 + 2.2 * talk : mood === "shocked" ? 1.8 : 0.35, 1]}>
          <sphereGeometry args={[0.07, 16, 16]} /><meshStandardMaterial color={talk > 0.05 || mood === "shocked" ? "#5a1e28" : "#141418"} />
        </mesh>
      </group>
    </group>
  );
};

export const Bot3D: React.FC<P> = ({ mood, t, talk, colors }) => {
  const c = { ...BOT, ...(colors || {}) };
  const hover = Math.sin(t * 2.6) * 0.06;
  const eyeCol = mood === "error" ? "#f06056" : c.eyes;
  const bl = blinkAt(t, 1.3);
  const wave = mood === "happy" || mood === "love" ? Math.sin(t * 6) * 0.5 : 0;
  return (
    <group position={[0, -1.0 + hover, 0]} rotation={[0, Math.sin(t * 0.7) * 0.2, 0]}>
      <mesh position={[0, 0.2, 0]}><cylinderGeometry args={[0.3, 0.38, 0.22, 24]} /><meshStandardMaterial color={c.trim} metalness={0.4} roughness={0.4} /></mesh>
      <mesh position={[0, 0.85, 0]}><boxGeometry args={[0.9, 0.85, 0.6]} /><meshStandardMaterial color={c.body} metalness={0.3} roughness={0.35} /></mesh>
      <mesh position={[0, 0.9, 0.31]}><sphereGeometry args={[0.1, 16, 16]} /><meshBasicMaterial color={c.eyes} /></mesh>
      {[-1, 1].map((sx) => (
        <mesh key={sx} position={[sx * 0.58, 0.95, 0]} rotation={[0, 0, sx * (0.5 + (sx > 0 ? wave : 0))]}><capsuleGeometry args={[0.07, 0.4, 6, 12]} /><meshStandardMaterial color={c.trim} /></mesh>
      ))}
      <mesh position={[0, 1.38, 0]}><cylinderGeometry args={[0.1, 0.1, 0.2, 16]} /><meshStandardMaterial color={c.trim} /></mesh>
      <group position={[0, 2.0, 0]}>
        <mesh><boxGeometry args={[1.5, 1.15, 0.7]} /><meshStandardMaterial color={c.body} metalness={0.3} roughness={0.3} /></mesh>
        <mesh position={[0, 0, 0.36]}><planeGeometry args={[1.25, 0.9]} /><meshBasicMaterial color={c.screen} /></mesh>
        <mesh position={[0, 0.72, 0]}><cylinderGeometry args={[0.03, 0.03, 0.35, 8]} /><meshStandardMaterial color={c.trim} /></mesh>
        <mesh position={[0, 0.93, 0]}><sphereGeometry args={[0.09, 16, 16]} /><meshBasicMaterial color={c.eyes} /></mesh>
        <Eye x={-0.28} y={0.12} z={0.37} mood={mood} color={eyeCol} blink={bl} flat />
        <Eye x={0.28} y={0.12} z={0.37} mood={mood} color={eyeCol} blink={bl} flat />
        {talk > 0.05
          ? Array.from({ length: 7 }, (_, i) => {
              const h = 0.03 + 0.16 * talk * (0.5 + 0.5 * Math.sin(t * 30 + i * 1.7));
              return <mesh key={i} position={[-0.27 + i * 0.09, -0.22, 0.37]}><planeGeometry args={[0.05, h]} /><meshBasicMaterial color={eyeCol} /></mesh>;
            })
          : <mesh position={[0, -0.22, 0.37]}><planeGeometry args={[0.36, 0.035]} /><meshBasicMaterial color={eyeCol} /></mesh>}
      </group>
    </group>
  );
};

/** A character in its own transparent WebGL canvas, positioned like the Pillow engine: (x, y) = feet.
 *  `who` is the resolved base (person | bot | blob); `colors` is the resolved look from prep.mjs. */
export const Character3D: React.FC<{ who: string; x: number; y: number; scale: number; mood: string; t: number; talk: number; colors?: Record<string, string> }> = ({ who, x, y, scale, mood, t, talk, colors }) => {
  const w = Math.round(620 * scale), h = Math.round(760 * scale);
  return (
    <div style={{ position: "absolute", left: x - w / 2, top: y - h, width: w, height: h }}>
      <ThreeCanvas width={w} height={h} camera={{ fov: 30, position: [0, 0.6, 7.2] }} gl={{ alpha: true, antialias: true }}
        onCreated={({ gl }) => { gl.setClearColor(new THREE.Color(0x000000), 0); }}>
        <ambientLight intensity={0.9} />
        <directionalLight position={[3, 5, 6]} intensity={2.2} />
        <directionalLight position={[-4, 2, -3]} intensity={0.8} color="#88aaff" />
        {who === "bot" ? <Bot3D mood={mood} t={t} talk={talk} colors={colors} />
          : who === "blob" ? <Blob3D mood={mood} t={t} talk={talk} colors={colors} />
          : <Person3D mood={mood} t={t} talk={talk} colors={colors} />}
      </ThreeCanvas>
    </div>
  );
};
