-- Mema Brain Schema

-- Documents (Long-term Memory)
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT UNIQUE NOT NULL,
    path TEXT NOT NULL,
    title TEXT,
    tag TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_tag ON documents(tag);
CREATE INDEX IF NOT EXISTS idx_updated ON documents(updated_at);
CREATE INDEX IF NOT EXISTS idx_document_id ON documents(document_id);

-- Skills Tracking
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id TEXT UNIQUE NOT NULL,
    skill_name TEXT NOT NULL,
    tag TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    error_count INTEGER DEFAULT 0,
    last_error_at DATETIME,
    success_count INTEGER DEFAULT 0,
    last_success_at DATETIME,
    last_use_at DATETIME,
    usage_count INTEGER DEFAULT 0
);
