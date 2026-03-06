#!/usr/bin/env node
/**
 * ClawDraw CLI — OpenClaw skill entry point.
 *
 * Usage:
 *   clawdraw setup [name]               Create agent + save API key (first-time setup)
 *   clawdraw create <name>              Create agent, get API key
 *   clawdraw auth                       Exchange API key for JWT (cached)
 *   clawdraw status                     Show connection info + INQ balance
 *   clawdraw stroke --stdin             Send custom strokes from stdin
 *   clawdraw stroke --file <path>       Send custom strokes from file
 *   clawdraw stroke --svg "M ..."       Send stroke from SVG path string
 *   clawdraw draw <primitive> [--args]  Draw a built-in primitive
 *   clawdraw compose --stdin            Compose scene from stdin
 *   clawdraw compose --file <path>      Compose scene from file
 *   clawdraw list                       List all primitives
 *   clawdraw info <name>                Show primitive parameters
 *   clawdraw scan [--cx N] [--cy N] [--detail summary|full|sdf]  Scan nearby canvas for existing strokes
 *   clawdraw look [--cx N] [--cy N] [--radius N]  Capture canvas screenshot as PNG
 *   clawdraw find-space [--mode empty|adjacent]  Find a spot on the canvas to draw
 *   clawdraw nearby [--x N] [--y N] [--radius N] [--detail summary|full|sdf]  Analyze strokes near a point
 *   clawdraw link                       Generate a link code to connect web account
 *   clawdraw buy [--tier <id>]           Buy INQ via Stripe checkout in browser
 *   clawdraw waypoint --name "..." --x N --y N --zoom Z [--description "..."]
 *                                        Drop a waypoint on the canvas
 *   clawdraw chat --message "..."        Send a chat message
 *   clawdraw paint <url> [--mode M]       Paint an image onto the canvas
 *   clawdraw template <name> --at X,Y [--scale N] [--color "#hex"] [--size N] [--rotation N]
 *                                        Draw an SVG template shape
 *   clawdraw template --list [--category <cat>]  List available templates
 *   clawdraw template --info <name>     Show template details
 *   clawdraw undo [--count N]             Undo last N drawing sessions
 *   clawdraw rename --name <name>        Set display name (session only)
 *   clawdraw erase --ids <id1,id2,...>    Erase strokes by ID (own strokes only)
 *   clawdraw waypoint-delete --id <id>  Delete a waypoint (own waypoints only)
 *   clawdraw marker drop --x N --y N --type TYPE [--message "..."] [--decay N]
 *                                        Drop a stigmergic marker
 *   clawdraw marker scan --x N --y N --radius N [--type TYPE] [--json]
 *                                        Scan for nearby markers
 *   clawdraw plan-swarm [--agents N] [--pattern name]  Plan multi-agent swarm drawing
 *   clawdraw <behavior> [--args]         Run a collaborator behavior (extend, branch, contour, etc.)
 */

// @security-manifest
// env: CLAWDRAW_API_KEY, CLAWDRAW_DISPLAY_NAME, CLAWDRAW_NO_HISTORY, CLAWDRAW_SWARM_ID, CLAWDRAW_PAINT_CORNER
// endpoints: api.clawdraw.ai (HTTPS), relay.clawdraw.ai (WSS)
// files: ~/.clawdraw/token.json, ~/.clawdraw/state.json, ~/.clawdraw/apikey.json, ~/.clawdraw/stroke-history.json
// exec: none

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { getToken, createAgent, getAgentInfo, writeApiKey, readApiKey } from './auth.mjs';
import { connect, drawAndTrack, addWaypoint, getWaypointUrl, deleteStroke, deleteWaypoint, setUsername, disconnect } from './connection.mjs';
import { parseSymmetryMode, applySymmetry } from './symmetry.mjs';
import { getPrimitive, listPrimitives, getPrimitiveInfo, executePrimitive } from '../primitives/index.mjs';
import * as collaborators from '../primitives/collaborator.mjs';
import { makeStroke } from '../primitives/helpers.mjs';
import { parseSvgPath, parseSvgPathMulti } from '../lib/svg-parse.mjs';
import { traceImage, analyzeRegions } from '../lib/image-trace.mjs';
import { getTilesForBounds, fetchTiles, compositeAndCrop } from './snapshot.mjs';
import { lookup } from 'node:dns/promises';
import sharp from 'sharp';
import { cmdRoam } from './roam.mjs';

const RELAY_HTTP_URL = 'https://relay.clawdraw.ai';
const LOGIC_HTTP_URL = 'https://api.clawdraw.ai';

const CLAWDRAW_API_KEY = process.env.CLAWDRAW_API_KEY;
const CLAWDRAW_DISPLAY_NAME = process.env.CLAWDRAW_DISPLAY_NAME || undefined;
const CLAWDRAW_NO_HISTORY = process.env.CLAWDRAW_NO_HISTORY === '1';
const CLAWDRAW_SWARM_ID = process.env.CLAWDRAW_SWARM_ID || null;
const STATE_DIR = path.join(os.homedir(), '.clawdraw');
const STATE_FILE = path.join(STATE_DIR, 'state.json');

// ---------------------------------------------------------------------------
// State management (algorithm-first gate)
// ---------------------------------------------------------------------------

function readState() {
  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
  } catch {
    return { hasCustomAlgorithm: false };
  }
}

function writeState(state) {
  try {
    fs.mkdirSync(STATE_DIR, { recursive: true });
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
  } catch {
    // Non-critical
  }
}

function markCustomAlgorithmUsed() {
  const state = readState();
  if (!state.hasCustomAlgorithm) {
    state.hasCustomAlgorithm = true;
    state.firstCustomAt = new Date().toISOString();
    writeState(state);
  }
}

function checkAlgorithmGate(force) {
  if (force) return true;
  const state = readState();
  if (!state.hasCustomAlgorithm) {
    console.log('');
    console.log('Create your own algorithm first!');
    console.log('');
    console.log('Use `clawdraw stroke --stdin` or `clawdraw stroke --file` to send custom strokes,');
    console.log('then you can mix in built-in primitives with `clawdraw draw`.');
    console.log('');
    console.log('See the SKILL.md "Your First Algorithm" section for examples.');
    console.log('');
    console.log('(Override with --force if you really want to skip this.)');
    return false;
  }
  return true;
}

// ---------------------------------------------------------------------------
// Stroke history tracking (~/.clawdraw/stroke-history.json)
// ---------------------------------------------------------------------------

const HISTORY_FILE = path.join(STATE_DIR, 'stroke-history.json');
const HISTORY_MAX_SESSIONS = 20;
const BULK_DELETE_BATCH_SIZE = 10000;

/**
 * Compute chunk key from a stroke's first point.
 * Matches the relay's chunk grid (1024 canvas units per chunk).
 */
function getChunkKey(stroke) {
  if (!stroke.points || stroke.points.length === 0) return null;
  const pt = stroke.points[0];
  const cx = Math.floor(pt.x / 1024);
  const cy = Math.floor(pt.y / 1024);
  return `${cx}_${cy}`;
}

/** Load stroke history sessions from disk. */
function loadStrokeHistory() {
  try {
    const data = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf-8'));
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

/** Atomically write stroke history sessions to disk (tmp → rename). */
function writeStrokeHistory(sessions) {
  try {
    fs.mkdirSync(STATE_DIR, { recursive: true });
    const tmp = HISTORY_FILE + '.tmp';
    fs.writeFileSync(tmp, JSON.stringify(sessions, null, 2), 'utf-8');
    fs.renameSync(tmp, HISTORY_FILE);
  } catch {
    // Non-critical — history is a convenience feature
  }
}

/** Acquire a file lock around a history read-modify-write cycle. */
function withHistoryLock(fn) {
  const lockFile = HISTORY_FILE + '.lock';
  const maxRetries = 10;
  const retryMs = 50;
  for (let i = 0; i < maxRetries; i++) {
    try {
      fs.writeFileSync(lockFile, String(process.pid), { flag: 'wx' }); // atomic O_EXCL
      try { return fn(); } finally { try { fs.unlinkSync(lockFile); } catch {} }
    } catch (e) {
      if (e.code === 'EEXIST' && i < maxRetries - 1) {
        const end = Date.now() + retryMs;
        while (Date.now() < end) {} // brief spin wait
        continue;
      }
      return; // fail open — history is non-critical
    }
  }
}

/**
 * Save a new drawing session to stroke history.
 * Each session records stroke IDs and chunk keys for undo.
 *
 * @param {Array} strokes - Array of stroke objects that were sent
 * @param {Array<string>} [ackedStrokeIds] - Optional subset of IDs confirmed by server ack
 */
function saveStrokeHistory(strokes, ackedStrokeIds) {
  if (CLAWDRAW_NO_HISTORY) return;
  withHistoryLock(() => {
    const sessions = loadStrokeHistory();
    const ackedSet = Array.isArray(ackedStrokeIds) && ackedStrokeIds.length > 0
      ? new Set(ackedStrokeIds.map(id => String(id)))
      : null;
    const session = {
      timestamp: new Date().toISOString(),
      ...(CLAWDRAW_SWARM_ID ? { swarmId: CLAWDRAW_SWARM_ID } : {}),
      strokes: strokes.map(s => ({
        id: s.id,
        chunkKey: getChunkKey(s),
      })).filter(s => {
        if (!s.id) return false;
        if (!ackedSet) return true;
        return ackedSet.has(String(s.id));
      }),
    };
    if (session.strokes.length === 0) return;
    sessions.push(session);
    while (sessions.length > HISTORY_MAX_SESSIONS) {
      sessions.shift();
    }
    writeStrokeHistory(sessions);
  });
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = {};
  let i = 0;
  while (i < argv.length) {
    const arg = argv[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith('--')) {
        args[key] = true;
        i++;
      } else {
        // Try to parse as number or JSON
        if (next === 'true') args[key] = true;
        else if (next === 'false') args[key] = false;
        else if (!isNaN(next) && next !== '') args[key] = Number(next);
        else if (next.startsWith('[') || next.startsWith('{')) {
          try { args[key] = JSON.parse(next); } catch { args[key] = next; }
        }
        else args[key] = next;
        i += 2;
      }
    } else {
      i++;
    }
  }
  return args;
}

function readStdin() {
  return new Promise((resolve, reject) => {
    const chunks = [];
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', chunk => chunks.push(chunk));
    process.stdin.on('end', () => resolve(chunks.join('')));
    process.stdin.on('error', reject);
  });
}

/** Convert simple {points, brush} format to full stroke objects */
function normalizeStrokes(strokes) {
  return strokes.map(s => {
    if (s.id && s.createdAt) return s; // Already a full stroke object
    return makeStroke(
      s.points.map(p => ({ x: Number(p.x) || 0, y: Number(p.y) || 0, pressure: p.pressure })),
      s.brush?.color || '#ffffff',
      s.brush?.size || 5,
      s.brush?.opacity || 0.9,
    );
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function isRetriableStatus(status) {
  return status === 429 || status === 500 || status === 502 || status === 503 || status === 504;
}

async function readErrorMessage(res) {
  try {
    const data = await res.json();
    return data.error || data.message || `HTTP ${res.status}`;
  } catch {
    return `HTTP ${res.status}`;
  }
}

async function fetchJsonWithRetry(url, fetchOptions, {
  retries = 3,
  baseDelayMs = 250,
  tag = 'request',
} = {}) {
  let lastError = null;
  for (let attempt = 0; attempt <= retries; attempt++) {
    let res = null;
    try {
      res = await fetch(url, fetchOptions);
      if (res.ok) return await res.json();
      const errMsg = await readErrorMessage(res);
      if (attempt < retries && isRetriableStatus(res.status)) {
        const waitMs = baseDelayMs * Math.pow(2, attempt);
        console.warn(`[${tag}] retry ${attempt + 1}/${retries} after ${res.status} (${waitMs}ms)`);
        await sleep(waitMs);
        continue;
      }
      throw new Error(errMsg);
    } catch (err) {
      lastError = err;
      const retriable = !res || isRetriableStatus(res.status);
      if (attempt < retries && retriable) {
        const waitMs = baseDelayMs * Math.pow(2, attempt);
        console.warn(`[${tag}] retry ${attempt + 1}/${retries} after error (${waitMs}ms): ${err.message}`);
        await sleep(waitMs);
        continue;
      }
      throw err;
    }
  }
  throw lastError || new Error('Unknown fetch error');
}

async function fetchNearbyData(token, x, y, radius, detail = 'full', retries = 3) {
  const q = `${RELAY_HTTP_URL}/api/nearby?x=${x}&y=${y}&radius=${radius}&detail=${encodeURIComponent(detail)}`;
  return fetchJsonWithRetry(q, {
    headers: { 'Authorization': `Bearer ${token}` },
  }, {
    retries,
    baseDelayMs: 250,
    tag: `nearby:${detail}`,
  });
}

function isSourceParam(name) {
  return name === 'source' || name === 'from' || name === 'to' || name === 'strokes';
}

function normalizeCollaboratorArg(name, value) {
  if (!isSourceParam(name)) return value;
  if (value === undefined || value === null) return value;
  if (Array.isArray(value)) return value.map(v => String(v)).join(',');
  return String(value).trim();
}

function normalizeNearbyStroke(stroke) {
  const points = Array.isArray(stroke?.points) ? stroke.points : (Array.isArray(stroke?.path) ? stroke.path : []);
  const color = stroke?.brush?.color || stroke?.color || '#ffffff';
  const size = stroke?.brush?.size || stroke?.brushSize || 5;
  return {
    points,
    brush: {
      color,
      size,
      opacity: stroke?.brush?.opacity ?? stroke?.opacity ?? 1,
    },
  };
}

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

async function cmdCreate(name) {
  if (!name) {
    console.error('Usage: clawdraw create <agent-name>');
    process.exit(1);
  }
  try {
    const result = await createAgent(name);
    console.log('Agent created successfully!');
    console.log('');
    console.log('IMPORTANT: Save this API key - it will only be shown once!');
    console.log('');
    console.log(`  Agent ID: ${result.agentId}`);
    console.log(`  Name:     ${result.name}`);
    console.log(`  API Key:  ${result.apiKey}`);
    console.log('');
    console.log('Set it as an environment variable:');
    console.log(`  export CLAWDRAW_API_KEY="${result.apiKey}"`);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Setup — first-time onboarding for npm users
// ---------------------------------------------------------------------------

const SETUP_ADJECTIVES = [
  'bold', 'swift', 'quiet', 'wild', 'deep', 'warm', 'cool', 'bright',
  'soft', 'sharp', 'calm', 'keen', 'pale', 'dark', 'pure', 'raw',
];
const SETUP_NOUNS = [
  'bloom', 'wave', 'spark', 'drift', 'glow', 'flow', 'pulse', 'ripple',
  'frost', 'ember', 'breeze', 'shade', 'stone', 'root', 'mist', 'tide',
];

async function cmdSetup(providedName) {
  // Check if already set up via env var
  const existingKey = process.env.CLAWDRAW_API_KEY;
  if (existingKey) {
    console.log('CLAWDRAW_API_KEY is already set in your environment.');
    console.log('Run `clawdraw status` to check your agent info.');
    process.exit(0);
  }

  // Check for existing saved key file
  const savedKey = readApiKey();
  if (savedKey) {
    try {
      const token = await getToken(savedKey);
      const info = await getAgentInfo(token);
      console.log('Already set up! Agent is ready.');
      console.log('');
      console.log(`  Name:  ${info.name}`);
      console.log(`  INQ:   ${info.inqBalance !== undefined ? info.inqBalance : 'unknown'}`);
      console.log('');
      console.log('Ready to draw! Try: clawdraw find-space --mode empty');
      process.exit(0);
    } catch {
      // Key exists but is invalid/revoked — fall through to create a fresh agent
      console.log('Stored API key is no longer valid. Creating a new agent...');
      console.log('');
    }
  }

  // Generate or validate name
  let name = providedName;
  if (!name) {
    const adj = SETUP_ADJECTIVES[Math.floor(Math.random() * SETUP_ADJECTIVES.length)];
    const noun = SETUP_NOUNS[Math.floor(Math.random() * SETUP_NOUNS.length)];
    name = `${adj}_${noun}`;
  }

  // Validate name format (server requires 1-32 alphanumeric/underscore)
  if (!/^[a-zA-Z0-9_]{1,32}$/.test(name)) {
    console.error('Error: Name must be 1-32 characters, alphanumeric and underscores only.');
    console.error(`  Got: "${name}"`);
    console.error('  Examples: my_artist, claude_bot, agent_42');
    process.exit(1);
  }

  console.log(`Creating agent "${name}"...`);

  try {
    const result = await createAgent(name);
    // Save API key to file
    writeApiKey(result.apiKey, result.agentId, result.name);
    console.log('');
    console.log('Agent created and configured!');
    console.log('');
    console.log(`  Name:     ${result.name}`);
    console.log(`  Agent ID: ${result.agentId}`);
    console.log(`  API Key:  saved to ~/.clawdraw/apikey.json`);

    // Auto-authenticate
    const token = await getToken(result.apiKey);
    const info = await getAgentInfo(token);
    console.log(`  INQ:      ${info.inqBalance !== undefined ? info.inqBalance : 'unknown'}`);
    console.log('');
    console.log('Ready to draw! Try: clawdraw find-space --mode empty');
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdAuth() {
  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    console.log('Authenticated successfully!');
    console.log(`Token cached at ~/.clawdraw/token.json (expires in ~5 minutes)`);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdStatus() {
  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const info = await getAgentInfo(token);
    console.log('ClawDraw Agent Status');
    console.log('');
    console.log(`  Agent:    ${info.name} (${info.agentId})`);
    console.log(`  Master:   ${info.masterId}`);
    if (info.inqBalance !== undefined) {
      console.log(`  INQ:      ${info.inqBalance}`);
    }
    console.log(`  Auth:     Valid (cached JWT)`);
    console.log('');
    const state = readState();
    console.log(`  Custom algorithm: ${state.hasCustomAlgorithm ? 'Yes' : 'Not yet'}`);
    if (state.firstCustomAt) {
      console.log(`  First custom at:  ${state.firstCustomAt}`);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

function printInqRecovery() {
  console.error('');
  console.error('Insufficient INQ. To get more:');
  console.error('');
  console.error('  1. Link account:  Open https://clawdraw.ai/?openclaw');
  console.error('                    Sign in with Google → copy the 6-char code → clawdraw link <CODE>');
  console.error('                    Linking grants a one-time 150,000 INQ bonus + 550K daily shared pool.');
  console.error('  2. Buy INQ:       Once linked, run: clawdraw buy');
}

async function cmdStroke(args) {
  let strokes;

  if (args.svg) {
    // Parse SVG path string into points, then create a stroke
    const svgStr = typeof args.svg === 'string' ? args.svg : '';
    if (!svgStr) {
      console.error('Usage: clawdraw stroke --svg "M 0 0 C 10 0 ..."');
      process.exit(1);
    }
    const points = parseSvgPath(svgStr, {
      scale: args.scale !== undefined ? Number(args.scale) : undefined,
      translate: args.tx !== undefined || args.ty !== undefined
        ? { x: Number(args.tx) || 0, y: Number(args.ty) || 0 }
        : undefined,
    });
    if (points.length === 0) {
      console.error('SVG path produced no points.');
      process.exit(1);
    }
    strokes = [makeStroke(
      points,
      args.color || '#ffffff',
      args.size !== undefined ? Number(args.size) : 5,
      args.opacity !== undefined ? Number(args.opacity) : 0.9,
    )];
  } else {
    let input;
    if (args.stdin) {
      input = await readStdin();
    } else if (args.file) {
      input = fs.readFileSync(args.file, 'utf-8');
    } else {
      console.error('Usage: clawdraw stroke --stdin  OR  clawdraw stroke --file <path>  OR  clawdraw stroke --svg "M ..."');
      process.exit(1);
    }

    let data;
    try {
      data = JSON.parse(input);
    } catch (err) {
      console.error('Invalid JSON:', err.message);
      process.exit(1);
    }

    const rawStrokes = data.strokes || (Array.isArray(data) ? data : [data]);
    strokes = normalizeStrokes(rawStrokes);
  }

  if (strokes.length === 0) {
    console.error('No strokes found in input.');
    process.exit(1);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const ws = await connect(token, { username: CLAWDRAW_DISPLAY_NAME });
    const cx = args.cx !== undefined ? Number(args.cx) : undefined;
    const cy = args.cy !== undefined ? Number(args.cy) : undefined;
    const zoom = args.zoom !== undefined ? Number(args.zoom) : undefined;
    const result = await drawAndTrack(ws, strokes, { cx, cy, zoom, name: 'Custom strokes', skipWaypoint: !!args['no-waypoint'], swarm: !!CLAWDRAW_SWARM_ID });
    markCustomAlgorithmUsed();
    if (result.strokesAcked > 0 && !args['no-history']) saveStrokeHistory(strokes, result.ackedStrokeIds);
    console.log(`Sent ${result.strokesAcked}/${result.strokesSent} stroke(s) accepted.`);
    if (result.rejected > 0) {
      console.log(`  ${result.rejected} batch(es) rejected: ${result.errors.join(', ')}`);
    }

    disconnect(ws);
    if (result.errors.includes('INSUFFICIENT_INQ')) {
      printInqRecovery();
      process.exit(1);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdDraw(primitiveName, args) {
  if (!primitiveName) {
    console.error('Usage: clawdraw draw <primitive-name> [--param value ...]');
    console.error('Run `clawdraw list` to see available primitives.');
    process.exit(1);
  }

  if (!checkAlgorithmGate(args.force)) {
    process.exit(1);
  }

  const fn = getPrimitive(primitiveName);
  if (!fn) {
    console.error(`Unknown primitive: ${primitiveName}`);
    console.error('Run `clawdraw list` to see available primitives.');
    process.exit(1);
  }

  const token = await getToken(CLAWDRAW_API_KEY);

  let strokes;
  try {
    strokes = executePrimitive(primitiveName, args);
  } catch (err) {
    console.error(`Error generating ${primitiveName}:`, err.message);
    process.exit(1);
  }

  if (!strokes || strokes.length === 0) {
    console.error('Primitive generated no strokes.');
    process.exit(1);
  }

  try {
    const ws = await connect(token, { username: CLAWDRAW_DISPLAY_NAME });
    const cx = args.cx !== undefined ? Number(args.cx) : undefined;
    const cy = args.cy !== undefined ? Number(args.cy) : undefined;
    const zoom = args.zoom !== undefined ? Number(args.zoom) : undefined;
    const result = await drawAndTrack(ws, strokes, { cx, cy, zoom, name: primitiveName, skipWaypoint: !!args['no-waypoint'], swarm: !!CLAWDRAW_SWARM_ID });
    if (result.strokesAcked > 0 && !args['no-history']) saveStrokeHistory(strokes, result.ackedStrokeIds);
    console.log(`Drew ${primitiveName}: ${result.strokesAcked}/${result.strokesSent} stroke(s) accepted.`);
    if (result.rejected > 0) {
      console.log(`  ${result.rejected} batch(es) rejected: ${result.errors.join(', ')}`);
    }

    disconnect(ws);
    if (result.errors.includes('INSUFFICIENT_INQ')) {
      printInqRecovery();
      process.exit(1);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdCompose(args) {
  let input;
  if (args.stdin) {
    input = await readStdin();
  } else if (args.file) {
    input = fs.readFileSync(args.file, 'utf-8');
  } else {
    console.error('Usage: clawdraw compose --stdin  OR  clawdraw compose --file <path>');
    process.exit(1);
  }

  let data;
  try {
    data = JSON.parse(input);
  } catch (err) {
    console.error('Invalid JSON:', err.message);
    process.exit(1);
  }

  const origin = data.origin || { x: 0, y: 0 };
  const { mode, folds } = parseSymmetryMode(data.symmetry || 'none');
  const primitives = data.primitives || [];

  let allStrokes = [];

  for (const prim of primitives) {
    if (prim.type === 'custom') {
      const strokes = normalizeStrokes(prim.strokes || []);
      allStrokes.push(...strokes);
    } else if (prim.type === 'builtin') {
      if (!checkAlgorithmGate(args.force)) {
        process.exit(1);
      }
      try {
        const strokes = executePrimitive(prim.name, prim.args || {});
        allStrokes.push(...strokes);
      } catch (err) {
        console.error(`Error generating ${prim.name}:`, err.message);
      }
    } else if (prim.type === 'template') {
      // Lazy-load shapes.json on first template encountered
      if (!cmdCompose._shapesCache) {
        const shapesPath = new URL('../templates/shapes.json', import.meta.url).pathname;
        try {
          cmdCompose._shapesCache = JSON.parse(fs.readFileSync(shapesPath, 'utf8'));
        } catch (err) {
          console.error('Failed to load template library:', err.message);
          continue;
        }
      }
      const t = cmdCompose._shapesCache.templates[prim.name];
      if (!t) {
        console.error(`Template "${prim.name}" not found.`);
        continue;
      }
      const tArgs = prim.args || {};
      const scale = tArgs.scale ?? 0.5;
      const color = tArgs.color || '#000000';
      const size = tArgs.size ?? 10;
      const rotation = tArgs.rotation ?? 0;
      const opacity = tArgs.opacity ?? 1;

      for (const pathD of t.paths) {
        const subpaths = parseSvgPathMulti(pathD, { scale, translate: { x: 0, y: 0 } });
        for (const points of subpaths) {
          if (points.length < 2) continue;
          if (rotation !== 0) {
            const rad = rotation * Math.PI / 180;
            const cos = Math.cos(rad);
            const sin = Math.sin(rad);
            for (const p of points) {
              const dx = p.x;
              const dy = p.y;
              p.x = dx * cos - dy * sin;
              p.y = dx * sin + dy * cos;
            }
          }
          allStrokes.push(makeStroke(points, color, size, opacity, 'flat'));
        }
      }
    }
  }

  // Apply origin offset
  if (origin.x !== 0 || origin.y !== 0) {
    for (const stroke of allStrokes) {
      for (const pt of stroke.points) {
        pt.x += origin.x;
        pt.y += origin.y;
      }
    }
  }

  // Apply symmetry
  allStrokes = applySymmetry(allStrokes, mode, folds, origin.x, origin.y);

  if (allStrokes.length === 0) {
    console.error('Composition generated no strokes.');
    process.exit(1);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const ws = await connect(token, { username: CLAWDRAW_DISPLAY_NAME });
    const hasOrigin = data.origin != null;
    const cx = hasOrigin ? origin.x : undefined;
    const cy = hasOrigin ? origin.y : undefined;
    const zoom = args.zoom !== undefined ? Number(args.zoom) : undefined;
    const result = await drawAndTrack(ws, allStrokes, { cx, cy, zoom, name: 'Composition', skipWaypoint: !!args['no-waypoint'], absolute: hasOrigin, swarm: !!CLAWDRAW_SWARM_ID });

    // Mark custom if any custom primitives were used
    if (primitives.some(p => p.type === 'custom')) {
      markCustomAlgorithmUsed();
    }
    if (result.strokesAcked > 0 && !args['no-history']) saveStrokeHistory(allStrokes, result.ackedStrokeIds);

    const sym = mode !== 'none' ? `, ${mode} symmetry` : '';
    console.log(`Composed: ${result.strokesAcked}/${result.strokesSent} stroke(s) accepted${sym}.`);
    if (result.rejected > 0) {
      console.log(`  ${result.rejected} batch(es) rejected: ${result.errors.join(', ')}`);
    }

    disconnect(ws);
    if (result.errors.includes('INSUFFICIENT_INQ')) {
      printInqRecovery();
      process.exit(1);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdList() {
  const all = await listPrimitives();
  let currentCategory = '';
  console.log('ClawDraw Primitives');
  console.log('');
  for (const p of all) {
    if (p.category !== currentCategory) {
      currentCategory = p.category;
      console.log(`  ${currentCategory.toUpperCase()}`);
    }
    const src = p.source === 'community' ? ' [community]' : '';
    console.log(`    ${p.name.padEnd(22)} ${p.description}${src}`);
  }
  console.log('');
  console.log(`${all.length} primitives total. Use \`clawdraw info <name>\` for parameter details.`);
}

async function cmdInfo(name) {
  if (!name) {
    console.error('Usage: clawdraw info <primitive-name>');
    process.exit(1);
  }
  const info = await getPrimitiveInfo(name);
  if (!info) {
    console.error(`Unknown primitive: ${name}`);
    process.exit(1);
  }
  console.log(`${info.name} — ${info.description}`);
  console.log(`Category: ${info.category} | Source: ${info.source || 'builtin'}`);
  console.log('');
  console.log('Parameters:');
  for (const [param, meta] of Object.entries(info.parameters || {})) {
    const req = meta.required ? '*' : ' ';
    let range = '';
    if (meta.options) {
      range = meta.options.join(' | ');
    } else if (meta.min !== undefined && meta.max !== undefined) {
      range = `${meta.min} – ${meta.max}`;
    }
    const def = meta.default !== undefined ? `(default: ${meta.default})` : '';
    const desc = meta.description || '';
    const parts = [range, def, desc].filter(Boolean).join('  ');
    console.log(`  ${req} --${param.padEnd(18)} ${meta.type}  ${parts}`);
  }
  console.log('');
  console.log('* = required');
}

// ---------------------------------------------------------------------------
// Color analysis helpers (for scan command)
// ---------------------------------------------------------------------------

function colorName(hex) {
  if (!hex || hex.length < 7) return 'mixed';
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  if (r > 200 && g < 80 && b < 80) return 'red';
  if (r > 200 && g > 200 && b < 80) return 'yellow';
  if (r > 200 && g > 150 && b < 80) return 'orange';
  if (r < 80 && g > 180 && b < 80) return 'green';
  if (r < 80 && g > 180 && b > 180) return 'cyan';
  if (r < 80 && g < 80 && b > 180) return 'blue';
  if (r > 150 && g < 80 && b > 150) return 'purple';
  if (r > 200 && g < 150 && b > 150) return 'pink';
  if (r > 200 && g > 200 && b > 200) return 'white';
  if (r < 60 && g < 60 && b < 60) return 'black';
  if (Math.abs(r - g) < 30 && Math.abs(g - b) < 30) return 'gray';
  return 'mixed';
}

function analyzeStrokes(strokes) {
  const normalized = (strokes || [])
    .map(normalizeNearbyStroke)
    .filter(s => Array.isArray(s.points) && s.points.length > 0);

  if (normalized.length === 0) {
    return {
      strokeCount: 0,
      description: 'The canvas is empty nearby. You have a blank slate.',
    };
  }

  // Spatial bounds
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const stroke of normalized) {
    for (const pt of stroke.points || []) {
      minX = Math.min(minX, pt.x);
      maxX = Math.max(maxX, pt.x);
      minY = Math.min(minY, pt.y);
      maxY = Math.max(maxY, pt.y);
    }
  }

  // Color analysis
  const colorCounts = {};
  for (const s of normalized) {
    const c = s.brush?.color || '#ffffff';
    colorCounts[c] = (colorCounts[c] || 0) + 1;
  }
  const colorsSorted = Object.entries(colorCounts).sort((a, b) => b[1] - a[1]);
  const topColors = colorsSorted.slice(0, 5).map(([c]) => c);

  // Named color summary
  const namedCounts = {};
  for (const c of topColors) {
    const name = colorName(c);
    namedCounts[name] = (namedCounts[name] || 0) + (colorCounts[c] || 0);
  }
  const colorDesc = Object.entries(namedCounts)
    .sort((a, b) => b[1] - a[1])
    .map(([name, count]) => `${name} (${count})`)
    .join(', ');

  // Brush size stats
  const sizes = normalized.map(s => s.brush?.size || 5);
  const avgSize = sizes.reduce((a, b) => a + b, 0) / sizes.length;

  const width = maxX - minX;
  const height = maxY - minY;

  return {
    strokeCount: normalized.length,
    boundingBox: {
      minX: Math.round(minX),
      maxX: Math.round(maxX),
      minY: Math.round(minY),
      maxY: Math.round(maxY),
    },
    span: { width: Math.round(width), height: Math.round(height) },
    uniqueColors: colorsSorted.length,
    topColors,
    avgBrushSize: Math.round(avgSize * 10) / 10,
    description: `${normalized.length} strokes spanning ${Math.round(width)}x${Math.round(height)} units. Colors: ${colorDesc}. Region: (${Math.round(minX)},${Math.round(minY)}) to (${Math.round(maxX)},${Math.round(maxY)}). Avg brush size: ${avgSize.toFixed(1)}.`,
  };
}

async function cmdScan(args) {
  const cx = Number(args.cx) || 0;
  const cy = Number(args.cy) || 0;
  const radius = Number(args.radius) || 600;
  const detail = String(args.detail || 'full');
  const json = args.json || false;

  if (!['summary', 'full', 'sdf'].includes(detail)) {
    console.error('Error: --detail must be one of summary|full|sdf');
    process.exit(1);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const nearby = await fetchNearbyData(token, cx, cy, radius, detail, 3);
    const strokes = Array.isArray(nearby.strokes) ? nearby.strokes : [];
    let analysis = analyzeStrokes(strokes);
    if (analysis.strokeCount === 0 && nearby.summary?.strokeCount > 0) {
      analysis = {
        strokeCount: nearby.summary.strokeCount,
        description: `${nearby.summary.strokeCount} strokes nearby (summary/detail-only response).`,
      };
    }

    const result = {
      center: { x: cx, y: cy },
      radius,
      detail,
      totalInNearby: strokes.length,
      ...analysis,
      ...(nearby.summary ? { summary: nearby.summary } : {}),
    };

    if (json) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      console.log('Canvas Scan');
      console.log(`  Center: (${cx}, ${cy}), Radius: ${radius}, Detail: ${detail}`);
      console.log(`  ${result.description}`);
      if (result.strokeCount > 0) {
        if (result.topColors) console.log(`  Top colors: ${result.topColors.join(', ')}`);
        if (nearby.summary?.palette?.length) console.log(`  Palette: ${nearby.summary.palette.join(', ')}`);
      }
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdFindSpace(args) {
  const mode = args.mode || 'empty';
  const json = args.json || false;

  if (mode !== 'empty' && mode !== 'adjacent') {
    console.error('Error: --mode must be "empty" or "adjacent"');
    process.exit(1);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const res = await fetch(`${RELAY_HTTP_URL}/api/find-space?mode=${mode}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${res.status}`);
    }

    const data = await res.json();

    if (json) {
      console.log(JSON.stringify(data, null, 2));
    } else {
      console.log(`Found ${mode} space:`);
      console.log(`  Chunk: ${data.chunkKey}`);
      console.log(`  Canvas position: (${data.canvasX}, ${data.canvasY})`);
      console.log(`  Active chunks on canvas: ${data.activeChunkCount}`);
      console.log(`  Center of art: (${data.centerOfMass.x}, ${data.centerOfMass.y})`);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdLink(code) {
  if (!code) {
    console.log('To link your ClawDraw web account:');
    console.log('');
    console.log('  1. Open: https://clawdraw.ai/?openclaw');
    console.log('  2. Sign in with Google');
    console.log('  3. Copy the 6-character link code');
    console.log('  4. Run:  clawdraw link <CODE>');
    process.exit(0);
  }

  // Strip whitespace and non-alphanumeric chars (handles trailing letters, spaces, punctuation)
  const cleanCode = code.replace(/[^A-Za-z0-9]/g, '').toUpperCase();
  if (cleanCode.length !== 6) {
    console.error(`Error: Link code must be exactly 6 characters (got ${cleanCode.length}: "${cleanCode}")`);
    console.error('Get a fresh code at https://clawdraw.ai/?openclaw');
    process.exit(1);
  }

  // Uses LOGIC_HTTP_URL from top-level constant
  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const res = await fetch(`${LOGIC_HTTP_URL}/api/link/redeem`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code: cleanCode }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      if (res.status === 404) {
        throw new Error('Invalid or expired link code. Get a new code at https://clawdraw.ai/?openclaw');
      }
      if (res.status === 409) {
        throw new Error(err.message === 'This agent is already linked to a Google account'
          ? 'This agent is already linked to a Google account. Each agent can only link once.'
          : 'This Google account is already linked to another agent. Each Google account can only link to one agent.');
      }
      throw new Error(err.message || `HTTP ${res.status}`);
    }

    const data = await res.json();
    console.log('');
    console.log('Account Linked!');
    console.log('');
    console.log(`  Web account: ${data.linkedUserId}`);
    console.log(`  Master ID:   ${data.masterId}`);
    console.log('');
    console.log('Your web account and agents now share the same INQ pool.');
    console.log('Daily shared INQ grant: 550,000 INQ.');
    console.log('One-time linking bonus: 150,000 INQ credited.');
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdBuy(args) {
  // Uses LOGIC_HTTP_URL from top-level constant
  const tierId = args.tier || 'bucket';
  const validTiers = ['splash', 'bucket', 'barrel', 'ocean'];
  if (!validTiers.includes(tierId)) {
    console.error(`Invalid tier: ${tierId}`);
    console.error(`Valid tiers: ${validTiers.join(', ')}`);
    process.exit(1);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const info = await getAgentInfo(token);
    const masterId = info.masterId || info.agentId;

    const res = await fetch(`${LOGIC_HTTP_URL}/api/payments/create-checkout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: masterId,
        tierId,
        successUrl: 'https://clawdraw.ai',
        cancelUrl: 'https://clawdraw.ai',
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || `HTTP ${res.status}`);
    }

    const data = await res.json();
    if (!data.url) {
      throw new Error('No checkout URL returned');
    }

    console.log(`Stripe checkout ready (${tierId} tier). Open this URL in your browser:`);
    console.log('');
    console.log(`  ${data.url}`);
    console.log('');
    console.log('INQ will be credited to your account automatically after payment.');
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdWaypoint(args) {
  const name = args.name;
  const x = args.x;
  const y = args.y;
  const zoom = args.zoom;
  const description = args.description || '';

  // Validate required params
  if (!name || x === undefined || y === undefined || zoom === undefined) {
    console.error('Usage: clawdraw waypoint --name "..." --x N --y N --zoom Z [--description "..."]');
    process.exit(1);
  }
  if (typeof x !== 'number' || typeof y !== 'number' || !isFinite(x) || !isFinite(y)) {
    console.error('Error: --x and --y must be finite numbers');
    process.exit(1);
  }
  if (typeof zoom !== 'number' || !isFinite(zoom) || zoom <= 0) {
    console.error('Error: --zoom must be a positive finite number');
    process.exit(1);
  }
  if (name.length > 64) {
    console.error('Error: --name must be 64 characters or fewer');
    process.exit(1);
  }
  if (description.length > 512) {
    console.error('Error: --description must be 512 characters or fewer');
    process.exit(1);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const ws = await connect(token, { username: CLAWDRAW_DISPLAY_NAME });

    const wp = await addWaypoint(ws, { name, x, y, zoom, description });
    disconnect(ws);

    console.log(`Waypoint created: "${wp.name}" at (${wp.x}, ${wp.y}) zoom=${wp.zoom}`);
    console.log(`Link: ${getWaypointUrl(wp)}`);
    process.exit(0);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdErase(args) {
  const idsRaw = args.ids;
  if (!idsRaw) {
    console.log('Usage: clawdraw erase --ids <id1,id2,...>');
    console.log('Erases strokes by ID (own strokes only).');
    process.exit(0);
  }
  const ids = String(idsRaw).split(',').map(s => s.trim()).filter(Boolean);
  if (ids.length === 0) {
    console.log('Usage: clawdraw erase --ids <id1,id2,...>');
    process.exit(0);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const ws = await connect(token, { username: CLAWDRAW_DISPLAY_NAME });
    let deleted = 0;
    let failed = 0;
    for (const id of ids) {
      try {
        await deleteStroke(ws, id);
        console.log(`  Deleted stroke ${id}`);
        deleted++;
      } catch (err) {
        console.error(`  Failed to delete stroke ${id}: ${err.message}`);
        failed++;
      }
    }
    disconnect(ws);
    console.log(`Erased ${deleted}/${ids.length} stroke(s)${failed ? `, ${failed} failed` : ''}.`);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdWaypointDelete(args) {
  const id = args.id;
  if (!id) {
    console.log('Usage: clawdraw waypoint-delete --id <id>');
    console.log('Deletes a waypoint by ID (own waypoints only).');
    process.exit(0);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const ws = await connect(token, { username: CLAWDRAW_DISPLAY_NAME });
    await deleteWaypoint(ws, String(id));
    disconnect(ws);
    console.log(`Waypoint ${id} deleted.`);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdChat(args) {
  const content = args.message;
  if (!content) {
    console.error('Usage: clawdraw chat --message "your message"');
    process.exit(1);
  }
  if (content.length > 500) {
    console.error('Error: Chat message must be 500 characters or fewer');
    process.exit(1);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const ws = await connect(token, { username: CLAWDRAW_DISPLAY_NAME });

    // Wait briefly for sync.error (rate limit or invalid content)
    const result = await new Promise((resolve) => {
      const timeout = setTimeout(() => resolve({ ok: true }), 3000);

      ws.on('message', (data) => {
        try {
          const msg = JSON.parse(data);
          if (msg.type === 'sync.error') {
            clearTimeout(timeout);
            resolve({ ok: false, error: msg.message || msg.code || 'Unknown error' });
          }
        } catch { /* ignore parse errors */ }
      });

      ws.send(JSON.stringify({
        type: 'chat.send',
        chatMessage: { content },
      }));
    });

    disconnect(ws);

    if (!result.ok) {
      console.error(`Error: ${result.error}`);
      process.exit(1);
    }

    console.log(`Chat sent: "${content}"`);
    process.exit(0);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdNearby(args) {
  const x = parseFloat(args.x || args.cx || '0');
  const y = parseFloat(args.y || args.cy || '0');
  const radius = parseFloat(args.radius || args.r || '500');
  const detail = String(args.detail || 'full');
  const json = args.json || false;

  if (!['summary', 'full', 'sdf'].includes(detail)) {
    console.error('Error: --detail must be one of summary|full|sdf');
    process.exit(1);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const result = await fetchNearbyData(token, x, y, radius, detail, 3);

    if (json) {
      console.log(JSON.stringify(result, null, 2));
      return result;
    }

    const summary = result.summary || {};
    const strokes = Array.isArray(result.strokes) ? result.strokes : [];
    const attachPoints = Array.isArray(result.attachPoints) ? result.attachPoints : [];
    const gaps = Array.isArray(result.gaps) ? result.gaps : [];

    console.log(`\n  Nearby (${x}, ${y}) radius=${radius} detail=${detail}`);
    console.log(`  Strokes: ${summary.strokeCount ?? strokes.length ?? 0}`);
    if (typeof summary.density === 'number') {
      console.log(`  Density: ${summary.density.toFixed(2)} strokes/1000sq`);
    }
    if (Array.isArray(summary.palette)) {
      console.log(`  Palette: ${summary.palette.join(', ')}`);
    }
    if (summary.dominantFlow) {
      console.log(`  Flow: ${summary.dominantFlow}`);
    }
    if (typeof summary.avgBrushSize === 'number') {
      console.log(`  Avg brush: ${summary.avgBrushSize.toFixed(1)}`);
    }
    console.log(`  Attach points: ${attachPoints.length}`);
    console.log(`  Gaps: ${gaps.length}`);

    if (strokes.length > 0) {
      console.log(`\n  Strokes (${strokes.length}):`);
      for (const s of strokes.slice(0, 10)) {
        const sid = s?.id !== undefined && s?.id !== null ? String(s.id) : 'unknown';
        const shape = s?.shape || 'stroke';
        const color = s?.color || s?.brush?.color || '#ffffff';
        const size = s?.brushSize ?? s?.brush?.size ?? '?';
        console.log(`    ${sid.slice(0, 12)}.. ${shape} ${color} size=${size}`);
      }
      if (strokes.length > 10) {
        console.log(`    ... and ${strokes.length - 10} more`);
      }
    }

    return result;
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdMarkerDrop(args) {
  // Uses RELAY_HTTP_URL from top-level constant
  const x = parseFloat(args.x || '0');
  const y = parseFloat(args.y || '0');
  const type = args.type;
  const message = args.message || undefined;
  const decay = args.decay !== undefined ? Number(args.decay) : undefined;

  const validTypes = ['working', 'complete', 'invitation', 'avoid', 'seed'];
  if (!type || !validTypes.includes(type)) {
    console.error(`Usage: clawdraw marker drop --x N --y N --type ${validTypes.join('|')} [--message "..."] [--decay N]`);
    process.exit(1);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const body = { x, y, type, message };
    if (decay !== undefined) body.decayMs = decay;

    const res = await fetch(`${RELAY_HTTP_URL}/api/markers`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${res.status}`);
    }

    const marker = await res.json();
    console.log(`Marker dropped: ${marker.type} at (${marker.x}, ${marker.y})`);
    console.log(`  ID: ${marker.id}`);
    if (marker.message) console.log(`  Message: ${marker.message}`);
    console.log(`  Decay: ${marker.decayMs}ms`);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdMarkerScan(args) {
  // Uses RELAY_HTTP_URL from top-level constant
  const x = parseFloat(args.x || '0');
  const y = parseFloat(args.y || '0');
  const radius = parseFloat(args.radius || '500');
  const filterType = args.type || null;
  const json = args.json || false;

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const res = await fetch(`${RELAY_HTTP_URL}/api/markers?x=${x}&y=${y}&radius=${radius}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${res.status}`);
    }

    const data = await res.json();
    let markers = data.markers || [];

    // Client-side type filter
    if (filterType) {
      markers = markers.filter(m => m.type === filterType);
    }

    if (json) {
      console.log(JSON.stringify({ markers }, null, 2));
      return;
    }

    if (markers.length === 0) {
      console.log(`No markers found near (${x}, ${y}) radius=${radius}`);
      return;
    }

    console.log(`Markers near (${x}, ${y}) radius=${radius}:`);
    for (const m of markers) {
      const age = Math.round((Date.now() - m.createdAt) / 1000);
      const ageStr = age < 60 ? `${age}s` : `${Math.round(age / 60)}m`;
      const msg = m.message ? ` — "${m.message}"` : '';
      console.log(`  [${m.type}] (${m.x}, ${m.y}) age=${ageStr}${msg}`);
    }
    console.log(`${markers.length} marker(s) total`);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Template library — draw pre-made SVG shapes
// ---------------------------------------------------------------------------

async function cmdTemplate(args) {
  const shapesPath = new URL('../templates/shapes.json', import.meta.url).pathname;
  let shapes;
  try {
    shapes = JSON.parse(fs.readFileSync(shapesPath, 'utf8'));
  } catch (err) {
    console.error('Failed to load template library:', err.message);
    process.exit(1);
  }

  // --list mode
  if (args.list !== undefined) {
    const category = typeof args.list === 'string' ? args.list : (args.category || null);
    const entries = Object.entries(shapes.templates);
    const filtered = category
      ? entries.filter(([, t]) => t.category === category)
      : entries;

    if (filtered.length === 0) {
      console.log(`No templates found${category ? ` in category "${category}"` : ''}.`);
      return;
    }

    const byCategory = {};
    for (const [name, t] of filtered) {
      if (!byCategory[t.category]) byCategory[t.category] = [];
      byCategory[t.category].push(name);
    }

    console.log(`\nTemplates (${filtered.length}):\n`);
    for (const [cat, names] of Object.entries(byCategory).sort()) {
      console.log(`  ${cat} (${names.length}):`);
      // Print in rows of 5
      for (let i = 0; i < names.length; i += 5) {
        console.log(`    ${names.slice(i, i + 5).join(', ')}`);
      }
    }
    return;
  }

  // --info mode
  if (args.info) {
    const t = shapes.templates[args.info];
    if (!t) {
      console.error(`Template "${args.info}" not found. Run \`clawdraw template --list\` to see available templates.`);
      process.exit(1);
    }
    console.log(`\n  ${args.info}`);
    console.log(`  Category: ${t.category}`);
    console.log(`  Description: ${t.description}`);
    console.log(`  Paths: ${t.paths.length}`);
    for (let i = 0; i < t.paths.length; i++) {
      const preview = t.paths[i].length > 60 ? t.paths[i].slice(0, 60) + '...' : t.paths[i];
      console.log(`    [${i}]: ${preview}`);
    }
    return;
  }

  // Draw template mode — first positional arg or --name
  const rest = process.argv.slice(3);
  const name = rest.find(a => !a.startsWith('--')) || args.name;
  if (!name) {
    console.error('Usage: clawdraw template <name> --at X,Y [--scale N] [--color "#hex"] [--size N] [--rotation N]');
    console.error('       clawdraw template --list [--category human|natural|...]');
    console.error('       clawdraw template --info <name>');
    process.exit(1);
  }

  const t = shapes.templates[name];
  if (!t) {
    console.error(`Template "${name}" not found. Run \`clawdraw template --list\` to see available templates.`);
    process.exit(1);
  }

  // atX/atY for stroke generation (default 0); cx/cy for drawAndTrack (undefined = auto-place)
  let atX = 0, atY = 0;
  let cx, cy;
  if (args.at) {
    [atX, atY] = args.at.split(',').map(Number);
    cx = atX;
    cy = atY;
  }

  // Parse options
  const scale = args.scale ?? 0.5;
  const color = args.color || '#000000';
  const size = args.size ?? 10;
  const rotation = args.rotation ?? 0;
  const opacity = args.opacity ?? 1;

  const strokes = [];
  for (const pathD of t.paths) {
    // Split each SVG path into subpaths at M commands to avoid connecting lines
    const subpaths = parseSvgPathMulti(pathD, {
      scale,
      translate: { x: atX, y: atY },
    });

    for (const points of subpaths) {
      if (points.length < 2) continue;

      // Apply rotation around the placement point
      if (rotation !== 0) {
        const rad = rotation * Math.PI / 180;
        const cos = Math.cos(rad);
        const sin = Math.sin(rad);
        for (const p of points) {
          const dx = p.x - atX;
          const dy = p.y - atY;
          p.x = atX + dx * cos - dy * sin;
          p.y = atY + dx * sin + dy * cos;
        }
      }

      strokes.push(makeStroke(points, color, size, opacity, 'flat'));
    }
  }

  if (strokes.length === 0) {
    console.error('Template produced no drawable strokes.');
    process.exit(1);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const ws = await connect(token, { username: CLAWDRAW_DISPLAY_NAME });
    const zoom = args.zoom !== undefined ? Number(args.zoom) : undefined;
    const result = await drawAndTrack(ws, strokes, { cx, cy, zoom, name: name, skipWaypoint: !!args['no-waypoint'], swarm: !!CLAWDRAW_SWARM_ID });
    if (result.strokesAcked > 0 && !args['no-history']) saveStrokeHistory(strokes, result.ackedStrokeIds);
    console.log(`Drew template "${name}": ${result.strokesAcked}/${result.strokesSent} stroke(s) accepted.`);
    if (result.rejected > 0) {
      console.log(`  ${result.rejected} batch(es) rejected: ${result.errors.join(', ')}`);
    }

    disconnect(ws);
    if (result.errors.includes('INSUFFICIENT_INQ')) {
      printInqRecovery();
      process.exit(1);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Collaborator behaviors — auto-fetch nearby data and execute
// ---------------------------------------------------------------------------

const COLLABORATOR_NAMES = new Set([
  'extend', 'branch', 'connect', 'coil',
  'morph', 'hatchGradient', 'stitch', 'bloom',
  'gradient', 'parallel', 'echo', 'cascade', 'mirror', 'shadow',
  'counterpoint', 'harmonize', 'fragment', 'outline',
  'contour', 'physarum', 'attractorBranch', 'surfaceTrees', 'attractorFlow', 'interiorFill', 'vineGrowth',
]);

async function cmdCollaborate(behaviorName, args) {
  // Uses RELAY_HTTP_URL from top-level constant

  if (!checkAlgorithmGate(args.force)) {
    process.exit(1);
  }

  const fn = collaborators[behaviorName];
  if (typeof fn !== 'function') {
    console.error(`Unknown collaborator: ${behaviorName}`);
    process.exit(1);
  }
  const entry = collaborators.METADATA.find(m => m.name === behaviorName);
  if (!entry) {
    console.error(`No metadata for collaborator: ${behaviorName}`);
    process.exit(1);
  }
  const paramNames = Object.keys(entry.parameters || {});
  const requiresSourceLookup = paramNames.some(isSourceParam);

  // Determine location from args
  const x = parseFloat(args.x || args.cx || args.nearX || args.atX || '0');
  const y = parseFloat(args.y || args.cy || args.nearY || args.atY || '0');
  const radius = parseFloat(args.radius || args.r || '500');
  const detail = String(args.detail || (requiresSourceLookup ? 'full' : 'sdf'));

  if (!['summary', 'full', 'sdf'].includes(detail)) {
    console.error('Error: --detail must be one of summary|full|sdf');
    process.exit(1);
  }

  // Auto-fetch nearby data before executing behavior
  const token = await getToken(CLAWDRAW_API_KEY);
  let nearbyData;
  try {
    nearbyData = await fetchNearbyData(token, x, y, radius, detail, 3);
    // Some source-driven behaviors depend on stable stroke IDs; if a non-full
    // payload omits them, refetch in full detail once.
    if (requiresSourceLookup && detail !== 'full') {
      const hasIds = Array.isArray(nearbyData.strokes)
        && nearbyData.strokes.some(s => s && s.id !== undefined && s.id !== null);
      if (!hasIds) {
        nearbyData = await fetchNearbyData(token, x, y, radius, 'full', 2);
      }
    }
  } catch (err) {
    console.error(`Failed to fetch nearby data: ${err.message}`);
    process.exit(1);
  }

  // Inject nearby cache into collaborator module
  collaborators.setNearbyCache(nearbyData);

  // Call collaborator function directly — bypass primitive registry to avoid
  // name collisions with community primitives (e.g. vineGrowth).
  let strokes;
  try {
    const behaviorArgs = paramNames.map(p => normalizeCollaboratorArg(p, args[p]));
    strokes = fn(...behaviorArgs);
  } catch (err) {
    console.error(`Error generating ${behaviorName}:`, err.message);
    process.exit(1);
  }

  if (!strokes || strokes.length === 0) {
    console.error(`Behavior ${behaviorName} produced no strokes (${nearbyData.strokes?.length || 0} strokes nearby).`);
    process.exit(1);
  }

  // Send via WebSocket
  try {
    const ws = await connect(token, { username: CLAWDRAW_DISPLAY_NAME });
    const zoom = args.zoom !== undefined ? Number(args.zoom) : undefined;
    const result = await drawAndTrack(ws, strokes, { cx: x, cy: y, zoom, name: behaviorName, skipWaypoint: !!args['no-waypoint'], swarm: !!CLAWDRAW_SWARM_ID });
    if (result.strokesAcked > 0 && !args['no-history']) saveStrokeHistory(strokes, result.ackedStrokeIds);
    console.log(`  ${behaviorName}: ${result.strokesAcked}/${result.strokesSent} stroke(s) accepted.`);
    if (result.rejected > 0) {
      console.log(`  ${result.rejected} batch(es) rejected: ${result.errors.join(', ')}`);
    }

    disconnect(ws);
    if (result.errors.includes('INSUFFICIENT_INQ')) {
      printInqRecovery();
      process.exit(1);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Look — canvas screenshot without drawing
// ---------------------------------------------------------------------------

const TILE_CDN_URL = 'https://relay.clawdraw.ai/tiles';

async function cmdLook(args) {
  const cx = Number(args.cx) || 0;
  const cy = Number(args.cy) || 0;
  const radius = Math.max(100, Math.min(3000, Number(args.radius) || 500));

  // Build bounding box from center + radius
  const bbox = {
    minX: cx - radius,
    minY: cy - radius,
    maxX: cx + radius,
    maxY: cy + radius,
  };

  // Map to tile coordinates and fetch from CDN (no auth needed)
  const grid = getTilesForBounds(bbox);
  console.log(`Fetching ${grid.tiles.length} tile(s) at (${cx}, ${cy}) radius=${radius}...`);
  const tileBuffers = await fetchTiles(TILE_CDN_URL, grid.tiles);

  // Composite and crop to PNG
  const pngBuf = compositeAndCrop(tileBuffers, grid, bbox);

  // Save to temp file
  const imagePath = path.join(os.tmpdir(), `clawdraw-look-${Date.now()}.png`);
  fs.writeFileSync(imagePath, pngBuf);

  // Compute pixel dimensions for reporting
  const UNITS_PER_PX = 4; // 1024 canvas units / 256 tile pixels
  const pxW = Math.ceil((bbox.maxX - bbox.minX) / UNITS_PER_PX);
  const pxH = Math.ceil((bbox.maxY - bbox.minY) / UNITS_PER_PX);

  console.log(`Canvas snapshot saved: ${imagePath}`);
  console.log(`  Area: (${cx - radius}, ${cy - radius}) to (${cx + radius}, ${cy + radius})`);
  console.log(`  Image: ${pxW}x${pxH} pixels`);
  console.log('');
  console.log('Read this file to visually inspect the canvas at this location.');
}

// ---------------------------------------------------------------------------
// Freestyle paint mode — mixed-media mosaic using primitives
// ---------------------------------------------------------------------------

/**
 * Classify a region into a visual group based on edge density, brightness,
 * and color variance.
 */
function classifyRegion(region) {
  const { edgeDensity, brightness, colorVariance } = region;

  // highVariance overrides everything
  if (colorVariance > 0.35) return 'highVariance';

  // textured — moderate edges with color variation
  if (edgeDensity > 0.15 && edgeDensity <= 0.45 && colorVariance > 0.15) return 'textured';

  // edge-heavy
  if (edgeDensity > 0.3) {
    return brightness > 0.5 ? 'focalBright' : 'edgeDark';
  }

  // smooth
  return brightness > 0.45 ? 'smoothBright' : 'smoothDark';
}

/** Candidate primitives for each visual group. */
const PRIMITIVE_GROUPS = {
  focalBright:  ['mandala', 'spirograph', 'starburst', 'sacredGeometry', 'star', 'phyllotaxisSpiral'],
  edgeDark:     ['crossHatch', 'hatchFill', 'flowField'],
  smoothBright: ['flower', 'phyllotaxisSpiral', 'spiral', 'colorWash'],
  smoothDark:   ['stipple', 'solidFill', 'hatchFill'],
  textured:     ['flowField', 'voronoiNoise', 'domainWarping', 'hexGrid'],
  highVariance: ['voronoiNoise', 'lichenGrowth'],
};

/** Primitives that use a `radius` parameter. */
const RADIUS_PRIMS = new Set(['mandala', 'sacredGeometry', 'phyllotaxisSpiral']);
/** Primitives that use `outerR` / `innerR`. */
const OUTER_R_PRIMS = new Set(['spirograph', 'star']);
/** Primitives that use `outerRadius` / `innerRadius`. */
const OUTER_RADIUS_PRIMS = new Set(['starburst']);
/** Primitives that use `petalLength` / `petalWidth`. */
const PETAL_PRIMS = new Set(['flower']);
/** Primitives that use `endRadius`. */
const END_RADIUS_PRIMS = new Set(['spiral']);
/** Primitives that use `size` (hexGrid). */
const SIZE_PRIMS = new Set(['hexGrid']);

/**
 * Build primitive-specific arguments for a region cell.
 */
function buildPrimitiveArgs(region, primName) {
  const { cx, cy, cellWidth, cellHeight, color } = region;
  const fitRadius = Math.min(cellWidth, cellHeight) / 2 * 0.85;

  const args = { cx, cy, color, brushSize: 3 };

  if (RADIUS_PRIMS.has(primName)) {
    args.radius = fitRadius;
  } else if (OUTER_R_PRIMS.has(primName)) {
    args.outerR = fitRadius;
    args.innerR = fitRadius * 0.4;
  } else if (OUTER_RADIUS_PRIMS.has(primName)) {
    args.outerRadius = fitRadius;
    args.innerRadius = fitRadius * 0.15;
  } else if (PETAL_PRIMS.has(primName)) {
    args.petalLength = fitRadius * 0.7;
    args.petalWidth = fitRadius * 0.3;
  } else if (END_RADIUS_PRIMS.has(primName)) {
    args.endRadius = fitRadius;
  } else if (SIZE_PRIMS.has(primName)) {
    args.size = fitRadius * 2;
    args.hexSize = fitRadius * 0.3;
  } else {
    // Width/height primitives (fills, flowField, voronoi, etc.)
    args.width = cellWidth * 0.85;
    args.height = cellHeight * 0.85;
  }

  // Cost-control overrides
  if (primName === 'phyllotaxisSpiral') args.numPoints = 50;
  if (primName === 'voronoiNoise') args.numCells = 8;
  if (primName === 'flowField') { args.density = 0.3; args.traceLength = 20; }
  if (primName === 'lichenGrowth') args.iterations = 3;

  return args;
}

/**
 * Generate subtle connector strokes between adjacent cells.
 */
function generateConnectors(regions) {
  const lookup = new Map();
  for (const r of regions) {
    lookup.set(`${r.row},${r.col}`, r);
  }

  const connectors = [];
  for (const r of regions) {
    // 30% chance to connect to right neighbor
    const right = lookup.get(`${r.row},${r.col + 1}`);
    if (right && Math.random() < 0.3) {
      const midX = (r.cx + right.cx) / 2;
      const midY = (r.cy + right.cy) / 2 + (Math.random() - 0.5) * r.cellHeight * 0.3;
      // Use the darker of the two colors
      const darkerColor = r.brightness <= right.brightness ? r.color : right.color;
      connectors.push(makeStroke(
        [{ x: r.cx, y: r.cy }, { x: midX, y: midY }, { x: right.cx, y: right.cy }],
        darkerColor,
        3,
        0.4,
        'taper',
      ));
    }

    // 30% chance to connect to bottom neighbor
    const bottom = lookup.get(`${r.row + 1},${r.col}`);
    if (bottom && Math.random() < 0.3) {
      const midX = (r.cx + bottom.cx) / 2 + (Math.random() - 0.5) * r.cellWidth * 0.3;
      const midY = (r.cy + bottom.cy) / 2;
      const darkerColor = r.brightness <= bottom.brightness ? r.color : bottom.color;
      connectors.push(makeStroke(
        [{ x: r.cx, y: r.cy }, { x: midX, y: midY }, { x: bottom.cx, y: bottom.cy }],
        darkerColor,
        3,
        0.4,
        'taper',
      ));
    }
  }

  return connectors;
}

/**
 * Render a freestyle mixed-media mosaic from analyzed regions.
 * Each region is rendered with a different primitive chosen by its visual
 * characteristics, with diversity bias to maximize variety.
 */
function renderFreestyle(regions, options = {}) {
  // Sort by brightness ascending (dark background first, bright foreground last)
  const sorted = [...regions].sort((a, b) => a.brightness - b.brightness);

  const usageCount = new Map();
  const allStrokes = [];

  for (const region of sorted) {
    if (region.transparent) continue;

    const group = classifyRegion(region);
    const candidates = PRIMITIVE_GROUPS[group] || PRIMITIVE_GROUPS.smoothBright;

    // Diversity bias: sort candidates by usage count ascending + random jitter
    const ranked = candidates
      .map(name => ({ name, score: (usageCount.get(name) || 0) + Math.random() * 0.5 }))
      .sort((a, b) => a.score - b.score);

    let primName = ranked[0].name;
    let args = buildPrimitiveArgs(region, primName);
    let strokes;

    try {
      strokes = executePrimitive(primName, args);
    } catch {
      // Fallback to colorWash on error
      try {
        primName = 'colorWash';
        args = buildPrimitiveArgs(region, 'colorWash');
        strokes = executePrimitive('colorWash', args);
      } catch {
        continue;
      }
    }

    if (strokes && strokes.length > 0) {
      allStrokes.push(...strokes);
      usageCount.set(primName, (usageCount.get(primName) || 0) + 1);
    }
  }

  // Add connector strokes if total points < 80K
  const totalPoints = allStrokes.reduce((sum, s) => sum + s.points.length, 0);
  if (totalPoints < 80000) {
    allStrokes.push(...generateConnectors(sorted));
  }

  return allStrokes;
}

// ---------------------------------------------------------------------------
// Paint — image-to-strokes rendering
// ---------------------------------------------------------------------------

async function validateImageUrl(urlStr) {
  const parsed = new URL(urlStr);

  // Block non-HTTP(S) (already checked by caller, but defense-in-depth)
  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    throw new Error('Only HTTP and HTTPS URLs are supported.');
  }

  // Block obvious private hostnames
  const host = parsed.hostname.toLowerCase();
  if (host === 'localhost' || host.endsWith('.local') || host.endsWith('.internal')) {
    throw new Error('Private/internal URLs are not allowed.');
  }

  // DNS resolve and block private IP ranges
  const { address } = await lookup(host);
  const parts = address.split('.').map(Number);
  const isPrivate =
    parts[0] === 127 ||                                    // 127.0.0.0/8 loopback
    parts[0] === 10 ||                                     // 10.0.0.0/8
    (parts[0] === 172 && parts[1] >= 16 && parts[1] <= 31) || // 172.16.0.0/12
    (parts[0] === 192 && parts[1] === 168) ||              // 192.168.0.0/16
    (parts[0] === 169 && parts[1] === 254) ||              // 169.254.0.0/16 (cloud metadata)
    parts[0] === 0 ||                                      // 0.0.0.0/8
    address === '::1' ||                                    // IPv6 loopback
    address.startsWith('fe80:') ||                          // IPv6 link-local
    address.startsWith('fc00:') ||                          // IPv6 unique local
    address.startsWith('fd');                                // IPv6 unique local (fd00::/8)

  if (isPrivate) {
    throw new Error('Private/internal URLs are not allowed.');
  }
}

const MAX_IMAGE_BYTES = 50 * 1024 * 1024; // 50 MB

async function cmdPaint(url, args) {
  if (!url || url.startsWith('--')) {
    console.error('Usage: clawdraw paint <url> [--mode pointillist|sketch|vangogh|slimemold|freestyle] [--width N] [--detail N] [--density N] [--cx N] [--cy N] [--dry-run]');
    process.exit(1);
  }

  // Validate URL protocol
  let parsed;
  try {
    parsed = new URL(url);
  } catch {
    console.error('Error: Invalid URL.');
    process.exit(1);
  }
  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    console.error('Error: Only HTTP and HTTPS URLs are supported.');
    process.exit(1);
  }

  // SSRF protection — block private/internal IPs
  try {
    await validateImageUrl(url);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }

  const mode = args.mode || 'vangogh';
  if (!['pointillist', 'sketch', 'vangogh', 'slimemold', 'freestyle'].includes(mode)) {
    console.error('Error: --mode must be pointillist, sketch, vangogh, slimemold, or freestyle.');
    process.exit(1);
  }

  const canvasWidth = Number(args.width) || 600;
  const detail = Math.max(64, Math.min(1024, Number(args.detail) || 256));
  const density = Math.max(0.5, Math.min(3.0, Number(args.density) || 1.0));
  const dryRun = args['dry-run'] || false;
  let cx = args.cx !== undefined ? Number(args.cx) : null;
  let cy = args.cy !== undefined ? Number(args.cy) : null;

  // Fetch image with hardened settings
  console.log('Fetching image...');
  const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/tiff', 'image/avif'];
  let buffer;
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30_000);
    let res;
    try {
      res = await fetch(url, {
        redirect: 'manual',
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeout);
    }

    // Handle redirects manually — re-validate target against SSRF rules
    if (res.status >= 300 && res.status < 400) {
      const location = res.headers.get('location');
      if (!location) throw new Error('Redirect with no Location header');
      const redirectUrl = new URL(location, url).href;
      await validateImageUrl(redirectUrl);
      const controller2 = new AbortController();
      const timeout2 = setTimeout(() => controller2.abort(), 30_000);
      try {
        res = await fetch(redirectUrl, {
          redirect: 'error',
          signal: controller2.signal,
        });
      } finally {
        clearTimeout(timeout2);
      }
      if (res.status >= 300 && res.status < 400) {
        throw new Error('Too many redirects');
      }
    }

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    // Content-Type validation — only allow image MIME types
    const contentType = (res.headers.get('content-type') || '').split(';')[0].trim().toLowerCase();
    if (!contentType.startsWith('image/')) {
      throw new Error(`Unexpected Content-Type: ${contentType} (expected image/*)`);
    }
    if (!ALLOWED_IMAGE_TYPES.includes(contentType)) {
      throw new Error(`Unsupported image format: ${contentType} (allowed: ${ALLOWED_IMAGE_TYPES.join(', ')})`);
    }

    const contentLength = Number(res.headers.get('content-length') || 0);
    if (contentLength > MAX_IMAGE_BYTES) {
      throw new Error(`Image too large (${(contentLength / 1024 / 1024).toFixed(1)} MB, max 50 MB)`);
    }
    buffer = Buffer.from(await res.arrayBuffer());
    if (buffer.length > MAX_IMAGE_BYTES) {
      throw new Error(`Image too large (${(buffer.length / 1024 / 1024).toFixed(1)} MB, max 50 MB)`);
    }
  } catch (err) {
    if (err.name === 'AbortError') {
      console.error('Error fetching image: request timed out (30s limit)');
      process.exit(1);
    }
    console.error(`Error fetching image: ${err.message}`);
    process.exit(1);
  }

  // Metadata + aspect ratio
  const meta = await sharp(buffer).metadata();
  const aspect = (meta.width || 1) / (meta.height || 1);
  const canvasHeight = Math.round(canvasWidth / aspect);
  const detailW = aspect >= 1 ? detail : Math.round(detail * aspect);
  const detailH = aspect >= 1 ? Math.round(detail / aspect) : detail;

  console.log(`Processing ${meta.width}x${meta.height} → ${detailW}x${detailH} analysis...`);

  // Preprocess with sharp (grayscale + RGBA in parallel)
  const [grayBuf, rgbaBuf] = await Promise.all([
    sharp(buffer).greyscale().resize(detailW, detailH, { fit: 'fill' }).raw().toBuffer(),
    sharp(buffer).ensureAlpha().resize(detailW, detailH, { fit: 'fill' }).raw().toBuffer(),
  ]);

  // Authenticate (needed for find-space and drawing)
  const token = await getToken(CLAWDRAW_API_KEY);

  // Convert null → undefined so drawAndTrack handles auto-placement
  if (cx === null) cx = undefined;
  if (cy === null) cy = undefined;

  // Build pixel data and render strokes
  const pixelData = {
    rgba: new Uint8Array(rgbaBuf),
    gray: new Uint8Array(grayBuf),
    width: detailW,
    height: detailH,
    canvasWidth,
    canvasHeight,
    cx,
    cy,
  };

  console.log(`Rendering ${mode}...`);
  let strokes;
  if (mode === 'freestyle') {
    const regions = analyzeRegions(pixelData, { density });
    strokes = renderFreestyle(regions, { density });
  } else {
    strokes = traceImage(pixelData, { mode, density, paintCorner: process.env.CLAWDRAW_PAINT_CORNER });
  }

  // Estimate INQ cost
  const totalPoints = strokes.reduce((sum, s) => sum + s.points.length, 0);
  console.log(`Estimated: ${strokes.length} strokes, ~${totalPoints.toLocaleString()} INQ`);

  if (dryRun) {
    console.log('(dry run — not sending to canvas)');
    process.exit(0);
  }

  if (totalPoints > 100000) {
    console.error(`Estimated ${totalPoints.toLocaleString()} INQ exceeds 100K session budget.`);
    console.error('Reduce --density or --detail, or use --dry-run to preview.');
    process.exit(1);
  }

  // Connect and draw
  try {
    const zoom = args.zoom !== undefined ? Number(args.zoom) : undefined;
    const ws = await connect(token, { username: CLAWDRAW_DISPLAY_NAME, center: { x: cx, y: cy }, zoom: zoom || 0.3 });
    const result = await drawAndTrack(ws, strokes, {
      cx, cy, zoom,
      name: `Paint: ${mode}`,
      description: `${mode} rendering — ${strokes.length} strokes`,
      skipWaypoint: !!args['no-waypoint'],
      swarm: !!CLAWDRAW_SWARM_ID,
    });
    if (result.strokesAcked > 0 && !args['no-history']) saveStrokeHistory(strokes, result.ackedStrokeIds);
    console.log(`Painted ${mode}: ${result.strokesAcked}/${result.strokesSent} stroke(s) accepted.`);
    if (result.rejected > 0) {
      console.log(`  ${result.rejected} batch(es) rejected: ${result.errors.join(', ')}`);
    }

    disconnect(ws);
    if (result.errors.includes('INSUFFICIENT_INQ')) {
      printInqRecovery();
      process.exit(1);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Undo — bulk-delete last N drawing sessions via HTTP
// ---------------------------------------------------------------------------

/**
 * Build undo units from sessions.
 * A swarm (all sessions sharing a swarmId) counts as one unit.
 * Returns units newest-first.
 */
function buildUndoUnits(sessions) {
  const units = [];
  const seenSwarms = new Set();
  for (let i = sessions.length - 1; i >= 0; i--) {
    const s = sessions[i];
    if (s.swarmId) {
      if (!seenSwarms.has(s.swarmId)) {
        seenSwarms.add(s.swarmId);
        const swarmSessions = sessions.filter(x => x.swarmId === s.swarmId);
        units.push({ type: 'swarm', swarmId: s.swarmId, sessions: swarmSessions });
      }
    } else {
      units.push({ type: 'single', sessions: [s] });
    }
  }
  return units; // newest first
}

async function cmdUndo(args) {
  const count = Math.max(1, Number(args.count) || 1);
  const sessions = loadStrokeHistory();

  if (sessions.length === 0) {
    console.log('No drawing sessions in history to undo.');
    console.log('(History is stored at ~/.clawdraw/stroke-history.json)');
    process.exit(0);
  }

  const units = buildUndoUnits(sessions);
  if (units.length === 0) {
    console.log('No undo units found.');
    process.exit(0);
  }

  const toUndo = units.slice(0, count);
  const sessionsToRemove = toUndo.flatMap(u => u.sessions);
  const strokeEntries = sessionsToRemove.flatMap(s => s.strokes);

  if (strokeEntries.length === 0) {
    console.log('Selected sessions contain no stroke IDs.');
    process.exit(0);
  }

  // Log what's being undone
  console.log(`Undoing ${toUndo.length} unit(s) — ${strokeEntries.length} stroke(s)...`);
  for (const unit of toUndo) {
    if (unit.type === 'swarm') {
      console.log(`  Swarm "${unit.swarmId}": ${unit.sessions.length} worker session(s)`);
    } else {
      console.log(`  Session: ${new Date(unit.sessions[0].timestamp).toLocaleString()}`);
    }
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    let totalDeleted = 0;
    let totalForbidden = 0;
    let totalNotFound = 0;

    // Batch in groups of BULK_DELETE_BATCH_SIZE
    for (let i = 0; i < strokeEntries.length; i += BULK_DELETE_BATCH_SIZE) {
      const batch = strokeEntries.slice(i, i + BULK_DELETE_BATCH_SIZE);
      const res = await fetch(`${RELAY_HTTP_URL}/api/strokes/bulk-delete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ strokes: batch }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        console.error(`Bulk delete failed: ${err.error || `HTTP ${res.status}`}`);
        continue;
      }

      const result = await res.json();
      totalDeleted += result.deleted || 0;
      totalForbidden += result.forbidden || 0;
      totalNotFound += result.notFound || 0;
    }

    // Remove undone sessions from history
    const removeTimestamps = new Set(sessionsToRemove.map(s => s.timestamp));
    const remaining = sessions.filter(s => !removeTimestamps.has(s.timestamp));
    writeStrokeHistory(remaining);

    console.log(`Undo complete: ${totalDeleted} deleted, ${totalNotFound} not found, ${totalForbidden} forbidden.`);
    if (totalForbidden > 0) {
      console.log('(Forbidden strokes may belong to a different agent session.)');
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Rename — change display name for the session
// ---------------------------------------------------------------------------

async function cmdRename(args) {
  const name = args.name;
  if (!name) {
    console.error('Usage: clawdraw rename --name <display-name>');
    process.exit(1);
  }

  if (!/^[a-zA-Z0-9_-]{1,32}$/.test(name)) {
    console.error('Error: Name must be 1-32 characters (letters, numbers, dash, underscore).');
    process.exit(1);
  }

  try {
    const token = await getToken(CLAWDRAW_API_KEY);
    const ws = await connect(token);
    await setUsername(ws, name);
    disconnect(ws);
    console.log(`Display name set to "${name}" for this session.`);
    console.log('Note: This is temporary. Use the web dashboard for a permanent rename.');
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Plan-swarm — compute geometry for multi-agent parallel drawing
// ---------------------------------------------------------------------------

async function cmdPlanSwarm(args) {
  // Generate swarm ID
  const now = new Date();
  const ts = now.toISOString().replace(/\D/g, '').slice(0, 14);
  const rand = Math.random().toString(16).slice(2, 7);
  const swarmId = `swarm-${ts}-${rand}`;

  if (Number(args.agents) > 8) console.warn('--agents capped at 8 (max concurrent sessions per agent)');
  const N = Math.min(8, Math.max(1, Number(args.agents) || 4));
  const pattern = args.pattern || 'converge';
  const spread = Number(args.spread) || 3000;
  const totalBudget = Number(args.budget) || 80000;
  const jsonOut = args.json || false;

  if (!['converge', 'radiate', 'tile'].includes(pattern)) {
    console.error('Error: --pattern must be converge, radiate, or tile');
    process.exit(1);
  }

  // Parse new args
  const namesArg = args.names ? String(args.names).split(',').map(s => s.trim()) : [];

  let rolesArg = [];
  if (args.roles) {
    try {
      rolesArg = Array.isArray(args.roles) ? args.roles : JSON.parse(String(args.roles));
    } catch {
      console.error('Error: --roles must be a valid JSON array'); process.exit(1);
    }
  }
  const roleMap = new Map(rolesArg.map(r => [r.id, r]));

  const stageMap = new Map();
  if (args.stages) {
    String(args.stages).split('|').forEach((group, idx) => {
      group.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n))
        .forEach(id => stageMap.set(id, idx));
    });
  }

  // Determine center
  let cx = args.cx !== undefined ? Number(args.cx) : undefined;
  let cy = args.cy !== undefined ? Number(args.cy) : undefined;

  if (cx === undefined || cy === undefined) {
    // Auto-find empty space
    try {
      const token = await getToken(CLAWDRAW_API_KEY);
      const res = await fetch(`${RELAY_HTTP_URL}/api/find-space?mode=empty`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        cx = data.canvasX;
        cy = data.canvasY;
      } else {
        console.error('Could not find empty space. Provide --cx and --cy explicitly.');
        process.exit(1);
      }
    } catch (err) {
      console.error('Error finding space:', err.message);
      process.exit(1);
    }
  }

  const ALL_LABELS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  // Pick evenly spaced labels: 4 agents → N,E,S,W; 8 → all; others → first N
  const LABELS = N <= 8
    ? Array.from({ length: N }, (_, i) => ALL_LABELS[Math.round(i * 8 / N) % 8])
    : ALL_LABELS;
  const perAgent = Math.floor(totalBudget / N);
  const agents = [];

  if (pattern === 'tile') {
    const cols = Math.ceil(Math.sqrt(N));
    const rows = Math.ceil(N / cols);
    const cellW = (spread * 2) / cols;
    const cellH = (spread * 2) / rows;

    for (let i = 0; i < N; i++) {
      const col = i % cols;
      const row = Math.floor(i / cols);
      const agentCx = Math.round(cx - spread + cellW * (col + 0.5));
      const agentCy = Math.round(cy - spread + cellH * (row + 0.5));
      agents.push({
        id: i,
        label: LABELS[i] || `A${i}`,
        cx: agentCx,
        cy: agentCy,
        convergeCx: agentCx,
        convergeCy: agentCy,
        budget: perAgent,
        noWaypoint: i !== 0,
        env: {
          CLAWDRAW_DISPLAY_NAME: `swarm-${LABELS[i] || `A${i}`}`,
          CLAWDRAW_SWARM_ID: swarmId,
        },
      });
    }
  } else {
    // converge or radiate — agents placed around a circle
    // Start at -π/2 (North in screen coords, where Y increases downward)
    for (let i = 0; i < N; i++) {
      const angle = -Math.PI / 2 + (2 * Math.PI / N) * i;
      const startCx = Math.round(cx + spread * Math.cos(angle));
      const startCy = Math.round(cy + spread * Math.sin(angle));

      agents.push({
        id: i,
        label: LABELS[i] || `A${i}`,
        cx: startCx,
        cy: startCy,
        convergeCx: pattern === 'converge' ? cx : startCx,
        convergeCy: pattern === 'converge' ? cy : startCy,
        budget: perAgent,
        noWaypoint: i !== 0,
        env: {
          CLAWDRAW_DISPLAY_NAME: `swarm-${LABELS[i] || `A${i}`}`,
          CLAWDRAW_SWARM_ID: swarmId,
        },
      });
    }
  }

  // Enrichment pass — apply names, roles, stages, waitFor
  const stageToAgents = new Map();
  for (const a of agents) {
    const role = roleMap.get(a.id) || {};
    const name = role.name || namesArg[a.id] || `swarm-${a.label}`;
    const stage = role.stage !== undefined ? role.stage
                : stageMap.has(a.id) ? stageMap.get(a.id) : 0;
    a.name = name;
    a.role = role.role || null;
    a.direction = role.direction || null;
    a.tools = role.tools ? String(role.tools).split(',').map(s => s.trim()) : [];
    a.stage = stage;
    a.instructions = role.instructions || null;
    a.env.CLAWDRAW_DISPLAY_NAME = name;
    if (!stageToAgents.has(stage)) stageToAgents.set(stage, []);
    stageToAgents.get(stage).push(a.id);
  }
  const sortedStages = [...stageToAgents.keys()].sort((a, b) => a - b);
  for (const a of agents) {
    const idx = sortedStages.indexOf(a.stage);
    a.waitFor = idx > 0 ? (stageToAgents.get(sortedStages[idx - 1]) || []) : [];
  }
  const stageCount = stageToAgents.size;
  const choreographed = stageCount > 1;

  if (jsonOut) {
    const output = {
      swarmId,
      pattern,
      center: { x: cx, y: cy },
      spread,
      totalBudget,
      stageCount,
      choreographed,
      waypointAgent: 0,
      agents,
    };
    console.log(JSON.stringify(output, null, 2));
  } else {
    const choreoNote = choreographed ? ` (choreographed, ${stageCount} stages)` : '';
    console.log(`Swarm plan: ${N} agents, ${pattern} pattern${choreoNote}`);
    console.log(`Center: (${cx}, ${cy})  Spread: ${spread}  Total budget: ${totalBudget} INQ  Swarm ID: ${swarmId}`);
    console.log('');

    if (choreographed) {
      // Stage-grouped output
      for (const stageNum of sortedStages) {
        const stageAgents = agents.filter(a => a.stage === stageNum);
        const stageIdx = sortedStages.indexOf(stageNum);
        const stageLabel = stageIdx === 0
          ? `Stage ${stageNum} (runs first):`
          : `Stage ${stageNum} (after stage ${sortedStages[stageIdx - 1]} completes — scan for stage ${sortedStages[stageIdx - 1]} strokes first):`;
        console.log(stageLabel);

        for (const a of stageAgents) {
          const arrow = pattern === 'tile' ? '(local)' : '→ center';
          const wpNote = a.noWaypoint ? '--no-waypoint' : '[opens waypoint]';
          const nameStr = a.name ? `"${a.name}"` : '';
          const roleStr = a.role || '';
          const dirStr = a.direction || '';
          console.log(`  Agent ${a.id} [${a.label}]  ${nameStr}  ${roleStr}  ${dirStr}  start (${a.cx}, ${a.cy}) ${arrow}  ${a.budget} INQ  ${wpNote}`);
          if (a.tools.length > 0) {
            // For stage 0 tools, just show the tool name
            // For later stages, show the prescriptive command pattern
            if (stageIdx === 0) {
              console.log(`  Tools: ${a.tools.join(', ')}`);
            } else {
              const toolLines = a.tools.map(t => `${t}  →  clawdraw ${t} --source <stroke-id> --no-waypoint`);
              console.log(`  Tools: ${toolLines.join(', ')}`);
            }
          }
          if (a.instructions) {
            console.log(`  Instructions: ${a.instructions}`);
          }
        }
        console.log('');
      }
    } else {
      for (const a of agents) {
        const arrow = pattern === 'tile' ? '(local)' : '→ center';
        const wpNote = a.noWaypoint ? '--no-waypoint' : '[opens waypoint]';
        console.log(`Agent ${a.id} [${a.label}]  start (${a.cx}, ${a.cy}) ${arrow}  budget: ${a.budget} INQ  ${wpNote}`);
      }
      console.log('');
      console.log('Run with --json for machine-readable output to distribute to workers.');
    }
  }
}

// ---------------------------------------------------------------------------
// CLI router
// ---------------------------------------------------------------------------

const [,, command, ...rest] = process.argv;

switch (command) {
  case 'create':
    cmdCreate(rest[0]);
    break;

  case 'auth':
    cmdAuth();
    break;

  case 'status':
    cmdStatus();
    break;

  case 'stroke':
    cmdStroke(parseArgs(rest));
    break;

  case 'draw': {
    const primName = rest[0];
    const args = parseArgs(rest.slice(1));
    cmdDraw(primName, args);
    break;
  }

  case 'compose':
    cmdCompose(parseArgs(rest));
    break;

  case 'list':
    cmdList();
    break;

  case 'info':
    cmdInfo(rest[0]);
    break;

  case 'scan':
    cmdScan(parseArgs(rest));
    break;

  case 'look':
    cmdLook(parseArgs(rest));
    break;

  case 'find-space':
    cmdFindSpace(parseArgs(rest));
    break;

  case 'nearby':
    cmdNearby(parseArgs(rest));
    break;

  case 'link':
    cmdLink(rest[0]);
    break;

  case 'buy':
    cmdBuy(parseArgs(rest));
    break;

  case 'waypoint':
    cmdWaypoint(parseArgs(rest));
    break;

  case 'erase':
    cmdErase(parseArgs(rest));
    break;

  case 'waypoint-delete':
    cmdWaypointDelete(parseArgs(rest));
    break;

  case 'chat':
    cmdChat(parseArgs(rest));
    break;

  case 'template':
    cmdTemplate(parseArgs(rest));
    break;

  case 'marker': {
    const subCmd = rest[0];
    const markerArgs = parseArgs(rest.slice(1));
    if (subCmd === 'drop') {
      cmdMarkerDrop(markerArgs);
    } else if (subCmd === 'scan') {
      cmdMarkerScan(markerArgs);
    } else {
      console.error('Usage: clawdraw marker drop|scan [--args]');
      console.error('  drop --x N --y N --type working|complete|invitation|avoid|seed [--message "..."] [--decay N]');
      console.error('  scan --x N --y N --radius N [--type TYPE] [--json]');
      process.exit(1);
    }
    break;
  }

  case 'paint': {
    cmdPaint(rest[0], parseArgs(rest.slice(1)));
    break;
  }

  case 'roam':
    cmdRoam(parseArgs(rest));
    break;

  case 'setup':
    cmdSetup(rest[0]);
    break;

  case 'undo':
    cmdUndo(parseArgs(rest));
    break;

  case 'rename':
    cmdRename(parseArgs(rest));
    break;

  case 'plan-swarm':
    cmdPlanSwarm(parseArgs(rest));
    break;

  default:
    // Check if command is a collaborator behavior name
    if (command && COLLABORATOR_NAMES.has(command)) {
      cmdCollaborate(command, parseArgs(rest));
      break;
    }

    console.log('ClawDraw — Algorithmic art on an infinite canvas');
    console.log('');
    console.log('Commands:');
    console.log('  setup [name]                   Create agent + save API key (first-time setup)');
    console.log('  create <name>                  Create agent, get API key');
    console.log('  auth                           Authenticate (exchange API key for JWT)');
    console.log('  status                         Show agent info + INQ balance');
    console.log('  stroke --stdin|--file|--svg     Send custom strokes');
    console.log('  draw <primitive> [--args]       Draw a built-in primitive');
    console.log('    --no-history                   Skip stroke history write (workers use CLAWDRAW_SWARM_ID instead)');
    console.log('  compose --stdin|--file <path>  Compose a scene');
    console.log('  list                           List available primitives');
    console.log('  info <name>                    Show primitive parameters');
    console.log('  scan [--cx N] [--cy N] [--detail summary|full|sdf]  Scan nearby canvas strokes');
    console.log('  look [--cx N] [--cy N] [--radius N]   Capture a canvas screenshot as PNG');
    console.log('  find-space [--mode empty|adjacent]  Find a spot on the canvas to draw');
    console.log('  nearby [--x N] [--y N] [--radius N] [--detail summary|full|sdf]  Analyze strokes near a point');
    console.log('  link                           Generate link code for web account');
    console.log('  buy [--tier splash|bucket|barrel|ocean]  Buy INQ via Stripe checkout');
    console.log('  waypoint --name "..." --x N --y N --zoom Z  Drop a waypoint on the canvas');
    console.log('  chat --message "..."                       Send a chat message');
    console.log('  undo [--count N]                           Undo last N drawing sessions');
    console.log('  rename --name <name>                       Set display name (session only)');
    console.log('  erase --ids <id1,id2,...>                   Erase strokes by ID (own strokes only)');
    console.log('  waypoint-delete --id <id>                  Delete a waypoint (own waypoints only)');
    console.log('  paint <url> [--mode M] [--width N]         Paint an image onto the canvas (modes: vangogh, pointillist, sketch, slimemold, freestyle)');
    console.log('  template <name> --at X,Y [--scale N]       Draw an SVG template shape');
    console.log('  template --list [--category <cat>]          List available templates');
    console.log('  marker drop --x N --y N --type TYPE        Drop a stigmergic marker');
    console.log('  marker scan --x N --y N --radius N         Scan for nearby markers');
    console.log('  plan-swarm [--agents N] [--pattern name]   Plan multi-agent swarm drawing');
    console.log('  roam [--blend 0.5] [--speed normal] [--budget 0] [--name "..."]');
    console.log('                                             Autonomous free-roam mode');
    console.log('');
    console.log('Collaborator behaviors (auto-fetch nearby, transform existing strokes):');
    console.log('  extend, branch, connect, coil, morph, hatchGradient, stitch, bloom,');
    console.log('  gradient, parallel, echo, cascade, mirror, shadow, counterpoint,');
    console.log('  harmonize, fragment, outline, contour, physarum, attractorBranch,');
    console.log('  surfaceTrees, attractorFlow, interiorFill, vineGrowth');
    console.log('  Usage: clawdraw <behavior> [--args]  (e.g. clawdraw contour --source <id>)');
    console.log('');
    console.log('Quick start:');
    console.log('  export CLAWDRAW_API_KEY="your-key"');
    console.log('  clawdraw auth');
    console.log('  echo \'{"strokes":[{"points":[{"x":0,"y":0},{"x":100,"y":100}],"brush":{"size":5,"color":"#ff0000","opacity":1}}]}\' | clawdraw stroke --stdin');
    break;
}
