#!/usr/bin/env node
// scripts/session-watcher.js – Layer 2: Real-time /new detection daemon
const path = require('path');
const fs = require('fs');
const { getDb, getConfig, estimateTokens } = require('../lib/db');
const { getSessionsDir, getCurrentSession } = require('../lib/sessions');
const { parseJSONL } = require('../lib/jsonl-parser');

const POLL_INTERVAL = 3000;
let lastSessionId = null;
let running = true;

async function watch() {
  const config = getConfig();
  const db = getDb();
  const sessionsDir = getSessionsDir();

  console.log(`[WATCHER] Monitoring: ${sessionsDir}`);

  const initial = getCurrentSession(sessionsDir);
  lastSessionId = initial?.sessionId || null;
  if (lastSessionId) {
    console.log(`[WATCHER] Current session: ${lastSessionId.slice(0, 8)}...`);
  }

  while (running) {
    await sleep(POLL_INTERVAL);

    try {
      const current = getCurrentSession(sessionsDir);
      const currentId = current?.sessionId || null;

      if (currentId && lastSessionId && currentId !== lastSessionId) {
        console.log(`[WATCHER] Session change: ${lastSessionId.slice(0, 8)}... → ${currentId.slice(0, 8)}...`);
        await ingestSession(db, sessionsDir, lastSessionId);
      }

      lastSessionId = currentId;
    } catch (err) {
      console.error(`[WATCHER] Error: ${err.message}`);
    }
  }
}

async function ingestSession(db, sessionsDir, sessionId) {
  const jsonlPath = path.join(sessionsDir, `${sessionId}.jsonl`);
  if (!fs.existsSync(jsonlPath)) return;

  const existing = db.prepare(
    'SELECT id FROM shortterm_buffer WHERE session_id = ? AND is_complete = 1'
  ).get(sessionId);
  if (existing) return;

  const rawContent = fs.readFileSync(jsonlPath, 'utf8');
  const messages = parseJSONL(rawContent);
  if (messages.length === 0) return;

  const content = messages.join('\n\n');
  const tokens = estimateTokens(content);

  const result = db.prepare(`
    INSERT OR IGNORE INTO shortterm_buffer
      (source, session_id, channel, raw_content, token_count, is_complete)
    VALUES (?, ?, ?, ?, ?, 1)
  `).run('session_watcher', sessionId, 'default', content, tokens);

  if (result.changes > 0) {
    console.log(`[WATCHER] ✅ Ingested ${sessionId.slice(0, 8)}... (${tokens} tokens)`);
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
process.on('SIGINT', () => { running = false; console.log('\n[WATCHER] Stopping...'); });
process.on('SIGTERM', () => { running = false; });

watch().catch(err => { console.error('[WATCHER] Fatal:', err.message); process.exit(1); });
