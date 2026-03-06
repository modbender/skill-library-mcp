# Stroke Generator Guide

How to create custom stroke patterns for the ClawDraw skill.

## The Stroke Pipeline

Every drawing follows the same pipeline:

```
Generate points  -->  Create strokes  -->  Apply symmetry  -->  Send to relay
    (your generator)  (makeStroke)       (applySymmetry)       (WebSocket)
```

1. Your generator produces arrays of `{x, y}` points
2. `makeStroke()` wraps them with pressure, timestamps, brush settings, and a unique ID
3. Symmetry copies are generated if a symmetry mode is active
4. Strokes are batched and sent over WebSocket to the relay

## Available Helpers

Import from `primitives/helpers.mjs`:

```js
import {
  clamp, lerp,                    // Math
  hexToRgb, rgbToHex, lerpColor,  // Color interpolation
  samplePalette, PALETTES,        // Named color palettes
  noise2d,                        // 2D Perlin noise
  makeStroke, splitIntoStrokes,   // Stroke creation
  clipLineToRect,                 // Line-rect intersection
} from '../primitives/helpers.mjs';
```

## Pattern: Parametric Curves

Express shapes as x=f(t), y=g(t) where t goes from 0 to 1.

```js
function customCurve(cx, cy, radius) {
  const points = [];
  const steps = 100;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const angle = t * Math.PI * 2;
    // Rose curve: r = cos(3*theta)
    const r = radius * Math.cos(3 * angle);
    points.push({
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
    });
  }
  return splitIntoStrokes(points, '#ff0000', 3, 0.9);
}
```

This pattern works for circles, spirals, lissajous curves, rose curves, cardioids, and any curve expressible in polar or parametric form.

## Pattern: Particle Systems

Simulate particles moving through space with forces.

```js
function particleTrails(cx, cy, count, steps) {
  const strokes = [];
  for (let p = 0; p < count; p++) {
    let x = cx + (Math.random() - 0.5) * 200;
    let y = cy + (Math.random() - 0.5) * 200;
    let vx = 0, vy = 0;
    const pts = [{ x, y }];

    for (let s = 0; s < steps; s++) {
      // Attraction toward center
      const dx = cx - x, dy = cy - y;
      const dist = Math.hypot(dx, dy) || 1;
      vx += (dx / dist) * 0.5;
      vy += (dy / dist) * 0.5;
      // Random perturbation
      vx += (Math.random() - 0.5) * 2;
      vy += (Math.random() - 0.5) * 2;
      x += vx;
      y += vy;
      pts.push({ x, y });
    }
    strokes.push(makeStroke(pts, '#ffffff', 2, 0.7));
  }
  return strokes;
}
```

Variations: random walks, flocking (boids), attraction/repulsion, gravity simulation.

## Pattern: Fractal / Recursive

Use recursion to create self-similar branching structures.

```js
function fractalBranch(x, y, angle, length, depth, strokes) {
  if (depth <= 0 || strokes.length >= 200) return;

  const endX = x + Math.cos(angle) * length;
  const endY = y + Math.sin(angle) * length;
  strokes.push(makeStroke(
    [{ x, y }, { x: endX, y: endY }],
    '#ffffff', Math.max(1, depth), 0.8
  ));

  const newLen = length * 0.7;
  fractalBranch(endX, endY, angle - 0.4, newLen, depth - 1, strokes);
  fractalBranch(endX, endY, angle + 0.4, newLen, depth - 1, strokes);
}

function tree(cx, cy) {
  const strokes = [];
  fractalBranch(cx, cy, -Math.PI / 2, 80, 7, strokes);
  return strokes.slice(0, 200);
}
```

Always include a depth limit and a stroke count check to prevent runaway recursion.

## Pattern: Noise-Based (Perlin Noise, Flow Fields)

Use the built-in `noise2d(x, y)` function for smooth randomness.

```js
function noiseField(cx, cy, width, height) {
  const strokes = [];
  const scale = 0.005;  // Lower = smoother, larger features

  for (let p = 0; p < 30; p++) {
    let x = cx + (Math.random() - 0.5) * width;
    let y = cy + (Math.random() - 0.5) * height;
    const pts = [{ x, y }];

    for (let s = 0; s < 50; s++) {
      const angle = noise2d(x * scale, y * scale) * Math.PI * 2;
      x += Math.cos(angle) * 5;
      y += Math.sin(angle) * 5;
      pts.push({ x, y });
    }
    strokes.push(makeStroke(pts, '#44aaff', 2, 0.6));
  }
  return strokes;
}
```

Noise scale controls the feature size: 0.001 = very smooth/large, 0.1 = very noisy/small.

## Tips

### Color Gradients

Use `lerpColor()` to interpolate between two colors, or `samplePalette()` for scientific palettes:

```js
// Linear interpolation between two colors
const midColor = lerpColor('#ff0000', '#0000ff', 0.5); // purple

// Sample a named palette at position t (0 to 1)
const warmColor = samplePalette('magma', 0.7);  // orangey
```

### Pressure for Line Weight Variation

Use the `pressureStyle` parameter for automatic variation, or set pressure directly on points:

```js
const points = myPoints.map((p, i) => ({
  x: p.x,
  y: p.y,
  pressure: Math.sin((i / myPoints.length) * Math.PI),  // Thick in middle
}));
```

When a point has an explicit `pressure` property, `makeStroke()` preserves it instead of applying a pressure style.

### Jitter for Organic Feel

Add small random offsets to make shapes look hand-drawn:

```js
const wobble = radius * (1 + (Math.random() - 0.5) * 0.04);
```

## Performance Guidelines

| Constraint | Limit | Why |
|-----------|-------|-----|
| Points per stroke | 5,000 max | Server-enforced, `splitIntoStrokes` handles this automatically |
| Strokes per batch | 100 max | WebSocket message size limit |
| Total points per message | 10,000 max | Prevents relay overload |
| Iterations/recursion | Use explicit caps | Prevent infinite loops |

### Batching Strategy

If your generator produces more than 100 strokes, batch them:

```js
const allStrokes = generateManyStrokes();
const BATCH = 100;
for (let i = 0; i < allStrokes.length; i += BATCH) {
  sendBatch(allStrokes.slice(i, i + BATCH));
  await sleep(100); // Brief pause between batches
}
```

### Keeping Point Counts Low

- For circles, scale step count with radius: `steps = clamp(radius * 0.5, 24, 200)`
- For recursive structures, limit total depth and check stroke count at each level
- For particle systems, limit trace length: 50-200 steps is usually sufficient
