/**
 * Voronoi Noise — organic cellular pattern based on Voronoi tessellation.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, lerp, makeStroke, samplePalette, noise2d } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'voronoiNoise',
  description: 'Organic Voronoi cell noise pattern with hand-drawn edges',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    width:         { type: 'number', required: false, default: 300, description: 'Pattern width' },
    height:        { type: 'number', required: false, default: 300, description: 'Pattern height' },
    numCells:      { type: 'number', required: false, default: 25, description: 'Number of seed points (5-80)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    wobble:        { type: 'number', required: false, default: 0.3, description: 'Hand-drawn wobble amount (0-1)' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

/**
 * Generate a Voronoi cell noise pattern.
 *
 * Scatters seed points across the area, then traces cell boundaries by
 * scanning a grid and detecting where the nearest seed point changes.
 * Boundary points are clustered into strokes with hand-drawn wobble.
 *
 * @returns {Array} Array of stroke objects
 */
export function voronoiNoise(cx, cy, width, height, numCells, color, brushSize, opacity, palette, wobble, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 50, 800);
  height = clamp(Number(height) || 300, 50, 800);
  numCells = clamp(Math.round(Number(numCells) || 25), 5, 80);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);
  wobble = clamp(Number(wobble) || 0.3, 0, 1);

  const hw = width / 2, hh = height / 2;

  // Generate seed points with noise-based jitter for organic distribution
  const seeds = [];
  for (let i = 0; i < numCells; i++) {
    const nx = noise2d(i * 1.7, 0.5) * 0.3;
    const ny = noise2d(0.5, i * 1.7) * 0.3;
    seeds.push({
      x: cx - hw + Math.random() * width + nx * width * 0.1,
      y: cy - hh + Math.random() * height + ny * height * 0.1,
    });
  }

  // Find nearest seed for a point
  function nearest(px, py) {
    let minD = Infinity, minI = 0;
    for (let i = 0; i < seeds.length; i++) {
      const dx = px - seeds[i].x, dy = py - seeds[i].y;
      const d = dx * dx + dy * dy;
      if (d < minD) { minD = d; minI = i; }
    }
    return minI;
  }

  // Scan grid to find boundary points
  const step = Math.max(3, Math.min(width, height) / 60);
  const boundaryPoints = [];

  for (let gx = cx - hw; gx <= cx + hw; gx += step) {
    for (let gy = cy - hh; gy <= cy + hh; gy += step) {
      const cell = nearest(gx, gy);
      // Check if neighbors belong to a different cell
      const right = nearest(gx + step, gy);
      const below = nearest(gx, gy + step);
      if (cell !== right || cell !== below) {
        const w = wobble * step * 0.5;
        boundaryPoints.push({
          x: gx + (Math.random() - 0.5) * w,
          y: gy + (Math.random() - 0.5) * w,
          cell,
        });
      }
    }
  }

  // Cluster boundary points into strokes by tracing connected edges
  const result = [];
  const used = new Set();

  for (let i = 0; i < boundaryPoints.length && result.length < 200; i++) {
    if (used.has(i)) continue;

    // Start a new stroke from this boundary point
    const chain = [i];
    used.add(i);
    const maxChainLen = 30;

    // Greedily connect to nearest unused boundary point
    let current = i;
    while (chain.length < maxChainLen) {
      let bestJ = -1, bestD = (step * 2.5) * (step * 2.5);
      for (let j = 0; j < boundaryPoints.length; j++) {
        if (used.has(j)) continue;
        const dx = boundaryPoints[j].x - boundaryPoints[current].x;
        const dy = boundaryPoints[j].y - boundaryPoints[current].y;
        const d = dx * dx + dy * dy;
        if (d < bestD) { bestD = d; bestJ = j; }
      }
      if (bestJ === -1) break;
      chain.push(bestJ);
      used.add(bestJ);
      current = bestJ;
    }

    if (chain.length < 2) continue;

    const pts = chain.map(idx => ({
      x: boundaryPoints[idx].x,
      y: boundaryPoints[idx].y,
    }));

    // Color based on position relative to center
    const midPt = pts[Math.floor(pts.length / 2)];
    const dist = Math.hypot(midPt.x - cx, midPt.y - cy);
    const maxDist = Math.hypot(hw, hh);
    const t = clamp(dist / maxDist, 0, 1);
    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');

    result.push(makeStroke(pts, c, brushSize, opacity, pressureStyle));
  }

  return result.slice(0, 200);
}
