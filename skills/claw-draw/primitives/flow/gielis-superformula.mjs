/**
 * Gielis Superformula — parametric supershape curves with layered variation.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'gielisSuperformula',
  description: 'Layered Gielis superformula curves (supershapes) with parametric variation',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:             { type: 'number', required: true, description: 'Center X' },
    cy:             { type: 'number', required: true, description: 'Center Y' },
    radius:         { type: 'number', required: false, default: 120, description: 'Outer radius' },
    m:              { type: 'number', required: false, default: 5, description: 'Rotational symmetry order' },
    n1:             { type: 'number', required: false, default: 0.3, description: 'Exponent n1' },
    n2:             { type: 'number', required: false, default: 0.3, description: 'Exponent n2' },
    n3:             { type: 'number', required: false, default: 0.3, description: 'Exponent n3' },
    a:              { type: 'number', required: false, default: 1, description: 'Parameter a' },
    b:              { type: 'number', required: false, default: 1, description: 'Parameter b' },
    layers:         { type: 'number', required: false, default: 8, description: 'Number of concentric layers (1-30)' },
    pointsPerLayer: { type: 'number', required: false, default: 200, description: 'Points per layer (50-500)' },
    color:          { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:      { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:        { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:        { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle:  { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

/**
 * Evaluate the Gielis superformula at angle theta.
 * r(theta) = ( |cos(m*theta/4)/a|^n2 + |sin(m*theta/4)/b|^n3 )^(-1/n1)
 */
function superformula(theta, m, n1, n2, n3, a, b) {
  const mTheta4 = m * theta / 4;
  const term1 = Math.abs(Math.cos(mTheta4) / a);
  const term2 = Math.abs(Math.sin(mTheta4) / b);

  // Guard against zero/infinity
  const t1 = n2 === 0 ? 1 : Math.pow(term1 + 1e-10, n2);
  const t2 = n3 === 0 ? 1 : Math.pow(term2 + 1e-10, n3);
  const sum = t1 + t2;

  if (sum < 1e-15 || n1 === 0) return 1;
  return Math.pow(sum, -1 / n1);
}

/**
 * Generate layered Gielis superformula curves.
 *
 * Each layer varies the m, n1, n2, n3 parameters slightly from the base
 * values, creating a family of related supershape curves at different
 * scales for visual richness.
 *
 * @returns {Array} Array of stroke objects
 */
export function gielisSuperformula(cx, cy, radius, m, n1, n2, n3, a, b, layers, pointsPerLayer, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 120, 10, 500);
  m = Number(m) || 5;
  n1 = Number(n1) || 0.3;
  n2 = Number(n2) || 0.3;
  n3 = Number(n3) || 0.3;
  a = Number(a) || 1;
  b = Number(b) || 1;
  if (a === 0) a = 1;
  if (b === 0) b = 1;
  layers = clamp(Math.round(Number(layers) || 8), 1, 30);
  pointsPerLayer = clamp(Math.round(Number(pointsPerLayer) || 200), 50, 500);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const result = [];

  for (let layer = 0; layer < layers && result.length < 200; layer++) {
    const t = layer / Math.max(layers - 1, 1);
    const scale = 0.3 + t * 0.7; // inner layers smaller

    // Vary parameters per layer for visual interest
    const lm = m + Math.sin(t * Math.PI * 2) * 0.5;
    const ln1 = n1 + t * 0.4;
    const ln2 = n2 + Math.cos(t * Math.PI) * 0.15;
    const ln3 = n3 + Math.sin(t * Math.PI * 1.5) * 0.15;

    // Compute the curve for this layer
    const pts = [];
    let maxR = 0;
    const rawR = [];
    for (let i = 0; i <= pointsPerLayer; i++) {
      const theta = (i / pointsPerLayer) * 2 * Math.PI;
      const r = superformula(theta, lm, ln1, ln2, ln3, a, b);
      rawR.push({ theta, r });
      if (r > maxR) maxR = r;
    }

    // Normalize and scale to fit within radius
    if (maxR < 1e-10) continue;
    for (const entry of rawR) {
      const normR = (entry.r / maxR) * radius * scale;
      pts.push({
        x: cx + Math.cos(entry.theta) * normR,
        y: cy + Math.sin(entry.theta) * normR,
      });
    }

    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, c, brushSize, opacity, pressureStyle));
  }

  return result.slice(0, 200);
}
