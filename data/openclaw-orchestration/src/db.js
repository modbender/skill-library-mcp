/**
 * @module db
 * Database initialization, WAL mode, and migration runner.
 */
import Database from 'better-sqlite3';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_DB_PATH = path.join(__dirname, '..', 'data', 'orchestration.db');
const MIGRATIONS_DIR = path.join(__dirname, '..', 'migrations');

let _db = null;

/**
 * Get or create the database connection.
 * @param {string} [dbPath] - Optional path to database file
 * @returns {import('better-sqlite3').Database}
 */
export function getDb(dbPath) {
  if (_db) return _db;
  const p = dbPath || DEFAULT_DB_PATH;
  fs.mkdirSync(path.dirname(p), { recursive: true });
  _db = new Database(p);
  _db.pragma('journal_mode = WAL');
  _db.pragma('foreign_keys = ON');
  return _db;
}

/**
 * Close the database connection.
 */
export function closeDb() {
  if (_db) {
    _db.close();
    _db = null;
  }
}

/**
 * Reset the cached db reference (for testing).
 */
export function resetDb() {
  _db = null;
}

/**
 * Run pending migrations.
 * @param {import('better-sqlite3').Database} db
 */
export function runMigrations(db) {
  // Ensure _migrations table exists
  db.exec(`CREATE TABLE IF NOT EXISTS _migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    checksum TEXT NOT NULL
  )`);

  const applied = new Set(
    db.prepare('SELECT version FROM _migrations').all().map(r => r.version)
  );

  const files = fs.readdirSync(MIGRATIONS_DIR)
    .filter(f => f.endsWith('.sql'))
    .sort();

  for (const file of files) {
    const version = parseInt(file.split('_')[0], 10);
    if (applied.has(version)) continue;

    const sql = fs.readFileSync(path.join(MIGRATIONS_DIR, file), 'utf8');
    const upSection = sql.split('-- DOWN')[0].replace('-- UP', '').trim();
    const checksum = crypto.createHash('sha256').update(sql).digest('hex').slice(0, 16);

    const migrate = db.transaction(() => {
      db.exec(upSection);
      db.prepare('INSERT INTO _migrations (version, name, checksum) VALUES (?, ?, ?)')
        .run(version, file, checksum);
    });
    migrate();
  }
}

/**
 * Initialize database: open + migrate.
 * @param {string} [dbPath]
 * @returns {import('better-sqlite3').Database}
 */
export function initDb(dbPath) {
  const db = getDb(dbPath);
  runMigrations(db);
  return db;
}
