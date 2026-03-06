PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS company (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  domain TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  archived_at TEXT
);

CREATE TABLE IF NOT EXISTS project (
  id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL,
  name TEXT NOT NULL,
  stage TEXT NOT NULL,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  archived_at TEXT,
  UNIQUE(company_id, name),
  FOREIGN KEY(company_id) REFERENCES company(id)
);

CREATE TABLE IF NOT EXISTS organisation (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  archived_at TEXT
);

CREATE TABLE IF NOT EXISTS contact (
  id TEXT PRIMARY KEY,
  company_id TEXT,
  org_id TEXT,
  name TEXT NOT NULL,
  role TEXT,
  email TEXT,
  phone TEXT,
  wechat TEXT,
  channel_handles TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  archived_at TEXT,
  FOREIGN KEY(company_id) REFERENCES company(id),
  FOREIGN KEY(org_id) REFERENCES organisation(id)
);

CREATE TABLE IF NOT EXISTS activity (
  id TEXT PRIMARY KEY,
  company_id TEXT,
  project_id TEXT,
  contact_id TEXT,
  ts TEXT NOT NULL,
  channel TEXT,
  summary TEXT NOT NULL,
  details TEXT,
  source_text TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(company_id) REFERENCES company(id),
  FOREIGN KEY(project_id) REFERENCES project(id),
  FOREIGN KEY(contact_id) REFERENCES contact(id)
);

CREATE INDEX IF NOT EXISTS idx_activity_ts ON activity(ts);
CREATE INDEX IF NOT EXISTS idx_activity_company_ts ON activity(company_id, ts);
CREATE INDEX IF NOT EXISTS idx_activity_project_ts ON activity(project_id, ts);

CREATE TABLE IF NOT EXISTS task (
  id TEXT PRIMARY KEY,
  company_id TEXT,
  project_id TEXT,
  contact_id TEXT,
  created_from_activity_id TEXT,
  title TEXT NOT NULL,
  assignee TEXT,
  notes TEXT,
  due_at TEXT,
  status TEXT NOT NULL,
  priority INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  done_at TEXT,
  FOREIGN KEY(company_id) REFERENCES company(id),
  FOREIGN KEY(project_id) REFERENCES project(id),
  FOREIGN KEY(contact_id) REFERENCES contact(id),
  FOREIGN KEY(created_from_activity_id) REFERENCES activity(id)
);

CREATE INDEX IF NOT EXISTS idx_task_status_due ON task(status, due_at);
CREATE INDEX IF NOT EXISTS idx_task_company_status_due ON task(company_id, status, due_at);
CREATE INDEX IF NOT EXISTS idx_task_project_status_due ON task(project_id, status, due_at);

CREATE TABLE IF NOT EXISTS participant (
  id TEXT PRIMARY KEY,
  parent_kind TEXT NOT NULL,
  parent_id TEXT NOT NULL,
  ordinal INTEGER NOT NULL,
  label TEXT NOT NULL,
  ref_kind TEXT,
  ref_id TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(parent_kind, parent_id, ordinal),
  UNIQUE(parent_kind, parent_id, label, ref_kind, ref_id)
);

CREATE INDEX IF NOT EXISTS idx_participant_parent ON participant(parent_kind, parent_id, id);

CREATE TABLE IF NOT EXISTS draft (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  status TEXT NOT NULL,
  preview TEXT NOT NULL,
  payload TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_draft_status_created ON draft(status, created_at, id);
