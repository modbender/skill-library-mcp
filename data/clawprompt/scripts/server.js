#!/usr/bin/env node
// ClawPrompt Server — teleprompter + mobile remote via WebSocket
const http = require('http');
const fs = require('fs');
const path = require('path');
const { WebSocketServer } = require('ws');
const os = require('os');

const PORT = parseInt(process.env.PORT || '7870', 10);
const DIR = __dirname;

function getLanIP() {
  const nets = os.networkInterfaces();
  for (const name of Object.keys(nets)) {
    for (const n of nets[name]) {
      if (n.family === 'IPv4' && !n.internal) return n.address;
    }
  }
  return '127.0.0.1';
}

const QRCode = require('qrcode');

const MIME = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.png': 'image/png', '.svg': 'image/svg+xml' };
const lanIP = getLanIP();

const server = http.createServer((req, res) => {
  const parsed = new URL(req.url, 'http://localhost');

  // QR URL endpoint
  if (parsed.pathname === '/qr-url') {
    const url = `http://${lanIP}:${PORT}/remote`;
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ url }));
    return;
  }

  // QR image endpoint
  if (parsed.pathname === '/qr.png') {
    const url = parsed.searchParams.get('url') || `http://${lanIP}:${PORT}/remote`;
    const size = parseInt(parsed.searchParams.get('size') || '160', 10);
    QRCode.toBuffer(url, { width: size, margin: 1 }, (err, buf) => {
      if (err) { res.writeHead(500); res.end(); return; }
      res.writeHead(200, { 'Content-Type': 'image/png', 'Cache-Control': 'max-age=3600' });
      res.end(buf);
    });
    return;
  }

  let filePath = parsed.pathname === '/' ? '/index.html' : parsed.pathname;
  if (filePath === '/remote') filePath = '/remote.html';
  const full = path.join(DIR, filePath);
  if (!full.startsWith(DIR)) { res.writeHead(403); res.end(); return; }
  fs.readFile(full, (err, data) => {
    if (err) { res.writeHead(404); res.end('Not found'); return; }
    const ext = path.extname(full);
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    res.end(data);
  });
});

const wss = new WebSocketServer({ server });
const clients = new Map(); // ws -> { role: 'main'|'remote' }
let state = { idx: 0, total: 0, current: '', next: '' };

function broadcast(data, exclude) {
  const json = JSON.stringify(data);
  for (const [c] of clients) { if (c !== exclude && c.readyState === 1) c.send(json); }
}

function broadcastAll(data) {
  const json = JSON.stringify(data);
  for (const [c] of clients) { if (c.readyState === 1) c.send(json); }
}

function remoteCount() {
  let n = 0;
  for (const [, info] of clients) { if (info.role === 'remote') n++; }
  return n;
}

function broadcastRemoteCount() {
  broadcastAll({ type: 'remoteCount', count: remoteCount() });
}

wss.on('connection', (ws) => {
  clients.set(ws, { role: 'main' }); // default role
  ws.send(JSON.stringify({ type: 'state', ...state }));

  ws.on('message', (raw) => {
    try {
      const msg = JSON.parse(raw);
      if (msg.type === 'register') {
        clients.set(ws, { role: msg.role || 'main' });
        broadcastRemoteCount();
      } else if (msg.type === 'sync') {
        // Main teleprompter syncs state
        state = { idx: msg.idx, total: msg.total, current: msg.current || '', next: msg.next || '' };
        broadcast({ type: 'state', ...state }, ws);
      } else if (msg.type === 'cmd') {
        // Remote sends command → broadcast to all (main will handle)
        broadcast({ type: 'cmd', action: msg.action }, ws);
      } else if (msg.type === 'text') {
        // Remote uploaded text → broadcast to all
        broadcast({ type: 'text', text: msg.text }, ws);
      } else if (msg.type === 'fulltext') {
        // Main syncs text to remotes
        broadcast({ type: 'fulltext', text: msg.text }, ws);
      }
    } catch {}
  });

  ws.on('close', () => {
    clients.delete(ws);
    broadcastRemoteCount();
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`\n🎬 ClawPrompt Server`);
  console.log(`   电脑提词器: http://localhost:${PORT}`);
  console.log(`   手机遥控:   http://${lanIP}:${PORT}/remote`);
  console.log(`   (确保手机和电脑在同一 WiFi)\n`);
});
