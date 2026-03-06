-- Migration 001: Initial schema

CREATE TABLE IF NOT EXISTS token_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  model TEXT NOT NULL,
  tokens_in INTEGER NOT NULL,
  tokens_out INTEGER NOT NULL,
  cost REAL NOT NULL,
  skill TEXT,
  timestamp TEXT NOT NULL DEFAULT (datetime('now')),
  event_source TEXT NOT NULL DEFAULT 'manual',
  event_id TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS task_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  command TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('success', 'failure', 'timeout')),
  duration_ms INTEGER NOT NULL,
  error TEXT,
  timestamp TEXT NOT NULL DEFAULT (datetime('now')),
  event_id TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS cron_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_name TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('success', 'failure')),
  started TEXT NOT NULL DEFAULT (datetime('now')),
  duration_ms INTEGER NOT NULL,
  error TEXT,
  event_id TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_aggregates (
  date TEXT PRIMARY KEY,
  total_tokens_in INTEGER NOT NULL DEFAULT 0,
  total_tokens_out INTEGER NOT NULL DEFAULT 0,
  total_cost REAL NOT NULL DEFAULT 0,
  task_success INTEGER NOT NULL DEFAULT 0,
  task_failure INTEGER NOT NULL DEFAULT 0,
  computed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS _migrations (
  version INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  applied_at TEXT NOT NULL,
  checksum TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_token_events_timestamp ON token_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_token_events_model ON token_events(model);
CREATE INDEX IF NOT EXISTS idx_task_events_timestamp ON task_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_cron_runs_job_name ON cron_runs(job_name);
