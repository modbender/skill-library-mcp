/**
 * Game of Life — Conway's cellular automaton rendered as filled cell squares.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'gameOfLife',
  description: "Conway's Game of Life cellular automaton with R-pentomino seed",
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    width:         { type: 'number', required: false, default: 300, description: 'Grid width in pixels' },
    height:        { type: 'number', required: false, default: 300, description: 'Grid height in pixels' },
    generations:   { type: 'number', required: false, default: 200, description: 'Simulation generations' },
    cellSize:      { type: 'number', required: false, default: 5, description: 'Cell size in pixels' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width' },
    opacity:       { type: 'number', required: false, default: 0.7, description: 'Stroke opacity' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'flat', description: 'Pressure style' },
  },
};

export function gameOfLife(cx, cy, width, height, generations, cellSize, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 50, 800);
  height = clamp(Number(height) || 300, 50, 800);
  generations = clamp(Math.round(Number(generations) || 200), 10, 500);
  cellSize = clamp(Number(cellSize) || 5, 2, 20);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.7, 0.01, 1);

  const cols = Math.floor(width / cellSize);
  const rows = Math.floor(height / cellSize);

  // Initialize grid
  let grid = new Uint8Array(cols * rows);
  const idx = (c, r) => ((r % rows + rows) % rows) * cols + ((c % cols + cols) % cols);

  // Seed: R-pentomino at center
  const mc = Math.floor(cols / 2);
  const mr = Math.floor(rows / 2);
  const rPentomino = [[1, 0], [2, 0], [0, 1], [1, 1], [1, 2]];
  for (const [dc, dr] of rPentomino) {
    grid[idx(mc + dc, mr + dr)] = 1;
  }

  // Also seed some gliders for visual interest
  const glider = [[1, 0], [2, 1], [0, 2], [1, 2], [2, 2]];
  for (const [dc, dr] of glider) {
    grid[idx(5 + dc, 5 + dr)] = 1;
    grid[idx(cols - 10 + dc, rows - 10 + dr)] = 1;
    grid[idx(5 + dc, rows - 10 + dr)] = 1;
  }

  // Track first generation each cell becomes alive (for coloring)
  const birthGen = new Float32Array(cols * rows).fill(-1);

  // Run simulation
  for (let gen = 0; gen < generations; gen++) {
    const next = new Uint8Array(cols * rows);
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        let neighbors = 0;
        for (let dr = -1; dr <= 1; dr++) {
          for (let dc = -1; dc <= 1; dc++) {
            if (dr === 0 && dc === 0) continue;
            neighbors += grid[idx(c + dc, r + dr)];
          }
        }
        const alive = grid[idx(c, r)];
        if (alive && (neighbors === 2 || neighbors === 3)) {
          next[idx(c, r)] = 1;
        } else if (!alive && neighbors === 3) {
          next[idx(c, r)] = 1;
          if (birthGen[idx(c, r)] < 0) birthGen[idx(c, r)] = gen;
        }
      }
    }
    grid = next;
  }

  // Render live cells: draw horizontal runs of consecutive cells as strokes
  const ox = cx - width / 2;
  const oy = cy - height / 2;
  const result = [];

  // Collect all live cells grouped by row
  for (let r = 0; r < rows && result.length < 198; r++) {
    let runStart = -1;
    for (let c = 0; c <= cols; c++) {
      const alive = c < cols && grid[idx(c, r)];
      if (alive && runStart < 0) {
        runStart = c;
      } else if (!alive && runStart >= 0) {
        // End of a horizontal run: draw connected cell squares
        const pts = [];
        for (let rc = runStart; rc < c; rc++) {
          const x0 = ox + rc * cellSize;
          const y0 = oy + r * cellSize;
          const s = cellSize * 0.9;
          // Draw square for this cell
          pts.push({ x: x0, y: y0 });
          pts.push({ x: x0 + s, y: y0 });
          pts.push({ x: x0 + s, y: y0 + s });
          pts.push({ x: x0, y: y0 + s });
          pts.push({ x: x0, y: y0 });
        }
        if (pts.length >= 2 && result.length < 200) {
          // Color by birth generation of first cell in run
          const gen = birthGen[idx(runStart, r)];
          const t = gen >= 0 ? clamp(gen / generations, 0, 1) : 0.5;
          const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
          const capped = pts.length > 4990 ? pts.slice(0, 4990) : pts;
          result.push(makeStroke(capped, col, brushSize, opacity, pressureStyle));
        }
        runStart = -1;
      }
    }
  }

  return result.slice(0, 200);
}
