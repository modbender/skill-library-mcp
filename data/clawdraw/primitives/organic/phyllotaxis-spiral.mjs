/**
 * Phyllotaxis Spiral — sunflower-inspired golden angle spiral pattern.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'phyllotaxisSpiral',
  description: 'Sunflower-inspired golden angle spiral pattern',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 170, description: 'Outer radius' },
    numPoints:     { type: 'number', required: false, default: 200, description: 'Number of seed points (10-500)' },
    dotSize:       { type: 'number', required: false, default: 0.4, description: 'Dot scale relative to spacing (0.1-1.0)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 4, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.9, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'flat', description: 'Pressure style' },
  },
};

/**
 * Generate a phyllotaxis spiral pattern.
 *
 * Places points using the golden angle (137.508 degrees) — the same
 * arrangement found in sunflower heads, pinecones, and other botanical
 * structures. Each point is drawn as a small circular stroke.
 *
 * @returns {Array} Array of stroke objects
 */
export function phyllotaxisSpiral(cx, cy, radius, numPoints, dotSize, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 170, 10, 500);
  numPoints = clamp(Math.round(Number(numPoints) || 200), 10, 500);
  dotSize = clamp(Number(dotSize) || 0.4, 0.1, 1.0);
  brushSize = clamp(Number(brushSize) || 4, 3, 100);
  opacity = clamp(Number(opacity) || 0.9, 0.01, 1);

  const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5)); // ~137.508 degrees
  const result = [];

  // Cap strokes at 200
  const count = Math.min(numPoints, 200);

  for (let i = 0; i < count; i++) {
    const t = i / count;
    const r = radius * Math.sqrt(t);
    const theta = i * GOLDEN_ANGLE;

    const px = cx + Math.cos(theta) * r;
    const py = cy + Math.sin(theta) * r;

    // Each dot is a small circle
    const spacing = radius / Math.sqrt(count);
    const dotR = spacing * dotSize * 0.5;
    const steps = 8;
    const pts = [];
    for (let s = 0; s <= steps; s++) {
      const a = (s / steps) * Math.PI * 2;
      pts.push({
        x: px + Math.cos(a) * dotR + (Math.random() - 0.5) * dotR * 0.15,
        y: py + Math.sin(a) * dotR + (Math.random() - 0.5) * dotR * 0.15,
      });
    }

    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, c, brushSize, opacity, pressureStyle));
  }

  return result;
}
