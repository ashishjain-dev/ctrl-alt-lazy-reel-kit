import React from "react";
import { Composition, Still, staticFile } from "remotion";
import { CoverStill } from "./Cover";
import { ReelVideo } from "./Reel";
import type { Reel } from "./types";

const load = async (): Promise<Reel> => {
  const r = await fetch(staticFile("reel.json"));
  if (!r.ok) throw new Error("public/reel.json missing: run `npm run prep -- <scenes.yaml>` first");
  return r.json();
};

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="Reel"
      component={ReelVideo as any}
      width={1080}
      height={1920}
      fps={60}
      durationInFrames={60}
      defaultProps={{ reel: null as unknown as Reel }}
      calculateMetadata={async () => {
        const reel = await load();
        return { props: { reel }, fps: reel.fps, width: reel.width, height: reel.height,
          durationInFrames: Math.max(1, Math.round(reel.total * reel.fps)) };
      }}
    />
    <Still
      id="Cover"
      component={CoverStill as any}
      width={1080}
      height={1920}
      defaultProps={{ reel: null as unknown as Reel }}
      calculateMetadata={async () => ({ props: { reel: await load() } })}
    />
  </>
);
