#!/usr/bin/env node
/**
 * Vexa meeting ingest helper for OpenClaw.
 * - Pull meeting + transcript from Vexa API
 * - Write a markdown report into workspace/memory/meetings/
 *
 * Env:
 * - VEXA_BASE_URL (default https://vexa-lite.fly.dev)
 * - VEXA_API_KEY (required)
 */

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SECRETS_FILE_SKILL = path.join(__dirname, '..', 'secrets', 'vexa.env');
const SECRETS_FILE_HOME = path.join(os.homedir(), '.openclaw', 'secrets', 'vexa.env');

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

loadVexaEnv();

const BASE_URL = (process.env.VEXA_BASE_URL || 'https://api.cloud.vexa.ai').replace(/\/$/, '');
const API_KEY = process.env.VEXA_API_KEY;

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

async function vexaFetch(p, { method = 'GET', body } = {}) {
  if (!API_KEY) die('Missing VEXA_API_KEY. Source skills/vexa/secrets/vexa.env or run: node skills/vexa/scripts/onboard.mjs');
  const url = `${BASE_URL}${p}`;
  const headers = { 'X-API-Key': API_KEY, 'Accept': 'application/json' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  const res = await fetch(url, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  const text = await res.text();
  let json;
  try { json = text ? JSON.parse(text) : null; } catch { json = { raw: text }; }
  if (!res.ok) throw new Error(`Vexa API error ${res.status} ${res.statusText}: ${text}`);
  return json;
}

function ymd(d = new Date()) {
  return d.toISOString().slice(0, 10);
}

function safeSlug(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '').slice(0, 80);
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function secondsToTimestamp(sec) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function parseMeetingInput({ meeting_url, platform, native_meeting_id }) {
  if (platform && native_meeting_id) {
    return { platform, native_meeting_id: String(native_meeting_id) };
  }
  if (!meeting_url) return null;
  const v = String(meeting_url).trim();
  const g = /^[a-z]{3}-[a-z]{4}-[a-z]{3}$/i.test(v)
    ? v.toLowerCase()
    : (() => {
        try {
          const u = new URL(v);
          if (!/meet\.google\.com$/i.test(u.hostname)) return null;
          const m = u.pathname.match(/\/([a-z]{3}-[a-z]{4}-[a-z]{3})/i);
          return m?.[1]?.toLowerCase() || null;
        } catch { return null; }
      })();
  if (g) return { platform: 'google_meet', native_meeting_id: g };
  try {
    const u = new URL(v);
    if (!/teams\./i.test(u.hostname)) return null;
    const m = u.pathname.match(/\/meet\/(\d{10,15})/i);
    return m?.[1] ? { platform: 'teams', native_meeting_id: m[1] } : null;
  } catch { return null; }
}

function formatDuration(startTime, endTime) {
  if (!startTime || !endTime) return null;
  const a = new Date(startTime);
  const b = new Date(endTime);
  if (Number.isNaN(a.getTime()) || Number.isNaN(b.getTime())) return null;
  const mins = Math.round((b - a) / 60000);
  if (mins < 0) return null;
  return mins < 60 ? `${mins} min` : `${Math.floor(mins / 60)}h ${mins % 60}m`;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const parsed = parseMeetingInput({
    meeting_url: args.meeting_url,
    platform: args.platform,
    native_meeting_id: args.native_meeting_id
  });
  if (!parsed) {
    die('Usage: node skills/vexa/scripts/ingest.mjs (--meeting_url <url> | --platform <google_meet|teams> --native_meeting_id <id>)');
  }
  const { platform, native_meeting_id } = parsed;

  // Fetch transcript
  const transcript = await vexaFetch(`/transcripts/${encodeURIComponent(platform)}/${encodeURIComponent(native_meeting_id)}`);

  // Fetch meeting list and pick the matching meeting for richer metadata
  const meetings = await vexaFetch('/meetings');
  const meeting = meetings?.meetings?.find?.((m) => m?.platform === platform && m?.native_meeting_id === native_meeting_id) || null;

  const day = ymd();
  const outDir = path.join(process.cwd(), 'memory', 'meetings');
  ensureDir(outDir);

  const status = meeting?.status ?? transcript?.status ?? '';
  const meetingName = meeting?.data?.name || meeting?.name || '';
  const title = meetingName || `${platform} ${native_meeting_id}`;
  const file = path.join(outDir, `${day}-${safeSlug(meetingName || platform)}-${safeSlug(native_meeting_id)}.md`);

  const segs = Array.isArray(transcript?.segments) ? transcript.segments : [];
  const fullTranscript = segs
    .filter((s) => (s?.text || '').trim())
    .map((s) => {
      const start = secondsToTimestamp(Number(s.start || 0));
      const speaker = (s.speaker || '').trim();
      const who = speaker ? `**${speaker}:**` : '';
      return `- [${start}] ${who} ${String(s.text).trim()}`;
    })
    .join('\n');

  const duration = formatDuration(meeting?.start_time, meeting?.end_time);

  const md = [
    `# Meeting report: ${title}`,
    ``,
    `## Meeting info`,
    ``,
    `| Field | Value |`,
    `|-------|-------|`,
    `| Platform | ${platform} |`,
    `| Meeting ID | ${native_meeting_id} |`,
    `| Status | ${status || '(unknown)'} |`,
    meeting?.start_time ? `| Start | ${meeting.start_time} |` : null,
    meeting?.end_time ? `| End | ${meeting.end_time} |` : null,
    duration ? `| Duration | ${duration} |` : null,
    meeting?.constructed_meeting_url ? `| URL | ${meeting.constructed_meeting_url} |` : null,
    meeting?.data?.participants ? `| Participants | ${meeting.data.participants} |` : null,
    ``,
    `## Summary`,
    ``,
    `_Add a brief summary of the meeting here._`,
    ``,
    `## Key decisions`,
    ``,
    `_List key decisions made._`,
    ``,
    `## Action items`,
    ``,
    `_List action items and owners._`,
    ``,
    `## Transcript`,
    ``,
    fullTranscript || '_No transcript yet._',
    ``
  ].filter(Boolean).join('\n');

  fs.writeFileSync(file, md, 'utf8');
  process.stdout.write(JSON.stringify({ ok: true, file, platform, native_meeting_id, status, title }, null, 2) + '\n');
}

main().catch((e) => {
  console.error(e?.stack || String(e));
  process.exit(1);
});
