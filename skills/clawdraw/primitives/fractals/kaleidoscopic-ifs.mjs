/**
 * Kaleidoscopic IFS — chaos game with kaleidoscopic symmetry folding.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'kaleidoscopicIfs',
  description: 'Chaos game iterated function system with kaleidoscopic symmetry',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 150, description: 'Fit radius' },
    symmetry:      { type: 'number', required: false, default: 6, description: 'Fold symmetry order' },
    transforms:    { type: 'number', required: false, default: 3, description: 'Number of IFS transforms' },
    iterations:    { type: 'number', required: false, default: 8000, description: 'Chaos game iterations' },
    numStrokes:    { type: 'number', required: false, default: 80, description: 'Stroke segments' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width' },
    opacity:       { type: 'number', required: false, default: 0.8, description: 'Stroke opacity' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

export function kaleidoscopicIfs(cx, cy, radius, symmetry, transforms, iterations, numStrokes, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 150, 20, 500);
  symmetry = clamp(Math.round(Number(symmetry) || 6), 2, 24);
  transforms = clamp(Math.round(Number(transforms) || 3), 2, 8);
  iterations = clamp(Math.round(Number(iterations) || 8000), 100, 50000);
  numStrokes = clamp(Math.round(Number(numStrokes) || 80), 1, 200);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.8, 0.01, 1);

  // Deterministic seeded random for reproducible transforms
  let seed = symmetry * 1337 + transforms * 7919;
  function srand() {
    seed = (seed * 16807 + 0) % 2147483647;
    return (seed - 1) / 2147483646;
  }

  // Generate random affine transforms
  const xforms = [];
  for (let i = 0; i < transforms; i++) {
    const scale = 0.3 + srand() * 0.4;
    const angle = srand() * Math.PI * 2;
    const cosA = Math.cos(angle) * scale;
    const sinA = Math.sin(angle) * scale;
    const tx = (srand() - 0.5) * 0.8;
    const ty = (srand() - 0.5) * 0.8;
    xforms.push({ cosA, sinA, tx, ty });
  }

  const sectorAngle = (Math.PI * 2) / symmetry;

  // Chaos game iteration
  const rawPoints = [];
  let x = 0.1, y = 0.1;

  // Skip initial transient
  for (let i = 0; i < 20; i++) {
    const ti = Math.floor(srand() * transforms);
    const xf = xforms[ti];
    const nx = xf.cosA * x - xf.sinA * y + xf.tx;
    const ny = xf.sinA * x + xf.cosA * y + xf.ty;
    x = nx;
    y = ny;
  }

  for (let i = 0; i < iterations; i++) {
    // Pick random transform
    const ti = Math.floor(srand() * transforms);
    const xf = xforms[ti];
    const nx = xf.cosA * x - xf.sinA * y + xf.tx;
    const ny = xf.sinA * x + xf.cosA * y + xf.ty;
    x = nx;
    y = ny;

    // Fold into first sector then replicate with symmetry
    const angle = Math.atan2(y, x);
    const r = Math.sqrt(x * x + y * y);
    // Fold into first sector
    let foldedAngle = ((angle % sectorAngle) + sectorAngle) % sectorAngle;
    // Reflect if in second half of sector
    if (foldedAngle > sectorAngle / 2) {
      foldedAngle = sectorAngle - foldedAngle;
    }

    // Emit one point per symmetry fold
    for (let s = 0; s < symmetry; s++) {
      const sa = foldedAngle + s * sectorAngle;
      rawPoints.push({
        x: r * Math.cos(sa),
        y: r * Math.sin(sa),
      });
    }
  }

  if (rawPoints.length < 2) return [];

  // Scale to fit radius
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const p of rawPoints) {
    if (p.x < minX) minX = p.x;
    if (p.x > maxX) maxX = p.x;
    if (p.y < minY) minY = p.y;
    if (p.y > maxY) maxY = p.y;
  }
  const rangeX = maxX - minX || 1;
  const rangeY = maxY - minY || 1;
  const scale = radius * 2 / Math.max(rangeX, rangeY);
  const mapped = rawPoints.map(p => ({
    x: cx + (p.x - (minX + maxX) / 2) * scale,
    y: cy + (p.y - (minY + maxY) / 2) * scale,
  }));

  // Group into strokes
  const result = [];
  const chunkSize = Math.ceil(mapped.length / numStrokes);
  for (let i = 0; i < numStrokes && result.length < 200; i++) {
    const start = i * chunkSize;
    const end = Math.min(start + chunkSize + 1, mapped.length);
    const pts = mapped.slice(start, end);
    if (pts.length < 2) continue;
    // Cap points per stroke at 4990
    const capped = pts.length > 4990 ? pts.slice(0, 4990) : pts;
    // Color by angle from center for distributed palette spread
    let avgX = 0, avgY = 0;
    for (const p of capped) { avgX += p.x; avgY += p.y; }
    avgX /= capped.length;
    avgY /= capped.length;
    const t = (Math.atan2(avgY - cy, avgX - cx) / (2 * Math.PI) + 0.5) % 1.0;
    const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(capped, col, brushSize, opacity, pressureStyle));
  }
  return result.slice(0, 200);
}
