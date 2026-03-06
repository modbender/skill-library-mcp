import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import Database from 'better-sqlite3';

const BASE_SCHEMA_SQL = `
CREATE TABLE IF NOT EXISTS facts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category TEXT NOT NULL,
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  source TEXT,
  confidence REAL DEFAULT 1.0,
  created TEXT NOT NULL,
  updated TEXT NOT NULL,
  scope TEXT DEFAULT 'global',
  tier TEXT DEFAULT 'long-term',
  expires_at TEXT,
  last_verified TEXT,
  source_type TEXT DEFAULT 'manual',
  UNIQUE(category, key)
);

CREATE INDEX IF NOT EXISTS idx_facts_category ON facts(category);
CREATE INDEX IF NOT EXISTS idx_facts_key ON facts(key);
CREATE INDEX IF NOT EXISTS idx_facts_updated ON facts(updated);

CREATE TABLE IF NOT EXISTS relations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_fact_id INTEGER NOT NULL,
  target_fact_id INTEGER NOT NULL,
  relation_type TEXT NOT NULL,
  created TEXT NOT NULL,
  FOREIGN KEY (source_fact_id) REFERENCES facts(id) ON DELETE CASCADE,
  FOREIGN KEY (target_fact_id) REFERENCES facts(id) ON DELETE CASCADE,
  UNIQUE(source_fact_id, target_fact_id, relation_type)
);

CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_fact_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_fact_id);
`;

const FACT_COLUMN_MIGRATIONS = [
  { name: 'scope', sql: "ALTER TABLE facts ADD COLUMN scope TEXT DEFAULT 'global'" },
  { name: 'tier', sql: "ALTER TABLE facts ADD COLUMN tier TEXT DEFAULT 'long-term'" },
  { name: 'expires_at', sql: 'ALTER TABLE facts ADD COLUMN expires_at TEXT' },
  { name: 'last_verified', sql: 'ALTER TABLE facts ADD COLUMN last_verified TEXT' },
  { name: 'source_type', sql: "ALTER TABLE facts ADD COLUMN source_type TEXT DEFAULT 'manual'" },
  { name: 'access_count', sql: 'ALTER TABLE facts ADD COLUMN access_count INTEGER DEFAULT 0' },
  { name: 'last_accessed', sql: 'ALTER TABLE facts ADD COLUMN last_accessed TEXT DEFAULT NULL' }
];

const FTS_SQL = `
CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(key, value, content='facts', content_rowid='id');

CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON facts BEGIN
  INSERT INTO facts_fts(rowid, key, value) VALUES (new.id, new.key, new.value);
END;

CREATE TRIGGER IF NOT EXISTS facts_ad AFTER DELETE ON facts BEGIN
  INSERT INTO facts_fts(facts_fts, rowid, key, value) VALUES ('delete', old.id, old.key, old.value);
END;

CREATE TRIGGER IF NOT EXISTS facts_au AFTER UPDATE ON facts BEGIN
  INSERT INTO facts_fts(facts_fts, rowid, key, value) VALUES ('delete', old.id, old.key, old.value);
  INSERT INTO facts_fts(rowid, key, value) VALUES (new.id, new.key, new.value);
END;
`;

const EXTRACTION_LOG_SQL = `
CREATE TABLE IF NOT EXISTS extraction_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_path TEXT NOT NULL,
  file_hash TEXT NOT NULL,
  engine TEXT NOT NULL,
  model TEXT NOT NULL,
  facts_extracted INTEGER DEFAULT 0,
  facts_inserted INTEGER DEFAULT 0,
  facts_updated INTEGER DEFAULT 0,
  facts_skipped INTEGER DEFAULT 0,
  duration_ms INTEGER,
  status TEXT DEFAULT 'ok',
  error TEXT,
  created TEXT NOT NULL,
  UNIQUE(file_path, file_hash)
);
CREATE INDEX IF NOT EXISTS idx_extraction_log_path ON extraction_log(file_path);
CREATE INDEX IF NOT EXISTS idx_extraction_log_created ON extraction_log(created);
`;

const CHANGELOG_SQL = `
CREATE TABLE IF NOT EXISTS changelog (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fact_id INTEGER NOT NULL,
  category TEXT NOT NULL,
  key TEXT NOT NULL,
  old_value TEXT,
  new_value TEXT NOT NULL,
  change_type TEXT NOT NULL,
  source TEXT,
  created TEXT NOT NULL,
  FOREIGN KEY (fact_id) REFERENCES facts(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_changelog_fact ON changelog(fact_id);
CREATE INDEX IF NOT EXISTS idx_changelog_created ON changelog(created);
`;

const PERFORMANCE_LOG_SQL = `
CREATE TABLE IF NOT EXISTS performance_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT NOT NULL,
  category TEXT,
  detail TEXT NOT NULL,
  severity TEXT DEFAULT 'info',
  session_id TEXT,
  created TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_perf_type ON performance_log(event_type);
CREATE INDEX IF NOT EXISTS idx_perf_created ON performance_log(created);
`;

const FACT_POST_MIGRATION_INDEXES_SQL = `
CREATE INDEX IF NOT EXISTS idx_facts_scope ON facts(scope);
CREATE INDEX IF NOT EXISTS idx_facts_tier ON facts(tier);
CREATE INDEX IF NOT EXISTS idx_facts_expires_at ON facts(expires_at);
CREATE INDEX IF NOT EXISTS idx_facts_access ON facts(access_count DESC, last_accessed DESC);
`;

export const DB_PATH = path.join(os.homedir(), '.openclaw', 'memory.db');

export function ensureDbPath(dbPath = DB_PATH) {
  const dir = path.dirname(dbPath);
  fs.mkdirSync(dir, { recursive: true });
}

function tableExists(db, tableName) {
  const row = db.prepare("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?").get(tableName);
  return Boolean(row);
}

function migrateFactColumns(db) {
  const columns = new Set(db.prepare('PRAGMA table_info(facts)').all().map((row) => row.name));
  let changed = false;

  for (const migration of FACT_COLUMN_MIGRATIONS) {
    if (!columns.has(migration.name)) {
      db.exec(migration.sql);
      changed = true;
    }
  }

  return changed;
}

function backfillFacts(db) {
  db.exec("UPDATE facts SET scope = 'global' WHERE scope IS NULL OR trim(scope) = ''");
  db.exec("UPDATE facts SET tier = 'long-term' WHERE tier IS NULL OR trim(tier) = ''");
  db.exec("UPDATE facts SET source_type = 'manual' WHERE source_type IS NULL OR trim(source_type) = ''");
}

function rebuildFtsIndex(db) {
  db.prepare("INSERT INTO facts_fts(facts_fts) VALUES ('rebuild')").run();
}

export function openDb(dbPath = DB_PATH) {
  ensureDbPath(dbPath);
  const db = new Database(dbPath);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');

  db.exec(BASE_SCHEMA_SQL);
  const hadFtsTable = tableExists(db, 'facts_fts');
  const migratedColumns = migrateFactColumns(db);
  db.exec(FACT_POST_MIGRATION_INDEXES_SQL);
  backfillFacts(db);

  db.exec(FTS_SQL);
  if (!hadFtsTable || migratedColumns) {
    rebuildFtsIndex(db);
  }

  db.exec(EXTRACTION_LOG_SQL);
  db.exec(CHANGELOG_SQL);
  db.exec(PERFORMANCE_LOG_SQL);

  return db;
}

export function nowIso() {
  return new Date().toISOString();
}

/**
 * Track access to a fact (T-027: Access tracking)
 */
export function trackFactAccess(db, factId, sessionId = null) {
  const now = new Date().toISOString();
  db.prepare(`
    UPDATE facts 
    SET access_count = access_count + 1, 
        last_accessed = ?
    WHERE id = ?
  `).run(now, factId);
  
  // Optionally log to performance_log
  if (sessionId) {
    db.prepare(`
      INSERT INTO performance_log (event_type, category, detail, session_id, created)
      VALUES ('fact-access', 'memory', ?, ?, ?)
    `).run(`Accessed fact ${factId}`, sessionId, now);
  }
}

/**
 * Calculate relevance boost based on access patterns and age (T-026)
 */
export function calculateAccessBoost(fact) {
  const now = Date.now();
  const accessCount = fact.access_count || 0;
  const lastAccessed = fact.last_accessed ? new Date(fact.last_accessed).getTime() : null;
  const updated = new Date(fact.updated).getTime();
  
  // Access frequency boost (0-0.2)
  const accessBoost = Math.min(0.2, (accessCount * 0.02));
  
  // Recency boost for recently accessed facts (0-0.15)
  let recencyBoost = 0;
  if (lastAccessed) {
    const daysSinceAccess = (now - lastAccessed) / (1000 * 60 * 60 * 24);
    recencyBoost = Math.max(0, 0.15 * Math.exp(-daysSinceAccess / 7)); // Decay over 7 days
  }
  
  // Age penalty for old facts (0 to -0.1)
  const daysSinceUpdate = (now - updated) / (1000 * 60 * 60 * 24);
  const agePenalty = Math.max(-0.1, -daysSinceUpdate / 100); // Small penalty for very old facts
  
  return accessBoost + recencyBoost + agePenalty;
}
