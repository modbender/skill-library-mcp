/**
 * Fill/texture primitives: hatchFill, crossHatch, stipple, gradientFill, colorWash, solidFill.
 */

import { clamp, lerp, lerpColor, makeStroke, clipLineToRect } from './helpers.mjs';

// ---------------------------------------------------------------------------
// Metadata
// ---------------------------------------------------------------------------

export const METADATA = [
  {
    name: 'hatchFill', description: 'Parallel line shading (hatching)', category: 'fills',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      width: { type: 'number', min: 10, max: 600, default: 300, description: 'Area width' },
      height: { type: 'number', min: 10, max: 600, default: 300, description: 'Area height' },
      angle: { type: 'number', description: 'Line angle in degrees' },
      spacing: { type: 'number', min: 2, max: 50, default: 8, description: 'Line spacing' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1, default: 0.5 },
      colorEnd: { type: 'string', description: 'End color for gradient' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'crossHatch', description: 'Two-angle crosshatch shading', category: 'fills',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      width: { type: 'number', min: 10, max: 600, description: 'Area width' },
      height: { type: 'number', min: 10, max: 600, description: 'Area height' },
      spacing: { type: 'number', min: 2, max: 50, description: 'Line spacing' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      opacity: { type: 'number', min: 0.01, max: 1 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'stipple', description: 'Random dot pattern fill', category: 'fills',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      width: { type: 'number', min: 10, max: 600, default: 300, description: 'Area width' },
      height: { type: 'number', min: 10, max: 600, default: 300, description: 'Area height' },
      density: { type: 'number', min: 0.1, max: 1, default: 0.5, description: 'Dot density' },
      color: { type: 'string' }, brushSize: { type: 'number', min: 3, max: 100 },
      dotCount: { type: 'number', min: 10, max: 500, description: 'Exact dot count' },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'gradientFill', description: 'Color gradient via stroke density', category: 'fills',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      width: { type: 'number', min: 10, max: 600, default: 300, description: 'Area width' },
      height: { type: 'number', min: 10, max: 600, default: 300, description: 'Area height' },
      colorStart: { type: 'string', description: 'Start color' },
      colorEnd: { type: 'string', description: 'End color' },
      angle: { type: 'number', description: 'Gradient angle in degrees' },
      density: { type: 'number', min: 0.1, max: 1, default: 0.5, description: 'Line density' },
      brushSize: { type: 'number', min: 3, max: 100 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'colorWash', description: 'Seamless color wash fill', category: 'fills',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      width: { type: 'number', min: 10, max: 800, default: 300, description: 'Area width' },
      height: { type: 'number', min: 10, max: 800, default: 300, description: 'Area height' },
      color: { type: 'string' }, opacity: { type: 'number', min: 0.01, max: 0.6, default: 0.35 },
      pressureStyle: { type: 'string' },
    },
  },
  {
    name: 'solidFill', description: 'Solid color fill (alias for colorWash)', category: 'fills',
    parameters: {
      cx: { type: 'number', required: true }, cy: { type: 'number', required: true },
      width: { type: 'number', min: 10, max: 800, description: 'Area width' },
      height: { type: 'number', min: 10, max: 800, description: 'Area height' },
      color: { type: 'string' }, opacity: { type: 'number', min: 0.01, max: 0.6 },
      direction: { type: 'string', description: 'Reserved' },
      pressureStyle: { type: 'string' },
    },
  },
];

// ---------------------------------------------------------------------------
// Primitives
// ---------------------------------------------------------------------------

export function hatchFill(cx, cy, width, height, angle, spacing, color, brushSize, opacity, colorEnd, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 10, 600);
  height = clamp(Number(height) || 300, 10, 600);
  angle = (Number(angle) || 45) * Math.PI / 180;
  spacing = clamp(Number(spacing) || 8, 2, 50);
  brushSize = clamp(Number(brushSize) || 2, 3, 100);
  opacity = clamp(Number(opacity) || 0.5, 0.01, 1);

  const result = [];
  const diag = Math.hypot(width, height) / 2;
  const dx = Math.cos(angle), dy = Math.sin(angle);
  const nx = -dy, ny = dx;

  const totalLines = Math.ceil((diag * 2) / spacing);
  let lineIdx = 0;

  for (let d = -diag; d <= diag; d += spacing) {
    const lineStart = { x: cx + nx * d - dx * diag, y: cy + ny * d - dy * diag };
    const lineEnd = { x: cx + nx * d + dx * diag, y: cy + ny * d + dy * diag };

    const t = totalLines > 1 ? lineIdx / (totalLines - 1) : 0;
    const lineColor = colorEnd ? lerpColor(color || '#ffffff', colorEnd, t) : color;
    lineIdx++;

    const pts = clipLineToRect(lineStart, lineEnd, cx - width/2, cy - height/2, cx + width/2, cy + height/2);
    if (pts) result.push(makeStroke(pts, lineColor, brushSize, opacity, pressureStyle));
    if (result.length >= 200) break;
  }

  return result;
}

export function crossHatch(cx, cy, width, height, spacing, color, brushSize, opacity, pressureStyle) {
  const s1 = hatchFill(cx, cy, width, height, 45, spacing, color, brushSize, opacity, undefined, pressureStyle);
  const s2 = hatchFill(cx, cy, width, height, -45, spacing, color, brushSize, opacity, undefined, pressureStyle);
  return [...s1, ...s2].slice(0, 200);
}

export function stipple(cx, cy, width, height, density, color, brushSize, dotCount, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 10, 600);
  height = clamp(Number(height) || 300, 10, 600);
  density = clamp(Number(density) || 0.5, 0.1, 1);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  dotCount = clamp(Math.round(Number(dotCount) || Math.round(50 * density)), 10, 500);

  const numDots = dotCount;
  const result = [];
  for (let i = 0; i < numDots && result.length < 200; i++) {
    const x = cx + (Math.random() - 0.5) * width;
    const y = cy + (Math.random() - 0.5) * height;
    result.push(makeStroke(
      [{ x, y }, { x: x + 1, y: y + 1 }, { x: x - 1, y }],
      color, brushSize, 0.8, pressureStyle,
    ));
  }
  return result;
}

export function gradientFill(cx, cy, width, height, colorStart, colorEnd, angle, density, brushSize, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 10, 600);
  height = clamp(Number(height) || 300, 10, 600);
  angle = (Number(angle) || 0) * Math.PI / 180;
  density = clamp(Number(density) || 0.5, 0.1, 1);
  brushSize = clamp(Number(brushSize) || 10, 3, 100);

  const numLines = Math.round(20 * density);
  const dx = Math.cos(angle), dy = Math.sin(angle);
  const nx = -dy, ny = dx;
  const diag = Math.max(width, height) / 2;
  const result = [];

  for (let i = 0; i < numLines && result.length < 200; i++) {
    const t = i / (numLines - 1 || 1);
    const d = lerp(-diag, diag, t);
    const c = lerpColor(colorStart || '#ffffff', colorEnd || '#000000', t);
    const p0 = { x: cx + nx * d - dx * diag, y: cy + ny * d - dy * diag };
    const p1 = { x: cx + nx * d + dx * diag, y: cy + ny * d + dy * diag };
    const pts = clipLineToRect(p0, p1, cx - width/2, cy - height/2, cx + width/2, cy + height/2);
    if (pts) result.push(makeStroke(pts, c, brushSize, 0.6, pressureStyle));
  }

  return result;
}

export function colorWash(cx, cy, width, height, color, opacity, pressureStyle) {
  cx = Number(cx) || 0; cy = Number(cy) || 0;
  width = clamp(Number(width) || 300, 10, 800);
  height = clamp(Number(height) || 300, 10, 800);
  opacity = clamp(Number(opacity) || 0.35, 0.01, 0.6);

  const result = [];

  const targetStrokes = 10;
  const shorter = Math.min(width, height);
  const brushSize = clamp(Math.round(shorter / targetStrokes), 8, 60);
  const step = Math.round(brushSize * 0.75);

  const passOpacity = opacity * 0.6;
  const startY = cy - height / 2;
  const endY = cy + height / 2;
  for (let y = startY; y <= endY && result.length < 100; y += step) {
    const jitterX = (Math.random() - 0.5) * step * 0.3;
    result.push(makeStroke([
      { x: cx - width / 2 + jitterX, y },
      { x: cx + width / 2 + jitterX, y },
    ], color, brushSize, passOpacity, pressureStyle));
  }

  const startX = cx - width / 2;
  const endX = cx + width / 2;
  for (let x = startX; x <= endX && result.length < 200; x += step) {
    const jitterY = (Math.random() - 0.5) * step * 0.3;
    result.push(makeStroke([
      { x, y: cy - height / 2 + jitterY },
      { x, y: cy + height / 2 + jitterY },
    ], color, brushSize, passOpacity, pressureStyle));
  }

  return result;
}

export function solidFill(cx, cy, width, height, color, opacity, direction, pressureStyle) {
  return colorWash(cx, cy, width, height, color, opacity, pressureStyle);
}
