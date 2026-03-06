/**
 * Schotter — Georg Nees "Gravel" generative art: grid of squares with increasing disorder.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette, noise2d } from './helpers.mjs';

export const METADATA = {
  name: 'schotter',
  description: 'Georg Nees Schotter — grid of squares with increasing random disorder',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    width:         { type: 'number', required: false, default: 300, description: 'Grid width' },
    height:        { type: 'number', required: false, default: 300, description: 'Grid height' },
    cols:          { type: 'number', required: false, default: 12, description: 'Number of columns (2-30)' },
    rows:          { type: 'number', required: false, default: 12, description: 'Number of rows (2-30)' },
    decay:         { type: 'number', required: false, default: 1.0, description: 'Disorder increase rate (0.1-3)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

export function schotter(cx, cy, width, height, cols, rows, decay, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 50, 800);
  height = clamp(Number(height) || 300, 50, 800);
  cols = clamp(Math.round(Number(cols) || 12), 2, 30);
  rows = clamp(Math.round(Number(rows) || 12), 2, 30);
  decay = clamp(Number(decay) || 1.0, 0.1, 3);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  // Cap grid to stay within 200 strokes
  const totalSquares = cols * rows;
  if (totalSquares > 200) {
    const scale = Math.sqrt(200 / totalSquares);
    cols = Math.max(2, Math.floor(cols * scale));
    rows = Math.max(2, Math.floor(rows * scale));
  }

  const cellW = width / cols;
  const cellH = height / rows;
  const hw = width / 2;
  const hh = height / 2;

  const result = [];

  for (let row = 0; row < rows; row++) {
    const t = row / Math.max(1, rows - 1);
    const disorder = t * decay;
    const maxRotation = disorder * Math.PI * 0.25;
    const maxJitter = disorder * Math.min(cellW, cellH) * 0.4;

    for (let col = 0; col < cols; col++) {
      const baseCx = cx - hw + col * cellW + cellW / 2;
      const baseCy = cy - hh + row * cellH + cellH / 2;

      // Use noise for deterministic randomness
      const n1 = noise2d(col * 1.7, row * 1.7);
      const n2 = noise2d(col * 1.7 + 50, row * 1.7 + 50);
      const n3 = noise2d(col * 1.7 + 100, row * 1.7 + 100);

      const rotation = n1 * maxRotation;
      const jx = n2 * maxJitter;
      const jy = n3 * maxJitter;

      const scx = baseCx + jx;
      const scy = baseCy + jy;

      const halfW = cellW * 0.45;
      const halfH = cellH * 0.45;
      const cos = Math.cos(rotation);
      const sin = Math.sin(rotation);

      const corners = [
        [-halfW, -halfH],
        [ halfW, -halfH],
        [ halfW,  halfH],
        [-halfW,  halfH],
      ];

      const pts = corners.map(([lx, ly]) => ({
        x: scx + lx * cos - ly * sin,
        y: scy + lx * sin + ly * cos,
      }));
      // Close the square
      pts.push({ x: pts[0].x, y: pts[0].y });

      const ct = palette ? (row * cols + col) / Math.max(1, cols * rows - 1) : 0;
      const c = palette ? samplePalette(palette, ct) : (color || '#ffffff');
      result.push(makeStroke(pts, c, brushSize, opacity, pressureStyle));
    }
  }

  return result.slice(0, 200);
}
