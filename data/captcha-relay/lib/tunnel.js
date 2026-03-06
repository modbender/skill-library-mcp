/**
 * Tunnel management for public URL access
 *
 * Strategies (in order):
 *   1. localtunnel (via npx) — free, no install, works well
 *   2. cloudflared — Cloudflare's tunnel, heavier binary
 *   3. Local IP fallback — LAN only
 *
 * NOTE: For production, Tailscale is recommended. See TAILSCALE.md.
 * With Tailscale, no tunnel is needed — the relay server is directly
 * accessible via Tailscale IP from any device on the same Tailnet.
 */
const { spawn } = require('child_process');
const os = require('os');

/**
 * Start a tunnel to expose localPort publicly.
 * @param {number} localPort
 * @param {object} opts
 * @param {string} opts.method - 'localtunnel' | 'cloudflared' | 'auto' (default: 'auto')
 */
function startTunnel(localPort, opts = {}) {
  const method = opts.method || 'auto';

  if (method === 'cloudflared') return startCloudflared(localPort);
  if (method === 'localtunnel') return startLocaltunnel(localPort);

  // Auto: try localtunnel first, fall back to cloudflared, then local IP
  return startLocaltunnel(localPort).catch(() =>
    startCloudflared(localPort)
  );
}

function startLocaltunnel(localPort) {
  return new Promise((resolve, reject) => {
    const proc = spawn('npx', ['localtunnel', '--port', String(localPort)], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let resolved = false;
    const timer = setTimeout(() => {
      if (!resolved) {
        resolved = true;
        proc.kill();
        reject(new Error('localtunnel timeout'));
      }
    }, 30000);

    function checkOutput(data) {
      const text = data.toString();
      const match = text.match(/(https:\/\/[a-z0-9-]+\.loca\.lt)/);
      if (match && !resolved) {
        resolved = true;
        clearTimeout(timer);
        resolve({ url: match[1], process: proc, isLocal: false, method: 'localtunnel' });
      }
    }

    proc.stdout.on('data', checkOutput);
    proc.stderr.on('data', checkOutput);

    proc.on('error', () => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timer);
        reject(new Error('localtunnel not available'));
      }
    });

    proc.on('exit', (code) => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timer);
        reject(new Error(`localtunnel exited with code ${code}`));
      }
    });
  });
}

function startCloudflared(localPort) {
  return new Promise((resolve, reject) => {
    const proc = spawn('cloudflared', ['tunnel', '--url', `http://localhost:${localPort}`], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let resolved = false;
    const timer = setTimeout(() => {
      if (!resolved) {
        resolved = true;
        proc.kill();
        // Final fallback: local IP
        const localUrl = `http://${getLocalIp()}:${localPort}`;
        resolve({ url: localUrl, process: null, isLocal: true, method: 'local' });
      }
    }, 15000);

    function checkOutput(data) {
      const text = data.toString();
      const match = text.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/);
      if (match && !resolved) {
        resolved = true;
        clearTimeout(timer);
        resolve({ url: match[0], process: proc, isLocal: false, method: 'cloudflared' });
      }
    }

    proc.stdout.on('data', checkOutput);
    proc.stderr.on('data', checkOutput);

    proc.on('error', () => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timer);
        const localUrl = `http://${getLocalIp()}:${localPort}`;
        resolve({ url: localUrl, process: null, isLocal: true, method: 'local' });
      }
    });
  });
}

function stopTunnel(tunnel) {
  if (tunnel && tunnel.process) {
    tunnel.process.kill();
  }
}

function getTailscaleIp() {
  try {
    const { execSync } = require('child_process');
    const ip = execSync('tailscale ip -4 2>/dev/null', { timeout: 3000 }).toString().trim();
    if (/^100\./.test(ip)) return ip;
  } catch {}
  return null;
}

function getLocalIp() {
  const nets = os.networkInterfaces();
  for (const name of Object.keys(nets)) {
    for (const net of nets[name]) {
      if (net.family === 'IPv4' && !net.internal) {
        return net.address;
      }
    }
  }
  return '127.0.0.1';
}

module.exports = { startTunnel, stopTunnel, getLocalIp, getTailscaleIp };
