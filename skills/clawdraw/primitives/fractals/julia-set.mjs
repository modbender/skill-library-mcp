/**
 * Julia Set — escape-time fractal with contour lines via marching squares.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'juliaSet',
  description: 'Julia set escape-time fractal with marching-squares contour lines',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X on canvas' },
    cy:            { type: 'number', required: true, description: 'Center Y on canvas' },
    width:         { type: 'number', required: false, default: 300, description: 'Pattern width' },
    height:        { type: 'number', required: false, default: 300, description: 'Pattern height' },
    cReal:         { type: 'number', required: false, default: -0.7, description: 'Real part of c constant' },
    cImag:         { type: 'number', required: false, default: 0.27015, description: 'Imaginary part of c constant' },
    maxIter:       { type: 'number', required: false, default: 50, description: 'Max iterations (10-200)' },
    contours:      { type: 'number', required: false, default: 10, description: 'Number of contour levels (2-20)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

export function juliaSet(cx, cy, width, height, cReal, cImag, maxIter, contours, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 50, 800);
  height = clamp(Number(height) || 300, 50, 800);
  cReal = (cReal === undefined || cReal === null) ? -0.7 : Number(cReal);
  cImag = (cImag === undefined || cImag === null) ? 0.27015 : Number(cImag);
  maxIter = clamp(Math.round(Number(maxIter) || 50), 10, 200);
  contours = clamp(Math.round(Number(contours) || 10), 2, 20);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const hw = width / 2, hh = height / 2;
  const step = Math.max(3, Math.min(width, height) / 80);
  const cols = Math.ceil(width / step) + 1;
  const rows = Math.ceil(height / step) + 1;
  const viewRange = 1.8;

  // Compute escape-time field for Julia set (z iterates, c is fixed)
  const field = new Float32Array(cols * rows);
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const px = cx - hw + col * step;
      const py = cy - hh + row * step;
      // Map pixel to complex plane
      let zr = (px - cx) / (hw) * viewRange;
      let zi = (py - cy) / (hh) * viewRange;

      let iter = 0;
      while (iter < maxIter && zr * zr + zi * zi <= 4) {
        const tmp = zr * zr - zi * zi + cReal;
        zi = 2 * zr * zi + cImag;
        zr = tmp;
        iter++;
      }

      // Smooth iteration count
      if (iter < maxIter) {
        const log2 = Math.log(2);
        const modulus = Math.sqrt(zr * zr + zi * zi);
        field[row * cols + col] = iter + 1 - Math.log(Math.log(modulus)) / log2;
      } else {
        field[row * cols + col] = maxIter;
      }
    }
  }

  const result = [];

  // Extract contour lines via marching squares
  for (let level = 0; level < contours && result.length < 200; level++) {
    const threshold = 2 + (level / (contours - 1)) * (maxIter * 0.7);
    const t = level / (contours - 1);
    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');

    const segments = [];
    for (let row = 0; row < rows - 1; row++) {
      for (let col = 0; col < cols - 1; col++) {
        const tl = field[row * cols + col] - threshold;
        const tr = field[row * cols + col + 1] - threshold;
        const br = field[(row + 1) * cols + col + 1] - threshold;
        const bl = field[(row + 1) * cols + col] - threshold;

        const code = (tl > 0 ? 8 : 0) | (tr > 0 ? 4 : 0) | (br > 0 ? 2 : 0) | (bl > 0 ? 1 : 0);
        if (code === 0 || code === 15) continue;

        const x0 = cx - hw + col * step;
        const y0 = cy - hh + row * step;

        const top    = { x: x0 + step * clamp(tl / (tl - tr), 0, 1), y: y0 };
        const right  = { x: x0 + step, y: y0 + step * clamp(tr / (tr - br), 0, 1) };
        const bottom = { x: x0 + step * clamp(bl / (bl - br), 0, 1), y: y0 + step };
        const left   = { x: x0, y: y0 + step * clamp(tl / (tl - bl), 0, 1) };

        const edgePairs = {
          1: [[left, bottom]], 2: [[bottom, right]], 3: [[left, right]],
          4: [[top, right]], 5: [[top, left], [bottom, right]], 6: [[top, bottom]],
          7: [[top, left]], 8: [[top, left]], 9: [[top, bottom]],
          10: [[top, right], [bottom, left]], 11: [[top, right]],
          12: [[left, right]], 13: [[bottom, right]], 14: [[left, bottom]],
        };

        if (edgePairs[code]) {
          for (const seg of edgePairs[code]) segments.push(seg);
        }
      }
    }

    // Chain segments into strokes
    const used = new Set();
    for (let i = 0; i < segments.length && result.length < 200; i++) {
      if (used.has(i)) continue;
      used.add(i);

      const chain = [segments[i][0], segments[i][1]];
      let extended = true;
      while (extended && chain.length < 100) {
        extended = false;
        const tail = chain[chain.length - 1];
        let bestJ = -1, bestD = (step * 1.8) * (step * 1.8);
        for (let j = 0; j < segments.length; j++) {
          if (used.has(j)) continue;
          const dx = segments[j][0].x - tail.x, dy = segments[j][0].y - tail.y;
          const d = dx * dx + dy * dy;
          if (d < bestD) { bestD = d; bestJ = j; }
        }
        if (bestJ !== -1) {
          used.add(bestJ);
          chain.push(segments[bestJ][1]);
          extended = true;
        }
      }

      if (chain.length >= 3) {
        result.push(makeStroke(chain, c, brushSize, opacity, pressureStyle));
      }
    }
  }

  return result.slice(0, 200);
}
