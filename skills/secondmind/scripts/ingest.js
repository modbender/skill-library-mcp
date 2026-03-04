#!/usr/bin/env node
// scripts/ingest.js – Triple-Safety Chat Ingestion (Layer 3: Cron Smart-Diff)
const path = require('path');
const fs = require('fs');
const { getDb, getConfig, acquireLock, releaseLock, estimateTokens, updateState, BASE_DIR } = require('../lib/db');
const { getSessionsDir, getActiveSessions } = require('../lib/sessions');
const { parseJSONL } = require('../lib/jsonl-parser');

async function ingest() {
  if (!acquireLock('ingest')) return;

  try {
    const config = getConfig();
    const db = getDb();
    const sessionsDir = getSessionsDir();

    if (!fs.existsSync(sessionsDir)) {
      console.log(`[INGEST] Sessions dir not found: ${sessionsDir}`);
      return;
    }

    console.log(`[INGEST] Scanning: ${sessionsDir}`);

    // Load state: track byte offsets per file
    const statePath = path.resolve(BASE_DIR, config.paths.stateFile);
    const state = fs.existsSync(statePath)
      ? JSON.parse(fs.readFileSync(statePath, 'utf8'))
      : {};

    // Get currently active session IDs (robust parsing)
    const activeSessions = getActiveSessions(sessionsDir).map(s => s.sessionId);

    // Find all JSONL files
    const files = fs.readdirSync(sessionsDir)
      .filter(f => f.endsWith('.jsonl'))
      .map(f => path.join(sessionsDir, f));

    let totalNew = 0;

    const insertStmt = db.prepare(`
      INSERT OR IGNORE INTO shortterm_buffer
        (source, session_id, channel, raw_content, token_count, is_complete)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    for (const file of files) {
      const fileName = path.basename(file);
      const sessionId = fileName.replace('.jsonl', '').split('-topic-')[0];
      const channel = fileName.includes('-topic-') ? 'telegram-topic' : 'default';
      const stat = fs.statSync(file);
      const prevBytes = state[fileName]?.bytes || 0;

      if (stat.size <= prevBytes) continue; // No new data

      // Read only new content (delta ingest)
      const fd = fs.openSync(file, 'r');
      const buf = Buffer.alloc(stat.size - prevBytes);
      fs.readSync(fd, buf, 0, buf.length, prevBytes);
      fs.closeSync(fd);

      const newContent = buf.toString('utf8');

      // Use shared parser (handles both OpenClaw format and simple format)
      const messages = parseJSONL(newContent);

      if (messages.length === 0) {
        state[fileName] = { bytes: stat.size, ts: new Date().toISOString() };
        continue;
      }

      const content = messages.join('\n\n');
      const tokens = estimateTokens(content);

      // Session complete = NOT in active sessions list
      const isComplete = !activeSessions.includes(sessionId);

      const result = insertStmt.run(
        'cron_diff', sessionId, channel, content, tokens, isComplete ? 1 : 0
      );

      if (result.changes > 0) {
        totalNew++;
        console.log(`[INGEST] ${isComplete ? '✅' : '📝'} ${sessionId.slice(0, 8)}... ${tokens} tokens (${messages.length} msgs)`);
      }

      state[fileName] = { bytes: stat.size, ts: new Date().toISOString() };
    }

    // Cleanup: remove state entries for deleted files
    for (const f of Object.keys(state)) {
      if (!fs.existsSync(path.join(sessionsDir, f))) {
        delete state[f];
      }
    }

    fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
    updateState('last_ingest');
    console.log(`[INGEST] Done. ${totalNew} new sessions from ${files.length} files.`);
  } finally {
    releaseLock('ingest');
  }
}

ingest().catch(err => {
  console.error('[INGEST] Fatal:', err.message);
  releaseLock('ingest');
  process.exit(1);
});
