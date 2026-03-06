/**
 * Langton's Ant — cellular automaton that produces emergent highway patterns.
 *
 * Draws the ant's trail as a continuous path, scaled to fill the canvas.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'langtonsAnt',
  description: 'Langton\'s Ant cellular automaton with emergent highway patterns',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    width:         { type: 'number', required: false, default: 280, description: 'Pattern width' },
    height:        { type: 'number', required: false, default: 280, description: 'Pattern height' },
    steps:         { type: 'number', required: false, default: 11000, description: 'Simulation steps' },
    cellSize:      { type: 'number', required: false, default: 4, description: 'Cell size in pixels (2-20)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

export function langtonsAnt(cx, cy, width, height, steps, cellSize, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 280, 50, 800);
  height = clamp(Number(height) || 280, 50, 800);
  steps = clamp(Math.round(Number(steps) || 11000), 100, 50000);
  cellSize = clamp(Math.round(Number(cellSize) || 4), 2, 20);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  // Size grid to fit the chaotic phase tightly within the canvas
  const gridSize = Math.max(60, Math.ceil(Math.sqrt(steps) * 0.8));
  const gridCols = gridSize;
  const gridRows = gridSize;
  // Cell size that fills the canvas area
  const actualCellSize = Math.min(width, height) / gridSize;
  const grid = new Uint8Array(gridCols * gridRows);

  const ddx = [0, 1, 0, -1];
  const ddy = [-1, 0, 1, 0];

  let antX = Math.floor(gridCols / 2);
  let antY = Math.floor(gridRows / 2);
  let dir = 0;

  // Record the ant's path
  let actualSteps = steps;
  const pathX = new Float64Array(steps + 1);
  const pathY = new Float64Array(steps + 1);
  pathX[0] = antX;
  pathY[0] = antY;

  for (let s = 0; s < steps; s++) {
    const idx = antY * gridCols + antX;
    if (grid[idx] === 0) {
      dir = (dir + 1) & 3;
      grid[idx] = 1;
    } else {
      dir = (dir + 3) & 3;
      grid[idx] = 0;
    }
    const newX = antX + ddx[dir];
    const newY = antY + ddy[dir];
    if (newX < 0 || newX >= gridCols || newY < 0 || newY >= gridRows) {
      actualSteps = s + 1;
      break;
    }
    antX = newX;
    antY = newY;
    pathX[s + 1] = antX;
    pathY[s + 1] = antY;
  }

  // Map grid coordinates to canvas using natural cell spacing
  const hw = width / 2;
  const hh = height / 2;
  const gridCenterX = gridCols / 2;
  const gridCenterY = gridRows / 2;

  // Split path into strokes with natural grid positioning
  const numStrokes = Math.min(190, Math.ceil(actualSteps / 50));
  const ptsPerStroke = Math.ceil((actualSteps + 1) / numStrokes);
  const result = [];

  for (let i = 0; i < numStrokes && result.length < 195; i++) {
    const start = i * ptsPerStroke;
    const end = Math.min(start + ptsPerStroke + 1, actualSteps + 1);
    if (end - start < 2) continue;

    const pts = [];
    for (let s = start; s < end; s++) {
      pts.push({
        x: cx + (pathX[s] - gridCenterX) * actualCellSize,
        y: cy + (pathY[s] - gridCenterY) * actualCellSize,
      });
    }

    const t = palette ? i / numStrokes : 0;
    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, c, brushSize, opacity, pressureStyle));
  }

  return result.slice(0, 200);
}
