/**
 * Orbital Dynamics — gravitational orbit trails around attractor points.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, splitIntoStrokes, samplePalette } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'orbitalDynamics',
  description: 'Gravitational orbit trails around attractor points',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 150, description: 'System radius' },
    numBodies:     { type: 'number', required: false, default: 8, description: 'Number of orbiting bodies (2-30)' },
    attractors:    { type: 'number', required: false, default: 2, description: 'Number of gravity attractors (1-5)' },
    steps:         { type: 'number', required: false, default: 300, description: 'Simulation steps per body (50-2000)' },
    gravity:       { type: 'number', required: false, default: 500, description: 'Gravitational strength (50-5000)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.8, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'taper', description: 'Pressure style' },
  },
};

/**
 * Generate orbital dynamics trails.
 *
 * Places attractor points (gravity wells) and launches bodies from
 * various positions. Each body is simulated with simple Newtonian
 * gravity — its trajectory is traced as a stroke, producing elegant
 * elliptical, hyperbolic, or chaotic orbit paths.
 *
 * @returns {Array} Array of stroke objects
 */
export function orbitalDynamics(cx, cy, radius, numBodies, attractors, steps, gravity, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 150, 20, 500);
  numBodies = clamp(Math.round(Number(numBodies) || 8), 2, 30);
  attractors = clamp(Math.round(Number(attractors) || 2), 1, 5);
  steps = clamp(Math.round(Number(steps) || 300), 50, 2000);
  gravity = clamp(Number(gravity) || 500, 50, 5000);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.8, 0.01, 1);

  // Place attractors
  const attractorPts = [];
  for (let i = 0; i < attractors; i++) {
    const angle = (i / attractors) * Math.PI * 2 + Math.random() * 0.5;
    const dist = radius * 0.2 * (0.5 + Math.random() * 0.5);
    attractorPts.push({
      x: cx + Math.cos(angle) * dist,
      y: cy + Math.sin(angle) * dist,
      mass: 0.5 + Math.random() * 1.5,
    });
  }

  const result = [];
  const dt = 0.015;
  const softening = radius * 0.05; // Prevent division by zero

  for (let b = 0; b < numBodies && result.length < 200; b++) {
    const t = b / numBodies;

    // Launch from the outer edge at various angles
    const launchAngle = t * Math.PI * 2 + (Math.random() - 0.5) * 0.3;
    const launchR = radius * (0.6 + Math.random() * 0.4);
    let px = cx + Math.cos(launchAngle) * launchR;
    let py = cy + Math.sin(launchAngle) * launchR;

    // Initial tangential velocity
    const speed = Math.sqrt(gravity / launchR) * (0.6 + Math.random() * 0.8);
    let vx = -Math.sin(launchAngle) * speed;
    let vy = Math.cos(launchAngle) * speed;

    const trail = [{ x: px, y: py }];

    for (let s = 0; s < steps; s++) {
      // Accumulate gravitational force from all attractors
      let ax = 0, ay = 0;
      for (const att of attractorPts) {
        const dx = att.x - px;
        const dy = att.y - py;
        const distSq = dx * dx + dy * dy + softening * softening;
        const dist = Math.sqrt(distSq);
        const force = gravity * att.mass / distSq;
        ax += (dx / dist) * force;
        ay += (dy / dist) * force;
      }

      vx += ax * dt;
      vy += ay * dt;
      px += vx * dt;
      py += vy * dt;

      trail.push({ x: px, y: py });

      // Escape check — if too far from center, stop
      if (Math.hypot(px - cx, py - cy) > radius * 3) break;
    }

    if (trail.length < 3) continue;

    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');
    const strokes = splitIntoStrokes(trail, c, brushSize, opacity, pressureStyle);
    for (const stroke of strokes) {
      if (result.length >= 200) break;
      result.push(stroke);
    }
  }

  return result.slice(0, 200);
}
