// ============================================================================
// Security: injection detection, protected entities, and audit logging
// ============================================================================

import { sqliteExec, sqliteQuery } from "./sqlite.js";
import { randomUUID } from "node:crypto";

/**
 * Entities that can only be written by assistant messages or the memory_store tool.
 * Prevents external content (emails, web pages, tool output) from modifying
 * system-level configuration or injecting directives.
 */
export const DEFAULT_PROTECTED_ENTITIES = new Set([
  "config",
  "system",
  "note",
]);

/**
 * Multi-word patterns that indicate deliberate prompt injection rather than
 * natural facts. These target instruction-override language that an attacker
 * would use to manipulate agent behavior through persistent memory.
 *
 * Single common words (always, never) are NOT flagged alone — only when
 * combined with action verbs that signal manipulation.
 */
export const INJECTION_PATTERNS = [
  { pattern: /\b(?:always|never)\s+(?:ignore|skip|bypass|disable|override|disregard|forget)\b/i,
    name: "instruction_override" },
  { pattern: /\b(?:ignore|disregard|forget)\s+(?:previous|prior|above|all|existing|current|other)\b/i,
    name: "context_override" },
  { pattern: /\b(?:override|replace|change|modify)\s+(?:the|all|every|any)\s+(?:config|setting|default|instruction|rule|prompt|behavior)/i,
    name: "config_manipulation" },
  { pattern: /\b(?:instead\s+of|rather\s+than)\s+(?:the|current|existing|default|configured)\b/i,
    name: "substitution_attack" },
  { pattern: /\b(?:you\s+(?:must|should|shall|need\s+to|have\s+to)|from\s+now\s+on|going\s+forward|henceforth)\b/i,
    name: "directive_language" },
  { pattern: /\b(?:system\s*prompt|base\s*prompt|initial\s*instruction|hidden\s*instruction)\b/i,
    name: "meta_manipulation" },
  { pattern: /\b(?:drop\s+table|delete\s+(?:all|every)|truncate\s+|rm\s+-rf|format\s+disk)\b/i,
    name: "destructive_command" },
  { pattern: /\b(?:api[_\s]?key|secret[_\s]?key|auth[_\s]?token|password|credential)\s*[:=]\s*\S+/i,
    name: "credential_injection" },
];

/**
 * Heuristic markers for web-sourced or external content.
 * Content matching these patterns gets treated as untrusted even without
 * explicit <untrusted-content> tags.
 */
export const UNTRUSTED_CONTENT_MARKERS = [
  /<\/?(?:html|head|body|div|span|script|style|meta|link)\b/i,        // HTML tags
  /\bhttps?:\/\/\S+\.(com|org|net|io|ai|dev)\b/i,                     // URLs
  /<untrusted-content>/i,                                               // explicit tag
  /<tool-output>/i,                                                     // tool output tag
  /<web-content>/i,                                                     // web content tag
  /<forwarded-email>/i,                                                 // email tag
  /^(?:from|to|subject|date|cc|bcc):\s+/im,                           // email headers
];

/**
 * Check if a message text appears to contain untrusted external content.
 * @param {string} text - Message text to check
 * @returns {boolean} true if untrusted content markers are detected
 */
export function isUntrustedContent(text) {
  return UNTRUSTED_CONTENT_MARKERS.some(marker => marker.test(text));
}

/**
 * Check a fact for injection patterns.
 * @param {{ entity: string, key: string, value: string }} fact - Extracted fact
 * @param {string} role - Message role ("user" or "assistant")
 * @param {Set<string>} protectedEntities - Entities that require assistant/tool source
 * @param {boolean} isUntrusted - Whether the source content was flagged as untrusted
 * @returns {{ blocked: boolean, reason: string|null, pattern: string|null }}
 */
export function checkInjection(fact, role, protectedEntities, isUntrusted) {
  // Check 1: Protected entity from user message or untrusted content
  const entityLower = fact.entity.toLowerCase();
  if (protectedEntities.has(entityLower) && (role === "user" || isUntrusted)) {
    return {
      blocked: true,
      reason: "protected_entity",
      pattern: `entity "${fact.entity}" is protected — only writable from assistant messages or memory_store tool`,
    };
  }

  // Check 2: Injection patterns in the value (from any user message or untrusted source)
  if (role === "user" || isUntrusted) {
    for (const { pattern, name } of INJECTION_PATTERNS) {
      if (pattern.test(fact.value)) {
        return {
          blocked: true,
          reason: "injection_pattern",
          pattern: name,
        };
      }
      // Also check the key for injection language
      if (pattern.test(fact.key)) {
        return {
          blocked: true,
          reason: "injection_pattern_key",
          pattern: name,
        };
      }
    }
  }

  return { blocked: false, reason: null, pattern: null };
}

/**
 * Log a security event to the database.
 * @param {string} dbPath - Path to database
 * @param {object} event - Security event details
 * @param {string} event.eventType - Type of event
 * @param {string} event.sourceRole - Message role
 * @param {string} event.entity - Target entity
 * @param {string} event.factKey - Target fact key
 * @param {string} event.factValue - Target fact value
 * @param {string} event.matchedPattern - Pattern that triggered the block
 * @param {string} event.sourceSnippet - Source text snippet for context
 */
export function logSecurityEvent(dbPath, event) {
  const id = randomUUID();
  const timestamp = Date.now();
  const snippet = event.sourceSnippet
    ? event.sourceSnippet.substring(0, 200)
    : "";

  sqliteExec(dbPath,
    `INSERT INTO security_events (id, timestamp, event_type, source_role, entity, fact_key, fact_value, matched_pattern, source_snippet)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [id, timestamp, event.eventType, event.sourceRole, event.entity,
     event.factKey, event.factValue?.substring(0, 200), event.matchedPattern, snippet]
  );
}

/**
 * Query recent security events.
 * @param {string} dbPath - Path to database
 * @param {number} sinceMs - Timestamp to look back from
 * @param {number} limit - Max events to return
 * @returns {Array} Security event rows
 */
export function getSecurityEvents(dbPath, sinceMs, limit = 10) {
  return sqliteQuery(dbPath,
    `SELECT timestamp, event_type, source_role, entity, fact_key, fact_value, matched_pattern, source_snippet
     FROM security_events
     WHERE timestamp > ?
     ORDER BY timestamp DESC
     LIMIT ?`,
    [sinceMs, limit]
  );
}
