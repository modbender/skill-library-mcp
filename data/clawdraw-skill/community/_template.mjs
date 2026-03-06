/**
 * [Primitive Name] -- [short description]
 *
 * Community primitive for ClawDraw.
 * See CONTRIBUTING.md for contribution guidelines.
 */

import { makeStroke, splitIntoStrokes, clamp, lerp, noise2d } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'myPrimitive',           // unique identifier (camelCase)
  description: 'Short description of what this draws',
  category: 'community',         // always 'community' for community primitives
  author: 'your-github-username',
  parameters: {
    cx: { type: 'number', required: true, description: 'Center X' },
    cy: { type: 'number', required: true, description: 'Center Y' },
    // Add your parameters here...
    color: { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize: { type: 'number', required: false, default: 5, description: 'Brush width (3-100)' },
  },
};

/**
 * Generate strokes for this primitive.
 * @returns {Array} Array of stroke objects
 */
export function myPrimitive(cx, cy, color, brushSize) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  brushSize = clamp(Number(brushSize) || 5, 3, 100);

  const points = [];
  // Your algorithm here...
  // Generate points as {x, y} objects

  return splitIntoStrokes(points, color, brushSize, 0.9);
}
