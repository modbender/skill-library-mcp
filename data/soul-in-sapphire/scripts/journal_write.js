#!/usr/bin/env node
/**
 * Write one journal entry to <base>-journal.
 *
 * stdin JSON:
 * {
 *   "title": "..." (optional),
 *   "when": "ISO" (optional),
 *   "body": "..." (required),
 *   "worklog": "..." (optional),
 *   "session_summary": "..." (optional),
 *   "future": "..." (optional),
 *   "world_news": "..." (optional),
 *   "tags": ["..."] (optional),
 *   "mood_label": "clear|..." (optional),
 *   "intent": "build|..." (optional),
 *   "highlights": ["..."] (optional),
 *   "links": "..." (optional),
 *   "source": "cron|manual" (optional)
 * }
 */

import fs from 'fs';
import os from 'os';
import path from 'path';

import { createPage } from './notionctl_bridge.js';

function die(msg) {
  process.stderr.write(String(msg) + '\n');
  process.exit(1);
}

function titleProp(s) { return { title: [{ type: 'text', text: { content: String(s) } }] }; }
function rtProp(s) {
  if (!s) return { rich_text: [] };
  return { rich_text: [{ type: 'text', text: { content: String(s) } }] };
}
function selectProp(name) { return { select: name ? { name: String(name) } : null }; }
function multiProp(arr) {
  const xs = Array.isArray(arr) ? arr : [];
  return { multi_select: xs.filter(Boolean).map(n => ({ name: String(n) })) };
}
function dateProp(start) { return { date: start ? { start: String(start) } : null }; }

function nowIso() {
  const d = new Date();
  const tz = -d.getTimezoneOffset();
  const sign = tz >= 0 ? '+' : '-';
  const pad = n => String(Math.floor(Math.abs(n))).padStart(2,'0');
  const hh = pad(tz/60);
  const mm = pad(tz%60);
  const iso = d.toISOString().replace('Z','');
  return `${iso}${sign}${hh}:${mm}`;
}

function readConfig() {
  const p = path.join(os.homedir(), '.config', 'soul-in-sapphire', 'config.json');
  if (!fs.existsSync(p)) die(`Missing config: ${p}. Run setup_ltm.js first.`);
  return JSON.parse(fs.readFileSync(p, 'utf-8'));
}

async function main() {
  const cfg = readConfig();
  const journalDb = cfg?.journal?.database_id || cfg.journal_database_id;
  if (!journalDb) die('Config missing journal_database_id. Re-run setup_ltm.js.');

  const raw = fs.readFileSync(0, 'utf-8').trim();
  if (!raw) die('Expected JSON on stdin');
  const obj = JSON.parse(raw);

  const when = obj.when || nowIso();
  const title = obj.title || `journal@${when}`;
  const body = (obj.body || '').trim();
  if (!body) die('Missing body');

  const props = {
    Name: titleProp(title),
    when: dateProp(when),
    body: rtProp(body),
    worklog: rtProp(obj.worklog || ""),
    session_summary: rtProp(obj.session_summary || ""),
    future: rtProp(obj.future || ""),
    world_news: rtProp(obj.world_news || ""),
    tags: multiProp(obj.tags || []),
    mood_label: selectProp(obj.mood_label || null),
    intent: selectProp(obj.intent || null),
    source: selectProp(obj.source || 'manual'),
  };

  try {
    const page = await createPage(journalDb, props);
    console.log(JSON.stringify({ ok: true, id: page.id, url: page.url }, null, 2));
    return;
  } catch (err) {
    // Some journal DBs may not have optional properties (e.g., older schemas).
    // If Notion rejects unknown properties, retry once with those props removed.
    const msg = String(err?.message || err);
    const missingHighlights = msg.includes('highlights is not a property that exists');
    const missingLinks = msg.includes('links is not a property that exists');
    if (missingHighlights || missingLinks) {
      if (missingHighlights) delete props.highlights;
      if (missingLinks) delete props.links;
      try {
        const page = await createPage(journalDb, props);
        console.log(JSON.stringify({ ok: true, id: page.id, url: page.url, note: 'retried_without_optional_props' }, null, 2));
        return;
      } catch (retryErr) {
        const retryMsg = String(retryErr?.message || retryErr);
        throw new Error(`Notion write failed after retry: ${retryMsg}`);
      }
    }
    throw new Error(`Notion write failed: ${msg}`);
  }
}

main().catch(err => die(err?.stack || err?.message || String(err)));
