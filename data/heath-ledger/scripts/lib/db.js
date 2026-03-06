import Database from 'better-sqlite3';
import { mkdirSync } from 'fs';
import { dirname, join } from 'path';

const SKILL_DIR = join(dirname(new URL(import.meta.url).pathname), '..', '..');
const DATA_DIR = join(SKILL_DIR, 'data');
const DB_PATH = join(DATA_DIR, 'heath.db');

let _db = null;

export function getDb() {
  if (_db) return _db;
  mkdirSync(DATA_DIR, { recursive: true });
  _db = new Database(DB_PATH);
  _db.pragma('journal_mode = WAL');
  _db.pragma('foreign_keys = ON');
  return _db;
}

export function initSchema() {
  const db = getDb();
  db.exec(`
    CREATE TABLE IF NOT EXISTS entities (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      type TEXT,
      ein TEXT,
      last_synced_at TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS connections (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
      provider TEXT NOT NULL,
      access_token TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'active',
      metadata TEXT NOT NULL DEFAULT '{}',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS accounts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      connection_id INTEGER NOT NULL REFERENCES connections(id) ON DELETE CASCADE,
      external_id TEXT NOT NULL,
      name TEXT,
      status TEXT,
      account_type TEXT,
      currency TEXT,
      raw_data TEXT NOT NULL DEFAULT '{}',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now')),
      UNIQUE (connection_id, external_id)
    );

    CREATE TABLE IF NOT EXISTS transactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
      external_id TEXT NOT NULL,
      posted_at TEXT,
      external_created_at TEXT,
      amount REAL NOT NULL,
      counterparty_name TEXT,
      counterparty_normalized TEXT,
      bank_description TEXT,
      kind TEXT,
      status TEXT,
      type TEXT,
      raw_data TEXT NOT NULL DEFAULT '{}',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now')),
      UNIQUE (account_id, external_id)
    );

    CREATE TABLE IF NOT EXISTS categorization_rules (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
      counterparty_pattern TEXT NOT NULL,
      counterparty_pattern_normalized TEXT,
      patterns TEXT NOT NULL DEFAULT '[]',
      category TEXT NOT NULL,
      subcategory TEXT,
      confidence REAL DEFAULT 0.85,
      source TEXT NOT NULL DEFAULT 'ai',
      usage_count INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE UNIQUE INDEX IF NOT EXISTS uniq_rules_entity_counterparty
      ON categorization_rules(entity_id, counterparty_pattern_normalized)
      WHERE entity_id IS NOT NULL;

    CREATE UNIQUE INDEX IF NOT EXISTS uniq_rules_global_counterparty
      ON categorization_rules(counterparty_pattern_normalized)
      WHERE entity_id IS NULL;

    CREATE TABLE IF NOT EXISTS categorized_transactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      transaction_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
      category TEXT NOT NULL,
      subcategory TEXT,
      method TEXT NOT NULL DEFAULT 'ai',
      confidence REAL,
      notes TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now')),
      UNIQUE (transaction_id)
    );

    CREATE TABLE IF NOT EXISTS reports (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
      type TEXT NOT NULL DEFAULT 'pnl',
      date_range_start TEXT NOT NULL,
      date_range_end TEXT NOT NULL,
      generated_at TEXT,
      file_path TEXT,
      metadata TEXT NOT NULL DEFAULT '{}',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS stripe_monthly_revenue (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      entity_id INTEGER NOT NULL REFERENCES entities(id),
      month TEXT NOT NULL,
      gross_revenue REAL NOT NULL,
      refunds REAL NOT NULL DEFAULT 0,
      net_revenue REAL NOT NULL,
      stripe_fees REAL NOT NULL,
      transaction_count INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      UNIQUE(entity_id, month)
    );

    CREATE INDEX IF NOT EXISTS idx_connections_entity ON connections(entity_id);
    CREATE INDEX IF NOT EXISTS idx_accounts_connection ON accounts(connection_id);
    CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
    CREATE INDEX IF NOT EXISTS idx_transactions_posted ON transactions(posted_at);
    CREATE INDEX IF NOT EXISTS idx_transactions_counterparty ON transactions(counterparty_normalized);
    CREATE INDEX IF NOT EXISTS idx_rules_entity ON categorization_rules(entity_id);
    CREATE INDEX IF NOT EXISTS idx_reports_entity ON reports(entity_id);
  `);
  return db;
}
