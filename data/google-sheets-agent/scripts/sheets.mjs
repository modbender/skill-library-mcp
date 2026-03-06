#!/usr/bin/env node
/**
 * google-sheets-agent — Zero-dep Google Sheets via service account.
 *
 * Auth: SA JSON key from 1Password or GOOGLE_SA_KEY_JSON env var.
 *
 * Usage:
 *   node sheets.mjs list                          # list sheets shared with SA
 *   node sheets.mjs read <sheetId> [range]         # read cells (default: Sheet1!A:ZZ)
 *   node sheets.mjs meta <sheetId>                 # sheet metadata (tabs, titles)
 *   node sheets.mjs append <sheetId> <range>       # append rows from stdin JSON [[r1],[r2]]
 *   node sheets.mjs write <sheetId> <range>        # overwrite range from stdin JSON [[r1],[r2]]
 *
 * Output: JSON to stdout. Logs to stderr.
 */

import https from 'https';
import crypto from 'crypto';
import { exec as execCb } from 'child_process';
import { promisify } from 'util';
const execAsync = promisify(execCb);

// ── SA Auth ─────────────────────────────────────────────────────────────

let _token = null;
let _tokenExp = 0;

async function loadSAKey() {
  if (process.env.GOOGLE_SA_KEY_JSON) return JSON.parse(process.env.GOOGLE_SA_KEY_JSON);
  if (process.env.GOOGLE_SA_KEY_FILE) {
    const fs = await import('fs');
    return JSON.parse(fs.readFileSync(process.env.GOOGLE_SA_KEY_FILE, 'utf8'));
  }
  // Fallback: 1Password
  try {
    const { stdout } = await execAsync('op document get "Google Service Account - sheets-reader" --vault AbundanceM');
    return JSON.parse(stdout);
  } catch {
    throw new Error(
      'No SA key found. Set GOOGLE_SA_KEY_JSON, GOOGLE_SA_KEY_FILE, or ensure `op` CLI is configured.'
    );
  }
}

async function getAccessToken(scope = 'https://www.googleapis.com/auth/spreadsheets') {
  if (_token && Date.now() < _tokenExp - 60000) return _token;
  const key = await loadSAKey();
  const now = Math.floor(Date.now() / 1000);
  const header = Buffer.from(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).toString('base64url');
  const payload = Buffer.from(JSON.stringify({
    iss: key.client_email, scope, aud: 'https://oauth2.googleapis.com/token',
    iat: now, exp: now + 3600,
  })).toString('base64url');
  const sig = crypto.sign('RSA-SHA256', Buffer.from(`${header}.${payload}`), key.private_key).toString('base64url');
  const jwt = `${header}.${payload}.${sig}`;
  const body = `grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=${jwt}`;
  const res = await httpReq('https://oauth2.googleapis.com/token', {
    method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  }, body);
  const tok = JSON.parse(res);
  if (!tok.access_token) throw new Error(`Token exchange failed: ${res}`);
  _token = tok.access_token;
  _tokenExp = Date.now() + tok.expires_in * 1000;
  return _token;
}

// ── HTTP helpers ────────────────────────────────────────────────────────

function httpReq(url, opts = {}, body = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, opts, res => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => {
        if (res.statusCode >= 400) reject(new Error(`HTTP ${res.statusCode}: ${d}`));
        else resolve(d);
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function sheetsApi(path, method = 'GET', body = null) {
  const token = await getAccessToken();
  const url = `https://sheets.googleapis.com/v4/spreadsheets/${path}`;
  const opts = { method, headers: { Authorization: `Bearer ${token}` } };
  if (body) opts.headers['Content-Type'] = 'application/json';
  return JSON.parse(await httpReq(url, opts, body ? JSON.stringify(body) : null));
}

async function driveApi(path) {
  const token = await getAccessToken('https://www.googleapis.com/auth/drive.readonly');
  const url = `https://www.googleapis.com/drive/v3/${path}`;
  return JSON.parse(await httpReq(url, { headers: { Authorization: `Bearer ${token}` } }));
}

// ── Commands ────────────────────────────────────────────────────────────

async function listSheets() {
  const res = await driveApi("files?q=mimeType='application/vnd.google-apps.spreadsheet'&fields=files(id,name,modifiedTime)");
  return res.files || [];
}

async function readSheet(sheetId, range = 'Sheet1!A:ZZ') {
  return sheetsApi(`${sheetId}/values/${encodeURIComponent(range)}`);
}

async function getMeta(sheetId) {
  const res = await sheetsApi(sheetId);
  return {
    title: res.properties?.title,
    sheets: (res.sheets || []).map(s => ({
      title: s.properties.title,
      sheetId: s.properties.sheetId,
      rowCount: s.properties.gridProperties?.rowCount,
      colCount: s.properties.gridProperties?.columnCount,
    })),
  };
}

async function appendRows(sheetId, range, rows) {
  return sheetsApi(
    `${sheetId}/values/${encodeURIComponent(range)}:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS`,
    'POST', { values: rows }
  );
}

async function writeRange(sheetId, range, rows) {
  return sheetsApi(
    `${sheetId}/values/${encodeURIComponent(range)}?valueInputOption=USER_ENTERED`,
    'PUT', { values: rows }
  );
}

// ── CLI ─────────────────────────────────────────────────────────────────

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString());
}

async function main() {
  const [cmd, ...args] = process.argv.slice(2);
  let result;
  switch (cmd) {
    case 'list':
      result = await listSheets();
      break;
    case 'read':
      if (!args[0]) { console.error('Usage: sheets.mjs read <sheetId> [range]'); process.exit(1); }
      result = await readSheet(args[0], args[1]);
      break;
    case 'meta':
      if (!args[0]) { console.error('Usage: sheets.mjs meta <sheetId>'); process.exit(1); }
      result = await getMeta(args[0]);
      break;
    case 'append':
      if (!args[0] || !args[1]) { console.error('Usage: echo \'[[...]]\'| sheets.mjs append <sheetId> <range>'); process.exit(1); }
      result = await appendRows(args[0], args[1], await readStdin());
      break;
    case 'write':
      if (!args[0] || !args[1]) { console.error('Usage: echo \'[[...]]\'| sheets.mjs write <sheetId> <range>'); process.exit(1); }
      result = await writeRange(args[0], args[1], await readStdin());
      break;
    default:
      console.error('Commands: list, read, meta, append, write');
      process.exit(1);
  }
  console.log(JSON.stringify(result, null, 2));
}

main().catch(e => { console.error(e.message); process.exit(1); });
