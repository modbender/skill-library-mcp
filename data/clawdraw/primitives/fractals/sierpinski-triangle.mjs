/**
 * Sierpinski Triangle — recursive fractal drawing algorithm.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'sierpinskiTriangle',
  description: 'Recursive Sierpinski triangle fractal',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 170, description: 'Distance from center to vertex' },
    depth:         { type: 'number', required: false, default: 4, description: 'Recursion depth (1-5)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.9, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

/**
 * Generate a Sierpinski triangle fractal.
 *
 * Computes an equilateral triangle centered at (cx, cy), then recursively
 * subdivides: at each level, the three corner sub-triangles are kept and the
 * center sub-triangle is left empty (the classic Sierpinski void).
 *
 * At the leaf level (depth 0), each triangle is drawn as a closed 4-point
 * stroke with slight wobble for a hand-drawn feel.
 *
 * @returns {Array} Array of stroke objects
 */
export function sierpinskiTriangle(cx, cy, radius, depth, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 170, 10, 500);
  depth = clamp(Math.round(Number(depth) || 4), 1, 6);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.9, 0.01, 1);

  const result = [];

  // Equilateral triangle vertices, point-up, centered at (cx, cy)
  const angles = [-Math.PI / 2, Math.PI / 6, 5 * Math.PI / 6];
  const outerVerts = angles.map(a => ({
    x: cx + Math.cos(a) * radius,
    y: cy + Math.sin(a) * radius,
  }));

  function midpoint(a, b) {
    return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
  }

  function wobble(pt) {
    const w = radius * 0.008;
    return { x: pt.x + (Math.random() - 0.5) * w, y: pt.y + (Math.random() - 0.5) * w };
  }

  function subdivide(v0, v1, v2, d) {
    if (result.length >= 250) return;

    if (d <= 0) {
      // Leaf: draw this triangle as a closed stroke
      const dist = Math.hypot(
        (v0.x + v1.x + v2.x) / 3 - cx,
        (v0.y + v1.y + v2.y) / 3 - cy,
      );
      const t = clamp(dist / radius, 0, 1);
      const c = palette ? samplePalette(palette, t) : (color || '#ffffff');

      const pts = [wobble(v0), wobble(v1), wobble(v2), wobble(v0)];
      result.push(makeStroke(pts, c, brushSize, opacity, pressureStyle));
      return;
    }

    // Midpoints of each edge
    const m01 = midpoint(v0, v1);
    const m12 = midpoint(v1, v2);
    const m20 = midpoint(v2, v0);

    // Recurse into 3 corner sub-triangles (skip center = Sierpinski void)
    subdivide(v0, m01, m20, d - 1);
    subdivide(m01, v1, m12, d - 1);
    subdivide(m20, m12, v2, d - 1);
  }

  subdivide(outerVerts[0], outerVerts[1], outerVerts[2], depth);

  return result.slice(0, 250);
}
