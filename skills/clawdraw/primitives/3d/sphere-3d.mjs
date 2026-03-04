/**
 * 3D Sphere — wireframe sphere with latitude/longitude lines.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'sphere3d',
  description: 'Wireframe 3D sphere with latitude and longitude lines',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 120, description: 'Sphere radius' },
    latLines:      { type: 'number', required: false, default: 8, description: 'Latitude lines (2-20)' },
    lonLines:      { type: 'number', required: false, default: 12, description: 'Longitude lines (3-24)' },
    rotateX:       { type: 'number', required: false, default: 20, description: 'X rotation in degrees (-90 to 90)' },
    rotateY:       { type: 'number', required: false, default: 30, description: 'Y rotation in degrees (-180 to 180)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

/**
 * Generate a wireframe 3D sphere.
 *
 * Draws latitude circles and longitude arcs with 3D rotation,
 * projected to 2D. Back-facing portions are drawn at reduced
 * opacity for depth effect.
 *
 * @returns {Array} Array of stroke objects
 */
export function sphere3d(cx, cy, radius, latLines, lonLines, rotateX, rotateY, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 120, 10, 500);
  latLines = clamp(Math.round(Number(latLines) || 8), 2, 20);
  lonLines = clamp(Math.round(Number(lonLines) || 12), 3, 24);
  rotateX = clamp(Number(rotateX) || 20, -90, 90) * Math.PI / 180;
  rotateY = clamp(Number(rotateY) || 30, -180, 180) * Math.PI / 180;
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const cosRX = Math.cos(rotateX), sinRX = Math.sin(rotateX);
  const cosRY = Math.cos(rotateY), sinRY = Math.sin(rotateY);

  function project(x, y, z) {
    // Rotate around Y axis
    const x1 = x * cosRY - z * sinRY;
    const z1 = x * sinRY + z * cosRY;
    // Rotate around X axis
    const y1 = y * cosRX - z1 * sinRX;
    const z2 = y * sinRX + z1 * cosRX;
    return { x: cx + x1, y: cy + y1, z: z2 };
  }

  const result = [];
  const steps = 36;

  // Latitude lines
  for (let i = 1; i <= latLines && result.length < 200; i++) {
    const phi = (i / (latLines + 1)) * Math.PI;
    const ringR = radius * Math.sin(phi);
    const ringY = -radius * Math.cos(phi);
    const t = phi / Math.PI;
    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');

    const frontPts = [];
    const backPts = [];

    for (let s = 0; s <= steps; s++) {
      const theta = (s / steps) * Math.PI * 2;
      const px = ringR * Math.cos(theta);
      const pz = ringR * Math.sin(theta);
      const p = project(px, ringY, pz);

      if (p.z >= 0) {
        if (backPts.length >= 2) {
          result.push(makeStroke(backPts, c, brushSize, opacity * 0.3, pressureStyle));
          if (result.length >= 200) break;
        }
        frontPts.push({ x: p.x, y: p.y });
        backPts.length = 0;
      } else {
        if (frontPts.length >= 2) {
          result.push(makeStroke(frontPts, c, brushSize, opacity, pressureStyle));
          if (result.length >= 200) break;
        }
        backPts.push({ x: p.x, y: p.y });
        frontPts.length = 0;
      }
    }
    if (frontPts.length >= 2 && result.length < 200) {
      result.push(makeStroke(frontPts, c, brushSize, opacity, pressureStyle));
    }
    if (backPts.length >= 2 && result.length < 200) {
      result.push(makeStroke(backPts, c, brushSize, opacity * 0.3, pressureStyle));
    }
  }

  // Longitude lines
  for (let i = 0; i < lonLines && result.length < 200; i++) {
    const theta = (i / lonLines) * Math.PI * 2;
    const t = (1 - Math.cos(theta)) / 2;
    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');

    const frontPts = [];
    const backPts = [];

    for (let s = 0; s <= steps; s++) {
      const phi = (s / steps) * Math.PI;
      const px = radius * Math.sin(phi) * Math.cos(theta);
      const py = -radius * Math.cos(phi);
      const pz = radius * Math.sin(phi) * Math.sin(theta);
      const p = project(px, py, pz);

      if (p.z >= 0) {
        if (backPts.length >= 2) {
          result.push(makeStroke(backPts, c, brushSize, opacity * 0.3, pressureStyle));
          if (result.length >= 200) break;
        }
        frontPts.push({ x: p.x, y: p.y });
        backPts.length = 0;
      } else {
        if (frontPts.length >= 2) {
          result.push(makeStroke(frontPts, c, brushSize, opacity, pressureStyle));
          if (result.length >= 200) break;
        }
        backPts.push({ x: p.x, y: p.y });
        frontPts.length = 0;
      }
    }
    if (frontPts.length >= 2 && result.length < 200) {
      result.push(makeStroke(frontPts, c, brushSize, opacity, pressureStyle));
    }
    if (backPts.length >= 2 && result.length < 200) {
      result.push(makeStroke(backPts, c, brushSize, opacity * 0.3, pressureStyle));
    }
  }

  return result.slice(0, 200);
}
