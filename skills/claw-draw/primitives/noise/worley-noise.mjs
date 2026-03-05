/**
 * Worley Noise — cellular/Voronoi distance field contour lines.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'worleyNoise',
  description: 'Worley (cellular) noise with F1/F2 distance field contour extraction',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    width:         { type: 'number', required: false, default: 350, description: 'Pattern width' },
    height:        { type: 'number', required: false, default: 350, description: 'Pattern height' },
    numCells:      { type: 'number', required: false, default: 15, description: 'Number of Worley seed points (3-50)' },
    mode:          { type: 'string', required: false, default: 'F2minusF1', description: 'Distance mode: F1, F2, or F2minusF1' },
    contours:      { type: 'number', required: false, default: 5, description: 'Number of contour levels (2-12)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

/**
 * Generate Worley noise contour patterns.
 *
 * Places random seed points, computes F1 (nearest) and F2 (second
 * nearest) distances at each grid point, then contours the resulting
 * field. F2-F1 mode highlights cell edges; F1 produces rounded cells;
 * F2 produces more complex patterns.
 *
 * @returns {Array} Array of stroke objects
 */
export function worleyNoise(cx, cy, width, height, numCells, mode, contours, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 350, 50, 800);
  height = clamp(Number(height) || 350, 50, 800);
  numCells = clamp(Math.round(Number(numCells) || 15), 3, 50);
  mode = (typeof mode === 'string' && ['F1', 'F2', 'F2minusF1'].includes(mode)) ? mode : 'F2minusF1';
  contours = clamp(Math.round(Number(contours) || 5), 2, 12);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const hw = width / 2, hh = height / 2;
  const step = Math.max(4, Math.min(width, height) / 50);

  // Generate deterministic seed points distributed across the field
  const seeds = [];
  for (let i = 0; i < numCells; i++) {
    const angle = (i / numCells) * Math.PI * 2 * 3.7 + i * 1.618;
    const r = Math.sqrt((i + 0.5) / numCells) * Math.min(hw, hh) * 0.9;
    seeds.push({
      x: cx + Math.cos(angle) * r,
      y: cy + Math.sin(angle) * r,
    });
  }

  const cols = Math.ceil(width / step) + 1;
  const rows = Math.ceil(height / step) + 1;
  const field = new Float32Array(cols * rows);

  let minVal = Infinity, maxVal = -Infinity;

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const wx = cx - hw + col * step;
      const wy = cy - hh + row * step;

      // Find F1 and F2 distances
      let f1 = Infinity, f2 = Infinity;
      for (const seed of seeds) {
        const dx = wx - seed.x, dy = wy - seed.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < f1) { f2 = f1; f1 = dist; }
        else if (dist < f2) { f2 = dist; }
      }

      let val;
      if (mode === 'F1') val = f1;
      else if (mode === 'F2') val = f2;
      else val = f2 - f1; // F2minusF1

      field[row * cols + col] = val;
      if (val < minVal) minVal = val;
      if (val > maxVal) maxVal = val;
    }
  }

  const result = [];

  // Extract contour lines via marching squares
  for (let level = 0; level < contours && result.length < 200; level++) {
    const threshold = minVal + (level / (contours - 1)) * (maxVal - minVal);
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
          for (const seg of edgePairs[code]) segments.push(seg);
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
