import { sqliteQuery, sqliteExec } from './sqlite.js';

/**
 * Consolidate duplicate memory entries, keeping the most recently accessed.
 * @param {string} dbPath - Path to SQLite database
 * @param {Function} [logger] - Optional logging function; defaults to console.log
 * @returns {number} Count of merged (deleted) duplicate entries
 */
export function consolidateMemories(dbPath, logger) {
  const log = (typeof logger === 'function') ? logger : console.log;
  const nowMs = Date.now();
  let merged = 0;

  // 1. Find duplicate entity+fact_key groups (non-expired)
  const duplicates = sqliteQuery(dbPath, `
    SELECT entity, fact_key, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
    FROM decisions
    WHERE entity IS NOT NULL AND fact_key IS NOT NULL
      AND (expires_at IS NULL OR expires_at > ?)
    GROUP BY entity, fact_key
    HAVING cnt > 1
  `, [nowMs]);

  for (const dup of duplicates) {
    const ids = dup.ids.split(',').map(id => id.trim());

    // Find the entry with the latest last_accessed_at or timestamp
    const placeholders = ids.map(() => '?').join(',');
    const latestRows = sqliteQuery(dbPath, `
      SELECT id, importance FROM decisions
      WHERE id IN (${placeholders})
      ORDER BY COALESCE(last_accessed_at, timestamp) DESC
      LIMIT 1
    `, ids);

    if (latestRows.length === 0) continue;

    const latestId = latestRows[0].id;

    // Collect all importances to find the max for the boost
    const allEntries = sqliteQuery(dbPath, `
      SELECT id, importance FROM decisions
      WHERE id IN (${placeholders})
    `, ids);

    const maxImportance = Math.min(
      0.95,
      Math.max(...allEntries.map(e => e.importance)) + 0.05
    );

    // Boost survivor importance
    sqliteExec(dbPath, `
      UPDATE decisions
      SET importance = ?, last_accessed_at = ?
      WHERE id = ?
    `, [maxImportance, nowMs, latestId]);

    // Delete all other entries in the group
    const deleteIds = ids.filter(id => id !== latestId);
    for (const delId of deleteIds) {
      sqliteExec(dbPath, `DELETE FROM decisions WHERE id = ?`, [delId]);
      sqliteExec(dbPath, `DELETE FROM vectors WHERE decision_id = ?`, [delId]);
    }

    merged += deleteIds.length;
  }

  // 2. Clean orphaned vectors (decision_id no longer in decisions table)
  sqliteExec(dbPath, `
    DELETE FROM vectors WHERE decision_id NOT IN (SELECT id FROM decisions)
  `);

  if (merged > 0) {
    log(`lily-memory: consolidated ${merged} duplicate entries`);
  }

  return merged;
}
