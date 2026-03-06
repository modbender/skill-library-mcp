#!/usr/bin/env node
// scripts/archive.js – Mid-term → Long-term archival
// Moves mature knowledge entries to permanent longterm storage
const { getDb, acquireLock, releaseLock, updateState } = require('../lib/db');

async function archive() {
  if (!acquireLock('archive')) return;

  try {
    const db = getDb();

    // Archive entries that are: mentioned 2+ times OR older than 7 days
    const entries = db.prepare(`
      SELECT * FROM knowledge_entries
      WHERE id NOT IN (SELECT knowledge_id FROM longterm_archive WHERE knowledge_id IS NOT NULL)
      AND (update_count >= 2 OR first_seen < datetime('now', '-7 days'))
      AND status != 'obsolete'
    `).all();

    if (entries.length === 0) {
      console.log('[ARCHIVE] Nothing to archive.');
      return;
    }

    const insert = db.prepare(`
      INSERT OR IGNORE INTO longterm_archive
        (knowledge_id, category, title, summary, details, tags, relevance_score)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    const transaction = db.transaction(() => {
      for (const e of entries) {
        insert.run(
          e.id, e.category, e.title, e.summary,
          e.details, e.tags, e.update_count
        );
      }
    });

    transaction();
    updateState('last_archive');
    console.log(`[ARCHIVE] Archived ${entries.length} entries to longterm.`);
  } finally {
    releaseLock('archive');
  }
}

archive().catch(err => {
  console.error('[ARCHIVE] Fatal:', err.message);
  releaseLock('archive');
  process.exit(1);
});
