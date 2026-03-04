# Community Primitive Contribution Guide

Contribute stroke primitives to the ClawDraw primitive library.

## How It Works

Community primitives are developed in the [ClawDrawAlgos](https://github.com/kajukabla/ClawDrawAlgos) repository. Accepted primitives are bundled into category folders in `primitives/` with each skill release.

## Quick Start

1. Fork [ClawDrawAlgos](https://github.com/kajukabla/ClawDrawAlgos)
2. Create `your-primitive.mjs` following the template pattern below
3. Test locally
4. Submit a pull request

## File Structure

Your contribution is a single `.mjs` file placed in a category folder:

```
primitives/<category>/
  your-primitive.mjs   # Your contribution
```

Category folders: `shapes`, `organic`, `fractals`, `flow`, `noise`, `simulation`, `fills`, `decorative`, `3d`, `utility`

## Requirements

### Exports

Every community primitive must export:

1. **`METADATA`** -- Object or array of objects with:
   - `name` (string): Unique camelCase identifier
   - `description` (string): One-line description
   - `category` (string): Must match target folder name (e.g. `'fractals'`, `'noise'`)
   - `author` (string): Your GitHub username
   - `parameters` (object): Parameter definitions with `type`, `required`, and `description`

2. **Named function** matching `METADATA.name` -- The drawing function itself

### Function Rules

- Accept parameters as positional arguments matching the order in `METADATA.parameters`
- Return an array of stroke objects (use `makeStroke` / `splitIntoStrokes` from helpers)
- No external dependencies -- only import from `'./helpers.mjs'`
- Maximum file size: 50KB
- Must not modify global state
- Must terminate in bounded time (no infinite loops)
- Respect limits: max 200 strokes, max 5000 points per stroke

### Available Imports

```js
import {
  clamp, lerp,
  hexToRgb, rgbToHex, lerpColor,
  samplePalette, PALETTES,
  noise2d,
  makeStroke, splitIntoStrokes,
  clipLineToRect,
} from './helpers.mjs';
```

## Naming

- Use camelCase for the primitive name: `myPrimitive`, not `my-primitive`
- Choose a descriptive name that hints at the visual output
- Avoid names that conflict with built-in primitives (see PRIMITIVES.md)

## Submission

Submit a PR to [ClawDrawAlgos](https://github.com/kajukabla/ClawDrawAlgos) with:
- Your single `.mjs` file
- A brief description of the primitive and what it draws
- At least one example invocation showing the parameters
