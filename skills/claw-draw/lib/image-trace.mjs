/**
 * Image-to-strokes rendering engine.
 *
 * Pure math — no Node builtins, no fetch, no sharp, no dynamic imports.
 * Receives plain numeric arrays (pixels, gradients), returns stroke objects.
 *
 * Modes:
 *   pointillist — Seurat-style dots, color sampled from image
 *   sketch      — Sobel edge contours + directional hatching
 *   vangogh     — Dense swirling brushstrokes following flow field
 *   slimemold   — Physarum-style agents guided by Sobel edge attractors
 */

import { makeStroke, splitIntoStrokes, noise2d, rgbToHex, clamp } from '../primitives/helpers.mjs';

// ---------------------------------------------------------------------------
// Pixel-space ↔ canvas-space helpers
// ---------------------------------------------------------------------------

/** Convert pixel coordinate to canvas coordinate. */
function pixToCanvas(px, py, pd) {
  return {
    x: pd.cx - pd.canvasWidth / 2 + (px / pd.width) * pd.canvasWidth,
    y: pd.cy - pd.canvasHeight / 2 + (py / pd.height) * pd.canvasHeight,
  };
}

/** Sample RGBA at pixel coordinate (clamped). */
function sampleRgb(rgba, x, y, w, h) {
  const sx = clamp(Math.round(x), 0, w - 1);
  const sy = clamp(Math.round(y), 0, h - 1);
  const i = (sy * w + sx) * 4;
  return [rgba[i], rgba[i + 1], rgba[i + 2]];
}

/** Sample grayscale value at pixel coordinate (clamped). Returns 0–255. */
function sampleGray(gray, x, y, w, h) {
  return gray[clamp(Math.round(y), 0, h - 1) * w + clamp(Math.round(x), 0, w - 1)];
}

// ---------------------------------------------------------------------------
// Image analysis — Sobel edge detection
// ---------------------------------------------------------------------------

/**
 * Compute Sobel gradient magnitude and direction for a grayscale image.
 * @param {Uint8Array} gray  — Grayscale pixel values
 * @param {number} width
 * @param {number} height
 * @returns {{ magnitude: Float32Array, direction: Float32Array }}
 */
export function computeSobel(gray, width, height) {
  const magnitude = new Float32Array(width * height);
  const direction = new Float32Array(width * height);

  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      const tl = gray[(y - 1) * width + x - 1];
      const tc = gray[(y - 1) * width + x];
      const tr = gray[(y - 1) * width + x + 1];
      const ml = gray[y * width + x - 1];
      const mr = gray[y * width + x + 1];
      const bl = gray[(y + 1) * width + x - 1];
      const bc = gray[(y + 1) * width + x];
      const br = gray[(y + 1) * width + x + 1];

      const gx = -tl + tr - 2 * ml + 2 * mr - bl + br;
      const gy = -tl - 2 * tc - tr + bl + 2 * bc + br;

      const idx = y * width + x;
      magnitude[idx] = Math.sqrt(gx * gx + gy * gy);
      direction[idx] = Math.atan2(gy, gx);
    }
  }

  return { magnitude, direction };
}

/**
 * Trace edge pixels into polyline chains.
 * Applies non-maximum suppression, then greedy chain-following.
 *
 * @param {Float32Array} magnitude
 * @param {Float32Array} direction
 * @param {number} width
 * @param {number} height
 * @param {number} threshold — Minimum magnitude to consider an edge
 * @returns {Array<Array<{x:number, y:number}>>} — Array of point chains
 */
export function traceEdges(magnitude, direction, width, height, threshold) {
  // Non-maximum suppression
  const nms = new Uint8Array(width * height);
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      const idx = y * width + x;
      const m = magnitude[idx];
      if (m < threshold) continue;

      const a = direction[idx];
      const dx = Math.round(Math.cos(a));
      const dy = Math.round(Math.sin(a));
      const n1x = x + dx, n1y = y + dy;
      const n2x = x - dx, n2y = y - dy;

      const m1 = (n1x >= 0 && n1x < width && n1y >= 0 && n1y < height)
        ? magnitude[n1y * width + n1x] : 0;
      const m2 = (n2x >= 0 && n2x < width && n2y >= 0 && n2y < height)
        ? magnitude[n2y * width + n2x] : 0;

      if (m >= m1 && m >= m2) nms[idx] = 1;
    }
  }

  // Greedy chain-following with 8-connectivity
  const visited = new Uint8Array(width * height);
  const chains = [];
  const dirs8 = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]];

  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      const idx = y * width + x;
      if (!nms[idx] || visited[idx]) continue;

      const chain = [];
      let cx = x, cy = y;
      visited[idx] = 1;
      chain.push({ x: cx, y: cy });

      let moving = true;
      while (moving) {
        moving = false;
        for (const [ddx, ddy] of dirs8) {
          const nx = cx + ddx, ny = cy + ddy;
          if (nx < 1 || nx >= width - 1 || ny < 1 || ny >= height - 1) continue;
          const ni = ny * width + nx;
          if (nms[ni] && !visited[ni]) {
            visited[ni] = 1;
            chain.push({ x: nx, y: ny });
            cx = nx;
            cy = ny;
            moving = true;
            break;
          }
        }
      }

      if (chain.length >= 4) chains.push(chain);
    }
  }

  return chains;
}

// ---------------------------------------------------------------------------
// Mode: Pointillist — Seurat-style dots
// ---------------------------------------------------------------------------

/**
 * Grid-sample pixels with jitter. Each pixel → small 2-point dot stroke.
 * Color = pixel color, dot size ∝ inverse brightness (darker = larger).
 */
export function renderPointillist(pixelData, options = {}) {
  const { rgba, gray, width, height } = pixelData;
  const density = options.density || 1.0;
  const spacing = Math.max(1, Math.round(4 / density));
  const strokes = [];

  for (let py = 0; py < height; py += spacing) {
    for (let px = 0; px < width; px += spacing) {
      const jx = (Math.random() - 0.5) * spacing * 0.6;
      const jy = (Math.random() - 0.5) * spacing * 0.6;
      const sx = clamp(Math.round(px + jx), 0, width - 1);
      const sy = clamp(Math.round(py + jy), 0, height - 1);

      // Skip transparent pixels
      const ai = (sy * width + sx) * 4 + 3;
      if (rgba[ai] < 128) continue;

      const [r, g, b] = sampleRgb(rgba, sx, sy, width, height);
      const brightness = sampleGray(gray, sx, sy, width, height) / 255;
      const dotSize = clamp(3 + (1 - brightness) * 12, 3, 15);

      const c = pixToCanvas(sx, sy, pixelData);
      const dr = dotSize * 0.25;
      strokes.push(makeStroke(
        [{ x: c.x - dr, y: c.y }, { x: c.x + dr, y: c.y }],
        rgbToHex(r, g, b),
        dotSize,
        clamp(0.7 + brightness * 0.25, 0.7, 0.95),
      ));
    }
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// Mode: Sketch — edge contours + diagonal hatching
// ---------------------------------------------------------------------------

/**
 * Hatch-line helper. Walks parallel lines at a given angle across the image,
 * creating stroke segments where brightness is below a threshold.
 */
function generateHatchStrokes(gray, width, height, pixelData, angle, spacing, brightnessThreshold, color, brushSize, opacity) {
  const cosA = Math.cos(angle), sinA = Math.sin(angle);
  const cosP = -sinA, sinP = cosA; // perpendicular direction

  // Project image corners onto perpendicular axis
  const corners = [[0, 0], [width, 0], [0, height], [width, height]];
  let minProj = Infinity, maxProj = -Infinity;
  for (const [x, y] of corners) {
    const proj = x * cosP + y * sinP;
    if (proj < minProj) minProj = proj;
    if (proj > maxProj) maxProj = proj;
  }

  const strokes = [];

  for (let d = minProj; d <= maxProj; d += spacing) {
    const ox = d * cosP;
    const oy = d * sinP;

    // Find t-range where line stays within image bounds
    let tMin = -1e6, tMax = 1e6;
    if (Math.abs(cosA) > 1e-10) {
      const t1 = -ox / cosA, t2 = (width - 1 - ox) / cosA;
      tMin = Math.max(tMin, Math.min(t1, t2));
      tMax = Math.min(tMax, Math.max(t1, t2));
    } else if (ox < 0 || ox >= width) continue;
    if (Math.abs(sinA) > 1e-10) {
      const t1 = -oy / sinA, t2 = (height - 1 - oy) / sinA;
      tMin = Math.max(tMin, Math.min(t1, t2));
      tMax = Math.min(tMax, Math.max(t1, t2));
    } else if (oy < 0 || oy >= height) continue;
    if (tMin >= tMax) continue;

    // Walk line, create segments where dark enough
    let seg = null;
    for (let t = tMin; t <= tMax; t += 1.0) {
      const px = ox + t * cosA;
      const py = oy + t * sinA;
      const brightness = sampleGray(gray, px, py, width, height) / 255;

      if (brightness < brightnessThreshold) {
        if (!seg) seg = [];
        seg.push(pixToCanvas(px, py, pixelData));
      } else {
        if (seg && seg.length >= 3) {
          strokes.push(makeStroke(seg, color, brushSize, opacity, 'flat'));
        }
        seg = null;
      }
    }
    if (seg && seg.length >= 3) {
      strokes.push(makeStroke(seg, color, brushSize, opacity, 'flat'));
    }
  }

  return strokes;
}

/**
 * Bold edge contours + directional hatching with cross-hatch in dark areas.
 */
export function renderSketch(pixelData, options = {}) {
  const { rgba, gray, width, height } = pixelData;
  const density = options.density || 1.0;
  const strokes = [];

  const sobel = computeSobel(gray, width, height);

  // --- Edge contours ---
  let maxMag = 0;
  for (let i = 0; i < sobel.magnitude.length; i++) {
    if (sobel.magnitude[i] > maxMag) maxMag = sobel.magnitude[i];
  }
  const threshold = Math.max(maxMag * 0.15, 1);
  const chains = traceEdges(sobel.magnitude, sobel.direction, width, height, threshold);

  for (const chain of chains) {
    // Subsample every 2nd point for smoother strokes
    const pts = [];
    for (let i = 0; i < chain.length; i += 2) {
      pts.push(pixToCanvas(chain[i].x, chain[i].y, pixelData));
    }
    // Always include last point
    const last = chain[chain.length - 1];
    const lastPt = pixToCanvas(last.x, last.y, pixelData);
    if (pts.length > 0) {
      const end = pts[pts.length - 1];
      if (Math.abs(end.x - lastPt.x) > 0.5 || Math.abs(end.y - lastPt.y) > 0.5) {
        pts.push(lastPt);
      }
    }
    if (pts.length < 2) continue;
    strokes.push(...splitIntoStrokes(pts, '#1a1a1a', 4, 0.9, 'default'));
  }

  // --- Primary hatching at 135° (NW → SE) ---
  const hatchSpacing = Math.max(1.5, 3 / density);
  strokes.push(...generateHatchStrokes(
    gray, width, height, pixelData,
    Math.PI * 0.75, hatchSpacing, 0.72,
    '#2a2a2a', 2, 0.7,
  ));

  // --- Cross-hatch at 45° for very dark areas ---
  const crossSpacing = hatchSpacing * 1.5;
  strokes.push(...generateHatchStrokes(
    gray, width, height, pixelData,
    Math.PI * 0.25, crossSpacing, 0.4,
    '#333333', 2, 0.5,
  ));

  return strokes;
}

// ---------------------------------------------------------------------------
// Mode: Van Gogh — dense swirling brushstrokes
// ---------------------------------------------------------------------------

/**
 * Compute gradient flow field, seed particles on a grid with jitter,
 * trace short curved paths following contour direction + Perlin noise swirl.
 * Second pass fills any coverage gaps.
 */
export function renderVanGogh(pixelData, options = {}) {
  const { rgba, gray, width, height } = pixelData;
  const density = options.density || 1.0;
  const strokes = [];

  const sobel = computeSobel(gray, width, height);

  const spacing = Math.max(1, Math.floor(2 / density));
  const noiseFreq = 0.08;
  const swirlStrength = 1.0;

  // Coverage tracking grid
  const covW = Math.ceil(width / spacing);
  const covH = Math.ceil(height / spacing);
  const covered = new Uint8Array(covW * covH);

  /** Trace a particle along the flow field, returning canvas-space points. */
  function traceParticle(startX, startY, steps, stepSize) {
    const pts = [];
    let px = startX, py = startY;
    for (let i = 0; i < steps; i++) {
      pts.push(pixToCanvas(px, py, pixelData));

      const ix = clamp(Math.round(px), 0, width - 1);
      const iy = clamp(Math.round(py), 0, height - 1);
      const idx = iy * width + ix;

      // Flow direction: perpendicular to gradient = contour-following
      let angle = sobel.direction[idx] + Math.PI / 2;
      // Add Perlin noise for organic swirl
      angle += noise2d(px * noiseFreq, py * noiseFreq) * swirlStrength;

      px += Math.cos(angle) * stepSize;
      py += Math.sin(angle) * stepSize;

      if (px < 0 || px >= width || py < 0 || py >= height) break;
    }
    return pts;
  }

  // --- Corner-based iteration (CLAWDRAW_PAINT_CORNER: nw/ne/sw/se) ---
  // Sort grid cells by distance from the target corner so painting radiates from corner inward
  const paintCorner = (options.paintCorner || 'nw').toLowerCase();
  const cornerX = (paintCorner === 'ne' || paintCorner === 'se') ? width : 0;
  const cornerY = (paintCorner === 'sw' || paintCorner === 'se') ? height : 0;

  // Collect all grid positions and sort by distance from corner
  const gridCells = [];
  for (let gy = 0; gy < height; gy += spacing) {
    for (let gx = 0; gx < width; gx += spacing) {
      gridCells.push({ gx, gy });
    }
  }
  gridCells.sort((a, b) => {
    const da = (a.gx - cornerX) ** 2 + (a.gy - cornerY) ** 2;
    const db = (b.gx - cornerX) ** 2 + (b.gy - cornerY) ** 2;
    return da - db;
  });

  // --- First pass: dense grid seeding (from corner outward) ---
  for (const { gx, gy } of gridCells) {
    const jx = (Math.random() - 0.5) * spacing;
    const jy = (Math.random() - 0.5) * spacing;
    const px = clamp(gx + jx, 0, width - 1);
    const py = clamp(gy + jy, 0, height - 1);

    const steps = 4 + Math.floor(Math.random() * 5); // 4–8 points
    const pts = traceParticle(px, py, steps, 0.5);
    if (pts.length < 3) continue;

    const [r, g, b] = sampleRgb(rgba, px, py, width, height);
    const grayVal = sampleGray(gray, px, py, width, height) / 255;
    const idx = clamp(Math.round(py), 0, height - 1) * width + clamp(Math.round(px), 0, width - 1);
    const contrast = clamp(sobel.magnitude[idx] / 400, 0, 1);
    // Medium brushes for visible strokes with fine detail
    const brushSize = clamp(Math.round(4 + (1 - contrast) * 3 + (1 - grayVal) * 3), 4, 10);

    strokes.push(makeStroke(pts, rgbToHex(r, g, b), brushSize, 0.85));

    // Mark coverage cell
    const ci = Math.floor(gy / spacing) * covW + Math.floor(gx / spacing);
    if (ci >= 0 && ci < covered.length) covered[ci] = 1;
  }

  // Collect fill-pass cells and sort by distance from corner
  const fillCells = [];
  for (let ccy = 0; ccy < covH; ccy++) {
    for (let ccx = 0; ccx < covW; ccx++) {
      if (!covered[ccy * covW + ccx]) fillCells.push({ ccx, ccy });
    }
  }
  fillCells.sort((a, b) => {
    const ax = (a.ccx + 0.5) * spacing, ay = (a.ccy + 0.5) * spacing;
    const bx = (b.ccx + 0.5) * spacing, by = (b.ccy + 0.5) * spacing;
    const da = (ax - cornerX) ** 2 + (ay - cornerY) ** 2;
    const db = (bx - cornerX) ** 2 + (by - cornerY) ** 2;
    return da - db;
  });

  // --- Second pass: fill uncovered cells (from corner outward) ---
  for (const { ccx, ccy } of fillCells) {
    const px = clamp((ccx + 0.5) * spacing, 0, width - 1);
    const py = clamp((ccy + 0.5) * spacing, 0, height - 1);

    const pts = traceParticle(px, py, 4, 0.4);
    if (pts.length < 2) continue;

    const [r, g, b] = sampleRgb(rgba, px, py, width, height);
    const grayVal = sampleGray(gray, px, py, width, height) / 255;
    const brushSize = clamp(Math.round(4 + (1 - grayVal) * 3), 4, 8);

    strokes.push(makeStroke(pts, rgbToHex(r, g, b), brushSize, 0.8));
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// Mode: Slime Mold — Physarum agents guided by Sobel edge attractors
// ---------------------------------------------------------------------------

/**
 * Physarum-style agent simulation seeded with Sobel edge magnitudes.
 * Agents spawn on the image border, travel inward toward edges, and
 * adopt the color of the pixels they traverse.  A fill pass ensures
 * 100 % coverage.
 */
export function renderSlimeMold(pixelData, options = {}) {
  const { rgba, gray, width, height } = pixelData;
  const density = options.density || 1.0;

  // --- Edge attractor field ---
  const sobel = computeSobel(gray, width, height);

  // Normalize magnitude to 0–1
  let maxMag = 0;
  for (let i = 0; i < sobel.magnitude.length; i++) {
    if (sobel.magnitude[i] > maxMag) maxMag = sobel.magnitude[i];
  }
  const invMax = maxMag > 0 ? 1 / maxMag : 0;

  // Trail map grid (coarse for speed)
  const gridStep = 3;
  const cols = Math.ceil(width / gridStep);
  const rows = Math.ceil(height / gridStep);
  const trail = new Float32Array(cols * rows);

  // Seed trail map with amplified edge magnitudes so agents are drawn to edges
  for (let py = 0; py < height; py++) {
    for (let px = 0; px < width; px++) {
      const col = Math.floor(px / gridStep);
      const row = Math.floor(py / gridStep);
      if (col < cols && row < rows) {
        const edgeVal = sobel.magnitude[py * width + px] * invMax;
        trail[row * cols + col] = Math.max(trail[row * cols + col], edgeVal * 5.0);
      }
    }
  }

  // --- Agent initialization — spawn on image border, facing inward ---
  const numAgents = Math.round(250 * density);
  const perimeter = 2 * (width + height);
  const agents = [];

  for (let i = 0; i < numAgents; i++) {
    const t = (i + Math.random() * 0.5) / numAgents * perimeter;
    let ax, ay, heading;
    if (t < width) {                        // top edge
      ax = t; ay = 0;
      heading = Math.PI / 2 + (Math.random() - 0.5) * 0.6;
    } else if (t < width + height) {        // right edge
      ax = width - 1; ay = t - width;
      heading = Math.PI + (Math.random() - 0.5) * 0.6;
    } else if (t < 2 * width + height) {    // bottom edge
      ax = 2 * width + height - t; ay = height - 1;
      heading = -Math.PI / 2 + (Math.random() - 0.5) * 0.6;
    } else {                                // left edge
      ax = 0; ay = perimeter - t;
      heading = (Math.random() - 0.5) * 0.6;
    }
    agents.push({ x: ax, y: ay, heading, path: [] });
  }

  // Simulation parameters (from slime-mold.mjs defaults)
  const sensorDist = 9;
  const sensorAngle = 0.5;
  const turnSpeed = 0.3;
  const moveSpeed = 1.8;
  const decayRate = 0.9;
  const simSteps = 80;

  function sampleTrail(x, y) {
    const c = Math.floor(x / gridStep);
    const r = Math.floor(y / gridStep);
    if (c < 0 || c >= cols || r < 0 || r >= rows) return 0;
    return trail[r * cols + c];
  }

  function deposit(x, y, amount) {
    const c = Math.floor(x / gridStep);
    const r = Math.floor(y / gridStep);
    if (c >= 0 && c < cols && r >= 0 && r < rows) {
      trail[r * cols + c] += amount;
    }
  }

  // --- Simulation loop ---
  for (let step = 0; step < simSteps; step++) {
    for (const agent of agents) {
      // 3-sensor steering
      const sl = sampleTrail(
        agent.x + Math.cos(agent.heading - sensorAngle) * sensorDist,
        agent.y + Math.sin(agent.heading - sensorAngle) * sensorDist,
      );
      const sc = sampleTrail(
        agent.x + Math.cos(agent.heading) * sensorDist,
        agent.y + Math.sin(agent.heading) * sensorDist,
      );
      const sr = sampleTrail(
        agent.x + Math.cos(agent.heading + sensorAngle) * sensorDist,
        agent.y + Math.sin(agent.heading + sensorAngle) * sensorDist,
      );

      if (sc >= sl && sc >= sr) {
        // keep heading
      } else if (sl > sr) {
        agent.heading -= turnSpeed;
      } else if (sr > sl) {
        agent.heading += turnSpeed;
      } else {
        agent.heading += (Math.random() - 0.5) * turnSpeed * 2;
      }

      // Move and clamp to image bounds (no wrapping)
      agent.x = clamp(agent.x + Math.cos(agent.heading) * moveSpeed, 0, width - 1);
      agent.y = clamp(agent.y + Math.sin(agent.heading) * moveSpeed, 0, height - 1);

      deposit(agent.x, agent.y, 1.0);

      // Record position + sampled color
      const [r, g, b] = sampleRgb(rgba, agent.x, agent.y, width, height);
      agent.path.push({ px: agent.x, py: agent.y, r, g, b });
    }

    // Decay and diffuse trail map
    const prev = new Float32Array(trail);
    for (let row = 1; row < rows - 1; row++) {
      for (let col = 1; col < cols - 1; col++) {
        const i = row * cols + col;
        const avg = (prev[i - 1] + prev[i + 1] + prev[i - cols] + prev[i + cols] + prev[i] * 4) / 8;
        trail[i] = avg * decayRate;
      }
    }
  }

  // --- Stroke generation — break trails into segments ---
  const strokes = [];
  const segLen = 12;

  // Coverage tracking grid (same spacing as vangogh)
  const covSpacing = Math.max(2, Math.round(6 / density));
  const covW = Math.ceil(width / covSpacing);
  const covH = Math.ceil(height / covSpacing);
  const covered = new Uint8Array(covW * covH);

  for (const agent of agents) {
    if (agent.path.length < 3) continue;

    for (let s = 0; s < agent.path.length; s += segLen) {
      const seg = agent.path.slice(s, s + segLen);
      if (seg.length < 3) continue;

      // Convert to canvas-space points
      const pts = seg.map(p => pixToCanvas(p.px, p.py, pixelData));

      // Color from segment midpoint
      const mid = seg[Math.floor(seg.length / 2)];
      const color = rgbToHex(mid.r, mid.g, mid.b);

      // Brush size scales with local darkness
      const grayVal = sampleGray(gray, mid.px, mid.py, width, height) / 255;
      const brushSize = clamp(Math.round(3 + (1 - grayVal) * 10), 3, 14);

      strokes.push(makeStroke(pts, color, brushSize, 0.85));

      // Mark coverage
      for (const p of seg) {
        const ci = Math.floor(p.py / covSpacing) * covW + Math.floor(p.px / covSpacing);
        if (ci >= 0 && ci < covered.length) covered[ci] = 1;
      }
    }
  }

  // --- Coverage fill pass ---
  for (let cy = 0; cy < covH; cy++) {
    for (let cx = 0; cx < covW; cx++) {
      if (covered[cy * covW + cx]) continue;

      const px = clamp((cx + 0.5) * covSpacing, 0, width - 1);
      const py = clamp((cy + 0.5) * covSpacing, 0, height - 1);

      const [r, g, b] = sampleRgb(rgba, px, py, width, height);
      const grayVal = sampleGray(gray, px, py, width, height) / 255;
      const dotSize = clamp(Math.round(4 + (1 - grayVal) * 6), 3, 12);

      const c = pixToCanvas(px, py, pixelData);
      const dr = dotSize * 0.3;
      strokes.push(makeStroke(
        [{ x: c.x - dr, y: c.y }, { x: c.x + dr, y: c.y }],
        rgbToHex(r, g, b),
        dotSize,
        0.75,
      ));
    }
  }

  return strokes;
}

// ---------------------------------------------------------------------------
// Main entry — dispatches to mode renderer
// ---------------------------------------------------------------------------

/**
 * Convert pixel data into ClawDraw strokes.
 *
 * @param {object} pixelData
 * @param {Uint8Array} pixelData.rgba    — Raw RGBA bytes (width × height × 4)
 * @param {Uint8Array} pixelData.gray    — Grayscale bytes (width × height)
 * @param {number}     pixelData.width   — Pixel dimensions
 * @param {number}     pixelData.height
 * @param {number}     pixelData.canvasWidth  — Output canvas dimensions
 * @param {number}     pixelData.canvasHeight
 * @param {number}     pixelData.cx      — Canvas center X
 * @param {number}     pixelData.cy      — Canvas center Y
 *
 * @param {object} [options]
 * @param {string} [options.mode='vangogh']  — pointillist | sketch | vangogh | slimemold
 * @param {number} [options.density=1.0]     — Stroke density multiplier
 *
 * @returns {Array} Array of stroke objects
 */
export function traceImage(pixelData, options = {}) {
  const mode = options.mode || 'vangogh';
  switch (mode) {
    case 'pointillist': return renderPointillist(pixelData, options);
    case 'sketch':      return renderSketch(pixelData, options);
    case 'vangogh':     return renderVanGogh(pixelData, options);
    case 'slimemold':   return renderSlimeMold(pixelData, options);
    default:
      throw new Error(`Unknown paint mode: "${mode}". Use pointillist, sketch, vangogh, or slimemold.`);
  }
}

// ---------------------------------------------------------------------------
// Region analysis for freestyle mode
// ---------------------------------------------------------------------------

/**
 * Analyze an image by dividing it into a grid of regions, computing visual
 * characteristics for each cell.  Pure math — uses only existing internal
 * helpers (sampleRgb, sampleGray, pixToCanvas, computeSobel, rgbToHex, clamp).
 *
 * @param {object} pixelData  — Same shape as traceImage input
 * @param {object} [options]
 * @param {number} [options.density=1.0]
 * @returns {Array<{ row, col, cx, cy, cellWidth, cellHeight, color, brightness, edgeDensity, colorVariance, transparent }>}
 */
export function analyzeRegions(pixelData, options = {}) {
  const { rgba, gray, width, height, canvasWidth, canvasHeight } = pixelData;
  const density = options.density || 1.0;
  const aspect = width / height;

  const gridCols = clamp(Math.round(6 * density), 4, 10);
  const gridRows = clamp(Math.round(gridCols / aspect), 4, 10);

  // Compute Sobel once for whole image
  const sobel = computeSobel(gray, width, height);

  // Normalize Sobel magnitudes to 0-1
  let maxMag = 0;
  for (let i = 0; i < sobel.magnitude.length; i++) {
    if (sobel.magnitude[i] > maxMag) maxMag = sobel.magnitude[i];
  }
  const invMax = maxMag > 0 ? 1 / maxMag : 0;

  const cellW = width / gridCols;
  const cellH = height / gridRows;
  const regions = [];

  for (let row = 0; row < gridRows; row++) {
    for (let col = 0; col < gridCols; col++) {
      const x0 = Math.floor(col * cellW);
      const y0 = Math.floor(row * cellH);
      const x1 = Math.min(Math.floor((col + 1) * cellW), width);
      const y1 = Math.min(Math.floor((row + 1) * cellH), height);

      let rSum = 0, gSum = 0, bSum = 0;
      let graySum = 0;
      let edgeCount = 0;
      let transparentCount = 0;
      let pixelCount = 0;

      // First pass: averages
      for (let py = y0; py < y1; py++) {
        for (let px = x0; px < x1; px++) {
          pixelCount++;
          const ai = (py * width + px) * 4 + 3;
          if (rgba[ai] < 128) {
            transparentCount++;
            continue;
          }
          const [r, g, b] = sampleRgb(rgba, px, py, width, height);
          rSum += r;
          gSum += g;
          bSum += b;
          graySum += sampleGray(gray, px, py, width, height);

          const normMag = sobel.magnitude[py * width + px] * invMax;
          if (normMag > 0.15) edgeCount++;
        }
      }

      // Skip transparent cells
      if (transparentCount > pixelCount * 0.5) continue;

      const opaqueCount = pixelCount - transparentCount;
      if (opaqueCount === 0) continue;

      const avgR = rSum / opaqueCount;
      const avgG = gSum / opaqueCount;
      const avgB = bSum / opaqueCount;
      const brightness = (graySum / opaqueCount) / 255;
      const edgeDensity = edgeCount / opaqueCount;

      // Second pass: color variance
      let varR = 0, varG = 0, varB = 0;
      for (let py = y0; py < y1; py++) {
        for (let px = x0; px < x1; px++) {
          const ai = (py * width + px) * 4 + 3;
          if (rgba[ai] < 128) continue;
          const [r, g, b] = sampleRgb(rgba, px, py, width, height);
          varR += (r - avgR) ** 2;
          varG += (g - avgG) ** 2;
          varB += (b - avgB) ** 2;
        }
      }
      const colorVariance = clamp(
        ((varR + varG + varB) / (opaqueCount * 3)) / (255 * 255),
        0, 1,
      );

      // Map cell center to canvas coordinates
      const centerPx = (col + 0.5) * cellW;
      const centerPy = (row + 0.5) * cellH;
      const canvasPos = pixToCanvas(centerPx, centerPy, pixelData);

      regions.push({
        row,
        col,
        cx: canvasPos.x,
        cy: canvasPos.y,
        cellWidth: (cellW / width) * canvasWidth,
        cellHeight: (cellH / height) * canvasHeight,
        color: rgbToHex(Math.round(avgR), Math.round(avgG), Math.round(avgB)),
        brightness,
        edgeDensity,
        colorVariance,
        transparent: false,
      });
    }
  }

  return regions;
}
