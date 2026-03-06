/**
 * Basic shape primitives: circle, ellipse, arc, rectangle, polygon, star.
 */

import { clamp, lerp, makeStroke, splitIntoStrokes } from './helpers.mjs';

// ---------------------------------------------------------------------------
// Metadata for registry auto-discovery
// ---------------------------------------------------------------------------

export const METADATA = [
  {
    name: 'circle', description: 'Smooth circle', category: 'basic-shapes',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      radius: { type: 'number', required: true, min: 1, max: 500, default: 150, description: 'Circle radius' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1, default: 0.9 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'ellipse', description: 'Rotated oval', category: 'basic-shapes',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      radiusX: { type: 'number', required: true, min: 1, max: 500, default: 170, description: 'Horizontal radius' },
      radiusY: { type: 'number', required: true, min: 1, max: 500, default: 110, description: 'Vertical radius' },
      rotation: { type: 'number', description: 'Rotation in degrees' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1, default: 0.9 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'arc', description: 'Partial circle arc', category: 'basic-shapes',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      radius: { type: 'number', required: true, min: 1, max: 500, default: 150, description: 'Arc radius' },
      startAngle: { type: 'number', required: true, description: 'Start angle in degrees' },
      endAngle: { type: 'number', required: true, description: 'End angle in degrees' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1, default: 0.9 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'rectangle', description: 'Rectangle outline', category: 'basic-shapes',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      width: { type: 'number', required: true, min: 2, max: 1000, default: 300, description: 'Rectangle width' },
      height: { type: 'number', required: true, min: 2, max: 1000, default: 200, description: 'Rectangle height' },
      rotation: { type: 'number', description: 'Rotation in degrees' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1, default: 0.9 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'polygon', description: 'Regular N-sided polygon', category: 'basic-shapes',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      radius: { type: 'number', required: true, min: 1, max: 500, default: 150, description: 'Polygon radius' },
      sides: { type: 'number', required: true, min: 3, max: 24, default: 6, description: 'Number of sides' },
      rotation: { type: 'number', description: 'Rotation in degrees' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1, default: 0.9 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'star', description: 'N-pointed star', category: 'basic-shapes',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      outerR: { type: 'number', required: true, min: 5, max: 500, default: 150, description: 'Outer radius' },
      innerR: { type: 'number', required: true, min: 2, max: 499, default: 65, description: 'Inner radius' },
      points: { type: 'number', required: true, min: 3, max: 20, default: 5, description: 'Number of points' },
      rotation: { type: 'number', description: 'Rotation in degrees' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1, default: 0.9 },
      pressureStyle: { type: 'string' },
    },
  },
];

// ---------------------------------------------------------------------------
// Primitives
// ---------------------------------------------------------------------------

export function circle(cx, cy, radius, color, brushSize, opacity, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 150, 1, 500);
  const steps = clamp(Math.round(radius * 0.5), 24, 200);
  const pts = [];
  for (let i = 0; i <= steps; i++) {
    const a = (i / steps) * Math.PI * 2;
    const wobble = radius * (1 + (Math.random() - 0.5) * 0.04);
    pts.push({ x: cx + Math.cos(a) * wobble, y: cy + Math.sin(a) * wobble });
  }
  return splitIntoStrokes(pts, color, brushSize, opacity, pressureStyle);
}

export function ellipse(cx, cy, radiusX, radiusY, rotation, color, brushSize, opacity, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  radiusX = clamp(Number(radiusX) || 170, 1, 500);
  radiusY = clamp(Number(radiusY) || 110, 1, 500);
  rotation = (Number(rotation) || 0) * Math.PI / 180;
  const steps = clamp(Math.round(Math.max(radiusX, radiusY) * 0.5), 24, 200);
  const pts = [];
  for (let i = 0; i <= steps; i++) {
    const a = (i / steps) * Math.PI * 2;
    const lx = Math.cos(a) * radiusX, ly = Math.sin(a) * radiusY;
    pts.push({
      x: cx + lx * Math.cos(rotation) - ly * Math.sin(rotation),
      y: cy + lx * Math.sin(rotation) + ly * Math.cos(rotation),
    });
  }
  return splitIntoStrokes(pts, color, brushSize, opacity, pressureStyle);
}

export function arc(cx, cy, radius, startAngle, endAngle, color, brushSize, opacity, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 150, 1, 500);
  startAngle = (Number(startAngle) || 0) * Math.PI / 180;
  endAngle = (Number(endAngle) || 180) * Math.PI / 180;
  const span = Math.abs(endAngle - startAngle);
  const steps = clamp(Math.round(radius * span * 0.3), 12, 200);
  const pts = [];
  for (let i = 0; i <= steps; i++) {
    const a = lerp(startAngle, endAngle, i / steps);
    pts.push({ x: cx + Math.cos(a) * radius, y: cy + Math.sin(a) * radius });
  }
  return splitIntoStrokes(pts, color, brushSize, opacity, pressureStyle);
}

export function rectangle(cx, cy, width, height, rotation, color, brushSize, opacity, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 2, 1000);
  height = clamp(Number(height) || 200, 2, 1000);
  rotation = (Number(rotation) || 0) * Math.PI / 180;
  const hw = width / 2, hh = height / 2;
  const corners = [[-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh], [-hw, -hh]];
  const pts = corners.map(([lx, ly]) => ({
    x: cx + lx * Math.cos(rotation) - ly * Math.sin(rotation),
    y: cy + lx * Math.sin(rotation) + ly * Math.cos(rotation),
  }));
  return [makeStroke(pts, color, brushSize, opacity, pressureStyle)];
}

export function polygon(cx, cy, radius, sides, rotation, color, brushSize, opacity, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 150, 1, 500);
  sides = clamp(Math.round(Number(sides) || 6), 3, 24);
  rotation = (Number(rotation) || 0) * Math.PI / 180;
  const pts = [];
  for (let i = 0; i <= sides; i++) {
    const a = rotation + (i / sides) * Math.PI * 2;
    pts.push({ x: cx + Math.cos(a) * radius, y: cy + Math.sin(a) * radius });
  }
  return [makeStroke(pts, color, brushSize, opacity, pressureStyle)];
}

export function star(cx, cy, outerR, innerR, points, rotation, color, brushSize, opacity, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  outerR = clamp(Number(outerR) || 150, 5, 500);
  innerR = clamp(Number(innerR) || 65, 2, outerR - 1);
  points = clamp(Math.round(Number(points) || 5), 3, 20);
  rotation = (Number(rotation) || -90) * Math.PI / 180;
  const pts = [];
  const totalVerts = points * 2;
  for (let i = 0; i <= totalVerts; i++) {
    const a = rotation + (i / totalVerts) * Math.PI * 2;
    const r = i % 2 === 0 ? outerR : innerR;
    pts.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
  }
  return [makeStroke(pts, color, brushSize, opacity, pressureStyle)];
}
