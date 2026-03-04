-- Ghost Catalog Database Schema
-- Version: 1.0.0
-- Database: data/ghost-catalog.db

CREATE TABLE IF NOT EXISTS file_catalog (
    file_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    path TEXT NOT NULL,
    project_id TEXT,
    category TEXT,
    version TEXT,
    created TEXT,
    modified TEXT,
    agent_id TEXT,
    execution TEXT,
    checksum TEXT,
    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS file_tags (
    file_id TEXT,
    tag TEXT,
    PRIMARY KEY (file_id, tag),
    FOREIGN KEY (file_id) REFERENCES file_catalog(file_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS agent_registry (
    id TEXT PRIMARY KEY,
    name TEXT,
    model TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP
);

CREATE TABLE IF NOT EXISTS file_dependencies (
    file_id TEXT,
    depends_on_file_id TEXT,
    dependency_type TEXT DEFAULT 'import',
    PRIMARY KEY (file_id, depends_on_file_id),
    FOREIGN KEY (file_id) REFERENCES file_catalog(file_id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_file_id) REFERENCES file_catalog(file_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_category ON file_catalog(category);
CREATE INDEX IF NOT EXISTS idx_project ON file_catalog(project_id);
CREATE INDEX IF NOT EXISTS idx_agent ON file_catalog(agent_id);
CREATE INDEX IF NOT EXISTS idx_modified ON file_catalog(modified);
CREATE INDEX IF NOT EXISTS idx_tags ON file_tags(tag);
