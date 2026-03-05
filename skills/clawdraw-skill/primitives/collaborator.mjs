/**
 * Collaborator behaviors — 19 transform primitives that operate on existing strokes.
 *
 * These behaviors look up source stroke(s) from a nearby cache (set by the CLI
 * before calling), apply geometric transforms, and return stroke arrays.
 */

import { makeStroke, splitIntoStrokes, lerpColor, hexToRgb, rgbToHex, noise2d, clipLineToRect, getPressureForStyle, samplePalette, clamp, lerp, hslToHex } from './helpers.mjs';
import { classifyEndpoints, buildDensityMap, detectEnclosedRegions, buildAttractors, detectClosedShapes, pointInPolygon, clipLineToPolygon, buildSDF, shoelaceArea, extractPlanarFaces } from './spatial.mjs';

// ---------------------------------------------------------------------------
// Nearby cache — populated by CLI before calling behaviors
// ---------------------------------------------------------------------------

let _nearbyCache = null;

/** Set the nearby cache data (called by CLI before executing a behavior). */
export function setNearbyCache(data) { _nearbyCache = data; }

/** Get the current nearby cache data. */
export function getNearbyCache() { return _nearbyCache; }

// ---------------------------------------------------------------------------
// Internal geometry helpers (inline since .mjs can't import from @clawdraw/shared)
// ---------------------------------------------------------------------------

/** Find a stroke by id from the nearby cache. */
function findStrokeById(id, nearCache) {
  if (!nearCache || !nearCache.strokes) return null;
  for (const s of nearCache.strokes) {
    if (s.id === id) return s;
  }
  return null;
}

/** Find the stroke nearest to a point from the nearby cache. */
function findNearestStroke(x, y, nearCache) {
  if (!nearCache || !nearCache.strokes || nearCache.strokes.length === 0) return null;
  let best = null;
  let bestDist = Infinity;
  for (const s of nearCache.strokes) {
    const pts = s.path || s.points || [];
    for (const p of pts) {
      const dx = p.x - x;
      const dy = p.y - y;
      const d = dx * dx + dy * dy;
      if (d < bestDist) {
        bestDist = d;
        best = s;
      }
    }
  }
  return best;
}

/** Find a stroke by id or nearest to a given point. */
function findStroke(idOrPoint, nearCache) {
  if (!nearCache) nearCache = _nearbyCache;
  if (!nearCache) return null;
  if (typeof idOrPoint === 'string') {
    return findStrokeById(idOrPoint, nearCache);
  }
  if (idOrPoint && typeof idOrPoint.x === 'number') {
    return findNearestStroke(idOrPoint.x, idOrPoint.y, nearCache);
  }
  return null;
}

/** Resample a path to exactly n evenly-spaced points. */
function resamplePath(points, n) {
  if (!points || points.length === 0) return [];
  if (points.length === 1 || n <= 1) return [{ ...points[0] }];

  const totalLen = pathLength(points);
  if (totalLen < 1e-6) return points.slice(0, 1).map(p => ({ ...p }));

  const step = totalLen / (n - 1);
  const result = [{ ...points[0] }];
  let dist = 0;
  let segIdx = 0;
  let segDist = 0;

  for (let i = 1; i < n; i++) {
    const target = step * i;
    while (segIdx < points.length - 1) {
      const dx = points[segIdx + 1].x - points[segIdx].x;
      const dy = points[segIdx + 1].y - points[segIdx].y;
      const segLen = Math.sqrt(dx * dx + dy * dy);
      if (dist + segLen - segDist >= target) {
        const remain = target - dist + segDist;
        const t = segLen > 1e-8 ? remain / segLen : 0;
        result.push({
          x: points[segIdx].x + dx * t,
          y: points[segIdx].y + dy * t,
        });
        segDist = remain;
        dist = target;
        break;
      }
      dist += segLen - segDist;
      segDist = 0;
      segIdx++;
    }
    if (result.length <= i) {
      result.push({ ...points[points.length - 1] });
    }
  }
  return result;
}

/** Compute tangent vector at index i in a point array. */
function tangentAt(points, i) {
  const n = points.length;
  if (n < 2) return { x: 1, y: 0 };
  let dx, dy;
  if (i <= 0) {
    dx = points[1].x - points[0].x;
    dy = points[1].y - points[0].y;
  } else if (i >= n - 1) {
    dx = points[n - 1].x - points[n - 2].x;
    dy = points[n - 1].y - points[n - 2].y;
  } else {
    dx = points[i + 1].x - points[i - 1].x;
    dy = points[i + 1].y - points[i - 1].y;
  }
  const len = Math.sqrt(dx * dx + dy * dy);
  if (len < 1e-8) return { x: 1, y: 0 };
  return { x: dx / len, y: dy / len };
}

/** Compute normal vector (perpendicular to tangent) at index i. */
function normalAt(points, i) {
  const t = tangentAt(points, i);
  return { x: -t.y, y: t.x };
}

/** Offset all points by dx, dy. */
function offsetPath(points, dx, dy) {
  return points.map(p => ({ x: p.x + dx, y: p.y + dy }));
}

/** Rotate all points by angle (radians) around an origin. */
function rotatePath(points, angle, origin) {
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  const ox = origin.x || 0;
  const oy = origin.y || 0;
  return points.map(p => {
    const dx = p.x - ox;
    const dy = p.y - oy;
    return { x: ox + dx * cos - dy * sin, y: oy + dx * sin + dy * cos };
  });
}

/** Scale all points by factor around an origin. */
function scalePath(points, factor, origin) {
  const ox = origin.x || 0;
  const oy = origin.y || 0;
  return points.map(p => ({
    x: ox + (p.x - ox) * factor,
    y: oy + (p.y - oy) * factor,
  }));
}

/** Mirror a path across an axis at a given position. */
function mirrorPath(points, axis, position) {
  return points.map(p => {
    if (axis === 'vertical') {
      return { x: 2 * position - p.x, y: p.y };
    }
    return { x: p.x, y: 2 * position - p.y };
  });
}

/** Compute total path length. */
function pathLength(points) {
  let len = 0;
  for (let i = 1; i < points.length; i++) {
    const dx = points[i].x - points[i - 1].x;
    const dy = points[i].y - points[i - 1].y;
    len += Math.sqrt(dx * dx + dy * dy);
  }
  return len;
}

/** Compute centroid of a point array. */
function centroid(points) {
  if (!points || points.length === 0) return { x: 0, y: 0 };
  let sx = 0, sy = 0;
  for (const p of points) { sx += p.x; sy += p.y; }
  return { x: sx / points.length, y: sy / points.length };
}

/** Simple easing functions. */
function applyEasing(t, easing) {
  switch (easing) {
    case 'ease-in': return t * t;
    case 'ease-out': return t * (2 - t);
    case 'ease-in-out': return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    default: return t; // linear
  }
}

/** Extract points from a nearby-cache stroke object. */
function getStrokePoints(s) {
  if (!s) return [];
  // nearby API returns geometry in `path`, raw strokes use `points`
  return (s.path || s.points || []).map(p => ({ x: p.x, y: p.y }));
}

/** Get stroke color from nearby-cache stroke. */
function getStrokeColor(s) {
  if (!s) return '#ffffff';
  return s.brush?.color || s.color || '#ffffff';
}

/** Get stroke brush size from nearby-cache stroke. */
function getStrokeBrushSize(s) {
  if (!s) return 5;
  return s.brush?.size || s.brushSize || 5;
}

/** Get stroke opacity. */
function getStrokeOpacity(s) {
  if (!s) return 0.9;
  return s.brush?.opacity || s.opacity || 0.9;
}

/** Darken a hex color by a factor (0-1). */
function darkenColor(hex, amount) {
  const c = hexToRgb(hex);
  return rgbToHex(
    Math.round(c.r * (1 - amount)),
    Math.round(c.g * (1 - amount)),
    Math.round(c.b * (1 - amount)),
  );
}

/** Compute the convex hull of a set of 2D points (Andrew's monotone chain). */
function convexHull(points) {
  if (points.length <= 1) return points.slice();
  const sorted = points.slice().sort((a, b) => a.x - b.x || a.y - b.y);
  const cross = (o, a, b) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
  const lower = [];
  for (const p of sorted) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) lower.pop();
    lower.push(p);
  }
  const upper = [];
  for (let i = sorted.length - 1; i >= 0; i--) {
    const p = sorted[i];
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) upper.pop();
    upper.push(p);
  }
  lower.pop();
  upper.pop();
  return lower.concat(upper);
}

// ---------------------------------------------------------------------------
// Metadata for registry auto-discovery
// ---------------------------------------------------------------------------

export const METADATA = [
  // STRUCTURAL
  {
    name: 'extend', description: 'Continue from an endpoint in its direction', category: 'collaborator',
    parameters: {
      from: { type: 'string', required: true, description: 'Source stroke ID' },
      endpoint: { type: 'string', default: 'end', options: ['start', 'end'], description: 'Which endpoint' },
      length: { type: 'number', default: 200, min: 10, max: 2000, description: 'Extension length' },
      curve: { type: 'number', default: 0, min: 0, max: 1, description: 'Curve amount toward target' },
      curveTowardX: { type: 'number', description: 'Curve target X' },
      curveTowardY: { type: 'number', description: 'Curve target Y' },
    },
  },
  {
    name: 'branch', description: 'Fork from an endpoint at an angle', category: 'collaborator',
    parameters: {
      from: { type: 'string', required: true, description: 'Source stroke ID' },
      endpoint: { type: 'string', default: 'end', options: ['start', 'end'], description: 'Which endpoint' },
      angle: { type: 'number', default: 45, description: 'Branch angle in degrees' },
      length: { type: 'number', default: 150, min: 10, max: 1000, description: 'Branch length' },
      taper: { type: 'boolean', default: true, description: 'Taper the branch' },
      count: { type: 'number', default: 3, min: 1, max: 10, description: 'Number of branches' },
    },
  },
  {
    name: 'connect', description: 'Bridge two nearest unconnected endpoints', category: 'collaborator',
    parameters: {
      nearX: { type: 'number', default: 0, description: 'Center X' },
      nearY: { type: 'number', default: 0, description: 'Center Y' },
      radius: { type: 'number', default: 500, description: 'Search radius' },
      style: { type: 'string', default: 'blend', options: ['blend', 'match-a', 'match-b'], description: 'Color style' },
      curve: { type: 'number', default: 0.3, min: 0, max: 1, description: 'Curve amount' },
    },
  },
  {
    name: 'coil', description: 'Spiral around a stroke path', category: 'collaborator',
    parameters: {
      source: { type: 'string', required: true, description: 'Source stroke ID' },
      loops: { type: 'number', default: 6, min: 1, max: 30, description: 'Number of coil loops' },
      radius: { type: 'number', default: 25, min: 2, max: 100, description: 'Coil radius' },
      taper: { type: 'boolean', default: true, description: 'Taper the coil' },
      direction: { type: 'string', default: 'cw', options: ['cw', 'ccw'], description: 'Coil direction' },
    },
  },
  // FILLING
  {
    name: 'morph', description: 'Blend between two strokes (generates many intermediate strokes)', category: 'collaborator',
    parameters: {
      from: { type: 'string', required: true, description: 'Source stroke ID A' },
      to: { type: 'string', required: true, description: 'Source stroke ID B' },
      steps: { type: 'number', default: 15, min: 2, max: 50, description: 'Number of intermediate strokes' },
      easing: { type: 'string', default: 'linear', options: ['linear', 'ease-in', 'ease-out', 'ease-in-out'], description: 'Easing function' },
    },
  },
  {
    name: 'hatchGradient', description: 'Hatching with density gradient (fills a region with many hatch lines)', category: 'collaborator',
    parameters: {
      x: { type: 'number', required: true, description: 'Region X' },
      y: { type: 'number', required: true, description: 'Region Y' },
      w: { type: 'number', required: true, default: 300, description: 'Region width' },
      h: { type: 'number', required: true, default: 300, description: 'Region height' },
      angle: { type: 'number', default: 45, description: 'Hatch angle in degrees' },
      spacingFrom: { type: 'number', default: 5, min: 3, max: 50, description: 'Min spacing (dense)' },
      spacingTo: { type: 'number', default: 15, min: 5, max: 100, description: 'Max spacing (sparse)' },
      gradientDirection: { type: 'string', default: 'along', options: ['along', 'across'], description: 'Gradient direction' },
      color: { type: 'string', default: '#ffffff', description: 'Hatch color' },
      brushSize: { type: 'number', default: 3, description: 'Brush size' },
    },
  },
  {
    name: 'stitch', description: 'Short perpendicular marks along a path', category: 'collaborator',
    parameters: {
      source: { type: 'string', required: true, description: 'Source stroke ID' },
      spacing: { type: 'number', default: 8, min: 3, max: 100, description: 'Stitch spacing (smaller = more stitches)' },
      length: { type: 'number', default: 15, min: 3, max: 100, description: 'Stitch length' },
      alternating: { type: 'boolean', default: true, description: 'Alternate stitch direction' },
    },
  },
  {
    name: 'bloom', description: 'Radiate many strokes outward from a point', category: 'collaborator',
    parameters: {
      atX: { type: 'number', required: true, description: 'Center X' },
      atY: { type: 'number', required: true, description: 'Center Y' },
      count: { type: 'number', default: 24, min: 3, max: 120, description: 'Number of rays' },
      length: { type: 'number', default: 120, min: 10, max: 1000, description: 'Ray length' },
      spread: { type: 'number', default: 360, min: 10, max: 360, description: 'Spread angle in degrees' },
      taper: { type: 'boolean', default: true, description: 'Taper the rays' },
      noise: { type: 'number', default: 0.2, min: 0, max: 1, description: 'Direction/length noise' },
      color: { type: 'string', default: '#ffffff', description: 'Ray color' },
      brushSize: { type: 'number', default: 4, description: 'Brush size' },
    },
  },
  // COPY/TRANSFORM
  {
    name: 'gradient', description: 'Progressive color/offset copies (many copies along a direction)', category: 'collaborator',
    parameters: {
      source: { type: 'string', required: true, description: 'Source stroke ID' },
      count: { type: 'number', default: 10, min: 2, max: 40, description: 'Number of copies' },
      offsetX: { type: 'number', default: 8, description: 'X offset per copy' },
      offsetY: { type: 'number', default: 0, description: 'Y offset per copy' },
      colorFrom: { type: 'string', description: 'Starting color (default: source color)' },
      colorTo: { type: 'string', description: 'Ending color' },
      sizeFrom: { type: 'number', description: 'Starting brush size' },
      sizeTo: { type: 'number', description: 'Ending brush size' },
    },
  },
  {
    name: 'parallel', description: 'Offset copies perpendicular to path', category: 'collaborator',
    parameters: {
      source: { type: 'string', required: true, description: 'Source stroke ID' },
      count: { type: 'number', default: 8, min: 1, max: 30, description: 'Number of copies' },
      spacing: { type: 'number', default: 6, min: 1, max: 100, description: 'Spacing between copies' },
      colorShift: { type: 'string', description: 'Color for copies' },
      bothSides: { type: 'boolean', default: true, description: 'Create copies on both sides' },
    },
  },
  {
    name: 'echo', description: 'Scaled + faded ripple copies', category: 'collaborator',
    parameters: {
      source: { type: 'string', required: true, description: 'Source stroke ID' },
      count: { type: 'number', default: 6, min: 1, max: 15, description: 'Number of echoes' },
      scaleEach: { type: 'number', default: 1.12, min: 0.5, max: 2, description: 'Scale factor per echo' },
      opacityEach: { type: 'number', default: 0.75, min: 0.1, max: 1, description: 'Opacity multiplier per echo' },
      noise: { type: 'number', default: 0.1, min: 0, max: 1, description: 'Position noise' },
    },
  },
  {
    name: 'cascade', description: 'Shrinking rotated copies (fractal fan)', category: 'collaborator',
    parameters: {
      source: { type: 'string', required: true, description: 'Source stroke ID' },
      count: { type: 'number', default: 8, min: 2, max: 20, description: 'Number of copies' },
      scaleEach: { type: 'number', default: 0.8, min: 0.3, max: 1, description: 'Scale factor per copy' },
      rotateEach: { type: 'number', default: 20, description: 'Rotation per copy in degrees' },
      anchor: { type: 'string', default: 'end', options: ['start', 'end', 'center'], description: 'Rotation anchor' },
    },
  },
  {
    name: 'mirror', description: 'Reflect across an axis', category: 'collaborator',
    parameters: {
      source: { type: 'string', required: true, description: 'Source stroke ID' },
      axis: { type: 'string', default: 'vertical', options: ['horizontal', 'vertical'], description: 'Mirror axis' },
      offset: { type: 'number', default: 0, description: 'Axis offset from centroid' },
      opacity: { type: 'number', default: 1, min: 0.01, max: 1, description: 'Mirror opacity' },
      colorShift: { type: 'string', description: 'Override color for mirrored copy' },
    },
  },
  {
    name: 'shadow', description: 'Darker, thicker, offset copy', category: 'collaborator',
    parameters: {
      source: { type: 'string', required: true, description: 'Source stroke ID' },
      offsetX: { type: 'number', default: 5, description: 'Shadow X offset' },
      offsetY: { type: 'number', default: 5, description: 'Shadow Y offset' },
      darken: { type: 'number', default: 0.4, min: 0, max: 1, description: 'Darken amount' },
      opacity: { type: 'number', default: 0.5, min: 0.01, max: 1, description: 'Shadow opacity' },
      blur: { type: 'number', default: 0.3, min: 0, max: 1, description: 'Blur (size increase)' },
    },
  },
  // REACTIVE
  {
    name: 'counterpoint', description: 'Inverse shape (peaks become valleys)', category: 'collaborator',
    parameters: {
      source: { type: 'string', required: true, description: 'Source stroke ID' },
      offsetX: { type: 'number', default: 0, description: 'X offset' },
      offsetY: { type: 'number', default: 30, description: 'Y offset' },
      amplitude: { type: 'number', default: 1, min: 0.1, max: 5, description: 'Inversion amplitude' },
      invertX: { type: 'boolean', default: false, description: 'Also invert X deviations' },
    },
  },
  {
    name: 'harmonize', description: 'Continue detected pattern of nearby strokes', category: 'collaborator',
    parameters: {
      nearX: { type: 'number', default: 0, description: 'Center X' },
      nearY: { type: 'number', default: 0, description: 'Center Y' },
      radius: { type: 'number', default: 300, description: 'Search radius' },
      count: { type: 'number', default: 3, min: 1, max: 10, description: 'Strokes to generate' },
      directionX: { type: 'number', description: 'Force direction X (auto if omitted)' },
      directionY: { type: 'number', description: 'Force direction Y (auto if omitted)' },
    },
  },
  {
    name: 'fragment', description: 'Break stroke into scattered segments', category: 'collaborator',
    parameters: {
      source: { type: 'string', required: true, description: 'Source stroke ID' },
      pieces: { type: 'number', default: 5, min: 2, max: 20, description: 'Number of pieces' },
      scatter: { type: 'number', default: 30, min: 0, max: 200, description: 'Scatter radius' },
      opacityDecay: { type: 'number', default: 0.15, min: 0, max: 1, description: 'Opacity decay per piece' },
    },
  },
  {
    name: 'outline', description: 'Contour around stroke cluster', category: 'collaborator',
    parameters: {
      strokes: { type: 'string', required: true, description: 'Comma-separated stroke IDs' },
      padding: { type: 'number', default: 20, min: 0, max: 200, description: 'Outline padding' },
      style: { type: 'string', default: 'convex', options: ['convex', 'tight'], description: 'Hull style' },
      color: { type: 'string', description: 'Outline color' },
      brushSize: { type: 'number', default: 3, description: 'Brush size' },
    },
  },
  // SHADING
  {
    name: 'contour', description: 'Light-aware form-following hatching', category: 'collaborator',
    parameters: {
      source: { type: 'string', required: true, description: 'Source stroke ID' },
      lightAngle: { type: 'number', default: 315, description: 'Light direction in degrees (315 = upper-left)' },
      style: { type: 'string', default: 'hatch', options: ['hatch', 'crosshatch'], description: 'Hatching style' },
      layers: { type: 'number', default: 1, min: 1, max: 3, description: 'Number of hatch layers' },
      intensity: { type: 'number', default: 0.7, min: 0, max: 1, description: 'Shading intensity' },
    },
  },
  // SPATIAL
  {
    name: 'physarum', description: 'Grow tube networks connecting exterior edges (slime mold simulation)', category: 'collaborator',
    parameters: {
      nearX: { type: 'number', default: 0, description: 'Center X' },
      nearY: { type: 'number', default: 0, description: 'Center Y' },
      radius: { type: 'number', default: 300, min: 50, max: 2000, description: 'Search radius' },
      agents: { type: 'number', default: 30, min: 5, max: 100, description: 'Number of virtual agents' },
      steps: { type: 'number', default: 50, min: 10, max: 200, description: 'Simulation steps' },
      trailWidth: { type: 'number', default: 3, min: 1, max: 15, description: 'Trail stroke width' },
      color: { type: 'string', default: '#ffffff', description: 'Trail color' },
    },
  },
  {
    name: 'attractorBranch', description: 'Grow fractal branches outward from exterior edge points', category: 'collaborator',
    parameters: {
      nearX: { type: 'number', default: 0, description: 'Center X' },
      nearY: { type: 'number', default: 0, description: 'Center Y' },
      radius: { type: 'number', default: 200, min: 50, max: 1000, description: 'Search radius' },
      length: { type: 'number', default: 30, min: 5, max: 200, description: 'Branch length' },
      generations: { type: 'number', default: 3, min: 1, max: 6, description: 'Branch depth' },
      color: { type: 'string', default: '#ffffff', description: 'Branch color' },
      brushSize: { type: 'number', default: 4, min: 1, max: 15, description: 'Brush size' },
    },
  },
  {
    name: 'attractorFlow', description: 'Flow field biased toward exterior attractors, repelled by dense areas', category: 'collaborator',
    parameters: {
      nearX: { type: 'number', default: 0, description: 'Center X' },
      nearY: { type: 'number', default: 0, description: 'Center Y' },
      radius: { type: 'number', default: 300, min: 50, max: 2000, description: 'Search radius' },
      lines: { type: 'number', default: 20, min: 3, max: 80, description: 'Number of flow lines' },
      steps: { type: 'number', default: 40, min: 10, max: 150, description: 'Steps per line' },
      color: { type: 'string', default: '#ffffff', description: 'Line color' },
      brushSize: { type: 'number', default: 3, min: 1, max: 15, description: 'Brush size' },
    },
  },
  {
    name: 'interiorFill', description: 'Detect and fill enclosed regions with hatch/stipple/wash', category: 'collaborator',
    parameters: {
      nearX: { type: 'number', default: 0, description: 'Center X' },
      nearY: { type: 'number', default: 0, description: 'Center Y' },
      radius: { type: 'number', default: 300, min: 50, max: 2000, description: 'Search radius' },
      style: { type: 'string', default: 'hatch', options: ['hatch', 'stipple', 'wash'], description: 'Fill style' },
      density: { type: 'number', default: 0.5, min: 0.1, max: 1, description: 'Fill density' },
      color: { type: 'string', default: '#ffffff', description: 'Fill color' },
      brushSize: { type: 'number', default: 2, min: 1, max: 10, description: 'Brush size' },
    },
  },
  {
    name: 'vineGrowth',
    description: 'Grow organic branching vines from exterior endpoints with edge-following and color drift',
    category: 'collaborator',
    parameters: {
      nearX: { type: 'number', default: 0, description: 'Center X' },
      nearY: { type: 'number', default: 0, description: 'Center Y' },
      radius: { type: 'number', default: 300, min: 50, max: 2000, description: 'Search radius' },
      maxBranches: { type: 'number', default: 200, min: 5, max: 2000, description: 'Max vine branches' },
      stepLen: { type: 'number', default: 8, min: 3, max: 30, description: 'Growth step length' },
      branchProb: { type: 'number', default: 0.08, min: 0.01, max: 0.3, description: 'Branch probability per step' },
      mode: { type: 'string', default: 'grow', options: ['grow', 'fill'], description: 'Grow outward or fill inward' },
      driftRange: { type: 'number', default: 0.4, min: 0, max: 1, description: 'Color drift intensity (0=none, 1=full)' },
    },
  },
];

// ---------------------------------------------------------------------------
// 1. extend — Continue from an endpoint in its direction
// ---------------------------------------------------------------------------

export function extend(from, endpoint, length, curve, curveTowardX, curveTowardY) {
  const src = findStroke(from, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  endpoint = endpoint || 'end';
  length = length || 100;
  curve = curve || 0;

  const isStart = endpoint === 'start';
  const epIdx = isStart ? 0 : pts.length - 1;
  const ep = pts[epIdx];
  const tang = tangentAt(pts, epIdx);

  // If endpoint is 'start', direction is reversed
  const dir = isStart ? { x: -tang.x, y: -tang.y } : { x: tang.x, y: tang.y };

  const nPts = Math.max(20, Math.round(length / 3));
  const result = [];

  for (let i = 0; i <= nPts; i++) {
    const t = i / nPts;
    let x = ep.x + dir.x * length * t;
    let y = ep.y + dir.y * length * t;

    // Apply curve toward target point using quadratic interpolation
    if (curve > 0 && curveTowardX !== undefined && curveTowardY !== undefined) {
      const ctrlX = ep.x + dir.x * length * 0.5 + (curveTowardX - ep.x) * curve;
      const ctrlY = ep.y + dir.y * length * 0.5 + (curveTowardY - ep.y) * curve;
      const endX = ep.x + dir.x * length;
      const endY = ep.y + dir.y * length;
      // Quadratic bezier: B(t) = (1-t)^2*P0 + 2*(1-t)*t*P1 + t^2*P2
      const mt = 1 - t;
      x = mt * mt * ep.x + 2 * mt * t * ctrlX + t * t * endX;
      y = mt * mt * ep.y + 2 * mt * t * ctrlY + t * t * endY;
    }

    result.push({ x, y });
  }

  return [makeStroke(result, getStrokeColor(src), getStrokeBrushSize(src), getStrokeOpacity(src))];
}

// ---------------------------------------------------------------------------
// 2. branch — Fork from an endpoint at an angle
// ---------------------------------------------------------------------------

export function branch(from, endpoint, angle, length, taper, count) {
  const src = findStroke(from, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  endpoint = endpoint || 'end';
  angle = angle !== undefined ? angle : 45;
  length = length || 80;
  taper = taper !== undefined ? taper : true;
  count = clamp(count || 1, 1, 5);

  const isStart = endpoint === 'start';
  const epIdx = isStart ? 0 : pts.length - 1;
  const ep = pts[epIdx];
  const tang = tangentAt(pts, epIdx);
  const baseDir = isStart ? { x: -tang.x, y: -tang.y } : { x: tang.x, y: tang.y };
  const baseAngle = Math.atan2(baseDir.y, baseDir.x);

  const strokes = [];
  const angleStep = count > 1 ? (angle * 2 * Math.PI / 180) / (count - 1) : 0;
  const startAngle = count > 1 ? baseAngle + (angle * Math.PI / 180) - angleStep * (count - 1) / 2 * 0 : baseAngle + angle * Math.PI / 180;

  for (let b = 0; b < count; b++) {
    let branchAngle;
    if (count === 1) {
      branchAngle = baseAngle + angle * Math.PI / 180;
    } else {
      const spread = angle * Math.PI / 180;
      branchAngle = baseAngle - spread + (2 * spread / (count - 1)) * b;
    }

    const nPts = Math.max(15, Math.round(length / 4));
    const result = [];
    for (let i = 0; i <= nPts; i++) {
      const t = i / nPts;
      result.push({
        x: ep.x + Math.cos(branchAngle) * length * t,
        y: ep.y + Math.sin(branchAngle) * length * t,
      });
    }

    const pressureStyle = taper ? 'taper' : 'default';
    strokes.push(makeStroke(result, getStrokeColor(src), getStrokeBrushSize(src) * 0.8, getStrokeOpacity(src), pressureStyle));
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 3. connect — Bridge two nearest unconnected endpoints
// ---------------------------------------------------------------------------

export function connect(nearX, nearY, radius, style, curve) {
  nearX = nearX || 0;
  nearY = nearY || 0;
  radius = radius || 200;
  style = style || 'blend';
  curve = curve !== undefined ? curve : 0.3;

  const nc = _nearbyCache;
  if (!nc || !nc.attachPoints || nc.attachPoints.length < 2) {
    // Fallback: try to use strokes directly
    if (!nc || !nc.strokes || nc.strokes.length < 2) return [];
    // Use first points of two nearest strokes
    const sorted = nc.strokes.slice().sort((a, b) => {
      const pa = (a.path || a.points || [])[0] || { x: 0, y: 0 };
      const pb = (b.path || b.points || [])[0] || { x: 0, y: 0 };
      const da = (pa.x - nearX) ** 2 + (pa.y - nearY) ** 2;
      const db = (pb.x - nearX) ** 2 + (pb.y - nearY) ** 2;
      return da - db;
    });
    const sA = sorted[0], sB = sorted[1];
    const ptsA = getStrokePoints(sA);
    const ptsB = getStrokePoints(sB);
    if (ptsA.length === 0 || ptsB.length === 0) return [];
    const epA = ptsA[ptsA.length - 1];
    const epB = ptsB[0];
    return [_makeBridge(epA, epB, curve, sA, sB, style)];
  }

  // Use attach points from nearby data
  const aps = nc.attachPoints.slice().sort((a, b) => {
    const da = (a.x - nearX) ** 2 + (a.y - nearY) ** 2;
    const db = (b.x - nearX) ** 2 + (b.y - nearY) ** 2;
    return da - db;
  });

  // Pick two from different strokes
  let apA = aps[0];
  let apB = null;
  for (let i = 1; i < aps.length; i++) {
    if (aps[i].strokeId !== apA.strokeId) {
      apB = aps[i];
      break;
    }
  }
  if (!apB && aps.length >= 2) apB = aps[1];
  if (!apA || !apB) return [];

  const sA = findStroke(apA.strokeId, nc);
  const sB = findStroke(apB.strokeId, nc);
  return [_makeBridge(apA, apB, curve, sA, sB, style)];
}

function _makeBridge(epA, epB, curve, sA, sB, style) {
  const dx = epB.x - epA.x;
  const dy = epB.y - epA.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const nx = -dy / (dist || 1);
  const ny = dx / (dist || 1);
  const ctrlOff = dist * curve;

  const nPts = Math.max(20, Math.round(dist / 3));
  const result = [];
  for (let i = 0; i <= nPts; i++) {
    const t = i / nPts;
    // Cubic bezier with control points offset perpendicular
    const mt = 1 - t;
    const p1x = epA.x + dx * 0.33 + nx * ctrlOff;
    const p1y = epA.y + dy * 0.33 + ny * ctrlOff;
    const p2x = epA.x + dx * 0.66 - nx * ctrlOff;
    const p2y = epA.y + dy * 0.66 - ny * ctrlOff;
    const x = mt * mt * mt * epA.x + 3 * mt * mt * t * p1x + 3 * mt * t * t * p2x + t * t * t * epB.x;
    const y = mt * mt * mt * epA.y + 3 * mt * mt * t * p1y + 3 * mt * t * t * p2y + t * t * t * epB.y;
    result.push({ x, y });
  }

  let color = '#ffffff';
  let brushSize = 5;
  const colorA = getStrokeColor(sA);
  const colorB = getStrokeColor(sB);
  const sizeA = getStrokeBrushSize(sA);
  const sizeB = getStrokeBrushSize(sB);

  if (style === 'match-a') {
    color = colorA;
    brushSize = sizeA;
  } else if (style === 'match-b') {
    color = colorB;
    brushSize = sizeB;
  } else {
    color = lerpColor(colorA, colorB, 0.5);
    brushSize = (sizeA + sizeB) / 2;
  }

  return makeStroke(result, color, brushSize, Math.min(getStrokeOpacity(sA), getStrokeOpacity(sB)));
}

// ---------------------------------------------------------------------------
// 4. coil — Spiral around a stroke's path
// ---------------------------------------------------------------------------

export function coil(source, loops, radius, taper, direction) {
  const src = findStroke(source, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  loops = loops || 3;
  radius = radius || 20;
  taper = taper !== undefined ? taper : true;
  direction = direction || 'cw';
  const sign = direction === 'ccw' ? -1 : 1;

  const nSamples = Math.max(100, loops * 40);
  const resampled = resamplePath(pts, nSamples);
  const result = [];

  for (let i = 0; i < resampled.length; i++) {
    const t = i / (resampled.length - 1);
    const norm = normalAt(resampled, i);
    const phase = t * loops * 2 * Math.PI;
    const r = taper ? radius * (1 - t * 0.5) : radius;
    const offset = Math.sin(phase) * r * sign;
    result.push({
      x: resampled[i].x + norm.x * offset,
      y: resampled[i].y + norm.y * offset,
    });
  }

  return [makeStroke(result, getStrokeColor(src), getStrokeBrushSize(src) * 0.6, getStrokeOpacity(src))];
}

// ---------------------------------------------------------------------------
// 5. morph — Blend between two strokes
// ---------------------------------------------------------------------------

export function morph(from, to, steps, easing) {
  const srcA = findStroke(from, _nearbyCache);
  const srcB = findStroke(to, _nearbyCache);
  if (!srcA || !srcB) return [];

  steps = steps || 5;
  easing = easing || 'linear';

  const ptsA = getStrokePoints(srcA);
  const ptsB = getStrokePoints(srcB);
  if (ptsA.length < 2 || ptsB.length < 2) return [];

  const n = Math.max(ptsA.length, ptsB.length, 30);
  const rA = resamplePath(ptsA, n);
  const rB = resamplePath(ptsB, n);

  const colorA = getStrokeColor(srcA);
  const colorB = getStrokeColor(srcB);
  const sizeA = getStrokeBrushSize(srcA);
  const sizeB = getStrokeBrushSize(srcB);
  const opA = getStrokeOpacity(srcA);
  const opB = getStrokeOpacity(srcB);

  const strokes = [];
  for (let s = 1; s < steps + 1; s++) {
    const rawT = s / (steps + 1);
    const t = applyEasing(rawT, easing);
    const morphed = [];
    for (let i = 0; i < n; i++) {
      morphed.push({
        x: lerp(rA[i].x, rB[i].x, t),
        y: lerp(rA[i].y, rB[i].y, t),
      });
    }
    strokes.push(makeStroke(
      morphed,
      lerpColor(colorA, colorB, t),
      lerp(sizeA, sizeB, t),
      lerp(opA, opB, t),
    ));
  }
  return strokes;
}

// ---------------------------------------------------------------------------
// 6. hatchGradient — Hatching with density gradient
// ---------------------------------------------------------------------------

export function hatchGradient(x, y, w, h, angle, spacingFrom, spacingTo, gradientDirection, color, brushSize) {
  x = x || 0;
  y = y || 0;
  w = w || 200;
  h = h || 200;
  angle = angle !== undefined ? angle : 45;
  spacingFrom = spacingFrom || 10;
  spacingTo = spacingTo || 30;
  gradientDirection = gradientDirection || 'along';
  color = color || '#ffffff';
  brushSize = brushSize || 3;

  const rad = angle * Math.PI / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);

  const diagonal = Math.sqrt(w * w + h * h);
  const minX = x, maxX = x + w, minY = y, maxY = y + h;

  // Build stroke boundary segments from nearby cache for clipping
  const strokeSegs = [];
  const nc = _nearbyCache;
  if (nc && nc.strokes) {
    const MARGIN = 6; // proximity threshold — hatch stops this close to a stroke
    for (const s of nc.strokes) {
      const pts = s.path || s.points || [];
      for (let i = 0; i < pts.length - 1; i++) {
        strokeSegs.push({ ax: pts[i].x, ay: pts[i].y, bx: pts[i + 1].x, by: pts[i + 1].y, margin: MARGIN + (s.brushSize || 3) });
      }
    }
  }

  // Test if a point is "too close" to any existing stroke segment
  function nearStroke(px, py) {
    for (const seg of strokeSegs) {
      const dx = seg.bx - seg.ax, dy = seg.by - seg.ay;
      const len2 = dx * dx + dy * dy;
      let t = len2 > 0 ? ((px - seg.ax) * dx + (py - seg.ay) * dy) / len2 : 0;
      t = Math.max(0, Math.min(1, t));
      const cx = seg.ax + t * dx, cy = seg.ay + t * dy;
      const d2 = (px - cx) * (px - cx) + (py - cy) * (py - cy);
      if (d2 < seg.margin * seg.margin) return true;
    }
    return false;
  }

  const strokes = [];
  let d = -diagonal;

  while (d < diagonal) {
    const gT = (d + diagonal) / (2 * diagonal);
    const spacing = lerp(spacingFrom, spacingTo, gradientDirection === 'along' ? gT : (1 - gT));

    const cx = x + w / 2 + (-sin) * d;
    const cy = y + h / 2 + cos * d;
    const lx0 = cx - cos * diagonal;
    const ly0 = cy - sin * diagonal;
    const lx1 = cx + cos * diagonal;
    const ly1 = cy + sin * diagonal;

    const clipped = clipLineToRect({ x: lx0, y: ly0 }, { x: lx1, y: ly1 }, minX, minY, maxX, maxY);
    if (clipped) {
      if (strokeSegs.length > 0) {
        // Walk along the hatch line and emit segments that are in negative space
        const p0 = clipped[0], p1 = clipped[1];
        const hdx = p1.x - p0.x, hdy = p1.y - p0.y;
        const hlen = Math.sqrt(hdx * hdx + hdy * hdy);
        if (hlen < 2) { d += spacing; continue; }
        const steps = Math.max(10, Math.ceil(hlen / 4));
        let segStart = null;
        for (let i = 0; i <= steps; i++) {
          const t = i / steps;
          const px = p0.x + hdx * t, py = p0.y + hdy * t;
          const blocked = nearStroke(px, py);
          if (!blocked) {
            if (!segStart) segStart = { x: px, y: py };
          } else {
            if (segStart) {
              const segEnd = { x: p0.x + hdx * ((i - 1) / steps), y: p0.y + hdy * ((i - 1) / steps) };
              const segLen = Math.sqrt((segEnd.x - segStart.x) ** 2 + (segEnd.y - segStart.y) ** 2);
              if (segLen > 5) {
                strokes.push(makeStroke([segStart, segEnd], color, brushSize, 0.8, 'flat'));
              }
              segStart = null;
            }
          }
        }
        // Emit trailing segment
        if (segStart) {
          const segEnd = p1;
          const segLen = Math.sqrt((segEnd.x - segStart.x) ** 2 + (segEnd.y - segStart.y) ** 2);
          if (segLen > 5) {
            strokes.push(makeStroke([segStart, segEnd], color, brushSize, 0.8, 'flat'));
          }
        }
      } else {
        // No nearby data — fall back to simple rectangle clipping
        strokes.push(makeStroke([clipped[0], clipped[1]], color, brushSize, 0.8, 'flat'));
      }
    }

    d += spacing;
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 7. stitch — Short perpendicular marks along a path
// ---------------------------------------------------------------------------

export function stitch(source, spacing, length, alternating) {
  const src = findStroke(source, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  spacing = spacing || 15;
  length = length || 10;
  alternating = alternating !== undefined ? alternating : true;

  const totalLen = pathLength(pts);
  const nStitches = Math.max(1, Math.floor(totalLen / spacing));
  const resampled = resamplePath(pts, nStitches + 1);

  const strokes = [];
  const color = getStrokeColor(src);
  const size = getStrokeBrushSize(src) * 0.6;

  for (let i = 0; i < resampled.length; i++) {
    const norm = normalAt(resampled, i);
    const sign = (alternating && i % 2 === 1) ? -1 : 1;
    const halfLen = length / 2;

    strokes.push(makeStroke([
      { x: resampled[i].x - norm.x * halfLen * sign, y: resampled[i].y - norm.y * halfLen * sign },
      { x: resampled[i].x + norm.x * halfLen * sign, y: resampled[i].y + norm.y * halfLen * sign },
    ], color, size, getStrokeOpacity(src) * 0.8, 'flat'));
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 8. bloom — Radiate strokes outward from a point
// ---------------------------------------------------------------------------

export function bloom(atX, atY, count, length, spread, taper, noise, color, brushSize) {
  atX = atX || 0;
  atY = atY || 0;
  count = count || 12;
  length = length || 80;
  spread = spread !== undefined ? spread : 360;
  taper = taper !== undefined ? taper : true;
  noise = noise !== undefined ? noise : 0.2;
  color = color || '#ffffff';
  brushSize = brushSize || 4;

  const spreadRad = spread * Math.PI / 180;
  const startAngle = spread < 360 ? -spreadRad / 2 : 0;
  const step = spreadRad / count;

  const strokes = [];
  for (let i = 0; i < count; i++) {
    const baseAngle = startAngle + step * i + step * 0.5;
    const angleNoise = (noise2d(i * 0.7, 0) * 2 - 1) * noise * 0.5;
    const lenNoise = 1 + (noise2d(0, i * 0.7) * 2 - 1) * noise * 0.3;
    const a = baseAngle + angleNoise;
    const l = length * lenNoise;

    const nPts = Math.max(10, Math.round(l / 5));
    const result = [];
    for (let j = 0; j <= nPts; j++) {
      const t = j / nPts;
      result.push({
        x: atX + Math.cos(a) * l * t,
        y: atY + Math.sin(a) * l * t,
      });
    }

    strokes.push(makeStroke(result, color, brushSize, 0.85, taper ? 'taper' : 'default'));
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 9. gradient — Progressive color/offset copies
// ---------------------------------------------------------------------------

export function gradient(source, count, offsetX, offsetY, colorFrom, colorTo, sizeFrom, sizeTo) {
  const src = findStroke(source, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  count = count || 5;
  offsetX = offsetX !== undefined ? offsetX : 10;
  offsetY = offsetY !== undefined ? offsetY : 0;
  const srcColor = getStrokeColor(src);
  const srcSize = getStrokeBrushSize(src);
  colorFrom = colorFrom || srcColor;
  colorTo = colorTo || srcColor;
  sizeFrom = sizeFrom !== undefined ? sizeFrom : srcSize;
  sizeTo = sizeTo !== undefined ? sizeTo : srcSize;

  const strokes = [];
  for (let i = 0; i < count; i++) {
    const t = count > 1 ? i / (count - 1) : 0;
    const shifted = offsetPath(pts, offsetX * (i + 1), offsetY * (i + 1));
    strokes.push(makeStroke(
      shifted,
      lerpColor(colorFrom, colorTo, t),
      lerp(sizeFrom, sizeTo, t),
      getStrokeOpacity(src),
    ));
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 10. parallel — Offset copies perpendicular to path
// ---------------------------------------------------------------------------

export function parallel(source, count, spacing, colorShift, bothSides) {
  const src = findStroke(source, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  count = count || 3;
  spacing = spacing || 10;
  bothSides = bothSides || false;

  const color = colorShift || getStrokeColor(src);
  const size = getStrokeBrushSize(src);
  const opacity = getStrokeOpacity(src);

  const strokes = [];
  const offsets = [];
  for (let i = 1; i <= count; i++) {
    offsets.push(i);
    if (bothSides) offsets.push(-i);
  }

  for (const off of offsets) {
    const result = [];
    for (let i = 0; i < pts.length; i++) {
      const norm = normalAt(pts, i);
      result.push({
        x: pts[i].x + norm.x * spacing * off,
        y: pts[i].y + norm.y * spacing * off,
      });
    }
    strokes.push(makeStroke(result, color, size * 0.9, opacity * 0.85));
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 11. echo — Scaled + faded ripple copies
// ---------------------------------------------------------------------------

export function echo(source, count, scaleEach, opacityEach, noise) {
  const src = findStroke(source, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  count = count || 3;
  scaleEach = scaleEach !== undefined ? scaleEach : 1.15;
  opacityEach = opacityEach !== undefined ? opacityEach : 0.7;
  noise = noise !== undefined ? noise : 0.1;

  const center = centroid(pts);
  const color = getStrokeColor(src);
  const size = getStrokeBrushSize(src);
  const opacity = getStrokeOpacity(src);

  const strokes = [];
  for (let i = 1; i <= count; i++) {
    const scale = Math.pow(scaleEach, i);
    const op = opacity * Math.pow(opacityEach, i);
    const scaled = scalePath(pts, scale, center);
    const noisy = scaled.map((p, j) => ({
      x: p.x + noise2d(j * 0.3, i * 1.7) * noise * size * 5,
      y: p.y + noise2d(i * 1.7, j * 0.3) * noise * size * 5,
    }));
    strokes.push(makeStroke(noisy, color, size, clamp(op, 0.05, 1)));
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 12. cascade — Shrinking rotated copies (fractal fan)
// ---------------------------------------------------------------------------

export function cascade(source, count, scaleEach, rotateEach, anchor) {
  const src = findStroke(source, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  count = count || 5;
  scaleEach = scaleEach !== undefined ? scaleEach : 0.75;
  rotateEach = rotateEach !== undefined ? rotateEach : 30;
  anchor = anchor || 'end';

  let anchorPt;
  if (anchor === 'start') anchorPt = pts[0];
  else if (anchor === 'center') anchorPt = centroid(pts);
  else anchorPt = pts[pts.length - 1];

  const color = getStrokeColor(src);
  const size = getStrokeBrushSize(src);
  const opacity = getStrokeOpacity(src);
  const rotRad = rotateEach * Math.PI / 180;

  const strokes = [];
  let current = pts;
  for (let i = 1; i <= count; i++) {
    current = scalePath(current, scaleEach, anchorPt);
    current = rotatePath(current, rotRad, anchorPt);
    strokes.push(makeStroke(
      current.map(p => ({ ...p })),
      color,
      Math.max(3, size * Math.pow(scaleEach, i)),
      clamp(opacity * Math.pow(0.9, i), 0.1, 1),
    ));
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 13. mirror — Reflect across an axis
// ---------------------------------------------------------------------------

export function mirror(source, axis, offset, opacity, colorShift) {
  const src = findStroke(source, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  axis = axis || 'vertical';
  offset = offset || 0;
  opacity = opacity !== undefined ? opacity : 1;

  const center = centroid(pts);
  const axisPos = (axis === 'vertical' ? center.x : center.y) + offset;
  const mirrored = mirrorPath(pts, axis, axisPos);
  const color = colorShift || getStrokeColor(src);

  return [makeStroke(mirrored, color, getStrokeBrushSize(src), clamp(opacity, 0.05, 1))];
}

// ---------------------------------------------------------------------------
// 14. shadow — Darker, thicker, offset copy
// ---------------------------------------------------------------------------

export function shadow(source, offsetX, offsetY, darken, opacity, blur) {
  const src = findStroke(source, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  offsetX = offsetX !== undefined ? offsetX : 5;
  offsetY = offsetY !== undefined ? offsetY : 5;
  darken = darken !== undefined ? darken : 0.4;
  opacity = opacity !== undefined ? opacity : 0.5;
  blur = blur !== undefined ? blur : 0.3;

  const shifted = offsetPath(pts, offsetX, offsetY);
  const color = darkenColor(getStrokeColor(src), darken);
  const size = getStrokeBrushSize(src) * (1 + blur * 0.5);

  return [makeStroke(shifted, color, size, clamp(opacity, 0.05, 1))];
}

// ---------------------------------------------------------------------------
// 15. counterpoint — Inverse shape
// ---------------------------------------------------------------------------

export function counterpoint(source, offsetX, offsetY, amplitude, invertX) {
  const src = findStroke(source, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  offsetX = offsetX !== undefined ? offsetX : 0;
  offsetY = offsetY !== undefined ? offsetY : 30;
  amplitude = amplitude !== undefined ? amplitude : 1;
  invertX = invertX || false;

  // Compute chord line from first to last point
  const p0 = pts[0];
  const pN = pts[pts.length - 1];
  const chordDx = pN.x - p0.x;
  const chordDy = pN.y - p0.y;
  const chordLen = Math.sqrt(chordDx * chordDx + chordDy * chordDy);

  const result = [];
  for (let i = 0; i < pts.length; i++) {
    const t = pts.length > 1 ? i / (pts.length - 1) : 0;
    // Point on chord at parameter t
    const chordX = p0.x + chordDx * t;
    const chordY = p0.y + chordDy * t;
    // Deviation from chord
    const devX = pts[i].x - chordX;
    const devY = pts[i].y - chordY;
    // Invert deviations
    result.push({
      x: chordX + (invertX ? -devX : devX) * amplitude + offsetX,
      y: chordY + (-devY) * amplitude + offsetY,
    });
  }

  return [makeStroke(result, getStrokeColor(src), getStrokeBrushSize(src), getStrokeOpacity(src))];
}

// ---------------------------------------------------------------------------
// 16. harmonize — Continue detected pattern
// ---------------------------------------------------------------------------

export function harmonize(nearX, nearY, radius, count, directionX, directionY) {
  nearX = nearX || 0;
  nearY = nearY || 0;
  radius = radius || 300;
  count = count || 3;

  const nc = _nearbyCache;
  if (!nc || !nc.strokes || nc.strokes.length < 2) return [];

  // Filter strokes within radius
  const nearby = nc.strokes.filter(s => {
    const pts = s.path || s.points || [];
    if (pts.length === 0) return false;
    const c = centroid(pts);
    const dx = c.x - nearX;
    const dy = c.y - nearY;
    return Math.sqrt(dx * dx + dy * dy) <= radius;
  });

  if (nearby.length < 2) return [];

  // Analyze pattern: compute centroid offsets between consecutive strokes
  const centroids = nearby.map(s => centroid(getStrokePoints(s)));
  let avgDx = 0, avgDy = 0;
  for (let i = 1; i < centroids.length; i++) {
    avgDx += centroids[i].x - centroids[i - 1].x;
    avgDy += centroids[i].y - centroids[i - 1].y;
  }
  avgDx /= (centroids.length - 1);
  avgDy /= (centroids.length - 1);

  // Override with explicit direction if provided
  if (directionX !== undefined && directionX !== null) avgDx = directionX;
  if (directionY !== undefined && directionY !== null) avgDy = directionY;

  // Analyze average style from nearby strokes
  const lastStroke = nearby[nearby.length - 1];
  const lastPts = getStrokePoints(lastStroke);
  const lastCentroid = centroids[centroids.length - 1];
  const avgColor = getStrokeColor(lastStroke);
  const avgSize = getStrokeBrushSize(lastStroke);
  const avgOpacity = getStrokeOpacity(lastStroke);

  const strokes = [];
  for (let i = 1; i <= count; i++) {
    // Offset points from last stroke
    const shifted = lastPts.map(p => ({
      x: p.x + avgDx * i,
      y: p.y + avgDy * i,
    }));
    strokes.push(makeStroke(shifted, avgColor, avgSize, avgOpacity));
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 17. fragment — Break into scattered segments
// ---------------------------------------------------------------------------

export function fragment(source, pieces, scatter, opacityDecay) {
  const src = findStroke(source, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  pieces = pieces || 5;
  scatter = scatter || 30;
  opacityDecay = opacityDecay !== undefined ? opacityDecay : 0.15;

  const segSize = Math.max(2, Math.floor(pts.length / pieces));
  const color = getStrokeColor(src);
  const size = getStrokeBrushSize(src);
  const opacity = getStrokeOpacity(src);

  const strokes = [];
  for (let i = 0; i < pieces; i++) {
    const start = Math.min(i * segSize, pts.length - 1);
    const end = Math.min(start + segSize, pts.length);
    const segment = pts.slice(start, end);
    if (segment.length < 2) continue;

    const dx = (noise2d(i * 1.3, 0.5) * 2 - 1) * scatter;
    const dy = (noise2d(0.5, i * 1.3) * 2 - 1) * scatter;
    const shifted = offsetPath(segment, dx, dy);
    const op = clamp(opacity - opacityDecay * i, 0.05, 1);

    strokes.push(makeStroke(shifted, color, size, op));
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 18. outline — Contour around stroke cluster
// ---------------------------------------------------------------------------

export function outline(strokes, padding, style, color, brushSize) {
  padding = padding !== undefined ? padding : 20;
  style = style || 'convex';
  brushSize = brushSize || 3;

  // Parse stroke IDs (comma-separated string)
  const ids = typeof strokes === 'string' ? strokes.split(',').map(s => s.trim()) : (strokes || []);
  const nc = _nearbyCache;
  if (!nc) return [];

  // Collect all points from specified strokes
  const allPts = [];
  for (const id of ids) {
    const s = findStroke(id, nc);
    if (s) {
      for (const p of getStrokePoints(s)) {
        allPts.push(p);
      }
    }
  }

  if (allPts.length < 3) return [];

  // Default color from first found stroke
  if (!color) {
    const first = findStroke(ids[0], nc);
    color = first ? getStrokeColor(first) : '#ffffff';
  }

  // Compute convex hull
  const hull = convexHull(allPts);
  if (hull.length < 3) return [];

  // Expand hull outward by padding
  const center = centroid(hull);
  const expanded = hull.map(p => {
    const dx = p.x - center.x;
    const dy = p.y - center.y;
    const d = Math.sqrt(dx * dx + dy * dy);
    if (d < 1e-6) return { ...p };
    return {
      x: p.x + (dx / d) * padding,
      y: p.y + (dy / d) * padding,
    };
  });

  // Close the loop
  expanded.push({ ...expanded[0] });

  return [makeStroke(expanded, color, brushSize, 0.8)];
}

// ---------------------------------------------------------------------------
// 19. contour — Light-aware form-following hatching (THE SHOWCASE)
// ---------------------------------------------------------------------------

export function contour(source, lightAngle, style, layers, intensity) {
  const src = findStroke(source, _nearbyCache);
  if (!src) return [];
  const pts = getStrokePoints(src);
  if (pts.length < 2) return [];

  lightAngle = lightAngle !== undefined ? lightAngle : 315;
  style = style || 'hatch';
  layers = clamp(layers || 1, 1, 3);
  intensity = intensity !== undefined ? intensity : 0.7;

  const srcColor = getStrokeColor(src);
  const srcSize = getStrokeBrushSize(src);
  const darkColor = darkenColor(srcColor, 0.5);

  // Light direction vector from angle (315 = upper-left, standard math convention)
  const lightRad = lightAngle * Math.PI / 180;
  const lightDir = { x: Math.cos(lightRad), y: Math.sin(lightRad) };

  // Resample source path — ensure enough samples even for short strokes
  const totalLen = pathLength(pts);
  if (totalLen < 5) return []; // truly degenerate (< 5 canvas units)
  const sampleSpacing = Math.min(10, totalLen / 8); // adapt spacing for short strokes
  const nSamples = Math.max(10, Math.floor(totalLen / sampleSpacing));
  const resampled = resamplePath(pts, nSamples);

  const allStrokes = [];

  const layerAngles = [0, Math.PI / 2, Math.PI / 4]; // primary, perpendicular, diagonal

  for (let layer = 0; layer < layers; layer++) {
    const layerAngleOffset = layerAngles[layer] || 0;
    let accumDist = 0;
    let nextHatchDist = 0;

    for (let i = 0; i < resampled.length; i++) {
      // Accumulate distance
      if (i > 0) {
        const dx = resampled[i].x - resampled[i - 1].x;
        const dy = resampled[i].y - resampled[i - 1].y;
        accumDist += Math.sqrt(dx * dx + dy * dy);
      }

      if (accumDist < nextHatchDist) continue;

      // Compute surface normal at this sample point
      const norm = normalAt(resampled, i);

      // Illumination: dot product of normal with light direction
      // Higher = more lit, lower = more shadow
      const illumination = clamp(norm.x * lightDir.x + norm.y * lightDir.y, -1, 1);
      // Remap to 0-1 range (0 = full shadow, 1 = full light)
      const lit = (illumination + 1) / 2;

      // Spacing inversely proportional to shadow: dense in shadow, sparse in light
      const spacing = 5 + lit * intensity * 15;
      nextHatchDist = accumDist + spacing;

      // Skip only the most brightly-lit areas (always produce *some* hatching)
      if (lit > 0.92 && layer === 0) continue;
      if (lit > 0.75 && layer > 0) continue;

      // Hatch line perpendicular to source path (with layer rotation)
      const tang = tangentAt(resampled, i);
      const hatchAngle = Math.atan2(tang.y, tang.x) + Math.PI / 2 + layerAngleOffset;
      const hatchDirX = Math.cos(hatchAngle);
      const hatchDirY = Math.sin(hatchAngle);

      const hatchLen = srcSize * 2;
      const halfLen = hatchLen / 2;
      const cx = resampled[i].x;
      const cy = resampled[i].y;

      // Generate hatch stroke with pressure variation (thick in shadow, thin in light)
      const hatchPts = [];
      const hatchSegments = 6;
      for (let j = 0; j <= hatchSegments; j++) {
        const ht = j / hatchSegments;
        const pos = -halfLen + ht * hatchLen;
        hatchPts.push({
          x: cx + hatchDirX * pos,
          y: cy + hatchDirY * pos,
          // Pressure: heavier on shadow side
          pressure: clamp(0.3 + (1 - lit) * intensity * 0.6 + (Math.random() - 0.5) * 0.1, 0.1, 1),
        });
      }

      // Color: darker for shadow hatches
      const hatchColor = lerpColor(srcColor, darkColor, (1 - lit) * intensity);
      const hatchSize = Math.max(2, srcSize * 0.4 * (0.5 + (1 - lit) * 0.5));
      const hatchOpacity = clamp(0.4 + (1 - lit) * intensity * 0.5, 0.2, 0.9);

      allStrokes.push(makeStroke(hatchPts, hatchColor, hatchSize, hatchOpacity));
    }
  }

  return allStrokes;
}

// ---------------------------------------------------------------------------
// 20. physarum — Slime mold tube network connecting exterior edges
// ---------------------------------------------------------------------------

export function physarum(nearX, nearY, radius, agents, steps, trailWidth, color) {
  nearX = nearX || 0;
  nearY = nearY || 0;
  radius = radius || 300;
  agents = clamp(agents || 30, 5, 100);
  steps = clamp(steps || 50, 10, 200);
  trailWidth = trailWidth || 3;
  color = color || '#ffffff';

  const nc = _nearbyCache;
  if (!nc || !nc.strokes || nc.strokes.length === 0) return [];

  // Build attractors from exterior endpoints
  const attractors = buildAttractors(nc.strokes, Math.min(agents, 20));
  if (attractors.length === 0) return [];

  // Build density map for pheromone-like trail avoidance
  const bounds = {
    minX: nearX - radius, minY: nearY - radius,
    maxX: nearX + radius, maxY: nearY + radius,
  };
  const density = buildDensityMap(nc.strokes, bounds, 32);

  // Initialize virtual agents at center with random directions
  const agentState = [];
  for (let i = 0; i < agents; i++) {
    const angle = (i / agents) * Math.PI * 2 + (noise2d(i * 0.7, 0.3) - 0.5) * 0.5;
    agentState.push({
      x: nearX + (noise2d(i * 0.3, 1.7) - 0.5) * radius * 0.3,
      y: nearY + (noise2d(1.7, i * 0.3) - 0.5) * radius * 0.3,
      angle,
      trail: [],
    });
  }

  const SENSOR_ANGLE = 22.5 * Math.PI / 180;
  const SENSOR_DIST = radius * 0.08;
  const STEP_SIZE = radius * 0.015;

  // Simulate
  for (let step = 0; step < steps; step++) {
    for (const agent of agentState) {
      // Sense at three directions: ahead, left, right
      const senseAhead = senseAttractors(agent.x, agent.y, agent.angle, SENSOR_DIST, attractors, density);
      const senseLeft = senseAttractors(agent.x, agent.y, agent.angle - SENSOR_ANGLE, SENSOR_DIST, attractors, density);
      const senseRight = senseAttractors(agent.x, agent.y, agent.angle + SENSOR_ANGLE, SENSOR_DIST, attractors, density);

      // Turn toward strongest signal
      if (senseLeft > senseAhead && senseLeft > senseRight) {
        agent.angle -= SENSOR_ANGLE * 0.5;
      } else if (senseRight > senseAhead && senseRight > senseLeft) {
        agent.angle += SENSOR_ANGLE * 0.5;
      }
      // Add small random jitter
      agent.angle += (noise2d(step * 0.1, agent.x * 0.01) - 0.5) * 0.3;

      // Move
      agent.x += Math.cos(agent.angle) * STEP_SIZE;
      agent.y += Math.sin(agent.angle) * STEP_SIZE;

      // Clamp to radius
      const dx = agent.x - nearX;
      const dy = agent.y - nearY;
      const d = Math.sqrt(dx * dx + dy * dy);
      if (d > radius) {
        agent.x = nearX + (dx / d) * radius;
        agent.y = nearY + (dy / d) * radius;
        agent.angle += Math.PI * 0.5; // bounce
      }

      agent.trail.push({ x: agent.x, y: agent.y });
    }
  }

  // Convert trails to strokes, splitting into segments
  const strokes = [];
  for (const agent of agentState) {
    if (agent.trail.length < 3) continue;
    // Split trail into reasonable segments
    const maxSegLen = 30;
    for (let i = 0; i < agent.trail.length; i += maxSegLen) {
      const seg = agent.trail.slice(i, Math.min(i + maxSegLen + 1, agent.trail.length));
      if (seg.length >= 2) {
        const t = i / agent.trail.length;
        const opacity = clamp(0.4 + t * 0.4, 0.3, 0.85);
        strokes.push(makeStroke(seg, color, trailWidth, opacity, 'taper'));
      }
    }
  }

  return strokes;
}

function senseAttractors(x, y, angle, dist, attractors, density) {
  const sx = x + Math.cos(angle) * dist;
  const sy = y + Math.sin(angle) * dist;
  let signal = 0;

  // Attractor pull
  for (const a of attractors) {
    const dx = a.x - sx;
    const dy = a.y - sy;
    const d2 = dx * dx + dy * dy;
    if (d2 < 1) continue;
    signal += a.strength / (1 + d2 * 0.001);
  }

  // Avoid dense areas
  const d = density.get(sx, sy);
  signal -= d * 2;

  return signal;
}

// ---------------------------------------------------------------------------
// 21. attractorBranch — Grow fractal branches from exterior edge points
// ---------------------------------------------------------------------------

export function attractorBranch(nearX, nearY, radius, length, generations, color, brushSize) {
  nearX = nearX || 0;
  nearY = nearY || 0;
  radius = radius || 200;
  length = length || 30;
  generations = clamp(generations || 3, 1, 6);
  color = color || '#ffffff';
  brushSize = brushSize || 4;

  const nc = _nearbyCache;
  if (!nc || !nc.strokes || nc.strokes.length === 0) return [];

  const attractors = buildAttractors(nc.strokes, 10);
  if (attractors.length === 0) return [];

  const strokes = [];
  const branchAngle = 30 * Math.PI / 180;
  const shrink = 0.7;

  function growBranch(x, y, angle, len, gen, size) {
    if (gen <= 0 || len < 3) return;

    const nPts = Math.max(8, Math.round(len / 3));
    const pts = [];
    for (let i = 0; i <= nPts; i++) {
      const t = i / nPts;
      pts.push({
        x: x + Math.cos(angle) * len * t + (noise2d(gen * 3.7, t * 5) - 0.5) * len * 0.1,
        y: y + Math.sin(angle) * len * t + (noise2d(t * 5, gen * 3.7) - 0.5) * len * 0.1,
      });
    }

    const opacity = clamp(0.9 - (generations - gen) * 0.15, 0.3, 0.9);
    strokes.push(makeStroke(pts, color, size, opacity, 'taper'));

    const endX = x + Math.cos(angle) * len;
    const endY = y + Math.sin(angle) * len;

    // Branch left and right
    growBranch(endX, endY, angle - branchAngle, len * shrink, gen - 1, size * 0.8);
    growBranch(endX, endY, angle + branchAngle, len * shrink, gen - 1, size * 0.8);
  }

  for (const attr of attractors) {
    const dx = attr.x - nearX;
    const dy = attr.y - nearY;
    if (Math.sqrt(dx * dx + dy * dy) > radius) continue;

    const angle = Math.atan2(attr.direction.y, attr.direction.x);
    growBranch(attr.x, attr.y, angle, length, generations, brushSize);
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 22. attractorFlow — Flow field biased toward exterior attractors
// ---------------------------------------------------------------------------

export function attractorFlow(nearX, nearY, radius, lines, steps, color, brushSize) {
  nearX = nearX || 0;
  nearY = nearY || 0;
  radius = radius || 300;
  lines = clamp(lines || 20, 3, 80);
  steps = clamp(steps || 40, 10, 150);
  color = color || '#ffffff';
  brushSize = brushSize || 3;

  const nc = _nearbyCache;
  if (!nc || !nc.strokes || nc.strokes.length === 0) return [];

  const attractors = buildAttractors(nc.strokes, 15);
  if (attractors.length === 0) return [];

  const bounds = {
    minX: nearX - radius, minY: nearY - radius,
    maxX: nearX + radius, maxY: nearY + radius,
  };
  const density = buildDensityMap(nc.strokes, bounds, 32);

  const stepSize = radius * 0.02;
  const strokes = [];

  for (let i = 0; i < lines; i++) {
    // Start lines distributed in a ring around center
    const startAngle = (i / lines) * Math.PI * 2;
    const startR = radius * (0.2 + noise2d(i * 0.7, 0.5) * 0.3);
    let x = nearX + Math.cos(startAngle) * startR;
    let y = nearY + Math.sin(startAngle) * startR;

    const pts = [{ x, y }];

    for (let s = 0; s < steps; s++) {
      // Compute flow direction: sum of attractor pulls minus density repulsion
      let fx = 0, fy = 0;

      for (const a of attractors) {
        const adx = a.x - x;
        const ady = a.y - y;
        const d2 = adx * adx + ady * ady;
        if (d2 < 1) continue;
        const d = Math.sqrt(d2);
        fx += (adx / d) * a.strength / (1 + d * 0.01);
        fy += (ady / d) * a.strength / (1 + d * 0.01);
      }

      // Repel from dense areas using density gradient approximation
      const gx = density.get(x + 5, y) - density.get(x - 5, y);
      const gy = density.get(x, y + 5) - density.get(x, y - 5);
      fx -= gx * 3;
      fy -= gy * 3;

      // Add curl noise for organic feel
      const noiseAngle = noise2d(x * 0.005, y * 0.005) * Math.PI * 2;
      fx += Math.cos(noiseAngle) * 0.3;
      fy += Math.sin(noiseAngle) * 0.3;

      // Normalize and step
      const fLen = Math.sqrt(fx * fx + fy * fy);
      if (fLen < 1e-6) break;
      x += (fx / fLen) * stepSize;
      y += (fy / fLen) * stepSize;

      // Check bounds
      const dx = x - nearX;
      const dy = y - nearY;
      if (dx * dx + dy * dy > radius * radius) break;

      pts.push({ x, y });
    }

    if (pts.length >= 3) {
      const opacity = clamp(0.5 + noise2d(i * 1.3, 0.7) * 0.3, 0.3, 0.85);
      strokes.push(makeStroke(pts, color, brushSize, opacity, 'taper'));
    }
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 23. interiorFill — Fill enclosed regions with hatch/stipple/wash
// ---------------------------------------------------------------------------

export function interiorFill(nearX, nearY, radius, style, density, color, brushSize) {
  nearX = nearX || 0;
  nearY = nearY || 0;
  radius = radius || 300;
  style = style || 'hatch';
  density = density !== undefined ? clamp(density, 0.1, 1) : 0.5;
  brushSize = brushSize || 2;

  // Default color: prefer dominant palette color from nearby data, fall back to white
  if (!color || color === '#ffffff') {
    const nc0 = _nearbyCache;
    if (nc0 && nc0.summary && nc0.summary.palette && nc0.summary.palette.length > 0) {
      color = nc0.summary.palette[0];
    } else {
      color = color || '#ffffff';
    }
  }

  const nc = _nearbyCache;
  if (!nc || !nc.strokes || nc.strokes.length === 0) return [];

  const bounds = {
    minX: nearX - radius, minY: nearY - radius,
    maxX: nearX + radius, maxY: nearY + radius,
  };

  // Try topology-aware shape detection first (uses relay topology block)
  let shapes = [];
  if (nc.topology) {
    shapes = detectClosedShapes(nc);
  }

  // PSLG face extraction — finds ALL enclosed regions including self-intersections
  if (shapes.length === 0) {
    shapes = extractPlanarFaces(nc.strokes, bounds);
    // Carry stroke color through for single-stroke faces
    for (const face of shapes) {
      if (face.strokeIds.length === 1) {
        const src = nc.strokes.find(s => s.id === face.strokeIds[0]);
        if (src) face.color = src.color || (src.brush && src.brush.color);
      }
    }
  }

  if (shapes.length === 0) return [];

  const strokes = [];

  for (const shape of shapes) {
    const polygon = shape.polygon;
    if (!polygon || polygon.length < 3) continue;

    // Per-shape color: prefer shape's own color (from self-closing detection), then global color
    const shapeColor = shape.color || color;

    const cx = shape.centroid.x;
    const cy = shape.centroid.y;

    // Compute bounding box of the polygon
    let pMinX = Infinity, pMaxX = -Infinity, pMinY = Infinity, pMaxY = -Infinity;
    for (const p of polygon) {
      if (p.x < pMinX) pMinX = p.x;
      if (p.x > pMaxX) pMaxX = p.x;
      if (p.y < pMinY) pMinY = p.y;
      if (p.y > pMaxY) pMaxY = p.y;
    }
    const polyW = pMaxX - pMinX;
    const polyH = pMaxY - pMinY;
    const diagonal = Math.sqrt(polyW * polyW + polyH * polyH);

    if (style === 'hatch') {
      // Generate hatch lines with gradient: stroke color → darker shade, fading opacity
      const spacing = lerp(15, 4, density);
      const angle = 45 * Math.PI / 180;
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      const darkShade = darkenColor(shapeColor, 0.4);
      const totalSteps = Math.max(1, Math.ceil(2 * diagonal / spacing));
      let stepIndex = 0;

      for (let d = -diagonal; d < diagonal; d += spacing) {
        const t = stepIndex / totalSteps; // 0 → 1 across the shape
        const hatchColor = lerpColor(shapeColor, darkShade, t);
        const hatchOpacity = lerp(0.7, 0.4, t);

        const lx0 = cx + (-sin) * d - cos * diagonal;
        const ly0 = cy + cos * d - sin * diagonal;
        const lx1 = cx + (-sin) * d + cos * diagonal;
        const ly1 = cy + cos * d + sin * diagonal;

        // Clip hatch line to polygon boundary
        const segments = clipLineToPolygon({ x: lx0, y: ly0 }, { x: lx1, y: ly1 }, polygon);
        for (const [segStart, segEnd] of segments) {
          const segLen = Math.sqrt((segEnd.x - segStart.x) ** 2 + (segEnd.y - segStart.y) ** 2);
          if (segLen > 3) {
            strokes.push(makeStroke(
              [segStart, segEnd],
              hatchColor, brushSize, hatchOpacity, 'flat'
            ));
          }
        }
        stepIndex++;
      }
    } else if (style === 'stipple') {
      // Generate random dots — only emit if inside polygon
      const count = Math.round((shape.area || polyW * polyH) * density * 0.01);
      for (let i = 0; i < count; i++) {
        const px = pMinX + noise2d(i * 0.7, cx * 0.01) * polyW;
        const py = pMinY + noise2d(cx * 0.01, i * 0.7) * polyH;
        if (!pointInPolygon(px, py, polygon)) continue;
        strokes.push(makeStroke(
          [{ x: px, y: py }, { x: px + 1, y: py + 1 }],
          shapeColor, brushSize, clamp(0.3 + noise2d(i * 0.3, 0.5) * 0.4, 0.2, 0.7)
        ));
      }
    } else if (style === 'wash') {
      // Generate overlapping soft strokes — start points checked against polygon
      const regionRadius = Math.max(polyW, polyH) / 2;
      const count = Math.round(5 + density * 10);
      for (let i = 0; i < count; i++) {
        const angle = noise2d(i * 0.5, cy * 0.01) * Math.PI * 2;
        const len = regionRadius * (0.5 + noise2d(i * 0.3, 0.7) * 0.5);
        const startX = cx + (noise2d(i * 0.7, 1.3) - 0.5) * regionRadius * 0.5;
        const startY = cy + (noise2d(1.3, i * 0.7) - 0.5) * regionRadius * 0.5;

        // Only start inside the polygon
        if (!pointInPolygon(startX, startY, polygon)) continue;

        const pts = [];
        const nPts = 15;
        for (let j = 0; j <= nPts; j++) {
          const t = j / nPts;
          const wx = startX + Math.cos(angle) * len * t + (noise2d(j * 0.3, i * 0.7) - 0.5) * 10;
          const wy = startY + Math.sin(angle) * len * t + (noise2d(i * 0.7, j * 0.3) - 0.5) * 10;
          // Stop if waypoint exits the polygon
          if (!pointInPolygon(wx, wy, polygon)) break;
          pts.push({ x: wx, y: wy });
        }

        if (pts.length >= 2) {
          strokes.push(makeStroke(pts, shapeColor, brushSize * 3, 0.15 + density * 0.2));
        }
      }
    }
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// 24. vineGrowth — Organic branching vines from exterior endpoints
// ---------------------------------------------------------------------------

/**
 * Grow organic vine-like branches from exterior endpoints of existing strokes.
 *
 * Combines SDF edge-following, stochastic branching, HSL color drift from
 * source stroke, and self-avoidance to produce organic growth patterns.
 *
 * @param {number} nearX - Center X of search area
 * @param {number} nearY - Center Y of search area
 * @param {number} radius - Search radius
 * @param {number} maxBranches - Maximum total vine branches
 * @param {number} stepLen - Step distance per growth tick
 * @param {number} branchProb - Base branching probability per step
 * @param {string} mode - 'grow' (outward from endpoints) or 'fill' (inward from face boundaries)
 * @param {number} driftRange - Color drift intensity (0=none, 1=wild)
 * @returns {Array} Array of stroke objects
 */
export function vineGrowth(nearX, nearY, radius, maxBranches, stepLen, branchProb, mode, driftRange) {
  nearX = nearX || 0;
  nearY = nearY || 0;
  radius = radius || 300;
  maxBranches = clamp(maxBranches || 200, 5, 2000);
  stepLen = clamp(stepLen || 8, 3, 30);
  branchProb = clamp(branchProb || 0.08, 0.01, 0.3);
  mode = mode || 'grow';
  driftRange = driftRange !== undefined ? clamp(driftRange, 0, 1) : 0.4;

  const nc = _nearbyCache;
  if (!nc || !nc.strokes || nc.strokes.length === 0) return [];

  const bounds = {
    minX: nearX - radius, minY: nearY - radius,
    maxX: nearX + radius, maxY: nearY + radius,
  };

  const sdf = buildSDF(nc.strokes, bounds, 120);
  const densityMap = buildDensityMap(nc.strokes, bounds, 32);

  // Inline RGB → HSL conversion
  function _rgbToHsl(r, g, b) {
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h = 0, s = 0;
    const l = (max + min) / 2;
    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
      else if (max === g) h = ((b - r) / d + 2) / 6;
      else h = ((r - g) / d + 4) / 6;
    }
    return { h: h * 360, s: s * 100, l: l * 100 };
  }

  // --- Constants ---
  const TIP_BUDGET = 250;
  const MAX_GLOBAL_ITERATIONS = 3000;
  const EDGE_THRESHOLD = 25;
  const EDGE_FOLLOW_BLEND = 0.7;
  const AVOID_RADIUS = 18;
  const NOISE_SCALE = 0.008;
  const NOISE_STRENGTH = 0.6;
  const MAX_GENERATION = 6;
  const SIZE_SHRINK = 0.82;
  const COLLISION_DIST = stepLen * 1.5;
  const COLOR_GRACE_DIST = stepLen * 30;

  const strokes = [];
  const tips = [];
  let totalBranches = 0;

  // Spatial hash grid for cross-tip avoidance (replaces O(n²) allVinePoints array)
  const VP_CELL = AVOID_RADIUS * 2;
  const vineGrid = new Map(); // "gx,gy" → [{x, y, tipIdx}]
  let vinePointCounter = 0;

  function addVinePoint(x, y, tipIdx) {
    const key = `${Math.floor(x / VP_CELL)},${Math.floor(y / VP_CELL)}`;
    let cell = vineGrid.get(key);
    if (!cell) { cell = []; vineGrid.set(key, cell); }
    cell.push({ x, y, tipIdx });
  }

  function* nearbyVinePoints(x, y) {
    const gx = Math.floor(x / VP_CELL);
    const gy = Math.floor(y / VP_CELL);
    for (let dx = -1; dx <= 1; dx++) {
      for (let dy = -1; dy <= 1; dy++) {
        const cell = vineGrid.get(`${gx + dx},${gy + dy}`);
        if (cell) yield* cell;
      }
    }
  }

  // Diagnostic stats
  const stats = { seeds: 0, branches: 0, deaths: { sdf: 0, boundary: 0, collision: 0, stalled: 0, budget: 0 }, maxSteps: 0, totalPoints: 0 };

  // --- Seed tips ---
  if (mode === 'fill') {
    const faces = extractPlanarFaces(nc.strokes, bounds);
    for (const face of faces) {
      if (totalBranches >= maxBranches) break;
      const polygon = face.polygon;
      if (!polygon || polygon.length < 3) continue;

      // Compute centroid
      let cx = 0, cy = 0;
      for (const p of polygon) { cx += p.x; cy += p.y; }
      cx /= polygon.length;
      cy /= polygon.length;

      // Get color from nearby stroke
      const nearStroke = findNearestStroke(cx, cy, nc);
      const srcColor = getStrokeColor(nearStroke);
      const srcSize = getStrokeBrushSize(nearStroke);
      const rgb = hexToRgb(srcColor);
      const hsl = _rgbToHsl(rgb.r, rgb.g, rgb.b);

      // Seed tips along polygon boundary pointing inward
      const tipCount = Math.min(Math.ceil(polygon.length / 3), maxBranches - totalBranches);
      const tipStep = Math.max(1, Math.floor(polygon.length / tipCount));
      for (let i = 0; i < polygon.length && totalBranches < maxBranches; i += tipStep) {
        const p = polygon[i];
        const angle = Math.atan2(cy - p.y, cx - p.x);
        tips.push({
          x: p.x, y: p.y, angle,
          sourceAngle: angle,
          h: hsl.h, s: hsl.s, l: hsl.l,
          brushSize: srcSize * 0.8,
          generation: 0, distFromOrigin: 0, stepCount: 0,
          stepsRemaining: TIP_BUDGET,
          points: [{ x: p.x, y: p.y }],
          alive: true, cooldown: 0,
        });
        totalBranches++;
      }
    }
  } else {
    // Grow mode — seed from EVERY endpoint (both start + end of every stroke)
    for (const stroke of nc.strokes) {
      if (totalBranches >= maxBranches) break;
      const pts = (stroke.path || stroke.points || []).map(p => ({ x: p.x, y: p.y }));
      if (pts.length < 2) continue;

      const srcColor = getStrokeColor(stroke);
      const srcSize = getStrokeBrushSize(stroke);
      const rgb = hexToRgb(srcColor);
      const hsl = _rgbToHsl(rgb.r, rgb.g, rgb.b);

      // Seed both start and end
      const endpoints = [
        { pt: pts[0], angle: Math.atan2(pts[1].y - pts[0].y, pts[1].x - pts[0].x) + Math.PI }, // start — flip outward
        { pt: pts[pts.length - 1], angle: Math.atan2(pts[pts.length - 1].y - pts[pts.length - 2].y, pts[pts.length - 1].x - pts[pts.length - 2].x) }, // end — already outward
      ];

      for (const ep of endpoints) {
        if (totalBranches >= maxBranches) break;
        tips.push({
          x: ep.pt.x, y: ep.pt.y, angle: ep.angle,
          sourceAngle: ep.angle,
          h: hsl.h, s: hsl.s, l: hsl.l,
          brushSize: srcSize * 0.8,
          generation: 0, distFromOrigin: 0, stepCount: 0,
          stepsRemaining: TIP_BUDGET,
          points: [{ x: ep.pt.x, y: ep.pt.y }],
          alive: true, cooldown: 0,
        });
        totalBranches++;
      }
    }
  }

  if (tips.length === 0) return [];
  stats.seeds = tips.length;

  // --- Growth loop (per-tip step budget) ---
  let globalIterations = 0;
  while (globalIterations < MAX_GLOBAL_ITERATIONS && tips.some(t => t.alive && t.stepsRemaining > 0)) {
    globalIterations++;

    for (let ti = 0; ti < tips.length; ti++) {
      const tip = tips[ti];
      if (!tip.alive || tip.stepsRemaining <= 0) continue;

      tip.stepsRemaining--;
      tip.stepCount++;

      // 1. Base direction — blend between source tangent (momentum) and current heading
      // First ~12 steps strongly follow the source stroke direction, then gradually loosen
      const MOMENTUM_STEPS = 12;
      const momentum = tip.stepCount < MOMENTUM_STEPS
        ? 1 - (tip.stepCount / MOMENTUM_STEPS) * 0.8  // 1.0 → 0.2 over 12 steps
        : 0;
      const srcDx = Math.cos(tip.sourceAngle);
      const srcDy = Math.sin(tip.sourceAngle);
      const curDx = Math.cos(tip.angle);
      const curDy = Math.sin(tip.angle);
      let dx = srcDx * momentum + curDx * (1 - momentum);
      let dy = srcDy * momentum + curDy * (1 - momentum);

      // 2. SDF edge interaction (unsigned distance — open polylines have unreliable sign)
      const dist = Math.abs(sdf.query(tip.x, tip.y));

      // Kill if overlapping a stroke (after momentum phase grace period)
      if (tip.stepCount > 15 && dist < stepLen * 0.8) {
        tip.points.pop();
        tip.alive = false;
        stats.deaths.sdf++;
        continue;
      }

      if (dist < EDGE_THRESHOLD) {
        const grad = sdf.gradient(tip.x, tip.y);
        // Tangent = perpendicular to gradient
        const tx = -grad.y;
        const ty = grad.x;
        // Blend toward tangent proportional to proximity
        const blendFactor = (1 - dist / EDGE_THRESHOLD) * EDGE_FOLLOW_BLEND;
        // Pick tangent direction closest to current heading
        const dot = dx * tx + dy * ty;
        const signT = dot >= 0 ? 1 : -1;
        dx = dx * (1 - blendFactor) + signT * tx * blendFactor;
        dy = dy * (1 - blendFactor) + signT * ty * blendFactor;

        // Stronger repulsion when close to strokes (always push away)
        if (dist < stepLen * 3) {
          const repel = (1 - dist / (stepLen * 3)) * 0.8;
          dx += grad.x * repel;
          dy += grad.y * repel;
        }
      }

      // 3. Curl noise
      const noiseAngle = noise2d(tip.x * NOISE_SCALE, tip.y * NOISE_SCALE) * Math.PI * 2;
      dx += Math.cos(noiseAngle) * NOISE_STRENGTH;
      dy += Math.sin(noiseAngle) * NOISE_STRENGTH;

      // 4. Cross-tip avoidance (spatial hash, skip own trail)
      let avoidX = 0, avoidY = 0;
      for (const vp of nearbyVinePoints(tip.x, tip.y)) {
        if (vp.tipIdx === ti) continue; // don't avoid own trail
        const adx = tip.x - vp.x;
        const ady = tip.y - vp.y;
        const ad2 = adx * adx + ady * ady;
        if (ad2 < AVOID_RADIUS * AVOID_RADIUS && ad2 > 1) {
          const ad = Math.sqrt(ad2);
          avoidX += (adx / ad) * (1 - ad / AVOID_RADIUS);
          avoidY += (ady / ad) * (1 - ad / AVOID_RADIUS);
        }
      }
      dx += avoidX * 0.5;
      dy += avoidY * 0.5;

      // 5. Density repulsion
      const localDensity = densityMap.get(tip.x, tip.y);
      if (localDensity > 0.3) {
        dx += (noise2d(tip.x * 0.02, globalIterations * 0.1) - 0.5) * localDensity * 0.8;
        dy += (noise2d(globalIterations * 0.1, tip.y * 0.02) - 0.5) * localDensity * 0.8;
      }

      // 6. Normalize and step forward
      const dLen = Math.sqrt(dx * dx + dy * dy);
      if (dLen < 1e-6) { tip.alive = false; stats.deaths.stalled++; continue; }
      dx /= dLen;
      dy /= dLen;

      tip.x += dx * stepLen;
      tip.y += dy * stepLen;
      tip.angle = Math.atan2(dy, dx);
      tip.distFromOrigin += stepLen;
      tip.points.push({ x: tip.x, y: tip.y });

      // Record for cross-tip avoidance (every 3rd point, spatial hash)
      vinePointCounter++;
      if (vinePointCounter % 3 === 0) {
        addVinePoint(tip.x, tip.y, ti);
      }

      // 7. Color drift (HSL random walk) — grace period before drift begins
      const rawDistRatio = clamp(tip.distFromOrigin / (radius * 1.5), 0, 1);
      const distRatio = tip.distFromOrigin < COLOR_GRACE_DIST ? 0 : rawDistRatio;
      const walkWidth = driftRange * distRatio;
      const colorNoise = noise2d(tip.x * 0.01 + globalIterations * 0.3, tip.y * 0.01);
      tip.h = (tip.h + (colorNoise - 0.5) * walkWidth * 60 + 360) % 360;
      tip.s = clamp(tip.s + (colorNoise - 0.5) * walkWidth * 15, 10, 95);
      // Slight upward bias (+0.3) prevents vines from going dark too quickly
      tip.l = clamp(tip.l + (noise2d(globalIterations * 0.3, tip.x * 0.01) - 0.2) * walkWidth * 10, 35, 85);

      // 8. Branch decision (suppressed during momentum phase)
      if (tip.cooldown > 0) {
        tip.cooldown--;
      } else if (tip.stepCount <= MOMENTUM_STEPS) {
        // No branching during momentum phase — let vine establish direction first
      } else {
        const sparseness = 1 - localDensity;
        const effectiveProb = branchProb
          * (1 + distRatio * 0.5)
          * (1 + sparseness * 0.3)
          * (tip.generation < 2 ? 1.0 : 0.5);
        if (noise2d(globalIterations * 1.7 + ti * 3.1, tip.x * 0.05) < effectiveProb
            && tip.generation < MAX_GENERATION
            && totalBranches < maxBranches) {
          // Fork: ±50-90° from current heading (wide spread)
          const forkAngle = (50 + noise2d(ti * 2.3, globalIterations * 1.1) * 40) * Math.PI / 180;
          const forkSign = noise2d(globalIterations * 0.9, ti * 1.7) > 0.5 ? 1 : -1;
          const branchAngle = tip.angle + forkSign * forkAngle;
          tips.push({
            x: tip.x, y: tip.y,
            angle: branchAngle,
            sourceAngle: branchAngle, // branch inherits its fork angle as momentum
            h: tip.h, s: tip.s, l: tip.l,
            brushSize: tip.brushSize * SIZE_SHRINK,
            generation: tip.generation + 1,
            distFromOrigin: tip.distFromOrigin, stepCount: 0,
            stepsRemaining: TIP_BUDGET,
            points: [{ x: tip.x, y: tip.y }],
            alive: true, cooldown: 0,
          });
          totalBranches++;
          stats.branches++;
          tip.cooldown = 8;
        }
      }

      // 9. Death conditions
      const offX = tip.x - nearX;
      const offY = tip.y - nearY;
      if (offX * offX + offY * offY > radius * radius * 16) {  // 4× radius boundary
        tip.alive = false;
        stats.deaths.boundary++;
        continue;
      }
      // Cross-tip collision (skip during momentum phase — seeds start near each other)
      if (tip.stepCount > 15) {
        for (const vp of nearbyVinePoints(tip.x, tip.y)) {
          if (vp.tipIdx === ti) continue;
          const cdx = tip.x - vp.x;
          const cdy = tip.y - vp.y;
          if (cdx * cdx + cdy * cdy < COLLISION_DIST * COLLISION_DIST) {
            tip.alive = false;
            stats.deaths.collision++;
            break;
          }
        }
      }

      // Track max steps for diagnostics
      if (tip.stepCount > stats.maxSteps) stats.maxSteps = tip.stepCount;
    }
  }

  // Count budget exhaustions
  for (const tip of tips) {
    if (tip.stepsRemaining <= 0 && tip.alive) {
      stats.deaths.budget++;
      tip.alive = false;
    }
  }

  // --- Convert trails to strokes ---
  for (const tip of tips) {
    if (tip.points.length < 3) continue;
    const color = hslToHex(tip.h, tip.s, tip.l);
    const opacity = clamp(0.9 - tip.generation * 0.12, 0.3, 0.9);
    strokes.push(makeStroke(tip.points, color, tip.brushSize, opacity, 'taper'));
    stats.totalPoints += tip.points.length;
  }

  return strokes;
}
