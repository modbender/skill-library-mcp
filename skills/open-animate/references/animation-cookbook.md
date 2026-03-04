# Animation Cookbook

Complete reference for all `@oanim/core` animation presets.

## Element Animations

All element animations take `{ frame, fps, delay?, spring? }` and return `CSSProperties`.

### fadeUp
Fades in while moving up 20px. The default go-to for text and UI elements.
```tsx
import { fadeUp } from '@oanim/core';
<div style={fadeUp({ frame, fps, delay: 0.2 })}>Content</div>
```

### fadeDown
Fades in while moving down 20px. Good for dropdown menus, secondary info.
```tsx
import { fadeDown } from '@oanim/core';
<div style={fadeDown({ frame, fps, delay: 0.2 })}>Content</div>
```

### slideInLeft / slideInRight
Slides in from left/right with fade. Good for side-by-side comparisons.
```tsx
import { slideInLeft, slideInRight } from '@oanim/core';
<div style={slideInLeft({ frame, fps, delay: 0.2 })}>Left panel</div>
<div style={slideInRight({ frame, fps, delay: 0.3 })}>Right panel</div>
```

### popIn
Spring-based scale entrance (0.5→1) with bounce. Great for badges, icons, CTAs.
```tsx
import { popIn } from '@oanim/core';
<div style={popIn({ frame, fps, delay: 0.1 })}>🚀</div>
```

### blurIn
Fades in from blurry to sharp. Cinematic feel, good for hero text.
```tsx
import { blurIn } from '@oanim/core';
<div style={blurIn({ frame, fps, delay: 0.2 })}>Title</div>
```

### elasticScale
Wobbly spring scale entrance. Playful, attention-grabbing.
```tsx
import { elasticScale } from '@oanim/core';
<div style={elasticScale({ frame, fps })}>Boing!</div>
```

### perspectiveRotateIn
3D rotation entrance from below. Dramatic, good for cards and panels.
```tsx
import { perspectiveRotateIn } from '@oanim/core';
<div style={perspectiveRotateIn({ frame, fps, delay: 0.3 })}>Card</div>
```

## Spring Presets

Override the default spring on any element animation:
```tsx
fadeUp({ frame, fps, spring: 'bouncy' })
```

| Preset | Feel | Best for |
|--------|------|----------|
| `snappy` | Quick, precise | Default, UI elements |
| `bouncy` | Playful overshoot | Badges, icons, CTAs |
| `gentle` | Slow, smooth | Backgrounds, large elements |
| `stiff` | Very fast, no overshoot | Micro-interactions |
| `wobbly` | Lots of bounce | Playful animations |
| `smooth` | Medium, no overshoot | Text, panels |
| `poppy` | Fast with slight bounce | Buttons, cards |

## Easing Presets

For `interpolate()` with frame-based animations:
```tsx
import { easings } from '@oanim/core';
import { interpolate } from 'remotion';

const value = interpolate(frame, [0, 30], [0, 100], {
  easing: easings.easeOut,
  extrapolateRight: 'clamp',
});
```

| Preset | Curve |
|--------|-------|
| `easeOut` | Fast start, slow end |
| `circOut` | Circular deceleration |
| `easeInOut` | Smooth S-curve |
| `backOut` | Slight overshoot |
| `expoOut` | Exponential deceleration |

## Transition Presets

For use with `<TransitionSeries.Transition presentation={...}>`:

```tsx
import { fadeBlur, scaleFade, clipCircle } from '@oanim/core';
```

| Preset | Effect |
|--------|--------|
| `fadeBlur()` | Crossfade with blur |
| `scaleFade()` | Scale 0.95→1 with fade |
| `clipCircle()` | Circular reveal |
| `clipPolygon()` | Diamond/polygon reveal |
| `wipe()` | Directional wipe (pass `{ direction: 'left'\|'right'\|'up'\|'down' }`) |
| `splitHorizontal()` | Open from horizontal center |
| `splitVertical()` | Open from vertical center |
| `perspectiveFlip()` | 3D flip |
| `morphExpand()` | Scale up from circle to full |
| `zoomThrough()` | Zoom into next scene |
| `pushLeft()` | Push current scene left |
| `pushRight()` | Push current scene right |
| `slideLeft()` | New scene slides in from right |
| `slideRight()` | New scene slides in from left |

## Typography Components

### AnimatedCharacters
Staggered per-character spring entrance:
```tsx
import { AnimatedCharacters } from '@oanim/core';

<AnimatedCharacters
  text="Hello World"
  delay={0.2}       // seconds before first char
  stagger={0.03}    // seconds between chars
  spring="snappy"   // spring preset
/>
```

### TypewriterText
Character-by-character typing reveal:
```tsx
import { TypewriterText } from '@oanim/core';

<TypewriterText
  text="npm install @oanim/core"
  delay={0.5}
  charsPerSecond={20}
  showCursor={true}
/>
```

### CountUp
Animated number counter:
```tsx
import { CountUp } from '@oanim/core';

<CountUp
  from={0}
  to={10000}
  delay={0.3}
  duration={1}
  prefix="$"
  suffix="+"
  decimals={0}
/>
```

## Helpers

### springValue
Get a 0→1 spring value for custom animations:
```tsx
import { springValue } from '@oanim/core';

const progress = springValue({ frame, fps, delay: 0.2, spring: 'bouncy' });
```

### springInterpolate
Map a spring to a custom range:
```tsx
import { springInterpolate } from '@oanim/core';

const rotation = springInterpolate({ frame, fps }, [0, 360]);
```
