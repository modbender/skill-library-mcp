#!/usr/bin/env node
// Freqtrade REST API client - shared helper
import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

// Auto-load .env files (same logic as aicoin-api.mjs)
function loadEnv() {
  const candidates = [
    resolve(process.cwd(), '.env'),
    resolve(process.env.HOME || '', '.openclaw', 'workspace', '.env'),
    resolve(process.env.HOME || '', '.openclaw', '.env'),
  ];
  for (const file of candidates) {
    if (!existsSync(file)) continue;
    try {
      for (const line of readFileSync(file, 'utf-8').split('\n')) {
        const t = line.trim();
        if (!t || t.startsWith('#')) continue;
        const eq = t.indexOf('=');
        if (eq < 1) continue;
        const key = t.slice(0, eq).trim();
        let val = t.slice(eq + 1).trim();
        if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) val = val.slice(1, -1);
        if (!process.env[key]) process.env[key] = val;
      }
    } catch {}
  }
}
loadEnv();

const BASE = process.env.FREQTRADE_URL || 'http://localhost:8080';
const USER = process.env.FREQTRADE_USERNAME || 'freqtrader';
const PASS = process.env.FREQTRADE_PASSWORD || '';

const auth = 'Basic ' + Buffer.from(`${USER}:${PASS}`).toString('base64');

export async function ftGet(path, params = {}) {
  const url = new URL(`/api/v1/${path}`, BASE);
  for (const [k, v] of Object.entries(params)) {
    if (v != null) url.searchParams.set(k, String(v));
  }
  const res = await fetch(url, { headers: { Authorization: auth }, signal: AbortSignal.timeout(30000) });
  if (!res.ok) throw new Error(`Freqtrade ${res.status}: ${await res.text()}`);
  return res.json();
}

export async function ftPost(path, body = {}) {
  const res = await fetch(new URL(`/api/v1/${path}`, BASE), {
    method: 'POST',
    headers: { Authorization: auth, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(30000),
  });
  if (!res.ok) throw new Error(`Freqtrade ${res.status}: ${await res.text()}`);
  return res.json();
}

export async function ftDelete(path) {
  const res = await fetch(new URL(`/api/v1/${path}`, BASE), {
    method: 'DELETE',
    headers: { Authorization: auth },
    signal: AbortSignal.timeout(30000),
  });
  if (!res.ok) throw new Error(`Freqtrade ${res.status}: ${await res.text()}`);
  return res.json();
}

// CLI helper
export function ftCli(handlers) {
  const [action, ...rest] = process.argv.slice(2);
  if (!action || !handlers[action]) {
    console.log(`Usage: node <script> <action> [json-params]\nActions: ${Object.keys(handlers).join(', ')}`);
    process.exit(1);
  }
  const params = rest.length ? JSON.parse(rest.join(' ')) : {};
  handlers[action](params).then(r => console.log(JSON.stringify(r, null, 2))).catch(e => {
    console.error(e.message); process.exit(1);
  });
}
