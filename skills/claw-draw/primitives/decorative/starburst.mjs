/**
 * Starburst — radial sunburst with alternating long/short pointed rays.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'starburst',
  description: 'Radial sunburst with alternating triangular rays colored by angle',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    outerRadius:   { type: 'number', required: false, default: 185, description: 'Outer ray radius' },
    rays:          { type: 'number', required: false, default: 24, description: 'Number of rays (8-60)' },
    innerRadius:   { type: 'number', required: false, default: 30, description: 'Inner circle radius' },
    shortRatio:    { type: 'number', required: false, default: 0.6, description: 'Short ray length ratio (0.3-0.9)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'flat', description: 'Pressure style' },
  },
};

/**
 * Generate a radial starburst / sunburst pattern.
 *
 * Alternating long and short pointed triangular rays emanate from a central
 * circle. Each ray is a filled triangular wedge drawn as an outline. Rays
 * are colored by their angle around the circle via the palette.
 *
 * @returns {Array} Array of stroke objects
 */
export function starburst(cx, cy, outerRadius, rays, innerRadius, shortRatio, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  outerRadius = clamp(Number(outerRadius) || 185, 30, 500);
  rays = clamp(Math.round(Number(rays) || 24), 8, 60);
  innerRadius = clamp(Number(innerRadius) || 30, 5, outerRadius * 0.5);
  shortRatio = clamp(Number(shortRatio) || 0.6, 0.3, 0.9);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const result = [];
  const anglePerRay = (Math.PI * 2) / rays;
  const halfAngle = anglePerRay * 0.45; // slight gap between rays

  // --- Draw rays as triangular wedges ---
  for (let i = 0; i < rays && result.length < 180; i++) {
    const centerAngle = i * anglePerRay;
    const isLong = i % 2 === 0;
    const rayLen = isLong ? outerRadius : outerRadius * shortRatio;

    // Triangle: two base points on inner circle, one tip point at ray length
    const leftAngle = centerAngle - halfAngle;
    const rightAngle = centerAngle + halfAngle;

    const baseLeft = {
      x: cx + Math.cos(leftAngle) * innerRadius,
      y: cy + Math.sin(leftAngle) * innerRadius,
    };
    const baseRight = {
      x: cx + Math.cos(rightAngle) * innerRadius,
      y: cy + Math.sin(rightAngle) * innerRadius,
    };
    const tip = {
      x: cx + Math.cos(centerAngle) * rayLen,
      y: cy + Math.sin(centerAngle) * rayLen,
    };

    // Draw wedge outline: left edge -> tip -> right edge -> back to base
    const pts = [];
    const steps = 8;

    // Left side: base left -> tip
    for (let s = 0; s <= steps; s++) {
      const frac = s / steps;
      pts.push({
        x: baseLeft.x + (tip.x - baseLeft.x) * frac,
        y: baseLeft.y + (tip.y - baseLeft.y) * frac,
      });
    }
    // Right side: tip -> base right
    for (let s = 1; s <= steps; s++) {
      const frac = s / steps;
      pts.push({
        x: tip.x + (baseRight.x - tip.x) * frac,
        y: tip.y + (baseRight.y - tip.y) * frac,
      });
    }
    // Close: base right -> base left (arc along inner circle)
    for (let s = 1; s <= 4; s++) {
      const frac = s / 4;
      const a = rightAngle + (leftAngle + anglePerRay - rightAngle) * frac;
      pts.push({
        x: cx + Math.cos(a) * innerRadius,
        y: cy + Math.sin(a) * innerRadius,
      });
    }

    const t = i / rays;
    const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, col, brushSize, opacity, pressureStyle));
  }

  // --- Inner circle outline ---
  const circlePts = [];
  const circleSteps = 48;
  for (let s = 0; s <= circleSteps; s++) {
    const a = (s / circleSteps) * Math.PI * 2;
    circlePts.push({
      x: cx + Math.cos(a) * innerRadius,
      y: cy + Math.sin(a) * innerRadius,
    });
  }
  const circleCol = palette ? samplePalette(palette, 0.5) : (color || '#ffffff');
  result.push(makeStroke(circlePts, circleCol, brushSize + 1, opacity, pressureStyle));

  // --- Outer boundary circle (connects ray tips) ---
  const outerPts = [];
  for (let s = 0; s <= circleSteps; s++) {
    const a = (s / circleSteps) * Math.PI * 2;
    // Undulate between long and short ray lengths
    const rayIdx = (a / anglePerRay);
    const frac = rayIdx - Math.floor(rayIdx);
    const isLongA = Math.floor(rayIdx) % 2 === 0;
    const isLongB = (Math.floor(rayIdx) + 1) % 2 === 0;
    const rA = isLongA ? outerRadius : outerRadius * shortRatio;
    const rB = isLongB ? outerRadius : outerRadius * shortRatio;
    // Smooth interpolation between tip radii
    const smoothFrac = frac * frac * (3 - 2 * frac);
    const r = rA + (rB - rA) * smoothFrac;
    outerPts.push({
      x: cx + Math.cos(a) * r,
      y: cy + Math.sin(a) * r,
    });
  }
  // Split outer boundary into colored segments
  const segCount = Math.min(24, rays);
  const chunkSize = Math.ceil(outerPts.length / segCount);
  for (let i = 0; i < segCount && result.length < 200; i++) {
    const start = i * chunkSize;
    const end = Math.min(start + chunkSize + 1, outerPts.length);
    const pts = outerPts.slice(start, end);
    if (pts.length < 2) continue;
    const t = i / Math.max(segCount - 1, 1);
    const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, col, brushSize * 0.7, opacity * 0.5, pressureStyle));
  }

  return result.slice(0, 200);
}
