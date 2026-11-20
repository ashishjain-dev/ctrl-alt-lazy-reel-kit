import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setConcurrency(null);
// Three.js needs WebGL in headless Chrome. "angle" works on most machines; try "swangle" on CI/servers without a GPU.
Config.setChromiumOpenGlRenderer("angle");
