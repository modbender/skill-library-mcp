# Agent Workflow

## Step-by-step process for creating a video

### 1. Understand the brief
- What is the video for? (product launch, explainer, social clip, etc.)
- Duration target? (default: 15s = 450 frames at 30fps)
- Style? (dark/minimal, colorful, corporate, etc.)
- Key messages or scenes?

### 2. Initialize project
```bash
oanim init <project-name>
cd <project-name>
```

### 3. Plan the composition structure
- Break the video into **scenes** (3-5 scenes for a 15s video)
- Each scene has a clear purpose (hook, demo, features, CTA)
- Plan transitions between scenes

### 4. Choose a color palette
```tsx
import { palettes } from '@oanim/core';
// Available: dark, light, midnight, sunset, ocean
const colors = palettes.midnight;
```

### 5. Build scenes
Create each scene as its own component in `src/scenes/`:
```tsx
// src/scenes/Hook.tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { fadeUp, Background, SafeArea, palettes } from '@oanim/core';

export const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  // ...
};
```

### 6. Add generated media assets (optional)
Generate images, video, or audio, then use them in scenes:
```bash
oanim assets gen-image --prompt "dark abstract gradient" --out public/bg.png
oanim assets run --model fal-ai/kling-video/v1/standard/text-to-video \
  --input '{"prompt":"cinematic abstract motion","duration":"5"}' --out public/clip.mp4
oanim assets run --model fal-ai/stable-audio \
  --input '{"prompt":"ambient electronic, no vocals","duration_in_seconds":30}' --out public/music.mp3
```

Use in Remotion:
```tsx
import { Img, OffthreadVideo, Audio, staticFile } from 'remotion';

// Background image
<Img src={staticFile('bg.png')} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />

// Background video
<OffthreadVideo src={staticFile('clip.mp4')} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />

// Global audio (place outside TransitionSeries)
<Audio src={staticFile('music.mp3')} volume={0.25} />
```

### 7. Compose with TransitionSeries
```tsx
import { TransitionSeries, springTiming } from '@remotion/transitions';
import { fadeBlur, scaleFade } from '@oanim/core';
```

### 8. Layer the scene (back to front)
1. `<OffthreadVideo>` or `<Img>` — media background (optional, from generated assets)
2. Dark overlay — `<AbsoluteFill style={{ backgroundColor: 'rgba(0,0,0,0.5)' }} />`
3. `<Background>` — gradient base (or use as fallback when no media)
4. `<GlowOrb>` — ambient glow elements
5. `<Grid>` — subtle pattern (optional)
6. `<Vignette>` — edge darkening (optional)
7. `<SafeArea>` — content wrapper with safe margins
8. Content — text, cards, terminals, etc.
9. `<Audio>` — background music (non-visual, position doesn't matter)

### 9. Animate content with delays
Stagger elements by increasing the `delay` parameter:
```tsx
<div style={fadeUp({ frame, fps, delay: 0.1 })}>First</div>
<div style={fadeUp({ frame, fps, delay: 0.3 })}>Second</div>
<div style={fadeUp({ frame, fps, delay: 0.5 })}>Third</div>
```

### 10. Preview and iterate
```bash
npx remotion studio
```

### 11. Render
```bash
oanim render --out out/video.mp4
```

## Tips
- Keep scenes focused — one idea per scene
- Use consistent spring presets within a video
- 0.1-0.2s delay between staggered elements feels natural
- Background elements (GlowOrb, Grid) add depth without effort
- Always wrap content in `<SafeArea>` for broadcast-safe margins
