#!/usr/bin/env node
// scripts/consolidate.js – Short-term → Mid-term knowledge + social intelligence
// Extracts structured knowledge AND emotional context from raw chats
const { getDb, getConfig, acquireLock, releaseLock, estimateTokens, updateState } = require('../lib/db');
const { extractKnowledge } = require('../lib/extractor');
const { findSimilarEntry } = require('../lib/search');

async function consolidate() {
  if (!acquireLock('consolidate')) return;

  try {
    const config = getConfig();
    const db = getDb();
    const minTokens = config.initiative?.minTokensForProcessing || 200;

    const pending = db.prepare(
      'SELECT * FROM shortterm_buffer WHERE processed = 0 ORDER BY ingested_at'
    ).all();

    if (pending.length === 0) {
      console.log('[CONSOLIDATE] Nothing to process.');
      return;
    }

    console.log(`[CONSOLIDATE] Processing ${pending.length} buffer entries...`);

    const batches = batchByTokens(pending, 4000);

    // Prepared statements
    const insertKnowledge = db.prepare(`
      INSERT INTO knowledge_entries (category, title, summary, details, tags, status, source_ref)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);
    const updateKnowledge = db.prepare(`
      UPDATE knowledge_entries
      SET summary = ?, details = COALESCE(?, details), tags = ?,
          last_updated = datetime('now'), update_count = update_count + 1
      WHERE id = ?
    `);
    const insertEmotion = db.prepare(`
      INSERT INTO social_context (person, mood, intensity, trigger_text, topic_ref, session_id)
      VALUES (?, ?, ?, ?, ?, ?)
    `);
    const insertEvent = db.prepare(`
      INSERT OR IGNORE INTO social_events (person, event_type, description, event_date, source_ref)
      VALUES (?, ?, ?, ?, ?)
    `);
    const markProcessed = db.prepare(
      'UPDATE shortterm_buffer SET processed = 1 WHERE id = ?'
    );

    let stats = { newKnowledge: 0, merged: 0, emotions: 0, events: 0 };

    for (const batch of batches) {
      const content = batch.items.map(b => b.raw_content).join('\n\n---\n\n');
      const tokens = estimateTokens(content);

      if (tokens < minTokens) {
        batch.items.forEach(b => markProcessed.run(b.id));
        continue;
      }

      console.log(`[CONSOLIDATE] Extracting from ${batch.items.length} entries (${tokens} tokens)...`);

      try {
        const result = await extractKnowledge(content);

        // Normalize: handle array, {knowledge,emotions,events}, or single object
        let knowledge, emotions, events;
        if (Array.isArray(result)) {
          knowledge = result;
          emotions = [];
          events = [];
        } else if (result && typeof result === 'object') {
          const k = result.knowledge || [];
          knowledge = Array.isArray(k) ? k : (k.title ? [k] : []);
          const e = result.emotions || [];
          emotions = Array.isArray(e) ? e : (e.mood ? [e] : []);
          const ev = result.events || [];
          events = Array.isArray(ev) ? ev : (ev.person ? [ev] : []);
        } else {
          knowledge = []; emotions = []; events = [];
        }

        const transaction = db.transaction(() => {
          // 1. Process knowledge entries
          for (const entry of knowledge) {
            if (!entry.title || !entry.summary || !entry.category) continue;

            const existing = findSimilarEntry(db, entry);
            if (existing) {
              const mergedTags = mergeTags(existing.tags, entry.tags);
              updateKnowledge.run(entry.summary, entry.details || null, JSON.stringify(mergedTags), existing.id);
              stats.merged++;
            } else {
              insertKnowledge.run(
                entry.category, entry.title, entry.summary,
                entry.details || null, JSON.stringify(entry.tags || []),
                entry.status || 'active', batch.items[0].session_id
              );
              stats.newKnowledge++;
            }
          }

          // 2. Process emotions (Soziale Intelligenz)
          for (const emo of emotions) {
            if (!emo.mood) continue;
            insertEmotion.run(
              emo.person || 'self',
              emo.mood,
              emo.intensity || 0.5,
              emo.trigger || null,
              emo.topic_ref || null,
              batch.items[0].session_id
            );
            stats.emotions++;
          }

          // 3. Process events
          for (const evt of events) {
            if (!evt.person || !evt.type) continue;
            insertEvent.run(
              evt.person, evt.type,
              evt.description || null,
              evt.date || null,
              batch.items[0].session_id
            );
            stats.events++;
          }
        });

        transaction();

      } catch (err) {
        console.error('[CONSOLIDATE] LLM extraction failed:', err.message);
      }

      batch.items.forEach(b => markProcessed.run(b.id));
    }

    // Cleanup old processed entries
    const cleaned = db.prepare(`
      DELETE FROM shortterm_buffer
      WHERE processed = 1 AND ingested_at < datetime('now', '-48 hours')
    `).run();

    updateState('last_consolidate');
    console.log(`[CONSOLIDATE] Done. Knowledge: ${stats.newKnowledge} new, ${stats.merged} merged. Emotions: ${stats.emotions}. Events: ${stats.events}. Cleaned: ${cleaned.changes}`);

  } finally {
    releaseLock('consolidate');
  }
}

function batchByTokens(items, maxTokens) {
  const batches = [];
  let current = { items: [], tokens: 0 };
  for (const item of items) {
    const t = item.token_count || estimateTokens(item.raw_content);
    if (current.tokens + t > maxTokens && current.items.length > 0) {
      batches.push(current);
      current = { items: [], tokens: 0 };
    }
    current.items.push(item);
    current.tokens += t;
  }
  if (current.items.length > 0) batches.push(current);
  return batches;
}

function mergeTags(existingJson, newTags) {
  let existing = [];
  try { existing = JSON.parse(existingJson || '[]'); } catch {}
  return [...new Set([...existing, ...(newTags || [])])];
}

consolidate().catch(err => {
  console.error('[CONSOLIDATE] Fatal:', err.message);
  releaseLock('consolidate');
  process.exit(1);
});
