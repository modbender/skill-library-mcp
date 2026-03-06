/**
 * Reaction-Diffusion — Turing pattern contour lines (spots, stripes, labyrinths).
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette, noise2d } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'reactionDiffusion',
  description: 'Turing-inspired reaction-diffusion contour patterns (spots, stripes, labyrinths)',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    width:         { type: 'number', required: false, default: 300, description: 'Pattern width' },
    height:        { type: 'number', required: false, default: 300, description: 'Pattern height' },
    scale:         { type: 'number', required: false, default: 0.04, description: 'Noise scale — smaller = larger blobs (0.005-0.2)' },
    contours:      { type: 'number', required: false, default: 5, description: 'Number of contour levels (2-12)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

/**
 * Generate reaction-diffusion style contour patterns.
 *
 * Uses layered Perlin noise to approximate the look of Gray-Scott
 * reaction-diffusion systems. Contour lines are extracted via marching
 * squares on the noise field, producing organic spots, stripes, and
 * labyrinthine patterns depending on scale.
 *
 * @returns {Array} Array of stroke objects
 */
export function reactionDiffusion(cx, cy, width, height, scale, contours, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 50, 800);
  height = clamp(Number(height) || 300, 50, 800);
  scale = clamp(Number(scale) || 0.04, 0.005, 0.2);
  contours = clamp(Math.round(Number(contours) || 5), 2, 12);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const hw = width / 2, hh = height / 2;
  const step = Math.max(4, Math.min(width, height) / 50);

  // Sample noise field with two octaves for organic feel
  const cols = Math.ceil(width / step) + 1;
  const rows = Math.ceil(height / step) + 1;
  const field = new Float32Array(cols * rows);

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const wx = cx - hw + col * step;
      const wy = cy - hh + row * step;
      const n1 = noise2d(wx * scale, wy * scale);
      const n2 = noise2d(wx * scale * 2.3 + 100, wy * scale * 2.3 + 100) * 0.5;
      field[row * cols + col] = n1 + n2;
    }
  }

  const result = [];

  // Extract contour lines via marching squares
  for (let level = 0; level < contours && result.length < 200; level++) {
    const threshold = -0.8 + (level / (contours - 1)) * 1.6;
    const t = level / (contours - 1);
    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');

    // Scan each cell in the grid
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

        // Interpolation along edges
        const top    = { x: x0 + step * (tl / (tl - tr)), y: y0 };
        const right  = { x: x0 + step, y: y0 + step * (tr / (tr - br)) };
        const bottom = { x: x0 + step * (bl / (bl - br)), y: y0 + step };
        const left   = { x: x0, y: y0 + step * (tl / (tl - bl)) };

        const edgePairs = {
          1: [[left, bottom]], 2: [[bottom, right]], 3: [[left, right]],
          4: [[top, right]], 5: [[top, left], [bottom, right]], 6: [[top, bottom]],
          7: [[top, left]], 8: [[top, left]], 9: [[top, bottom]],
          10: [[top, right], [bottom, left]], 11: [[top, right]],
          12: [[left, right]], 13: [[bottom, right]], 14: [[left, bottom]],
        };

        if (edgePairs[code]) {
          for (const seg of edgePairs[code]) {
            segments.push(seg);
          }
        }
      }
    }

    // Chain nearby segments into longer strokes
    const used = new Set();
    for (let i = 0; i < segments.length && result.length < 200; i++) {
      if (used.has(i)) continue;
      used.add(i);

      const chain = [segments[i][0], segments[i][1]];
      let extended = true;

      while (extended && chain.length < 80) {
        extended = false;
        const tail = chain[chain.length - 1];
        let bestJ = -1, bestD = (step * 1.8) * (step * 1.8);

        for (let j = 0; j < segments.length; j++) {
          if (used.has(j)) continue;
          const dx0 = segments[j][0].x - tail.x, dy0 = segments[j][0].y - tail.y;
          const d0 = dx0 * dx0 + dy0 * dy0;
          if (d0 < bestD) { bestD = d0; bestJ = j; }
        }

        if (bestJ !== -1) {
          used.add(bestJ);
          chain.push(segments[bestJ][1]);
          extended = true;
        }
      }

      if (chain.length >= 3) {
        // Add slight wobble
        const wobbledPts = chain.map(p => ({
          x: p.x + (Math.random() - 0.5) * step * 0.12,
          y: p.y + (Math.random() - 0.5) * step * 0.12,
        }));
        result.push(makeStroke(wobbledPts, c, brushSize, opacity, pressureStyle));
      }
    }
  }

  return result.slice(0, 200);
}
