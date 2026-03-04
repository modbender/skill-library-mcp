#!/usr/bin/env node
/**
 * Cherry MCP 🍒 - HTTP bridge for MCP servers
 */

const http = require('http');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const CONFIG_PATH = process.env.CHERRY_MCP_CONFIG || path.join(__dirname, 'config.json');
let config;

try {
  config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
} catch (err) {
  console.error('Failed to load config:', err.message);
  process.exit(1);
}

const PORT = process.env.PORT || config.port || 3456;
const HOST = config.host || '127.0.0.1';
const SECURITY = config.security || {};
const RATE_LIMIT = SECURITY.rateLimit || 0;
const ALLOWED_IPS = SECURITY.allowedIps || [];
const AUDIT_LOG = SECURITY.auditLog || false;
const AUDIT_PATH = path.join(__dirname, 'audit.log');

const rateLimitState = new Map();
const servers = new Map();
let rpcId = 1;

function audit(req, action, details = {}) {
  if (!AUDIT_LOG) return;
  const entry = { ts: new Date().toISOString(), ip: req.socket.remoteAddress, action, ...details };
  fs.appendFileSync(AUDIT_PATH, JSON.stringify(entry) + '\n');
}

class MCPServer {
  constructor(name, cfg) {
    this.name = name;
    this.config = cfg;
    this.process = null;
    this.buffer = '';
    this.pending = new Map();
    this.tools = null;
    this.ready = false;
    this.restarts = 0;
  }

  async start() {
    if (this.process) return;
    const { command, args = [], env = {} } = this.config;
    console.log(`[${this.name}] Starting: ${command} ${args.join(' ')}`);

    this.process = spawn(command, args, {
      env: { ...process.env, ...env },
      stdio: ['pipe', 'pipe', 'pipe']
    });

    this.process.stdout.on('data', d => this.onData(d));
    this.process.stderr.on('data', d => {
      const msg = d.toString().trim();
      if (msg && !msg.includes('npm warn')) console.error(`[${this.name}]`, msg);
    });

    this.process.on('close', code => {
      console.log(`[${this.name}] Exited (${code})`);
      this.process = null;
      this.ready = false;
      for (const [id, h] of this.pending) { h.reject(new Error('closed')); clearTimeout(h.timeout); }
      this.pending.clear();
      if (this.restarts < 5) { this.restarts++; setTimeout(() => this.start(), 1000 * this.restarts); }
    });

    await this.init();
  }

  async init() {
    try {
      await this.send('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'cherry-mcp', version: '1.0.0' } });
      const r = await this.send('tools/list', {});
      this.tools = r.tools || [];
      console.log(`[${this.name}] Ready (${this.tools.length} tools)`);
      this.ready = true;
      this.restarts = 0;
    } catch (e) {
      console.error(`[${this.name}] Init failed:`, e.message);
    }
  }

  onData(data) {
    this.buffer += data.toString();
    const lines = this.buffer.split('\n');
    this.buffer = lines.pop();
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const msg = JSON.parse(line);
        if (msg.id !== undefined && this.pending.has(msg.id)) {
          const h = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          clearTimeout(h.timeout);
          msg.error ? h.reject(new Error(msg.error.message)) : h.resolve(msg.result);
        }
      } catch {}
    }
  }

  send(method, params, timeoutMs = 30000) {
    return new Promise((resolve, reject) => {
      if (!this.process) return reject(new Error('not running'));
      const id = rpcId++;
      const timeout = setTimeout(() => { this.pending.delete(id); reject(new Error('timeout')); }, timeoutMs);
      this.pending.set(id, { resolve, reject, timeout });
      this.process.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
    });
  }

  callTool(name, args = {}) { return this.send('tools/call', { name, arguments: args }); }
  stop() { if (this.process) { this.restarts = 99; this.process.kill(); } }
  status() { return { name: this.name, running: !!this.process, ready: this.ready, tools: this.tools?.length || 0 }; }
}

function checkSecurity(req, res) {
  const ip = req.socket.remoteAddress?.replace('::ffff:', '') || '';
  
  if (ALLOWED_IPS.length && !ALLOWED_IPS.includes(ip) && ip !== '127.0.0.1') {
    res.writeHead(403, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'IP not allowed' }));
    return false;
  }

  if (RATE_LIMIT > 0) {
    const now = Date.now();
    let s = rateLimitState.get(ip);
    if (!s || s.reset < now) s = { count: 0, reset: now + 60000 };
    if (++s.count > RATE_LIMIT) {
      res.writeHead(429, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Rate limit exceeded' }));
      return false;
    }
    rateLimitState.set(ip, s);
  }
  return true;
}

async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }
  if (!checkSecurity(req, res)) return;

  const parts = req.url.split('/').filter(Boolean);
  
  try {
    if (!parts.length) {
      const list = {};
      for (const [n, s] of servers) list[n] = s.status();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ servers: list }));
      return;
    }

    const srv = servers.get(parts[0]);
    if (!srv) { res.writeHead(404); res.end(JSON.stringify({ error: 'Server not found' })); return; }

    const action = parts[1] || 'status';

    if (action === 'status') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(srv.status()));
    } else if (action === 'tools') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ tools: srv.tools || [] }));
    } else if (action === 'call' && req.method === 'POST') {
      let body = '';
      for await (const chunk of req) body += chunk;
      const { tool, arguments: args } = JSON.parse(body);
      audit(req, 'call', { server: parts[0], tool });
      const result = await srv.callTool(tool, args || {});
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ result }));
    } else if (action === 'restart' && req.method === 'POST') {
      srv.stop();
      srv.restarts = 0;
      setTimeout(() => srv.start(), 500);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'restarting' }));
    } else {
      res.writeHead(404);
      res.end(JSON.stringify({ error: 'Not found' }));
    }
  } catch (e) {
    audit(req, 'error', { error: e.message });
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: e.message }));
  }
}

async function main() {
  console.log(`\n🍒 Cherry MCP starting on ${HOST}:${PORT}\n`);
  
  const cfgs = Object.entries(config.servers || {});
  if (!cfgs.length) console.log('No servers configured. Use: node cli.js add-server <name> <cmd>\n');
  
  for (const [name, cfg] of cfgs) {
    const srv = new MCPServer(name, cfg);
    servers.set(name, srv);
    await srv.start();
  }

  http.createServer(handler).listen(PORT, HOST, () => console.log(`\nReady at http://${HOST}:${PORT}\n`));
  process.on('SIGINT', () => { for (const s of servers.values()) s.stop(); process.exit(); });
  process.on('SIGTERM', () => { for (const s of servers.values()) s.stop(); process.exit(); });
}

main();
