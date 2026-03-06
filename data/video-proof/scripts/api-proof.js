#!/usr/bin/env node
/**
 * api-proof.js — Record proof for API/backend changes (no browser needed)
 *
 * Usage:
 *   node api-proof.js --spec api-spec.yaml --output ./proof-artifacts
 *   node api-proof.js --start "npm start" --port 3000 --request "GET /api/health" --output ./artifacts
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const yaml = require('yaml');
const http = require('http');
const https = require('https');

const args = process.argv.slice(2);

function getArg(name) {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 && idx + 1 < args.length ? args[idx + 1] : null;
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function httpRequest(method, url, body, headers) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const mod = parsed.protocol === 'https:' ? https : http;
    const opts = {
      hostname: parsed.hostname,
      port: parsed.port,
      path: parsed.pathname + parsed.search,
      method,
      headers: headers || {},
    };
    const req = mod.request(opts, res => {
      let data = '';
      res.on('data', c => (data += c));
      res.on('end', () => resolve({ statusCode: res.statusCode, body: data }));
    });
    req.on('error', reject);
    req.setTimeout(10000, () => { req.destroy(new Error('Request timeout')); });
    if (body) req.write(typeof body === 'string' ? body : JSON.stringify(body));
    req.end();
  });
}

async function waitForPort(port, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      execSync(`curl -sf -o /dev/null http://localhost:${port}`, { timeout: 5000 });
      return true;
    } catch {
      await sleep(1000);
    }
  }
  return false;
}

async function main() {
  const specPath = getArg('spec');
  const outputDir = getArg('output') || './proof-artifacts';
  fs.mkdirSync(outputDir, { recursive: true });
  let spec;

  if (specPath) {
    spec = yaml.parse(fs.readFileSync(specPath, 'utf8'));
    if (spec.proof) spec = spec.proof;
  } else {
    spec = {
      start_command: getArg('start'),
      start_port: parseInt(getArg('port') || '3000'),
      base_url: getArg('url') || `http://localhost:${getArg('port') || 3000}`,
      requests: [],
      timeout: parseInt(getArg('timeout') || '30000'),
    };
    for (let i = 0; i < args.length; i++) {
      if (args[i] === '--request' && args[i + 1]) {
        const parts = args[++i].split(' ');
        spec.requests.push({ method: parts[0], path: parts.slice(1).join(' ') });
      }
    }
  }

  // --- Start server ---
  let serverProc = null;
  if (spec.start_command) {
    const port = spec.start_port || 3000;
    const timeout = spec.start_timeout || spec.timeout || 30000;

    console.log(`[api-proof] Starting: ${spec.start_command}`);
    serverProc = spawn('sh', ['-c', spec.start_command], {
      stdio: 'pipe',
      detached: true,
      env: { ...process.env, PORT: String(port) },
    });
    serverProc.stdout?.on('data', d => process.stdout.write(`[server] ${d}`));
    serverProc.stderr?.on('data', d => process.stderr.write(`[server] ${d}`));

    console.log(`[api-proof] Waiting for port ${port}...`);
    const ready = await waitForPort(port, timeout);
    if (!ready) {
      console.error(`[api-proof] Server not ready within ${Math.round(timeout / 1000)}s`);
      if (serverProc) try { process.kill(-serverProc.pid, 'SIGTERM'); } catch {}
      process.exit(1);
    }
    console.log(`[api-proof] Server ready`);
  }

  const baseUrl = spec.base_url || `http://localhost:${spec.start_port || 3000}`;
  const results = [];

  // --- Execute requests ---
  for (let i = 0; i < (spec.requests || []).length; i++) {
    const req = spec.requests[i];
    const method = (req.method || 'GET').toUpperCase();
    const url = `${baseUrl}${req.path}`;
    const n = i + 1;

    console.log(`[api-proof] Request ${n}: ${method} ${req.path}`);
    try {
      const res = await httpRequest(method, url, req.body, req.headers);
      const result = {
        request: n,
        method,
        path: req.path,
        status: res.statusCode,
        body: res.body.slice(0, 2000),
        ok: res.statusCode < 400,
      };

      if (req.assert_status && res.statusCode !== req.assert_status) {
        result.ok = false;
        result.error = `Expected status ${req.assert_status}, got ${res.statusCode}`;
      }
      if (req.assert_body_contains && !res.body.includes(req.assert_body_contains)) {
        result.ok = false;
        result.error = `Response body missing: "${req.assert_body_contains}"`;
      }

      results.push(result);
      console.log(`[api-proof] ${result.ok ? '✅' : '❌'} ${method} ${req.path} → ${res.statusCode}`);
    } catch (err) {
      results.push({ request: n, method, path: req.path, ok: false, error: err.message });
      console.log(`[api-proof] ❌ ${method} ${req.path} → ${err.message}`);
    }
  }

  // --- Generate summary ---
  const failed = results.some(r => !r.ok);

  let summary = `# API Proof\n\n`;
  summary += `**Status:** ${failed ? '❌ FAILED' : '✅ PASSED'}\n`;
  summary += `**Date:** ${new Date().toISOString()}\n`;
  summary += `**Requests:** ${results.length}\n\n`;
  summary += `## Results\n\n`;
  for (const r of results) {
    summary += `### ${r.ok ? '✅' : '❌'} ${r.method} ${r.path}\n\n`;
    summary += `- Status: ${r.status || 'N/A'}\n`;
    if (r.error) summary += `- Error: ${r.error}\n`;
    if (r.body) summary += `\n\`\`\`json\n${r.body}\n\`\`\`\n`;
    summary += '\n';
  }

  fs.writeFileSync(path.join(outputDir, 'api-proof.md'), summary);
  fs.writeFileSync(path.join(outputDir, 'api-results.json'), JSON.stringify(results, null, 2));

  console.log(`[api-proof] Summary: ${path.join(outputDir, 'api-proof.md')}`);
  console.log(`[api-proof] ${failed ? 'FAILED' : 'PASSED'} — ${results.length} requests`);

  if (serverProc) try { process.kill(-serverProc.pid, 'SIGTERM'); } catch {}
  process.exit(failed ? 1 : 0);
}

main().catch(err => {
  console.error('[api-proof] Fatal:', err.message);
  process.exit(1);
});
