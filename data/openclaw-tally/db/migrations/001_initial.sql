CREATE TABLE IF NOT EXISTS tasks (
  task_id TEXT PRIMARY KEY,
  parent_task_id TEXT,
  started_at TEXT NOT NULL,
  completed_at TEXT,
  status TEXT NOT NULL DEFAULT 'in_progress',
  complexity_score INTEGER DEFAULT 0,
  complexity_level TEXT DEFAULT 'L1',
  quality_score REAL DEFAULT 0,
  total_tokens INTEGER DEFAULT 0,
  total_cost_usd REAL DEFAULT 0,
  tes REAL,
  models_used TEXT DEFAULT '[]',
  sessions TEXT DEFAULT '[]',
  sub_agents INTEGER DEFAULT 0,
  cron_id TEXT,
  cron_triggered INTEGER DEFAULT 0,
  tools_called INTEGER DEFAULT 0,
  tool_names TEXT DEFAULT '[]',
  external_api_calls INTEGER DEFAULT 0,
  user_turns INTEGER DEFAULT 0,
  intent_summary TEXT DEFAULT '',
  outcome_summary TEXT DEFAULT '',
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_complexity_level ON tasks(complexity_level);
CREATE INDEX IF NOT EXISTS idx_tasks_started_at ON tasks(started_at);
CREATE INDEX IF NOT EXISTS idx_tasks_cron_id ON tasks(cron_id);
