export type El = { type: string; at?: number; until?: number; [k: string]: any };
export type Line = {
  who: string; text: string; mood?: string; react?: Record<string, string>;
  start: number; dur: number; env: number[] | null; audio: string | null; subtitle?: boolean;
};
export type Scene = {
  name: string; start: number; dur: number; glow?: string; glow_at?: [number, number];
  elements?: El[]; cast?: El[]; lines: Line[]; shake?: number[]; punch?: number[];
};
export type Brand = {
  handle: string; label: string; colors: Record<string, string>;
  frame: { progress_bar: boolean; watermark: boolean; accent_bar: boolean; safe_top: number; safe_bottom: number };
  web_fonts: { display: string; mono: string }; characters: Record<string, Record<string, string>>;
};
export type Reel = {
  title: string; fps: number; width: number; height: number; total: number; brand: Brand;
  scenes: Scene[]; cover: any; audio: string | null; voicesInMix: boolean;
};
