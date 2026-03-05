/**
 * Penrose Tiling — Robinson triangle subdivision (P3 rhombus tiling).
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'penroseTiling',
  description: 'Penrose P3 tiling via Robinson triangle subdivision with golden ratio',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 170, description: 'Outer radius of initial decagon' },
    depth:         { type: 'number', required: false, default: 4, description: 'Subdivision depth (1-6)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

const PHI = (1 + Math.sqrt(5)) / 2;

/**
 * Generate a Penrose P3 tiling.
 *
 * Starts with 10 Robinson triangles arranged in a decagon, then performs
 * recursive subdivision using the Penrose P3 rules where thick (type 0)
 * triangles split into 2 thick + 1 thin, and thin (type 1) triangles split
 * into 1 thick + 1 thin. Edge splits happen at golden ratio points.
 *
 * @returns {Array} Array of stroke objects
 */
export function penroseTiling(cx, cy, radius, depth, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 170, 10, 500);
  depth = clamp(Math.round(Number(depth) || 4), 1, 6);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  // Triangle: { type: 0=thick, 1=thin, a:{x,y}, b:{x,y}, c:{x,y} }
  // a = apex vertex, b and c = base vertices

  // Start with 10 triangles forming a decagon (sun configuration)
  let triangles = [];
  for (let i = 0; i < 10; i++) {
    const a0 = (2 * i - 1) * Math.PI / 10;
    const a1 = (2 * i + 1) * Math.PI / 10;
    const b = { x: cx + Math.cos(a0) * radius, y: cy + Math.sin(a0) * radius };
    const c = { x: cx + Math.cos(a1) * radius, y: cy + Math.sin(a1) * radius };
    if (i % 2 === 0) {
      triangles.push({ type: 0, a: { x: cx, y: cy }, b: b, c: c });
    } else {
      triangles.push({ type: 0, a: { x: cx, y: cy }, b: c, c: b });
    }
  }

  function lerpPt(p1, p2, t) {
    return { x: p1.x + (p2.x - p1.x) * t, y: p1.y + (p2.y - p1.y) * t };
  }

  // Subdivide using Penrose P3 rules
  for (let d = 0; d < depth; d++) {
    const next = [];
    for (const tri of triangles) {
      if (tri.type === 0) {
        // Thick triangle (acute Robinson) -> 2 thick + 1 thin
        const p = lerpPt(tri.a, tri.b, 1 / PHI);
        const q = lerpPt(tri.a, tri.c, 1 / PHI);
        next.push({ type: 0, a: tri.c, b: p, c: tri.b });
        next.push({ type: 1, a: p, b: q, c: tri.b });
        next.push({ type: 0, a: tri.a, b: q, c: p });
      } else {
        // Thin triangle (obtuse Robinson) -> 1 thick + 1 thin
        const p = lerpPt(tri.b, tri.a, 1 / PHI);
        next.push({ type: 1, a: p, b: tri.c, c: tri.a });
        next.push({ type: 0, a: tri.c, b: p, c: tri.b });
      }
    }
    triangles = next;
  }

  // Shuffle triangles so the 200-stroke cap samples from all areas
  let rseed = 54321;
  for (let i = triangles.length - 1; i > 0; i--) {
    rseed = (rseed * 16807 + 0) % 2147483647;
    const j = rseed % (i + 1);
    const tmp = triangles[i]; triangles[i] = triangles[j]; triangles[j] = tmp;
  }

  const result = [];

  // Draw each triangle as a closed stroke, capping at 200
  for (let i = 0; i < triangles.length && result.length < 200; i++) {
    const tri = triangles[i];
    const centX = (tri.a.x + tri.b.x + tri.c.x) / 3;
    const centY = (tri.a.y + tri.b.y + tri.c.y) / 3;
    const dist = Math.hypot(centX - cx, centY - cy);
    const t = clamp(dist / radius, 0, 1);
    // Mix in triangle type for color variety
    const colorT = clamp(t * 0.7 + tri.type * 0.3, 0, 1);
    const c = palette ? samplePalette(palette, colorT) : (color || '#ffffff');

    const w = radius * 0.004;
    const pts = [
      { x: tri.a.x + (Math.random() - 0.5) * w, y: tri.a.y + (Math.random() - 0.5) * w },
      { x: tri.b.x + (Math.random() - 0.5) * w, y: tri.b.y + (Math.random() - 0.5) * w },
      { x: tri.c.x + (Math.random() - 0.5) * w, y: tri.c.y + (Math.random() - 0.5) * w },
      { x: tri.a.x + (Math.random() - 0.5) * w, y: tri.a.y + (Math.random() - 0.5) * w },
    ];
    result.push(makeStroke(pts, c, brushSize, opacity, pressureStyle));
  }

  return result.slice(0, 200);
}
