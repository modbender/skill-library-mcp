/**
 * Utility primitives: bezierCurve, dashedLine, arrow, strokeText, alienGlyphs.
 */

import { clamp, lerp, makeStroke, splitIntoStrokes } from './helpers.mjs';

// ---------------------------------------------------------------------------
// Metadata
// ---------------------------------------------------------------------------

export const METADATA = [
  {
    name: 'bezierCurve', description: 'Smooth Bezier curve through control points', category: 'utility',
    parameters: {
      points: { type: 'array', required: true, description: 'Array of {x, y} control points (max 20)' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'dashedLine', description: 'Dashed line segment', category: 'utility',
    parameters: {
      startX: { type: 'number', required: true }, startY: { type: 'number', required: true },
      endX: { type: 'number', required: true }, endY: { type: 'number', required: true },
      dashLength: { type: 'number', min: 2, max: 50, default: 10, description: 'Dash length' },
      gapLength: { type: 'number', min: 1, max: 50, default: 5, description: 'Gap length' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'arrow', description: 'Line with arrowhead', category: 'utility',
    parameters: {
      startX: { type: 'number', required: true }, startY: { type: 'number', required: true },
      endX: { type: 'number', required: true }, endY: { type: 'number', required: true },
      headSize: { type: 'number', min: 3, max: 60, default: 15, description: 'Arrowhead size' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'strokeText', description: 'Draw text as single-stroke letterforms', category: 'utility',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      text: { type: 'string', required: true, description: 'Text to draw (max 40 chars)' },
      charHeight: { type: 'number', min: 5, max: 200, default: 30, description: 'Character height' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1 },
      rotation: { type: 'number', description: 'Rotation in degrees' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'alienGlyphs', description: 'Procedural cryptic alien/AI glyphs', category: 'utility',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      count: { type: 'number', min: 1, max: 20, default: 8, description: 'Number of glyphs' },
      glyphSize: { type: 'number', min: 5, max: 100, default: 30, description: 'Glyph size' },
      arrangement: { type: 'string', options: ['line', 'grid', 'scatter', 'circle'], default: 'line', description: 'Layout arrangement' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1 },
      pressureStyle: { type: 'string' },
    },
  },
];

// ---------------------------------------------------------------------------
// Glyph map for strokeText
// ---------------------------------------------------------------------------

const GLYPH_MAP = {
  'A': [[[0,1],[0.5,0],[1,1]],[[0.2,0.6],[0.8,0.6]]],
  'B': [[[0,1],[0,0],[0.7,0],[0.9,0.15],[0.9,0.35],[0.7,0.5],[0,0.5]],[[0.7,0.5],[0.9,0.65],[0.9,0.85],[0.7,1],[0,1]]],
  'C': [[[1,0.1],[0.7,0],[0.3,0],[0,0.3],[0,0.7],[0.3,1],[0.7,1],[1,0.9]]],
  'D': [[[0,0],[0,1],[0.6,1],[0.9,0.8],[1,0.5],[0.9,0.2],[0.6,0],[0,0]]],
  'E': [[[1,0],[0,0],[0,0.5],[0.7,0.5]],[[0,0.5],[0,1],[1,1]]],
  'F': [[[1,0],[0,0],[0,0.5],[0.7,0.5]],[[0,0.5],[0,1]]],
  'G': [[[1,0.1],[0.7,0],[0.3,0],[0,0.3],[0,0.7],[0.3,1],[0.7,1],[1,0.7],[1,0.5],[0.5,0.5]]],
  'H': [[[0,0],[0,1]],[[1,0],[1,1]],[[0,0.5],[1,0.5]]],
  'I': [[[0.3,0],[0.7,0]],[[0.5,0],[0.5,1]],[[0.3,1],[0.7,1]]],
  'J': [[[0.3,0],[0.8,0]],[[0.6,0],[0.6,0.8],[0.4,1],[0.2,0.9]]],
  'K': [[[0,0],[0,1]],[[1,0],[0,0.5],[1,1]]],
  'L': [[[0,0],[0,1],[1,1]]],
  'M': [[[0,1],[0,0],[0.5,0.4],[1,0],[1,1]]],
  'N': [[[0,1],[0,0],[1,1],[1,0]]],
  'O': [[[0.3,0],[0.7,0],[1,0.3],[1,0.7],[0.7,1],[0.3,1],[0,0.7],[0,0.3],[0.3,0]]],
  'P': [[[0,1],[0,0],[0.7,0],[1,0.15],[1,0.35],[0.7,0.5],[0,0.5]]],
  'Q': [[[0.3,0],[0.7,0],[1,0.3],[1,0.7],[0.7,1],[0.3,1],[0,0.7],[0,0.3],[0.3,0]],[[0.6,0.8],[1,1.1]]],
  'R': [[[0,1],[0,0],[0.7,0],[1,0.15],[1,0.35],[0.7,0.5],[0,0.5]],[[0.5,0.5],[1,1]]],
  'S': [[[1,0.1],[0.7,0],[0.3,0],[0,0.15],[0,0.35],[0.3,0.5],[0.7,0.5],[1,0.65],[1,0.85],[0.7,1],[0.3,1],[0,0.9]]],
  'T': [[[0,0],[1,0]],[[0.5,0],[0.5,1]]],
  'U': [[[0,0],[0,0.7],[0.3,1],[0.7,1],[1,0.7],[1,0]]],
  'V': [[[0,0],[0.5,1],[1,0]]],
  'W': [[[0,0],[0.25,1],[0.5,0.5],[0.75,1],[1,0]]],
  'X': [[[0,0],[1,1]],[[1,0],[0,1]]],
  'Y': [[[0,0],[0.5,0.5],[1,0]],[[0.5,0.5],[0.5,1]]],
  'Z': [[[0,0],[1,0],[0,1],[1,1]]],
  '0': [[[0.3,0],[0.7,0],[1,0.3],[1,0.7],[0.7,1],[0.3,1],[0,0.7],[0,0.3],[0.3,0]],[[0.1,0.8],[0.9,0.2]]],
  '1': [[[0.3,0.2],[0.5,0]],[[0.5,0],[0.5,1]],[[0.3,1],[0.7,1]]],
  '2': [[[0,0.15],[0.3,0],[0.7,0],[1,0.15],[1,0.35],[0,1],[1,1]]],
  '3': [[[0,0.1],[0.3,0],[0.7,0],[1,0.15],[1,0.35],[0.7,0.5],[0.5,0.5]],[[0.7,0.5],[1,0.65],[1,0.85],[0.7,1],[0.3,1],[0,0.9]]],
  '4': [[[0,0],[0,0.5],[1,0.5]],[[0.7,0],[0.7,1]]],
  '5': [[[1,0],[0,0],[0,0.5],[0.7,0.5],[1,0.65],[1,0.85],[0.7,1],[0.3,1],[0,0.9]]],
  '6': [[[0.7,0],[0.3,0],[0,0.3],[0,0.7],[0.3,1],[0.7,1],[1,0.7],[1,0.5],[0.7,0.4],[0,0.5]]],
  '7': [[[0,0],[1,0],[0.3,1]]],
  '8': [[[0.3,0],[0.7,0],[1,0.15],[1,0.35],[0.7,0.5],[0.3,0.5],[0,0.15],[0,0.35],[0.3,0.5]],[[0.3,0.5],[0,0.65],[0,0.85],[0.3,1],[0.7,1],[1,0.85],[1,0.65],[0.7,0.5]]],
  '9': [[[1,0.5],[0.3,0.6],[0,0.3],[0,0.15],[0.3,0],[0.7,0],[1,0.3],[1,0.7],[0.7,1],[0.3,1]]],
  ' ': [],
  '.': [[[0.4,0.9],[0.6,0.9],[0.6,1],[0.4,1],[0.4,0.9]]],
  ',': [[[0.5,0.85],[0.5,1],[0.3,1.15]]],
  '!': [[[0.5,0],[0.5,0.7]],[[0.45,0.9],[0.55,0.9],[0.55,1],[0.45,1],[0.45,0.9]]],
  '?': [[[0.1,0.15],[0.3,0],[0.7,0],[0.9,0.15],[0.9,0.35],[0.5,0.55],[0.5,0.7]],[[0.45,0.9],[0.55,0.9],[0.55,1],[0.45,1],[0.45,0.9]]],
  '-': [[[0.2,0.5],[0.8,0.5]]],
  ':': [[[0.45,0.25],[0.55,0.25],[0.55,0.35],[0.45,0.35],[0.45,0.25]],[[0.45,0.65],[0.55,0.65],[0.55,0.75],[0.45,0.75],[0.45,0.65]]],
  '/': [[[0.1,1],[0.9,0]]],
  '\'': [[[0.45,0],[0.5,0.2]]],
};

// ---------------------------------------------------------------------------
// Primitives
// ---------------------------------------------------------------------------

export function bezierCurve(points, color, brushSize, opacity, pressureStyle) {
  if (!Array.isArray(points) || points.length < 2) return [];
  const cps = points.slice(0, 20).map(p => ({ x: Number(p.x) || 0, y: Number(p.y) || 0 }));
  brushSize = clamp(Number(brushSize) || 5, 3, 100);

  const result = [];
  const stepsPerSeg = 12;
  for (let i = 0; i < cps.length - 1; i++) {
    const p0 = cps[Math.max(0, i - 1)];
    const p1 = cps[i];
    const p2 = cps[Math.min(cps.length - 1, i + 1)];
    const p3 = cps[Math.min(cps.length - 1, i + 2)];
    for (let s = 0; s < stepsPerSeg; s++) {
      const t = s / stepsPerSeg;
      const t2 = t * t, t3 = t2 * t;
      result.push({
        x: 0.5 * (2*p1.x + (-p0.x+p2.x)*t + (2*p0.x-5*p1.x+4*p2.x-p3.x)*t2 + (-p0.x+3*p1.x-3*p2.x+p3.x)*t3),
        y: 0.5 * (2*p1.y + (-p0.y+p2.y)*t + (2*p0.y-5*p1.y+4*p2.y-p3.y)*t2 + (-p0.y+3*p1.y-3*p2.y+p3.y)*t3),
      });
    }
  }
  result.push(cps[cps.length - 1]);

  return splitIntoStrokes(result, color, brushSize, opacity, pressureStyle);
}

export function dashedLine(startX, startY, endX, endY, dashLength, gapLength, color, brushSize, pressureStyle) {
  startX = Number(startX) || 0; startY = Number(startY) || 0;
  endX = Number(endX) || 100; endY = Number(endY) || 0;
  dashLength = clamp(Number(dashLength) || 10, 2, 50);
  gapLength = clamp(Number(gapLength) || 5, 1, 50);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);

  const total = Math.hypot(endX - startX, endY - startY);
  if (total < 1) return [];
  const dx = (endX - startX) / total, dy = (endY - startY) / total;

  const result = [];
  let d = 0;
  while (d < total && result.length < 200) {
    const end = Math.min(d + dashLength, total);
    result.push(makeStroke([
      { x: startX + dx * d, y: startY + dy * d },
      { x: startX + dx * end, y: startY + dy * end },
    ], color, brushSize, 0.9, pressureStyle));
    d = end + gapLength;
  }
  return result;
}

export function arrow(startX, startY, endX, endY, headSize, color, brushSize, pressureStyle) {
  startX = Number(startX) || 0; startY = Number(startY) || 0;
  endX = Number(endX) || 100; endY = Number(endY) || 0;
  headSize = clamp(Number(headSize) || 15, 3, 60);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);

  const dx = endX - startX, dy = endY - startY;
  const angle = Math.atan2(dy, dx);
  const ha = Math.PI * 0.8;

  const result = [];
  result.push(makeStroke([{ x: startX, y: startY }, { x: endX, y: endY }], color, brushSize, 0.9, pressureStyle));
  result.push(makeStroke([
    { x: endX + Math.cos(angle + Math.PI - ha) * headSize, y: endY + Math.sin(angle + Math.PI - ha) * headSize },
    { x: endX, y: endY },
    { x: endX + Math.cos(angle + Math.PI + ha) * headSize, y: endY + Math.sin(angle + Math.PI + ha) * headSize },
  ], color, brushSize, 0.9, pressureStyle));

  return result;
}

export function strokeText(cx, cy, text, charHeight, color, brushSize, opacity, rotation, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  text = String(text || 'HELLO').toUpperCase().slice(0, 40);
  charHeight = clamp(Number(charHeight) || 30, 5, 200);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.9, 0.01, 1);
  rotation = (Number(rotation) || 0) * Math.PI / 180;

  const charWidth = charHeight * 0.7;
  const spacing = charHeight * 0.15;
  const totalWidth = text.length * (charWidth + spacing) - spacing;

  const result = [];
  let cursorX = cx - totalWidth / 2;

  for (const ch of text) {
    const glyph = GLYPH_MAP[ch];
    if (!glyph || glyph.length === 0) {
      cursorX += charWidth + spacing;
      continue;
    }

    for (const polyline of glyph) {
      if (polyline.length < 2) continue;
      const pts = polyline.map(([gx, gy]) => {
        const lx = cursorX + gx * charWidth - cx;
        const ly = cy + gy * charHeight - charHeight / 2 - cy;
        return {
          x: cx + lx * Math.cos(rotation) - ly * Math.sin(rotation),
          y: cy + lx * Math.sin(rotation) + ly * Math.cos(rotation),
        };
      });
      result.push(makeStroke(pts, color, brushSize, opacity, pressureStyle));
      if (result.length >= 200) break;
    }
    cursorX += charWidth + spacing;
    if (result.length >= 200) break;
  }

  return result.slice(0, 200);
}

export function alienGlyphs(cx, cy, count, glyphSize, arrangement, color, brushSize, opacity, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  count = clamp(Math.round(Number(count) || 8), 1, 20);
  glyphSize = clamp(Number(glyphSize) || 30, 5, 100);
  arrangement = String(arrangement || 'line').toLowerCase();
  brushSize = clamp(Number(brushSize) || 2, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const result = [];
  const spacing = glyphSize * 1.4;

  const positions = [];
  for (let i = 0; i < count; i++) {
    let gx, gy;
    if (arrangement === 'grid') {
      const cols = Math.ceil(Math.sqrt(count));
      const col = i % cols, row = Math.floor(i / cols);
      const totalW = (cols - 1) * spacing, totalH = (Math.ceil(count / cols) - 1) * spacing;
      gx = cx - totalW / 2 + col * spacing;
      gy = cy - totalH / 2 + row * spacing;
    } else if (arrangement === 'scatter') {
      const r = glyphSize * 2 + Math.random() * glyphSize * 3;
      const a = Math.random() * Math.PI * 2;
      gx = cx + Math.cos(a) * r;
      gy = cy + Math.sin(a) * r;
    } else if (arrangement === 'circle') {
      const a = (i / count) * Math.PI * 2 - Math.PI / 2;
      const r = spacing * count / (Math.PI * 2) + glyphSize;
      gx = cx + Math.cos(a) * r;
      gy = cy + Math.sin(a) * r;
    } else {
      const totalW = (count - 1) * spacing;
      gx = cx - totalW / 2 + i * spacing;
      gy = cy;
    }
    positions.push({ x: gx, y: gy });
  }

  for (const pos of positions) {
    if (result.length >= 200) break;
    const half = glyphSize / 2;

    const numElements = 2 + Math.floor(Math.random() * 3);
    for (let e = 0; e < numElements && result.length < 200; e++) {
      const type = Math.random();

      if (type < 0.2) {
        const x1 = pos.x + (Math.random() - 0.5) * glyphSize * 0.6;
        const y1 = pos.y - half * (0.5 + Math.random() * 0.5);
        const y2 = pos.y + half * (0.5 + Math.random() * 0.5);
        const lean = (Math.random() - 0.5) * glyphSize * 0.3;
        result.push(makeStroke([{ x: x1, y: y1 }, { x: x1 + lean, y: y2 }], color, brushSize, opacity, pressureStyle));
      } else if (type < 0.4) {
        const pts = [];
        const arcSteps = 8 + Math.floor(Math.random() * 8);
        const startA = Math.random() * Math.PI * 2;
        const sweep = (0.5 + Math.random()) * Math.PI;
        const r = half * (0.3 + Math.random() * 0.5);
        const acx = pos.x + (Math.random() - 0.5) * half * 0.5;
        const acy = pos.y + (Math.random() - 0.5) * half * 0.5;
        for (let s = 0; s <= arcSteps; s++) {
          const a = startA + (s / arcSteps) * sweep;
          pts.push({ x: acx + Math.cos(a) * r, y: acy + Math.sin(a) * r });
        }
        result.push(makeStroke(pts, color, brushSize, opacity, pressureStyle));
      } else if (type < 0.55) {
        const dots = 1 + Math.floor(Math.random() * 3);
        for (let d = 0; d < dots && result.length < 200; d++) {
          const dx = pos.x + (Math.random() - 0.5) * glyphSize * 0.5;
          const dy = pos.y + (Math.random() - 0.5) * glyphSize * 0.6;
          result.push(makeStroke([{ x: dx, y: dy }, { x: dx + 1, y: dy + 1 }], color, brushSize * 1.5, opacity, pressureStyle));
        }
      } else if (type < 0.7) {
        const y = pos.y + (Math.random() - 0.5) * glyphSize * 0.6;
        const x1 = pos.x - half * (0.2 + Math.random() * 0.4);
        const x2 = pos.x + half * (0.2 + Math.random() * 0.4);
        result.push(makeStroke([{ x: x1, y }, { x: x2, y }], color, brushSize, opacity, pressureStyle));
      } else if (type < 0.85) {
        const pts = [];
        const segs = 2 + Math.floor(Math.random() * 3);
        let px = pos.x + (Math.random() - 0.5) * half;
        let py = pos.y - half * 0.8;
        pts.push({ x: px, y: py });
        for (let s = 0; s < segs; s++) {
          px += (Math.random() - 0.5) * glyphSize * 0.5;
          py += glyphSize * (0.3 + Math.random() * 0.3) / segs;
          pts.push({ x: px, y: py });
        }
        result.push(makeStroke(pts, color, brushSize, opacity, pressureStyle));
      } else {
        const r = half * (0.15 + Math.random() * 0.25);
        const ringCx = pos.x + (Math.random() - 0.5) * half * 0.6;
        const ringCy = pos.y + (Math.random() - 0.5) * half * 0.6;
        const pts = [];
        const steps = 12;
        for (let s = 0; s <= steps; s++) {
          const a = (s / steps) * Math.PI * 2;
          pts.push({ x: ringCx + Math.cos(a) * r, y: ringCy + Math.sin(a) * r });
        }
        result.push(makeStroke(pts, color, brushSize, opacity, pressureStyle));
      }
    }
  }

  return result.slice(0, 200);
}
