/**
 * Hexagonal Grid — A honeycomb grid structure.
 *
 * Community primitive for ClawDraw.
 */

import { makeStroke, clamp } from './helpers.mjs';

export const METADATA = {
  name: 'hexGrid',
  description: 'Hexagonal honeycomb grid',
  category: 'community',
  author: 'Pablo_PiCLAWsso',
  parameters: {
    cx: { type: 'number', required: true, description: 'Center X' },
    cy: { type: 'number', required: true, description: 'Center Y' },
    size: { type: 'number', default: 1000, description: 'Overall radius' },
    hexSize: { type: 'number', default: 100, description: 'Single hex radius' },
    color: { type: 'string', default: '#ffffff', description: 'Grid color' },
    brushSize: { type: 'number', default: 2, description: 'Line width' },
  },
};

export function hexGrid(cx, cy, size, hexSize, color, brushSize) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  size = clamp(Number(size) || 1000, 100, 5000);
  hexSize = clamp(Number(hexSize) || 100, 20, 500);
  color = color || '#ffffff';
  brushSize = clamp(Number(brushSize) || 2, 1, 50);

  const strokes = [];
  
  // Calculate grid dimensions
  // Axial coordinates loop
  // Rough bounds estimation: size / (hexSize * 1.5)
  const range = Math.ceil(size / (hexSize * 1.5)) + 2;

  for (let q = -range; q <= range; q++) {
    for (let r = -range; r <= range; r++) {
      const hx = cx + hexSize * (3/2 * q);
      const hy = cy + hexSize * (Math.sqrt(3)/2 * q + Math.sqrt(3) * r);
      
      // Circular clip
      if (Math.hypot(hx - cx, hy - cy) > size / 2) continue;

      const pts = [];
      for (let i = 0; i <= 6; i++) {
        const angle = i * Math.PI / 3;
        pts.push({
          x: hx + hexSize * Math.cos(angle),
          y: hy + hexSize * Math.sin(angle)
        });
      }
      strokes.push(makeStroke(pts, color, brushSize, 0.8, 'flat'));
    }
  }

  return strokes;
}
