/**
 * Organic/natural primitives: lSystem, flower, leaf, vine, spaceColonization, mycelium, barnsleyFern.
 */

import { clamp, lerp, lerpColor, makeStroke, splitIntoStrokes, samplePalette } from './helpers.mjs';

/**
 * Interpolate points between two coordinates to create denser geometry.
 * This prevents miter joint artifacts in space colonization strokes.
 * @param {Object} from - Starting point {x, y}
 * @param {Object} to - Ending point {x, y}
 * @param {number} maxSegmentLength - Maximum distance between interpolated points (default: 5)
 * @returns {Array} Interpolated points (includes from, excludes to)
 */
function interpolatePoints(from, to, maxSegmentLength = 5) {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const distance = Math.hypot(dx, dy);

  if (distance <= maxSegmentLength) {
    return [from];
  }

  // Calculate number of segments needed
  const numSegments = Math.ceil(distance / maxSegmentLength);
  const result = [];

  for (let i = 0; i < numSegments; i++) {
    const t = i / numSegments;
    result.push({
      x: from.x + dx * t,
      y: from.y + dy * t,
    });
  }

  return result;
}

// ---------------------------------------------------------------------------
// Metadata
// ---------------------------------------------------------------------------

export const METADATA = [
  {
    name: 'lSystem', description: 'L-System branching structures (fern, tree, bush, coral, seaweed)', category: 'organic',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      preset: { type: 'string', required: true, options: ['fern', 'tree', 'bush', 'coral', 'seaweed'], description: 'L-System preset (controls shape rules)' },
      iterations: { type: 'number', min: 1, max: 5, description: 'Iteration depth (max varies by preset)' },
      scale: { type: 'number', min: 0.1, max: 5, default: 3, description: 'Size multiplier (0.5=small, 2=large)' },
      rotation: { type: 'number', description: 'Starting rotation in degrees' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      palette: { type: 'string', options: ['magma', 'plasma', 'viridis', 'turbo', 'inferno'], description: 'Color palette (gradient)' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'flower', description: 'Multi-petal flower with filled center spiral', category: 'organic',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      petals: { type: 'number', min: 3, max: 20, default: 8, description: 'Number of petals' },
      petalLength: { type: 'number', min: 10, max: 300, default: 60, description: 'Petal length' },
      petalWidth: { type: 'number', min: 5, max: 150, default: 25, description: 'Petal width' },
      centerRadius: { type: 'number', min: 5, max: 100, default: 20, description: 'Center circle size' },
      petalColor: { type: 'string', description: 'Petal color (hex)' },
      centerColor: { type: 'string', description: 'Center color (hex)' },
      brushSize: { type: 'number', min: 3, max: 100 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'leaf', description: 'Single leaf with midrib and veins', category: 'organic',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      length: { type: 'number', min: 10, max: 300, default: 200, description: 'Leaf length' },
      width: { type: 'number', min: 5, max: 150, default: 80, description: 'Leaf width' },
      rotation: { type: 'number', description: 'Rotation in degrees' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      veinCount: { type: 'number', min: 0, max: 12, default: 4, description: 'Number of veins' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'vine', description: 'Curving vine with small leaves', category: 'organic',
    parameters: {
      startX: { type: 'number', required: true }, startY: { type: 'number', required: true },
      endX: { type: 'number', required: true }, endY: { type: 'number', required: true },
      curveAmount: { type: 'number', min: 0, max: 300, default: 50, description: 'Curve intensity' },
      leafCount: { type: 'number', min: 0, max: 20, default: 5, description: 'Number of leaves' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'spaceColonization', description: 'Space colonization algorithm (roots, veins, lightning)', category: 'organic',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      width: { type: 'number', min: 20, max: 600, default: 300, description: 'Area width' },
      height: { type: 'number', min: 20, max: 600, default: 300, description: 'Area height' },
      density: { type: 'number', min: 0.1, max: 1, default: 0.5, description: 'Attractor density' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      palette: { type: 'string', description: 'Color palette' },
      stepLength: { type: 'number', min: 2, max: 30, default: 8, description: 'Growth step length' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'mycelium', description: 'Organic branching mycelium network', category: 'organic',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      radius: { type: 'number', min: 20, max: 500, default: 180, description: 'Spread radius' },
      density: { type: 'number', min: 0.1, max: 1, default: 0.5, description: 'Branch density' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      palette: { type: 'string', description: 'Color palette' },
      branchiness: { type: 'number', min: 0.1, max: 1, default: 0.5, description: 'Branch probability' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'barnsleyFern', description: 'Barnsley Fern IFS fractal', category: 'organic',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      scale: { type: 'number', min: 3, max: 100, default: 30, description: 'Size scale' },
      iterations: { type: 'number', min: 500, max: 8000, default: 2000, description: 'Point count' },
      lean: { type: 'number', min: -30, max: 30, default: 0, description: 'Lean angle in degrees' },
      curl: { type: 'number', min: 0.5, max: 1.5, default: 1, description: 'Curl factor' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      palette: { type: 'string', description: 'Color palette' },
      pressureStyle: { type: 'string' },
    },
  },
];

// ---------------------------------------------------------------------------
// Primitives
// ---------------------------------------------------------------------------

const L_SYSTEM_PRESETS = {
  fern:    { axiom: 'X', rules: { X: 'F+[[X]-X]-F[-FX]+X', F: 'FF' }, angle: 25, maxIter: 5 },
  tree:    { axiom: 'F', rules: { F: 'FF+[+F-F-F]-[-F+F+F]' },        angle: 22, maxIter: 4 },
  bush:    { axiom: 'F', rules: { F: 'F[+F]F[-F]F' },                  angle: 25, maxIter: 4 },
  coral:   { axiom: 'F', rules: { F: 'FF-[-F+F+F]+[+F-F-F]' },        angle: 22, maxIter: 4 },
  seaweed: { axiom: 'F', rules: { F: 'F[+F]F[-F]+F' },                 angle: 20, maxIter: 5 },
};

export function lSystem(cx, cy, preset, iterations, scale, rotation, color, brushSize, palette, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  const cfg = L_SYSTEM_PRESETS[preset] || L_SYSTEM_PRESETS.tree;
  iterations = clamp(Math.round(Number(iterations) || cfg.maxIter), 1, cfg.maxIter);
  scale = clamp(Number(scale) || 3, 0.1, 5);
  const startAngle = (Number(rotation) || -90);

  let str = cfg.axiom;
  for (let i = 0; i < iterations; i++) {
    let next = '';
    for (const ch of str) next += cfg.rules[ch] ?? ch;
    str = next;
    if (str.length > 50000) break;
  }

  const baseStepLen = 4 * scale;
  const baseTurnRad = cfg.angle * Math.PI / 180;
  const strokes = [];
  const stack = [];
  let x = cx, y = cy, angle = startAngle * Math.PI / 180;
  let cur = [{ x, y }];
  let depth = 0;
  let maxDepth = 0;

  let tempDepth = 0;
  for (const ch of str) {
    if (ch === '[') { tempDepth++; if (tempDepth > maxDepth) maxDepth = tempDepth; }
    else if (ch === ']') tempDepth--;
  }
  maxDepth = maxDepth || 1;

  for (const ch of str) {
    if (ch === 'F') {
      const stepJitter = baseStepLen * (1 + (Math.random() - 0.5) * 0.3);
      x += Math.cos(angle) * stepJitter;
      y += Math.sin(angle) * stepJitter;
      cur.push({ x, y });
    } else if (ch === '+') { angle += baseTurnRad + (Math.random() - 0.5) * 0.087; }
    else if (ch === '-') { angle -= baseTurnRad + (Math.random() - 0.5) * 0.087; }
    else if (ch === '[') {
      stack.push({ x, y, angle, depth });
      depth++;
    } else if (ch === ']') {
      if (cur.length > 1) {
        const t = depth / maxDepth;
        const c = palette ? samplePalette(palette, t) : color;
        strokes.push(makeStroke(cur, c, brushSize, 0.9, pressureStyle));
      }
      if (stack.length > 0) {
        const s = stack.pop();
        x = s.x; y = s.y; angle = s.angle; depth = s.depth;
      }
      cur = [{ x, y }];
    }
    if (strokes.length >= 200) break;
  }
  if (cur.length > 1) {
    const t = depth / maxDepth;
    const c = palette ? samplePalette(palette, t) : color;
    strokes.push(makeStroke(cur, c, brushSize, 0.9, pressureStyle));
  }

  return strokes.slice(0, 200);
}

export function flower(cx, cy, petals, petalLength, petalWidth, centerRadius, petalColor, centerColor, brushSize, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  petals = clamp(Math.round(Number(petals) || 8), 3, 20);
  petalLength = clamp(Number(petalLength) || 60, 10, 300);
  petalWidth = clamp(Number(petalWidth) || 25, 5, 150);
  centerRadius = clamp(Number(centerRadius) || 20, 5, 100);
  brushSize = clamp(Number(brushSize) || 8, 3, 100);

  const result = [];

  // Petals — each petal gets a two-color gradient from petalColor (base) to centerColor (tip)
  for (let i = 0; i < petals; i++) {
    const a = (i / petals) * Math.PI * 2;
    const dx = Math.cos(a), dy = Math.sin(a);
    const nx = -dy, ny = dx;
    const thisLength = petalLength * (1 + (Math.random() - 0.5) * 0.2);

    const bands = 3;
    for (let b = 0; b < bands; b++) {
      const tStart = b / bands;
      const tEnd = (b + 1) / bands;
      const gradT = (b + 0.5) / bands;
      const c = lerpColor(petalColor || '#ff6688', centerColor || '#ffcc00', gradT);

      const pts = [];
      const stepsPerBand = 8;
      for (let j = 0; j <= stepsPerBand; j++) {
        const localT = j / stepsPerBand;
        const t = tStart + localT * (tEnd - tStart);
        const along = t * thisLength;
        const across = Math.sin(t * Math.PI) * petalWidth * 0.5;
        pts.push({ x: cx + dx * along + nx * across, y: cy + dy * along + ny * across });
      }
      for (let j = stepsPerBand; j >= 0; j--) {
        const localT = j / stepsPerBand;
        const t = tStart + localT * (tEnd - tStart);
        const along = t * thisLength;
        const across = -Math.sin(t * Math.PI) * petalWidth * 0.5;
        pts.push({ x: cx + dx * along + nx * across, y: cy + dy * along + ny * across });
      }
      result.push(makeStroke(pts, c, brushSize, 0.85, pressureStyle));
    }
  }

  const centerPts = [];
  const cSteps = 40;
  for (let i = 0; i <= cSteps; i++) {
    const t = i / cSteps;
    const a = t * Math.PI * 4;
    const r = centerRadius * (1 - t * 0.8);
    centerPts.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
  }
  result.push(makeStroke(centerPts, centerColor, clamp(centerRadius * 0.8, 5, 60), 0.9, pressureStyle));

  return result;
}

export function leaf(cx, cy, length, width, rotation, color, brushSize, veinCount, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  length = clamp(Number(length) || 200, 10, 300);
  width = clamp(Number(width) || 80, 5, 150);
  rotation = (Number(rotation) || 0) * Math.PI / 180;
  veinCount = clamp(Math.round(Number(veinCount) || 4), 0, 12);
  brushSize = clamp(Number(brushSize) || 5, 3, 100);

  const result = [];

  const pts = [];
  const steps = 24;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    let lx, ly;
    if (t < 0.5) {
      const s = t * 2;
      lx = s * length;
      ly = Math.sin(s * Math.PI) * width * 0.5;
    } else {
      const s = (1 - t) * 2;
      lx = s * length;
      ly = -Math.sin(s * Math.PI) * width * 0.5;
    }
    const rx = lx * Math.cos(rotation) - ly * Math.sin(rotation);
    const ry = lx * Math.sin(rotation) + ly * Math.cos(rotation);
    pts.push({ x: cx + rx, y: cy + ry });
  }
  result.push(makeStroke(pts, color, brushSize, 0.85, pressureStyle));

  const midPts = [
    { x: cx, y: cy },
    { x: cx + Math.cos(rotation) * length, y: cy + Math.sin(rotation) * length },
  ];
  result.push(makeStroke(midPts, color, clamp(brushSize * 0.6, 3, 20), 0.7, pressureStyle));

  for (let i = 0; i < veinCount; i++) {
    const t = (i + 1) / (veinCount + 1);
    const baseX = cx + Math.cos(rotation) * length * t;
    const baseY = cy + Math.sin(rotation) * length * t;
    const veinLen = width * 0.4 * Math.sin(t * Math.PI);
    const perpAngle = rotation + Math.PI / 2;
    const sign = i % 2 === 0 ? 1 : -1;
    const tipX = baseX + Math.cos(perpAngle) * veinLen * sign + Math.cos(rotation) * veinLen * 0.3;
    const tipY = baseY + Math.sin(perpAngle) * veinLen * sign + Math.sin(rotation) * veinLen * 0.3;
    result.push(makeStroke([{ x: baseX, y: baseY }, { x: tipX, y: tipY }], color, clamp(brushSize * 0.4, 3, 10), 0.5, pressureStyle));
  }

  return result;
}

export function vine(startX, startY, endX, endY, curveAmount, leafCount, color, brushSize, pressureStyle) {
  startX = Number(startX) || 0; startY = Number(startY) || 0;
  endX = Number(endX) || 100; endY = Number(endY) || 0;
  curveAmount = clamp(Number(curveAmount) || 50, 0, 300);
  leafCount = clamp(Math.round(Number(leafCount) || 5), 0, 20);
  brushSize = clamp(Number(brushSize) || 4, 3, 100);

  const result = [];

  const mx = (startX + endX) / 2 + (Math.random() - 0.5) * curveAmount;
  const my = (startY + endY) / 2 + (Math.random() - 0.5) * curveAmount;
  const vinePts = [];
  const steps = 30;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = (1-t)*(1-t)*startX + 2*(1-t)*t*mx + t*t*endX;
    const y = (1-t)*(1-t)*startY + 2*(1-t)*t*my + t*t*endY;
    vinePts.push({ x, y });
  }
  result.push(makeStroke(vinePts, color, brushSize, 0.9, pressureStyle));

  for (let i = 0; i < leafCount; i++) {
    const t = (i + 0.5) / leafCount;
    const idx = Math.floor(t * steps);
    const base = vinePts[idx];
    const next = vinePts[Math.min(idx + 1, steps)];
    const dx = next.x - base.x, dy = next.y - base.y;
    const len = Math.hypot(dx, dy) || 1;
    const perpX = -dy / len, perpY = dx / len;
    const side = i % 2 === 0 ? 1 : -1;
    const leafLen = 12 + Math.random() * 10;
    const lPts = [
      { x: base.x, y: base.y },
      { x: base.x + perpX * leafLen * side * 0.5 + dx / len * leafLen * 0.3, y: base.y + perpY * leafLen * side * 0.5 + dy / len * leafLen * 0.3 },
      { x: base.x + perpX * leafLen * side, y: base.y + perpY * leafLen * side },
    ];
    result.push(makeStroke(lPts, color, clamp(brushSize * 0.6, 3, 20), 0.7, pressureStyle));
  }

  return result;
}

export function spaceColonization(cx, cy, width, height, density, color, brushSize, palette, stepLength, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 20, 600);
  height = clamp(Number(height) || 300, 20, 600);
  density = clamp(Number(density) || 0.5, 0.1, 1);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);

  const numAttractors = Math.round(30 * density);
  const attractors = [];
  for (let i = 0; i < numAttractors; i++) {
    attractors.push({
      x: cx + (Math.random() - 0.5) * width,
      y: cy + (Math.random() - 0.5) * height,
      alive: true,
    });
  }

  stepLength = clamp(Number(stepLength) || 8, 2, 30);
  const nodes = [{ x: cx, y: cy + height * 0.4, parent: -1 }];
  const killDist = 10, attractDist = width * 0.4, stepLen = stepLength;

  for (let iter = 0; iter < 100; iter++) {
    const dirs = new Array(nodes.length).fill(null).map(() => ({ x: 0, y: 0, count: 0 }));

    for (const att of attractors) {
      if (!att.alive) continue;
      let closest = -1, closestDist = Infinity;
      for (let n = 0; n < nodes.length; n++) {
        const d = Math.hypot(att.x - nodes[n].x, att.y - nodes[n].y);
        if (d < closestDist) { closestDist = d; closest = n; }
      }
      if (closestDist < killDist) { att.alive = false; continue; }
      if (closestDist < attractDist && closest >= 0) {
        const d = closestDist || 1;
        dirs[closest].x += (att.x - nodes[closest].x) / d;
        dirs[closest].y += (att.y - nodes[closest].y) / d;
        dirs[closest].count++;
      }
    }

    let grew = false;
    for (let n = 0; n < dirs.length; n++) {
      if (dirs[n].count === 0) continue;
      const len = Math.hypot(dirs[n].x, dirs[n].y) || 1;
      nodes.push({
        x: nodes[n].x + (dirs[n].x / len) * stepLen,
        y: nodes[n].y + (dirs[n].y / len) * stepLen,
        parent: n,
      });
      grew = true;
      if (nodes.length >= 500) break;
    }
    if (!grew || nodes.length >= 500) break;
  }

  const result = [];
  const isLeaf = new Array(nodes.length).fill(true);
  for (const n of nodes) if (n.parent >= 0) isLeaf[n.parent] = false;

  for (let i = 0; i < nodes.length && result.length < 200; i++) {
    if (!isLeaf[i]) continue;
    const pts = [];
    let idx = i;
    const nodePath = [];
    while (idx >= 0) {
      nodePath.unshift(idx);
      idx = nodes[idx].parent;
    }

    // Interpolate points between algorithm nodes to prevent miter joint artifacts
    // Use maxSegmentLength = 5 for smooth strokes with proper miter calculation
    for (let n = 0; n < nodePath.length; n++) {
      const node = nodes[nodePath[n]];
      if (n === 0) {
        pts.push({ x: node.x, y: node.y });
      } else {
        const prevNode = nodes[nodePath[n - 1]];
        const interpolated = interpolatePoints(prevNode, node, 5);
        for (let p = 1; p < interpolated.length; p++) {
          pts.push(interpolated[p]);
        }
        pts.push({ x: node.x, y: node.y });
      }
      if (pts.length >= 100) break;
    }

    if (pts.length > 1) {
      const t = palette ? clamp(1 - pts.length / 20, 0, 1) : 0;
      const c = palette ? samplePalette(palette, t) : color;
      result.push(makeStroke(pts, c, brushSize, 0.8, pressureStyle));
    }
  }

  return result.slice(0, 200);
}

export function mycelium(cx, cy, radius, density, color, brushSize, palette, branchiness, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 180, 20, 500);
  density = clamp(Number(density) || 0.5, 0.1, 1);
  brushSize = clamp(Number(brushSize) || 3, 3, 10);
  branchiness = clamp(Number(branchiness) || 0.5, 0.1, 1.0);

  const numSeeds = Math.round(3 + density * 2);
  const seeds = [];
  for (let i = 0; i < numSeeds; i++) {
    const a = (i / numSeeds) * Math.PI * 2 + Math.random() * 0.5;
    const r = radius * (0.1 + Math.random() * 0.2);
    seeds.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
  }

  const result = [];
  const stepLen = 4 + Math.random() * 3;
  const branchProb = 0.04 + branchiness * 0.12;
  const maxBranches = Math.round(150 * density);

  for (const seed of seeds) {
    const tips = [{ x: seed.x, y: seed.y, angle: Math.random() * Math.PI * 2, depth: 0 }];
    let branches = 0;

    while (tips.length > 0 && branches < maxBranches && result.length < 200) {
      const tip = tips.shift();
      const pts = [{ x: tip.x, y: tip.y }];
      let { x, y, angle, depth } = tip;
      const steps = 5 + Math.floor(Math.random() * 10);

      for (let s = 0; s < steps; s++) {
        angle += (Math.random() - 0.5) * 0.6;
        x += Math.cos(angle) * stepLen;
        y += Math.sin(angle) * stepLen;
        pts.push({ x, y });

        if (Math.hypot(x - cx, y - cy) > radius) break;

        if (Math.random() < branchProb && depth < 6) {
          tips.push({ x, y, angle: angle + (Math.random() - 0.5) * 1.2, depth: depth + 1 });
        }
      }

      if (pts.length > 1) {
        const t = palette ? clamp(depth / 5, 0, 1) : 0;
        const c = palette ? samplePalette(palette, t) : color;
        const size = Math.max(3, brushSize - depth * 0.3);
        result.push(makeStroke(pts, c, size, 0.6 + Math.random() * 0.2, pressureStyle));
        branches++;
      }
    }
  }

  return result.slice(0, 200);
}

export function barnsleyFern(cx, cy, scale, iterations, lean, curl, color, brushSize, palette, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  scale = clamp(Number(scale) || 30, 3, 100);
  iterations = clamp(Math.round(Number(iterations) || 2000), 500, 8000);
  lean = clamp(Number(lean) || 0, -30, 30) * Math.PI / 180;
  curl = clamp(Number(curl) || 1.0, 0.5, 1.5);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);

  let x = 0, y = 0;
  const allPts = [];
  for (let i = 0; i < iterations; i++) {
    const r = Math.random();
    let nx, ny;
    if (r < 0.01) {
      nx = 0;
      ny = 0.16 * y;
    } else if (r < 0.86) {
      nx = 0.85 * x + 0.04 * y;
      ny = -0.04 * x + (0.85 * curl) * y + 1.6;
    } else if (r < 0.93) {
      nx = 0.2 * x - 0.26 * y;
      ny = 0.23 * x + 0.22 * y + 1.6;
    } else {
      nx = -0.15 * x + 0.28 * y;
      ny = 0.26 * x + 0.24 * y + 0.44;
    }
    x = nx; y = ny;

    const rx = (x * Math.cos(lean) - y * Math.sin(lean)) * scale + cx;
    const ry = (-y * Math.cos(lean) - x * Math.sin(lean)) * scale + cy;
    allPts.push({ x: rx, y: ry, rawY: y });
  }

  allPts.sort((a, b) => a.rawY - b.rawY);

  const result = [];
  const segSize = Math.max(10, Math.floor(allPts.length / 60));
  const maxRawY = allPts[allPts.length - 1]?.rawY || 1;

  for (let i = 0; i < allPts.length && result.length < 200; i += segSize) {
    const seg = allPts.slice(i, i + segSize);
    if (seg.length < 2) continue;
    seg.sort((a, b) => a.x - b.x || a.y - b.y);
    const t = palette ? clamp(seg[0].rawY / maxRawY, 0, 1) : 0;
    const c = palette ? samplePalette(palette, t) : color;
    result.push(makeStroke(
      seg.map(p => ({ x: p.x, y: p.y })),
      c, brushSize, 0.75, pressureStyle
    ));
  }

  return result.slice(0, 200);
}
