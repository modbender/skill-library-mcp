/**
 * clawdraw roam — Autonomous free-roam mode.
 *
 * A decision loop that alternates between creating new art and collaborating
 * with existing art on the canvas. A single --blend factor (0.0–1.0) controls
 * the ratio: 0 = pure creation, 1 = pure collaboration, 0.5 = 50/50 default.
 *
 * Usage:
 *   clawdraw roam [--blend 0.5] [--speed normal] [--budget 0] [--name "session-name"]
 */

// @security-manifest
// env: CLAWDRAW_API_KEY (via auth.mjs)
// endpoints: api.clawdraw.ai (HTTPS), relay.clawdraw.ai (WSS)
// files: none
// exec: none

import WebSocket from 'ws';
import { getToken } from './auth.mjs';
import { connectWithRetry, sendStrokes, addWaypoint, getWaypointUrl, disconnect } from './connection.mjs';
import { executePrimitive, listPrimitives } from '../primitives/index.mjs';
import { setNearbyCache } from '../primitives/collaborator.mjs';
import { randomPalette, samplePalette } from '../primitives/helpers.mjs';

const RELAY_HTTP_URL = 'https://relay.clawdraw.ai';
const CLAWDRAW_API_KEY = process.env.CLAWDRAW_API_KEY;

// ---------------------------------------------------------------------------
// Session name generator
// ---------------------------------------------------------------------------

const ADJECTIVES = [
  'bold', 'swift', 'quiet', 'wild', 'deep', 'warm', 'cool', 'bright',
  'soft', 'sharp', 'calm', 'keen', 'pale', 'dark', 'pure', 'raw',
];
const NOUNS = [
  'bloom', 'wave', 'spark', 'drift', 'glow', 'flow', 'pulse', 'ripple',
  'frost', 'ember', 'breeze', 'shade', 'stone', 'root', 'mist', 'tide',
];

function generateSessionName() {
  const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)];
  const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)];
  return `${adj}-${noun}`;
}

// ---------------------------------------------------------------------------
// Speed presets (loop interval in ms)
// ---------------------------------------------------------------------------

const SPEED_MS = { slow: 12000, normal: 8000, fast: 6000 };

// ---------------------------------------------------------------------------
// Primitive categories for CREATE mode (weighted selection)
// ---------------------------------------------------------------------------

/** Category weights for random primitive selection. */
const CATEGORY_WEIGHTS = [
  { category: 'organic',       weight: 0.30 },
  { category: 'decorative',    weight: 0.20 },
  { category: 'flow-abstract', weight: 0.15 },
  { category: 'basic-shapes',  weight: 0.15 },
  { category: 'fills',         weight: 0.10 },
  { category: 'utility',       weight: 0.10 },
];

/** Pick a category based on weights. */
function pickCategory() {
  const r = Math.random();
  let cumulative = 0;
  for (const { category, weight } of CATEGORY_WEIGHTS) {
    cumulative += weight;
    if (r < cumulative) return category;
  }
  return CATEGORY_WEIGHTS[CATEGORY_WEIGHTS.length - 1].category;
}

// ---------------------------------------------------------------------------
// Collaborator behavior selection (context-weighted)
// ---------------------------------------------------------------------------

/** Structural behaviors — good when there are endpoints. */
const STRUCTURAL = ['extend', 'branch', 'connect', 'vineGrowth'];
/** Fill behaviors — good when there are gaps or enclosed regions. */
const FILL = ['interiorFill', 'bloom', 'hatchGradient', 'stitch', 'contour'];
/** Transform behaviors — good when there are many strokes to riff on. */
const TRANSFORM = ['echo', 'parallel', 'shadow', 'cascade', 'mirror', 'gradient', 'fragment', 'outline'];
/** Organic growth behaviors. */
const GROWTH = ['physarum', 'attractorBranch', 'surfaceTrees', 'attractorFlow', 'coil'];
/** Harmony behaviors. */
const HARMONY = ['harmonize', 'counterpoint', 'morph'];

function pickCollaboratorBehavior(nearbyData) {
  const hasAttach = nearbyData.attachPoints && nearbyData.attachPoints.length > 0;
  const hasGaps = nearbyData.gaps && nearbyData.gaps.length > 0;
  const strokeCount = nearbyData.strokes ? nearbyData.strokes.length : 0;

  // Build weighted pool based on context
  const pool = [];
  if (hasAttach) {
    pool.push(...STRUCTURAL, ...STRUCTURAL); // double weight
  } else {
    pool.push(...STRUCTURAL);
  }
  if (hasGaps) {
    pool.push(...FILL, ...FILL); // double weight
  } else {
    pool.push(...FILL);
  }
  if (strokeCount > 5) {
    pool.push(...TRANSFORM, ...TRANSFORM);
  } else {
    pool.push(...TRANSFORM);
  }
  pool.push(...GROWTH);
  pool.push(...HARMONY);

  return pool[Math.floor(Math.random() * pool.length)];
}

// ---------------------------------------------------------------------------
// Nearby API with rate-limit pacing
// ---------------------------------------------------------------------------

let nearbyCallTimestamps = [];

async function fetchNearby(token, x, y, radius = 500) {
  // Enforce max 9 calls per 60s to stay under the 10/60s rate limit
  const now = Date.now();
  nearbyCallTimestamps = nearbyCallTimestamps.filter(t => now - t < 60000);
  if (nearbyCallTimestamps.length >= 9) {
    const oldest = nearbyCallTimestamps[0];
    const waitMs = 60000 - (now - oldest) + 500; // +500ms margin
    if (waitMs > 0) {
      log(`rate-limit pacing: waiting ${Math.round(waitMs / 1000)}s`);
      await sleep(waitMs);
    }
  }

  nearbyCallTimestamps.push(Date.now());
  const res = await fetch(`${RELAY_HTTP_URL}/api/nearby?x=${x}&y=${y}&radius=${radius}&detail=sdf`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `nearby HTTP ${res.status}`);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Find-space API
// ---------------------------------------------------------------------------

async function fetchFindSpace(token, mode = 'adjacent') {
  const res = await fetch(`${RELAY_HTTP_URL}/api/find-space?mode=${mode}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `find-space HTTP ${res.status}`);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Marker APIs
// ---------------------------------------------------------------------------

async function dropMarker(token, x, y, type, message, decayMs) {
  const body = { x, y, type };
  if (message) body.message = message;
  if (decayMs) body.decayMs = decayMs;
  const res = await fetch(`${RELAY_HTTP_URL}/api/markers`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) return null; // non-critical
  return res.json();
}

async function scanMarkers(token, x, y, radius = 2000) {
  const res = await fetch(`${RELAY_HTTP_URL}/api/markers?x=${x}&y=${y}&radius=${radius}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!res.ok) return { markers: [] };
  return res.json();
}

// ---------------------------------------------------------------------------
// Random parameter generation from METADATA
// ---------------------------------------------------------------------------

function randomInRange(min, max) {
  return min + Math.random() * (max - min);
}

function randomIntInRange(min, max) {
  return Math.floor(randomInRange(min, max + 1));
}

/**
 * Generate random args for a primitive based on its METADATA parameters.
 * Position is set from the current location; other params are randomized.
 */
function randomizeArgs(primitiveName, primitiveList, cx, cy, palette) {
  const info = primitiveList.find(p => p.name === primitiveName);
  // We can't get full param info from listPrimitives, so use sensible defaults
  const args = {};

  // Position params — always set from current location
  args.cx = cx + randomInRange(-100, 100);
  args.cy = cy + randomInRange(-100, 100);

  // For collaborator behaviors, use nearX/nearY instead
  args.nearX = args.cx;
  args.nearY = args.cy;
  args.x = args.cx;
  args.y = args.cy;

  // Color from session palette
  args.color = samplePalette(palette, Math.random());

  // Common size/count params with reasonable randomized ranges
  args.radius = randomInRange(30, 200);
  args.width = randomInRange(50, 400);
  args.height = randomInRange(50, 400);
  args.brushSize = randomInRange(3, 25);
  args.size = randomInRange(3, 25);
  args.opacity = randomInRange(0.5, 1.0);
  args.count = randomIntInRange(5, 40);
  args.steps = randomIntInRange(30, 200);
  args.iterations = randomIntInRange(3, 8);
  args.depth = randomIntInRange(3, 7);
  args.rings = randomIntInRange(3, 8);
  args.folds = randomIntInRange(4, 12);
  args.spacing = randomInRange(5, 25);
  args.density = randomInRange(0.3, 0.8);
  args.length = randomInRange(30, 200);
  args.angle = randomInRange(0, 360);
  args.rotation = randomInRange(0, 360);
  args.turns = randomInRange(2, 8);
  args.scale = randomInRange(0.5, 2.0);

  // Specific primitive overrides for better results
  if (primitiveName === 'mandala') {
    args.outerRadius = randomInRange(80, 250);
    args.rings = randomIntInRange(3, 8);
    args.folds = randomIntInRange(4, 16);
  } else if (primitiveName === 'fractalTree') {
    args.height = randomInRange(40, 150);
    args.depth = randomIntInRange(4, 8);
  } else if (primitiveName === 'lSystem') {
    args.preset = ['fern', 'tree', 'bush', 'coral', 'seaweed'][Math.floor(Math.random() * 5)];
    args.length = randomInRange(30, 120);
  } else if (primitiveName === 'flowField') {
    args.width = randomInRange(100, 400);
    args.height = randomInRange(100, 400);
    args.particleCount = randomIntInRange(10, 50);
  } else if (primitiveName === 'spiral') {
    args.outerRadius = randomInRange(50, 200);
    args.turns = randomInRange(3, 10);
  } else if (primitiveName === 'strangeAttractor') {
    args.attractor = ['lorenz', 'aizawa', 'thomas'][Math.floor(Math.random() * 3)];
  } else if (primitiveName === 'sacredGeometry') {
    args.pattern = ['goldenSpiral', 'flowerOfLife', 'metatronsCube', 'sriYantra'][Math.floor(Math.random() * 4)];
    args.outerRadius = randomInRange(80, 250);
  } else if (primitiveName === 'alienGlyphs') {
    args.count = randomIntInRange(3, 12);
    args.glyphSize = randomInRange(20, 60);
  }

  return args;
}

// ---------------------------------------------------------------------------
// Movement strategies
// ---------------------------------------------------------------------------

/** Recent positions to avoid revisiting. */
const visitedPositions = [];
const MAX_VISITED = 20;
const MIN_REVISIT_DIST = 200;

function addVisited(x, y) {
  visitedPositions.push({ x, y });
  if (visitedPositions.length > MAX_VISITED) visitedPositions.shift();
}

function isNearVisited(x, y) {
  for (const pos of visitedPositions) {
    const dx = x - pos.x;
    const dy = y - pos.y;
    if (Math.sqrt(dx * dx + dy * dy) < MIN_REVISIT_DIST) return true;
  }
  return false;
}

async function pickNextPosition(token, currentX, currentY, blend) {
  const roll = Math.random();

  if (roll < 0.4) {
    // Drift: random direction, 200–600 units
    const angle = Math.random() * Math.PI * 2;
    const dist = 200 + Math.random() * 400;
    const nx = currentX + Math.cos(angle) * dist;
    const ny = currentY + Math.sin(angle) * dist;
    if (!isNearVisited(nx, ny)) return { x: nx, y: ny, method: 'drift' };
    // If near visited, try opposite direction
    const nx2 = currentX - Math.cos(angle) * dist;
    const ny2 = currentY - Math.sin(angle) * dist;
    return { x: nx2, y: ny2, method: 'drift' };
  }

  if (roll < 0.7) {
    // Find-space
    try {
      const mode = blend > 0.5 ? 'adjacent' : 'empty';
      const space = await fetchFindSpace(token, mode);
      const nx = space.canvasX;
      const ny = space.canvasY;
      if (!isNearVisited(nx, ny)) return { x: nx, y: ny, method: 'find-space' };
    } catch {
      // Fall through to drift
    }
    const angle = Math.random() * Math.PI * 2;
    const dist = 300 + Math.random() * 300;
    return { x: currentX + Math.cos(angle) * dist, y: currentY + Math.sin(angle) * dist, method: 'drift-fallback' };
  }

  // Marker-guided: scan for invitations/seeds
  try {
    const data = await scanMarkers(token, currentX, currentY, 3000);
    const interesting = (data.markers || []).filter(
      m => m.type === 'invitation' || m.type === 'seed'
    );
    if (interesting.length > 0) {
      const target = interesting[Math.floor(Math.random() * interesting.length)];
      if (!isNearVisited(target.x, target.y)) {
        return { x: target.x, y: target.y, method: 'marker' };
      }
    }
  } catch {
    // Fall through to drift
  }

  // Fallback drift
  const angle = Math.random() * Math.PI * 2;
  const dist = 200 + Math.random() * 400;
  return { x: currentX + Math.cos(angle) * dist, y: currentY + Math.sin(angle) * dist, method: 'drift-fallback' };
}

// ---------------------------------------------------------------------------
// Viewport update helper
// ---------------------------------------------------------------------------

function updateViewport(ws, x, y, zoom = 0.5) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws._currentViewport = {
      type: 'viewport.update',
      viewport: { center: { x, y }, zoom, size: { width: 6000, height: 6000 } },
      cursor: { x, y },
      username: ws._clawdrawUsername || 'openclaw-roam',
    };
    ws.send(JSON.stringify(ws._currentViewport));
  }
}

// ---------------------------------------------------------------------------
// Logging
// ---------------------------------------------------------------------------

function log(msg) {
  console.log(`[roam] ${msg}`);
}

// ---------------------------------------------------------------------------
// Main roam loop
// ---------------------------------------------------------------------------

export async function cmdRoam(args) {
  const blend = args.blend !== undefined ? Number(args.blend) : 0.5;
  const speedKey = args.speed || 'normal';
  const budget = args.budget !== undefined ? Number(args.budget) : 0;
  const sessionName = args.name || generateSessionName();
  const requireGate = args.gate || false; // default: skip algorithm gate

  if (blend < 0 || blend > 1) {
    console.error('Error: --blend must be between 0.0 and 1.0');
    process.exit(1);
  }
  if (!SPEED_MS[speedKey]) {
    console.error(`Error: --speed must be one of: ${Object.keys(SPEED_MS).join(', ')}`);
    process.exit(1);
  }
  if (!CLAWDRAW_API_KEY) {
    console.error('Error: CLAWDRAW_API_KEY environment variable not set');
    process.exit(1);
  }

  const intervalMs = SPEED_MS[speedKey];
  const token = await getToken(CLAWDRAW_API_KEY);

  // Load available primitives for CREATE mode
  const allPrimitives = await listPrimitives();
  const createPrimitives = allPrimitives.filter(p => p.category !== 'collaborator' && p.category !== 'utility');

  // Session palette (consistent colors per session)
  const sessionPalette = randomPalette();

  // Find starting position
  log(`Starting "${sessionName}" blend=${blend} speed=${speedKey} budget=${budget || 'unlimited'}`);

  let startPos;
  try {
    const mode = blend > 0.5 ? 'adjacent' : 'empty';
    const space = await fetchFindSpace(token, mode);
    startPos = { x: space.canvasX, y: space.canvasY };
  } catch (err) {
    log(`find-space failed (${err.message}), starting at origin`);
    startPos = { x: 0, y: 0 };
  }

  let cx = startPos.x;
  let cy = startPos.y;
  addVisited(cx, cy);

  // Connect with retry
  const conn = await connectWithRetry(token, {
    username: `roam-${sessionName}`,
    center: { x: cx, y: cy },
    zoom: 0.5,
  });

  log(`Connected at (${Math.round(cx)}, ${Math.round(cy)})`);

  // Drop start waypoint + working marker
  try {
    const wp = await addWaypoint(conn.ws, {
      name: `${sessionName} start`,
      x: cx, y: cy, zoom: 0.5,
      description: `Roam session "${sessionName}" — blend=${blend}`,
    });
    log(`Start waypoint: ${getWaypointUrl(wp)}`);
  } catch (e) {
    log(`Start waypoint failed: ${e.message}`);
  }

  await dropMarker(token, cx, cy, 'working', `roam: ${sessionName}`, 600000);

  // ---------------------------------------------------------------------------
  // Graceful shutdown
  // ---------------------------------------------------------------------------

  let running = true;
  let forceExit = false;
  let iteration = 0;
  let inqSpent = 0; // rough estimate based on stroke count

  process.on('SIGINT', () => {
    if (!running) {
      // Second Ctrl+C — force exit
      log('Force exit');
      process.exit(1);
    }
    running = false;
    log('Ctrl+C — finishing current iteration...');
  });

  // ---------------------------------------------------------------------------
  // Loop state
  // ---------------------------------------------------------------------------

  let lastWaypointAt = Date.now();
  let lastWaypointIter = 0;
  let lastMarkerAt = Date.now();
  let lastAction = '';

  // ---------------------------------------------------------------------------
  // CREATE mode
  // ---------------------------------------------------------------------------

  async function doCreate() {
    const category = pickCategory();
    const candidates = createPrimitives.filter(p => p.category === category);
    if (candidates.length === 0) return { strokes: 0, name: 'none' };

    const prim = candidates[Math.floor(Math.random() * candidates.length)];
    const primArgs = randomizeArgs(prim.name, allPrimitives, cx, cy, sessionPalette);

    let strokes;
    try {
      strokes = executePrimitive(prim.name, primArgs);
    } catch (err) {
      log(`create ${prim.name} failed: ${err.message}`);
      return { strokes: 0, name: prim.name };
    }

    if (!strokes || strokes.length === 0) return { strokes: 0, name: prim.name };

    const result = await conn.sendStrokes(strokes);
    return { strokes: result.strokesAcked, name: prim.name, errors: result.errors };
  }

  // ---------------------------------------------------------------------------
  // COLLABORATE mode
  // ---------------------------------------------------------------------------

  async function doCollaborate() {
    let nearbyData;
    try {
      nearbyData = await fetchNearby(token, cx, cy, 500);
    } catch (err) {
      log(`nearby failed: ${err.message}`);
      return doCreate(); // fallback
    }

    if (!nearbyData.strokes || nearbyData.strokes.length === 0) {
      return doCreate(); // no strokes nearby, create instead
    }

    const behavior = pickCollaboratorBehavior(nearbyData);
    setNearbyCache(nearbyData);

    // Build args for the behavior
    const behaviorArgs = {
      nearX: cx,
      nearY: cy,
      x: cx,
      y: cy,
      cx: cx,
      cy: cy,
      radius: 500,
      color: samplePalette(sessionPalette, Math.random()),
      brushSize: randomInRange(3, 20),
      opacity: randomInRange(0.5, 1.0),
      count: randomIntInRange(5, 30),
    };

    // If there's a source stroke, pick one
    if (nearbyData.strokes.length > 0) {
      const srcStroke = nearbyData.strokes[Math.floor(Math.random() * nearbyData.strokes.length)];
      behaviorArgs.source = srcStroke.id;
      behaviorArgs.from = srcStroke.id;
    }

    // If there are two strokes for morph/connect
    if (nearbyData.strokes.length >= 2) {
      const idx1 = Math.floor(Math.random() * nearbyData.strokes.length);
      let idx2 = Math.floor(Math.random() * nearbyData.strokes.length);
      if (idx2 === idx1) idx2 = (idx1 + 1) % nearbyData.strokes.length;
      behaviorArgs.to = nearbyData.strokes[idx2].id;
      behaviorArgs.a = nearbyData.strokes[idx1].id;
      behaviorArgs.b = nearbyData.strokes[idx2].id;
    }

    let strokes;
    try {
      strokes = executePrimitive(behavior, behaviorArgs);
    } catch (err) {
      log(`collaborate ${behavior} failed: ${err.message}`);
      return doCreate(); // fallback
    }

    if (!strokes || strokes.length === 0) {
      return doCreate(); // fallback
    }

    const result = await conn.sendStrokes(strokes);
    return { strokes: result.strokesAcked, name: behavior, mode: 'collaborate', errors: result.errors };
  }

  // ---------------------------------------------------------------------------
  // Main loop
  // ---------------------------------------------------------------------------

  while (running) {
    iteration++;
    const iterStart = Date.now();

    // Decide: create or collaborate
    const roll = Math.random();
    const mode = roll < blend ? 'collaborate' : 'create';

    // Update viewport to current drawing position so Follow can track us
    updateViewport(conn.ws, cx, cy, 0.5);

    let result;
    if (mode === 'collaborate') {
      result = await doCollaborate();
    } else {
      result = await doCreate();
    }

    // Check for INSUFFICIENT_INQ
    if (result.errors && result.errors.includes('INSUFFICIENT_INQ')) {
      log(`Out of INQ after ${iteration} iterations`);
      break;
    }

    const modeLabel = result.mode || mode;
    const strokeCount = result.strokes || 0;
    inqSpent += strokeCount; // rough 1:1 estimate
    lastAction = `${modeLabel}: ${result.name}`;

    if (strokeCount > 0) {
      log(`#${iteration} ${modeLabel}: ${result.name} → ${strokeCount} strokes`);
    } else {
      log(`#${iteration} ${modeLabel}: ${result.name} → 0 strokes (skipped)`);
    }

    // Budget check
    if (budget > 0 && inqSpent >= budget) {
      log(`Budget reached (~${inqSpent} INQ spent)`);
      break;
    }

    if (!running) break;

    // Pick next position
    const next = await pickNextPosition(token, cx, cy, blend);
    cx = next.x;
    cy = next.y;
    addVisited(cx, cy);

    // Update viewport so relay knows our new AOI
    updateViewport(conn.ws, cx, cy, 0.5);

    // Waypoint: every 5 iterations or every 45 seconds
    const now = Date.now();
    if (iteration - lastWaypointIter >= 5 || now - lastWaypointAt > 45000) {
      try {
        const wp = await addWaypoint(conn.ws, {
          name: `${sessionName} #${iteration}`,
          x: cx, y: cy, zoom: 0.5,
          description: lastAction,
        });
        log(`Waypoint: "${sessionName} #${iteration}" → ${getWaypointUrl(wp)}`);
        lastWaypointAt = now;
        lastWaypointIter = iteration;
      } catch {
        // Non-critical
      }
    }

    // Refresh working marker every ~90 seconds
    if (now - lastMarkerAt > 90000) {
      await dropMarker(token, cx, cy, 'working', `roam: ${sessionName} #${iteration}`, 600000);
      lastMarkerAt = now;
    }

    // Sleep to respect speed interval
    const elapsed = Date.now() - iterStart;
    const sleepTime = Math.max(0, intervalMs - elapsed);
    if (sleepTime > 0 && running) {
      await sleep(sleepTime);
    }
  }

  // ---------------------------------------------------------------------------
  // Cleanup
  // ---------------------------------------------------------------------------

  log(`Stopping after ${iteration} iterations, ~${inqSpent} INQ spent`);

  // Drop end waypoint
  try {
    await addWaypoint(conn.ws, {
      name: `${sessionName} end`,
      x: cx, y: cy, zoom: 0.5,
      description: `Roam complete: ${iteration} iterations`,
    });
  } catch {
    // Non-critical
  }

  // Drop complete marker
  await dropMarker(token, cx, cy, 'complete', `roam: ${sessionName} (${iteration} iterations)`, 3600000);

  conn.disconnect();
  process.exit(0);
}

// ---------------------------------------------------------------------------
// Internal
// ---------------------------------------------------------------------------

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
