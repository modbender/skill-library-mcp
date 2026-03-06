/**
 * Lichen Growth — Cyclic cellular automaton drawn as colored cell blocks.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'lichenGrowth',
  description: 'Cyclic cellular automaton rendered as colored cell blocks',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    width:         { type: 'number', required: false, default: 300, description: 'Pattern width' },
    height:        { type: 'number', required: false, default: 300, description: 'Pattern height' },
    states:        { type: 'number', required: false, default: 6, description: 'Number of cell states (3-16)' },
    iterations:    { type: 'number', required: false, default: 30, description: 'Simulation iterations (1-100)' },
    contours:      { type: 'number', required: false, default: 5, description: 'Contour levels (unused, kept for compat)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

export function lichenGrowth(cx, cy, width, height, states, iterations, contours, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 50, 800);
  height = clamp(Number(height) || 300, 50, 800);
  states = clamp(Math.round(Number(states) || 6), 3, 16);
  iterations = clamp(Math.round(Number(iterations) || 30), 1, 100);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const hw = width / 2, hh = height / 2;

  // Use a grid size that fits within 200 strokes (14×14 = 196 cells)
  const gridCols = 14;
  const gridRows = 14;
  const cellW = width / gridCols;
  const cellH = height / gridRows;

  // Deterministic seeded random
  let seed = 73;
  function srand() {
    seed = (seed * 16807 + 0) % 2147483647;
    return (seed - 1) / 2147483646;
  }

  // Initialize grid randomly
  let grid = new Uint8Array(gridCols * gridRows);
  for (let i = 0; i < grid.length; i++) {
    grid[i] = Math.floor(srand() * states);
  }

  // Run cyclic CA: cell advances if any neighbor has the next state
  for (let iter = 0; iter < iterations; iter++) {
    const next = new Uint8Array(grid);
    for (let r = 0; r < gridRows; r++) {
      for (let c = 0; c < gridCols; c++) {
        const cur = grid[r * gridCols + c];
        const target = (cur + 1) % states;
        let found = false;
        // Check 8 neighbors (Moore neighborhood)
        for (let dr = -1; dr <= 1 && !found; dr++) {
          for (let dc = -1; dc <= 1 && !found; dc++) {
            if (dr === 0 && dc === 0) continue;
            const nr = (r + dr + gridRows) % gridRows;
            const nc = (c + dc + gridCols) % gridCols;
            if (grid[nr * gridCols + nc] === target) found = true;
          }
        }
        if (found) next[r * gridCols + c] = target;
      }
    }
    grid = next;
  }

  // Draw each cell as a small filled rectangle (closed polygon stroke)
  const result = [];
  for (let r = 0; r < gridRows && result.length < 198; r++) {
    for (let c = 0; c < gridCols && result.length < 198; c++) {
      const state = grid[r * gridCols + c];
      const t = state / (states - 1);
      const col = palette ? samplePalette(palette, t) : (color || '#ffffff');

      const x0 = cx - hw + c * cellW;
      const y0 = cy - hh + r * cellH;
      const x1 = x0 + cellW;
      const y1 = y0 + cellH;

      // Draw cell as filled rectangle (outline)
      const pts = [
        { x: x0, y: y0 }, { x: x1, y: y0 },
        { x: x1, y: y1 }, { x: x0, y: y1 },
        { x: x0, y: y0 },
      ];
      result.push(makeStroke(pts, col, brushSize, opacity, pressureStyle));
    }
  }

  return result.slice(0, 200);
}
