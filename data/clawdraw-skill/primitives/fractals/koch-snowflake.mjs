/**
 * Koch Snowflake — recursive edge subdivision of equilateral triangle.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'kochSnowflake',
  description: 'Koch snowflake fractal via recursive edge subdivision',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 170, description: 'Circumscribed radius' },
    depth:         { type: 'number', required: false, default: 4, description: 'Recursion depth (1-6)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width' },
    opacity:       { type: 'number', required: false, default: 0.8, description: 'Stroke opacity' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'flat', description: 'Pressure style' },
  },
};

export function kochSnowflake(cx, cy, radius, depth, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 170, 20, 500);
  depth = clamp(Math.round(Number(depth) || 4), 1, 6);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.8, 0.01, 1);

  // Koch subdivision: replace each segment with 4 segments
  function subdivide(points, d) {
    if (d <= 0) return points;

    const newPts = [];
    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[i];
      const p1 = points[i + 1];

      const dx = p1.x - p0.x;
      const dy = p1.y - p0.y;

      // Trisection points
      const a = { x: p0.x + dx / 3, y: p0.y + dy / 3 };
      const b = { x: p0.x + dx * 2 / 3, y: p0.y + dy * 2 / 3 };

      // Peak point (equilateral triangle pointing outward)
      const peak = {
        x: (a.x + b.x) / 2 + (b.y - a.y) * Math.sqrt(3) / 2,
        y: (a.y + b.y) / 2 - (b.x - a.x) * Math.sqrt(3) / 2,
      };

      newPts.push(p0, a, peak, b);
    }
    newPts.push(points[points.length - 1]);

    return subdivide(newPts, d - 1);
  }

  // Start with equilateral triangle (rotated so flat side on bottom)
  const triPts = [];
  for (let i = 0; i < 3; i++) {
    const angle = -Math.PI / 2 + (i * 2 * Math.PI / 3);
    triPts.push({
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    });
  }
  triPts.push(triPts[0]); // Close the triangle

  const snowflake = subdivide(triPts, depth);

  // Split into stroke segments for coloring
  const numSegments = Math.min(150, Math.max(3, Math.ceil(snowflake.length / 30)));
  const chunkSize = Math.ceil(snowflake.length / numSegments);
  const result = [];

  for (let i = 0; i < numSegments && result.length < 200; i++) {
    const start = i * chunkSize;
    const end = Math.min(start + chunkSize + 1, snowflake.length);
    const pts = snowflake.slice(start, end);
    if (pts.length < 2) continue;
    const t = i / Math.max(numSegments - 1, 1);
    const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, col, brushSize, opacity, pressureStyle));
  }

  return result.slice(0, 200);
}
