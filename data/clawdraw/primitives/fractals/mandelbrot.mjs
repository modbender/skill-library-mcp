/**
 * Mandelbrot — escape-time fractal contour visualization.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'mandelbrot',
  description: 'Mandelbrot set escape-time fractal with contour lines',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X on canvas' },
    cy:            { type: 'number', required: true, description: 'Center Y on canvas' },
    width:         { type: 'number', required: false, default: 300, description: 'Pattern width' },
    height:        { type: 'number', required: false, default: 300, description: 'Pattern height' },
    maxIter:       { type: 'number', required: false, default: 40, description: 'Max iterations (10-200)' },
    zoom:          { type: 'number', required: false, default: 1, description: 'Zoom level (0.1-100)' },
    centerReal:    { type: 'number', required: false, default: -0.5, description: 'Real center of view in complex plane' },
    centerImag:    { type: 'number', required: false, default: 0, description: 'Imaginary center of view' },
    contours:      { type: 'number', required: false, default: 8, description: 'Number of contour levels (2-20)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

/**
 * Generate Mandelbrot set contour lines.
 *
 * Computes escape-time iteration counts on a grid, then extracts
 * contour lines at evenly spaced iteration thresholds using marching
 * squares. Produces organic, fractal boundary strokes.
 *
 * @returns {Array} Array of stroke objects
 */
export function mandelbrot(cx, cy, width, height, maxIter, zoom, centerReal, centerImag, contours, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 50, 800);
  height = clamp(Number(height) || 300, 50, 800);
  maxIter = clamp(Math.round(Number(maxIter) || 40), 10, 200);
  zoom = clamp(Number(zoom) || 1, 0.1, 100);
  centerReal = (centerReal === undefined || centerReal === null) ? -0.5 : Number(centerReal);
  centerImag = (centerImag === undefined || centerImag === null) ? 0 : Number(centerImag);
  contours = clamp(Math.round(Number(contours) || 8), 2, 20);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const hw = width / 2, hh = height / 2;
  const step = Math.max(3, Math.min(width, height) / 80);
  const cols = Math.ceil(width / step) + 1;
  const rows = Math.ceil(height / step) + 1;
  const scale = 3.0 / (Math.min(width, height) * zoom);

  // Compute escape-time field
  const field = new Float32Array(cols * rows);
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const px = cx - hw + col * step;
      const py = cy - hh + row * step;
      const cReal = centerReal + (px - cx) * scale;
      const cImag = centerImag + (py - cy) * scale;

      let zr = 0, zi = 0;
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
