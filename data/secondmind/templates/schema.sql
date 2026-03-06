-- ============================================================
-- SECONDMIND – SQLite Schema v1.0
-- Single database, all tiers in one file
-- No sqlite-vec dependency – uses FTS5 + LLM reranking
-- ============================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ============================================================
-- TIER 1: SHORT-TERM BUFFER (raw chat ingestion)
-- ============================================================

CREATE TABLE IF NOT EXISTS shortterm_buffer (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  source      TEXT NOT NULL,        -- 'skill_hook', 'session_watcher', 'cron_diff'
  session_id  TEXT NOT NULL,        -- OpenClaw Session UUID
  channel     TEXT,                 -- 'telegram', 'discord', 'web'
  raw_content TEXT NOT NULL,
  ingested_at DATETIME DEFAULT (datetime('now')),
  processed   BOOLEAN DEFAULT 0,
  token_count INTEGER,
  is_complete BOOLEAN DEFAULT 0    -- Session finished? (/new triggered)
);

-- Dedup: One complete session ingested once (first writer wins)
CREATE UNIQUE INDEX IF NOT EXISTS idx_buffer_session_complete
  ON shortterm_buffer(session_id) WHERE is_complete = 1;

-- Fast lookup for active session deltas
CREATE INDEX IF NOT EXISTS idx_buffer_unprocessed
  ON shortterm_buffer(processed) WHERE processed = 0;

-- ============================================================
-- TIER 2: MID-TERM KNOWLEDGE (structured extraction)
-- ============================================================

CREATE TABLE IF NOT EXISTS knowledge_entries (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  category     TEXT NOT NULL,       -- project, problem, idea, fact, todo,
                                    -- preference, skill, person, social
  title        TEXT NOT NULL,
  summary      TEXT NOT NULL,       -- Max ~200 tokens
  details      TEXT,
  tags         TEXT,                -- JSON array: ["3d-druck", "bambu-lab"]
  status       TEXT DEFAULT 'active', -- active, resolved, obsolete
  source_ref   TEXT,                -- session_id reference
  first_seen   DATETIME DEFAULT (datetime('now')),
  last_updated DATETIME DEFAULT (datetime('now')),
  update_count INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_entries(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_status ON knowledge_entries(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_updated ON knowledge_entries(last_updated);

-- FTS5 full-text search on knowledge
CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
  title, summary, details, tags,
  content=knowledge_entries, content_rowid=id
);

-- Triggers to keep FTS5 in sync
CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge_entries BEGIN
  INSERT INTO knowledge_fts(rowid, title, summary, details, tags)
  VALUES (new.id, new.title, new.summary, new.details, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge_entries BEGIN
  INSERT INTO knowledge_fts(knowledge_fts, rowid, title, summary, details, tags)
  VALUES ('delete', old.id, old.title, old.summary, old.details, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS knowledge_au AFTER UPDATE ON knowledge_entries BEGIN
  INSERT INTO knowledge_fts(knowledge_fts, rowid, title, summary, details, tags)
  VALUES ('delete', old.id, old.title, old.summary, old.details, old.tags);
  INSERT INTO knowledge_fts(rowid, title, summary, details, tags)
  VALUES (new.id, new.title, new.summary, new.details, new.tags);
END;

-- Relations between knowledge entries
CREATE TABLE IF NOT EXISTS knowledge_relations (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  from_id   INTEGER REFERENCES knowledge_entries(id) ON DELETE CASCADE,
  to_id     INTEGER REFERENCES knowledge_entries(id) ON DELETE CASCADE,
  relation  TEXT NOT NULL,          -- depends_on, related_to, part_of, blocks
  created   DATETIME DEFAULT (datetime('now'))
);

-- ============================================================
-- TIER 3: LONG-TERM ARCHIVE (permanent, searchable)
-- ============================================================

CREATE TABLE IF NOT EXISTS longterm_archive (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  knowledge_id   INTEGER UNIQUE,    -- Source knowledge_entries.id
  category       TEXT NOT NULL,
  title          TEXT NOT NULL,
  summary        TEXT NOT NULL,
  details        TEXT,
  tags           TEXT,
  archived_at    DATETIME DEFAULT (datetime('now')),
  relevance_score REAL DEFAULT 1.0
);

-- FTS5 for longterm search
CREATE VIRTUAL TABLE IF NOT EXISTS longterm_fts USING fts5(
  title, summary, details, tags,
  content=longterm_archive, content_rowid=id
);

CREATE TRIGGER IF NOT EXISTS longterm_ai AFTER INSERT ON longterm_archive BEGIN
  INSERT INTO longterm_fts(rowid, title, summary, details, tags)
  VALUES (new.id, new.title, new.summary, new.details, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS longterm_ad AFTER DELETE ON longterm_archive BEGIN
  INSERT INTO longterm_fts(longterm_fts, rowid, title, summary, details, tags)
  VALUES ('delete', old.id, old.title, old.summary, old.details, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS longterm_au AFTER UPDATE ON longterm_archive BEGIN
  INSERT INTO longterm_fts(longterm_fts, rowid, title, summary, details, tags)
  VALUES ('delete', old.id, old.title, old.summary, old.details, old.tags);
  INSERT INTO longterm_fts(rowid, title, summary, details, tags)
  VALUES (new.id, new.title, new.summary, new.details, new.tags);
END;

-- ============================================================
-- PROPOSALS: Initiative tracking
-- ============================================================

CREATE TABLE IF NOT EXISTS proposals (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  type            TEXT NOT NULL,     -- automation, project, tool, optimization,
                                     -- fix, social_help, learning
  title           TEXT NOT NULL,
  description     TEXT NOT NULL,
  reasoning       TEXT,              -- Why was this proposed?
  follow_up       TEXT,              -- Follow-up question to ask the user
  source_ids      TEXT,              -- JSON array of knowledge_entry IDs
  priority        TEXT DEFAULT 'medium', -- low, medium, high, critical
  status          TEXT DEFAULT 'proposed', -- proposed, accepted, rejected,
                                           -- in_progress, completed, deferred
  user_feedback   TEXT,
  proposed_at     DATETIME DEFAULT (datetime('now')),
  resolved_at     DATETIME,
  effort_estimate TEXT               -- quick (<1h), medium (1-4h), large (>4h)
);

CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status);
CREATE INDEX IF NOT EXISTS idx_proposals_type ON proposals(type);

CREATE TABLE IF NOT EXISTS proposal_outcomes (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  proposal_id INTEGER REFERENCES proposals(id) ON DELETE CASCADE,
  outcome     TEXT NOT NULL,         -- success, partial, failed, abandoned
  notes       TEXT,
  recorded_at DATETIME DEFAULT (datetime('now'))
);

-- ============================================================
-- PROJECTS: Track accepted proposals as active projects
-- ============================================================

CREATE TABLE IF NOT EXISTS projects (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  proposal_id   INTEGER UNIQUE REFERENCES proposals(id) ON DELETE SET NULL,
  title         TEXT NOT NULL,
  description   TEXT NOT NULL,
  status        TEXT DEFAULT 'active',  -- active, completed, paused, abandoned
  started_at    DATETIME DEFAULT (datetime('now')),
  completed_at  DATETIME,
  notes         TEXT
);

CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_proposal ON projects(proposal_id);

-- ============================================================
-- SOZIALE INTELLIGENZ: Emotional context tracking
-- ============================================================

CREATE TABLE IF NOT EXISTS social_context (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  person       TEXT,                -- Person name (or 'self' for the user)
  mood         TEXT NOT NULL,       -- frustration, excitement, worry, celebration,
                                    -- stress, curiosity, boredom, gratitude
  intensity    REAL DEFAULT 0.5,    -- 0.0 = leicht, 1.0 = stark
  trigger_text TEXT,                -- Was hat die Emotion ausgelöst?
  topic_ref    TEXT,                -- Verbindung zu knowledge_entries Thema
  session_id   TEXT,
  detected_at  DATETIME DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_social_person ON social_context(person);
CREATE INDEX IF NOT EXISTS idx_social_mood ON social_context(mood);
CREATE INDEX IF NOT EXISTS idx_social_detected ON social_context(detected_at);

-- Geburtstage, Jahrestage, wiederkehrende Events
CREATE TABLE IF NOT EXISTS social_events (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  person       TEXT NOT NULL,
  event_type   TEXT NOT NULL,       -- birthday, anniversary, deadline, recurring
  description  TEXT,
  event_date   TEXT,                -- ISO date or "MM-DD" for recurring
  remind_days  INTEGER DEFAULT 3,   -- Tage vorher erinnern
  last_reminded DATETIME,
  source_ref   TEXT,
  created_at   DATETIME DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_events_date ON social_events(event_date);

-- Ungelöste Frustrationen: Wenn Problem > 14 Tage offen + Frustration erkannt
CREATE VIEW IF NOT EXISTS v_stale_frustrations AS
  SELECT sc.person, sc.trigger_text, sc.topic_ref, sc.detected_at,
         ke.title as problem_title, ke.status as problem_status,
         CAST(julianday('now') - julianday(sc.detected_at) AS INTEGER) as days_ago
  FROM social_context sc
  LEFT JOIN knowledge_entries ke ON ke.title = sc.topic_ref OR ke.id = CAST(sc.topic_ref AS INTEGER)
  WHERE sc.mood IN ('frustration', 'stress', 'worry')
  AND sc.detected_at > datetime('now', '-30 days')
  AND (ke.status IS NULL OR ke.status = 'active')
  ORDER BY sc.detected_at DESC;

-- Anstehende Events (nächste 7 Tage)
CREATE VIEW IF NOT EXISTS v_upcoming_events AS
  SELECT *,
    CASE
      WHEN event_date LIKE '____-__-__' THEN
        CAST(julianday(event_date) - julianday('now') AS INTEGER)
      WHEN event_date LIKE '__-__' THEN
        CAST(julianday(strftime('%Y', 'now') || '-' || event_date) - julianday('now') AS INTEGER)
      ELSE 999
    END as days_until
  FROM social_events
  WHERE days_until BETWEEN 0 AND 7
     OR (days_until < 0 AND days_until > -2);

-- ============================================================
-- META: System state and locks
-- ============================================================

CREATE TABLE IF NOT EXISTS system_state (
  key   TEXT PRIMARY KEY,
  value TEXT,
  updated_at DATETIME DEFAULT (datetime('now'))
);

-- Insert default state
INSERT OR IGNORE INTO system_state (key, value) VALUES ('schema_version', '1.0');
INSERT OR IGNORE INTO system_state (key, value) VALUES ('setup_complete', '0');
INSERT OR IGNORE INTO system_state (key, value) VALUES ('last_ingest', NULL);
INSERT OR IGNORE INTO system_state (key, value) VALUES ('last_consolidate', NULL);
INSERT OR IGNORE INTO system_state (key, value) VALUES ('last_archive', NULL);
INSERT OR IGNORE INTO system_state (key, value) VALUES ('last_initiative', NULL);
