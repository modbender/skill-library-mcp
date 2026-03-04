import { sqliteQuery, escapeSqlValue } from "./sqlite.js";

// ============================================================================
// Memory recall / context building (FTS5 + vector dedup)
// ============================================================================

/**
 * Build FTS-based memory context from the database.
 * @param {string} dbPath - Path to database file
 * @param {string} prompt - User prompt to extract keywords from
 * @param {number} maxResults - Maximum FTS results to return
 * @returns {{ lines: string[], ftsIds: Set<string> }}
 */
export function buildFtsContext(dbPath, prompt, maxResults) {
  const nowMs = Date.now();
  const lines = [];

  // 1. Always include permanent facts
  const permanent = sqliteQuery(dbPath, `
    SELECT entity, fact_key, fact_value, importance
    FROM decisions
    WHERE ttl_class = 'permanent'
      AND entity IS NOT NULL
      AND fact_key IS NOT NULL
    ORDER BY importance DESC
    LIMIT 15
  `);

  if (permanent.length > 0) {
    lines.push("## Permanent Knowledge");
    for (const row of permanent) {
      lines.push(`- **${row.entity}**.${row.fact_key} = ${row.fact_value}`);
    }
    lines.push("");
  }

  // 2. FTS5 search on the prompt
  const ftsIds = new Set();
  if (prompt && prompt.length >= 5) {
    const keywords = prompt
      .replace(/[^\w\s]/g, " ")
      .split(/\s+/)
      .filter((w) => w.length >= 3)
      .slice(0, 8)
      .map((w) => escapeSqlValue(w))
      .join(" OR ");

    if (keywords) {
      const ftsResults = sqliteQuery(dbPath, `
        SELECT d.id, d.entity, d.fact_key, d.fact_value, d.description, d.category, d.importance
        FROM decisions d
        JOIN decisions_fts fts ON d.rowid = fts.rowid
        WHERE decisions_fts MATCH '${keywords}'
          AND (d.expires_at IS NULL OR d.expires_at > ${nowMs})
        ORDER BY rank
        LIMIT ${maxResults}
      `);

      if (ftsResults.length > 0) {
        lines.push("## Relevant Memories (keyword)");
        for (const row of ftsResults) {
          ftsIds.add(row.id);
          if (row.entity && row.fact_key) {
            lines.push(`- **${row.entity}**.${row.fact_key} = ${row.fact_value}`);
          } else if (row.description) {
            lines.push(`- [${row.category || "general"}] ${row.description}`);
          }
        }
        lines.push("");
      }
    }
  }

  // 3. Recent high-importance active decisions
  const recent = sqliteQuery(dbPath, `
    SELECT description, category, importance
    FROM decisions
    WHERE importance >= 0.7
      AND ttl_class IN ('stable', 'active')
      AND (expires_at IS NULL OR expires_at > ${nowMs})
    ORDER BY timestamp DESC
    LIMIT 5
  `);

  if (recent.length > 0) {
    lines.push("## Recent Important Context");
    for (const row of recent) {
      lines.push(`- [${row.category}] ${row.description}`);
    }
    lines.push("");
  }

  return { lines, ftsIds };
}

/**
 * Combine FTS lines and vector results into a single XML context block.
 * @param {string[]} ftsLines - Lines from buildFtsContext
 * @param {Set<string>} ftsIds - Decision IDs already present in FTS results
 * @param {Array|null} vectorResults - Results from vectorSearch (may be null/empty)
 * @returns {string|null} Formatted context string or null if nothing to include
 */
export function buildRecallContext(ftsLines, ftsIds, vectorResults) {
  const lines = [...ftsLines];

  // Add vector search results (deduplicated against FTS results)
  if (vectorResults && vectorResults.length > 0) {
    const newResults = vectorResults.filter((r) => !ftsIds.has(r.decision_id));
    if (newResults.length > 0) {
      lines.push("## Semantically Related Memories");
      for (const row of newResults) {
        const sim = (row.similarity * 100).toFixed(0);
        if (row.entity && row.fact_key) {
          lines.push(`- **${row.entity}**.${row.fact_key} = ${row.fact_value} _(${sim}% match)_`);
        } else if (row.description) {
          lines.push(`- [${row.category || "general"}] ${row.description} _(${sim}% match)_`);
        }
      }
      lines.push("");
    }
  }

  if (lines.length === 0) return null;

  return [
    "<lily-memory>",
    "_Persistent memory context (auto-injected). Use memory_search/memory_entity/memory_store/memory_semantic_search tools for details._",
    "",
    ...lines,
    "</lily-memory>",
  ].join("\n");
}
