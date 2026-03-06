import { execSync } from "node:child_process";
import path from "node:path";
import os from "node:os";

/**
 * Resolve database path, expanding ~ to home directory.
 * @param {string} configured - Configured path or null/undefined for default
 * @returns {string} Absolute path to database
 */
export function resolveDbPath(configured) {
  const raw = configured || "~/.openclaw/memory/decisions.db";
  return raw.startsWith("~") ? path.join(os.homedir(), raw.slice(1)) : raw;
}

/**
 * Escape a SQL value for safe insertion.
 * @param {*} value - Value to escape
 * @returns {string} Escaped string (WITHOUT surrounding quotes)
 */
export function escapeSqlValue(value) {
  if (value === null || value === undefined) {
    return '';
  }

  let str = String(value);

  // Remove null bytes
  str = str.replace(/\0/g, '');

  // Truncate to 10000 chars
  if (str.length > 10000) {
    str = str.substring(0, 10000);
  }

  // Escape single quotes: ' → ''
  str = str.replace(/'/g, "''");

  return str;
}

/**
 * Run a SQLite query and return parsed JSON rows.
 * @param {string} dbPath - Path to database file
 * @param {string} query - SQL query to execute
 * @returns {Array} Parsed JSON rows, or [] on error
 */
export function sqliteQuery(dbPath, query) {
  try {
    const escaped = query
      .replace(/\n/g, " ")
      .replace(/\\/g, "\\\\")
      .replace(/"/g, '\\"')
      .replace(/\$/g, "\\$");
    const raw = execSync(
      `sqlite3 -json "${dbPath}" "${escaped}"`,
      { encoding: "utf-8", timeout: 5000 }
    ).trim();
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

/**
 * Run a SQLite statement (INSERT/UPDATE/DELETE).
 * @param {string} dbPath - Path to database file
 * @param {string} statement - SQL statement to execute
 * @returns {boolean} true on success, false on error
 */
export function sqliteExec(dbPath, statement) {
  try {
    const escaped = statement
      .replace(/\n/g, " ")
      .replace(/\\/g, "\\\\")
      .replace(/"/g, '\\"')
      .replace(/\$/g, "\\$");
    execSync(
      `sqlite3 "${dbPath}" "${escaped}"`,
      { encoding: "utf-8", timeout: 5000 }
    );
    return true;
  } catch {
    return false;
  }
}

/**
 * Ensure all required tables exist in the database.
 * @param {string} dbPath - Path to database file
 * @returns {boolean} true if successful, false on error
 */
export function ensureTables(dbPath) {
  const schema = `
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    rationale TEXT NOT NULL,
    classification TEXT NOT NULL DEFAULT 'ARCHIVE',
    importance REAL NOT NULL,
    constraints TEXT,
    affected_files TEXT,
    tags TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ttl_class TEXT DEFAULT 'active',
    expires_at INTEGER,
    last_accessed_at INTEGER,
    entity TEXT,
    fact_key TEXT,
    fact_value TEXT
);

CREATE INDEX IF NOT EXISTS idx_decisions_ttl ON decisions(ttl_class);
CREATE INDEX IF NOT EXISTS idx_decisions_expires ON decisions(expires_at);
CREATE INDEX IF NOT EXISTS idx_decisions_entity ON decisions(entity);
CREATE INDEX IF NOT EXISTS idx_decisions_fact ON decisions(entity, fact_key);
CREATE INDEX IF NOT EXISTS idx_decisions_importance ON decisions(importance DESC);
CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON decisions(timestamp);

CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(
    description, rationale, entity, fact_key, fact_value, tags,
    content='decisions', content_rowid='rowid'
);

CREATE TRIGGER IF NOT EXISTS decisions_ai AFTER INSERT ON decisions BEGIN
    INSERT INTO decisions_fts(rowid, description, rationale, entity, fact_key, fact_value, tags)
    VALUES (new.rowid, new.description, new.rationale, new.entity, new.fact_key, new.fact_value, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS decisions_ad AFTER DELETE ON decisions BEGIN
    INSERT INTO decisions_fts(decisions_fts, rowid, description, rationale, entity, fact_key, fact_value, tags)
    VALUES ('delete', old.rowid, old.description, old.rationale, old.entity, old.fact_key, old.fact_value, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS decisions_au AFTER UPDATE ON decisions BEGIN
    INSERT INTO decisions_fts(decisions_fts, rowid, description, rationale, entity, fact_key, fact_value, tags)
    VALUES ('delete', old.rowid, old.description, old.rationale, old.entity, old.fact_key, old.fact_value, old.tags);
    INSERT INTO decisions_fts(rowid, description, rationale, entity, fact_key, fact_value, tags)
    VALUES (new.rowid, new.description, new.rationale, new.entity, new.fact_key, new.fact_value, new.tags);
END;

CREATE TABLE IF NOT EXISTS vectors (
    id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL,
    text_content TEXT NOT NULL,
    embedding TEXT NOT NULL,
    model TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS entities (
    name TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    added_by TEXT NOT NULL DEFAULT 'runtime',
    added_at INTEGER NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER) * 1000)
);
  `.trim();

  return sqliteExec(dbPath, schema);
}
