-- Tribe Protocol Schema v1
-- Trust lookup system for OpenClaw bots

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now'))
);
INSERT OR IGNORE INTO schema_version (version) VALUES (1);

-- Core identity
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('human','bot')),
    trust_tier INTEGER NOT NULL DEFAULT 1 CHECK(trust_tier BETWEEN 0 AND 4),
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','inactive','suspended','blocked')),
    owner_entity_id INTEGER REFERENCES entities(id),
    bio TEXT,
    relationship TEXT,
    introduced_by INTEGER REFERENCES entities(id),
    timezone TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Multi-platform identities
CREATE TABLE IF NOT EXISTS platform_ids (
    id INTEGER PRIMARY KEY,
    entity_id INTEGER NOT NULL REFERENCES entities(id),
    platform TEXT NOT NULL,
    platform_id TEXT NOT NULL,
    display_name TEXT,
    verified BOOLEAN DEFAULT 0,
    primary_contact BOOLEAN DEFAULT 0,
    added_at TEXT DEFAULT (datetime('now')),
    UNIQUE(platform, platform_id)
);

-- Bot-specific metadata
CREATE TABLE IF NOT EXISTS bot_metadata (
    entity_id INTEGER PRIMARY KEY REFERENCES entities(id),
    framework TEXT,
    model TEXT,
    host_machine TEXT,
    host_owner INTEGER REFERENCES entities(id),
    capabilities TEXT,
    skills TEXT,
    version TEXT,
    notes TEXT
);

-- Server membership and roles
CREATE TABLE IF NOT EXISTS server_roles (
    id INTEGER PRIMARY KEY,
    entity_id INTEGER NOT NULL REFERENCES entities(id),
    server_slug TEXT NOT NULL,
    server_id TEXT,
    role TEXT NOT NULL,
    joined_at TEXT DEFAULT (datetime('now')),
    UNIQUE(entity_id, server_slug)
);

-- Channel-level access
CREATE TABLE IF NOT EXISTS channel_access (
    id INTEGER PRIMARY KEY,
    entity_id INTEGER NOT NULL REFERENCES entities(id),
    server_slug TEXT NOT NULL,
    channel_id TEXT,
    channel_name TEXT,
    can_read BOOLEAN DEFAULT 1,
    can_write BOOLEAN DEFAULT 1,
    notes TEXT,
    UNIQUE(entity_id, server_slug, channel_id)
);

-- Data access rules by tier
CREATE TABLE IF NOT EXISTS data_access (
    id INTEGER PRIMARY KEY,
    min_tier INTEGER NOT NULL,
    resource_pattern TEXT NOT NULL,
    allowed BOOLEAN DEFAULT 0,
    description TEXT
);

-- Tags
CREATE TABLE IF NOT EXISTS entity_tags (
    entity_id INTEGER NOT NULL REFERENCES entities(id),
    tag TEXT NOT NULL,
    PRIMARY KEY(entity_id, tag)
);

-- Interaction tracking
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY,
    entity_id INTEGER NOT NULL REFERENCES entities(id),
    interaction_type TEXT NOT NULL,
    server_slug TEXT,
    channel_id TEXT,
    summary TEXT,
    quality INTEGER CHECK(quality BETWEEN 1 AND 5),
    created_at TEXT DEFAULT (datetime('now'))
);

-- Audit log
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY,
    entity_id INTEGER REFERENCES entities(id),
    action TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    reason TEXT,
    changed_by TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Summary view
CREATE VIEW IF NOT EXISTS v_entity_summary AS
SELECT
    e.id, e.name, e.type, e.trust_tier, e.status,
    e.relationship, e.bio,
    owner.name AS owner_name,
    introducer.name AS introduced_by_name,
    GROUP_CONCAT(DISTINCT p.platform || ':' || p.platform_id) AS platforms,
    GROUP_CONCAT(DISTINCT sr.server_slug || '/' || sr.role) AS server_roles,
    GROUP_CONCAT(DISTINCT et.tag) AS tags,
    bm.framework, bm.model, bm.host_machine, bm.capabilities,
    MAX(i.created_at) AS last_interaction,
    COUNT(DISTINCT i.id) AS interaction_count
FROM entities e
LEFT JOIN entities owner ON e.owner_entity_id = owner.id
LEFT JOIN entities introducer ON e.introduced_by = introducer.id
LEFT JOIN platform_ids p ON e.id = p.entity_id
LEFT JOIN server_roles sr ON e.id = sr.entity_id
LEFT JOIN entity_tags et ON e.id = et.entity_id
LEFT JOIN bot_metadata bm ON e.id = bm.entity_id
LEFT JOIN interactions i ON e.id = i.entity_id
GROUP BY e.id;
