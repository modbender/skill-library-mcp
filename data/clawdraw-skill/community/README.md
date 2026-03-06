# Community Primitives

User-contributed drawing primitives for ClawDraw agents.

## Adding a New Primitive

1. Copy `_template.mjs` to a new file in this directory
2. Name your file in `lowercase-kebab-case.mjs` (e.g. `spiral-galaxy.mjs`)
3. Implement your drawing primitive

## Requirements

- **Must export `METADATA`** -- object with `name`, `description`, `category`, `author`, and `parameters`
- **Must export a named function** -- matching the `name` in METADATA
- **Must import helpers from `../primitives/helpers.mjs`** -- use `makeStroke`, `splitIntoStrokes`, `clamp`, `lerp`, `noise2d`, etc.
- **No external dependencies** -- only import from the helpers module
- **Function must return an array of stroke objects** -- use `splitIntoStrokes()` or `makeStroke()` to build them
- **Max file size: 50KB**

## File Structure

```
community/
  _template.mjs      # Start here -- copy this file
  README.md           # This file
  your-primitive.mjs  # Your contribution
```

## METADATA Format

```javascript
export const METADATA = {
  name: 'myPrimitive',           // camelCase, unique identifier
  description: 'What it draws',  // short, one line
  category: 'community',         // always 'community'
  author: 'github-username',     // your GitHub handle
  parameters: {
    cx: { type: 'number', required: true, description: 'Center X' },
    cy: { type: 'number', required: true, description: 'Center Y' },
    // additional params...
  },
};
```

## Submitting

1. Fork the repo and create a branch
2. Add your `.mjs` file to this directory
3. Test locally with the CLI: `node clawdraw.mjs draw myPrimitive --cx 0 --cy 0`
4. Submit a PR

## Available Helpers

Imported from `../primitives/helpers.mjs`:

| Function | Description |
|----------|-------------|
| `clamp(v, min, max)` | Clamp a value to a range |
| `lerp(a, b, t)` | Linear interpolation |
| `noise2d(x, y)` | 2D Perlin-style noise (-1 to 1) |
| `makeStroke(points, color, brushSize, opacity, pressureStyle)` | Build a single stroke object |
| `splitIntoStrokes(points, color, brushSize, opacity, pressureStyle)` | Split long point arrays into multiple strokes |
| `hexToRgb(hex)` | Convert hex color to `{r, g, b}` |
| `rgbToHex(r, g, b)` | Convert RGB to hex string |
| `lerpColor(hex1, hex2, t)` | Interpolate between two hex colors |
| `samplePalette(name, t)` | Sample a color from a named palette |
| `simulatePressure(index, total)` | Default pressure curve |
| `getPressureForStyle(index, total, style)` | Pressure curve by style name |
| `clipLineToRect(p0, p1, minX, minY, maxX, maxY)` | Clip a line segment to a rectangle |
