/**
 * Hopalong Attractor — Martin's hopalong map producing intricate orbital patterns.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'hopalongAttractor',
  description: 'Martin hopalong map producing intricate orbital scatter patterns',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 150, description: 'Fit radius' },
    a:             { type: 'number', required: false, default: 1.1, description: 'Parameter a' },
    b:             { type: 'number', required: false, default: 2.0, description: 'Parameter b' },
    c:             { type: 'number', required: false, default: 0.5, description: 'Parameter c' },
    numPoints:     { type: 'number', required: false, default: 5000, description: 'Iteration count' },
    numStrokes:    { type: 'number', required: false, default: 80, description: 'Stroke segments' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width' },
    opacity:       { type: 'number', required: false, default: 0.8, description: 'Stroke opacity' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

export function hopalongAttractor(cx, cy, radius, a, b, c, numPoints, numStrokes, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 150, 20, 500);
  a = Number(a) || 1.1;
  b = Number(b) || 2.0;
  c = Number(c) || 0.5;
  numPoints = clamp(Math.round(Number(numPoints) || 5000), 100, 50000);
  numStrokes = clamp(Math.round(Number(numStrokes) || 80), 1, 200);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.8, 0.01, 1);

  const rawPoints = [];
  let x = 0, y = 0;
  for (let i = 0; i < numPoints; i++) {
    const sign = x < 0 ? -1 : (x > 0 ? 1 : 0);
    const nx = y - sign * Math.sqrt(Math.abs(b * x - c));
    const ny = a - x;
    rawPoints.push({ x: nx, y: ny });
    x = nx;
    y = ny;
  }

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

  // Color by angle from center for distributed palette spread
  const result = [];
  const chunkSize = Math.ceil(mapped.length / numStrokes);
  for (let i = 0; i < numStrokes && result.length < 200; i++) {
    const start = i * chunkSize;
    const end = Math.min(start + chunkSize + 1, mapped.length);
    const pts = mapped.slice(start, end);
    if (pts.length < 2) continue;
    let avgX = 0, avgY = 0;
    for (const p of pts) { avgX += p.x; avgY += p.y; }
    avgX /= pts.length;
    avgY /= pts.length;
    const t = palette ? (Math.atan2(avgY - cy, avgX - cx) / (2 * Math.PI) + 0.5) % 1.0 : 0;
    const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, col, brushSize, opacity, pressureStyle));
  }
  return result.slice(0, 200);
}
