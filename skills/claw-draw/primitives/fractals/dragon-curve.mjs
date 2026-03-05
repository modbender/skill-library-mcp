/**
 * Dragon Curve — Heighway dragon via iterative fold sequence.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, splitIntoStrokes, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'dragonCurve',
  description: 'Heighway dragon fractal curve via L-system iterative fold sequence',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    size:          { type: 'number', required: false, default: 300, description: 'Fit size' },
    iterations:    { type: 'number', required: false, default: 12, description: 'Fold iterations (1-16)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width' },
    opacity:       { type: 'number', required: false, default: 0.8, description: 'Stroke opacity' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'flat', description: 'Pressure style' },
  },
};

export function dragonCurve(cx, cy, size, iterations, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  size = clamp(Number(size) || 300, 50, 800);
  iterations = clamp(Math.round(Number(iterations) || 12), 1, 16);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.8, 0.01, 1);

  // Build fold sequence: at each iteration, append reversed/flipped copy with a R in the middle
  // 0=Right, 1=Left
  let turns = [0];
  for (let i = 1; i < iterations; i++) {
    const mid = [0]; // Right turn at fold point
    const reversed = [];
    for (let j = turns.length - 1; j >= 0; j--) {
      reversed.push(turns[j] === 0 ? 1 : 0);
    }
    turns = turns.concat(mid, reversed);
  }

  // Walk the fold sequence to generate points
  const dirs = [[1, 0], [0, -1], [-1, 0], [0, 1]]; // R, U, L, D
  let dir = 0;
  const points = [{ x: 0, y: 0 }];
  const stepLen = 1;

  for (let i = 0; i < turns.length; i++) {
    if (turns[i] === 0) {
      dir = (dir + 1) % 4; // Turn right
    } else {
      dir = (dir + 3) % 4; // Turn left
    }
    const last = points[points.length - 1];
    points.push({
      x: last.x + dirs[dir][0] * stepLen,
      y: last.y + dirs[dir][1] * stepLen,
    });
  }

  // Scale and center
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const p of points) {
    if (p.x < minX) minX = p.x;
    if (p.x > maxX) maxX = p.x;
    if (p.y < minY) minY = p.y;
    if (p.y > maxY) maxY = p.y;
  }
  const rangeX = maxX - minX || 1;
  const rangeY = maxY - minY || 1;
  const scale = size / Math.max(rangeX, rangeY);
  const midX = (minX + maxX) / 2;
  const midY = (minY + maxY) / 2;
  const mapped = points.map(p => ({
    x: cx + (p.x - midX) * scale,
    y: cy + (p.y - midY) * scale,
  }));

  // Split into colored segments
  const numSegments = Math.min(100, Math.ceil(mapped.length / 50));
  const result = [];
  const chunkSize = Math.ceil(mapped.length / numSegments);

  for (let i = 0; i < numSegments && result.length < 200; i++) {
    const start = i * chunkSize;
    const end = Math.min(start + chunkSize + 1, mapped.length);
    const pts = mapped.slice(start, end);
    if (pts.length < 2) continue;
    const t = i / Math.max(numSegments - 1, 1);
    const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, col, brushSize, opacity, pressureStyle));
  }

  return result.slice(0, 200);
}
