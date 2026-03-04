/**
 * Wave Function Collapse — Simplified WFC with pipe/maze tileset.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'waveFunctionCollapse',
  description: 'Simplified wave function collapse with pipe/maze tileset',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    width:         { type: 'number', required: false, default: 280, description: 'Pattern width' },
    height:        { type: 'number', required: false, default: 280, description: 'Pattern height' },
    tileSize:      { type: 'number', required: false, default: 25, description: 'Tile size (10-60)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

// Tile edges: N, E, S, W — 0 = closed, 1 = open
const TILES = [
  { name: 'empty',  edges: [0, 0, 0, 0], draw: () => [] },
  { name: 'hpipe',  edges: [0, 1, 0, 1], draw: (x, y, s) => [[{x: x, y: y + s/2}, {x: x + s, y: y + s/2}]] },
  { name: 'vpipe',  edges: [1, 0, 1, 0], draw: (x, y, s) => [[{x: x + s/2, y: y}, {x: x + s/2, y: y + s}]] },
  { name: 'cross',  edges: [1, 1, 1, 1], draw: (x, y, s) => [
    [{x: x, y: y + s/2}, {x: x + s, y: y + s/2}],
    [{x: x + s/2, y: y}, {x: x + s/2, y: y + s}],
  ]},
  // Corners: NE, SE, SW, NW
  { name: 'cNE', edges: [1, 1, 0, 0], draw: (x, y, s) => {
    const pts = [];
    for (let i = 0; i <= 6; i++) { const a = -Math.PI/2 + (Math.PI/2) * i/6; pts.push({x: x + s - s/2*Math.cos(a), y: y + s/2*Math.sin(a) + s/2}); }
    // Approximate: connect top-center to right-center via arc
    return [[{x: x + s/2, y: y}, ...arc(x + s/2, y + s/2, s/2, -Math.PI/2, 0, 6), {x: x + s, y: y + s/2}]];
  }},
  { name: 'cSE', edges: [0, 1, 1, 0], draw: (x, y, s) => [
    [{x: x + s, y: y + s/2}, ...arc(x + s/2, y + s/2, s/2, 0, Math.PI/2, 6), {x: x + s/2, y: y + s}],
  ]},
  { name: 'cSW', edges: [0, 0, 1, 1], draw: (x, y, s) => [
    [{x: x + s/2, y: y + s}, ...arc(x + s/2, y + s/2, s/2, Math.PI/2, Math.PI, 6), {x: x, y: y + s/2}],
  ]},
  { name: 'cNW', edges: [1, 0, 0, 1], draw: (x, y, s) => [
    [{x: x, y: y + s/2}, ...arc(x + s/2, y + s/2, s/2, Math.PI, Math.PI * 1.5, 6), {x: x + s/2, y: y}],
  ]},
  // T-junctions: open on 3 sides
  { name: 'tN', edges: [1, 1, 0, 1], draw: (x, y, s) => [
    [{x: x, y: y + s/2}, {x: x + s, y: y + s/2}],
    [{x: x + s/2, y: y}, {x: x + s/2, y: y + s/2}],
  ]},
  { name: 'tE', edges: [1, 1, 1, 0], draw: (x, y, s) => [
    [{x: x + s/2, y: y}, {x: x + s/2, y: y + s}],
    [{x: x + s/2, y: y + s/2}, {x: x + s, y: y + s/2}],
  ]},
  { name: 'tS', edges: [0, 1, 1, 1], draw: (x, y, s) => [
    [{x: x, y: y + s/2}, {x: x + s, y: y + s/2}],
    [{x: x + s/2, y: y + s/2}, {x: x + s/2, y: y + s}],
  ]},
  { name: 'tW', edges: [1, 0, 1, 1], draw: (x, y, s) => [
    [{x: x + s/2, y: y}, {x: x + s/2, y: y + s}],
    [{x: x, y: y + s/2}, {x: x + s/2, y: y + s/2}],
  ]},
];

function arc(acx, acy, r, startA, endA, steps) {
  const pts = [];
  for (let i = 1; i < steps; i++) {
    const a = startA + (endA - startA) * i / steps;
    pts.push({ x: acx + r * Math.cos(a), y: acy + r * Math.sin(a) });
  }
  return pts;
}

// Opposite direction index: N<->S, E<->W
const OPP = [2, 3, 0, 1];

export function waveFunctionCollapse(cx, cy, width, height, tileSize, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 280, 50, 800);
  height = clamp(Number(height) || 280, 50, 800);
  tileSize = clamp(Math.round(Number(tileSize) || 25), 10, 60);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const gridCols = Math.floor(width / tileSize);
  const gridRows = Math.floor(height / tileSize);
  const numTiles = TILES.length;

  // Simple seeded RNG
  let seed = 42;
  const rand = () => { seed = (seed * 16807 + 0) % 2147483647; return (seed - 1) / 2147483646; };

  // Initialize possibilities: each cell can be any tile except empty (index 0)
  // This forces connected pipe/maze patterns
  const possible = [];
  for (let i = 0; i < gridCols * gridRows; i++) {
    const set = new Set();
    for (let t = 0; t < numTiles; t++) set.add(t);
    possible.push(set);
  }

  const collapsed = new Int8Array(gridCols * gridRows).fill(-1);

  const idx = (gx, gy) => gy * gridCols + gx;
  const neighbors = (gx, gy) => [
    [gx, gy - 1, 0], // N
    [gx + 1, gy, 1], // E
    [gx, gy + 1, 2], // S
    [gx - 1, gy, 3], // W
  ];

  // WFC loop
  for (let iter = 0; iter < gridCols * gridRows; iter++) {
    // Find cell with lowest entropy (fewest possibilities, not yet collapsed)
    let minEntropy = Infinity;
    let bestIdx = -1;
    for (let i = 0; i < gridCols * gridRows; i++) {
      if (collapsed[i] >= 0) continue;
      const e = possible[i].size;
      if (e === 0) continue;
      if (e < minEntropy || (e === minEntropy && rand() < 0.3)) {
        minEntropy = e;
        bestIdx = i;
      }
    }
    if (bestIdx === -1) break;

    // Collapse: pick random tile from possibilities
    const opts = [...possible[bestIdx]];
    const chosen = opts[Math.floor(rand() * opts.length)];
    collapsed[bestIdx] = chosen;
    possible[bestIdx] = new Set([chosen]);

    // Propagate constraints
    const stack = [bestIdx];
    const inStack = new Set(stack);
    while (stack.length > 0) {
      const ci = stack.pop();
      inStack.delete(ci);
      const cgx = ci % gridCols;
      const cgy = Math.floor(ci / gridCols);

      for (const [nx, ny, dir] of neighbors(cgx, cgy)) {
        if (nx < 0 || nx >= gridCols || ny < 0 || ny >= gridRows) continue;
        const ni = idx(nx, ny);
        if (collapsed[ni] >= 0) continue;

        const oppDir = OPP[dir];
        const validEdges = new Set();
        for (const t of possible[ci]) {
          validEdges.add(TILES[t].edges[dir]);
        }

        const before = possible[ni].size;
        for (const t of [...possible[ni]]) {
          if (!validEdges.has(TILES[t].edges[oppDir])) {
            possible[ni].delete(t);
          }
        }

        if (possible[ni].size < before && !inStack.has(ni)) {
          stack.push(ni);
          inStack.add(ni);
        }
      }
    }
  }

  // Draw the collapsed grid
  const result = [];
  const hw = width / 2;
  const hh = height / 2;

  for (let gy = 0; gy < gridRows && result.length < 195; gy++) {
    for (let gx = 0; gx < gridCols && result.length < 195; gx++) {
      const tIdx = collapsed[idx(gx, gy)];
      if (tIdx < 0) continue;

      const tile = TILES[tIdx];
      const tx = cx - hw + gx * tileSize;
      const ty = cy - hh + gy * tileSize;
      const segments = tile.draw(tx, ty, tileSize);

      // Merge all segments of a tile into one stroke (1 stroke per tile)
      const allPts = [];
      for (const seg of segments) {
        if (seg.length < 2) continue;
        for (const p of seg) allPts.push(p);
      }
      if (allPts.length < 2) continue;
      const t = palette ? (gy * gridCols + gx) / Math.max(1, gridCols * gridRows - 1) : 0;
      const c = palette ? samplePalette(palette, t) : (color || '#ffffff');
      result.push(makeStroke(allPts, c, brushSize, opacity, pressureStyle));
    }
  }

  return result.slice(0, 200);
}
