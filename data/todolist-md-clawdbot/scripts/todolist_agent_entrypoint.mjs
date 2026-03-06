#!/usr/bin/env node
/**
 * todolist_agent_entrypoint.mjs
 *
 * Single-entry helper for todolist-md agent workflows against Google Drive.
 *
 * What it does:
 * - Download a markdown todo file from Drive (by fileId)
 * - (Optional) run an LLM step elsewhere and feed edited Markdown back here
 * - Safely write local changes with atomic write
 * - Upload updates back to the SAME Drive fileId (no duplicates)
 * - Revision gate via headRevisionId to avoid overwriting while you edit in Chrome
 *
 * Auth options:
 *   1) Managed OAuth (recommended): provide CLIENT_ID and CLIENT_SECRET.
 *      - First run prints an auth URL (copy to Telegram, open in browser, approve)
 *      - Paste the returned code back with --authCode
 *      - Script stores refresh_token in REFRESH_TOKEN_FILE (default: /root/clawd/.secrets/todolist_drive_oauth.json)
 *   2) Provide ACCESS_TOKEN directly (short-lived): ACCESS_TOKEN=...
 *   3) Provide REFRESH_TOKEN + CLIENT_ID + CLIENT_SECRET
 *      - REFRESH_TOKEN can be exported via: `gog auth tokens export <email> --out=...`
 */

import fs from 'node:fs';
import path from 'node:path';

function must(v, name) {
  if (!v) throw new Error(`Missing required env/arg: ${name}`);
  return v;
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const [k, v] = a.slice(2).split('=');
      if (v !== undefined) out[k] = v;
      else out[k] = argv[++i];
    } else {
      out._.push(a);
    }
  }
  return out;
}

function atomicWriteFileSync(targetPath, content) {
  const dir = path.dirname(targetPath);
  const base = path.basename(targetPath);
  const tmp = path.join(dir, `.${base}.tmp.${process.pid}`);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(tmp, content, 'utf8');
  fs.renameSync(tmp, targetPath);
}

async function oauthAccessTokenFromRefresh({ refreshToken, clientId, clientSecret }) {
  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: 'refresh_token',
    }),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(`Token exchange failed (${res.status}): ${JSON.stringify(json)}`);
  return json.access_token;
}

function buildAuthUrl({ clientId, scopes }) {
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: 'urn:ietf:wg:oauth:2.0:oob',
    response_type: 'code',
    scope: scopes.join(' '),
    access_type: 'offline',
    prompt: 'consent',
  });
  return `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
}

async function exchangeAuthCodeForTokens({ clientId, clientSecret, code }) {
  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      code,
      redirect_uri: 'urn:ietf:wg:oauth:2.0:oob',
      grant_type: 'authorization_code',
    }),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(`Auth code exchange failed (${res.status}): ${JSON.stringify(json)}`);
  return json;
}

async function driveGetMetadata({ fileId, accessToken }) {
  const url = new URL(`https://www.googleapis.com/drive/v3/files/${fileId}`);
  url.searchParams.set('fields', 'id,name,mimeType,modifiedTime,headRevisionId,size');
  const res = await fetch(url, { headers: { authorization: `Bearer ${accessToken}` } });
  const json = await res.json();
  if (!res.ok) throw new Error(`Drive metadata failed (${res.status}): ${JSON.stringify(json)}`);
  return json;
}

async function driveDownloadText({ fileId, accessToken }) {
  const url = new URL(`https://www.googleapis.com/drive/v3/files/${fileId}`);
  url.searchParams.set('alt', 'media');
  const res = await fetch(url, { headers: { authorization: `Bearer ${accessToken}` } });
  if (!res.ok) throw new Error(`Drive download failed (${res.status}): ${await res.text()}`);
  return await res.text();
}

async function driveUpdateText({ fileId, accessToken, name, mimeType, text }) {
  // multipart/related PATCH files.update
  const boundary = '----todolistBoundary' + Math.random().toString(16).slice(2);
  const metadata = { name, mimeType };

  const body =
    `--${boundary}\r\n` +
    `Content-Type: application/json; charset=UTF-8\r\n\r\n` +
    `${JSON.stringify(metadata)}\r\n` +
    `--${boundary}\r\n` +
    `Content-Type: ${mimeType}\r\n\r\n` +
    text + `\r\n` +
    `--${boundary}--\r\n`;

  const res = await fetch(
    `https://www.googleapis.com/upload/drive/v3/files/${fileId}?uploadType=multipart`,
    {
      method: 'PATCH',
      headers: {
        authorization: `Bearer ${accessToken}`,
        'content-type': `multipart/related; boundary=${boundary}`,
      },
      body,
    }
  );
  const out = await res.text();
  if (!res.ok) throw new Error(`Drive update failed (${res.status}): ${out}`);
  return out;
}

function applyEditsPlaceholder(originalText) {
  // Placeholder: integrate with your LLM workflow.
  // For now, no-op.
  return originalText;
}

async function ensureManagedOAuth({ refreshTokenFile, clientId, clientSecret, authCode }) {
  // Returns { refresh_token } when available.
  if (fs.existsSync(refreshTokenFile)) {
    const existing = JSON.parse(fs.readFileSync(refreshTokenFile, 'utf8'));
    if (existing?.refresh_token) return existing;
  }

  const scopes = ['https://www.googleapis.com/auth/drive'];

  if (!authCode) {
    const url = buildAuthUrl({ clientId, scopes });
    return {
      needsAuth: true,
      authUrl: url,
      refreshTokenFile,
      scope: scopes,
      howTo: `Open the URL, approve, then rerun with: --authCode <CODE>`
    };
  }

  const tokens = await exchangeAuthCodeForTokens({ clientId, clientSecret, code: authCode });
  if (!tokens.refresh_token) {
    throw new Error('No refresh_token returned. Try again with prompt=consent and ensure you approved access.');
  }
  const toSave = {
    created_at: new Date().toISOString(),
    scopes,
    refresh_token: tokens.refresh_token,
  };
  fs.mkdirSync(path.dirname(refreshTokenFile), { recursive: true });
  atomicWriteFileSync(refreshTokenFile, JSON.stringify(toSave, null, 2) + '\n');
  try { fs.chmodSync(refreshTokenFile, 0o600); } catch {}
  return toSave;
}

async function main() {
  const args = parseArgs(process.argv);

  const fileId = must(args.fileId || process.env.TODO_FILE_ID, 'fileId (or TODO_FILE_ID)');
  const outPath = args.out || process.env.OUT_PATH || `outputs/todolist-md/${fileId}.md`;

  // Auth inputs
  const refreshTokenFile = args.refreshTokenFile || process.env.REFRESH_TOKEN_FILE || '/root/clawd/.secrets/todolist_drive_oauth.json';
  const clientId = args.clientId || process.env.CLIENT_ID;
  const clientSecret = args.clientSecret || process.env.CLIENT_SECRET;
  const authCode = args.authCode || process.env.AUTH_CODE;

  let accessToken = process.env.ACCESS_TOKEN;

  // Managed OAuth path (recommended): if clientId/secret present, we can bootstrap refresh token.
  if (!accessToken && clientId && clientSecret) {
    const managed = await ensureManagedOAuth({ refreshTokenFile, clientId, clientSecret, authCode });
    if (managed.needsAuth) {
      console.log(JSON.stringify({ ok: false, action: 'needs_auth', ...managed }, null, 2));
      process.exitCode = 2;
      return;
    }
    accessToken = await oauthAccessTokenFromRefresh({
      refreshToken: managed.refresh_token,
      clientId,
      clientSecret,
    });
  }

  // Alternative path: supply refresh token directly
  if (!accessToken) {
    const refreshToken = process.env.REFRESH_TOKEN;
    if (refreshToken) {
      must(clientId, 'CLIENT_ID');
      must(clientSecret, 'CLIENT_SECRET');
      accessToken = await oauthAccessTokenFromRefresh({ refreshToken, clientId, clientSecret });
    }
  }

  must(accessToken, 'ACCESS_TOKEN (or managed OAuth via CLIENT_ID/CLIENT_SECRET)');

  // Revision gate: capture revision before download and before upload
  const meta1 = await driveGetMetadata({ fileId, accessToken });
  const text = await driveDownloadText({ fileId, accessToken });

  // Save local copy (atomic)
  atomicWriteFileSync(outPath, text);

  // Apply edits (placeholder)
  const edited = applyEditsPlaceholder(text);

  // If no change, skip upload
  if (edited === text) {
    console.log(JSON.stringify({ ok: true, action: 'noop', fileId, name: meta1.name, headRevisionId: meta1.headRevisionId }, null, 2));
    return;
  }

  const meta2 = await driveGetMetadata({ fileId, accessToken });
  if (meta2.headRevisionId && meta1.headRevisionId && meta2.headRevisionId !== meta1.headRevisionId) {
    console.log(JSON.stringify({
      ok: false,
      action: 'skip_due_to_remote_change',
      fileId,
      name: meta2.name,
      before: meta1.headRevisionId,
      now: meta2.headRevisionId,
    }, null, 2));
    process.exitCode = 3;
    return;
  }

  const mimeType = meta1.mimeType || 'text/markdown';
  const name = meta1.name || 'todo.md';
  const result = await driveUpdateText({ fileId, accessToken, name, mimeType, text: edited });
  console.log(JSON.stringify({ ok: true, action: 'updated', fileId, name, result }, null, 2));
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
