import { sqliteQuery, sqliteExec, escapeSqlValue } from './sqlite.js';

/**
 * Default generic entity names (no personal names).
 * Personal names should be added via user config.
 */
export const DEFAULT_ENTITIES = new Set([
  "config",
  "system",
  "note",
  "project",
]);

/**
 * Common English words that look like entities but aren't.
 * These are rejected regardless of case or position.
 */
export const REJECT_WORDS = new Set([
  "still", "just", "acts", "you", "it", "the", "this", "that", "they",
  "we", "he", "she", "my", "or", "if", "up", "an", "no", "so", "do",
  "go", "is", "are", "was", "has", "had", "can", "not", "but", "and",
  "also", "very", "much", "more", "less", "what", "how", "why", "where",
  "when", "who", "well", "oh", "ah", "looks", "community", "here",
  "there", "then", "now", "already", "really", "actually", "maybe",
  "would", "each",
]);

/**
 * Validate an entity name. Accepts:
 * - Known names from runtimeEntities Set (case-insensitive)
 * - PascalCase multi-word names (e.g., "TradingSystem", "MemoryPlugin")
 * - Dotted paths (e.g., "User.preferred_language")
 * Rejects:
 * - Common English words (Still, Just, Acts, You, It, etc.)
 * - Single lowercase words not in runtimeEntities
 * - Words < 2 chars or > 60 chars
 * - Names starting with numbers, http, www
 *
 * @param {string} entity - Entity name to validate
 * @param {Set<string>} runtimeEntities - Set of lowercase valid entity names
 * @returns {boolean} true if valid entity
 */
export function isValidEntity(entity, runtimeEntities) {
  if (!entity || typeof entity !== 'string' || entity.length < 2 || entity.length > 60) {
    return false;
  }

  // Reject names starting with numbers, http, www
  if (/^[0-9]/.test(entity) || entity.toLowerCase().startsWith('http') || entity.toLowerCase().startsWith('www')) {
    return false;
  }

  // Extract base name (before first dot)
  const baseName = entity.split(".")[0].toLowerCase();

  // Reject common English words
  if (REJECT_WORDS.has(baseName)) {
    return false;
  }

  // Check against runtime entities (case-insensitive)
  if (runtimeEntities.has(baseName)) {
    return true;
  }

  // Accept PascalCase multi-word names (e.g., TradingSystem, MemoryPlugin)
  // Pattern: starts with uppercase letter, followed by lowercase, then another uppercase
  if (/^[A-Z][a-z]+[A-Z]/.test(entity)) {
    return true;
  }

  // Reject everything else
  return false;
}

/**
 * Load entity names from the database.
 * @param {string} dbPath - Path to SQLite database
 * @returns {string[]} Array of entity names from database
 */
export function loadEntitiesFromDb(dbPath) {
  const rows = sqliteQuery(dbPath, 'SELECT name FROM entities');
  return rows.map(row => row.name);
}

/**
 * Add a new entity to the database.
 * @param {string} dbPath - Path to SQLite database
 * @param {string} name - Entity name to add
 * @param {string} addedBy - Source that added this entity (e.g., "runtime", "config")
 * @returns {boolean} true on success, false on failure
 */
export function addEntityToDb(dbPath, name, addedBy) {
  // Validate name format
  if (!name || typeof name !== 'string') {
    return false;
  }

  if (!/^[A-Za-z][A-Za-z0-9_.]*$/.test(name)) {
    return false;
  }

  if (name.length < 2 || name.length > 60) {
    return false;
  }

  // Insert with OR IGNORE to handle duplicates gracefully
  const timestamp = Date.now();
  const sql = `
    INSERT OR IGNORE INTO entities (name, display_name, added_by, added_at)
    VALUES ('${escapeSqlValue(name)}', '${escapeSqlValue(name)}', '${escapeSqlValue(addedBy)}', ${timestamp})
  `.trim();

  return sqliteExec(dbPath, sql);
}

/**
 * Merge entity names from config and database into a unified Set.
 * All names are converted to lowercase for case-insensitive matching.
 *
 * @param {string[]} configEntities - Entity names from plugin config
 * @param {string[]} dbEntities - Entity names from database
 * @returns {Set<string>} Unified set of lowercase entity names
 */
export function mergeConfigEntities(configEntities, dbEntities) {
  const merged = new Set();

  // Add defaults
  for (const entity of DEFAULT_ENTITIES) {
    merged.add(entity.toLowerCase());
  }

  // Add config entities
  if (Array.isArray(configEntities)) {
    for (const entity of configEntities) {
      if (entity && typeof entity === 'string') {
        merged.add(entity.toLowerCase());
      }
    }
  }

  // Add database entities
  if (Array.isArray(dbEntities)) {
    for (const entity of dbEntities) {
      if (entity && typeof entity === 'string') {
        merged.add(entity.toLowerCase());
      }
    }
  }

  return merged;
}
