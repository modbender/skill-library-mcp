import { sqliteQuery } from "./sqlite.js";
import { createBudget, formatFactLine, DEFAULT_BUDGET, MAX_ITEM_VALUE_LENGTH } from "./budget.js";

// ============================================================================
// Memory recall / context building (budget-aware, FTS5 + vector dedup)
// ============================================================================

/**
 * Build FTS-based memory context from the database, respecting a character budget.
 * Sections fill in priority order: permanent > FTS > recent.
 * Each fact value is truncated to MAX_ITEM_VALUE_LENGTH chars.
 *
 * @param {string} dbPath - Path to database file
 * @param {string} prompt - User prompt to extract keywords from
 * @param {number} maxResults - Maximum FTS results to return
 * @param {number} budgetChars - Total character budget for this injection
 * @returns {{ lines: string[], ftsIds: Set<string>, budgetReport: object }}
 */
export function buildFtsContext(dbPath, prompt, maxResults, budgetChars = DEFAULT_BUDGET) {
  const nowMs = Date.now();
  const budget = createBudget(budgetChars);
  const lines = [];
  const ftsIds = new Set();

  // 1. Permanent facts (highest priority — identity + preferences)
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
    const section = [];
    for (const row of permanent) {
      const line = formatFactLine(row);
      if (!line) continue;
      if (!budget.tryAdd("permanent", line.length + 1)) break;
      section.push(line);
    }
    if (section.length > 0) {
      lines.push("## Permanent Knowledge");
      lines.push(...section);
      lines.push("");
    }
  }

  // 2. FTS5 search on the prompt (query-relevant recall)
  if (prompt && prompt.length >= 5 && budget.remaining > 100) {
    const keywords = prompt
      .replace(/[^\w\s]/g, " ")
      .split(/\s+/)
      .filter((w) => w.length >= 3)
      .slice(0, 8)
      .join(" OR ");

    if (keywords) {
      const ftsResults = sqliteQuery(dbPath, `
        SELECT d.id, d.entity, d.fact_key, d.fact_value, d.description, d.category, d.importance
        FROM decisions d
        JOIN decisions_fts fts ON d.rowid = fts.rowid
        WHERE decisions_fts MATCH ?
          AND (d.expires_at IS NULL OR d.expires_at > ?)
        ORDER BY rank
        LIMIT ?
      `, [keywords, nowMs, Math.min(maxResults, 10)]);

      if (ftsResults.length > 0) {
        const section = [];
        for (const row of ftsResults) {
          const line = formatFactLine(row);
          if (!line) continue;
          if (!budget.tryAdd("fts", line.length + 1)) break;
          ftsIds.add(row.id);
          section.push(line);
        }
        if (section.length > 0) {
          lines.push("## Relevant Memories (keyword)");
          lines.push(...section);
          lines.push("");
        }
      }
    }
  }

  // 3. Recent high-importance active decisions (recency signal)
  if (budget.remaining > 100) {
    const recent = sqliteQuery(dbPath, `
      SELECT description, category, importance
      FROM decisions
      WHERE importance >= 0.7
        AND ttl_class IN ('stable', 'active')
        AND (expires_at IS NULL OR expires_at > ?)
      ORDER BY timestamp DESC
      LIMIT 5
    `, [nowMs]);

    if (recent.length > 0) {
      const section = [];
      for (const row of recent) {
        const line = formatFactLine(row);
        if (!line) continue;
        if (!budget.tryAdd("recent", line.length + 1)) break;
        section.push(line);
      }
      if (section.length > 0) {
        lines.push("## Recent Important Context");
        lines.push(...section);
        lines.push("");
      }
    }
  }

  return { lines, ftsIds, budgetReport: budget.report() };
}

/**
 * Combine FTS lines and vector results into a single XML context block.
 * Vector results are budget-capped and deduplicated against FTS results.
 *
 * @param {string[]} ftsLines - Lines from buildFtsContext
 * @param {Set<string>} ftsIds - Decision IDs already present in FTS results
 * @param {Array|null} vectorResults - Results from vectorSearch (may be null/empty)
 * @param {number} vectorBudget - Remaining character budget for vector section
 * @returns {string|null} Formatted context string or null if nothing to include
 */
export function buildRecallContext(ftsLines, ftsIds, vectorResults, vectorBudget = 800) {
  const lines = [...ftsLines];

  // Add vector search results (deduplicated against FTS results, budget-capped)
  if (vectorResults && vectorResults.length > 0 && vectorBudget > 100) {
    const newResults = vectorResults.filter((r) => !ftsIds.has(r.decision_id));
    if (newResults.length > 0) {
      const section = [];
      let used = 0;
      for (const row of newResults) {
        const sim = (row.similarity * 100).toFixed(0);
        let line;
        if (row.entity && row.fact_key) {
          const val = row.fact_value?.length > MAX_ITEM_VALUE_LENGTH
            ? row.fact_value.substring(0, MAX_ITEM_VALUE_LENGTH - 3) + "..."
            : (row.fact_value || "");
          line = `- **${row.entity}**.${row.fact_key} = ${val} _(${sim}% match)_`;
        } else if (row.description) {
          const desc = row.description?.length > MAX_ITEM_VALUE_LENGTH
            ? row.description.substring(0, MAX_ITEM_VALUE_LENGTH - 3) + "..."
            : (row.description || "");
          line = `- [${row.category || "general"}] ${desc} _(${sim}% match)_`;
        }
        if (!line) continue;
        if (used + line.length + 1 > vectorBudget) break;
        used += line.length + 1;
        section.push(line);
      }
      if (section.length > 0) {
        lines.push("## Semantically Related Memories");
        lines.push(...section);
        lines.push("");
      }
    }
  }

  if (lines.length === 0) return null;

  return [
    "<lily-memory>",
    "_Persistent memory context (auto-injected). Use memory tools for details._",
    "",
    ...lines,
    "</lily-memory>",
  ].join("\n");
}
