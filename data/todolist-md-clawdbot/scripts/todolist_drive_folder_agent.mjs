#!/usr/bin/env node
/**
 * todolist_drive_folder_agent.mjs
 *
 * Single-script folder runner (Google Drive) for todolist-md.
 *
 * Design goals:
 * - Node-only I/O pipeline (unified)
 * - Minimum tokens: do not call LLM unless a file changed; extract only open tasks
 * - Safe write-back: write ONLY into a dedicated bot section using <!-- bot: ... --> markers
 * - Avoid duplicates: overwrite-update via Drive API files.update(fileId)
 * - Avoid overwriting while you edit: revision gate via headRevisionId
 *
 * LLM integration mode (recommended here): two-stage handoff
 * - This script does NOT call any LLM.
 * - It can generate a compact LLM request JSON for OpenClaw (the agent runtime) to process.
 * - Then it can apply the produced suggestions JSON back into Drive.
 */

import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

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

async function ensureManagedOAuth({ refreshTokenFile, clientId, clientSecret, authCode }) {
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

function gogDriveLs(folderId) {
  const gogBin = process.env.GOG_BIN || '/home/linuxbrew/.linuxbrew/bin/gog';
  const envFile = '/root/clawd/.secrets/gog.env';

  let account = process.env.GOG_ACCOUNT || '';
  let pw = process.env.GOG_KEYRING_PASSWORD || '';

  if ((!account || !pw) && fs.existsSync(envFile)) {
    const text = fs.readFileSync(envFile, 'utf8');
    for (const line of text.split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z0-9_]+)=(.*)\s*$/);
      if (!m) continue;
      const k = m[1];
      let v = m[2];
      v = v.replace(/^"|"$/g, '');
      if (k === 'GOG_ACCOUNT' && !account) account = v;
      if (k === 'GOG_KEYRING_PASSWORD' && !pw) pw = v;
      if (k === 'GOG_BIN' && !process.env.GOG_BIN) process.env.GOG_BIN = v;
    }
  }

  if (!account) throw new Error('missing GOG_ACCOUNT (or set default via gog auth manage, or provide /root/clawd/.secrets/gog.env)');

  const cmd = [
    'sudo','-u','ubuntu','-H','env',
    `GOG_ACCOUNT=${account}`,
    `GOG_KEYRING_PASSWORD=${pw}`,
    gogBin,
    'drive','ls','--parent', folderId,'--json'
  ];
  const raw = execFileSync(cmd[0], cmd.slice(1), { encoding: 'utf8' });
  return JSON.parse(raw);
}

function loadJsonOrDefault(p, def) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return def; }
}

function saveJson(p, obj) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  atomicWriteFileSync(p, JSON.stringify(obj, null, 2) + '\n');
}

function extractOpenTasks(mdText, maxLines = 120) {
  const lines = mdText.split(/\r?\n/);
  const out = [];
  for (const line of lines) {
    if (line.startsWith('- [ ]')) out.push(line);
    if (out.length >= maxLines) break;
  }
  return out.join('\n');
}

function ensureBotSuggestedSection(mdText, sectionTitle, botBlock) {
  const marker = '<!-- bot: suggested -->';
  const titleLine = `## ${sectionTitle}`;

  if (mdText.includes(titleLine)) {
    const idx = mdText.indexOf(titleLine);
    const after = mdText.slice(idx);

    if (after.includes(marker)) {
      const start = mdText.indexOf(marker, idx);
      const before = mdText.slice(0, start);
      const rest = mdText.slice(start);
      const restLines = rest.split(/\r?\n/);

      const kept = [];
      kept.push(marker);
      const botLines = botBlock.split(/\r?\n/).filter(Boolean);
      kept.push(...botLines);

      let i = 1;
      for (; i < restLines.length; i++) {
        const ln = restLines[i];
        if (ln.startsWith('## ')) break;
      }
      const tail = restLines.slice(i).join('\n');
      return before + kept.join('\n') + (tail ? '\n' + tail : '') + (mdText.endsWith('\n') ? '\n' : '');
    }

    const lines = mdText.split(/\r?\n/);
    const out = [];
    for (let i = 0; i < lines.length; i++) {
      out.push(lines[i]);
      if (lines[i] === titleLine) {
        out.push(marker);
        out.push(...botBlock.split(/\r?\n/).filter(Boolean));
      }
    }
    return out.join('\n') + (mdText.endsWith('\n') ? '\n' : '');
  }

  const sep = mdText.endsWith('\n') ? '' : '\n';
  return mdText + sep + `\n${titleLine}\n${marker}\n${botBlock.trim()}\n`;
}

function sanitizeBotBlock(text, maxChars = 1200) {
  // Ensure we only write markdown list items / blockquotes; keep it short.
  const lines = String(text || '').split(/\r?\n/);
  const kept = [];
  for (const ln of lines) {
    if (ln.startsWith('- ') || ln.startsWith('  >') || ln.startsWith('> ')) kept.push(ln);
  }
  const out = kept.join('\n').trim();
  return out.slice(0, maxChars);
}

function fallbackBotSuggestedSection({ fileName, openTasks }) {
  const now = new Date().toISOString();
  const lines = [
    `- [ ] Review open tasks in ${fileName} (generated ${now})`,
  ];
  if (openTasks.trim()) {
    lines.push(`  > <!-- bot: note --> Open tasks sampled: ${openTasks.split(/\r?\n/).length}`);
  } else {
    lines.push(`  > <!-- bot: note --> No open tasks found`);
  }
  return lines.join('\n');
}

async function main() {
  const args = parseArgs(process.argv);

  const folderId = must(args.folderId || process.env.ROOT_FOLDER_ID, 'folderId (or ROOT_FOLDER_ID)');
  const statePath = args.state || process.env.STATE_PATH || 'outputs/todolist-md/folder_state.json';
  const requestOut = args.requestOut || process.env.REQUEST_OUT || 'outputs/todolist-md/llm_request.json';
  const suggestionsIn = args.suggestionsIn || process.env.SUGGESTIONS_IN || '';

  const sectionTitle = args.sectionTitle || process.env.BOT_SECTION_TITLE || 'Tasks (bot-suggested)';
  const dryRun = !!(args.dryRun || process.env.DRY_RUN);
  const onlyName = args.onlyName || process.env.ONLY_NAME; // e.g. vyond.md

  const mode = args.mode || process.env.MODE || (suggestionsIn ? 'apply' : 'prepare');

  const refreshTokenFile = args.refreshTokenFile || process.env.REFRESH_TOKEN_FILE || '/root/clawd/.secrets/todolist_drive_oauth.json';
  const clientId = args.clientId || process.env.CLIENT_ID;
  const clientSecret = args.clientSecret || process.env.CLIENT_SECRET;
  const authCode = args.authCode || process.env.AUTH_CODE;

  let accessToken = process.env.ACCESS_TOKEN;
  if (!accessToken) {
    must(clientId, 'CLIENT_ID');
    must(clientSecret, 'CLIENT_SECRET');
    const managed = await ensureManagedOAuth({ refreshTokenFile, clientId, clientSecret, authCode });
    if (managed.needsAuth) {
      console.log(JSON.stringify({ ok: false, action: 'needs_auth', ...managed }, null, 2));
      process.exitCode = 2;
      return;
    }
    accessToken = await oauthAccessTokenFromRefresh({ refreshToken: managed.refresh_token, clientId, clientSecret });
  }

  const listing = gogDriveLs(folderId);
  const files = listing.files || listing.items || [];

  const state = loadJsonOrDefault(statePath, { files: {}, lastRunAtUtc: null });
  const stFiles = state.files || {};

  let mdFiles = files.filter(f => (f?.mimeType === 'text/markdown') || (f?.name || '').endsWith('.md'));
  if (onlyName) mdFiles = mdFiles.filter(f => f.name === onlyName);

  const changed = [];
  for (const f of mdFiles) {
    const fid = f.id;
    if (!fid) continue;
    const prev = stFiles[fid] || {};
    if (prev.modifiedTime !== f.modifiedTime || prev.size !== f.size) {
      changed.push(f);
    }
  }

  const report = {
    ok: true,
    folderId,
    onlyName: onlyName || null,
    totalMarkdown: mdFiles.length,
    changedCount: changed.length,
    changed: changed.map(f => ({ id: f.id, name: f.name, modifiedTime: f.modifiedTime, size: f.size })),
    dryRun,
    mode,
  };

  // Track all seen files in state
  for (const f of mdFiles) {
    stFiles[f.id] = { modifiedTime: f.modifiedTime, size: f.size };
  }

  if (mode === 'prepare') {
    if (changed.length === 0) {
      state.lastRunAtUtc = new Date().toISOString();
      state.files = stFiles;
      saveJson(statePath, state);
      console.log(JSON.stringify({ ...report, action: 'noop' }, null, 2));
      return;
    }

    // Build compact LLM request payload for OpenClaw to process.
    const items = [];
    for (const f of changed) {
      const fileId = f.id;
      const text = await driveDownloadText({ fileId, accessToken });
      const openTasks = extractOpenTasks(text, 120);
      items.push({
        fileId,
        name: f.name,
        sectionTitle,
        openTasks,
        // helpful for applying gate later
        hint: {
          modifiedTime: f.modifiedTime,
          size: f.size,
        }
      });
    }

    const req = {
      schema: 'todolist-md.llm_request.v1',
      folderId,
      createdAtUtc: new Date().toISOString(),
      instructions: {
        model: 'gpt4o',
        outputFormat: 'markdown_list_only',
        rules: [
          'Return ONLY Markdown list items and optional indented blockquotes.',
          'Do NOT rewrite the whole file.',
          'Do NOT mark tasks complete.',
          'Keep suggestions short and actionable.',
          'You may use bot markers inside blockquotes only, e.g. > <!-- bot: note --> ...'
        ],
      },
      items,
    };

    saveJson(requestOut, req);
    state.lastRunAtUtc = new Date().toISOString();
    state.files = stFiles;
    saveJson(statePath, state);

    console.log(JSON.stringify({ ...report, action: 'prepared', requestOut, items: items.map(i => ({ fileId: i.fileId, name: i.name, openTasksLines: i.openTasks ? i.openTasks.split(/\r?\n/).length : 0 })) }, null, 2));
    return;
  }

  if (mode !== 'apply') throw new Error(`Unknown mode: ${mode}`);
  must(suggestionsIn, 'suggestionsIn (or SUGGESTIONS_IN) when mode=apply');

  const sugg = loadJsonOrDefault(suggestionsIn, null);
  if (!sugg || sugg.schema !== 'todolist-md.llm_suggestions.v1') {
    throw new Error('Invalid suggestions JSON. Expect schema todolist-md.llm_suggestions.v1');
  }

  // APPLY mode intentionally does NOT require Drive "changed" detection.
  // We apply suggestions to the fileIds explicitly provided in suggestionsIn.
  const results = [];
  for (const s of sugg.items || []) {
    const fileId = s.fileId;
    const suggested = sanitizeBotBlock(s.suggested_markdown || '');
    if (!fileId || !suggested) {
      results.push({ fileId, name: s.name, action: 'skip_missing_suggestion' });
      continue;
    }

    const meta1 = await driveGetMetadata({ fileId, accessToken });
    const text = await driveDownloadText({ fileId, accessToken });
    const edited = ensureBotSuggestedSection(text, sectionTitle, suggested);

    if (edited === text) {
      results.push({ fileId, name: s.name, action: 'no_change' });
      continue;
    }

    const meta2 = await driveGetMetadata({ fileId, accessToken });
    if (meta2.headRevisionId && meta1.headRevisionId && meta2.headRevisionId !== meta1.headRevisionId) {
      results.push({ fileId, name: s.name, action: 'skip_due_to_remote_change', before: meta1.headRevisionId, now: meta2.headRevisionId });
      continue;
    }

    if (dryRun) {
      results.push({ fileId, name: s.name, action: 'dry_run_would_update', botPreview: suggested.slice(0, 300) });
      continue;
    }

    const mimeType = meta1.mimeType || 'text/markdown';
    const name = meta1.name || s.name || 'todo.md';
    await driveUpdateText({ fileId, accessToken, name, mimeType, text: edited });
    results.push({ fileId, name: s.name, action: 'updated' });
  }

  console.log(JSON.stringify({ ...report, action: 'applied', results }, null, 2));
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
