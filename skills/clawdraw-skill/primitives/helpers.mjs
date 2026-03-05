/**
 * Shared helper utilities for ClawDraw stroke generation.
 *
 * Stroke format:
 *   { id, points: [{x, y, pressure, timestamp}], brush: {size, color, opacity}, createdAt }
 */

// ---------------------------------------------------------------------------
// Core math helpers
// ---------------------------------------------------------------------------

export function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

export function lerp(a, b, t) { return a + (b - a) * t; }

// ---------------------------------------------------------------------------
// Color helpers
// ---------------------------------------------------------------------------

export function hexToRgb(hex) {
  const m = /^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(hex);
  if (!m) return { r: 255, g: 255, b: 255 };
  return { r: parseInt(m[1], 16), g: parseInt(m[2], 16), b: parseInt(m[3], 16) };
}

export function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map(v => clamp(Math.round(v), 0, 255).toString(16).padStart(2, '0')).join('');
}

export function lerpColor(hex1, hex2, t) {
  const a = hexToRgb(hex1), b = hexToRgb(hex2);
  return rgbToHex(lerp(a.r, b.r, t), lerp(a.g, b.g, t), lerp(a.b, b.b, t));
}

/**
 * Convert HSL values to a hex color string.
 * @param {number} h - Hue (0-360)
 * @param {number} s - Saturation (0-100)
 * @param {number} l - Lightness (0-100)
 * @returns {string} Hex color string (e.g. '#ff6600')
 */
export function hslToHex(h, s, l) {
  s /= 100;
  l /= 100;
  const k = (n) => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n) => l - a * Math.max(-1, Math.min(k(n) - 3, 9 - k(n), 1));
  return rgbToHex(Math.round(f(0) * 255), Math.round(f(8) * 255), Math.round(f(4) * 255));
}

// ---------------------------------------------------------------------------
// Color Palettes
// ---------------------------------------------------------------------------

import { createRequire } from 'node:module';
const _require = createRequire(import.meta.url);
const _communityPalettes = _require('./community-palettes.json');

/**
 * Scientific visualization gradients (8 stops each, smooth continuous gradients).
 * These are the primary palettes — high quality, perceptually uniform.
 */
export const PALETTES = {
  magma:   ['#000004', '#180f3d', '#440f76', '#721f81', '#b5367a', '#e55c30', '#fba40a', '#fcffa4'],
  plasma:  ['#0d0887', '#4b03a1', '#7d03a8', '#a82296', '#cb4679', '#e86825', '#f89540', '#f0f921'],
  viridis: ['#440154', '#443a83', '#31688e', '#21908c', '#35b779', '#6ece58', '#b5de2b', '#fde725'],
  turbo:   ['#30123b', '#4662d7', '#36aaf9', '#1ae4b6', '#72fe5e', '#c8ef34', '#faba39', '#e6550d'],
  inferno: ['#000004', '#1b0c41', '#4a0c6b', '#781c6d', '#a52c60', '#cf4446', '#ed6925', '#fcffa4'],
};

/** All scientific palette names. */
export const PALETTE_NAMES = Object.keys(PALETTES);

/** Community palettes — 992 curated 5-color schemes from ColourLovers. */
export const COMMUNITY_PALETTES = _communityPalettes;

/**
 * Sample any color-stop array as a gradient at parameter t in [0,1].
 * Works with any palette — 5 stops, 8 stops, any length.
 * Returns an interpolated hex color.
 */
export function samplePalette(paletteOrName, t) {
  const stops = typeof paletteOrName === 'string'
    ? (PALETTES[paletteOrName] || PALETTES.viridis)
    : paletteOrName;
  t = clamp(t, 0, 1);
  const pos = t * (stops.length - 1);
  const lo = Math.floor(pos);
  const hi = Math.min(lo + 1, stops.length - 1);
  const frac = pos - lo;
  return lerpColor(stops[lo], stops[hi], frac);
}

/**
 * Pick a random palette. Weighted 30% toward scientific palettes (magma, plasma,
 * viridis, turbo, inferno) and 70% toward the 992 community palettes.
 * Returns an array of hex color strings.
 */
export function randomPalette() {
  if (Math.random() < 0.3) {
    const names = PALETTE_NAMES;
    return PALETTES[names[Math.floor(Math.random() * names.length)]];
  }
  return _communityPalettes[Math.floor(Math.random() * _communityPalettes.length)];
}

/**
 * Pick a random color from a random palette.
 * Shorthand for choosing a palette and grabbing one discrete color.
 */
export function randomColor() {
  const pal = randomPalette();
  return pal[Math.floor(Math.random() * pal.length)];
}

// ---------------------------------------------------------------------------
// Pressure simulation
// ---------------------------------------------------------------------------

/**
 * Simulate natural pen pressure along a stroke.
 * Ramps up at start, sustains with organic variation, tapers at end.
 */
export function simulatePressure(index, total) {
  if (total <= 1) return 0.7;
  const t = index / (total - 1);

  const attackEnd = 0.15;
  const releaseStart = 0.85;
  let envelope;
  if (t < attackEnd) {
    envelope = 0.3 + 0.7 * (t / attackEnd);
  } else if (t > releaseStart) {
    const rt = (t - releaseStart) / (1 - releaseStart);
    envelope = 1.0 - rt * 0.6;
  } else {
    envelope = 1.0;
  }

  const noise = (Math.random() - 0.5) * 0.16;
  return clamp(envelope * 0.75 + noise, 0.15, 1.0);
}

/**
 * Return pressure value for a given style at position index/total.
 * Styles: default, flat, taper, taperBoth, pulse, heavy, flick.
 */
export function getPressureForStyle(index, total, style) {
  if (total <= 1) return 0.7;
  const t = index / (total - 1);

  switch (style) {
    case 'flat':
      return 0.8 + (Math.random() - 0.5) * 0.06;

    case 'taper':
      return clamp(1.0 - t * 0.85 + (Math.random() - 0.5) * 0.08, 0.1, 1.0);

    case 'taperBoth': {
      const env = Math.sin(t * Math.PI);
      return clamp(env * 0.85 + 0.1 + (Math.random() - 0.5) * 0.08, 0.1, 1.0);
    }

    case 'pulse': {
      const wave = 0.5 + 0.4 * Math.sin(t * Math.PI * 6);
      return clamp(wave + (Math.random() - 0.5) * 0.1, 0.15, 1.0);
    }

    case 'heavy':
      return clamp(0.9 + Math.random() * 0.1, 0.85, 1.0);

    case 'flick': {
      const ramp = t < 0.15 ? t / 0.15 : 1.0;
      const taper = t < 0.15 ? 1.0 : 1.0 - ((t - 0.15) / 0.85) * 0.9;
      return clamp(ramp * taper + (Math.random() - 0.5) * 0.06, 0.05, 1.0);
    }

    default:
      return simulatePressure(index, total);
  }
}

// ---------------------------------------------------------------------------
// Stroke creation
// ---------------------------------------------------------------------------

let _strokeSeq = 0;

/**
 * Create a stroke object from an array of {x, y} points.
 * Automatically adds pressure simulation and timestamps.
 */
export function makeStroke(points, color = '#ffffff', brushSize = 5, opacity = 0.9, pressureStyle = 'default') {
  const id = `tool-${Date.now().toString(36)}-${(++_strokeSeq).toString(36)}`;
  const now = Date.now();
  const n = points.length;
  return {
    id,
    points: points.map((p, i) => ({
      x: p.x,
      y: p.y,
      pressure: p.pressure ?? getPressureForStyle(i, n, pressureStyle),
      timestamp: now + i * 5,
    })),
    brush: {
      size: clamp(brushSize, 3, 100),
      color: color || '#ffffff',
      opacity: clamp(opacity, 0.01, 1),
    },
    createdAt: now,
  };
}

/**
 * Split a long point array into multiple strokes at 4990 points with 10-point overlap.
 */
export function splitIntoStrokes(points, color, brushSize, opacity, pressureStyle) {
  const MAX = 4990;
  const OVERLAP = 10;
  if (points.length <= MAX) return [makeStroke(points, color, brushSize, opacity, pressureStyle)];
  const strokes = [];
  let start = 0;
  while (start < points.length) {
    const end = Math.min(start + MAX, points.length);
    strokes.push(makeStroke(points.slice(start, end), color, brushSize, opacity, pressureStyle));
    start = end - OVERLAP;
    if (end === points.length) break;
  }
  return strokes;
}

// ---------------------------------------------------------------------------
// 2D Perlin Noise (inline, zero dependencies)
// ---------------------------------------------------------------------------

const _perm = new Uint8Array(512);
const _grad = [[1,1],[-1,1],[1,-1],[-1,-1],[1,0],[-1,0],[0,1],[0,-1]];

(function initNoise() {
  const p = new Uint8Array(256);
  for (let i = 0; i < 256; i++) p[i] = i;
  for (let i = 255; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [p[i], p[j]] = [p[j], p[i]];
  }
  for (let i = 0; i < 512; i++) _perm[i] = p[i & 255];
})();

function fade(t) { return t * t * t * (t * (t * 6 - 15) + 10); }

export function noise2d(x, y) {
  const X = Math.floor(x) & 255, Y = Math.floor(y) & 255;
  const xf = x - Math.floor(x), yf = y - Math.floor(y);
  const u = fade(xf), v = fade(yf);
  const aa = _perm[_perm[X] + Y], ab = _perm[_perm[X] + Y + 1];
  const ba = _perm[_perm[X + 1] + Y], bb = _perm[_perm[X + 1] + Y + 1];
  const dot = (g, dx, dy) => _grad[g & 7][0] * dx + _grad[g & 7][1] * dy;
  return lerp(
    lerp(dot(aa, xf, yf), dot(ba, xf - 1, yf), u),
    lerp(dot(ab, xf, yf - 1), dot(bb, xf - 1, yf - 1), u),
    v
  );
}

// ---------------------------------------------------------------------------
// Geometry helpers
// ---------------------------------------------------------------------------

/**
 * Clip a line segment to a rectangle using parametric clipping.
 * Returns array of 2 points or null if fully outside.
 */
export function clipLineToRect(p0, p1, minX, minY, maxX, maxY) {
  const dx = p1.x - p0.x, dy = p1.y - p0.y;
  let tMin = 0, tMax = 1;
  const edges = [
    [-dx, p0.x - minX], [dx, maxX - p0.x],
    [-dy, p0.y - minY], [dy, maxY - p0.y],
  ];
  for (const [p, q] of edges) {
    if (Math.abs(p) < 1e-10) { if (q < 0) return null; continue; }
    const t = q / p;
    if (p < 0) tMin = Math.max(tMin, t);
    else tMax = Math.min(tMax, t);
  }
  if (tMin > tMax) return null;
  return [
    { x: p0.x + dx * tMin, y: p0.y + dy * tMin },
    { x: p0.x + dx * tMax, y: p0.y + dy * tMax },
  ];
}
