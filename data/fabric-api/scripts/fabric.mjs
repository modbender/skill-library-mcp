#!/usr/bin/env node
/**
 * Fabric API helper (Node.js)
 *
 * Cross-platform wrapper for calling the Fabric HTTP API without relying on bash.
 *
 * Usage:
 *   node scripts/fabric.mjs GET /v2/user/me
 *   node scripts/fabric.mjs POST /v2/notepads --json '{"name":"Hello","text":"World","parentId":"@alias::inbox"}'
 *   node scripts/fabric.mjs POST /v2/notepads --file payload.json
 *   cat payload.json | node scripts/fabric.mjs POST /v2/notepads
 *
 * Env:
 *   FABRIC_API_KEY  (required for API paths like /v2/..., unless --no-key)
 *   FABRIC_BASE     (optional, default: https://api.fabric.so)
 */

import fs from 'node:fs';
import { readFile } from 'node:fs/promises';
import process from 'node:process';

function printUsage(exitCode = 2) {
  const msg = `Usage:
  node scripts/fabric.mjs <METHOD> <PATH_OR_URL> [options]

Examples:
  node scripts/fabric.mjs GET /v2/user/me

  node scripts/fabric.mjs POST /v2/notepads --json '{"name":"Test","text":"Hello","parentId":"@alias::inbox"}'

  node scripts/fabric.mjs POST /v2/notepads --file payload.json

  cat payload.json | node scripts/fabric.mjs POST /v2/notepads

Options:
  --base <url>          Base URL for API paths (default: $FABRIC_BASE or https://api.fabric.so)
  --json <string>       Send request body as a literal string (typically JSON)
  --file <path>         Send request body from a file (text by default)
  --raw                 With --file, send file bytes (octet-stream). Useful for presigned PUT uploads.
  --header "K: V"       Add a header (repeatable)
  --no-key              Do not attach X-Api-Key (useful for presigned URLs)
  --with-key            Force attaching X-Api-Key even for absolute URLs
  --pretty              Pretty-print JSON responses
  --no-pretty           Do not pretty-print JSON responses
  -h, --help            Show this help

Notes:
  * If <PATH_OR_URL> is an absolute URL (https://...), the script will NOT send X-Api-Key unless you pass --with-key.
  * For relative paths (e.g. /v2/notepads), the script requires FABRIC_API_KEY unless --no-key.
`;
  process.stderr.write(msg);
  process.exit(exitCode);
}

function isAbsoluteUrl(s) {
  return /^https?:\/\//i.test(s);
}

function joinBase(base, path) {
  const b = base.replace(/\/+$/, '');
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${b}${p}`;
}

function parseHeaderLine(line) {
  const idx = line.indexOf(':');
  if (idx === -1) {
    throw new Error(`Invalid --header value (missing ':'): ${line}`);
  }
  const key = line.slice(0, idx).trim();
  const value = line.slice(idx + 1).trim();
  if (!key) throw new Error(`Invalid --header key: ${line}`);
  return [key, value];
}

async function readStdinAsBuffer() {
  const chunks = [];
  for await (const chunk of process.stdin) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  return Buffer.concat(chunks);
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv.length === 0 || argv.includes('-h') || argv.includes('--help')) {
    printUsage(0);
  }

  const method = (argv[0] || '').toUpperCase();
  const target = argv[1];
  if (!method || !target) {
    printUsage(2);
  }

  let base = process.env.FABRIC_BASE || 'https://api.fabric.so';
  let jsonBody = null;
  let filePath = null;
  let raw = false;
  let noKey = false;
  let withKey = false;

  // Default pretty-print when stdout is a TTY
  let pretty = process.stdout.isTTY;

  const extraHeaders = [];

  for (let i = 2; i < argv.length; i += 1) {
    const a = argv[i];

    if (a === '--base') {
      base = argv[++i];
      if (!base) throw new Error('Missing value for --base');
      continue;
    }

    if (a === '--json') {
      jsonBody = argv[++i];
      if (jsonBody == null) throw new Error('Missing value for --json');
      continue;
    }

    if (a === '--file') {
      filePath = argv[++i];
      if (!filePath) throw new Error('Missing value for --file');
      continue;
    }

    if (a === '--raw') {
      raw = true;
      continue;
    }

    if (a === '--header') {
      const h = argv[++i];
      if (!h) throw new Error('Missing value for --header');
      extraHeaders.push(parseHeaderLine(h));
      continue;
    }

    if (a === '--no-key') {
      noKey = true;
      continue;
    }

    if (a === '--with-key') {
      withKey = true;
      continue;
    }

    if (a === '--pretty') {
      pretty = true;
      continue;
    }

    if (a === '--no-pretty') {
      pretty = false;
      continue;
    }

    // Unknown option
    throw new Error(`Unknown option: ${a}`);
  }

  const abs = isAbsoluteUrl(target);
  const url = abs ? target : joinBase(base, target);

  // Default: don't leak API keys to presigned URLs
  const shouldSendKey = !noKey && (!abs || withKey);

  const apiKey = process.env.FABRIC_API_KEY;
  if (shouldSendKey && (!apiKey || apiKey.trim() === '')) {
    process.stderr.write('ERROR: FABRIC_API_KEY is not set.\n');
    process.stderr.write('Set it in the environment or via OpenClaw skills config (skills.entries.fabric-api.apiKey).\n');
    process.exit(2);
  }

  let body = undefined;
  let bodyIsStream = false;
  let inferredContentType = null;

  if (jsonBody != null) {
    body = jsonBody;
    inferredContentType = 'application/json';
  } else if (filePath != null) {
    if (raw) {
      body = fs.createReadStream(filePath);
      bodyIsStream = true;
      inferredContentType = 'application/octet-stream';
    } else {
      body = await readFile(filePath, 'utf8');
      inferredContentType = 'application/json';
    }
  } else if (!process.stdin.isTTY) {
    const buf = await readStdinAsBuffer();
    if (buf.length > 0) {
      // Assume JSON-by-default when piping into an API call.
      body = buf.toString('utf8');
      inferredContentType = 'application/json';
    }
  }

  const headers = new Headers();

  // User-provided headers first (so our defaults can be overridden if desired).
  for (const [k, v] of extraHeaders) {
    headers.set(k, v);
  }

  if (!headers.has('accept')) {
    headers.set('Accept', 'application/json');
  }

  if (shouldSendKey) {
    headers.set('X-Api-Key', apiKey);
  }

  if (body !== undefined && !headers.has('content-type') && inferredContentType) {
    headers.set('Content-Type', inferredContentType);
  }

  const fetchOpts = {
    method,
    headers,
    body,
  };

  // Node fetch requires this when streaming request bodies.
  if (bodyIsStream) {
    fetchOpts.duplex = 'half';
  }

  let res;
  try {
    res = await fetch(url, fetchOpts);
  } catch (err) {
    process.stderr.write(`ERROR: request failed: ${err?.message || String(err)}\n`);
    process.exit(1);
  }

  const text = await res.text();
  const contentType = res.headers.get('content-type') || '';
  const isJson = /(^|\s|;)application\/(json|[^;]+\+json)(;|\s|$)/i.test(contentType);

  if (!res.ok) {
    process.stderr.write(`HTTP ${res.status} ${res.statusText}\n`);
    if (text) process.stdout.write(text);
    process.exit(1);
  }

  if (!text) return;

  if (pretty && isJson) {
    try {
      const obj = JSON.parse(text);
      process.stdout.write(JSON.stringify(obj, null, 2));
      if (process.stdout.isTTY) process.stdout.write('\n');
      return;
    } catch {
      // Fall back to raw text
    }
  }

  process.stdout.write(text);
  if (process.stdout.isTTY) process.stdout.write('\n');
}

main().catch((err) => {
  process.stderr.write(`ERROR: ${err?.stack || err?.message || String(err)}\n`);
  process.exit(1);
});
