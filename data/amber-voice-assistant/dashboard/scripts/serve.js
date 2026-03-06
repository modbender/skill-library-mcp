#!/usr/bin/env node
const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');
const { spawn } = require('child_process');

function parseArgs(argv) {
  const args = { port: 8787, host: '127.0.0.1' };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--port' && argv[i + 1]) args.port = Number(argv[++i]);
    else if (a === '--host' && argv[i + 1]) args.host = argv[++i];
    else if (a === '-h' || a === '--help') args.help = true;
  }
  return args;
}

function contentType(p) {
  if (p.endsWith('.html')) return 'text/html; charset=utf-8';
  if (p.endsWith('.css')) return 'text/css; charset=utf-8';
  if (p.endsWith('.js')) return 'text/javascript; charset=utf-8';
  if (p.endsWith('.json')) return 'application/json; charset=utf-8';
  if (p.endsWith('.svg')) return 'image/svg+xml';
  if (p.endsWith('.png')) return 'image/png';
  if (p.endsWith('.jpg') || p.endsWith('.jpeg')) return 'image/jpeg';
  return 'application/octet-stream';
}

const args = parseArgs(process.argv);
if (args.help) {
  console.log('Usage: node scripts/serve.js [--host 127.0.0.1] [--port 8787]');
  console.log('');
  console.log('  The dashboard binds to loopback only (127.0.0.1/::1/localhost).');
  console.log('  For remote access, use a reverse proxy with authentication.');
  process.exit(0);
}

const root = path.resolve(__dirname, '..');

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') { res.writeHead(200); res.end(); return; }

  // POST /api/sync — manually trigger process_logs.js
  // Security: target script path is hardcoded (not user-controlled); no user input is
  // passed to the spawned process. Environment is scoped to only what Node needs.
  if (req.method === 'POST' && req.url === '/api/sync') {
    // Hardcoded path — not derived from request input
    const processLogsPath = path.resolve(root, 'process_logs.js');
    // Verify target stays within the dashboard root (defense in depth)
    if (!processLogsPath.startsWith(root + path.sep) && processLogsPath !== path.resolve(root, 'process_logs.js')) {
      res.writeHead(403, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Forbidden' }));
      return;
    }
    const startTime = Date.now();
    // Scope env to minimal required vars rather than forwarding entire process.env
    const safeEnv = {
      HOME: process.env.HOME,
      PATH: process.env.PATH,
      LOGS_DIR: process.env.LOGS_DIR,
      TWILIO_CALLER_ID: process.env.TWILIO_CALLER_ID,
      ASSISTANT_NAME: process.env.ASSISTANT_NAME,
      OPERATOR_NAME: process.env.OPERATOR_NAME,
    };
    const child = spawn(process.execPath, [processLogsPath], { env: safeEnv, timeout: 120000 });
    let stdout = '', stderr = '';
    child.stdout.on('data', d => { stdout += d; });
    child.stderr.on('data', d => { stderr += d; });
    child.on('close', code => {
      const durationMs = Date.now() - startTime;
      console.log(`[sync] process_logs.js exited ${code} in ${durationMs}ms`);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: code === 0, exitCode: code, durationMs,
        output: stdout.trim().split('\n').slice(-5).join('\n'), error: stderr.trim() || null }));
    });
    child.on('error', err => {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: err.message }));
    });
    return;
  }

  const u = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  let pathname = decodeURIComponent(u.pathname);
  if (pathname === '/') pathname = '/index.html';

  const fsPath = path.resolve(root, '.' + pathname);
  if (!fsPath.startsWith(root + path.sep) && fsPath !== root) {
    res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Forbidden');
    return;
  }

  fs.readFile(fsPath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' });
      res.end('Not found');
      return;
    }
    res.writeHead(200, {
      'Content-Type': contentType(fsPath),
      'Cache-Control': 'no-store'
    });
    res.end(data);
  });
});

// Hard-reject non-loopback binding — no override flag exists.
// Call logs and transcripts contain PII; exposing them without authentication is not permitted.
// For remote access, place a reverse proxy with authentication in front of this server.
const LOOPBACK_ADDRESSES = new Set(['127.0.0.1', '::1', 'localhost']);
if (!LOOPBACK_ADDRESSES.has(args.host)) {
  console.error('');
  console.error('ERROR: Dashboard only binds to loopback (127.0.0.1 / ::1 / localhost).');
  console.error('   Requested: ' + args.host);
  console.error('   Call logs and transcripts contain PII and must not be exposed to the network without authentication.');
  console.error('   For remote access, use a reverse proxy (e.g. nginx, caddy) with authentication.');
  console.error('');
  process.exit(1);
}

server.listen(args.port, args.host, () => {
  console.log(`Serving ${root}`);
  console.log(`Open: http://${args.host}:${args.port}/`);
});
