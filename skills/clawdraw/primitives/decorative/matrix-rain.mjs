/**
 * Matrix Rain — Digital rain effect with glitch offsets.
 *
 * Community primitive for ClawDraw.
 */

import { makeStroke, clamp } from './helpers.mjs';

export const METADATA = {
  name: 'matrixRain',
  description: 'Digital rain effect with glitch offsets',
  category: 'community',
  author: 'Pablo_PiCLAWsso',
  parameters: {
    cx: { type: 'number', required: true, description: 'Center X' },
    cy: { type: 'number', required: true, description: 'Center Y' },
    width: { type: 'number', default: 1000, description: 'Field width' },
    height: { type: 'number', default: 1000, description: 'Field height' },
    density: { type: 'number', default: 50, description: 'Number of drops' },
    color: { type: 'string', default: '#00ff00', description: 'Color' },
    glitch: { type: 'number', default: 0.1, description: 'Glitch probability (0-1)' },
  },
};

export function matrixRain(cx, cy, width, height, density, color, glitch) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 1000, 100, 5000);
  height = clamp(Number(height) || 1000, 100, 5000);
  density = clamp(Number(density) || 50, 10, 500);
  color = color || '#00ff00';
  glitch = clamp(Number(glitch) || 0.1, 0, 1);

  const strokes = [];

  for (let i = 0; i < density; i++) {
    const rx = cx + (Math.random() - 0.5) * width;
    const ry = cy + (Math.random() - 0.5) * height;
    
    const pts = [];
    const len = 50 + Math.random() * 200; // Random drop length
    const step = 8;
    
    for (let j = 0; j < len; j += step) {
      // Glitch offset
      const dx = (Math.random() < glitch) ? (Math.random() - 0.5) * 15 : 0;
      pts.push({ x: rx + dx, y: ry + j });
    }
    
    strokes.push(makeStroke(
      pts,
      color,
      2,
      0.6 + Math.random() * 0.4, // Varied opacity
      'flick' // Taper end
    ));
  }

  return strokes;
}
