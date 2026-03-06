/**
 * Flow/abstract primitives: flowField, spiral, lissajous, strangeAttractor, spirograph.
 */

import { clamp, lerp, noise2d, makeStroke, splitIntoStrokes, samplePalette } from './helpers.mjs';

// ---------------------------------------------------------------------------
// Metadata
// ---------------------------------------------------------------------------

export const METADATA = [
  {
    name: 'flowField', description: 'Perlin noise flow field particle traces', category: 'flow-abstract',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      width: { type: 'number', min: 20, max: 600, default: 300, description: 'Area width (larger = bigger field)' },
      height: { type: 'number', min: 20, max: 600, default: 300, description: 'Area height (larger = bigger field)' },
      noiseScale: { type: 'number', min: 0.001, max: 0.1, default: 0.01, description: 'Noise frequency (0.005=smooth waves, 0.05=chaotic static)' },
      density: { type: 'number', min: 0.1, max: 1, default: 0.5, description: 'Particle density (0.2=sparse lines, 0.8=dense texture)' },
      segmentLength: { type: 'number', min: 1, max: 30, default: 5, description: 'Step size (2=smooth curves, 15=jagged/angular)' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      palette: { type: 'string', description: 'Color palette (overrides color)' },
      traceLength: { type: 'number', min: 5, max: 200, default: 40, description: 'Steps per trace (longer = longer lines)' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'spiral', description: 'Archimedean spiral', category: 'flow-abstract',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      turns: { type: 'number', min: 0.5, max: 20, default: 3, description: 'Number of turns (higher = tighter winding)' },
      startRadius: { type: 'number', min: 0, max: 500, default: 5, description: 'Inner starting radius' },
      endRadius: { type: 'number', min: 1, max: 500, default: 160, description: 'Outer ending radius' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'lissajous', description: 'Lissajous harmonic curves', category: 'flow-abstract',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      freqX: { type: 'number', min: 1, max: 20, default: 3, description: 'X frequency (loops horizontally)' },
      freqY: { type: 'number', min: 1, max: 20, default: 2, description: 'Y frequency (loops vertically)' },
      phase: { type: 'number', description: 'Phase offset in degrees (shifts the wave)' },
      amplitude: { type: 'number', min: 10, max: 500, default: 160, description: 'Curve size (radius)' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      palette: { type: 'string', description: 'Color palette (overrides color)' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'strangeAttractor', description: 'Strange attractor chaotic orbits (lorenz, aizawa, thomas)', category: 'flow-abstract',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      type: { type: 'string', options: ['lorenz', 'aizawa', 'thomas'], default: 'lorenz', description: 'Attractor type (lorenz=butterfly, aizawa=sphere-like)' },
      iterations: { type: 'number', min: 100, max: 5000, default: 2000, description: 'Point count (higher = denser cloud)' },
      scale: { type: 'number', min: 0.1, max: 50, default: 8, description: 'Display scale (zoom)' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      palette: { type: 'string', description: 'Color palette (overrides color)' },
      timeStep: { type: 'number', min: 0.001, max: 0.02, default: 0.005, description: 'Integration step (smaller = smoother/slower)' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'spirograph', description: 'Spirograph (epitrochoid/hypotrochoid) geometric curves', category: 'flow-abstract',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      outerR: { type: 'number', min: 10, max: 500, default: 150, description: 'Outer ring radius (primary size)' },
      innerR: { type: 'number', min: 5, max: 400, default: 55, description: 'Inner ring radius (loop frequency control)' },
      traceR: { type: 'number', min: 1, max: 400, default: 30, description: 'Trace point distance (loop amplitude)' },
      revolutions: { type: 'number', min: 1, max: 50, default: 10, description: 'Number of revolutions (higher = denser pattern)' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      palette: { type: 'string', description: 'Color palette (overrides color)' },
      startAngle: { type: 'number', description: 'Starting angle in degrees' },
      pressureStyle: { type: 'string' },
    },
  },
];

// ---------------------------------------------------------------------------
// Primitives
// ---------------------------------------------------------------------------

export function flowField(cx, cy, width, height, noiseScale, density, segmentLength, color, brushSize, palette, traceLength, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 20, 600);
  height = clamp(Number(height) || 300, 20, 600);
  noiseScale = clamp(Number(noiseScale) || 0.01, 0.001, 0.1);
  density = clamp(Number(density) || 0.5, 0.1, 1);
  segmentLength = clamp(Number(segmentLength) || 5, 1, 30);
  brushSize = clamp(Number(brushSize) || 2, 3, 100);

  traceLength = clamp(Math.round(Number(traceLength) || 40), 5, 200);
  const numParticles = Math.round(20 * density);
  const stepsPerParticle = traceLength;
  const result = [];

  for (let p = 0; p < numParticles; p++) {
    let x = cx + (Math.random() - 0.5) * width;
    let y = cy + (Math.random() - 0.5) * height;
    const pts = [{ x, y }];

    for (let s = 0; s < stepsPerParticle; s++) {
      const angle = noise2d(x * noiseScale, y * noiseScale) * Math.PI * 2;
      x += Math.cos(angle) * segmentLength;
      y += Math.sin(angle) * segmentLength;
      pts.push({ x, y });
      if (Math.abs(x - cx) > width * 0.6 || Math.abs(y - cy) > height * 0.6) break;
    }
    const c = palette ? samplePalette(palette, Math.random()) : color;
    if (pts.length > 2) result.push(makeStroke(pts, c, brushSize, 0.7, pressureStyle));
    if (result.length >= 200) break;
  }

  return result;
}

export function spiral(cx, cy, turns, startRadius, endRadius, color, brushSize, opacity, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  turns = clamp(Number(turns) || 3, 0.5, 20);
  startRadius = clamp(Number(startRadius) || 5, 0, 500);
  endRadius = clamp(Number(endRadius) || 160, 1, 500);
  const steps = clamp(Math.round(turns * 30), 20, 2000);
  const pts = [];
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const a = t * turns * Math.PI * 2;
    const r = lerp(startRadius, endRadius, t);
    pts.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
  }
  return splitIntoStrokes(pts, color, brushSize, opacity, pressureStyle);
}

export function lissajous(cx, cy, freqX, freqY, phase, amplitude, color, brushSize, palette, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  freqX = clamp(Number(freqX) || 3, 1, 20);
  freqY = clamp(Number(freqY) || 2, 1, 20);
  phase = (Number(phase) || 0) * Math.PI / 180;
  amplitude = clamp(Number(amplitude) || 160, 10, 500);

  const steps = 200;
  const noiseSeed = Math.random() * 100;

  if (!palette) {
    const pts = [];
    for (let i = 0; i <= steps; i++) {
      const t = (i / steps) * Math.PI * 2;
      const wobble = noise2d(i * 0.05 + noiseSeed, 0) * 0.1;
      pts.push({
        x: cx + Math.sin(freqX * t + phase + wobble) * amplitude,
        y: cy + Math.sin(freqY * t + wobble * 0.7) * amplitude,
      });
    }
    return splitIntoStrokes(pts, color, brushSize, 0.8, pressureStyle);
  }

  const segments = 12;
  const perSegment = Math.ceil(steps / segments) + 1;
  const strokes = [];
  for (let seg = 0; seg < segments; seg++) {
    const pts = [];
    const t0 = seg / segments;
    const c = samplePalette(palette, t0);
    for (let j = 0; j <= perSegment; j++) {
      const i = Math.min(seg * (steps / segments) + j, steps);
      const t = (i / steps) * Math.PI * 2;
      const wobble = noise2d(i * 0.05 + noiseSeed, 0) * 0.1;
      pts.push({
        x: cx + Math.sin(freqX * t + phase + wobble) * amplitude,
        y: cy + Math.sin(freqY * t + wobble * 0.7) * amplitude,
      });
    }
    if (pts.length > 1) strokes.push(makeStroke(pts, c, brushSize, 0.8, pressureStyle));
  }
  return strokes;
}

export function strangeAttractor(cx, cy, type, iterations, scale, color, brushSize, palette, timeStep, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  type = String(type || 'lorenz').toLowerCase();
  iterations = clamp(Math.round(Number(iterations) || 2000), 100, 5000);
  scale = clamp(Number(scale) || 8, 0.1, 50);
  brushSize = clamp(Number(brushSize) || 2, 3, 100);
  timeStep = clamp(Number(timeStep) || 0.005, 0.001, 0.02);

  let x = 0.1 + Math.random() * 0.05;
  let y = Math.random() * 0.05;
  let z = Math.random() * 0.05;
  const dt = timeStep;

  function step() {
    let dx, dy, dz;
    if (type === 'aizawa') {
      const a = 0.95, b = 0.7, c = 0.6, d = 3.5, e = 0.25, f = 0.1;
      dx = (z - b) * x - d * y;
      dy = d * x + (z - b) * y;
      dz = c + a * z - z * z * z / 3 - (x * x + y * y) * (1 + e * z) + f * z * x * x * x;
    } else if (type === 'thomas') {
      const b = 0.208186;
      dx = Math.sin(y) - b * x;
      dy = Math.sin(z) - b * y;
      dz = Math.sin(x) - b * z;
    } else {
      const sigma = 10, rho = 28, beta = 8/3;
      dx = sigma * (y - x);
      dy = x * (rho - z) - y;
      dz = x * y - beta * z;
    }
    x += dx * dt; y += dy * dt; z += dz * dt;
  }

  if (!palette) {
    const pts = [];
    for (let i = 0; i < iterations; i++) {
      step();
      pts.push({ x: cx + x * scale, y: cy + y * scale });
    }
    return splitIntoStrokes(pts, color, brushSize, 0.7, pressureStyle);
  }

  const segments = 10;
  const perSegment = Math.floor(iterations / segments);
  const strokes = [];
  for (let seg = 0; seg < segments; seg++) {
    const pts = [];
    const t = seg / (segments - 1);
    for (let i = 0; i < perSegment; i++) {
      step();
      pts.push({ x: cx + x * scale, y: cy + y * scale });
    }
    if (pts.length > 1) strokes.push(makeStroke(pts, samplePalette(palette, t), brushSize, 0.7, pressureStyle));
  }
  return strokes;
}

export function spirograph(cx, cy, outerR, innerR, traceR, revolutions, color, brushSize, palette, startAngle, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  outerR = clamp(Number(outerR) || 150, 10, 500);
  innerR = clamp(Number(innerR) || 55, 5, 400);
  traceR = clamp(Number(traceR) || 30, 1, 400);
  revolutions = clamp(Number(revolutions) || 10, 1, 50);
  brushSize = clamp(Number(brushSize) || 2, 3, 100);
  startAngle = (Number(startAngle) || 0) * Math.PI / 180;

  const steps = revolutions * 100;
  const diff = outerR - innerR;

  if (!palette) {
    const pts = [];
    for (let i = 0; i <= steps; i++) {
      const t = (i / steps) * revolutions * Math.PI * 2 + startAngle;
      const x = cx + diff * Math.cos(t) + traceR * Math.cos(t * diff / innerR);
      const y = cy + diff * Math.sin(t) - traceR * Math.sin(t * diff / innerR);
      pts.push({ x, y });
    }
    return splitIntoStrokes(pts, color, brushSize, 0.8, pressureStyle);
  }

  const segments = 16;
  const perSegment = Math.ceil(steps / segments) + 1;
  const strokes = [];
  for (let seg = 0; seg < segments; seg++) {
    const pts = [];
    const palT = seg / (segments - 1);
    for (let j = 0; j <= perSegment; j++) {
      const i = Math.min(seg * Math.floor(steps / segments) + j, steps);
      const t = (i / steps) * revolutions * Math.PI * 2 + startAngle;
      const x = cx + diff * Math.cos(t) + traceR * Math.cos(t * diff / innerR);
      const y = cy + diff * Math.sin(t) - traceR * Math.sin(t * diff / innerR);
      pts.push({ x, y });
    }
    if (pts.length > 1) strokes.push(makeStroke(pts, samplePalette(palette, palT), brushSize, 0.8, pressureStyle));
  }
  return strokes;
}
