# Composition Patterns

## Multi-scene architecture

### TransitionSeries (recommended)

Use `TransitionSeries` from `@remotion/transitions` for videos with multiple scenes:

```tsx
import { TransitionSeries, springTiming } from '@remotion/transitions';
import { fadeBlur, scaleFade, clipCircle } from '@oanim/core';

export const MyVideo: React.FC = () => {
  return (
    <AbsoluteFill>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={120}>
          <Scene1 />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fadeBlur()}
          timing={springTiming({ config: { damping: 200 }, durationInFrames: 30 })}
        />

        <TransitionSeries.Sequence durationInFrames={120}>
          <Scene2 />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </AbsoluteFill>
  );
};
```

### When to use Sequence vs TransitionSeries

| Pattern | Use case |
|---------|----------|
| `TransitionSeries` | Multiple scenes with transitions between them |
| `<Sequence>` | Sequencing elements WITHIN a single scene |
| Delay parameter | Staggering elements that appear together |

### Persistent background layer

For a background that stays consistent across transitions, wrap it outside the TransitionSeries:

```tsx
<AbsoluteFill>
  <Background gradient="linear-gradient(135deg, #0a0a0a, #1a1a2e)" />
  <GlowOrb color="rgba(99, 102, 241, 0.2)" x={30} y={40} />

  <TransitionSeries>
    {/* Scenes transition on top of persistent background */}
  </TransitionSeries>
</AbsoluteFill>
```

## Scene structure pattern

Each scene should follow this layering:

```tsx
<AbsoluteFill>
  {/* 1. Background */}
  <Background gradient="..." />

  {/* 2. Ambient elements */}
  <GlowOrb ... />
  <Grid ... />

  {/* 3. Overlays */}
  <Vignette intensity={0.4} />

  {/* 4. Content */}
  <SafeArea style={{ justifyContent: 'center', alignItems: 'center' }}>
    {/* Animated content here */}
  </SafeArea>
</AbsoluteFill>
```

## Duration guidelines

| Video type | Total duration | Scenes | Per scene |
|------------|---------------|--------|-----------|
| Social clip | 5-10s | 2-3 | 2-4s |
| Product launch | 15-30s | 4-6 | 3-5s |
| Explainer | 30-60s | 6-10 | 4-6s |
| Demo | 30-90s | 5-12 | 5-8s |

## Transition timing

- **Fast transitions** (15-20 frames): energetic, snappy feel
- **Medium transitions** (25-35 frames): professional, smooth
- **Slow transitions** (40-60 frames): cinematic, dramatic

Use `springTiming` with high damping (200) for smooth transitions.
Use `linearTiming` when you want constant-speed transitions.

## Media layers

When using AI-generated media (images, video, audio), layer them into the scene structure:

### Video or image background
```tsx
import { OffthreadVideo, Img, staticFile } from 'remotion';

// Video background
<OffthreadVideo
  src={staticFile('clip.mp4')}
  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
/>

// Or image background
<Img
  src={staticFile('bg.png')}
  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
/>

// Always add dark overlay for text readability
<AbsoluteFill style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }} />
```

### Global audio track
Place `<Audio>` at the composition level (outside TransitionSeries) so it plays across all scenes:
```tsx
import { Audio, staticFile } from 'remotion';

<AbsoluteFill>
  <Audio src={staticFile('bg-music.mp3')} volume={0.25} />
  <TransitionSeries>
    {/* Scenes here */}
  </TransitionSeries>
</AbsoluteFill>
```

### Full layer order (back to front)
1. `<OffthreadVideo>` or `<Img>` — media background
2. Dark overlay — `rgba(0, 0, 0, 0.5)`
3. `<GlowOrb>` — ambient glow
4. `<Vignette>` — edge darkening
5. `<SafeArea>` — content
6. `<Audio>` — non-visual, position doesn't matter
