/**
 * DLA — Diffusion-Limited Aggregation fractal growth pattern.
 *
 * Renders as a dendritic branching tree from center outward,
 * mimicking the characteristic fractal growth of DLA.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'dla',
  description: 'Diffusion-Limited Aggregation fractal growth pattern',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 170, description: 'Growth radius' },
    particles:     { type: 'number', required: false, default: 100, description: 'Max branches (10-500)' },
    stickiness:    { type: 'number', required: false, default: 0.8, description: 'Branch wiggle (0-1)' },
    cellSize:      { type: 'number', required: false, default: 4, description: 'Unused (kept for compat)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

export function dla(cx, cy, radius, particles, stickiness, cellSize, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 170, 20, 400);
  particles = clamp(Math.round(Number(particles) || 100), 10, 500);
  stickiness = clamp(Number(stickiness) || 0.8, 0.1, 1);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  // Seeded RNG
  let seed = 12345;
  const rand = () => { seed = (seed * 16807 + 0) % 2147483647; return (seed - 1) / 2147483646; };

  const result = [];
  const maxBranches = Math.min(particles * 2, 190);
  const queue = [];

  // Start with main trunks radiating from center
  const numTrunks = 8 + Math.floor(rand() * 5);
  for (let i = 0; i < numTrunks; i++) {
    const angle = (2 * Math.PI * i) / numTrunks + (rand() - 0.5) * 0.2;
    queue.push({
      x: cx, y: cy,
      angle,
      length: radius * (1.0 + rand() * 0.2),
      depth: 0,
      t: i / numTrunks,
    });
  }

  while (queue.length > 0 && result.length < maxBranches) {
    const b = queue.shift();

    // Generate branch path with random walk
    const numPts = Math.max(3, Math.floor(b.length / 3));
    const stepLen = b.length / numPts;
    const pts = [];
    let bx = b.x, by = b.y, angle = b.angle;

    pts.push({ x: bx, y: by });
    for (let i = 0; i < numPts; i++) {
      angle += (rand() - 0.5) * stickiness * 0.5;
      bx += Math.cos(angle) * stepLen;
      by += Math.sin(angle) * stepLen;
      pts.push({ x: bx, y: by });
    }

    const t = palette ? clamp(b.t, 0, 1) : 0;
    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');
    const bOpacity = opacity * Math.max(0.25, 1 - b.depth * 0.1);
    result.push(makeStroke(pts, c, brushSize, bOpacity, pressureStyle));

    // Sub-branches: more at early depths, fewer at later
    if (b.depth < 7 && b.length > 3 && result.length < maxBranches - 2) {
      const numSub = b.depth < 3 ? (1 + Math.floor(rand() * 3)) : (1 + Math.floor(rand() * 2));
      for (let s = 0; s < numSub; s++) {
        const splitT = 0.2 + rand() * 0.6;
        const si = Math.min(Math.floor(splitT * numPts), pts.length - 1);
        const subAngle = angle + (rand() > 0.5 ? 1 : -1) * (0.3 + rand() * 0.9);
        queue.push({
          x: pts[si].x, y: pts[si].y,
          angle: subAngle,
          length: b.length * (0.25 + rand() * 0.4),
          depth: b.depth + 1,
          t: b.t + (rand() - 0.5) * 0.12,
        });
      }
    }
  }

  return result.slice(0, 200);
}
