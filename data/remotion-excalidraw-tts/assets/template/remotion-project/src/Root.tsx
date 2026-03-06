import "./index.css";
import { Composition } from "remotion";
import { OpenClawMemoryVideo } from "./video/OpenClawMemoryVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="OpenClawMemory"
        component={OpenClawMemoryVideo}
        // Match voiceover duration (~191.26s) @ 30fps
        durationInFrames={5738}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
