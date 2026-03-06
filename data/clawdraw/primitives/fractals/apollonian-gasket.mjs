/**
 * Apollonian Gasket — recursive circle packing via Descartes circle theorem.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, makeStroke, samplePalette } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'apollonianGasket',
  description: 'Recursive circle packing using Descartes circle theorem',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    radius:        { type: 'number', required: false, default: 150, description: 'Outer circle radius' },
    maxDepth:      { type: 'number', required: false, default: 4, description: 'Recursion depth (1-6)' },
    minRadius:     { type: 'number', required: false, default: 3, description: 'Minimum circle radius to draw' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 3, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.85, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name (magma, plasma, viridis, turbo, inferno)' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

/**
 * Draw a circle as a closed polygon stroke.
 */
function circlePoints(cx, cy, r, numPts) {
  const pts = [];
  for (let i = 0; i <= numPts; i++) {
    const a = (i / numPts) * Math.PI * 2;
    pts.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
  }
  return pts;
}

/**
 * Generate an Apollonian gasket fractal.
 *
 * Starts with three mutually tangent circles inscribed in an outer circle,
 * then recursively fills the gaps using the Descartes circle theorem.
 *
 * @returns {Array} Array of stroke objects
 */
export function apollonianGasket(cx, cy, radius, maxDepth, minRadius, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  radius = clamp(Number(radius) || 150, 10, 500);
  maxDepth = clamp(Math.round(Number(maxDepth) || 4), 1, 6);
  minRadius = clamp(Number(minRadius) || 3, 1, 50);
  brushSize = clamp(Number(brushSize) || 3, 3, 100);
  opacity = clamp(Number(opacity) || 0.85, 0.01, 1);

  const result = [];

  // Draw the outer bounding circle
  const outerColor = palette ? samplePalette(palette, 0) : (color || '#ffffff');
  result.push(makeStroke(circlePoints(cx, cy, radius, 36), outerColor, brushSize, opacity, pressureStyle));

  // Three mutually tangent circles inscribed in the outer circle.
  // Place three equal circles of radius r = radius * (2/3 - 1/3) ≈ radius / (1 + 2/sqrt(3))
  // Using Soddy configuration: three equal circles tangent to each other and internally tangent to outer circle.
  const r3 = radius / (1 + 2 / Math.sqrt(3));
  const dist = radius - r3; // distance from center to each inner circle center

  const circles = [];
  for (let i = 0; i < 3; i++) {
    const a = (i / 3) * Math.PI * 2 - Math.PI / 2;
    circles.push({ x: cx + Math.cos(a) * dist, y: cy + Math.sin(a) * dist, r: r3 });
  }

  // Draw the initial three circles
  for (let i = 0; i < 3; i++) {
    const c = circles[i];
    const numPts = clamp(Math.round(c.r * 0.8), 12, 40);
    const col = palette ? samplePalette(palette, 0.2) : (color || '#ffffff');
    result.push(makeStroke(circlePoints(c.x, c.y, c.r, numPts), col, brushSize, opacity, pressureStyle));
  }

  // Use Descartes theorem to find the circle tangent to three given circles.
  // k = curvature = 1/r. For internally tangent outer circle, k is negative.
  // k4 = k1 + k2 + k3 + 2*sqrt(k1*k2 + k2*k3 + k1*k3)
  // Complex Descartes for center: z4 = (z1*k1 + z2*k2 + z3*k3 + 2*sqrt(k1*k2*z1*z2 + k2*k3*z2*z3 + k1*k3*z1*z3)) / k4

  function descartesK(k1, k2, k3) {
    const sum = k1 + k2 + k3;
    const disc = k1 * k2 + k2 * k3 + k1 * k3;
    if (disc < 0) return null;
    return sum + 2 * Math.sqrt(disc);
  }

  // Represent circles as {x, y, r, k} where k = 1/r (negative for outer bounding circle)
  const outerCircle = { x: cx, y: cy, r: radius, k: -1 / radius };
  const innerCircles = circles.map(c => ({ x: c.x, y: c.y, r: c.r, k: 1 / c.r }));

  // Find the Soddy circle tangent to three circles using Descartes theorem
  function findSoddyCircle(c1, c2, c3) {
    const k4 = descartesK(c1.k, c2.k, c3.k);
    if (k4 === null || k4 <= 0) return null;
    const r4 = 1 / k4;
    if (r4 < minRadius * 0.5) return null;

    // Use complex Descartes to find center
    // z = x + iy, multiply by k
    const zk1r = c1.x * c1.k, zk1i = c1.y * c1.k;
    const zk2r = c2.x * c2.k, zk2i = c2.y * c2.k;
    const zk3r = c3.x * c3.k, zk3i = c3.y * c3.k;

    const sumR = zk1r + zk2r + zk3r;
    const sumI = zk1i + zk2i + zk3i;

    // sqrt(k1*k2*z1*z2 + k2*k3*z2*z3 + k1*k3*z1*z3)
    // Each term: ka*kb * (xa+iya)*(xb+iyb) = ka*kb * ((xa*xb - ya*yb) + i(xa*yb + ya*xb))
    function complexMul(ar, ai, br, bi) {
      return [ar * br - ai * bi, ar * bi + ai * br];
    }

    const [t1r, t1i] = complexMul(c1.x, c1.y, c2.x, c2.y);
    const [t2r, t2i] = complexMul(c2.x, c2.y, c3.x, c3.y);
    const [t3r, t3i] = complexMul(c1.x, c1.y, c3.x, c3.y);

    const discR = c1.k * c2.k * t1r + c2.k * c3.k * t2r + c1.k * c3.k * t3r;
    const discI = c1.k * c2.k * t1i + c2.k * c3.k * t2i + c1.k * c3.k * t3i;

    // Complex square root
    const mag = Math.sqrt(discR * discR + discI * discI);
    if (mag < 1e-12) {
      return { x: sumR / k4, y: sumI / k4, r: r4, k: k4 };
    }
    const sqrtMag = Math.sqrt(mag);
    const angle = Math.atan2(discI, discR) / 2;
    const sqrtR = sqrtMag * Math.cos(angle);
    const sqrtI = sqrtMag * Math.sin(angle);

    const z4r = (sumR + 2 * sqrtR) / k4;
    const z4i = (sumI + 2 * sqrtI) / k4;

    return { x: z4r, y: z4i, r: r4, k: k4 };
  }

  // Check if a circle overlaps significantly with any existing circle
  function overlapsExisting(nc, existing) {
    for (const ec of existing) {
      if (ec.k < 0) continue; // skip outer
      const d = Math.hypot(nc.x - ec.x, nc.y - ec.y);
      const rsum = nc.r + ec.r;
      if (d < rsum * 0.8 && Math.abs(nc.r - ec.r) / Math.max(nc.r, ec.r) < 0.1) return true;
    }
    return false;
  }

  const allCircles = [outerCircle, ...innerCircles];

  // Recursively fill gaps between triplets of tangent circles
  function fillGap(c1, c2, c3, depth) {
    if (result.length >= 195 || depth >= maxDepth) return;

    const nc = findSoddyCircle(c1, c2, c3);
    if (!nc || nc.r < minRadius) return;

    // Check the new circle is within bounds
    const d = Math.hypot(nc.x - cx, nc.y - cy);
    if (d + nc.r > radius + 2) return;
    if (overlapsExisting(nc, allCircles)) return;

    allCircles.push(nc);

    const t = clamp(1 - nc.r / r3, 0, 1);
    const col = palette ? samplePalette(palette, t) : (color || '#ffffff');
    const numPts = clamp(Math.round(nc.r * 0.8), 10, 36);
    result.push(makeStroke(circlePoints(nc.x, nc.y, nc.r, numPts), col, brushSize, opacity, pressureStyle));

    // Recurse into the three new gaps formed
    fillGap(c1, c2, nc, depth + 1);
    fillGap(c2, c3, nc, depth + 1);
    fillGap(c1, c3, nc, depth + 1);
  }

  // Fill gaps between each pair of inner circles and the outer circle
  fillGap(outerCircle, innerCircles[0], innerCircles[1], 0);
  fillGap(outerCircle, innerCircles[1], innerCircles[2], 0);
  fillGap(outerCircle, innerCircles[0], innerCircles[2], 0);

  // Fill the central gap between the three inner circles
  fillGap(innerCircles[0], innerCircles[1], innerCircles[2], 0);

  return result.slice(0, 200);
}
