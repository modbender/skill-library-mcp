#!/usr/bin/env node
/**
 * Vexa onboarding helper:
 * 1) Capture API key and optionally persist it in skills/vexa/secrets/vexa.env (chmod 600)
 * 2) Start a bot for a test meeting
 * 3) Poll transcript briefly
 * 4) Stop bot
 */

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SKILL_ROOT = path.join(__dirname, '..');
const SKILL_SECRETS_DIR = path.join(SKILL_ROOT, 'secrets');
const STATE_FILE_SKILL = path.join(SKILL_SECRETS_DIR, 'vexa-state.json');
const SECRETS_FILE_SKILL = path.join(SKILL_SECRETS_DIR, 'vexa.env');
const STATE_FILE_HOME = path.join(os.homedir(), '.openclaw', 'secrets', 'vexa-state.json');
const SECRETS_FILE_HOME = path.join(os.homedir(), '.openclaw', 'secrets', 'vexa.env');

const BASE_URL = (process.env.VEXA_BASE_URL || 'https://api.cloud.vexa.ai').replace(/\/$/, '');

function die(msg, code = 1) {
  console.error(msg);
  process.exit(code);
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const v = argv[i + 1];
      if (v == null || v.startsWith('--')) out[k] = true;
      else {
        out[k] = v;
        i++;
      }
    } else out._.push(a);
  }
  return out;
}

function parseBool(v) {
  if (v === true) return true;
  if (v === false || v == null) return undefined;
  const s = String(v).trim().toLowerCase();
  if (["1", "true", "yes", "y", "on"].includes(s)) return true;
  if (["0", "false", "no", "n", "off"].includes(s)) return false;
  return undefined;
}

function secretsExist() {
  if (process.env.VEXA_API_KEY?.trim()) return true;
  for (const file of [SECRETS_FILE_SKILL, SECRETS_FILE_HOME]) {
    try {
      const raw = fs.readFileSync(file, 'utf8');
      const m = raw.match(/VEXA_API_KEY\s*=\s*(\S+)/);
      if (m?.[1]?.trim()) return true;
    } catch {}
  }
  return false;
}

function getStateFile() {
  return fs.existsSync(STATE_FILE_SKILL) ? STATE_FILE_SKILL : STATE_FILE_HOME;
}

function readState() {
  try {
    const raw = fs.readFileSync(getStateFile(), 'utf8');
    const parsed = JSON.parse(raw);
    return { first_use: parsed?.first_use !== false };
  } catch {
    return { first_use: true };
  }
}

function writeState(state) {
  fs.mkdirSync(SKILL_SECRETS_DIR, { recursive: true });
  fs.writeFileSync(STATE_FILE_SKILL, JSON.stringify(state, null, 2) + '\n', { mode: 0o600 });
  try { fs.chmodSync(STATE_FILE_SKILL, 0o600); } catch {}
}

function normalizeGoogleMeetId(raw) {
  if (!raw) return null;
  const v = String(raw).trim();
  if (/^[a-z]{3}-[a-z]{4}-[a-z]{3}$/i.test(v)) return v.toLowerCase();
  try {
    const u = new URL(v);
    if (!/meet\.google\.com$/i.test(u.hostname)) return null;
    const m = u.pathname.match(/\/([a-z]{3}-[a-z]{4}-[a-z]{3})/i);
    return m?.[1]?.toLowerCase() || null;
  } catch { return null; }
}

function normalizeTeamsInfo(raw) {
  if (!raw) return null;
  const v = String(raw).trim();
  if (/^\d{10,15}$/.test(v)) return { native_meeting_id: v, passcode: null };
  try {
    const u = new URL(v);
    if (!/teams\./i.test(u.hostname)) return null;
    const m = u.pathname.match(/\/meet\/(\d{10,15})/i);
    const native_meeting_id = m?.[1] || null;
    const passcode = u.searchParams.get('p') || null;
    if (!native_meeting_id) return null;
    return { native_meeting_id, passcode };
  } catch { return null; }
}

function parseMeetingInput({ meeting_url, platform, native_meeting_id, passcode }) {
  if (platform && native_meeting_id) {
    return { platform, native_meeting_id: String(native_meeting_id), passcode: passcode ? String(passcode) : undefined };
  }
  if (!meeting_url) return null;
  const g = normalizeGoogleMeetId(meeting_url);
  if (g) return { platform: 'google_meet', native_meeting_id: g };
  const t = normalizeTeamsInfo(meeting_url);
  if (t) return { platform: 'teams', native_meeting_id: t.native_meeting_id, passcode: t.passcode || passcode || undefined };
  return null;
}

async function vexaFetch(apiKey, endpoint, { method = 'GET', body } = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const headers = { 'X-API-Key': apiKey, Accept: 'application/json' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  const res = await fetch(url, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  const text = await res.text();
  let json;
  try { json = text ? JSON.parse(text) : null; } catch { json = { raw: text }; }
  if (!res.ok) throw new Error(`Vexa API error ${res.status} ${res.statusText}: ${JSON.stringify(json)}`);
  return json;
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function persistKey(apiKey) {
  fs.mkdirSync(SKILL_SECRETS_DIR, { recursive: true });
  fs.writeFileSync(SECRETS_FILE_SKILL, `VEXA_API_KEY=${apiKey}\n`, { mode: 0o600 });
  try { fs.chmodSync(SECRETS_FILE_SKILL, 0o600); } catch {}
  return SECRETS_FILE_SKILL;
}

function checkWebhookReceived(withinMinutes = 10) {
  const sessionsPaths = [
    path.join(os.homedir(), '.openclaw', 'agents', 'main', 'sessions', 'sessions.json'),
    process.env.OPENCLAW_HOME ? path.join(process.env.OPENCLAW_HOME, 'agents', 'main', 'sessions', 'sessions.json') : ''
  ].filter(Boolean);
  const cutoff = Date.now() - withinMinutes * 60 * 1000;
  for (const p of sessionsPaths) {
    try {
      const raw = fs.readFileSync(p, 'utf8');
      const data = JSON.parse(raw);
      const keys = Object.keys(data || {});
      const vexaHookKeys = keys.filter((k) => k.startsWith('agent:main:hook:vexa:meeting:'));
      const recent = vexaHookKeys.filter((k) => {
        const updatedAt = data[k]?.updatedAt;
        return typeof updatedAt === 'number' && updatedAt >= cutoff;
      });
      return {
        webhook_received: recent.length > 0,
        recent_vexa_sessions: recent,
        within_minutes: withinMinutes
      };
    } catch (e) {
      if (e?.code === 'ENOENT') continue;
      return { webhook_received: false, error: String(e?.message || e) };
    }
  }
  return { webhook_received: false, error: 'sessions.json not found' };
}

function checkWebhookConfig() {
  const configPaths = [
    path.join(os.homedir(), '.openclaw', 'openclaw.json'),
    process.env.OPENCLAW_CONFIG || '',
    process.env.OPENCLAW_HOME ? path.join(process.env.OPENCLAW_HOME, 'openclaw.json') : ''
  ].filter(Boolean);
  for (const p of configPaths) {
    try {
      const raw = fs.readFileSync(p, 'utf8');
      const cfg = JSON.parse(raw);
      const mappings = cfg?.hooks?.mappings || [];
      const hasVexa = Array.isArray(mappings) && mappings.some((m) => m?.id === 'vexa');
      return { webhook_configured: hasVexa, config_path: p };
    } catch (e) {
      if (e?.code === 'ENOENT') continue;
      return { webhook_configured: false, error: String(e?.message || e) };
    }
  }
  return { webhook_configured: false, error: 'openclaw.json not found' };
}

function firstNonEmptyTranscriptText(resp) {
  const segs = Array.isArray(resp?.segments) ? resp.segments : [];
  for (const s of segs) {
    const t = String(s?.text || '').trim();
    if (t) return t;
  }
  return null;
}

function loadVexaEnv() {
  if (process.env.VEXA_API_KEY?.trim()) return;
  for (const file of [SECRETS_FILE_SKILL, SECRETS_FILE_HOME]) {
    try {
      const raw = fs.readFileSync(file, 'utf8');
      for (const line of raw.split('\n')) {
        const rest = line.replace(/^\s*export\s+/, '').trim();
        const m = rest.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$/);
        if (m && !process.env[m[1]]) {
          process.env[m[1]] = m[2].replace(/^["']|["']$/g, '').trim();
        }
      }
      break;
    } catch {}
  }
}

async function validateWebhook(parsed, apiKey) {
  loadVexaEnv();
  const k = apiKey || process.env.VEXA_API_KEY;
  if (!k) return { ok: false, error: 'Missing VEXA_API_KEY' };

  const maxWait = 120 * 1000;
  const pollMs = 5000;
  const deadline = Date.now() + maxWait;
  let status = null;

  while (Date.now() < deadline) {
    try {
      const meetings = await vexaFetch(k, '/meetings');
      const m = meetings?.meetings?.find?.((x) => x?.platform === parsed.platform && x?.native_meeting_id === parsed.native_meeting_id);
      status = m?.status || null;
      if (status === 'completed' || status === 'failed') break;
    } catch {}
    await sleep(pollMs);
  }

  if (status !== 'completed' && status !== 'failed') {
    return { ok: false, error: 'Meeting did not finalize in time', status };
  }

  const ingestScript = path.join(__dirname, 'ingest.mjs');
  const result = spawnSync(process.execPath, [ingestScript, '--platform', parsed.platform, '--native_meeting_id', parsed.native_meeting_id], {
    encoding: 'utf8',
    env: { ...process.env, VEXA_API_KEY: k }
  });

  if (result.status !== 0) {
    return { ok: false, error: result.stderr || result.stdout || 'ingest failed' };
  }

  let reportFile = null;
  try {
    const out = JSON.parse(result.stdout.trim());
    reportFile = out?.file || null;
  } catch {}

  return { ok: true, webhook_validated: true, meeting_finalized: true, report_file: reportFile, status };
}

function getHookConfig() {
  const configPaths = [
    path.join(os.homedir(), '.openclaw', 'openclaw.json'),
    process.env.OPENCLAW_CONFIG || '',
    process.env.OPENCLAW_HOME ? path.join(process.env.OPENCLAW_HOME, 'openclaw.json') : ''
  ].filter(Boolean);
  for (const p of configPaths) {
    try {
      const raw = fs.readFileSync(p, 'utf8');
      const cfg = JSON.parse(raw);
      const port = cfg?.gateway?.port ?? 18789;
      const token = cfg?.hooks?.token ?? '';
      return { port, token, config_path: p };
    } catch (e) {
      if (e?.code === 'ENOENT') continue;
    }
  }
  return { port: 18789, token: '', config_path: null };
}

async function sendMockWebhook(parsed) {
  const { port, token } = getHookConfig();
  if (!token) return { ok: false, error: 'No hooks.token in openclaw.json' };
  const payload = {
    platform: parsed.platform,
    native_meeting_id: parsed.native_meeting_id,
    status: 'completed',
    meeting: { platform: parsed.platform, native_meeting_id: parsed.native_meeting_id, status: 'completed' }
  };
  const url = `http://127.0.0.1:${port}/hooks/vexa`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const text = await res.text();
    return { ok: false, error: `HTTP ${res.status} ${text}` };
  }
  return { ok: true, mock_webhook_sent: true };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args['check-secrets'] || args.check_secrets) {
    const ok = secretsExist();
    process.stdout.write(JSON.stringify({ secrets_ok: ok }) + '\n');
    process.exit(ok ? 0 : 1);
  }

  if (args['check-webhook'] || args.check_webhook) {
    const result = checkWebhookConfig();
    process.stdout.write(JSON.stringify(result) + '\n');
    process.exit(result.webhook_configured ? 0 : 1);
  }

  if (args['check-webhook-received'] || args.check_webhook_received) {
    const within = Number(args.within_minutes || args.withinMinutes || 10) || 10;
    const result = checkWebhookReceived(within);
    process.stdout.write(JSON.stringify(result) + '\n');
    process.exit(result.webhook_received ? 0 : 1);
  }

  if (args['validate-webhook'] || args.validate_webhook) {
    loadVexaEnv();
    const apiKey = args.api_key || process.env.VEXA_API_KEY;
    if (!apiKey) die('Missing VEXA_API_KEY for --validate-webhook');
    const parsed = parseMeetingInput({
      meeting_url: args.meeting_url,
      platform: args.platform,
      native_meeting_id: args.native_meeting_id,
      passcode: args.passcode
    });
    if (!parsed) die('Usage: --validate-webhook (--meeting_url <url> | --platform X --native_meeting_id Y)');

    const webhookReceived = checkWebhookReceived(2);
    if (!webhookReceived.webhook_received) {
      const mock = await sendMockWebhook(parsed);
      if (!mock.ok) {
        process.stdout.write(JSON.stringify({ ok: false, error: mock.error, hint: 'Webhook not received; mock webhook failed. Ensure OpenClaw gateway is running.' }, null, 2) + '\n');
        process.exit(1);
      }
    }

    const result = await validateWebhook(parsed, apiKey);
    if (result.ok && !webhookReceived.webhook_received) {
      result.mock_webhook_sent = true;
      result.note = 'Local pipeline validated via mock webhook. Real webhook requires a public URL — cannot be set or validated with internal URL.';
    }
    process.stdout.write(JSON.stringify(result, null, 2) + '\n');
    process.exit(result.ok ? 0 : 1);
  }

  if (args['send-mock-webhook'] || args.send_mock_webhook) {
    const parsed = parseMeetingInput({
      meeting_url: args.meeting_url,
      platform: args.platform,
      native_meeting_id: args.native_meeting_id,
      passcode: args.passcode
    });
    if (!parsed) die('Usage: --send-mock-webhook (--meeting_url <url> | --platform X --native_meeting_id Y)');
    const result = await sendMockWebhook(parsed);
    process.stdout.write(JSON.stringify(result, null, 2) + '\n');
    process.exit(result.ok ? 0 : 1);
  }

  const rl = readline.createInterface({ input, output });

  try {
    let apiKey = args.api_key || process.env.VEXA_API_KEY;
    if (!apiKey) {
      apiKey = (await rl.question('Paste your Vexa API key (from https://vexa.ai/dashboard/api-keys): ')).trim();
    }
    if (!apiKey) die('API key is required.');

    // Set up API key immediately when provided
    const persist = parseBool(args.persist) ?? true;
    const persistedPath = persist ? persistKey(apiKey) : null;
    if (persistedPath) {
      console.error('API key saved to', persistedPath);
    }

    const state = readState();

    const meeting_url = args.meeting_url || (await rl.question('Meeting link or ID for test (Google Meet or Teams): ')).trim();
    const language = args.language || (await rl.question('Preferred spoken language code (optional, e.g. en, pt, es): ')).trim() || undefined;

    const parsed = parseMeetingInput({
      meeting_url,
      platform: args.platform,
      native_meeting_id: args.native_meeting_id,
      passcode: args.passcode
    });

    if (!parsed) die('Could not parse meeting input. Provide a valid Google Meet/Teams URL or explicit --platform + --native_meeting_id.');
    if (parsed.platform === 'teams' && !parsed.passcode) die('Teams requires passcode. Provide Teams URL with ?p=... or --passcode.');

    const bot = await vexaFetch(apiKey, '/bots', {
      method: 'POST',
      body: {
        platform: parsed.platform,
        native_meeting_id: parsed.native_meeting_id,
        passcode: parsed.passcode,
        language,
        bot_name: args.bot_name || 'Claw'
      }
    });

    const waitSeconds = Number(args.wait_seconds || 60);
    const pollEvery = Number(args.poll_every_seconds || 10);
    const deadline = Date.now() + waitSeconds * 1000;

    let transcript = null;
    while (Date.now() < deadline) {
      try {
        const t = await vexaFetch(apiKey, `/transcripts/${encodeURIComponent(parsed.platform)}/${encodeURIComponent(parsed.native_meeting_id)}`);
        transcript = t;
        if (firstNonEmptyTranscriptText(t)) break;
      } catch {}
      await sleep(pollEvery * 1000);
    }

    const stop = await vexaFetch(apiKey, `/bots/${encodeURIComponent(parsed.platform)}/${encodeURIComponent(parsed.native_meeting_id)}`, { method: 'DELETE' });

    const snippet = firstNonEmptyTranscriptText(transcript);

    writeState({
      first_use: false,
      configured_at: new Date().toISOString(),
      api_key_saved: Boolean(persistedPath)
    });

    process.stdout.write(JSON.stringify({
      ok: true,
      base_url: BASE_URL,
      persisted_api_key: Boolean(persistedPath),
      persisted_path: persistedPath,
      state_path: STATE_FILE_SKILL,
      meeting: parsed,
      language: language || null,
      bot_start_response: bot,
      transcript_snippet: snippet,
      transcript_segments: Array.isArray(transcript?.segments) ? transcript.segments.length : 0,
      bot_stop_response: stop,
      next_step: persistedPath
        ? `Load key in future shells with: source ${persistedPath}`
        : 'Set VEXA_API_KEY before running vexa commands.'
    }, null, 2) + '\n');
  } finally {
    rl.close();
  }
}

main().catch((e) => {
  console.error(e?.stack || String(e));
  process.exit(1);
});
