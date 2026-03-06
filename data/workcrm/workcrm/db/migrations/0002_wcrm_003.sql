-- version: 2
-- WCRM-003 schema expansion: organisation/contact enhancements, participants, drafts

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS organisation (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  archived_at TEXT
);

ALTER TABLE contact ADD COLUMN org_id TEXT;
ALTER TABLE contact ADD COLUMN channel_handles TEXT; -- JSON

CREATE TABLE IF NOT EXISTS participant (
  id TEXT PRIMARY KEY,
  parent_kind TEXT NOT NULL, -- 'activity' | 'task'
  parent_id TEXT NOT NULL,
  label TEXT NOT NULL,
  ref_kind TEXT, -- 'contact' | 'organisation'
  ref_id TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(parent_kind, parent_id, label, ref_kind, ref_id)
);

CREATE INDEX IF NOT EXISTS idx_participant_parent ON participant(parent_kind, parent_id, id);

CREATE TABLE IF NOT EXISTS draft (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL, -- 'log' | 'task'
  status TEXT NOT NULL, -- 'pending' | 'committed' | 'rejected'
  preview TEXT NOT NULL, -- JSON
  payload TEXT NOT NULL, -- JSON
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_draft_status_created ON draft(status, created_at, id);
