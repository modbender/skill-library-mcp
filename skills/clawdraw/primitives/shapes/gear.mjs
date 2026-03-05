/**
 * Gear — mechanical cog wheel outline with teeth, hub, and spokes.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'gear',
  description: 'Mechanical cog wheel with trapezoidal teeth, inner hub, and radial spokes',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    outerRadius:   { type: 'number', required: false, default: 170, description: 'Outer tooth radius' },
    teeth:         { type: 'number', required: false, default: 16, description: 'Number of teeth (6-40)' },
    hubRadius:     { type: 'number', required: false, default: 60, description: 'Inner hub radius' },
    toothDepth:    { type: 'number', required: false, default: 0.25, description: 'Tooth depth ratio (0.1-0.5)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'flat', description: 'Pressure style' },
  },
};

/**
 * Generate a mechanical gear/cog wheel.
 *
 * Draws the outer profile with trapezoidal teeth, an inner hub circle,
 * and radial spoke lines connecting hub to teeth roots.
 *
 * @returns {Array} Array of stroke objects
 */
export function gear(cx, cy, outerRadius, teeth, hubRadius, toothDepth, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  outerRadius = clamp(Number(outerRadius) || 170, 30, 500);
  teeth = clamp(Math.round(Number(teeth) || 16), 6, 40);
  hubRadius = clamp(Number(hubRadius) || 60, 10, outerRadius * 0.6);
  toothDepth = clamp(Number(toothDepth) || 0.25, 0.1, 0.5);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const result = [];
  const innerRadius = outerRadius * (1 - toothDepth);
  const anglePerTooth = (Math.PI * 2) / teeth;
  // Tooth profile: flat top ~40% of tooth angle, sloped sides ~10% each, root ~40%
  const topFrac = 0.35;
  const slopeFrac = 0.1;

  // --- Outer gear profile ---
  const outerPts = [];
  for (let t = 0; t < teeth; t++) {
    const baseAngle = t * anglePerTooth;
    // Root start
    const a0 = baseAngle;
    // Slope up start
    const a1 = baseAngle + anglePerTooth * (0.5 - topFrac / 2 - slopeFrac);
    // Top start
    const a2 = baseAngle + anglePerTooth * (0.5 - topFrac / 2);
    // Top end
    const a3 = baseAngle + anglePerTooth * (0.5 + topFrac / 2);
    // Slope down end
    const a4 = baseAngle + anglePerTooth * (0.5 + topFrac / 2 + slopeFrac);
    // Root end
    const a5 = baseAngle + anglePerTooth;

    // Root arc
    for (let s = 0; s <= 4; s++) {
      const a = a0 + (a1 - a0) * (s / 4);
      outerPts.push({ x: cx + Math.cos(a) * innerRadius, y: cy + Math.sin(a) * innerRadius });
    }
    // Slope up
    outerPts.push({ x: cx + Math.cos(a2) * outerRadius, y: cy + Math.sin(a2) * outerRadius });
    // Tooth top arc
    for (let s = 0; s <= 4; s++) {
      const a = a2 + (a3 - a2) * (s / 4);
      outerPts.push({ x: cx + Math.cos(a) * outerRadius, y: cy + Math.sin(a) * outerRadius });
    }
    // Slope down
    outerPts.push({ x: cx + Math.cos(a4) * innerRadius, y: cy + Math.sin(a4) * innerRadius });
    // Remaining root
    for (let s = 0; s <= 4; s++) {
      const a = a4 + (a5 - a4) * (s / 4);
      outerPts.push({ x: cx + Math.cos(a) * innerRadius, y: cy + Math.sin(a) * innerRadius });
    }
  }
  // Close the profile
  if (outerPts.length > 0) outerPts.push({ ...outerPts[0] });

  // Split outer profile into colored segments by angle
  const segCount = Math.min(teeth * 2, 80);
  const chunkSize = Math.ceil(outerPts.length / segCount);
  for (let i = 0; i < segCount && result.length < 150; i++) {
    const start = i * chunkSize;
    const end = Math.min(start + chunkSize + 1, outerPts.length);
    const pts = outerPts.slice(start, end);
    if (pts.length < 2) continue;
    const t = i / Math.max(segCount - 1, 1);
    const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, col, brushSize, opacity, pressureStyle));
  }

  // --- Inner hub circle ---
  const hubSteps = 48;
  const hubPts = [];
  for (let s = 0; s <= hubSteps; s++) {
    const a = (s / hubSteps) * Math.PI * 2;
    hubPts.push({ x: cx + Math.cos(a) * hubRadius, y: cy + Math.sin(a) * hubRadius });
  }
  const hubCol = palette ? samplePalette(palette, 0.5) : (color || '#ffffff');
  result.push(makeStroke(hubPts, hubCol, brushSize, opacity, pressureStyle));

  // --- Radial spokes from hub to root circle ---
  const spokeCount = Math.min(teeth, 12);
  for (let i = 0; i < spokeCount && result.length < 200; i++) {
    const a = (i / spokeCount) * Math.PI * 2;
    const pts = [];
    const steps = 8;
    for (let s = 0; s <= steps; s++) {
      const r = hubRadius + (innerRadius - hubRadius) * (s / steps);
      pts.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
    }
    const t = i / Math.max(spokeCount - 1, 1);
    const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, col, brushSize, opacity * 0.7, pressureStyle));
  }

  // --- Center hole ---
  const centerR = hubRadius * 0.35;
  const centerPts = [];
  for (let s = 0; s <= 24; s++) {
    const a = (s / 24) * Math.PI * 2;
    centerPts.push({ x: cx + Math.cos(a) * centerR, y: cy + Math.sin(a) * centerR });
  }
  const centerCol = palette ? samplePalette(palette, 0.3) : (color || '#ffffff');
  result.push(makeStroke(centerPts, centerCol, brushSize, opacity, pressureStyle));

  return result.slice(0, 200);
}
