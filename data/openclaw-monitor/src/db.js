/**
 * @module db
 * Database initialization, WAL mode, and migration runner for openclaw-monitor.
 */

import Database from 'better-sqlite3';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const MIGRATIONS_DIR = path.join(__dirname, '..', 'migrations');
const DEFAULT_DB_PATH = path.join(__dirname, '..', 'data', 'monitor.db');

/** @type {Database.Database | null} */
let _db = null;

/**
 * Get or create the database connection.
 * @param {string} [dbPath] - Override database path (useful for testing)
 * @returns {Database.Database}
 */
export function getDb(dbPath) {
  if (_db) return _db;
  const p = dbPath || DEFAULT_DB_PATH;
  fs.mkdirSync(path.dirname(p), { recursive: true });
  _db = new Database(p);
  _db.pragma('journal_mode = WAL');
  _db.pragma('foreign_keys = ON');
  runMigrations(_db);
  return _db;
}

/**
 * Initialize a new database connection (for testing — always returns fresh).
 * @param {string} dbPath
 * @returns {Database.Database}
 */
export function initDb(dbPath) {
  const p = dbPath || DEFAULT_DB_PATH;
  fs.mkdirSync(path.dirname(p), { recursive: true });
  const db = new Database(p);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');
  runMigrations(db);
  return db;
}

/**
 * Close the shared database connection.
 */
export function closeDb() {
  if (_db) {
    _db.close();
    _db = null;
  }
}

/**
 * Run all pending migrations.
 * @param {Database.Database} db
 */
export function runMigrations(db) {
  // Ensure _migrations table exists
  db.exec(`CREATE TABLE IF NOT EXISTS _migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL,
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
    const checksum = crypto.createHash('sha256').update(sql).digest('hex').slice(0, 16);

    const migrate = db.transaction(() => {
      db.exec(sql);
      db.prepare(
        'INSERT INTO _migrations (version, name, applied_at, checksum) VALUES (?, ?, datetime(\'now\'), ?)'
      ).run(version, file, checksum);
    });
    migrate();
  }
}
