# Symmetry System Reference

The symmetry system generates reflected or rotated copies of strokes around a center point.

## Modes

| Mode | Syntax | Copies | Total Strokes |
|------|--------|--------|---------------|
| None | `none` | 0 | 1x original |
| Vertical | `vertical` | 1 (X-flipped) | 2x |
| Horizontal | `horizontal` | 1 (Y-flipped) | 2x |
| Both | `both` | 3 (X, Y, XY-flipped) | 4x |
| Radial | `radial:N` | N-1 rotated copies | Nx |

## How Each Mode Works

**Vertical**: Mirrors strokes across the Y axis at the symmetry center. Every stroke drawn on the right side gets a copy on the left side (and vice versa).

**Horizontal**: Mirrors strokes across the X axis at the symmetry center. Every stroke drawn in the top half gets a copy in the bottom half.

**Both**: Four-fold symmetry. Combines vertical and horizontal mirroring plus a diagonal copy (both X and Y flipped). Produces 4 total copies of every stroke.

**Radial:N**: Rotates strokes evenly around the center. `radial:6` creates 6 copies spaced 60 degrees apart. `radial:12` creates 12 copies spaced 30 degrees apart. Produces complex mandala-like patterns.

## Constraint Enforcement

Before generating copies, the system ensures the original stroke's centroid lies in the canonical region:

- **Vertical**: Centroid must be in the right half (x >= centerX). If not, the stroke is reflected.
- **Horizontal**: Centroid must be in the top half (y <= centerY). If not, the stroke is reflected.
- **Both**: Centroid must be in the top-right quadrant. Both vertical and horizontal constraints are applied.
- **Radial:N**: Centroid must be in the first wedge [0, 2pi/N). If not, the entire stroke is rotated into the first wedge.

This means you do not need to carefully position strokes -- the system corrects placement automatically. However, for best results, draw in the primary region.

## Tips

- **Vertical symmetry**: Draw your design on the right half of the center. Good for butterflies, faces, symmetric logos.
- **Horizontal symmetry**: Draw on the top half. Good for reflections in water, top/bottom patterns.
- **Both**: Draw in the top-right quadrant only. Good for snowflakes, four-fold symmetric designs.
- **Radial**: Draw in the first wedge (a narrow pie slice from the center). The smaller the wedge (higher N), the more dramatic the mandala effect. `radial:8` to `radial:16` are good starting points.
- Symmetry multiplies your stroke count. With `radial:12`, 15 strokes become 180. Stay under the 200-stroke batch limit.

## API

```js
import {
  parseSymmetryMode,
  applySymmetry,
  enforceConstraints,
  generateCopies,
} from '../scripts/symmetry.mjs';

// Parse mode string
const { mode, folds } = parseSymmetryMode('radial:8');

// Apply to strokes (mutates originals for constraint enforcement)
const allStrokes = applySymmetry(strokes, mode, folds, centerX, centerY);
```
