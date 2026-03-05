#!/usr/bin/env node
/**
 * RMN Visualizer — One-shot: start server + tunnel, return public URL
 * Usage: node scripts/launch.js
 * 
 * 1. Starts local HTTP server with D3 visualization
 * 2. Opens Cloudflare Tunnel (free, no account needed)
 * 3. Prints public URL to stdout for agent to relay to chat
 */

const { spawn, execSync } = require('child_process');
const path = require('path');

const PORT = parseInt(process.env.RMN_PORT || '3459');
const SERVE_SCRIPT = path.join(__dirname, 'serve.js');

// Check cloudflared
let hasCF = false;
try { execSync('which cloudflared', { stdio: 'ignore' }); hasCF = true; } catch {}

if (!hasCF) {
  console.error('❌ cloudflared not found. Install: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/');
  console.error('   Or run manually: node ' + SERVE_SCRIPT);
  process.exit(1);
}

// Start serve.js
const server = spawn('node', [SERVE_SCRIPT], {
  env: { ...process.env, RMN_PORT: String(PORT) },
  stdio: ['ignore', 'pipe', 'pipe'],
});

server.stdout.on('data', d => process.stderr.write(d));
server.stderr.on('data', d => process.stderr.write(d));

// Wait for server to be ready
setTimeout(() => {
  // Start cloudflared tunnel
  const tunnel = spawn('cloudflared', ['tunnel', '--url', `http://localhost:${PORT}`], {
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  let urlFound = false;

  function checkForURL(data) {
    const text = data.toString();
    const match = text.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/);
    if (match && !urlFound) {
      urlFound = true;
      // Print ONLY the URL to stdout (agent captures this)
      console.log(match[0]);
    }
    process.stderr.write(data);
  }

  tunnel.stdout.on('data', checkForURL);
  tunnel.stderr.on('data', checkForURL);

  // Timeout after 30s
  setTimeout(() => {
    if (!urlFound) {
      console.error('❌ Tunnel timeout — could not get public URL in 30s');
      process.exit(1);
    }
  }, 30000);

  // Cleanup on exit
  process.on('SIGINT', () => { tunnel.kill(); server.kill(); process.exit(0); });
  process.on('SIGTERM', () => { tunnel.kill(); server.kill(); process.exit(0); });

}, 2000);
