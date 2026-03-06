/**
 * Decorative primitives: border, mandala, fractalTree, radialSymmetry, sacredGeometry.
 */

import { clamp, lerp, makeStroke, samplePalette } from './helpers.mjs';
import { circle, arc, rectangle, polygon } from '../shapes/basic-shapes.mjs';

// ---------------------------------------------------------------------------
// Metadata
// ---------------------------------------------------------------------------

export const METADATA = [
  {
    name: 'border', description: 'Decorative border frame (dots, dashes, waves, zigzag)', category: 'decorative',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      width: { type: 'number', min: 20, max: 800, default: 300, description: 'Frame width' },
      height: { type: 'number', min: 20, max: 800, default: 200, description: 'Frame height' },
      pattern: { type: 'string', options: ['dots', 'dashes', 'waves', 'zigzag'], default: 'dashes', description: 'Border pattern' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      amplitude: { type: 'number', min: 2, max: 30, default: 8, description: 'Wave/zigzag amplitude' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'mandala', description: 'Radially symmetric mandala pattern', category: 'decorative',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      radius: { type: 'number', min: 10, max: 500, default: 150, description: 'Overall radius' },
      symmetry: { type: 'number', min: 3, max: 24, default: 8, description: 'Rotational folds' },
      complexity: { type: 'number', min: 1, max: 8, default: 3, description: 'Concentric rings' },
      colors: { type: 'array', description: 'Array of hex colors' },
      brushSize: { type: 'number', min: 3, max: 100 },
      wobbleAmount: { type: 'number', min: 0, max: 0.5, default: 0.15, description: 'Motif wobble intensity' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'fractalTree', description: 'Recursive branching tree', category: 'decorative',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      trunkLength: { type: 'number', min: 10, max: 300, default: 100, description: 'Trunk length' },
      branchAngle: { type: 'number', min: 5, max: 60, default: 25, description: 'Branch spread in degrees' },
      depth: { type: 'number', min: 1, max: 8, default: 5, description: 'Recursion depth' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      palette: { type: 'string', description: 'Color palette' },
      branchRatio: { type: 'number', min: 0.4, max: 0.9, default: 0.7, description: 'Length ratio per level' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'radialSymmetry', description: 'Complex mandala-like patterns with bezier motifs', category: 'decorative',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      radius: { type: 'number', min: 10, max: 500, default: 150, description: 'Overall radius' },
      folds: { type: 'number', min: 3, max: 24, default: 8, description: 'Rotational folds' },
      layers: { type: 'number', min: 1, max: 8, default: 4, description: 'Concentric layers' },
      complexity: { type: 'number', min: 1, max: 5, default: 3, description: 'Motif complexity' },
      colors: { type: 'array', description: 'Array of hex colors' },
      brushSize: { type: 'number', min: 3, max: 100 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'sacredGeometry', description: 'Sacred geometry (goldenSpiral, flowerOfLife, metatronsCube, sriYantra)', category: 'decorative',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      radius: { type: 'number', min: 10, max: 500, default: 150, description: 'Overall radius' },
      pattern: { type: 'string', options: ['flowerOfLife', 'goldenSpiral', 'metatronsCube', 'sriYantra'], description: 'Geometry pattern' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1 },
      pressureStyle: { type: 'string' },
    },
  },
];

// ---------------------------------------------------------------------------
// Primitives
// ---------------------------------------------------------------------------

export function border(cx, cy, width, height, pattern, color, brushSize, amplitude, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 20, 800);
  height = clamp(Number(height) || 200, 20, 800);
  pattern = String(pattern || 'dashes').toLowerCase();
  brushSize = clamp(Number(brushSize) || 4, 3, 100);
  amplitude = clamp(Number(amplitude) || 8, 2, 30);

  const hw = width / 2, hh = height / 2;
  const corners = [
    { x: cx - hw, y: cy - hh }, { x: cx + hw, y: cy - hh },
    { x: cx + hw, y: cy + hh }, { x: cx - hw, y: cy + hh },
  ];

  const result = [];
  const edges = [[0,1],[1,2],[2,3],[3,0]];

  for (const [a, b] of edges) {
    const p0 = corners[a], p1 = corners[b];
    const edgeLen = Math.hypot(p1.x - p0.x, p1.y - p0.y);
    const dx = (p1.x - p0.x) / edgeLen, dy = (p1.y - p0.y) / edgeLen;
    const nx = -dy, ny = dx;

    if (pattern === 'dots') {
      const step = 15;
      for (let d = 0; d < edgeLen; d += step) {
        const t = d / edgeLen;
        const x = lerp(p0.x, p1.x, t), y = lerp(p0.y, p1.y, t);
        result.push(makeStroke([{x,y},{x:x+1,y:y+1},{x:x-1,y}], color, brushSize, 0.9, pressureStyle));
      }
    } else if (pattern === 'waves') {
      const pts = [];
      const waveSteps = Math.round(edgeLen / 3);
      const amp = amplitude;
      for (let i = 0; i <= waveSteps; i++) {
        const t = i / waveSteps;
        const base_x = lerp(p0.x, p1.x, t), base_y = lerp(p0.y, p1.y, t);
        const off = Math.sin(t * Math.PI * 8) * amp;
        pts.push({ x: base_x + nx * off, y: base_y + ny * off });
      }
      result.push(makeStroke(pts, color, brushSize, 0.9, pressureStyle));
    } else if (pattern === 'zigzag') {
      const pts = [];
      const zigSteps = Math.round(edgeLen / 10);
      const amp = amplitude;
      for (let i = 0; i <= zigSteps; i++) {
        const t = i / zigSteps;
        const base_x = lerp(p0.x, p1.x, t), base_y = lerp(p0.y, p1.y, t);
        const off = (i % 2 === 0 ? amp : -amp);
        pts.push({ x: base_x + nx * off, y: base_y + ny * off });
      }
      result.push(makeStroke(pts, color, brushSize, 0.9, pressureStyle));
    } else {
      const dashLen = 12, gapLen = 8;
      let d = 0;
      while (d < edgeLen) {
        const end = Math.min(d + dashLen, edgeLen);
        const t0 = d / edgeLen, t1 = end / edgeLen;
        result.push(makeStroke([
          { x: lerp(p0.x, p1.x, t0), y: lerp(p0.y, p1.y, t0) },
          { x: lerp(p0.x, p1.x, t1), y: lerp(p0.y, p1.y, t1) },
        ], color, brushSize, 0.9, pressureStyle));
        d = end + gapLen;
      }
    }

    if (result.length >= 200) break;
  }

  return result.slice(0, 200);
}

export function mandala(cx, cy, radius, symmetry, complexity, colors, brushSize, wobbleAmount, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 150, 10, 500);
  symmetry = clamp(Math.round(Number(symmetry) || 8), 3, 24);
  complexity = clamp(Math.round(Number(complexity) || 3), 1, 8);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  wobbleAmount = clamp(Number(wobbleAmount) || 0.15, 0, 0.5);
  if (!Array.isArray(colors) || colors.length === 0) colors = ['#ffffff', '#aaaaaa'];

  const result = [];

  for (let ring = 1; ring <= complexity; ring++) {
    const r = (ring / complexity) * radius;
    const color = colors[(ring - 1) % colors.length];

    const motifPts = [];
    const motifSteps = 8;
    const segAngle = (Math.PI * 2) / symmetry;
    for (let i = 0; i <= motifSteps; i++) {
      const t = i / motifSteps;
      const a = t * segAngle;
      const wobble = Math.sin(t * Math.PI * 3) * r * wobbleAmount;
      const randWobble = (Math.random() - 0.5) * r * 0.2;
      motifPts.push({ a, r: r + wobble + randWobble });
    }

    for (let s = 0; s < symmetry; s++) {
      const baseA = (s / symmetry) * Math.PI * 2;
      const pts = motifPts.map(p => ({
        x: cx + Math.cos(baseA + p.a) * p.r,
        y: cy + Math.sin(baseA + p.a) * p.r,
      }));
      result.push(makeStroke(pts, color, brushSize, 0.8, pressureStyle));
      if (result.length >= 200) break;
    }
    if (result.length >= 200) break;
  }

  result.push(...circle(cx, cy, radius * 0.1, colors[0], brushSize, 0.9, pressureStyle));

  return result.slice(0, 200);
}

export function fractalTree(cx, cy, trunkLength, branchAngle, depth, color, brushSize, palette, branchRatio, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  trunkLength = clamp(Number(trunkLength) || 100, 10, 300);
  branchAngle = clamp(Number(branchAngle) || 25, 5, 60) * Math.PI / 180;
  depth = clamp(Math.round(Number(depth) || 5), 1, 8);
  brushSize = clamp(Number(brushSize) || 8, 5, 100);
  branchRatio = clamp(Number(branchRatio) || 0.7, 0.4, 0.9);
  const maxDepth = depth;

  const result = [];

  function branch(x, y, angle, len, d, size) {
    if (d <= 0 || result.length >= 200 || len < 2) return;
    const lenJitter = len * (1 + (Math.random() - 0.5) * 0.4);
    const ex = x + Math.cos(angle) * lenJitter;
    const ey = y + Math.sin(angle) * lenJitter;
    const t = 1 - d / maxDepth;
    const c = palette ? samplePalette(palette, t) : color;
    result.push(makeStroke([{ x, y }, { x: ex, y: ey }], c, size, 0.85, pressureStyle));
    const newLen = len * branchRatio;
    const newSize = Math.max(3, size * 0.75);
    const angleJitter = (Math.random() - 0.5) * 0.14;
    branch(ex, ey, angle - branchAngle + angleJitter, newLen, d - 1, newSize);
    branch(ex, ey, angle + branchAngle + angleJitter, newLen, d - 1, newSize);
  }

  branch(cx, cy, -Math.PI / 2, trunkLength, depth, brushSize);
  return result.slice(0, 200);
}

export function radialSymmetry(cx, cy, radius, folds, layers, complexity, colors, brushSize, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 150, 10, 500);
  folds = clamp(Math.round(Number(folds) || 8), 3, 24);
  layers = clamp(Math.round(Number(layers) || 4), 1, 8);
  complexity = clamp(Math.round(Number(complexity) || 3), 1, 5);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  if (!Array.isArray(colors) || colors.length === 0) colors = ['#ffffff', '#aaaaaa', '#ffaa00'];

  const result = [];
  const segAngle = (Math.PI * 2) / folds;

  for (let layer = 0; layer < layers; layer++) {
    const r = ((layer + 1) / layers) * radius;
    const color = colors[layer % colors.length];
    const layerRand = Math.random();

    for (let s = 0; s < folds && result.length < 200; s++) {
      const baseA = (s / folds) * Math.PI * 2;
      const motifType = (layer + Math.floor(layerRand * 3)) % 3;

      if (motifType === 0) {
        const pts = [];
        const steps = 12 + complexity * 4;
        for (let i = 0; i <= steps; i++) {
          const t = i / steps;
          const a = baseA + t * segAngle;
          const loopR = r + Math.sin(t * Math.PI * complexity) * r * 0.2 * (1 + (Math.random() - 0.5) * 0.3);
          pts.push({ x: cx + Math.cos(a) * loopR, y: cy + Math.sin(a) * loopR });
        }
        result.push(makeStroke(pts, color, brushSize, 0.8, pressureStyle));
      } else if (motifType === 1) {
        const pts = [];
        const spikes = 2 + complexity;
        for (let i = 0; i <= spikes * 2; i++) {
          const t = i / (spikes * 2);
          const a = baseA + t * segAngle;
          const spikeR = i % 2 === 0 ? r * (0.7 + Math.random() * 0.1) : r * (1.1 + Math.random() * 0.1);
          pts.push({ x: cx + Math.cos(a) * spikeR, y: cy + Math.sin(a) * spikeR });
        }
        result.push(makeStroke(pts, color, brushSize, 0.85, pressureStyle));
      } else {
        const midA = baseA + segAngle / 2;
        const dotR = r * (0.9 + Math.random() * 0.2);
        const dotX = cx + Math.cos(midA) * dotR;
        const dotY = cy + Math.sin(midA) * dotR;
        const dotSize = 3 + complexity * 2;
        result.push(...circle(dotX, dotY, dotSize, color, brushSize, 0.7, pressureStyle));
      }
    }
  }

  result.push(...circle(cx, cy, radius * 0.08, colors[0], brushSize, 0.9, pressureStyle));

  return result.slice(0, 200);
}

export function sacredGeometry(cx, cy, radius, pattern, color, brushSize, opacity, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 150, 10, 500);
  pattern = String(pattern || 'flowerOfLife').toLowerCase().replace(/[^a-z]/g, '');
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.8, 0.01, 1);

  const result = [];
  const PHI = (1 + Math.sqrt(5)) / 2;

  if (pattern === 'goldenspiral' || pattern === 'golden') {
    const quarters = 10;
    let r = radius * 0.02;
    let angle = 0;
    let px = cx, py = cy;
    for (let q = 0; q < quarters && result.length < 200; q++) {
      const pts = [];
      const steps = 20;
      for (let i = 0; i <= steps; i++) {
        const a = angle + (i / steps) * (Math.PI / 2);
        pts.push({ x: px + Math.cos(a) * r, y: py + Math.sin(a) * r });
      }
      result.push(makeStroke(pts, color, brushSize, opacity, pressureStyle));
      const endAngle = angle + Math.PI / 2;
      px += Math.cos(endAngle) * r * (1 - 1/PHI);
      py += Math.sin(endAngle) * r * (1 - 1/PHI);
      r *= PHI;
      angle += Math.PI / 2;
      if (r > radius * 2) break;
    }
    for (let q = 0; q < 6 && result.length < 200; q++) {
      const s = radius * Math.pow(1/PHI, q);
      result.push(...rectangle(cx, cy, s * 2, s * 2 / PHI, q * 90, color, Math.max(3, brushSize - 1), opacity * 0.4, pressureStyle));
    }
  } else if (pattern === 'metatronscube' || pattern === 'metatron') {
    const innerR = radius * 0.15;
    result.push(...circle(cx, cy, innerR, color, brushSize, opacity, pressureStyle));
    const ring1Pts = [];
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2 - Math.PI / 2;
      const x = cx + Math.cos(a) * radius * 0.4;
      const y = cy + Math.sin(a) * radius * 0.4;
      ring1Pts.push({ x, y });
      result.push(...circle(x, y, innerR, color, brushSize, opacity, pressureStyle));
    }
    const ring2Pts = [];
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2;
      const x = cx + Math.cos(a) * radius * 0.7;
      const y = cy + Math.sin(a) * radius * 0.7;
      ring2Pts.push({ x, y });
      result.push(...circle(x, y, innerR, color, brushSize, opacity, pressureStyle));
    }
    const allPts = [{ x: cx, y: cy }, ...ring1Pts, ...ring2Pts];
    for (let i = 0; i < allPts.length && result.length < 200; i++) {
      for (let j = i + 1; j < allPts.length && result.length < 200; j++) {
        result.push(makeStroke([allPts[i], allPts[j]], color, Math.max(3, brushSize - 1), opacity * 0.4, pressureStyle));
      }
    }
  } else if (pattern === 'sriyanta' || pattern === 'sriyantra') {
    const layers = 5;
    for (let i = 0; i < layers && result.length < 200; i++) {
      const r = radius * Math.pow(1/PHI, i * 0.5);
      const rot = i % 2 === 0 ? -90 : 90;
      result.push(...polygon(cx, cy, r, 3, rot, color, brushSize, opacity * (1 - i * 0.1), pressureStyle));
    }
    for (let i = 0; i < 8 && result.length < 200; i++) {
      const a = (i / 8) * Math.PI * 2;
      const lx = cx + Math.cos(a) * radius * 0.9;
      const ly = cy + Math.sin(a) * radius * 0.9;
      result.push(...arc(lx, ly, radius * 0.2, (a * 180/Math.PI) - 60, (a * 180/Math.PI) + 60, color, brushSize, opacity * 0.6, pressureStyle));
    }
    result.push(...circle(cx, cy, radius * 0.05, color, brushSize, opacity, pressureStyle));
  } else {
    // Default: Flower of Life
    const cellR = radius / 3;
    result.push(...circle(cx, cy, cellR, color, brushSize, opacity, pressureStyle));
    for (let i = 0; i < 6 && result.length < 200; i++) {
      const a = (i / 6) * Math.PI * 2;
      result.push(...circle(cx + Math.cos(a) * cellR, cy + Math.sin(a) * cellR, cellR, color, brushSize, opacity, pressureStyle));
    }
    for (let i = 0; i < 12 && result.length < 200; i++) {
      const a = (i / 12) * Math.PI * 2;
      const r2 = cellR * (i % 2 === 0 ? 2 : Math.sqrt(3));
      result.push(...circle(cx + Math.cos(a) * r2, cy + Math.sin(a) * r2, cellR, color, brushSize, opacity, pressureStyle));
    }
    result.push(...circle(cx, cy, radius, color, brushSize, opacity * 0.5, pressureStyle));
  }

  return result.slice(0, 200);
}
