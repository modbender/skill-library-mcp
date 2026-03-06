// ============================================================================
// Auto-capture: extract facts from messages (with entity validation)
// ============================================================================

import { sqliteQuery, sqliteExec, escapeSqlValue } from './sqlite.js';
import { extractFacts } from './extraction.js';
import { randomUUID } from 'node:crypto';

/**
 * Capture facts from conversation messages and store them in the database.
 *
 * @param {string} dbPath - Path to SQLite database
 * @param {Array} messages - Array of {role, content} message objects
 * @param {number} maxCapture - Maximum number of facts to capture this call
 * @param {Set<string>} runtimeEntities - Set of lowercase known entity names
 * @param {Function|null} logger - logger(msg) for status; falls back to console.log
 * @returns {{ stored: number, newDecisionIds: Array<{id: string, text: string}> }}
 */
export function captureFromMessages(dbPath, messages, maxCapture, runtimeEntities, logger) {
  const log = logger ?? console.log;
  const nowMs = Date.now();
  let stored = 0;
  const newDecisionIds = []; // Track for async embedding

  // Flatten messages to { role, text } pairs
  const texts = [];
  for (const msg of messages) {
    if (!msg || typeof msg !== 'object') continue;
    const role = msg.role;
    if (role !== 'user' && role !== 'assistant') continue;

    const content = msg.content;
    if (typeof content === 'string') {
      texts.push({ role, text: content });
      continue;
    }
    if (Array.isArray(content)) {
      for (const block of content) {
        if (block && typeof block === 'object' && block.type === 'text' && typeof block.text === 'string') {
          texts.push({ role, text: block.text });
        }
      }
    }
  }

  for (const { role, text } of texts) {
    if (stored >= maxCapture) break;

    // Skip injected memory context
    if (text.includes('<lily-memory>') || text.includes('<relevant-memories>')) continue;
    // Skip very short or very long
    if (text.length < 30 || text.length > 5000) continue;

    const facts = extractFacts(text, runtimeEntities);
    for (const fact of facts) {
      if (stored >= maxCapture) break;

      const entity = escapeSqlValue(fact.entity);
      const key = escapeSqlValue(fact.key);
      const value = escapeSqlValue(fact.value);

      // Check if this fact already exists
      const existing = sqliteQuery(dbPath, `SELECT id FROM decisions WHERE entity = '${entity}' AND fact_key = '${key}' AND (expires_at IS NULL OR expires_at > ${nowMs}) LIMIT 1`);

      if (existing.length > 0) {
        const existingId = escapeSqlValue(existing[0].id);
        sqliteExec(dbPath, `UPDATE decisions SET fact_value = '${value}', description = '${escapeSqlValue(`${fact.entity}.${fact.key} = ${fact.value}`)}', timestamp = ${nowMs}, last_accessed_at = ${nowMs} WHERE id = '${existingId}'`);
        // Re-embed on update
        newDecisionIds.push({ id: existing[0].id, text: `${fact.entity}.${fact.key} = ${fact.value}` });
        log(`lily-memory: updated fact ${fact.entity}.${fact.key}`);
        continue;
      }

      // Heuristic TTL assignment
      const ttlClass = role === 'user' ? 'stable' : 'active';
      const expiresAt = ttlClass === 'stable'
        ? nowMs + 90 * 86400 * 1000
        : nowMs + 14 * 86400 * 1000;

      // Heuristic importance
      const importance = role === 'user' ? 0.75 : 0.6;

      const id = randomUUID();
      const description = escapeSqlValue(`${fact.entity}.${fact.key} = ${fact.value}`);
      const ok = sqliteExec(dbPath, `INSERT INTO decisions (id, session_id, timestamp, category, description, rationale, classification, importance, ttl_class, expires_at, last_accessed_at, entity, fact_key, fact_value, tags) VALUES ('${escapeSqlValue(id)}', 'plugin-auto', ${nowMs}, 'auto-capture', '${description}', 'Auto-captured by lily-memory plugin v4', 'ARCHIVE', ${importance}, '${ttlClass}', ${expiresAt}, ${nowMs}, '${entity}', '${key}', '${value}', '["auto-capture","v4"]')`);

      if (ok) {
        stored++;
        newDecisionIds.push({ id, text: `${fact.entity}.${fact.key} = ${fact.value}` });
        log(`lily-memory: captured ${fact.entity}.${fact.key} = ${fact.value}`);
      }
    }
  }

  return { stored, newDecisionIds };
}
