/**
 * Gray-Scott — PDE reaction-diffusion contour visualization.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'grayScott',
  description: 'Gray-Scott PDE reaction-diffusion simulation with contour extraction',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    width:         { type: 'number', required: false, default: 350, description: 'Pattern width' },
    height:        { type: 'number', required: false, default: 350, description: 'Pattern height' },
    feed:          { type: 'number', required: false, default: 0.037, description: 'Feed rate (0.01-0.1)' },
    kill:          { type: 'number', required: false, default: 0.06, description: 'Kill rate (0.01-0.1)' },
    iterations:    { type: 'number', required: false, default: 150, description: 'Simulation iterations (50-500)' },
    contours:      { type: 'number', required: false, default: 5, description: 'Number of contour levels (2-12)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

/**
 * Generate Gray-Scott reaction-diffusion contour patterns.
 *
 * Runs a discrete Gray-Scott PDE on a small grid, then extracts
 * contour lines from the V chemical field via marching squares.
 *
 * @returns {Array} Array of stroke objects
 */
export function grayScott(cx, cy, width, height, feed, kill, iterations, contours, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 350, 50, 800);
  height = clamp(Number(height) || 350, 50, 800);
  feed = clamp(Number(feed) || 0.037, 0.01, 0.1);
  kill = clamp(Number(kill) || 0.06, 0.01, 0.1);
  iterations = clamp(Math.round(Number(iterations) || 150), 50, 500);
  contours = clamp(Math.round(Number(contours) || 5), 2, 12);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  // Simulation grid
  const gCols = 60, gRows = 60;
  const Du = 0.16, Dv = 0.08;
  let U = new Float32Array(gCols * gRows);
  let V = new Float32Array(gCols * gRows);
  const nextU = new Float32Array(gCols * gRows);
  const nextV = new Float32Array(gCols * gRows);

  // Initialize: U=1 everywhere, V=0, seed spots with V=0.5
  for (let i = 0; i < gCols * gRows; i++) { U[i] = 1; V[i] = 0; }

  // Seed a few spots deterministically based on grid center
  const seeds = [
    [Math.floor(gCols * 0.4), Math.floor(gRows * 0.4)],
    [Math.floor(gCols * 0.6), Math.floor(gRows * 0.6)],
    [Math.floor(gCols * 0.3), Math.floor(gRows * 0.6)],
    [Math.floor(gCols * 0.6), Math.floor(gRows * 0.3)],
    [Math.floor(gCols * 0.5), Math.floor(gRows * 0.5)],
  ];
  for (const [sx, sy] of seeds) {
    for (let dy = -2; dy <= 2; dy++) {
      for (let dx = -2; dx <= 2; dx++) {
        const nx = clamp(sx + dx, 0, gCols - 1);
        const ny = clamp(sy + dy, 0, gRows - 1);
        V[ny * gCols + nx] = 0.5;
        U[ny * gCols + nx] = 0.5;
      }
    }
  }

  // Run simulation
  for (let iter = 0; iter < iterations; iter++) {
    for (let r = 0; r < gRows; r++) {
      for (let c = 0; c < gCols; c++) {
        const idx = r * gCols + c;
        const rUp = r > 0 ? r - 1 : gRows - 1;
        const rDn = r < gRows - 1 ? r + 1 : 0;
        const cLt = c > 0 ? c - 1 : gCols - 1;
        const cRt = c < gCols - 1 ? c + 1 : 0;

        const lapU = U[rUp * gCols + c] + U[rDn * gCols + c] + U[r * gCols + cLt] + U[r * gCols + cRt] - 4 * U[idx];
        const lapV = V[rUp * gCols + c] + V[rDn * gCols + c] + V[r * gCols + cLt] + V[r * gCols + cRt] - 4 * V[idx];

        const uvv = U[idx] * V[idx] * V[idx];
        nextU[idx] = U[idx] + Du * lapU - uvv + feed * (1 - U[idx]);
        nextV[idx] = V[idx] + Dv * lapV + uvv - (feed + kill) * V[idx];
      }
    }
    // Swap buffers
    const tmpU = U; U = nextU; nextU.set(tmpU); // reuse array
    const tmpV = V; V = nextV; nextV.set(tmpV);
  }

  // Resample V field onto rendering grid
  const hw = width / 2, hh = height / 2;
  const step = Math.max(4, Math.min(width, height) / 50);
  const cols = Math.ceil(width / step) + 1;
  const rows = Math.ceil(height / step) + 1;
  const field = new Float32Array(cols * rows);

  let minVal = Infinity, maxVal = -Infinity;

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      // Map rendering grid position to simulation grid
      const gx = (col / (cols - 1)) * (gCols - 1);
      const gy = (row / (rows - 1)) * (gRows - 1);
      const gi = clamp(Math.floor(gx), 0, gCols - 2);
      const gj = clamp(Math.floor(gy), 0, gRows - 2);
      const fx = gx - gi, fy = gy - gj;

      // Bilinear interpolation
      const v00 = V[gj * gCols + gi];
      const v10 = V[gj * gCols + gi + 1];
      const v01 = V[(gj + 1) * gCols + gi];
      const v11 = V[(gj + 1) * gCols + gi + 1];
      const val = v00 * (1 - fx) * (1 - fy) + v10 * fx * (1 - fy) + v01 * (1 - fx) * fy + v11 * fx * fy;

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
