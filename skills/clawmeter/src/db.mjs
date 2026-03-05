import initSqlJs from 'sql.js';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { dirname } from 'path';

let _db;
let _dbPath;

// Wrapper to make sql.js API similar to better-sqlite3
class DbWrapper {
  constructor(sqlDb, dbPath) {
    this._db = sqlDb;
    this._path = dbPath;
  }

  exec(sql) {
    this._db.run(sql);
    this._save();
  }

  prepare(sql) {
    const db = this._db;
    const wrapper = this;
    return {
      run(...params) {
        db.run(sql, params);
        if (!wrapper._inTransaction) wrapper._save();
        return { changes: db.getRowsModified() };
      },
      get(...params) {
        const stmt = db.prepare(sql);
        stmt.bind(params);
        if (stmt.step()) {
          const cols = stmt.getColumnNames();
          const vals = stmt.get();
          stmt.free();
          const row = {};
          cols.forEach((c, i) => row[c] = vals[i]);
          return row;
        }
        stmt.free();
        return undefined;
      },
      all(...params) {
        const rows = [];
        const stmt = db.prepare(sql);
        stmt.bind(params);
        while (stmt.step()) {
          const cols = stmt.getColumnNames();
          const vals = stmt.get();
          const row = {};
          cols.forEach((c, i) => row[c] = vals[i]);
          rows.push(row);
        }
        stmt.free();
        return rows;
      }
    };
  }

  pragma(p) {
    try { this._db.run(`PRAGMA ${p}`); } catch {}
  }

  transaction(fn) {
    const self = this;
    return function(...args) {
      self._inTransaction = true;
      self._db.run('BEGIN');
      try {
        const result = fn(...args);
        self._db.run('COMMIT');
        self._inTransaction = false;
        self._save();
        return result;
      } catch (e) {
        self._inTransaction = false;
        try { self._db.run('ROLLBACK'); } catch {}
        throw e;
      }
    };
  }

  _save() {
    const data = this._db.export();
    writeFileSync(this._path, Buffer.from(data));
  }
}

export async function initDb(dbPath) {
  if (_db) return _db;
  _dbPath = dbPath;

  mkdirSync(dirname(dbPath), { recursive: true });
  const SQL = await initSqlJs();

  let sqlDb;
  if (existsSync(dbPath)) {
    const buf = readFileSync(dbPath);
    sqlDb = new SQL.Database(buf);
  } else {
    sqlDb = new SQL.Database();
  }

  _db = new DbWrapper(sqlDb, dbPath);
  _db.pragma('journal_mode = WAL');
  _db.pragma('foreign_keys = ON');

  _db.exec(`
    CREATE TABLE IF NOT EXISTS sessions (
      id TEXT PRIMARY KEY,
      agent TEXT NOT NULL DEFAULT 'main',
      started_at TEXT NOT NULL,
      model TEXT,
      provider TEXT,
      label TEXT,
      total_cost REAL DEFAULT 0,
      total_input_tokens INTEGER DEFAULT 0,
      total_output_tokens INTEGER DEFAULT 0,
      total_cache_read INTEGER DEFAULT 0,
      total_cache_write INTEGER DEFAULT 0,
      message_count INTEGER DEFAULT 0,
      last_ingested_line INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS usage_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT NOT NULL REFERENCES sessions(id),
      event_id TEXT NOT NULL,
      timestamp TEXT NOT NULL,
      model TEXT,
      provider TEXT,
      input_tokens INTEGER DEFAULT 0,
      output_tokens INTEGER DEFAULT 0,
      cache_read INTEGER DEFAULT 0,
      cache_write INTEGER DEFAULT 0,
      cost_input REAL DEFAULT 0,
      cost_output REAL DEFAULT 0,
      cost_cache_read REAL DEFAULT 0,
      cost_cache_write REAL DEFAULT 0,
      cost_total REAL DEFAULT 0,
      stop_reason TEXT,
      UNIQUE(session_id, event_id)
    );

    CREATE TABLE IF NOT EXISTS daily_aggregates (
      date TEXT NOT NULL,
      model TEXT NOT NULL DEFAULT 'all',
      provider TEXT NOT NULL DEFAULT 'all',
      total_cost REAL DEFAULT 0,
      total_input_tokens INTEGER DEFAULT 0,
      total_output_tokens INTEGER DEFAULT 0,
      session_count INTEGER DEFAULT 0,
      message_count INTEGER DEFAULT 0,
      PRIMARY KEY (date, model, provider)
    );

    CREATE TABLE IF NOT EXISTS alerts_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      type TEXT NOT NULL,
      threshold REAL,
      actual REAL,
      message TEXT,
      sent_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ingest_state (
      file_path TEXT PRIMARY KEY,
      last_line INTEGER DEFAULT 0,
      last_modified TEXT
    );
  `);

  // Create indexes separately (can't mix with CREATE TABLE in sql.js exec)
  try { _db.exec('CREATE INDEX IF NOT EXISTS idx_usage_session ON usage_events(session_id)'); } catch {}
  try { _db.exec('CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage_events(timestamp)'); } catch {}
  try { _db.exec('CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_aggregates(date)'); } catch {}

  return _db;
}

export function getDb() {
  if (!_db) throw new Error('Database not initialized. Call initDb() first.');
  return _db;
}
