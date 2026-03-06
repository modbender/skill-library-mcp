#!/usr/bin/env node
// scripts/flush.js – Pre-reset session capture (Layer 1: Skill Hook)
const path = require('path');
const fs = require('fs');
const { getDb, getConfig, estimateTokens } = require('../lib/db');
const { flushSession } = require('../lib/extractor');
const { getSessionsDir, getCurrentSession, getMostRecentSession } = require('../lib/sessions');
const { parseJSONL } = require('../lib/jsonl-parser');

async function flush() {
  const config = getConfig();
  const db = getDb();
  const sessionsDir = getSessionsDir();

  // Find current active session (robust parsing)
  let current = getCurrentSession(sessionsDir);
  if (!current) {
    current = getMostRecentSession(sessionsDir);
  }

  if (!current) {
    console.log('💾 No active session found.');
    return;
  }

  const { sessionId } = current;

  // Check if already flushed
  const existing = db.prepare(
    'SELECT id FROM shortterm_buffer WHERE session_id = ? AND is_complete = 1'
  ).get(sessionId);

  if (existing) {
    console.log('💾 Session already archived.');
    return;
  }

  // Read session JSONL
  const jsonlPath = path.join(sessionsDir, `${sessionId}.jsonl`);
  if (!fs.existsSync(jsonlPath)) {
    console.log('💾 Session file not found.');
    return;
  }

  const rawContent = fs.readFileSync(jsonlPath, 'utf8');
  const messages = parseJSONL(rawContent);

  if (messages.length === 0) {
    console.log('💾 Empty session.');
    return;
  }

  const content = messages.join('\n\n');
  const tokens = estimateTokens(content);

  // For short sessions, save raw. For long ones, use LLM summary.
  let saveContent = content;
  if (tokens > 2000) {
    try {
      const summary = await flushSession(content);
      saveContent = JSON.stringify(summary);
      console.log(`💾 Session summarized (${tokens} → ~${estimateTokens(saveContent)} tokens)`);
    } catch (err) {
      console.log(`💾 Summary failed, saving raw: ${err.message}`);
    }
  }

  db.prepare(`
    INSERT OR IGNORE INTO shortterm_buffer
      (source, session_id, channel, raw_content, token_count, is_complete)
    VALUES (?, ?, ?, ?, ?, 1)
  `).run('skill_hook', sessionId, current.channel || 'default', saveContent, estimateTokens(saveContent));

  console.log(`💾 Session archived. (${sessionId.slice(0, 8)}...)`);
}

flush().catch(err => {
  console.error('💾 Flush error:', err.message);
  process.exit(1);
});
