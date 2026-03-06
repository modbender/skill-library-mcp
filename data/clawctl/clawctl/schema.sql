-- clawctl schema v0.2
-- Shared coordination layer for OpenClaw agent fleets

CREATE TABLE IF NOT EXISTS tasks (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  subject     TEXT NOT NULL,
  description TEXT,
  status      TEXT DEFAULT 'pending'
                CHECK(status IN ('pending','claimed','in_progress','blocked','review','done','cancelled')),
  owner       TEXT,
  created_by  TEXT,
  priority    INTEGER DEFAULT 0,
  parent_id   INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
  tags        TEXT DEFAULT '[]',
  created_at  TEXT DEFAULT (datetime('now')),
  updated_at  TEXT DEFAULT (datetime('now')),
  claimed_at  TEXT,
  completed_at TEXT
);

CREATE TABLE IF NOT EXISTS task_deps (
  task_id     INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  blocked_by  INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  created_at  TEXT DEFAULT (datetime('now')),
  UNIQUE(task_id, blocked_by)
);

CREATE TABLE IF NOT EXISTS messages (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  from_agent  TEXT NOT NULL,
  to_agent    TEXT,
  task_id     INTEGER REFERENCES tasks(id),
  body        TEXT NOT NULL,
  msg_type    TEXT DEFAULT 'comment'
                CHECK(msg_type IN ('comment','status','handoff','question','answer','alert')),
  created_at  TEXT DEFAULT (datetime('now')),
  read_at     TEXT
);

CREATE TABLE IF NOT EXISTS agents (
  name        TEXT PRIMARY KEY,
  role        TEXT,
  last_seen   TEXT,
  status      TEXT DEFAULT 'idle'
                CHECK(status IN ('idle','busy','offline')),
  session_id  TEXT,
  registered_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS activity (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  agent       TEXT,
  action      TEXT NOT NULL,
  target_type TEXT,
  target_id   INTEGER,
  detail      TEXT,
  meta        TEXT,
  created_at  TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_owner ON tasks(owner);
CREATE INDEX IF NOT EXISTS idx_tasks_status_owner ON tasks(status, owner);
CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_id);
CREATE INDEX IF NOT EXISTS idx_task_deps_task ON task_deps(task_id);
CREATE INDEX IF NOT EXISTS idx_messages_to ON messages(to_agent);
CREATE INDEX IF NOT EXISTS idx_messages_unread ON messages(to_agent, read_at);
CREATE INDEX IF NOT EXISTS idx_activity_time ON activity(created_at);
