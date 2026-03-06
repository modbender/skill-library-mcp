-- OpenClaw Security Blacklist System (OSBS) Database Schema
-- Version: 1.0.0

-- Main threat entries table
CREATE TABLE IF NOT EXISTS threats (
    id TEXT PRIMARY KEY,                    -- OSA-YYYY-XXXXX format
    version INTEGER DEFAULT 1,
    created TEXT NOT NULL,                  -- ISO 8601
    updated TEXT NOT NULL,                  -- ISO 8601
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'deprecated', 'under_review', 'false_positive')),
    
    -- Classification
    tier INTEGER NOT NULL CHECK(tier BETWEEN 1 AND 6),
    category TEXT NOT NULL,                 -- e.g., T1.1
    subcategory TEXT,                       -- e.g., T1.1.1
    tags TEXT,                              -- JSON array
    
    -- Threat details
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    teaching_prompt TEXT,
    
    -- Risk assessment
    severity TEXT NOT NULL CHECK(severity IN ('critical', 'high', 'medium', 'low', 'info')),
    confidence REAL DEFAULT 0.5 CHECK(confidence BETWEEN 0 AND 1),
    false_positive_rate REAL DEFAULT 0.1 CHECK(false_positive_rate BETWEEN 0 AND 1),
    
    -- Response configuration (JSON)
    response TEXT NOT NULL,
    
    -- Provenance (JSON)
    source TEXT,
    refs TEXT,                              -- JSON array (renamed from 'references' - reserved word)
    related TEXT,                           -- JSON array of related OSA IDs
    
    -- Metadata
    mitre_attack TEXT,                      -- JSON array
    cve TEXT,                               -- JSON array
    campaign TEXT
);

-- Indicators table (fast lookup)
CREATE TABLE IF NOT EXISTS indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    threat_id TEXT NOT NULL REFERENCES threats(id) ON DELETE CASCADE,
    type TEXT NOT NULL,                     -- domain, url, ip, skill_name, etc.
    value TEXT NOT NULL,                    -- The actual indicator value
    value_lower TEXT NOT NULL,              -- Lowercase for case-insensitive matching
    match_type TEXT DEFAULT 'exact' CHECK(match_type IN ('exact', 'prefix', 'suffix', 'contains', 'regex', 'semantic', 'hash')),
    weight REAL DEFAULT 1.0 CHECK(weight BETWEEN 0 AND 1),
    context TEXT,                           -- url, skill_name, command, message, file
    negation INTEGER DEFAULT 0,             -- If 1, presence REDUCES threat score
    metadata TEXT                           -- JSON for type-specific data
);

-- Exact match index (domains, IPs, hashes) - for O(1) lookup
CREATE TABLE IF NOT EXISTS exact_index (
    value_lower TEXT PRIMARY KEY,
    indicator_id INTEGER NOT NULL REFERENCES indicators(id) ON DELETE CASCADE,
    threat_id TEXT NOT NULL REFERENCES threats(id) ON DELETE CASCADE,
    type TEXT NOT NULL
);

-- Pattern match cache (compiled regex patterns)
CREATE TABLE IF NOT EXISTS pattern_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_id INTEGER NOT NULL REFERENCES indicators(id) ON DELETE CASCADE,
    threat_id TEXT NOT NULL REFERENCES threats(id) ON DELETE CASCADE,
    pattern TEXT NOT NULL,
    context TEXT
);

-- Sync metadata
CREATE TABLE IF NOT EXISTS sync_meta (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated TEXT
);

-- Check log (optional, for analysis)
CREATE TABLE IF NOT EXISTS check_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    check_type TEXT NOT NULL,
    input_hash TEXT,                        -- SHA256 of input (privacy)
    result TEXT NOT NULL,                   -- block, warn, educate, safe
    threat_ids TEXT,                        -- JSON array of matched threats
    confidence REAL,
    duration_ms REAL
);

-- User reports (pending submission)
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TEXT NOT NULL,
    type TEXT NOT NULL,
    value TEXT NOT NULL,
    reason TEXT,
    submitted INTEGER DEFAULT 0,
    submitted_at TEXT
);

-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_threats_tier ON threats(tier);
CREATE INDEX IF NOT EXISTS idx_threats_status ON threats(status);
CREATE INDEX IF NOT EXISTS idx_threats_severity ON threats(severity);
CREATE INDEX IF NOT EXISTS idx_threats_campaign ON threats(campaign);

CREATE INDEX IF NOT EXISTS idx_indicators_threat ON indicators(threat_id);
CREATE INDEX IF NOT EXISTS idx_indicators_type ON indicators(type);
CREATE INDEX IF NOT EXISTS idx_indicators_value ON indicators(value_lower);
CREATE INDEX IF NOT EXISTS idx_indicators_context ON indicators(context);

CREATE INDEX IF NOT EXISTS idx_exact_type ON exact_index(type);

CREATE INDEX IF NOT EXISTS idx_pattern_context ON pattern_index(context);

-- Full-text search for threat names and descriptions
CREATE VIRTUAL TABLE IF NOT EXISTS threats_fts USING fts5(
    id,
    name,
    description,
    teaching_prompt,
    tags,
    content='threats',
    content_rowid='rowid'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS threats_ai AFTER INSERT ON threats BEGIN
    INSERT INTO threats_fts(id, name, description, teaching_prompt, tags)
    VALUES (new.id, new.name, new.description, new.teaching_prompt, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS threats_ad AFTER DELETE ON threats BEGIN
    INSERT INTO threats_fts(threats_fts, id, name, description, teaching_prompt, tags)
    VALUES ('delete', old.id, old.name, old.description, old.teaching_prompt, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS threats_au AFTER UPDATE ON threats BEGIN
    INSERT INTO threats_fts(threats_fts, id, name, description, teaching_prompt, tags)
    VALUES ('delete', old.id, old.name, old.description, old.teaching_prompt, old.tags);
    INSERT INTO threats_fts(id, name, description, teaching_prompt, tags)
    VALUES (new.id, new.name, new.description, new.teaching_prompt, new.tags);
END;
