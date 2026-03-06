/**
 * Spatial analysis primitives — pure geometry module for canvas topology analysis.
 *
 * Analyzes existing nearby strokes to extract canvas topology: edge classification,
 * density mapping, enclosed region detection, and attractor point generation.
 *
 * Strokes are arrays of {x, y} points (or objects with .path / .points arrays).
 * This module performs NO drawing — it returns analysis results only.
 */

// ---------------------------------------------------------------------------
// Internal geometry helpers
// ---------------------------------------------------------------------------

/** Euclidean distance between two points. */
function dist(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
}

/** Squared distance between two points (avoids sqrt when only comparing). */
function dist2(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return dx * dx + dy * dy;
}

/** Normalize a 2D vector. Returns {x: 0, y: 0} for zero-length input. */
function normalize(v) {
  const len = Math.sqrt(v.x * v.x + v.y * v.y);
  if (len < 1e-10) return { x: 0, y: 0 };
  return { x: v.x / len, y: v.y / len };
}

/** Extract plain {x, y} point array from a stroke object. */
function getPoints(stroke) {
  const raw = stroke.path || stroke.points || [];
  return raw.map(p => ({ x: p.x, y: p.y }));
}

/** Compute the angle (radians) of the stroke at its start or end. */
function endpointAngle(points, which) {
  if (points.length < 2) return 0;
  if (which === 'start') {
    return Math.atan2(points[1].y - points[0].y, points[1].x - points[0].x);
  }
  const n = points.length;
  return Math.atan2(points[n - 1].y - points[n - 2].y, points[n - 1].x - points[n - 2].x);
}

/**
 * Minimum distance from a point to a line segment (a → b).
 */
function pointToSegmentDist(px, py, ax, ay, bx, by) {
  const dx = bx - ax;
  const dy = by - ay;
  const len2 = dx * dx + dy * dy;
  if (len2 < 1e-10) return Math.sqrt((px - ax) * (px - ax) + (py - ay) * (py - ay));
  let t = ((px - ax) * dx + (py - ay) * dy) / len2;
  t = Math.max(0, Math.min(1, t));
  const cx = ax + t * dx;
  const cy = ay + t * dy;
  return Math.sqrt((px - cx) * (px - cx) + (py - cy) * (py - cy));
}

// ---------------------------------------------------------------------------
// 1. classifyEndpoints — Edge classifier for exterior/interior endpoints
// ---------------------------------------------------------------------------

/**
 * Classify stroke endpoints as "exterior" (surrounded by open space) or "interior".
 *
 * For each stroke, examines both the first and last point. Around each endpoint,
 * 8 angular sectors (45 deg each) are sampled within the given radius. Sectors
 * that contain no nearby stroke geometry are considered "empty". An endpoint with
 * 3 or more empty sectors is classified as exterior; otherwise interior.
 *
 * Exterior endpoints include a `growthDir` vector pointing toward open space
 * (centroid of empty sector directions), useful for determining where new
 * strokes could naturally extend.
 *
 * @param {Array} strokes - Array of stroke objects with .path or .points
 * @param {number} [radius=80] - Sampling radius around each endpoint
 * @returns {{ exterior: Array<{x, y, growthDir: {x, y}, strokeId: string, angle: number, which: string, emptySectors: number}>, interior: Array<{x, y, strokeId: string}> }}
 */
export function classifyEndpoints(strokes, radius = 80) {
  if (!strokes || strokes.length === 0) return { exterior: [], interior: [] };

  const NUM_SECTORS = 8;
  const SECTOR_ANGLE = (2 * Math.PI) / NUM_SECTORS;

  // Pre-extract all stroke segments for fast sector occupancy checks
  const allSegments = [];
  for (const stroke of strokes) {
    const pts = getPoints(stroke);
    for (let i = 0; i < pts.length - 1; i++) {
      allSegments.push({ ax: pts[i].x, ay: pts[i].y, bx: pts[i + 1].x, by: pts[i + 1].y });
    }
  }

  /**
   * For a given endpoint, determine which of the 8 sectors contain nearby stroke geometry.
   * Returns a boolean array of length 8 (true = sector has strokes).
   */
  function sectorOccupancy(ep, ownerStrokeId) {
    const occupied = new Array(NUM_SECTORS).fill(false);

    for (const seg of allSegments) {
      // Quick bounding check — skip segments too far away
      const midX = (seg.ax + seg.bx) / 2;
      const midY = (seg.ay + seg.by) / 2;
      const segHalfLen = Math.sqrt((seg.bx - seg.ax) ** 2 + (seg.by - seg.ay) ** 2) / 2;
      if (dist2(ep, { x: midX, y: midY }) > (radius + segHalfLen) * (radius + segHalfLen)) continue;

      // Check if segment is within radius of endpoint
      const d = pointToSegmentDist(ep.x, ep.y, seg.ax, seg.ay, seg.bx, seg.by);
      if (d > radius) continue;

      // Determine which sector(s) this segment falls into
      // Sample both segment endpoints and midpoint
      const samplePts = [
        { x: seg.ax, y: seg.ay },
        { x: seg.bx, y: seg.by },
        { x: midX, y: midY },
      ];

      for (const sp of samplePts) {
        const dx = sp.x - ep.x;
        const dy = sp.y - ep.y;
        const d2 = dx * dx + dy * dy;
        if (d2 > radius * radius || d2 < 1e-6) continue;
        let angle = Math.atan2(dy, dx);
        if (angle < 0) angle += 2 * Math.PI;
        const sector = Math.floor(angle / SECTOR_ANGLE) % NUM_SECTORS;
        occupied[sector] = true;
      }
    }

    return occupied;
  }

  const exterior = [];
  const interior = [];

  for (const stroke of strokes) {
    const pts = getPoints(stroke);
    if (pts.length < 2) continue;
    const strokeId = stroke.id || '';

    const endpoints = [
      { pt: pts[0], which: 'start' },
      { pt: pts[pts.length - 1], which: 'end' },
    ];

    for (const { pt, which } of endpoints) {
      const occupied = sectorOccupancy(pt, strokeId);
      const emptySectorIndices = [];
      for (let s = 0; s < NUM_SECTORS; s++) {
        if (!occupied[s]) emptySectorIndices.push(s);
      }

      if (emptySectorIndices.length >= 3) {
        // Compute growth direction: centroid of empty sector directions
        let gx = 0, gy = 0;
        for (const s of emptySectorIndices) {
          const a = s * SECTOR_ANGLE + SECTOR_ANGLE / 2;
          gx += Math.cos(a);
          gy += Math.sin(a);
        }
        const growthDir = normalize({ x: gx, y: gy });
        const angle = endpointAngle(pts, which);

        exterior.push({
          x: pt.x,
          y: pt.y,
          growthDir,
          strokeId,
          angle,
          which,
          emptySectors: emptySectorIndices.length,
        });
      } else {
        interior.push({
          x: pt.x,
          y: pt.y,
          strokeId,
        });
      }
    }
  }

  return { exterior, interior };
}

// ---------------------------------------------------------------------------
// 2. buildDensityMap — Grid-based stroke density tracking
// ---------------------------------------------------------------------------

/**
 * Build a grid-based stroke density map over the specified bounds.
 *
 * Creates a gridRes x gridRes grid covering the bounding rectangle. Each stroke
 * point increments the cell it falls in. The grid is then normalized so the
 * maximum cell value is 1.0.
 *
 * @param {Array} strokes - Array of stroke objects with .path or .points
 * @param {{minX: number, minY: number, maxX: number, maxY: number}} bounds - Region to map
 * @param {number} [gridRes=32] - Grid resolution (cells per axis)
 * @returns {{ get: (x: number, y: number) => number, hotspots: () => Array<{x, y, density}>, sparse: () => Array<{x, y}> }}
 */
export function buildDensityMap(strokes, bounds, gridRes = 32) {
  const { minX, minY, maxX, maxY } = bounds;
  const width = maxX - minX;
  const height = maxY - minY;

  // Allocate grid
  const grid = new Float64Array(gridRes * gridRes);

  // Guard against degenerate bounds
  if (width < 1e-6 || height < 1e-6) {
    return {
      get: () => 0,
      hotspots: () => [],
      sparse: () => [],
    };
  }

  const cellW = width / gridRes;
  const cellH = height / gridRes;

  // Accumulate stroke points into grid cells
  let maxVal = 0;
  if (strokes && strokes.length > 0) {
    for (const stroke of strokes) {
      const pts = getPoints(stroke);
      for (const p of pts) {
        const col = Math.floor((p.x - minX) / cellW);
        const row = Math.floor((p.y - minY) / cellH);
        if (col >= 0 && col < gridRes && row >= 0 && row < gridRes) {
          const idx = row * gridRes + col;
          grid[idx]++;
          if (grid[idx] > maxVal) maxVal = grid[idx];
        }
      }
    }
  }

  // Normalize
  if (maxVal > 0) {
    for (let i = 0; i < grid.length; i++) {
      grid[i] /= maxVal;
    }
  }

  /** Get density at a world-space coordinate (0-1, 0=empty, 1=saturated). */
  function get(x, y) {
    const col = Math.floor((x - minX) / cellW);
    const row = Math.floor((y - minY) / cellH);
    if (col < 0 || col >= gridRes || row < 0 || row >= gridRes) return 0;
    return grid[row * gridRes + col];
  }

  /** Return cells with density above 0.7 as hotspot locations. */
  function hotspots() {
    const result = [];
    for (let r = 0; r < gridRes; r++) {
      for (let c = 0; c < gridRes; c++) {
        const d = grid[r * gridRes + c];
        if (d > 0.7) {
          result.push({
            x: minX + (c + 0.5) * cellW,
            y: minY + (r + 0.5) * cellH,
            density: d,
          });
        }
      }
    }
    return result;
  }

  /** Return cells with density below 0.1 that are within bounds (sparse regions). */
  function sparse() {
    const result = [];
    for (let r = 0; r < gridRes; r++) {
      for (let c = 0; c < gridRes; c++) {
        const d = grid[r * gridRes + c];
        if (d < 0.1) {
          result.push({
            x: minX + (c + 0.5) * cellW,
            y: minY + (r + 0.5) * cellH,
          });
        }
      }
    }
    return result;
  }

  return { get, hotspots, sparse };
}

// ---------------------------------------------------------------------------
// 3. detectEnclosedRegions — Enclosed region detector using ray-casting
// ---------------------------------------------------------------------------

/**
 * Detect enclosed regions formed by strokes using the even-odd ray-casting rule.
 *
 * Samples a grid of test points across the given bounds. For each point, a ray
 * is cast in the +x direction and intersections with all stroke segments are
 * counted. Odd intersection count = inside, even = outside. Adjacent "inside"
 * points are then clustered into regions via flood-fill, and each region's
 * centroid, area, boundary points, and point count are computed.
 *
 * @param {Array} strokes - Array of stroke objects with .path or .points
 * @param {{minX: number, minY: number, maxX: number, maxY: number}} bounds - Search region
 * @param {number} [resolution=20] - Grid resolution for test point sampling
 * @returns {Array<{centroid: {x, y}, area: number, boundary: Array<{x, y}>, pointCount: number}>}
 */
export function detectEnclosedRegions(strokes, bounds, resolution = 60) {
  if (!strokes || strokes.length === 0) return [];

  const { minX, minY, maxX, maxY } = bounds;
  const width = maxX - minX;
  const height = maxY - minY;
  if (width < 1e-6 || height < 1e-6) return [];

  const cellW = width / resolution;
  const cellH = height / resolution;

  // Collect all segments from all strokes
  const segments = [];
  for (const stroke of strokes) {
    const pts = getPoints(stroke);
    for (let i = 0; i < pts.length - 1; i++) {
      segments.push({
        x1: pts[i].x, y1: pts[i].y,
        x2: pts[i + 1].x, y2: pts[i + 1].y,
      });
    }
  }

  if (segments.length === 0) return [];

  /**
   * Ray-cast from point (px, py) in +x direction.
   * Count intersections with all segments (even-odd rule).
   */
  function isInside(px, py) {
    let crossings = 0;
    for (const seg of segments) {
      const { x1, y1, x2, y2 } = seg;
      // Check if ray at py intersects segment (y1,y2)
      if ((y1 <= py && y2 > py) || (y2 <= py && y1 > py)) {
        // Compute x-coordinate of intersection
        const t = (py - y1) / (y2 - y1);
        const ix = x1 + t * (x2 - x1);
        if (ix > px) {
          crossings++;
        }
      }
    }
    return (crossings & 1) === 1;
  }

  // Build inside/outside grid
  const insideGrid = new Uint8Array(resolution * resolution);
  for (let r = 0; r < resolution; r++) {
    for (let c = 0; c < resolution; c++) {
      const px = minX + (c + 0.5) * cellW;
      const py = minY + (r + 0.5) * cellH;
      insideGrid[r * resolution + c] = isInside(px, py) ? 1 : 0;
    }
  }

  // Flood-fill to cluster adjacent inside points into regions
  const visited = new Uint8Array(resolution * resolution);
  const regions = [];

  function floodFill(startR, startC) {
    const cells = [];
    const stack = [{ r: startR, c: startC }];
    visited[startR * resolution + startC] = 1;

    while (stack.length > 0) {
      const { r, c } = stack.pop();
      cells.push({ r, c });

      // 4-connected neighbors
      const neighbors = [
        { r: r - 1, c },
        { r: r + 1, c },
        { r, c: c - 1 },
        { r, c: c + 1 },
      ];
      for (const n of neighbors) {
        if (n.r < 0 || n.r >= resolution || n.c < 0 || n.c >= resolution) continue;
        const idx = n.r * resolution + n.c;
        if (visited[idx] || !insideGrid[idx]) continue;
        visited[idx] = 1;
        stack.push(n);
      }
    }

    return cells;
  }

  for (let r = 0; r < resolution; r++) {
    for (let c = 0; c < resolution; c++) {
      const idx = r * resolution + c;
      if (insideGrid[idx] && !visited[idx]) {
        const cells = floodFill(r, c);
        if (cells.length >= 2) {
          regions.push(cells);
        }
      }
    }
  }

  // Convert cell clusters to region descriptors
  return regions.map(cells => {
    let cx = 0, cy = 0;
    let rMin = Infinity, rMax = -Infinity, cMin = Infinity, cMax = -Infinity;

    for (const { r, c } of cells) {
      const wx = minX + (c + 0.5) * cellW;
      const wy = minY + (r + 0.5) * cellH;
      cx += wx;
      cy += wy;
      if (r < rMin) rMin = r;
      if (r > rMax) rMax = r;
      if (c < cMin) cMin = c;
      if (c > cMax) cMax = c;
    }

    cx /= cells.length;
    cy /= cells.length;

    // Approximate area: cell count * cell area
    const area = cells.length * cellW * cellH;

    // Build boundary: cells that have at least one non-inside neighbor
    const boundary = [];
    for (const { r, c } of cells) {
      const neighbors = [
        { r: r - 1, c },
        { r: r + 1, c },
        { r, c: c - 1 },
        { r, c: c + 1 },
      ];
      let isBoundary = false;
      for (const n of neighbors) {
        if (n.r < 0 || n.r >= resolution || n.c < 0 || n.c >= resolution) {
          isBoundary = true;
          break;
        }
        if (!insideGrid[n.r * resolution + n.c]) {
          isBoundary = true;
          break;
        }
      }
      if (isBoundary) {
        boundary.push({
          x: minX + (c + 0.5) * cellW,
          y: minY + (r + 0.5) * cellH,
        });
      }
    }

    return {
      centroid: { x: cx, y: cy },
      area,
      boundary,
      pointCount: cells.length,
    };
  });
}

// ---------------------------------------------------------------------------
// 4. buildAttractors — Attractor points from exterior endpoints
// ---------------------------------------------------------------------------

/**
 * Build attractor points from exterior endpoints with growth directions.
 *
 * Calls `classifyEndpoints` internally, sorts exterior points by openness
 * (most empty sectors first), and returns the top N as attractor points with
 * a strength proportional to how much open space surrounds the endpoint.
 *
 * @param {Array} strokes - Array of stroke objects with .path or .points
 * @param {number} [maxAttractors=20] - Maximum number of attractors to return
 * @returns {Array<{x: number, y: number, direction: {x, y}, strength: number}>}
 */
export function buildAttractors(strokes, maxAttractors = 20) {
  if (!strokes || strokes.length === 0) return [];

  const { exterior } = classifyEndpoints(strokes);
  if (exterior.length === 0) return [];

  // Sort by number of empty sectors (most open space first)
  const sorted = exterior.slice().sort((a, b) => b.emptySectors - a.emptySectors);

  // Take top N
  const top = sorted.slice(0, maxAttractors);

  // Compute strength: normalize emptySectors (3..8) to (0..1)
  // 3 empty sectors = minimum exterior threshold, 8 = completely surrounded by open space
  const minEmpty = 3;
  const maxEmpty = 8;

  return top.map(ep => ({
    x: ep.x,
    y: ep.y,
    direction: { x: ep.growthDir.x, y: ep.growthDir.y },
    strength: (ep.emptySectors - minEmpty) / (maxEmpty - minEmpty),
  }));
}

// ---------------------------------------------------------------------------
// 5. pointInPolygon — Ray-casting even-odd rule
// ---------------------------------------------------------------------------

/**
 * Test whether a point (px, py) lies inside a polygon using the even-odd ray-casting rule.
 *
 * @param {number} px - Test point X
 * @param {number} py - Test point Y
 * @param {Array<{x: number, y: number}>} polygon - Polygon vertices (closed or open — auto-closes)
 * @returns {boolean}
 */
export function pointInPolygon(px, py, polygon) {
  if (!polygon || polygon.length < 3) return false;

  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i].x, yi = polygon[i].y;
    const xj = polygon[j].x, yj = polygon[j].y;

    if (((yi > py) !== (yj > py)) && (px < (xj - xi) * (py - yi) / (yj - yi) + xi)) {
      inside = !inside;
    }
  }
  return inside;
}

// ---------------------------------------------------------------------------
// 6. clipLineToPolygon — Walk a line and return inside sub-segments
// ---------------------------------------------------------------------------

/**
 * Clip a line segment to a polygon by walking along it and tracking inside/outside transitions.
 *
 * Returns an array of sub-segments (pairs of points) that lie inside the polygon.
 *
 * @param {{x: number, y: number}} p0 - Line start
 * @param {{x: number, y: number}} p1 - Line end
 * @param {Array<{x: number, y: number}>} polygon - Polygon vertices
 * @param {number} [stepSize=3] - Walk step size
 * @returns {Array<[{x: number, y: number}, {x: number, y: number}]>}
 */
export function clipLineToPolygon(p0, p1, polygon, stepSize = 3) {
  if (!polygon || polygon.length < 3) return [];

  const dx = p1.x - p0.x;
  const dy = p1.y - p0.y;
  const lineLen = Math.sqrt(dx * dx + dy * dy);
  if (lineLen < 1e-6) return [];

  const steps = Math.max(2, Math.ceil(lineLen / stepSize));
  const segments = [];
  let segStart = null;

  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const px = p0.x + dx * t;
    const py = p0.y + dy * t;
    const inside = pointInPolygon(px, py, polygon);

    if (inside) {
      if (!segStart) segStart = { x: px, y: py };
    } else {
      if (segStart) {
        // Previous point was the last inside point
        const prevT = (i - 1) / steps;
        const segEnd = { x: p0.x + dx * prevT, y: p0.y + dy * prevT };
        const segLen = Math.sqrt((segEnd.x - segStart.x) ** 2 + (segEnd.y - segStart.y) ** 2);
        if (segLen > 1) {
          segments.push([segStart, segEnd]);
        }
        segStart = null;
      }
    }
  }

  // Trailing segment
  if (segStart) {
    const segLen = Math.sqrt((p1.x - segStart.x) ** 2 + (p1.y - segStart.y) ** 2);
    if (segLen > 1) {
      segments.push([segStart, { x: p1.x, y: p1.y }]);
    }
  }

  return segments;
}

// ---------------------------------------------------------------------------
// 7. buildSDF — Signed Distance Field
// ---------------------------------------------------------------------------

/**
 * Build a signed distance field from strokes over a rectangular region.
 *
 * Returns an object with `query(x,y)` (negative inside, positive outside)
 * and `gradient(x,y)` (normalized direction vector pointing away from boundary).
 *
 * @param {Array} strokes - Array of stroke objects with .path or .points
 * @param {{minX: number, minY: number, maxX: number, maxY: number}} bounds - Region
 * @param {number} [resolution=60] - Grid resolution (cells per axis)
 * @returns {{ query: (x: number, y: number) => number, gradient: (x: number, y: number) => {x: number, y: number}, resolution: number }}
 */
export function buildSDF(strokes, bounds, resolution = 60) {
  const { minX, minY, maxX, maxY } = bounds;
  const width = maxX - minX;
  const height = maxY - minY;

  if (width < 1e-6 || height < 1e-6 || !strokes || strokes.length === 0) {
    return {
      query: () => Infinity,
      gradient: () => ({ x: 0, y: 0 }),
      resolution,
    };
  }

  const cellW = width / resolution;
  const cellH = height / resolution;

  // Collect all segments
  const segments = [];
  for (const stroke of strokes) {
    const pts = getPoints(stroke);
    for (let i = 0; i < pts.length - 1; i++) {
      segments.push({ ax: pts[i].x, ay: pts[i].y, bx: pts[i + 1].x, by: pts[i + 1].y });
    }
  }

  if (segments.length === 0) {
    return {
      query: () => Infinity,
      gradient: () => ({ x: 0, y: 0 }),
      resolution,
    };
  }

  // Build distance grid and sign grid
  const distGrid = new Float64Array(resolution * resolution);
  const signGrid = new Int8Array(resolution * resolution);

  for (let r = 0; r < resolution; r++) {
    for (let c = 0; c < resolution; c++) {
      const px = minX + (c + 0.5) * cellW;
      const py = minY + (r + 0.5) * cellH;

      // Min distance to any segment
      let minDist = Infinity;
      for (const seg of segments) {
        const d = pointToSegmentDist(px, py, seg.ax, seg.ay, seg.bx, seg.by);
        if (d < minDist) minDist = d;
      }
      distGrid[r * resolution + c] = minDist;

      // Sign via ray-casting (even-odd rule — +x direction)
      let crossings = 0;
      for (const seg of segments) {
        const { ax: x1, ay: y1, bx: x2, by: y2 } = seg;
        if ((y1 <= py && y2 > py) || (y2 <= py && y1 > py)) {
          const t = (py - y1) / (y2 - y1);
          const ix = x1 + t * (x2 - x1);
          if (ix > px) crossings++;
        }
      }
      // Odd crossings = inside (negative), even = outside (positive)
      signGrid[r * resolution + c] = (crossings & 1) === 1 ? -1 : 1;
    }
  }

  /** Bilinear interpolation of signed distance at world coordinates. */
  function query(x, y) {
    const fc = (x - minX) / cellW - 0.5;
    const fr = (y - minY) / cellH - 0.5;
    const c0 = Math.floor(fc);
    const r0 = Math.floor(fr);
    const c1 = c0 + 1;
    const r1 = r0 + 1;
    const tc = fc - c0;
    const tr = fr - r0;

    function sample(r, c) {
      if (r < 0 || r >= resolution || c < 0 || c >= resolution) return Infinity;
      const idx = r * resolution + c;
      return distGrid[idx] * signGrid[idx];
    }

    const v00 = sample(r0, c0);
    const v10 = sample(r1, c0);
    const v01 = sample(r0, c1);
    const v11 = sample(r1, c1);

    if (!isFinite(v00) || !isFinite(v10) || !isFinite(v01) || !isFinite(v11)) {
      // Fallback: nearest cell
      const nr = Math.max(0, Math.min(resolution - 1, Math.round(fr + 0.5)));
      const nc = Math.max(0, Math.min(resolution - 1, Math.round(fc + 0.5)));
      const idx = nr * resolution + nc;
      return distGrid[idx] * signGrid[idx];
    }

    return (1 - tr) * ((1 - tc) * v00 + tc * v01) + tr * ((1 - tc) * v10 + tc * v11);
  }

  /** Gradient via central differences — normalized direction vector. */
  function gradient(x, y) {
    const eps = cellW * 0.5;
    const dfdx = (query(x + eps, y) - query(x - eps, y)) / (2 * eps);
    const dfdy = (query(x, y + eps) - query(x, y - eps)) / (2 * eps);
    const len = Math.sqrt(dfdx * dfdx + dfdy * dfdy);
    if (len < 1e-10) return { x: 0, y: 0 };
    return { x: dfdx / len, y: dfdy / len };
  }

  return { query, gradient, resolution };
}

// ---------------------------------------------------------------------------
// 8. detectClosedShapes — Unified closed shape detection from topology block
// ---------------------------------------------------------------------------

/**
 * Consume a relay nearby result's topology block and return unified closed shapes.
 *
 * Combines single-stroke closed shapes (from stroke topology.isClosed) with
 * multi-stroke regions (from topology.multiStrokeRegions) into a uniform array.
 *
 * @param {object} nearbyData - Full nearby result from relay API (with .strokes and .topology)
 * @returns {Array<{type: 'single'|'multi', strokeIds: string[], polygon: Array<{x,y}>, centroid: {x,y}, area: number}>}
 */
export function detectClosedShapes(nearbyData) {
  const shapes = [];

  if (!nearbyData) return shapes;

  // Single-stroke closed shapes
  if (nearbyData.strokes) {
    for (const s of nearbyData.strokes) {
      const topo = s.topology;
      if (topo && topo.isClosed) {
        const polygon = (s.path || s.points || []).map(p => ({ x: p.x, y: p.y }));
        if (polygon.length >= 3) {
          shapes.push({
            type: 'single',
            strokeIds: [s.id],
            polygon,
            centroid: topo.centroid || { x: 0, y: 0 },
            area: topo.area || 0,
          });
        }
      }
    }
  }

  // Multi-stroke regions from topology block
  if (nearbyData.topology && nearbyData.topology.multiStrokeRegions) {
    for (const region of nearbyData.topology.multiStrokeRegions) {
      if (region.vertices && region.vertices.length >= 3) {
        shapes.push({
          type: 'multi',
          strokeIds: region.strokeIds || [],
          polygon: region.vertices.map(v => ({ x: v.x, y: v.y })),
          centroid: region.centroid || { x: 0, y: 0 },
          area: region.area || 0,
        });
      }
    }
  }

  return shapes;
}

// ---------------------------------------------------------------------------
// 9. shoelaceArea — Polygon area via the shoelace formula
// ---------------------------------------------------------------------------

/**
 * Compute the area of a polygon using the shoelace formula.
 *
 * @param {Array<{x: number, y: number}>} points - Polygon vertices (open or closed)
 * @returns {number} Unsigned area
 */
export function shoelaceArea(points) {
  if (!points || points.length < 3) return 0;
  let area = 0;
  for (let i = 0; i < points.length; i++) {
    const j = (i + 1) % points.length;
    area += points[i].x * points[j].y;
    area -= points[j].x * points[i].y;
  }
  return Math.abs(area) / 2;
}

// ---------------------------------------------------------------------------
// 10. extractPlanarFaces — PSLG face extraction from stroke intersections
// ---------------------------------------------------------------------------

/**
 * Extract enclosed faces from a planar subdivision of stroke paths.
 *
 * Treats all strokes as edges of a planar graph, finds intersection points,
 * splits edges there, then walks the graph to extract enclosed faces as
 * ordered polygon boundaries.
 *
 * @param {Array} strokes - Array of stroke objects with .path or .points and .id
 * @param {{minX: number, minY: number, maxX: number, maxY: number}} bounds - Filter region
 * @returns {Array<{type: 'face', strokeIds: string[], polygon: Array<{x,y}>, centroid: {x,y}, area: number}>}
 */
export function extractPlanarFaces(strokes, bounds) {
  if (!strokes || strokes.length === 0) return [];

  const MERGE_EPS = 0.5;
  const PARAM_EPS = 1e-8;
  const MIN_FACE_AREA = 100;

  // --- Step 1: Collect segments from strokes ---
  const segments = [];
  for (const stroke of strokes) {
    const pts = getPoints(stroke);
    if (pts.length < 2) continue;
    const strokeId = stroke.id || '';
    for (let i = 0; i < pts.length - 1; i++) {
      segments.push({
        ax: pts[i].x, ay: pts[i].y,
        bx: pts[i + 1].x, by: pts[i + 1].y,
        strokeId,
        strokeIdx: strokes.indexOf(stroke),
        segIdx: i,
      });
    }
    // For nearly-closed strokes, add synthetic closing segment
    const first = pts[0];
    const last = pts[pts.length - 1];
    const closeDist = Math.sqrt((first.x - last.x) ** 2 + (first.y - last.y) ** 2);
    if (closeDist > MERGE_EPS && closeDist < 20) {
      segments.push({
        ax: last.x, ay: last.y,
        bx: first.x, by: first.y,
        strokeId,
        strokeIdx: strokes.indexOf(stroke),
        segIdx: pts.length - 1,
      });
    }
  }

  if (segments.length < 2) return [];

  // --- Step 2: Find all intersections (brute force) ---
  // intersectionMap[segmentIndex] = [{t, x, y}, ...]
  const intersectionMap = new Map();

  for (let i = 0; i < segments.length; i++) {
    const a = segments[i];
    for (let j = i + 1; j < segments.length; j++) {
      const b = segments[j];

      // Skip adjacent segments from same stroke
      if (a.strokeIdx === b.strokeIdx && Math.abs(a.segIdx - b.segIdx) <= 1) continue;

      const dxa = a.bx - a.ax, dya = a.by - a.ay;
      const dxb = b.bx - b.ax, dyb = b.by - b.ay;
      const denom = dxa * dyb - dya * dxb;

      // Skip parallel/collinear segments
      if (Math.abs(denom) < 1e-10) continue;

      const offx = b.ax - a.ax;
      const offy = b.ay - a.ay;
      const t = (offx * dyb - offy * dxb) / denom;
      const u = (offx * dya - offy * dxa) / denom;

      // Both parameters must be in [0, 1]
      if (t < -PARAM_EPS || t > 1 + PARAM_EPS || u < -PARAM_EPS || u > 1 + PARAM_EPS) continue;

      const tc = Math.max(0, Math.min(1, t));
      const uc = Math.max(0, Math.min(1, u));
      const ix = a.ax + tc * dxa;
      const iy = a.ay + tc * dya;

      if (!intersectionMap.has(i)) intersectionMap.set(i, []);
      if (!intersectionMap.has(j)) intersectionMap.set(j, []);
      intersectionMap.get(i).push({ t: tc, x: ix, y: iy });
      intersectionMap.get(j).push({ t: uc, x: ix, y: iy });
    }
  }

  // If no intersections found, no enclosed faces possible
  if (intersectionMap.size === 0) return [];

  // --- Step 3: Build vertex list with epsilon merge ---
  const vertices = []; // [{x, y, id}]
  const gridCellSize = MERGE_EPS;
  const vertexGrid = new Map(); // "gx,gy" -> [vertex indices]

  function mergeOrAddVertex(x, y) {
    const gx = Math.floor(x / gridCellSize);
    const gy = Math.floor(y / gridCellSize);

    // Check 3x3 neighborhood
    for (let dx = -1; dx <= 1; dx++) {
      for (let dy = -1; dy <= 1; dy++) {
        const key = `${gx + dx},${gy + dy}`;
        const bucket = vertexGrid.get(key);
        if (!bucket) continue;
        for (const vi of bucket) {
          const v = vertices[vi];
          if (Math.abs(v.x - x) <= MERGE_EPS && Math.abs(v.y - y) <= MERGE_EPS) {
            return vi;
          }
        }
      }
    }

    // No merge found — add new vertex
    const id = vertices.length;
    vertices.push({ x, y, id });
    const key = `${gx},${gy}`;
    if (!vertexGrid.has(key)) vertexGrid.set(key, []);
    vertexGrid.get(key).push(id);
    return id;
  }

  // --- Step 4: Split segments at intersections, build edges ---
  // edges: [{from, to, strokeId}] — directed
  const edges = [];

  for (let si = 0; si < segments.length; si++) {
    const seg = segments[si];
    const splits = intersectionMap.get(si) || [];

    // Add segment endpoints
    splits.push({ t: 0, x: seg.ax, y: seg.ay });
    splits.push({ t: 1, x: seg.bx, y: seg.by });

    // Sort by parameter t
    splits.sort((a, b) => a.t - b.t);

    // Deduplicate very close splits
    const deduped = [splits[0]];
    for (let k = 1; k < splits.length; k++) {
      if (splits[k].t - deduped[deduped.length - 1].t > PARAM_EPS * 10) {
        deduped.push(splits[k]);
      }
    }

    // Emit sub-edges between consecutive split points
    for (let k = 0; k < deduped.length - 1; k++) {
      const fromId = mergeOrAddVertex(deduped[k].x, deduped[k].y);
      const toId = mergeOrAddVertex(deduped[k + 1].x, deduped[k + 1].y);
      if (fromId === toId) continue;
      edges.push({ from: fromId, to: toId, strokeId: seg.strokeId });
    }
  }

  if (edges.length < 3) return [];

  // --- Step 5: Build adjacency with angular sorting ---
  // adjacency[vertexId] = [{target, angle, edgeIdx}], sorted by angle ascending
  const adjacency = new Map();

  for (let ei = 0; ei < edges.length; ei++) {
    const e = edges[ei];
    // Each undirected edge → two directed half-edges
    addHalfEdge(e.from, e.to, ei);
    addHalfEdge(e.to, e.from, ei);
  }

  function addHalfEdge(from, to, edgeIdx) {
    if (!adjacency.has(from)) adjacency.set(from, []);
    const vFrom = vertices[from];
    const vTo = vertices[to];
    const angle = Math.atan2(vTo.y - vFrom.y, vTo.x - vFrom.x);
    adjacency.get(from).push({ target: to, angle, edgeIdx });
  }

  // Sort each vertex's adjacency list by angle ascending
  for (const [, list] of adjacency) {
    list.sort((a, b) => a.angle - b.angle);
  }

  // --- Step 6: Extract faces via wedge traversal ---
  const visitedHalfEdges = new Set(); // "from-to"

  function halfEdgeKey(from, to) {
    return `${from}-${to}`;
  }

  const faces = []; // [{polygon: [{x,y}], edgeIndices: []}]

  for (let ei = 0; ei < edges.length; ei++) {
    const e = edges[ei];
    // Try both directions of each edge
    for (const [startFrom, startTo] of [[e.from, e.to], [e.to, e.from]]) {
      const key = halfEdgeKey(startFrom, startTo);
      if (visitedHalfEdges.has(key)) continue;

      const faceVertices = [];
      const faceEdgeIndices = [];
      let curFrom = startFrom;
      let curTo = startTo;
      let steps = 0;
      const MAX_STEPS = 10000;
      let valid = true;

      while (steps < MAX_STEPS) {
        const heKey = halfEdgeKey(curFrom, curTo);
        if (visitedHalfEdges.has(heKey) && steps > 0) {
          // If we've returned to our starting half-edge, face is complete
          if (curFrom === startFrom && curTo === startTo) break;
          valid = false;
          break;
        }
        visitedHalfEdges.add(heKey);
        faceVertices.push(vertices[curFrom]);

        // Find which edge this corresponds to
        const adj = adjacency.get(curFrom);
        if (adj) {
          const he = adj.find(h => h.target === curTo);
          if (he) faceEdgeIndices.push(he.edgeIdx);
        }

        // At vertex curTo, find the reverse half-edge (curTo → curFrom)
        const adjAtTo = adjacency.get(curTo);
        if (!adjAtTo || adjAtTo.length === 0) { valid = false; break; }

        // Find index of reverse direction (curTo → curFrom) in curTo's adjacency
        const reverseAngle = Math.atan2(
          vertices[curFrom].y - vertices[curTo].y,
          vertices[curFrom].x - vertices[curTo].x
        );

        // Find the entry closest to reverseAngle
        let bestIdx = -1;
        let bestDiff = Infinity;
        for (let k = 0; k < adjAtTo.length; k++) {
          let diff = adjAtTo[k].angle - reverseAngle;
          // Normalize to [-PI, PI]
          while (diff > Math.PI) diff -= 2 * Math.PI;
          while (diff < -Math.PI) diff += 2 * Math.PI;
          const absDiff = Math.abs(diff);
          if (absDiff < bestDiff) { bestDiff = absDiff; bestIdx = k; }
        }

        if (bestIdx === -1) { valid = false; break; }

        // Take the PREVIOUS entry in CCW-sorted order (wrap around)
        const prevIdx = (bestIdx - 1 + adjAtTo.length) % adjAtTo.length;
        const nextHE = adjAtTo[prevIdx];

        curFrom = curTo;
        curTo = nextHE.target;
        steps++;
      }

      if (!valid || faceVertices.length < 3 || steps >= MAX_STEPS) continue;

      // Check that we actually closed the loop
      if (curFrom !== startFrom || curTo !== startTo) continue;

      faces.push({ polygon: faceVertices, edgeIndices: faceEdgeIndices });
    }
  }

  if (faces.length === 0) return [];

  // --- Step 7: Filter and classify faces ---
  const results = [];

  // Compute signed area for each face to find and remove the outer (unbounded) face
  let maxAbsArea = 0;
  let outerFaceIdx = -1;

  for (let fi = 0; fi < faces.length; fi++) {
    const poly = faces[fi].polygon;
    let signedArea = 0;
    for (let i = 0; i < poly.length; i++) {
      const j = (i + 1) % poly.length;
      signedArea += poly[i].x * poly[j].y;
      signedArea -= poly[j].x * poly[i].y;
    }
    faces[fi].signedArea = signedArea / 2;
    faces[fi].absArea = Math.abs(signedArea / 2);

    if (faces[fi].absArea > maxAbsArea) {
      maxAbsArea = faces[fi].absArea;
      outerFaceIdx = fi;
    }
  }

  for (let fi = 0; fi < faces.length; fi++) {
    if (fi === outerFaceIdx) continue; // Skip unbounded outer face

    const face = faces[fi];
    if (face.absArea < MIN_FACE_AREA) continue; // Skip tiny noise

    // Compute centroid
    const poly = face.polygon;
    let cx = 0, cy = 0;
    for (const v of poly) { cx += v.x; cy += v.y; }
    cx /= poly.length;
    cy /= poly.length;

    // Filter faces whose centroid is outside bounds
    if (bounds && (cx < bounds.minX || cx > bounds.maxX || cy < bounds.minY || cy > bounds.maxY)) continue;

    // Collect strokeIds from edges traversed
    const strokeIdSet = new Set();
    for (const eidx of face.edgeIndices) {
      if (eidx >= 0 && eidx < edges.length) {
        strokeIdSet.add(edges[eidx].strokeId);
      }
    }

    results.push({
      type: 'face',
      strokeIds: Array.from(strokeIdSet).filter(Boolean),
      polygon: poly.map(v => ({ x: v.x, y: v.y })),
      centroid: { x: cx, y: cy },
      area: face.absArea,
    });
  }

  return results;
}

// ---------------------------------------------------------------------------
// Default export — all functions bundled for convenience
// ---------------------------------------------------------------------------

export default {
  classifyEndpoints,
  buildDensityMap,
  detectEnclosedRegions,
  buildAttractors,
  pointInPolygon,
  clipLineToPolygon,
  buildSDF,
  detectClosedShapes,
  shoelaceArea,
  extractPlanarFaces,
};
