/**
 * Hyperbolic Tiling — Poincare disk model {p,q} tiling with Mobius transforms.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'hyperbolicTiling',
  description: 'Poincare disk model hyperbolic tiling using Mobius transformations',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 170, description: 'Poincare disk radius' },
    p:             { type: 'number', required: false, default: 5, description: 'Polygon sides (3-8)' },
    q:             { type: 'number', required: false, default: 4, description: 'Polygons meeting at each vertex (3-8)' },
    maxDepth:      { type: 'number', required: false, default: 3, description: 'Recursion depth (1-4)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

// Complex number operations
function cAdd(a, b) { return [a[0] + b[0], a[1] + b[1]]; }
function cSub(a, b) { return [a[0] - b[0], a[1] - b[1]]; }
function cMul(a, b) { return [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]]; }
function cDiv(a, b) {
  const d = b[0] * b[0] + b[1] * b[1];
  if (d < 1e-15) return [0, 0];
  return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d];
}
function cConj(a) { return [a[0], -a[1]]; }
function cAbs(a) { return Math.sqrt(a[0] * a[0] + a[1] * a[1]); }

// Mobius transformation: M(z) = (z - a) / (1 - conj(a)*z)
// This maps point a to 0 in the Poincare disk
function mobius(z, a) {
  return cDiv(cSub(z, a), cSub([1, 0], cMul(cConj(a), z)));
}

// Inverse Mobius: maps 0 back to a
function mobiusInv(z, a) {
  return cDiv(cAdd(z, a), cAdd([1, 0], cMul(cConj(a), z)));
}

/**
 * Generate a hyperbolic {p,q} tiling in the Poincare disk model.
 *
 * Computes the central regular p-gon inscribed in the Poincare disk at the
 * correct hyperbolic distance, then uses Mobius transformations to replicate
 * it outward. Each polygon is drawn as a closed stroke with geodesic arcs
 * approximated as line segments.
 *
 * @returns {Array} Array of stroke objects
 */
export function hyperbolicTiling(cx, cy, radius, p, q, maxDepth, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 170, 10, 500);
  p = clamp(Math.round(Number(p) || 5), 3, 8);
  q = clamp(Math.round(Number(q) || 4), 3, 8);
  maxDepth = clamp(Math.round(Number(maxDepth) || 3), 1, 4);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  // Check hyperbolic condition: (p-2)(q-2) > 4
  if ((p - 2) * (q - 2) <= 4) {
    // Not hyperbolic, fall back to valid config
    p = 5; q = 4;
  }

  const result = [];

  // Compute the distance from center to vertex of the fundamental polygon
  // In the Poincare disk: cosh(d) = cos(pi/q) / sin(pi/p)
  const cosDist = Math.cos(Math.PI / q) / Math.sin(Math.PI / p);
  // Convert hyperbolic distance to Poincare disk radius: r = tanh(d/2)
  const hypDist = Math.acosh(cosDist);
  const vertexR = Math.tanh(hypDist / 2);

  // Compute edge midpoint distance for reflection
  // cosh(d_mid) = cos(pi/p) / sin(pi/q) ... but we'll use vertex-to-vertex reflection
  // Distance from center to edge midpoint:
  const cosMidDist = Math.cos(Math.PI / p) / Math.sin(Math.PI / q);
  const midHypDist = Math.acosh(cosMidDist);
  const edgeMidR = Math.tanh(midHypDist / 2);

  // Generate the central polygon vertices in the Poincare disk
  function centralPolygon() {
    const verts = [];
    for (let i = 0; i < p; i++) {
      const angle = (2 * Math.PI * i) / p - Math.PI / 2;
      verts.push([vertexR * Math.cos(angle), vertexR * Math.sin(angle)]);
    }
    return verts;
  }

  // Draw a geodesic arc between two points in the Poincare disk
  // In the Poincare disk, geodesics are circular arcs orthogonal to the boundary
  function geodesicPoints(z1, z2, numPts) {
    const pts = [];
    // For simplicity, linearly interpolate in the disk (good approximation for small polygons)
    for (let i = 0; i <= numPts; i++) {
      const t = i / numPts;
      const zr = z1[0] + (z2[0] - z1[0]) * t;
      const zi = z1[1] + (z2[1] - z1[1]) * t;
      pts.push([zr, zi]);
    }
    return pts;
  }

  // Draw a polygon given its vertices in disk coordinates
  function drawPolygon(verts, depth) {
    if (result.length >= 195) return;

    const pts = [];
    const segsPerEdge = 4;
    for (let i = 0; i < verts.length; i++) {
      const next = (i + 1) % verts.length;
      const arcPts = geodesicPoints(verts[i], verts[next], segsPerEdge);
      for (let j = (i === 0 ? 0 : 1); j < arcPts.length; j++) {
        pts.push({
          x: cx + arcPts[j][0] * radius,
          y: cy + arcPts[j][1] * radius,
        });
      }
    }
    // Close the polygon
    pts.push({ x: pts[0].x, y: pts[0].y });

    const t = 1 - clamp(depth / maxDepth, 0, 1);
    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');
    result.push(makeStroke(pts, c, brushSize, opacity, pressureStyle));
  }

  // Track visited polygon centers to avoid duplicates
  const visited = new Set();
  const GRID_RES = 1000;

  function centerKey(verts) {
    let sx = 0, sy = 0;
    for (const v of verts) { sx += v[0]; sy += v[1]; }
    sx /= verts.length; sy /= verts.length;
    return Math.round(sx * GRID_RES) + ',' + Math.round(sy * GRID_RES);
  }

  // Reflect a point across a geodesic defined by its midpoint on disk
  function reflectAcrossEdge(verts, edgeIdx) {
    const v1 = verts[edgeIdx];
    const v2 = verts[(edgeIdx + 1) % verts.length];
    // Edge midpoint in the disk
    const mid = [(v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2];
    const midR = cAbs(mid);

    if (midR < 1e-10) return null;

    // Reflect each vertex through the edge using Mobius transform:
    // 1. Translate mid to origin via Mobius
    // 2. Reflect across real axis (or the appropriate geodesic)
    // 3. Translate back
    const newVerts = [];
    for (const v of verts) {
      // Move midpoint to origin
      const w = mobius(v, mid);
      // Reflect through the geodesic (rotation by pi around the edge)
      // The edge through the origin is a diameter; reflect across it
      const edgeInOrigin1 = mobius(v1, mid);
      const edgeAngle = Math.atan2(edgeInOrigin1[1], edgeInOrigin1[0]);
      // Reflect w across the line at angle edgeAngle
      const cos2a = Math.cos(2 * edgeAngle);
      const sin2a = Math.sin(2 * edgeAngle);
      const reflected = [
        w[0] * cos2a + w[1] * sin2a,
        w[0] * sin2a - w[1] * cos2a,
      ];
      // Move back
      const nv = mobiusInv(reflected, mid);
      if (cAbs(nv) > 0.97) return null; // too close to boundary
      newVerts.push(nv);
    }

    return newVerts;
  }

  // BFS to tile the disk
  const queue = [];
  const centralVerts = centralPolygon();
  const ck = centerKey(centralVerts);
  visited.add(ck);
  queue.push({ verts: centralVerts, depth: 0 });
  drawPolygon(centralVerts, 0);

  while (queue.length > 0 && result.length < 190) {
    const { verts, depth } = queue.shift();
    if (depth >= maxDepth) continue;

    // Try reflecting across each edge
    for (let e = 0; e < p; e++) {
      const reflected = reflectAcrossEdge(verts, e);
      if (!reflected) continue;

      const key = centerKey(reflected);
      if (visited.has(key)) continue;

      // Check all vertices are within the disk
      let inside = true;
      for (const v of reflected) {
        if (cAbs(v) > 0.96) { inside = false; break; }
      }
      if (!inside) continue;

      visited.add(key);
      drawPolygon(reflected, depth + 1);
      queue.push({ verts: reflected, depth: depth + 1 });
    }
  }

  return result.slice(0, 200);
}
