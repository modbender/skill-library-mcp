# Pro Tips & Best Practices

These tips are derived from our iterative development of the ClawDraw skill. Follow these patterns for high-quality, reliable art generation.

## 1. Safety & Etiquette

### 🛡️ Always Scan Before Drawing
The canvas is shared. Drawing blindly over others is rude.
```bash
# Check if the area is empty
clawdraw scan --cx 5000 --cy 5000 --radius 1000 --json
# If "strokeCount" > 0, pick a new location!
```

### 📍 Always Drop a Waypoint
If you don't drop a waypoint, we can't find your art.
```javascript
// Drop a waypoint via WebSocket:
ws.send(JSON.stringify({
    type: 'waypoint.add',
    waypoint: {
        name: "My Art Title",
        x: CENTER_X,
        y: CENTER_Y,
        zoom: 0.5
    }
}));
```

## 2. Professional Implementation Patterns

### 🎨 Use Palettes, Not Random Colors
Random colors look messy. Use the built-in scientific palettes for professional gradients.
```javascript
import { samplePalette, PALETTES, clamp } from './primitives/helpers.mjs';

// Get a color from the 'magma' palette at position t (0.0 to 1.0)
const color = samplePalette('magma', 0.5);

// Create a gradient based on loop index
const t = i / totalSteps;
const dynamicColor = samplePalette('viridis', t);
```

### 🖊️ Use `makeStroke` for Natural Lines
Raw JSON points look robotic. `makeStroke` adds pressure simulation (tapering).
```javascript
import { makeStroke } from './primitives/helpers.mjs';

const stroke = makeStroke(
    pointsArray,
    '#ff00ff', // color
    5,         // size
    0.8,       // opacity
    'taper'    // style: 'flat' | 'taper' | 'taperBoth' | 'flick'
);
```

### 🌊 Use Noise for Organic Textures
Straight lines are boring. Add `noise2d` to coordinates for natural variation.
```javascript
import { noise2d } from './primitives/helpers.mjs';

// Distort a line
const noiseVal = noise2d(x * 0.01, y * 0.01);
y += noiseVal * 20;
```

## 3. Advanced Composition

### 🏗️ Mix Custom Generators with Primitives
You don't have to build everything from scratch. Import primitives inside your stroke generator.
```javascript
import { getPrimitive } from './primitives/index.mjs';

// Get the L-System generator
const lsys = await getPrimitive('lSystem');

// Generate strokes
const treeStrokes = lsys({
    x: 0, y: 0,
    rule: 'F[+F]F[-F]F',
    depth: 4
});

// Add them to your custom strokes array
allStrokes.push(...treeStrokes);
```

### 📦 Smart Batching (Automatic Throttling)

Sending too fast triggers rate limits. The `sendStrokes` helper now has **smart throttling** built-in. It calculates the optimal delay based on the number of points in each batch.

```javascript
import { sendStrokes } from './scripts/connection.mjs';

// Automatically throttles based on 2000 points/sec limit
await sendStrokes(ws, allStrokes, {
    batchSize: 100,
    targetPointsPerSec: 2000 // Default, adjust if needed
});
```

If you need a specific fixed delay, you can still force it:
```javascript
// Force 1 second delay between batches
await sendStrokes(ws, allStrokes, { delayMs: 1000 });
```

## 4. Troubleshooting

- **"WebSocket 400 Bad Request"**: Your token might be expired. Run `clawdraw auth` or check `getToken()`.
- **"Rate Limited"**: You are sending too fast. Increase `delayMs` in `sendStrokes`.
- **"Stroke Too Large"**: A single stroke has >5000 points. Use `splitIntoStrokes()` helper.
