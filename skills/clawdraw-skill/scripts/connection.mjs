#!/usr/bin/env node
/**
 * WebSocket connection manager for sending strokes to the ClawDraw relay.
 *
 * Usage:
 *   import { connect, sendStrokes, addWaypoint, getWaypointUrl, deleteStroke, deleteWaypoint, disconnect } from './connection.mjs';
 *
 *   const ws = await connect(token);
 *   const result = await sendStrokes(ws, strokes);
 *   console.log(`${result.strokesAcked}/${result.strokesSent} accepted`);
 *   const wp = await addWaypoint(ws, { name: 'My Spot', x: 0, y: 0, zoom: 1 });
 *   console.log(getWaypointUrl(wp));
 *   disconnect(ws);
 */

// @security-manifest
// env: none (receives token from auth.mjs)
// endpoints: relay.clawdraw.ai (WSS, HTTPS)
// files: none
// exec: none

import WebSocket from 'ws';
import open from 'open';
import { computeBoundingBox, captureSnapshot } from './snapshot.mjs';

const WS_URL = 'wss://relay.clawdraw.ai/ws';
const RELAY_HTTP_URL = 'https://relay.clawdraw.ai';

/**
 * Open a URL in the user's default browser. Fire-and-forget.
 * @param {string} url
 */
function openInBrowser(url) {
  open(url).catch(() => {});  // silently fail in restricted environments
}

const TILE_CDN_URL = 'https://relay.clawdraw.ai/tiles';

// ---------------------------------------------------------------------------
// tile.updated listener registry (used by snapshot.mjs)
// ---------------------------------------------------------------------------

/** @type {Map<WebSocket, Set<Function>>} */
const _tileUpdateListeners = new Map();

/**
 * Register a callback for tile.updated messages on a WebSocket.
 *
 * @param {WebSocket} ws
 * @param {(msg: {x:number, y:number, z:number, version:number}) => void} callback
 */
export function onTileUpdate(ws, callback) {
  let set = _tileUpdateListeners.get(ws);
  if (!set) {
    set = new Set();
    _tileUpdateListeners.set(ws, set);
  }
  set.add(callback);
}

/**
 * Unregister a tile.updated callback.
 *
 * @param {WebSocket} ws
 * @param {Function} callback
 */
export function offTileUpdate(ws, callback) {
  const set = _tileUpdateListeners.get(ws);
  if (set) {
    set.delete(callback);
    if (set.size === 0) _tileUpdateListeners.delete(ws);
  }
}

/** Dispatch a tile.updated message to registered listeners. */
function _dispatchTileUpdate(ws, msg) {
  const set = _tileUpdateListeners.get(ws);
  if (set) {
    for (const cb of set) {
      try { cb(msg); } catch { /* ignore listener errors */ }
    }
  }
}

const MAX_RETRIES = 5;
const BASE_DELAY_MS = 1000;

/**
 * Connect to the relay WebSocket with auth token.
 * Sends an initial viewport.update on open.
 *
 * @param {string} token - JWT from auth.mjs getToken()
 * @param {object} [opts]
 * @param {string} [opts.username] - Bot display name
 * @param {{ x: number, y: number }} [opts.center] - Viewport center
 * @param {number} [opts.zoom] - Viewport zoom
 * @returns {Promise<WebSocket>}
 */
export function connect(token, opts = {}) {
  const username = opts.username || 'openclaw-bot';
  const center = opts.center || { x: 0, y: 0 };
  const zoom = opts.zoom || 0.2;

  return new Promise((resolve, reject) => {
    const ws = new WebSocket(WS_URL, {
      headers: { Authorization: `Bearer ${token}` },
    });

    ws.on('open', () => {
      // Send initial viewport so the relay knows where we are
      ws._currentViewport = {
        type: 'viewport.update',
        viewport: {
          center,
          zoom,
          size: { width: 6000, height: 6000 },
        },
        cursor: center,
        username,
      };
      ws.send(JSON.stringify(ws._currentViewport));
      ws._clawdrawUsername = username;
      ws._authToken = token;

      // Re-send presence every 30s to prevent 60s eviction timeout
      ws._presenceHeartbeat = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(ws._currentViewport));
        }
      }, 30000);

      // Persistent message handler for tile.updated dispatch
      ws.on('message', (data) => {
        try {
          const parsed = JSON.parse(data.toString());
          const msgs = Array.isArray(parsed) ? parsed : [parsed];
          for (const msg of msgs) {
            if (msg.type === 'tile.updated') {
              _dispatchTileUpdate(ws, msg);
            }
          }
        } catch { /* ignore non-JSON frames */ }
      });

      // Wait for chunks.initial before resolving — strokes sent before
      // subscription completes get rejected with REGION_FULL / chunk.full.
      const subTimeout = setTimeout(() => {
        ws.removeListener('message', onChunksInitial);
        console.warn('[connection] chunks.initial not received within 5s, resolving anyway');
        resolve(ws);
      }, 5000);

      function onChunksInitial(data) {
        try {
          const parsed = JSON.parse(data.toString());
          const msgs = Array.isArray(parsed) ? parsed : [parsed];
          for (const msg of msgs) {
            if (msg.type === 'chunks.initial') {
              clearTimeout(subTimeout);
              ws.removeListener('message', onChunksInitial);
              resolve(ws);
              return;
            }
          }
        } catch { /* ignore non-JSON frames */ }
      }

      ws.on('message', onChunksInitial);
    });

    ws.on('error', (err) => {
      reject(new Error(`WebSocket connection failed: ${err.message}`));
    });

    // If it closes before opening, reject
    ws.on('close', (code) => {
      if (ws.readyState !== WebSocket.OPEN) {
        reject(new Error(`WebSocket closed before open (code ${code})`));
      }
    });
  });
}

/** Default strokes per batch message (used when no adaptive pacing). */
export const BATCH_SIZE = 100;

/** Ideal batch size for smooth cursor animation on the viewer side. */
const ANIM_BATCH_SIZE = 2;
/** Ideal inter-batch delay (ms) for smooth animation. */
const ANIM_DELAY_MS = 100;
/** Maximum wall-clock seconds for the entire send. Large stroke counts
 *  auto-scale batch size upward to stay within this cap. */
const MAX_DRAW_SECONDS = 20;

/** Max retries per batch on RATE_LIMITED. */
const BATCH_MAX_RETRIES = 5;
/** Base backoff delay (ms) for rate-limit retries. */
const RATE_LIMIT_BASE_MS = 200;
/** Timeout (ms) waiting for ack/error per batch. */
const BATCH_ACK_TIMEOUT_MS = 5000;

/**
 * @typedef {Object} SendResult
 * @property {number} sent       - Batches transmitted
 * @property {number} acked      - Batches acknowledged by server
 * @property {number} rejected   - Batches rejected (after all retries exhausted)
 * @property {string[]} errors   - Error codes/messages for rejected batches
 * @property {number} strokesSent  - Total individual strokes transmitted
 * @property {number} strokesAcked - Total individual strokes acknowledged
 */

/**
 * Wait for a single ack or sync.error from the relay.
 * Resolves with { type: 'ack' } on stroke.ack/strokes.ack,
 * { type: 'error', code, message } on sync.error,
 * or { type: 'timeout' } after BATCH_ACK_TIMEOUT_MS.
 *
 * @param {WebSocket} ws
 * @returns {Promise<{type: string, code?: string, message?: string}>}
 */
function waitForBatchResponse(ws) {
  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      ws.removeListener('message', handler);
      resolve({ type: 'timeout' });
    }, BATCH_ACK_TIMEOUT_MS);

    function handler(data) {
      try {
        const parsed = JSON.parse(data.toString());
        const msgs = Array.isArray(parsed) ? parsed : [parsed];
        for (const msg of msgs) {
          if (msg.type === 'stroke.ack' || msg.type === 'strokes.ack') {
            clearTimeout(timeout);
            ws.removeListener('message', handler);
            resolve({ type: 'ack' });
            return;
          }
          if (msg.type === 'sync.error') {
            clearTimeout(timeout);
            ws.removeListener('message', handler);
            resolve({ type: 'error', code: msg.code || 'UNKNOWN', message: msg.message || '' });
            return;
          }
        }
      } catch { /* ignore non-JSON frames */ }
    }

    ws.on('message', handler);
  });
}

/**
 * Send an array of strokes to the relay, batched for efficiency.
 * Always waits for ack/error per batch. On RATE_LIMITED, retries with
 * exponential backoff. On INSUFFICIENT_INQ, stops immediately.
 *
 * By default, strokes are paced for animated viewing (small batches with
 * inter-batch delay so the web client's cursor-tracing animation can play).
 * Large stroke counts auto-scale batch size upward to keep total draw time
 * within MAX_DRAW_SECONDS (20s).
 *
 * @param {WebSocket} ws - Connected WebSocket
 * @param {Array} strokes - Array of stroke objects (from helpers.mjs makeStroke)
 * @param {object|number} [optsOrDelay={}] - Options object or legacy delayMs number
 * @param {number} [optsOrDelay.delayMs] - Milliseconds between successful batch sends (auto-computed if omitted)
 * @param {number} [optsOrDelay.batchSize] - Max strokes per batch (auto-computed if omitted)
 * @param {boolean} [optsOrDelay.legacy=false] - Use single stroke.add per stroke
 * @returns {Promise<SendResult>}
 */
export async function sendStrokes(ws, strokes, optsOrDelay = {}) {
  // Support legacy call signature: sendStrokes(ws, strokes, 50)
  const opts = typeof optsOrDelay === 'number'
    ? { delayMs: optsOrDelay }
    : optsOrDelay;

  const legacy = opts.legacy ?? false;

  // Auto-compute pacing for animated drawing when not explicitly set.
  // Ideal: batchSize=2, delay=100ms for smooth cursor animation.
  // If that would exceed MAX_DRAW_SECONDS, scale batch size up to fit.
  let batchSize, delayMs;
  if (opts.batchSize !== undefined || opts.delayMs !== undefined) {
    // Explicit values — use as-is
    batchSize = opts.batchSize ?? BATCH_SIZE;
    delayMs = opts.delayMs ?? 50;
  } else {
    // Auto-compute: start with ideal animation pacing
    const idealBatches = Math.ceil(strokes.length / ANIM_BATCH_SIZE);
    const idealTimeMs = idealBatches * ANIM_DELAY_MS;
    const capMs = MAX_DRAW_SECONDS * 1000;

    if (idealTimeMs <= capMs) {
      // Fits within cap — use ideal pacing
      batchSize = ANIM_BATCH_SIZE;
      delayMs = ANIM_DELAY_MS;
    } else {
      // Too many strokes — scale up batch size, keep delay constant
      const maxBatches = Math.floor(capMs / ANIM_DELAY_MS);
      batchSize = Math.ceil(strokes.length / maxBatches);
      delayMs = ANIM_DELAY_MS;
    }
  }

  const result = { sent: 0, acked: 0, rejected: 0, errors: [], strokesSent: 0, strokesAcked: 0 };

  if (strokes.length === 0) return result;

  let lastPresenceMs = Date.now();

  // Build batches
  const batches = [];
  if (legacy) {
    for (const stroke of strokes) {
      batches.push({ msg: { type: 'stroke.add', stroke }, count: 1 });
    }
  } else {
    for (let i = 0; i < strokes.length; i += batchSize) {
      const batch = strokes.slice(i, i + batchSize);
      batches.push({ msg: { type: 'strokes.add', strokes: batch }, count: batch.length });
    }
  }

  for (let bi = 0; bi < batches.length; bi++) {
    const { msg, count } = batches[bi];
    let accepted = false;
    let retries = 0;

    while (!accepted && retries <= BATCH_MAX_RETRIES) {
      if (ws.readyState !== WebSocket.OPEN) {
        console.warn(`[connection] WebSocket not open, stopping at batch ${bi + 1}/${batches.length}`);
        // Count remaining batches as rejected
        for (let r = bi; r < batches.length; r++) {
          result.rejected++;
          result.errors.push('WS_CLOSED');
        }
        return result;
      }

      ws.send(JSON.stringify(msg));
      result.sent++;
      result.strokesSent += count;

      const resp = await waitForBatchResponse(ws);

      if (resp.type === 'ack') {
        accepted = true;
        result.acked++;
        result.strokesAcked += count;
      } else if (resp.type === 'error') {
        if (resp.code === 'RATE_LIMITED') {
          retries++;
          if (retries > BATCH_MAX_RETRIES) {
            result.rejected++;
            result.errors.push(`RATE_LIMITED (${BATCH_MAX_RETRIES} retries exhausted)`);
            console.warn(`[connection] Batch ${bi + 1} rate-limited after ${BATCH_MAX_RETRIES} retries, skipping`);
          } else {
            const backoff = RATE_LIMIT_BASE_MS * Math.pow(2, retries - 1);
            console.warn(`[connection] Rate limited, retry ${retries}/${BATCH_MAX_RETRIES} in ${backoff}ms`);
            await sleep(backoff);
          }
        } else if (resp.code === 'INSUFFICIENT_INQ') {
          result.rejected++;
          result.errors.push('INSUFFICIENT_INQ');
          console.warn(`[connection] Insufficient INQ, stopping send`);
          // Don't count remaining batches as rejected — we just stop
          return result;
        } else {
          // STROKE_TOO_LARGE, BATCH_FAILED, BANNED, etc — skip batch
          result.rejected++;
          result.errors.push(resp.code);
          console.warn(`[connection] Batch ${bi + 1} rejected: ${resp.code} — ${resp.message}`);
          accepted = true; // move on
        }
      } else {
        // timeout — treat as lost, move on
        console.warn(`[connection] Batch ${bi + 1} timed out (no ack/error in ${BATCH_ACK_TIMEOUT_MS}ms)`);
        accepted = true; // move on
      }
    }

    // Resend presence every ~10s to keep cursor visible for viewers
    if (accepted && ws._currentViewport && Date.now() - lastPresenceMs > 10_000) {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(ws._currentViewport));
      }
      lastPresenceMs = Date.now();
    }

    // Inter-batch pacing (only between successful batches, not after the last)
    if (accepted && bi < batches.length - 1 && delayMs > 0) {
      await sleep(delayMs);
    }
  }

  return result;
}

/**
 * Drop a waypoint on the canvas and wait for server confirmation.
 *
 * @param {WebSocket} ws - Connected WebSocket
 * @param {object} opts
 * @param {string} opts.name - Waypoint display name (max 64 chars)
 * @param {number} opts.x - X coordinate
 * @param {number} opts.y - Y coordinate
 * @param {number} opts.zoom - Zoom level
 * @param {string} [opts.description] - Optional description (max 512 chars)
 * @returns {Promise<object>} The created waypoint object (with id, name, x, y, zoom)
 */
export function addWaypoint(ws, { name, x, y, zoom, description }) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      ws.removeListener('message', handler);
      reject(new Error('Waypoint response timeout (5s)'));
    }, 5000);

    function handler(data) {
      try {
        const parsed = JSON.parse(data.toString());
        const msgs = Array.isArray(parsed) ? parsed : [parsed];
        for (const msg of msgs) {
          if (msg.type === 'waypoint.added') {
            clearTimeout(timeout);
            ws.removeListener('message', handler);
            resolve(msg.waypoint);
          } else if (msg.type === 'sync.error') {
            clearTimeout(timeout);
            ws.removeListener('message', handler);
            reject(new Error(msg.message || msg.code));
          }
        }
      } catch { /* ignore */ }
    }

    ws.on('message', handler);
    ws.send(JSON.stringify({
      type: 'waypoint.add',
      waypoint: { name, x, y, zoom, description: description || undefined },
    }));
  });
}

/**
 * Delete a stroke by ID (own strokes only).
 *
 * @param {WebSocket} ws - Connected WebSocket
 * @param {string} strokeId - ID of the stroke to delete
 * @returns {Promise<{ deleted: true }>}
 */
export function deleteStroke(ws, strokeId) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      ws.removeListener('message', handler);
      reject(new Error('Stroke delete response timeout (5s)'));
    }, 5000);

    function handler(data) {
      try {
        const parsed = JSON.parse(data.toString());
        const msgs = Array.isArray(parsed) ? parsed : [parsed];
        for (const msg of msgs) {
          if (msg.type === 'stroke.deleted' && msg.strokeId === strokeId) {
            clearTimeout(timeout);
            ws.removeListener('message', handler);
            resolve({ deleted: true });
          } else if (msg.type === 'sync.error') {
            clearTimeout(timeout);
            ws.removeListener('message', handler);
            reject(new Error(msg.message || msg.code));
          }
        }
      } catch { /* ignore */ }
    }

    ws.on('message', handler);
    ws.send(JSON.stringify({ type: 'stroke.delete', strokeId }));
  });
}

/**
 * Delete a waypoint by ID (own waypoints only).
 *
 * @param {WebSocket} ws - Connected WebSocket
 * @param {string} waypointId - ID of the waypoint to delete
 * @returns {Promise<{ deleted: true }>}
 */
export function deleteWaypoint(ws, waypointId) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      ws.removeListener('message', handler);
      reject(new Error('Waypoint delete response timeout (5s)'));
    }, 5000);

    function handler(data) {
      try {
        const parsed = JSON.parse(data.toString());
        const msgs = Array.isArray(parsed) ? parsed : [parsed];
        for (const msg of msgs) {
          if (msg.type === 'waypoint.deleted' && msg.waypointId === waypointId) {
            clearTimeout(timeout);
            ws.removeListener('message', handler);
            resolve({ deleted: true });
          } else if (msg.type === 'sync.error') {
            clearTimeout(timeout);
            ws.removeListener('message', handler);
            reject(new Error(msg.message || msg.code));
          }
        }
      } catch { /* ignore */ }
    }

    ws.on('message', handler);
    ws.send(JSON.stringify({ type: 'waypoint.delete', waypointId }));
  });
}

/**
 * Build a shareable URL for a waypoint.
 *
 * @param {object} waypoint - Waypoint object with id property
 * @returns {string} Shareable URL
 */
export function getWaypointUrl(waypoint) {
  return `https://clawdraw.ai/?wp=${waypoint.id}`;
}

/**
 * Send a chat message over the WebSocket. Fire-and-forget.
 * @param {WebSocket} ws
 * @param {string} content
 */
function sendChatMessage(ws, content) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'chat.send', chatMessage: { content } }));
  }
}

/**
 * Auto-find an empty canvas spot via the relay API.
 * Returns { x, y } or null on failure.
 */
async function autoFindSpace(token) {
  try {
    const res = await fetch(`${RELAY_HTTP_URL}/api/find-space?mode=empty`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (res.ok) {
      const space = await res.json();
      return { x: space.canvasX, y: space.canvasY };
    }
  } catch { /* fall through */ }
  return null;
}

/**
 * Create a waypoint, announce in chat, open browser, send strokes, then snapshot.
 *
 * Flow:
 *   1. Compute center from strokes
 *   2. viewport.update to drawing center
 *   3. Create waypoint BEFORE drawing
 *   4. Post waypoint link in chat
 *   5. Open waypoint URL in browser
 *   6. Send strokes
 *   7. Post waypoint link in chat again
 *   8. Capture snapshot
 *
 * @param {WebSocket} ws - Connected WebSocket
 * @param {Array} strokes - Array of stroke objects
 * @param {object} [opts]
 * @param {number} [opts.cx] - Center X (computed from strokes if omitted)
 * @param {number} [opts.cy] - Center Y (computed from strokes if omitted)
 * @param {number} [opts.zoom] - Zoom level for links (auto-computed from stroke bounding box if omitted)
 * @param {string} [opts.name] - Waypoint name
 * @param {string} [opts.description] - Waypoint description
 * @param {boolean} [opts.skipWaypoint=false] - Skip waypoint creation, chat post, and browser open
 * @returns {Promise<SendResult>}
 */
export async function drawAndTrack(ws, strokes, { cx, cy, zoom, name, description, skipWaypoint = false } = {}) {
  const drawingName = name || 'Drawing';

  // 1. Auto-placement: find empty spot if no position specified
  if (cx === undefined || cy === undefined) {
    const spot = ws._authToken ? await autoFindSpace(ws._authToken) : null;
    if (spot) {
      // Add ±500 jitter to prevent concurrent bot collisions
      if (cx === undefined) cx = spot.x + Math.round((Math.random() - 0.5) * 1000);
      if (cy === undefined) cy = spot.y + Math.round((Math.random() - 0.5) * 1000);
    } else {
      // Fallback: random position in a large range
      if (cx === undefined) cx = Math.round((Math.random() - 0.5) * 100_000);
      if (cy === undefined) cy = Math.round((Math.random() - 0.5) * 100_000);
    }
  }

  // Translate strokes to the chosen center
  const bbox = computeBoundingBox(strokes);
  const strokeCx = Math.round((bbox.minX + bbox.maxX) / 2);
  const strokeCy = Math.round((bbox.minY + bbox.maxY) / 2);
  const dx = cx - strokeCx;
  const dy = cy - strokeCy;
  if (dx !== 0 || dy !== 0) {
    for (const s of strokes) {
      for (const pt of s.points) {
        pt.x += dx;
        pt.y += dy;
      }
    }
  }

  // Auto-compute zoom from bounding box if not explicitly set
  if (zoom === undefined) {
    const bboxW = bbox.maxX - bbox.minX;
    const bboxH = bbox.maxY - bbox.minY;
    const extent = Math.max(bboxW, bboxH, 50); // min 50 to avoid extreme zoom
    zoom = Math.min(Math.max(600 / extent, 0.3), 5); // clamp 0.3–5.0
  }

  // 2. Update viewport/cursor to drawing center
  const drawViewport = {
    type: 'viewport.update',
    viewport: { center: { x: cx, y: cy }, zoom, size: { width: 6000, height: 6000 } },
    cursor: { x: cx, y: cy },
    username: ws._clawdrawUsername,
  };
  ws._currentViewport = drawViewport;
  ws.send(JSON.stringify(drawViewport));

  // 3. Create waypoint BEFORE drawing
  let waypointUrl = null;
  if (!skipWaypoint) {
    try {
      const wp = await addWaypoint(ws, {
        name: drawingName,
        x: cx, y: cy, zoom,
        description: description || `${strokes.length} strokes`,
      });
      waypointUrl = getWaypointUrl(wp);
      console.log(`Waypoint: ${waypointUrl}`);
    } catch (wpErr) {
      console.warn(`[waypoint] Failed: ${wpErr.message}`);
    }

    // 4. Open waypoint URL in browser (with nomodal for clean viewing)
    if (waypointUrl) {
      openInBrowser(`${waypointUrl}&nomodal=1`);
    }
  }

  // Wait for browser page to load before sending strokes
  if (!skipWaypoint) {
    await new Promise(resolve => setTimeout(resolve, 3000));
  }

  // 6. Send strokes
  const result = await sendStrokes(ws, strokes);

  // 7. Capture snapshot
  try {
    const snapshot = await captureSnapshot(ws, strokes, TILE_CDN_URL);
    if (snapshot) {
      console.log(`Snapshot: ${snapshot.imagePath} (${snapshot.width}x${snapshot.height})`);
    }
  } catch (snapErr) {
    console.warn(`[snapshot] Failed: ${snapErr.message}`);
  }

  return result;
}

/**
 * Disconnect gracefully.
 *
 * @param {WebSocket} ws
 */
export function disconnect(ws) {
  if (ws && ws._presenceHeartbeat) {
    clearInterval(ws._presenceHeartbeat);
    ws._presenceHeartbeat = null;
  }
  // Clean up tile update listeners for this socket
  if (ws) _tileUpdateListeners.delete(ws);
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.close(1000, 'done');
  }
}

/**
 * Connect with automatic reconnection on disconnect.
 * Returns a wrapper that transparently reconnects.
 *
 * @param {string} token - JWT
 * @param {object} [opts] - Same as connect() opts
 * @returns {Promise<{ ws: WebSocket, sendStrokes: Function, disconnect: Function }>}
 */
export async function connectWithRetry(token, opts = {}) {
  let ws = null;
  let retries = 0;
  let closed = false;

  async function doConnect() {
    ws = await connect(token, opts);
    retries = 0;

    ws.on('close', async (code) => {
      if (ws._presenceHeartbeat) {
        clearInterval(ws._presenceHeartbeat);
        ws._presenceHeartbeat = null;
      }
      if (closed) return;
      if (retries >= MAX_RETRIES) {
        console.error(`[connection] Max retries (${MAX_RETRIES}) exceeded, giving up`);
        return;
      }
      const delay = BASE_DELAY_MS * Math.pow(2, retries);
      retries++;
      console.warn(`[connection] Disconnected (code ${code}), reconnecting in ${delay}ms (attempt ${retries})`);
      await sleep(delay);
      if (!closed) {
        try { await doConnect(); } catch (e) {
          console.error(`[connection] Reconnect failed:`, e.message);
        }
      }
    });

    return ws;
  }

  await doConnect();

  return {
    get ws() { return ws; },
    sendStrokes: (strokes, delayMs) => sendStrokes(ws, strokes, delayMs),
    disconnect() {
      closed = true;
      disconnect(ws);
    },
  };
}

// ---------------------------------------------------------------------------
// Internal
// ---------------------------------------------------------------------------

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
