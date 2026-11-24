import React from "react";
import { Composition } from "remotion";
import { BridgeShort, BRIDGE_FRAMES } from "./videos/bridge/Bridge";
import { Break10, BREAK10_FRAMES } from "./videos/break10/Break10";
export const Root: React.FC = () => (<>
  <Composition id="BridgeShort" component={BridgeShort} durationInFrames={BRIDGE_FRAMES} fps={30} width={1080} height={1920} />
  <Composition id="Break10" component={Break10} durationInFrames={BREAK10_FRAMES} fps={30} width={1080} height={1920} />
</>);
