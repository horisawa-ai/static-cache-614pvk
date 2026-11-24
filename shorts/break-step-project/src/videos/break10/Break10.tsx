// "Break Step" — 10.5 s example short built from the bridge template world.
// Each edit maps a run of new frames onto the template's story timeline (camera, physics, cast all come from story.ts).
import React from "react";
import { BridgeShort, FRAME_MAP } from "../bridge/Bridge";

// [new start, new end, old start]; voice starts at frame 6 (voice/voice.wav)
export const EDL: [number, number, number][] = [
  [0, 45, 140],     // town aerial: "Seventy-four soldiers"
  [45, 120, 290],   // column front -> boots CU: "marched across a bridge in perfect step"
  [120, 165, 765],  // low 3/4 front, deck bouncing: "It bounced to their rhythm"
  [165, 212, 1003], // bolt insert, snaps on new 201: "until one bolt snapped"
  [212, 232, 1099], // drop into the river (slam kick on 221)
  [232, 262, 1800], // officer nails up the new rule: "Now soldiers"
  [262, 315, 1867], // tourists ambling across the rebuilt bridge: "break step on every bridge"
];
export const BREAK10_FRAMES = 315;
export const mapFrame = (f: number) => {
  const e = EDL.find(([a, b]) => f >= a && f < b) ?? EDL[EDL.length - 1];
  return e[2] + (f - e[0]);
};
export const Break10: React.FC = () => {
  FRAME_MAP.fn = mapFrame;
  return <BridgeShort />;
};
