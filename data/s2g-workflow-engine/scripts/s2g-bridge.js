#!/usr/bin/env node
/**
 * S2G WebSocket Bridge — Persistent Service
 *
 * Connects to an S2G workflow over WebSocket, auto-discovers all sibling nodes,
 * and exposes them as callable tools via a local HTTP API.
 * Auto-reconnects on disconnect. Logs to file with rotation.
 *
 * Usage:
 *   node s2g-bridge.js --s2g wss://s2g.run --node-id YOUR_NODE_UUID [--port 18792] [--secret SECRET]
 *
 * Environment (alternative to CLI args):
 *   S2G_WS_HOST, S2G_NODE_ID, S2G_BRIDGE_PORT, S2G_SECRET
 *
 * HTTP API:
 *   GET  /health           — 200 if connected, 503 if not
 *   GET  /status           — Full status: connection, nodes, stats, errors
 *   GET  /nodes            — List available S2G nodes
 *   POST /execute          — Execute by nodeId: { nodeId, params, timeout? }
 *   POST /execute/:name    — Execute by name (fuzzy match): { params: {...} }
 *   POST /refresh          — Request fresh node list from S2G
 *   POST /reconnect        — Force reconnect to S2G
 */

const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

// --- File Logging ---
const LOG_DIR = process.env.S2G_LOG_DIR || path.join(process.cwd(), 'logs');
const LOG_FILE = path.join(LOG_DIR, 's2g-bridge.log');
const MAX_LOG_SIZE = 5 * 1024 * 1024; // 5MB

try { fs.mkdirSync(LOG_DIR, { recursive: true }); } catch (_) {}

function rotateIfNeeded() {
  try {
    const stat = fs.statSync(LOG_FILE);
    if (stat.size > MAX_LOG_SIZE) {
      const bak = LOG_FILE + '.1';
      if (fs.existsSync(bak)) fs.unlinkSync(bak);
      fs.renameSync(LOG_FILE, bak);
    }
  } catch (_) {}
}

function writeLog(line) {
  rotateIfNeeded();
  try { fs.appendFileSync(LOG_FILE, line + '\n'); } catch (_) {}
}

function log(msg) { const line = `[${new Date().toISOString()}] [s2g-bridge] ${msg}`; console.log(line); writeLog(line); }
function logErr(msg) { const line = `[${new Date().toISOString()}] [s2g-bridge] ERROR: ${msg}`; console.error(line); writeLog(line); }

// --- Config ---
const args = process.argv.slice(2);
function arg(name, envName, fallback) {
  const idx = args.indexOf(`--${name}`);
  return (idx >= 0 && args[idx + 1]) ? args[idx + 1] : (process.env[envName] || fallback);
}

const HTTP_PORT       = parseInt(arg('port', 'S2G_BRIDGE_PORT', '18792'), 10);
const S2G_WS_HOST     = arg('s2g', 'S2G_WS_HOST', '');
const NODE_ID         = arg('node-id', 'S2G_NODE_ID', '');
const SECRET          = arg('secret', 'S2G_SECRET', '');
const RECONNECT_MS    = 5000;
const PING_MS         = 30000;
const DEFAULT_TIMEOUT = 60000;

if (!S2G_WS_HOST || !NODE_ID) {
  console.error('Usage: node s2g-bridge.js --s2g wss://s2g.run --node-id NODE_UUID [--port 18792] [--secret SECRET]');
  console.error('\nOr set environment variables: S2G_WS_HOST, S2G_NODE_ID');
  process.exit(1);
}

// --- State ---
let ws = null;
let connected = false;
let connectingSince = null;
let lastConnected = null;
let lastError = null;
let availableNodes = [];
let pendingRequests = new Map();
let requestCounter = 0;
let pingTimer = null;
let reconnectTimer = null;
let stats = { connects: 0, executions: 0, errors: 0, lastExecution: null };

// --- WebSocket Client ---
function connect() {
  if (ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) return;

  const url = `${S2G_WS_HOST}/api/openclaw/ws/${NODE_ID}`;
  connectingSince = Date.now();
  log(`Connecting to ${url}...`);

  try {
    ws = new WebSocket(url);
  } catch (err) {
    logErr(`Failed to create WebSocket: ${err.message}`);
    scheduleReconnect();
    return;
  }

  ws.on('open', () => {
    log('WebSocket open');
    if (SECRET) send({ type: 'auth', secret: SECRET });
    startPing();
  });

  ws.on('message', handleMessage);

  ws.on('close', (code, reason) => {
    log(`WebSocket closed: ${code} ${reason || ''}`);
    cleanup();
    scheduleReconnect();
  });

  ws.on('error', (err) => {
    lastError = { message: err.message, time: new Date().toISOString() };
    if (err.message.includes('409')) {
      log('Workflow not running (409) — will retry...');
    } else {
      logErr(err.message);
    }
  });
}

function handleMessage(data) {
  let msg;
  try {
    msg = JSON.parse(data.toString());
  } catch (e) {
    logErr(`Invalid JSON: ${data.toString().slice(0, 200)}`);
    return;
  }

  switch (msg.type) {
    case 'connected':
      connected = true;
      connectingSince = null;
      lastConnected = new Date().toISOString();
      stats.connects++;
      availableNodes = (msg.availableNodes || []).map(normalizeNode);
      log(`Connected! ${availableNodes.length} nodes available`);
      availableNodes.forEach(n => log(`  🔧 ${n.name} (${n.nodeType}) id=${n.nodeId}`));
      break;

    case 'node_list':
      availableNodes = (msg.nodes || []).map(normalizeNode);
      log(`Node list refreshed: ${availableNodes.length} nodes`);
      break;

    case 'result': {
      const p = pendingRequests.get(msg.requestId);
      if (p) {
        clearTimeout(p.timer);
        pendingRequests.delete(msg.requestId);
        stats.executions++;
        stats.lastExecution = new Date().toISOString();
        p.resolve({ success: msg.success !== false, output: msg.output || {} });
        log(`Result ${msg.requestId}: success=${msg.success !== false}`);
      }
      break;
    }

    case 'error': {
      const p = pendingRequests.get(msg.requestId);
      if (p) {
        clearTimeout(p.timer);
        pendingRequests.delete(msg.requestId);
        stats.errors++;
        p.resolve({ success: false, output: {}, error: msg.message || 'Unknown error' });
        logErr(`Execute ${msg.requestId} failed: ${msg.message}`);
      } else {
        logErr(`Unhandled error: ${msg.message}`);
      }
      break;
    }

    case 'pong':
      break;

    case 'auth_required':
      logErr('Auth required but no secret configured! Use --secret or S2G_SECRET env var.');
      break;

    case 'auth_failed':
      logErr('Auth failed! Check secret.');
      lastError = { message: 'Auth failed', time: new Date().toISOString() };
      ws.close();
      break;

    default:
      log(`📨 Received [${msg.type}]: ${JSON.stringify(msg.data || msg).slice(0, 500)}`);
  }
}

function normalizeNode(n) {
  return {
    nodeId: n.NodeId || n.nodeId,
    name: n.Name || n.name,
    nodeType: n.NodeType || n.nodeType,
    outputParams: n.OutputParams || n.outputParams || []
  };
}

function send(msg) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg));
    return true;
  }
  return false;
}

function startPing() {
  stopPing();
  pingTimer = setInterval(() => {
    if (!send({ type: 'ping' })) stopPing();
  }, PING_MS);
}

function stopPing() {
  if (pingTimer) { clearInterval(pingTimer); pingTimer = null; }
}

function cleanup() {
  connected = false;
  stopPing();
  for (const [id, p] of pendingRequests) {
    clearTimeout(p.timer);
    p.resolve({ success: false, output: {}, error: 'Connection lost' });
  }
  pendingRequests.clear();
}

function scheduleReconnect() {
  if (reconnectTimer) return;
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    connect();
  }, RECONNECT_MS);
}

// --- Execute a node ---
function executeNode(nodeId, params = {}, timeoutMs = DEFAULT_TIMEOUT) {
  return new Promise((resolve) => {
    if (!connected || !ws || ws.readyState !== WebSocket.OPEN) {
      resolve({ success: false, output: {}, error: 'Not connected to S2G' });
      return;
    }
    const requestId = `r${++requestCounter}-${Date.now()}`;
    const timer = setTimeout(() => {
      pendingRequests.delete(requestId);
      stats.errors++;
      resolve({ success: false, output: {}, error: `Timeout after ${timeoutMs}ms` });
    }, timeoutMs);
    pendingRequests.set(requestId, { resolve, timer });
    send({ type: 'execute', requestId, nodeId, params });
    log(`Execute ${requestId} -> ${nodeId} params=${JSON.stringify(params)}`);
  });
}

function findNode(name) {
  const lower = name.toLowerCase().replace(/[\s_-]+/g, '');
  return availableNodes.find(n => {
    const nLower = n.name.toLowerCase().replace(/[\s_-]+/g, '');
    const tLower = n.nodeType.toLowerCase().replace(/[\s_-]+/g, '');
    return nLower === lower || tLower === lower ||
           nLower.includes(lower) || tLower.includes(lower);
  });
}

// --- HTTP API ---
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${HTTP_PORT}`);
  const p = url.pathname;

  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');

  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.statusCode = 204;
    res.end();
    return;
  }

  if (req.method === 'GET' && p === '/status') {
    res.end(JSON.stringify({
      connected, s2gHost: S2G_WS_HOST, nodeId: NODE_ID, lastConnected, lastError, stats,
      pendingRequests: pendingRequests.size,
      nodes: availableNodes.map(n => ({ name: n.name, type: n.nodeType, id: n.nodeId, outputs: n.outputParams }))
    }, null, 2));
    return;
  }

  if (req.method === 'GET' && p === '/nodes') {
    res.end(JSON.stringify({ connected, nodes: availableNodes }, null, 2));
    return;
  }

  if (req.method === 'GET' && p === '/health') {
    res.statusCode = connected ? 200 : 503;
    res.end(JSON.stringify({ healthy: connected, uptime: process.uptime() }));
    return;
  }

  if (req.method === 'POST' && p === '/execute') {
    const body = await readBody(req);
    if (!body.nodeId) {
      res.statusCode = 400;
      res.end(JSON.stringify({ error: 'Missing nodeId' }));
      return;
    }
    const result = await executeNode(body.nodeId, body.params || {}, body.timeout || DEFAULT_TIMEOUT);
    res.end(JSON.stringify(result, null, 2));
    return;
  }

  if (req.method === 'POST' && p.startsWith('/execute/')) {
    const name = decodeURIComponent(p.slice('/execute/'.length));
    const node = findNode(name);
    if (!node) {
      res.statusCode = 404;
      res.end(JSON.stringify({ error: `Node "${name}" not found`, available: availableNodes.map(n => n.name) }));
      return;
    }
    const body = await readBody(req);
    const params = body.params || body;
    const timeout = body.timeout || DEFAULT_TIMEOUT;
    const result = await executeNode(node.nodeId, params, timeout);
    res.end(JSON.stringify(result, null, 2));
    return;
  }

  if (req.method === 'POST' && p === '/refresh') {
    const ok = send({ type: 'list_nodes' });
    res.end(JSON.stringify({ ok, message: ok ? 'Refresh requested' : 'Not connected' }));
    return;
  }

  if (req.method === 'POST' && p === '/reconnect') {
    if (ws) ws.close();
    cleanup();
    setTimeout(connect, 500);
    res.end(JSON.stringify({ ok: true, message: 'Reconnecting...' }));
    return;
  }

  res.statusCode = 404;
  res.end(JSON.stringify({
    error: 'Not found',
    endpoints: [
      'GET  /health', 'GET  /status', 'GET  /nodes',
      'POST /execute { nodeId, params }', 'POST /execute/:name { params }',
      'POST /refresh', 'POST /reconnect'
    ]
  }));
});

function readBody(req) {
  return new Promise((resolve) => {
    let data = '';
    req.on('data', chunk => data += chunk);
    req.on('end', () => {
      try { resolve(JSON.parse(data)); } catch { resolve({}); }
    });
  });
}

// --- Start ---
server.listen(HTTP_PORT, '0.0.0.0', () => {
  log(`S2G Bridge listening on port ${HTTP_PORT}`);
  log(`S2G Host: ${S2G_WS_HOST} | Node: ${NODE_ID}`);
  log(`Log file: ${LOG_FILE}`);
  connect();
});

// Graceful shutdown
function shutdown(signal) {
  log(`Shutting down (${signal})...`);
  stopPing();
  if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
  if (ws) ws.close();
  server.close(() => process.exit(0));
  setTimeout(() => process.exit(0), 3000);
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
