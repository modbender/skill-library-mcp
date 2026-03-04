/**
 * Hypercube — 4D tesseract wireframe projected to 2D.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'hypercube',
  description: '4D tesseract wireframe projected to 2D with rotation',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    size:          { type: 'number', required: false, default: 150, description: 'Projection scale' },
    angleXW:       { type: 'number', required: false, default: 45, description: 'Rotation angle in XW plane (degrees)' },
    angleYZ:       { type: 'number', required: false, default: 30, description: 'Rotation angle in YZ plane (degrees)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'flat', description: 'Pressure style' },
  },
};

/**
 * Generate a 4D hypercube (tesseract) wireframe projected to 2D.
 *
 * 16 vertices (all combinations of +/-1 in 4D), 32 edges (vertices
 * differing in exactly one coordinate). Two rotation planes (XW and YZ)
 * applied before orthographic projection to 2D. Edges colored by
 * average w-depth via palette.
 *
 * @returns {Array} Array of stroke objects
 */
export function hypercube(cx, cy, size, angleXW, angleYZ, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  size = clamp(Number(size) || 150, 20, 500);
  angleXW = (Number(angleXW) || 45) * Math.PI / 180;
  angleYZ = (Number(angleYZ) || 30) * Math.PI / 180;
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  // Generate 16 vertices: all combinations of +/-1 in 4D
  const vertices4d = [];
  for (let i = 0; i < 16; i++) {
    vertices4d.push([
      (i & 1) ? 1 : -1,
      (i & 2) ? 1 : -1,
      (i & 4) ? 1 : -1,
      (i & 8) ? 1 : -1,
    ]);
  }

  // Find edges: pairs differing in exactly one coordinate
  const edges = [];
  for (let i = 0; i < 16; i++) {
    for (let j = i + 1; j < 16; j++) {
      let diff = 0;
      for (let k = 0; k < 4; k++) {
        if (vertices4d[i][k] !== vertices4d[j][k]) diff++;
      }
      if (diff === 1) edges.push([i, j]);
    }
  }

  // Apply 4D rotations
  const cosXW = Math.cos(angleXW), sinXW = Math.sin(angleXW);
  const cosYZ = Math.cos(angleYZ), sinYZ = Math.sin(angleYZ);

  // Also rotate in XZ plane for a more interesting 3D view
  const angleXZ = angleYZ * 0.7;
  const cosXZ = Math.cos(angleXZ), sinXZ = Math.sin(angleXZ);

  const projected = vertices4d.map(([x, y, z, w]) => {
    // Rotate in XW plane (4D rotation)
    const x1 = x * cosXW - w * sinXW;
    const w1 = x * sinXW + w * cosXW;
    // Rotate in YZ plane
    const y1 = y * cosYZ - z * sinYZ;
    const z1 = y * sinYZ + z * cosYZ;
    // Rotate in XZ plane for 3D depth
    const x2 = x1 * cosXZ - z1 * sinXZ;
    const z2 = x1 * sinXZ + z1 * cosXZ;
    // Perspective projection from 4D: w affects scale (classic tesseract look)
    const viewDist = 4;
    const perspW = viewDist / (viewDist - w1 * 0.5);
    const perspZ = viewDist / (viewDist - z2 * 0.3);
    const scale = perspW * perspZ;
    return { x: cx + x2 * size * 0.4 * scale, y: cy + y1 * size * 0.4 * scale, w: w1 };
  });

  // Draw edges colored by average w-depth
  const wValues = projected.map(v => v.w);
  const minW = Math.min(...wValues);
  const maxW = Math.max(...wValues);
  const wRange = maxW - minW || 1;

  const result = [];
  for (const [i, j] of edges) {
    const p0 = projected[i];
    const p1 = projected[j];
    const avgW = (p0.w + p1.w) / 2;
    const t = (avgW - minW) / wRange;

    // Subdivide edge for smooth drawing
    const steps = 12;
    const pts = [];
    for (let s = 0; s <= steps; s++) {
      const frac = s / steps;
      pts.push({
        x: p0.x + (p1.x - p0.x) * frac,
        y: p0.y + (p1.y - p0.y) * frac,
      });
    }

    const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, col, brushSize, opacity, pressureStyle));
  }

  // Draw vertex dots
  for (let i = 0; i < projected.length && result.length < 200; i++) {
    const v = projected[i];
    const t = (v.w - minW) / wRange;
    const dotR = 3;
    const pts = [];
    for (let s = 0; s <= 8; s++) {
      const a = (s / 8) * Math.PI * 2;
      pts.push({ x: v.x + Math.cos(a) * dotR, y: v.y + Math.sin(a) * dotR });
    }
    const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, col, brushSize + 1, opacity, pressureStyle));
  }

  return result.slice(0, 200);
}
