/**
 * Slime Mold — Physarum-inspired agent simulation with trail visualization.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, splitIntoStrokes, samplePalette } from './helpers.mjs';

export const METADATA = {
  name: 'slimeMold',
  description: 'Physarum slime mold agent simulation with trail visualization',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    width:         { type: 'number', required: false, default: 300, description: 'Field width' },
    height:        { type: 'number', required: false, default: 300, description: 'Field height' },
    agents:        { type: 'number', required: false, default: 100, description: 'Number of agents' },
    steps:         { type: 'number', required: false, default: 60, description: 'Simulation steps' },
    sensorDist:    { type: 'number', required: false, default: 9, description: 'Sensor distance' },
    sensorAngle:   { type: 'number', required: false, default: 0.5, description: 'Sensor angle (rad)' },
    turnSpeed:     { type: 'number', required: false, default: 0.3, description: 'Turn speed (rad)' },
    decayRate:     { type: 'number', required: false, default: 0.9, description: 'Trail decay rate' },
    contours:      { type: 'number', required: false, default: 5, description: 'Contour levels (unused, kept for compat)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

export function slimeMold(cx, cy, width, height, agents, steps, sensorDist, sensorAngle, turnSpeed, decayRate, contours, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 50, 600);
  height = clamp(Number(height) || 300, 50, 600);
  agents = clamp(Math.round(Number(agents) || 100), 10, 500);
  steps = clamp(Math.round(Number(steps) || 60), 10, 200);
  sensorDist = clamp(Number(sensorDist) || 9, 1, 30);
  sensorAngle = clamp(Number(sensorAngle) || 0.5, 0.1, 1.5);
  turnSpeed = clamp(Number(turnSpeed) || 0.3, 0.05, 1.0);
  decayRate = clamp(Number(decayRate) || 0.9, 0.5, 0.99);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const hw = width / 2, hh = height / 2;

  // Use a coarse grid for the trail map
  const gridStep = 3;
  const cols = Math.ceil(width / gridStep);
  const rows = Math.ceil(height / gridStep);
  const trail = new Float32Array(cols * rows);

  // Deterministic seeded random
  let seed = 42;
  function srand() {
    seed = (seed * 16807 + 0) % 2147483647;
    return (seed - 1) / 2147483646;
  }

  // Initialize agents: start clustered near center for better pattern formation
  const agentList = [];
  // Cap agents to stay within stroke budget (each agent = 1 stroke)
  const maxAgents = Math.min(agents, 180);
  for (let i = 0; i < maxAgents; i++) {
    const angle = srand() * Math.PI * 2;
    const dist = srand() * width * 0.45;
    agentList.push({
      x: width / 2 + Math.cos(angle) * dist,
      y: height / 2 + Math.sin(angle) * dist,
      heading: srand() * Math.PI * 2,
      trail: [{ x: cx - hw + width / 2 + Math.cos(angle) * dist, y: cy - hh + height / 2 + Math.sin(angle) * dist }],
    });
  }

  function sampleTrail(x, y) {
    const col = Math.floor(x / gridStep);
    const row = Math.floor(y / gridStep);
    if (col < 0 || col >= cols || row < 0 || row >= rows) return 0;
    return trail[row * cols + col];
  }

  function deposit(x, y, amount) {
    const col = Math.floor(x / gridStep);
    const row = Math.floor(y / gridStep);
    if (col >= 0 && col < cols && row >= 0 && row < rows) {
      trail[row * cols + col] += amount;
    }
  }

  // Simulation loop — each agent records its path
  for (let step = 0; step < steps; step++) {
    for (const agent of agentList) {
      // Sense left, center, right
      const sl = sampleTrail(
        agent.x + Math.cos(agent.heading - sensorAngle) * sensorDist,
        agent.y + Math.sin(agent.heading - sensorAngle) * sensorDist
      );
      const sc = sampleTrail(
        agent.x + Math.cos(agent.heading) * sensorDist,
        agent.y + Math.sin(agent.heading) * sensorDist
      );
      const sr = sampleTrail(
        agent.x + Math.cos(agent.heading + sensorAngle) * sensorDist,
        agent.y + Math.sin(agent.heading + sensorAngle) * sensorDist
      );

      if (sc >= sl && sc >= sr) {
        // keep heading
      } else if (sl > sr) {
        agent.heading -= turnSpeed;
      } else if (sr > sl) {
        agent.heading += turnSpeed;
      } else {
        agent.heading += (srand() - 0.5) * turnSpeed * 2;
      }

      agent.x += Math.cos(agent.heading) * 2.0;
      agent.y += Math.sin(agent.heading) * 2.0;

      // Wrap around
      if (agent.x < 0) agent.x += width;
      if (agent.x >= width) agent.x -= width;
      if (agent.y < 0) agent.y += height;
      if (agent.y >= height) agent.y -= height;

      deposit(agent.x, agent.y, 1.0);

      // Record trail point in world coords
      agent.trail.push({
        x: cx - hw + agent.x,
        y: cy - hh + agent.y,
      });
    }

    // Decay and blur
    const prev = new Float32Array(trail);
    for (let r = 1; r < rows - 1; r++) {
      for (let c = 1; c < cols - 1; c++) {
        const i = r * cols + c;
        const avg = (prev[i - 1] + prev[i + 1] + prev[i - cols] + prev[i + cols] + prev[i] * 4) / 8;
        trail[i] = avg * decayRate;
      }
    }
  }

  // Draw each agent's trail as a stroke
  const result = [];
  for (let i = 0; i < agentList.length && result.length < 195; i++) {
    const agent = agentList[i];
    if (agent.trail.length < 3) continue;
    const t = i / maxAgents;
    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');
    const strokes = splitIntoStrokes(agent.trail, c, brushSize, opacity * 0.6, pressureStyle);
    for (const s of strokes) {
      if (result.length >= 195) break;
      result.push(s);
    }
  }

  return result.slice(0, 200);
}
