/**
 * Double Pendulum — chaotic trajectories from RK4-integrated Lagrangian dynamics.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, splitIntoStrokes, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'doublePendulum',
  description: 'Chaotic double pendulum trajectories via RK4 Lagrangian integration',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 170, description: 'Fit radius' },
    angle1:        { type: 'number', required: false, default: 120, description: 'Initial angle 1 (degrees)' },
    angle2:        { type: 'number', required: false, default: 150, description: 'Initial angle 2 (degrees)' },
    steps:         { type: 'number', required: false, default: 1500, description: 'Simulation steps' },
    traces:        { type: 'number', required: false, default: 5, description: 'Number of pendulum traces' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width' },
    opacity:       { type: 'number', required: false, default: 0.8, description: 'Stroke opacity' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'taper', description: 'Pressure style' },
  },
};

export function doublePendulum(cx, cy, radius, angle1, angle2, steps, traces, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 170, 20, 500);
  angle1 = Number(angle1) || 120;
  angle2 = Number(angle2) || 150;
  steps = clamp(Math.round(Number(steps) || 1500), 100, 5000);
  traces = clamp(Math.round(Number(traces) || 5), 1, 40);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.8, 0.01, 1);

  const g = 9.81;
  const dt = 0.01;

  // Double pendulum derivatives: m1=m2=1, L1=L2=1
  function derivs(state) {
    const [th1, th2, w1, w2] = state;
    const dth = th1 - th2;
    const sinD = Math.sin(dth);
    const cosD = Math.cos(dth);
    const den1 = 2 - cosD * cosD;
    const dw1 = (-g * (2 * Math.sin(th1) - cosD * Math.sin(th2))
                 - sinD * (w2 * w2 + w1 * w1 * cosD)) / den1;
    const dw2 = (2 * sinD * (w1 * w1 + g * Math.cos(th1)
                 - w2 * w2 * cosD / 2 + g * cosD * Math.sin(th1) / 2
                 - g * Math.sin(th2))) / den1;
    return [w1, w2, dw1, dw2];
  }

  // Proper double pendulum equations
  function derivsProper(state) {
    const [th1, th2, w1, w2] = state;
    const dth = th1 - th2;
    const s = Math.sin(dth);
    const c = Math.cos(dth);
    const den = 2 - c * c; // simplified for m1=m2=1, L1=L2=1
    const dw1 = (-g * (2 * Math.sin(th1) - c * Math.sin(th2))
                 - s * (w2 * w2 + w1 * w1 * c)) / den;
    const dw2 = (2 * s * (w1 * w1 + g * Math.cos(th1) - w2 * w2 * c * 0.5)) / den
                + (g * Math.sin(th2) * (c * c - 2)) / den;
    return [w1, w2, dw1, dw2];
  }

  function rk4Step(state) {
    const k1 = derivs(state);
    const s2 = state.map((v, i) => v + k1[i] * dt * 0.5);
    const k2 = derivs(s2);
    const s3 = state.map((v, i) => v + k2[i] * dt * 0.5);
    const k3 = derivs(s3);
    const s4 = state.map((v, i) => v + k3[i] * dt);
    const k4 = derivs(s4);
    return state.map((v, i) => v + (dt / 6) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
  }

  const result = [];

  for (let tr = 0; tr < traces && result.length < 200; tr++) {
    const offset = tr * 0.02; // slight angle variation per trace
    const th1 = (angle1 + offset * 180 / Math.PI) * Math.PI / 180;
    const th2 = (angle2 - offset * 180 / Math.PI) * Math.PI / 180;
    let state = [th1, th2, 0, 0];

    const trail = [];
    for (let s = 0; s < steps; s++) {
      // Position of second bob (L1=L2=1)
      const x2 = Math.sin(state[0]) + Math.sin(state[1]);
      const y2 = Math.cos(state[0]) + Math.cos(state[1]);
      trail.push({ x: x2, y: y2 });
      state = rk4Step(state);
    }

    // Scale trail to fit radius
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const p of trail) {
      if (p.x < minX) minX = p.x;
      if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.y > maxY) maxY = p.y;
    }
    const rangeX = maxX - minX || 1;
    const rangeY = maxY - minY || 1;
    const scale = radius * 2 / Math.max(rangeX, rangeY);
    const mapped = trail.map(p => ({
      x: cx + (p.x - (minX + maxX) / 2) * scale,
      y: cy + (p.y - (minY + maxY) / 2) * scale,
    }));

    const rawT = tr / Math.max(traces - 1, 1);
    const t = 0.15 + rawT * 0.55;
    const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
    const strokes = splitIntoStrokes(mapped, col, brushSize, opacity, pressureStyle);
    for (const stroke of strokes) {
      if (result.length >= 200) break;
      result.push(stroke);
    }
  }

  return result.slice(0, 200);
}
