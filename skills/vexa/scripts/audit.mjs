#!/usr/bin/env node
/**
 * Audit Vexa meetings for cleanup/rename.
 * Outputs a JSON report with:
 * - status/duration
 * - segment count + short snippet (first non-empty text)
 * - simple heuristics for "test" (short duration, keyword hits)
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

function parseDate(s) {
  const d = s ? new Date(s) : null;
  return d && !Number.isNaN(d.getTime()) ? d : null;
}

function durSeconds(start, end) {
  const a = parseDate(start);
  const b = parseDate(end);
  if (!a || !b) return null;
  return Math.max(0, Math.round((b.getTime() - a.getTime()) / 1000));
}

function firstSnippet(segments) {
  if (!Array.isArray(segments)) return null;
  for (const s of segments) {
    const t = String(s?.text || '').trim();
    if (t) return t.slice(0, 200);
  }
  return null;
}

function isTestHeuristic(meeting, transcript) {
  const d = durSeconds(meeting?.start_time, meeting?.end_time);
  const segCount = Array.isArray(transcript?.segments) ? transcript.segments.filter(s => String(s?.text||'').trim()).length : 0;
  const snip = (firstSnippet(transcript?.segments) || '').toLowerCase();
  const kws = ['youtube', 'test', 'demo', 'in no shape or form do we advocate', 'it\'s been a long time'];
  const kwHit = kws.some(k => snip.includes(k));
  // very short meetings or keyword hit are likely tests
  const short = d !== null && d <= 120;
  return { likelyTest: Boolean(short || kwHit), short, kwHit, segCount, durationSec: d, snippet: snip ? snip.slice(0,200) : null };
}

async function main() {
  const meetingsResp = await vexaFetch('/meetings');
  const meetings = Array.isArray(meetingsResp?.meetings) ? meetingsResp.meetings : [];

  const out = [];

  // Limit transcript pulls to completed/failed to reduce noise.
  for (const m of meetings) {
    const platform = m?.platform;
    const native = m?.native_meeting_id;
    const status = m?.status;
    let transcript = null;
    if (platform && native && (status === 'completed' || status === 'failed')) {
      try {
        transcript = await vexaFetch(`/transcripts/${encodeURIComponent(platform)}/${encodeURIComponent(native)}`);
      } catch (e) {
        transcript = { error: String(e?.message || e) };
      }
    }

    const heur = isTestHeuristic(m, transcript);
    out.push({
      id: m?.id,
      platform,
      native_meeting_id: native,
      status,
      url: m?.constructed_meeting_url,
      start_time: m?.start_time,
      end_time: m?.end_time,
      completion_reason: m?.data?.completion_reason,
      name: m?.data?.name ?? null,
      transcript_error: transcript?.error ?? null,
      transcript_segment_count: heur.segCount,
      duration_seconds: heur.durationSec,
      snippet: heur.snippet,
      likely_test: heur.likelyTest,
      likely_test_reasons: { short: heur.short, keyword: heur.kwHit }
    });
  }

  out.sort((a,b)=>{
    const da = parseDate(a.start_time)?.getTime() ?? 0;
    const db = parseDate(b.start_time)?.getTime() ?? 0;
    return db - da;
  });

  process.stdout.write(JSON.stringify({ ok: true, count: out.length, meetings: out }, null, 2) + '\n');
}

main().catch((e) => {
  console.error(e?.stack || String(e));
  process.exit(1);
});
