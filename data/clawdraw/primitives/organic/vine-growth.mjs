/**
 * Vine Growth — recursive branching tendrils with curl noise perturbation.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette, noise2d } from './helpers.mjs';

export const METADATA = {
  name: 'vineGrowth',
  description: 'Recursive branching vine tendrils with curl noise and leaf loops at tips',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 150, description: 'Growth radius' },
    branches:      { type: 'number', required: false, default: 8, description: 'Root branch count' },
    maxDepth:      { type: 'number', required: false, default: 5, description: 'Max recursion depth' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 4, description: 'Brush width' },
    opacity:       { type: 'number', required: false, default: 0.8, description: 'Stroke opacity' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'taper', description: 'Pressure style' },
  },
};

export function vineGrowth(cx, cy, radius, branches, maxDepth, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 150, 20, 500);
  branches = clamp(Math.round(Number(branches) || 8), 2, 16);
  maxDepth = clamp(Math.round(Number(maxDepth) || 5), 1, 8);
  brushSize = clamp(Number(brushSize) || 4, 3, 100);
  opacity = clamp(Number(opacity) || 0.8, 0.01, 1);

  const result = [];

  // Deterministic seed
  let seed = branches * 3571 + maxDepth * 1913;
  function srand() {
    seed = (seed * 16807 + 0) % 2147483647;
    return (seed - 1) / 2147483646;
  }

  let branchBudget = 195; // will be set per root branch

  function growBranch(x, y, angle, length, depth, thickness) {
    if (depth > maxDepth || result.length >= branchBudget || length < 3) return;

    const steps = Math.max(10, Math.round(length / 2));
    const pts = [];
    let px = x, py = y;
    // Use a unique noise offset per branch to avoid uniform drift
    const noiseOx = srand() * 200 - 100;
    const noiseOy = srand() * 200 - 100;

    for (let i = 0; i <= steps; i++) {
      pts.push({ x: px, y: py });
      const t = i / steps;
      // Subtle curl noise perturbation — keep branches on-course
      const noiseScale = 2.0 / radius;
      const n = noise2d((px + noiseOx) * noiseScale, (py + noiseOy) * noiseScale);
      const curlAngle = angle + n * 0.25;
      const stepLen = (length / steps) * (1 - t * 0.15);
      px += Math.cos(curlAngle) * stepLen;
      py += Math.sin(curlAngle) * stepLen;
    }

    const depthT = depth / maxDepth;
    const col = palette ? samplePalette(palette, depthT) : (color || '#ffffff');
    const bSize = Math.max(3, Math.round(thickness));
    result.push(makeStroke(pts, col, bSize, opacity * (1 - depthT * 0.3), pressureStyle));

    // At tips, draw small leaf loops
    if (depth >= maxDepth - 1 || length < 10) {
      const leafPts = [];
      const leafSize = clamp(length * 0.25, 3, 15);
      for (let i = 0; i <= 14; i++) {
        const la = (i / 14) * Math.PI * 2;
        const lr = leafSize * (0.4 + 0.6 * Math.abs(Math.sin(la * 2)));
        leafPts.push({
          x: px + Math.cos(la + angle) * lr,
          y: py + Math.sin(la + angle) * lr,
        });
      }
      if (leafPts.length >= 2 && result.length < branchBudget) {
        const leafT = clamp(depthT + 0.3, 0, 1);
        const leafCol = palette ? samplePalette(palette, leafT) : (color || '#ffffff');
        result.push(makeStroke(leafPts, leafCol, 3, opacity * 0.6, 'flat'));
      }
      return;
    }

    // Branch into 2-3 sub-branches from along the vine
    const numSub = depth < 2 ? 3 : 2;
    for (let i = 0; i < numSub && result.length < branchBudget; i++) {
      const branchPos = 0.4 + srand() * 0.5;
      const idx = Math.floor(branchPos * (pts.length - 1));
      const bp = pts[idx];
      const spread = 0.3 + srand() * 0.6;
      const side = (i % 2 === 0) ? -1 : 1;
      const newAngle = angle + side * spread;
      const newLength = length * (0.45 + srand() * 0.25);
      const newThickness = thickness * 0.65;
      growBranch(bp.x, bp.y, newAngle, newLength, depth + 1, newThickness);
    }
  }

  const strokesPerBranch = Math.floor(195 / branches);
  for (let i = 0; i < branches; i++) {
    branchBudget = result.length + strokesPerBranch;
    const angle = (i / branches) * Math.PI * 2;
    const startX = cx + Math.cos(angle) * 8;
    const startY = cy + Math.sin(angle) * 8;
    const length = radius * (0.55 + srand() * 0.4);
    growBranch(startX, startY, angle, length, 0, brushSize);
  }

  return result.slice(0, 200);
}
