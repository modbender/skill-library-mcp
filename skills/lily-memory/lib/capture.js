// ============================================================================
// Auto-capture: extract facts from messages (with entity validation + limits)
// ============================================================================

import { sqliteQuery, sqliteExec, sanitizeValue } from "./sqlite.js";
import { extractFacts, MAX_VALUE_LENGTH } from "./extraction.js";
import { checkInjection, isUntrustedContent, logSecurityEvent, DEFAULT_PROTECTED_ENTITIES } from "./security.js";
import { randomUUID } from "node:crypto";

/** Maximum active entries in the database. Evict lowest-importance when exceeded. */
export const MAX_ACTIVE_ENTRIES = 50;

/** Maximum stable entries in the database. */
export const MAX_STABLE_ENTRIES = 30;

/** Status keywords that should auto-downgrade to session TTL. */
const STATUS_KEYWORDS = /(?:status|complete|deployed|spawned|launched|ready|sprint|checklist|final_state|session_|restart|attempt|debug|fix_|milestone|infrastructure|live_|validation_)/i;

/**
 * Capture facts from conversation messages and store them in the database.
 * Enforces value length limits, global entry count caps, and injection detection.
 *
 * @param {string} dbPath - Path to SQLite database
 * @param {Array} messages - Array of {role, content} message objects
 * @param {number} maxCapture - Maximum number of facts to capture this call
 * @param {Set<string>} runtimeEntities - Set of lowercase known entity names
 * @param {Function|null} logger - logger(msg) for status; falls back to console.log
 * @param {object} [securityOpts] - Security options
 * @param {Set<string>} [securityOpts.protectedEntities] - Entities only writable from assistant/tool
 * @param {string} [securityOpts.capturePolicy] - "all" | "assistant-only" | "tagged-only"
 * @returns {{ stored: number, newDecisionIds: Array<{id: string, text: string}>, blocked: number }}
 */
export function captureFromMessages(dbPath, messages, maxCapture, runtimeEntities, logger, securityOpts = {}) {
  const log = logger ?? console.log;
  const nowMs = Date.now();
  let stored = 0;
  let blocked = 0;
  const newDecisionIds = [];

  const protectedEntities = securityOpts.protectedEntities || DEFAULT_PROTECTED_ENTITIES;
  const capturePolicy = securityOpts.capturePolicy || "all";

  // Flatten messages to { role, text } pairs
  const texts = [];
  for (const msg of messages) {
    if (!msg || typeof msg !== "object") continue;
    const role = msg.role;
    if (role !== "user" && role !== "assistant") continue;

    const content = msg.content;
    if (typeof content === "string") {
      texts.push({ role, text: content });
      continue;
    }
    if (Array.isArray(content)) {
      for (const block of content) {
        if (block && typeof block === "object" && block.type === "text" && typeof block.text === "string") {
          texts.push({ role, text: block.text });
        }
      }
    }
  }

  for (const { role, text } of texts) {
    if (stored >= maxCapture) break;

    // Skip injected memory context
    if (text.includes("<lily-memory>") || text.includes("<relevant-memories>")) continue;
    // Skip very short or very long
    if (text.length < 30 || text.length > 5000) continue;

    // Capture policy enforcement
    if (capturePolicy === "assistant-only" && role === "user") continue;
    if (capturePolicy === "tagged-only" && !text.includes("<trusted-capture>")) continue;

    // Detect untrusted external content (emails, web pages, tool output)
    const untrusted = role === "user" && isUntrustedContent(text);

    const facts = extractFacts(text, runtimeEntities);
    for (const fact of facts) {
      if (stored >= maxCapture) break;

      // Enforce value length cap (defense-in-depth with extraction.js)
      if (fact.value.length > MAX_VALUE_LENGTH) continue;

      // Security: check for injection patterns and protected entities
      const secCheck = checkInjection(fact, role, protectedEntities, untrusted);
      if (secCheck.blocked) {
        blocked++;
        log(`lily-memory: BLOCKED — ${secCheck.reason}: ${fact.entity}.${fact.key} (pattern: ${secCheck.pattern})`);
        logSecurityEvent(dbPath, {
          eventType: secCheck.reason,
          sourceRole: role,
          entity: fact.entity,
          factKey: fact.key,
          factValue: fact.value,
          matchedPattern: secCheck.pattern,
          sourceSnippet: text,
        });
        continue;
      }

      const entity = sanitizeValue(fact.entity);
      const key = sanitizeValue(fact.key);
      const value = sanitizeValue(fact.value);

      // Check if this fact already exists
      const existing = sqliteQuery(dbPath,
        `SELECT id FROM decisions WHERE entity = ? AND fact_key = ? AND (expires_at IS NULL OR expires_at > ?) LIMIT 1`,
        [entity, key, nowMs]
      );

      if (existing.length > 0) {
        const existingId = existing[0].id;
        const description = `${fact.entity}.${fact.key} = ${fact.value}`;
        sqliteExec(dbPath,
          `UPDATE decisions SET fact_value = ?, description = ?, timestamp = ?, last_accessed_at = ? WHERE id = ?`,
          [value, description, nowMs, nowMs, existingId]
        );
        newDecisionIds.push({ id: existing[0].id, text: `${fact.entity}.${fact.key} = ${fact.value}` });
        log(`lily-memory: updated fact ${fact.entity}.${fact.key}`);
        continue;
      }

      // Heuristic TTL assignment
      // User-sourced facts get shorter TTL and lower importance (defense-in-depth)
      // Status facts always get session TTL regardless of source
      let ttlClass;
      if (STATUS_KEYWORDS.test(fact.key)) {
        ttlClass = "session";
      } else if (role === "user") {
        ttlClass = "active";    // 14d (downgraded from stable/90d)
      } else {
        ttlClass = "active";    // 14d for assistant
      }

      const ttlMs = { permanent: null, stable: 90 * 86400000, active: 14 * 86400000, session: 86400000 };
      const expiresAt = ttlMs[ttlClass] === null ? null : nowMs + ttlMs[ttlClass];

      // Importance: user-sourced facts get lower importance than assistant-sourced
      const importance = role === "user" ? 0.5 : 0.6;

      // Enforce global active entry cap — evict lowest-importance if full
      if (ttlClass === "active") {
        const countResult = sqliteQuery(dbPath,
          `SELECT COUNT(*) as cnt FROM decisions WHERE ttl_class = 'active' AND (expires_at IS NULL OR expires_at > ?)`,
          [nowMs]
        );
        if (countResult[0]?.cnt >= MAX_ACTIVE_ENTRIES) {
          const evicted = sqliteQuery(dbPath,
            `SELECT id FROM decisions WHERE ttl_class = 'active' AND (expires_at IS NULL OR expires_at > ?) ORDER BY importance ASC, timestamp ASC LIMIT 1`,
            [nowMs]
          );
          if (evicted.length > 0) {
            sqliteExec(dbPath, `DELETE FROM decisions WHERE id = ?`, [evicted[0].id]);
            sqliteExec(dbPath, `DELETE FROM vectors WHERE decision_id = ?`, [evicted[0].id]);
            log(`lily-memory: evicted low-importance active entry to make room`);
          }
        }
      }

      // Enforce global stable entry cap
      if (ttlClass === "stable") {
        const countResult = sqliteQuery(dbPath,
          `SELECT COUNT(*) as cnt FROM decisions WHERE ttl_class = 'stable' AND (expires_at IS NULL OR expires_at > ?)`,
          [nowMs]
        );
        if (countResult[0]?.cnt >= MAX_STABLE_ENTRIES) {
          const evicted = sqliteQuery(dbPath,
            `SELECT id FROM decisions WHERE ttl_class = 'stable' AND (expires_at IS NULL OR expires_at > ?) ORDER BY importance ASC, timestamp ASC LIMIT 1`,
            [nowMs]
          );
          if (evicted.length > 0) {
            sqliteExec(dbPath, `DELETE FROM decisions WHERE id = ?`, [evicted[0].id]);
            sqliteExec(dbPath, `DELETE FROM vectors WHERE decision_id = ?`, [evicted[0].id]);
            log(`lily-memory: evicted low-importance stable entry to make room`);
          }
        }
      }

      const id = randomUUID();
      const description = `${fact.entity}.${fact.key} = ${fact.value}`;
      const ok = sqliteExec(dbPath,
        `INSERT INTO decisions (id, session_id, timestamp, category, description, rationale, classification, importance, ttl_class, expires_at, last_accessed_at, entity, fact_key, fact_value, tags)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [id, 'plugin-auto', nowMs, 'auto-capture', description, 'Auto-captured by lily-memory plugin v5', 'ARCHIVE', importance, ttlClass, expiresAt, nowMs, entity, key, value, '["auto-capture","v5"]']
      );

      if (ok) {
        stored++;
        newDecisionIds.push({ id, text: `${fact.entity}.${fact.key} = ${fact.value}` });
        log(`lily-memory: captured ${fact.entity}.${fact.key} = ${fact.value}`);
      }
    }
  }

  return { stored, newDecisionIds, blocked };
}
