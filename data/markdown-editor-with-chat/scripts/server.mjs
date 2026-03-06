#!/usr/bin/env node
/**
 * Markdown Editor with Chat - Lightweight Server
 * 
 * A pure Node.js server with zero external dependencies.
 * Serves markdown files from a directory with optional OpenClaw gateway chat.
 * 
 * Usage:
 *   node server.mjs --folder /path/to/markdown [--port 3333] [--host 127.0.0.1]
 *   node server.mjs -f /path/to/markdown [-p 3333] [-h 127.0.0.1]
 * 
 * Environment (fallback if CLI args not provided):
 *   MARKDOWN_DIR          - Directory containing markdown files
 *   PORT                  - Server port (default: 3333)
 *   HOST                  - Server host (default: 127.0.0.1)
 *   OPENCLAW_GATEWAY_URL  - Optional. Gateway URL for chat
 *   OPENCLAW_GATEWAY_TOKEN - Optional. Gateway auth token
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parseArgs } from 'util';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Parse CLI arguments
let cliArgs = { values: {} };
try {
  cliArgs = parseArgs({
    options: {
      folder: { type: 'string', short: 'f' },
      port: { type: 'string', short: 'p' },
      host: { type: 'string', short: 'h' },
      help: { type: 'boolean' }
    },
    allowPositionals: false,
    strict: false
  });
} catch (e) {
  // Ignore parse errors, fall back to env vars
}

// Show help
if (cliArgs.values.help) {
  console.log(`
📝 Markdown Editor with Chat

Usage:
  node server.mjs --folder /path/to/markdown [options]
  node server.mjs -f /path/to/markdown [options]

Options:
  -f, --folder  Path to markdown files directory (required)
  -p, --port    Server port (default: 3333)
  -h, --host    Server host (default: 127.0.0.1)
      --help    Show this help message

Environment variables (used if CLI args not provided):
  MARKDOWN_DIR           Directory containing markdown files
  PORT                   Server port
  HOST                   Server host
  OPENCLAW_GATEWAY_URL   Gateway URL for chat feature
  OPENCLAW_GATEWAY_TOKEN Gateway auth token
`);
  process.exit(0);
}

// Configuration: CLI args take precedence over env vars
const MARKDOWN_DIR = cliArgs.values.folder || process.env.MARKDOWN_DIR;
const PORT = parseInt(cliArgs.values.port || process.env.PORT || '3333', 10);
const HOST = cliArgs.values.host || process.env.HOST || '127.0.0.1';
const FOLDER_NAME = MARKDOWN_DIR ? path.basename(path.resolve(MARKDOWN_DIR)) : '';
const GATEWAY_URL = process.env.OPENCLAW_GATEWAY_URL || '';
const GATEWAY_TOKEN = process.env.OPENCLAW_GATEWAY_TOKEN || '';

// Security: Only allow localhost/private network hosts
function isLocalhostHost(host) {
  // Check for Tailscale CGNAT range (100.64.0.0/10 = 100.64.x.x - 100.127.x.x)
  if (host.startsWith('100.')) {
    const secondOctet = parseInt(host.split('.')[1], 10);
    if (secondOctet >= 64 && secondOctet <= 127) {
      return true; // Tailscale IP
    }
  }
  return host === 'localhost' ||
         host === '127.0.0.1' ||
         host === '::1' ||
         host.startsWith('10.') ||
         host.startsWith('192.168.') ||
         host.startsWith('172.16.') ||
         host.startsWith('172.17.') ||
         host.startsWith('172.18.');
}

// Validate configuration
if (!MARKDOWN_DIR) {
  console.error('❌ MARKDOWN_DIR environment variable is required');
  console.error('   Set it to the directory containing your markdown files');
  process.exit(1);
}

if (!fs.existsSync(MARKDOWN_DIR)) {
  console.error(`❌ MARKDOWN_DIR does not exist: ${MARKDOWN_DIR}`);
  process.exit(1);
}

if (!isLocalhostHost(HOST)) {
  console.error('❌ SECURITY: Server can only bind to localhost/private network addresses');
  console.error(`   HOST=${HOST} is not allowed`);
  console.error('   Use 127.0.0.1, localhost, or a private IP (10.x, 192.168.x, 172.16-18.x)');
  process.exit(1);
}

// Security: Prevent path traversal
function safePath(requestedPath) {
  const resolved = path.resolve(MARKDOWN_DIR, requestedPath);
  if (!resolved.startsWith(path.resolve(MARKDOWN_DIR))) {
    return null; // Path traversal attempt
  }
  return resolved;
}

// Read the UI HTML file
const UI_HTML_PATH = path.join(__dirname, 'index.html');
let UI_HTML = '';
try {
  UI_HTML = fs.readFileSync(UI_HTML_PATH, 'utf-8');
} catch (e) {
  console.error(`❌ Could not read UI file: ${UI_HTML_PATH}`);
  process.exit(1);
}

// Helper: Send JSON response
function sendJSON(res, data, status = 200) {
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

// Helper: Send error
function sendError(res, message, status = 400) {
  sendJSON(res, { error: message }, status);
}

// Helper: Read request body
function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

// List files and folders
function listFiles(dirPath = '') {
  const fullPath = safePath(dirPath);
  if (!fullPath || !fs.existsSync(fullPath)) {
    return { error: 'Invalid path' };
  }

  const stat = fs.statSync(fullPath);
  if (!stat.isDirectory()) {
    return { error: 'Not a directory' };
  }

  const entries = fs.readdirSync(fullPath, { withFileTypes: true });
  const items = entries
    .filter(e => !e.name.startsWith('.'))
    .map(e => ({
      name: e.name,
      type: e.isDirectory() ? 'folder' : 'file',
      path: path.join(dirPath, e.name),
      extension: e.isFile() ? path.extname(e.name).toLowerCase() : null
    }))
    .filter(e => e.type === 'folder' || e.extension === '.md')
    .sort((a, b) => {
      if (a.type !== b.type) return a.type === 'folder' ? -1 : 1;
      return a.name.localeCompare(b.name);
    });

  return { path: dirPath, items };
}

// Get file content
function getFile(filePath) {
  const fullPath = safePath(filePath);
  if (!fullPath) {
    return { error: 'Invalid path' };
  }
  // Security: Only allow .md files, block dotfiles
  const basename = path.basename(filePath);
  if (basename.startsWith('.') || !filePath.endsWith('.md')) {
    return { error: 'Only .md files allowed' };
  }
  if (!fs.existsSync(fullPath)) {
    return { error: 'File not found' };
  }
  const stat = fs.statSync(fullPath);
  if (stat.isDirectory()) {
    return { error: 'Path is a directory' };
  }
  const content = fs.readFileSync(fullPath, 'utf-8');
  return { path: filePath, content, size: stat.size, modified: stat.mtime };
}

// Save file content
function saveFile(filePath, content) {
  const fullPath = safePath(filePath);
  if (!fullPath) {
    return { error: 'Invalid path' };
  }
  // Security: Only allow .md files, block dotfiles
  const basename = path.basename(filePath);
  if (basename.startsWith('.') || !filePath.endsWith('.md')) {
    return { error: 'Only .md files allowed' };
  }
  // Ensure parent directory exists
  const dir = path.dirname(fullPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(fullPath, content, 'utf-8');
  return { success: true, path: filePath };
}

// Proxy chat to gateway
async function proxyChat(messages) {
  if (!GATEWAY_URL || !GATEWAY_TOKEN) {
    return { error: 'Gateway not configured' };
  }

  const url = new URL('/v1/chat/completions', GATEWAY_URL);
  
  const response = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${GATEWAY_TOKEN}`
    },
    body: JSON.stringify({
      model: 'default',
      messages,
      stream: false
    })
  });

  if (!response.ok) {
    const text = await response.text();
    return { error: `Gateway error: ${response.status} ${text}` };
  }

  const data = await response.json();
  return data;
}

// Request handler
async function handleRequest(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const pathname = decodeURIComponent(url.pathname);

  // CORS: Same-origin only (no cross-origin requests needed for localhost tool)
  // No Access-Control-Allow-Origin header = same-origin policy enforced by browser

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  try {
    // Serve UI
    if (pathname === '/' || pathname === '/index.html') {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(UI_HTML);
      return;
    }

    // API: List files
    if (pathname === '/api/files' && req.method === 'GET') {
      const dirPath = url.searchParams.get('path') || '';
      const result = listFiles(dirPath);
      if (result.error) {
        sendError(res, result.error, 404);
      } else {
        sendJSON(res, result);
      }
      return;
    }

    // API: Get/Save/Delete file
    if (pathname.startsWith('/api/files/')) {
      const filePath = pathname.slice('/api/files/'.length);

      if (req.method === 'GET') {
        const result = getFile(filePath);
        if (result.error) {
          sendError(res, result.error, 404);
        } else {
          sendJSON(res, result);
        }
        return;
      }

      if (req.method === 'PUT' || req.method === 'POST') {
        const body = await readBody(req);
        const { content } = JSON.parse(body);
        const result = saveFile(filePath, content);
        if (result.error) {
          sendError(res, result.error);
        } else {
          sendJSON(res, result);
        }
        return;
      }

    }

    // API: Chat proxy
    if (pathname === '/api/chat' && req.method === 'POST') {
      const body = await readBody(req);
      const { messages } = JSON.parse(body);
      const result = await proxyChat(messages);
      if (result.error) {
        sendError(res, result.error, 502);
      } else {
        sendJSON(res, result);
      }
      return;
    }

    // API: Config (safe subset)
    if (pathname === '/api/config' && req.method === 'GET') {
      sendJSON(res, {
        chatEnabled: !!(GATEWAY_URL && GATEWAY_TOKEN),
        folderName: FOLDER_NAME
      });
      return;
    }

    // 404
    sendError(res, 'Not found', 404);

  } catch (err) {
    console.error('Request error:', err);
    sendError(res, 'Internal server error', 500);
  }
}

// Start server
const server = http.createServer(handleRequest);

server.listen(PORT, HOST, () => {
  console.log(`📝 Markdown Editor with Chat`);
  console.log(`   URL: http://${HOST}:${PORT}`);
  console.log(`   Directory: ${MARKDOWN_DIR}`);
  console.log(`   Chat: ${GATEWAY_URL ? 'enabled' : 'disabled'}`);
  console.log('');
  console.log('Press Ctrl+C to stop');
});
