# Example: Product Launch Video

A 15-second, 4-scene product launch video.

## Structure

| Scene | Duration | Purpose | Transition |
|-------|----------|---------|------------|
| Hook | 4s (120f) | Grab attention with bold text | → fadeBlur |
| Product Hero | 4.5s (135f) | Show the product in action | → scaleFade |
| Features | 3.5s (105f) | Highlight 3 key features | → clipCircle |
| CTA | 4s (120f) | Call to action | — |

## Composition

```tsx
<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={120}>
    <Hook />
  </TransitionSeries.Sequence>

  <TransitionSeries.Transition
    presentation={fadeBlur()}
    timing={springTiming({ config: { damping: 200 }, durationInFrames: 30 })}
  />

  <TransitionSeries.Sequence durationInFrames={135}>
    <ProductHero />
  </TransitionSeries.Sequence>

  <TransitionSeries.Transition
    presentation={scaleFade()}
    timing={springTiming({ config: { damping: 200 }, durationInFrames: 25 })}
  />

  <TransitionSeries.Sequence durationInFrames={105}>
    <Features />
  </TransitionSeries.Sequence>

  <TransitionSeries.Transition
    presentation={clipCircle()}
    timing={springTiming({ config: { damping: 200 }, durationInFrames: 30 })}
  />

  <TransitionSeries.Sequence durationInFrames={120}>
    <CTA />
  </TransitionSeries.Sequence>
</TransitionSeries>
```

## Key patterns used

- **Hook scene**: `AnimatedCharacters` for staggered title reveal, `Badge` for label, `blurIn` for cinematic feel
- **Product Hero**: `Terminal` component with animated typing, `Grid` background, `popIn` entrance
- **Features**: Staggered `Card` components with increasing delays (0.3, 0.45, 0.6)
- **CTA**: `AnimatedCharacters` + `TypewriterText` for the install command

## Color palette

Uses `palettes.midnight` — deep blue/indigo tones with high contrast.
