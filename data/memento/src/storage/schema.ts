export const SCHEMA_VERSION = 7;

// ---------------------------------------------------------------------------
// Table definitions — Phase 1
// ---------------------------------------------------------------------------

export const CREATE_SCHEMA_META_TABLE = `
CREATE TABLE IF NOT EXISTS schema_meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
`;

/** Raw conversation segments (one row per flushed buffer) */
export const CREATE_CONVERSATIONS_TABLE = `
CREATE TABLE IF NOT EXISTS conversations (
  id          TEXT    PRIMARY KEY,
  agent_id    TEXT    NOT NULL,
  session_key TEXT    NOT NULL,
  channel     TEXT,
  started_at  INTEGER NOT NULL,
  ended_at    INTEGER NOT NULL,
  turn_count  INTEGER NOT NULL,
  raw_text    TEXT    NOT NULL,
  metadata    TEXT
);
`;

/** Individual messages within a conversation segment */
export const CREATE_MESSAGES_TABLE = `
CREATE TABLE IF NOT EXISTS messages (
  id              TEXT    PRIMARY KEY,
  conversation_id TEXT    NOT NULL REFERENCES conversations(id),
  role            TEXT    NOT NULL,
  content         TEXT    NOT NULL,
  timestamp       INTEGER NOT NULL,
  message_id      TEXT,
  metadata        TEXT
);
`;

export const CREATE_CONVERSATIONS_IDX = `
CREATE INDEX IF NOT EXISTS idx_conversations_session_key
  ON conversations(session_key);
`;

export const CREATE_MESSAGES_IDX = `
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
  ON messages(conversation_id);
`;

// ---------------------------------------------------------------------------
// Table definitions — Phase 2: Knowledge Base
// ---------------------------------------------------------------------------

/** Extracted facts — the structured knowledge base */
export const CREATE_FACTS_TABLE = `
CREATE TABLE IF NOT EXISTS facts (
  id              TEXT    PRIMARY KEY,
  agent_id        TEXT    NOT NULL,
  category        TEXT    NOT NULL,
  content         TEXT    NOT NULL,
  summary         TEXT,
  visibility      TEXT    NOT NULL DEFAULT 'shared',
  confidence      REAL    DEFAULT 1.0,
  first_seen_at   INTEGER NOT NULL,
  last_seen_at    INTEGER NOT NULL,
  occurrence_count INTEGER DEFAULT 0,
  supersedes      TEXT,
  is_active       INTEGER DEFAULT 1,
  metadata        TEXT,
  previous_value  TEXT
);
`;

/** Fact occurrences — temporal tracking for each mention */
export const CREATE_FACT_OCCURRENCES_TABLE = `
CREATE TABLE IF NOT EXISTS fact_occurrences (
  id              TEXT    PRIMARY KEY,
  fact_id         TEXT    NOT NULL REFERENCES facts(id),
  conversation_id TEXT    NOT NULL REFERENCES conversations(id),
  timestamp       INTEGER NOT NULL,
  context_snippet TEXT,
  sentiment       TEXT
);
`;

/** Extraction log — tracks which conversations have been processed */
export const CREATE_EXTRACTION_LOG_TABLE = `
CREATE TABLE IF NOT EXISTS extraction_log (
  conversation_id   TEXT    PRIMARY KEY REFERENCES conversations(id),
  extracted_at      INTEGER NOT NULL,
  model_used        TEXT    NOT NULL,
  facts_extracted   INTEGER DEFAULT 0,
  facts_updated     INTEGER DEFAULT 0,
  facts_deduplicated INTEGER DEFAULT 0,
  error             TEXT
);
`;

// Phase 2 indexes
export const CREATE_FACTS_AGENT_IDX = `
CREATE INDEX IF NOT EXISTS idx_facts_agent_id ON facts(agent_id);
`;
export const CREATE_FACTS_CATEGORY_IDX = `
CREATE INDEX IF NOT EXISTS idx_facts_category ON facts(category);
`;
export const CREATE_FACTS_VISIBILITY_IDX = `
CREATE INDEX IF NOT EXISTS idx_facts_visibility ON facts(visibility);
`;
export const CREATE_FACTS_ACTIVE_IDX = `
CREATE INDEX IF NOT EXISTS idx_facts_is_active ON facts(is_active);
`;
export const CREATE_FACT_OCCURRENCES_FACT_IDX = `
CREATE INDEX IF NOT EXISTS idx_fact_occurrences_fact_id ON fact_occurrences(fact_id);
`;

// FTS5 virtual table for full-text search over fact content + summary.
// Uses external content table (content=facts) so the text is NOT duplicated —
// the FTS index only stores the inverted index. Triggers below keep it in sync.
export const CREATE_FACTS_FTS_TABLE = `
CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
  content,
  summary,
  content=facts,
  content_rowid=rowid
);
`;

// Keep facts_fts in sync with the facts table
export const CREATE_FACTS_FTS_INSERT_TRIGGER = `
CREATE TRIGGER IF NOT EXISTS facts_fts_ai AFTER INSERT ON facts BEGIN
  INSERT INTO facts_fts(rowid, content, summary)
    VALUES (new.rowid, new.content, COALESCE(new.summary, ''));
END;
`;

export const CREATE_FACTS_FTS_DELETE_TRIGGER = `
CREATE TRIGGER IF NOT EXISTS facts_fts_ad AFTER DELETE ON facts BEGIN
  INSERT INTO facts_fts(facts_fts, rowid, content, summary)
    VALUES ('delete', old.rowid, old.content, COALESCE(old.summary, ''));
END;
`;

export const CREATE_FACTS_FTS_UPDATE_TRIGGER = `
CREATE TRIGGER IF NOT EXISTS facts_fts_au AFTER UPDATE ON facts BEGIN
  INSERT INTO facts_fts(facts_fts, rowid, content, summary)
    VALUES ('delete', old.rowid, old.content, COALESCE(old.summary, ''));
  INSERT INTO facts_fts(rowid, content, summary)
    VALUES (new.rowid, new.content, COALESCE(new.summary, ''));
END;
`;

// ---------------------------------------------------------------------------
// Table definitions — Phase 2b: Knowledge Graph (fact relations)
// ---------------------------------------------------------------------------

/** Typed, weighted edges between facts — the knowledge graph */
export const CREATE_FACT_RELATIONS_TABLE = `
CREATE TABLE IF NOT EXISTS fact_relations (
  id            TEXT    PRIMARY KEY,
  source_id     TEXT    NOT NULL REFERENCES facts(id),
  target_id     TEXT    NOT NULL REFERENCES facts(id),
  relation_type TEXT    NOT NULL,
  strength      REAL    DEFAULT 1.0,
  causal_weight REAL    DEFAULT 1.0,
  created_at    INTEGER NOT NULL,
  created_by    TEXT,
  metadata      TEXT
);
`;

export const CREATE_FACT_RELATIONS_SOURCE_IDX = `
CREATE INDEX IF NOT EXISTS idx_fact_relations_source ON fact_relations(source_id);
`;

export const CREATE_FACT_RELATIONS_TARGET_IDX = `
CREATE INDEX IF NOT EXISTS idx_fact_relations_target ON fact_relations(target_id);
`;

export const CREATE_FACT_RELATIONS_TYPE_IDX = `
CREATE INDEX IF NOT EXISTS idx_fact_relations_type ON fact_relations(relation_type);
`;

// ---------------------------------------------------------------------------
// Table definitions — Phase 2c: Multi-Layer Memory (fact clusters)
// ---------------------------------------------------------------------------

/**
 * Cluster nodes — higher-level abstractions that consolidate groups of facts
 * (or other clusters). Each cluster lives at a specific abstraction `layer`:
 *   - Layer 2: groups of individual facts (e.g., "Ben is a serious cyclist")
 *   - Layer 3+: groups of clusters (e.g., "Ben's health & fitness profile")
 *
 * Clusters participate in the same graph as facts via fact_relations,
 * but are stored separately because they carry different metadata
 * (member list, layer depth, consolidation provenance).
 */
export const CREATE_FACT_CLUSTERS_TABLE = `
CREATE TABLE IF NOT EXISTS fact_clusters (
  id            TEXT    PRIMARY KEY,
  agent_id      TEXT    NOT NULL,
  summary       TEXT    NOT NULL,
  description   TEXT,
  layer         INTEGER NOT NULL DEFAULT 2,
  visibility    TEXT    NOT NULL DEFAULT 'shared',
  confidence    REAL    DEFAULT 1.0,
  created_at    INTEGER NOT NULL,
  updated_at    INTEGER NOT NULL,
  is_active     INTEGER DEFAULT 1,
  metadata      TEXT
);
`;

export const CREATE_FACT_CLUSTERS_AGENT_IDX = `
CREATE INDEX IF NOT EXISTS idx_fact_clusters_agent ON fact_clusters(agent_id);
`;

export const CREATE_FACT_CLUSTERS_LAYER_IDX = `
CREATE INDEX IF NOT EXISTS idx_fact_clusters_layer ON fact_clusters(layer);
`;

export const CREATE_FACT_CLUSTERS_ACTIVE_IDX = `
CREATE INDEX IF NOT EXISTS idx_fact_clusters_is_active ON fact_clusters(is_active);
`;

/**
 * Membership edges linking facts → clusters and clusters → parent clusters.
 * `member_type` distinguishes between the two: "fact" or "cluster".
 *
 * A single fact can belong to multiple clusters (soft clustering).
 * A cluster can belong to higher-layer clusters (hierarchical).
 */
export const CREATE_CLUSTER_MEMBERS_TABLE = `
CREATE TABLE IF NOT EXISTS cluster_members (
  cluster_id    TEXT    NOT NULL REFERENCES fact_clusters(id),
  member_id     TEXT    NOT NULL,
  member_type   TEXT    NOT NULL,
  added_at      INTEGER NOT NULL,
  PRIMARY KEY (cluster_id, member_id)
);
`;

export const CREATE_CLUSTER_MEMBERS_CLUSTER_IDX = `
CREATE INDEX IF NOT EXISTS idx_cluster_members_cluster ON cluster_members(cluster_id);
`;

export const CREATE_CLUSTER_MEMBERS_MEMBER_IDX = `
CREATE INDEX IF NOT EXISTS idx_cluster_members_member ON cluster_members(member_id);
`;

// ---------------------------------------------------------------------------
// Schema migration v2 → v3: Add embedding column to facts
// ---------------------------------------------------------------------------

/**
 * Add embedding BLOB column to facts table.
 * Stores Float32Array as raw bytes for compact storage.
 * ALTER TABLE IF NOT EXISTS not supported in SQLite — handled in migration code.
 */
export const MIGRATE_V2_TO_V3 = `
ALTER TABLE facts ADD COLUMN embedding BLOB;
`;

export const CREATE_FACTS_EMBEDDING_IDX = `
CREATE INDEX IF NOT EXISTS idx_facts_has_embedding
  ON facts(agent_id, is_active) WHERE embedding IS NOT NULL;
`;

// ---------------------------------------------------------------------------
// Schema migration v3 → v4: Add fact_relations table
// ---------------------------------------------------------------------------

/**
 * v3 → v4: Create fact_relations table for knowledge graph edges.
 * Uses CREATE IF NOT EXISTS so it's safe to re-run.
 */
export const MIGRATE_V3_TO_V4 = [
  CREATE_FACT_RELATIONS_TABLE,
  CREATE_FACT_RELATIONS_SOURCE_IDX,
  CREATE_FACT_RELATIONS_TARGET_IDX,
  CREATE_FACT_RELATIONS_TYPE_IDX,
];

// ---------------------------------------------------------------------------
// Schema migration v4 → v5: Add fact_clusters + cluster_members tables
// ---------------------------------------------------------------------------

export const MIGRATE_V4_TO_V5 = [
  CREATE_FACT_CLUSTERS_TABLE,
  CREATE_FACT_CLUSTERS_AGENT_IDX,
  CREATE_FACT_CLUSTERS_LAYER_IDX,
  CREATE_FACT_CLUSTERS_ACTIVE_IDX,
  CREATE_CLUSTER_MEMBERS_TABLE,
  CREATE_CLUSTER_MEMBERS_CLUSTER_IDX,
  CREATE_CLUSTER_MEMBERS_MEMBER_IDX,
];

// ---------------------------------------------------------------------------
// Table definitions — Phase 3: Remote Ingest
// ---------------------------------------------------------------------------

/** Authentication tokens for remote JSONL ingest */
export const CREATE_INGEST_TOKENS_TABLE = `
CREATE TABLE IF NOT EXISTS ingest_tokens (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  token_hash  TEXT NOT NULL UNIQUE,
  created_at  INTEGER NOT NULL,
  last_used_at INTEGER,
  is_active   INTEGER DEFAULT 1
);
`;

/** Dedup log — tracks ingested files by content hash */
export const CREATE_INGEST_FILE_LOG_TABLE = `
CREATE TABLE IF NOT EXISTS ingest_file_log (
  id           TEXT PRIMARY KEY,
  source       TEXT NOT NULL,
  file_path    TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  ingested_at  INTEGER NOT NULL
);
`;

export const CREATE_INGEST_FILE_LOG_HASH_IDX = `
CREATE UNIQUE INDEX IF NOT EXISTS idx_ingest_file_log_hash ON ingest_file_log(content_hash);
`;

// ---------------------------------------------------------------------------
// Schema migration v5 → v6: Add ingest_tokens + ingest_file_log tables
// ---------------------------------------------------------------------------

export const MIGRATE_V5_TO_V6 = [
  CREATE_INGEST_TOKENS_TABLE,
  CREATE_INGEST_FILE_LOG_TABLE,
  CREATE_INGEST_FILE_LOG_HASH_IDX,
];

// ---------------------------------------------------------------------------
// Schema migration v6 → v7: Add causal_weight to fact_relations, previous_value to facts
// ---------------------------------------------------------------------------

export const MIGRATE_V6_ADD_CAUSAL_WEIGHT = `
ALTER TABLE fact_relations ADD COLUMN causal_weight REAL DEFAULT 1.0;
`;

export const MIGRATE_V6_ADD_PREVIOUS_VALUE = `
ALTER TABLE facts ADD COLUMN previous_value TEXT;
`;

export const MIGRATE_V6_TO_V7 = [
  MIGRATE_V6_ADD_CAUSAL_WEIGHT,
  MIGRATE_V6_ADD_PREVIOUS_VALUE,
];

// ---------------------------------------------------------------------------
// All DDL statements to run on first boot (idempotent)
// ---------------------------------------------------------------------------

/** All DDL statements to run on first boot (idempotent) */
export const ALL_DDL = [
  // Phase 1
  CREATE_SCHEMA_META_TABLE,
  CREATE_CONVERSATIONS_TABLE,
  CREATE_MESSAGES_TABLE,
  CREATE_CONVERSATIONS_IDX,
  CREATE_MESSAGES_IDX,
  // Phase 2
  CREATE_FACTS_TABLE,
  CREATE_FACT_OCCURRENCES_TABLE,
  CREATE_EXTRACTION_LOG_TABLE,
  CREATE_FACTS_AGENT_IDX,
  CREATE_FACTS_CATEGORY_IDX,
  CREATE_FACTS_VISIBILITY_IDX,
  CREATE_FACTS_ACTIVE_IDX,
  CREATE_FACT_OCCURRENCES_FACT_IDX,
  CREATE_FACTS_FTS_TABLE,
  CREATE_FACTS_FTS_INSERT_TRIGGER,
  CREATE_FACTS_FTS_DELETE_TRIGGER,
  CREATE_FACTS_FTS_UPDATE_TRIGGER,
  // Phase 2b: Knowledge Graph
  CREATE_FACT_RELATIONS_TABLE,
  CREATE_FACT_RELATIONS_SOURCE_IDX,
  CREATE_FACT_RELATIONS_TARGET_IDX,
  CREATE_FACT_RELATIONS_TYPE_IDX,
  // Phase 2c: Multi-Layer Memory (clusters)
  CREATE_FACT_CLUSTERS_TABLE,
  CREATE_FACT_CLUSTERS_AGENT_IDX,
  CREATE_FACT_CLUSTERS_LAYER_IDX,
  CREATE_FACT_CLUSTERS_ACTIVE_IDX,
  CREATE_CLUSTER_MEMBERS_TABLE,
  CREATE_CLUSTER_MEMBERS_CLUSTER_IDX,
  CREATE_CLUSTER_MEMBERS_MEMBER_IDX,
  // Phase 3: Remote Ingest
  CREATE_INGEST_TOKENS_TABLE,
  CREATE_INGEST_FILE_LOG_TABLE,
  CREATE_INGEST_FILE_LOG_HASH_IDX,
];

// ---------------------------------------------------------------------------
// Row types — Phase 1
// ---------------------------------------------------------------------------

export type ConversationRow = {
  id: string;
  agent_id: string;
  session_key: string;
  channel: string | null;
  started_at: number;
  ended_at: number;
  turn_count: number;
  raw_text: string;
  metadata: string | null;
};

export type MessageRow = {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  timestamp: number;
  message_id: string | null;
  metadata: string | null;
};

// ---------------------------------------------------------------------------
// Row types — Phase 2
// ---------------------------------------------------------------------------

export type FactRow = {
  id: string;
  agent_id: string;
  category: string;
  content: string;
  summary: string | null;
  visibility: string;
  confidence: number;
  first_seen_at: number;
  last_seen_at: number;
  occurrence_count: number;
  supersedes: string | null;
  is_active: number; // 1 = active, 0 = superseded
  metadata: string | null;
  embedding: Buffer | null; // Float32Array stored as raw bytes
  /** Previous content value when this fact superseded an older one */
  previous_value: string | null;
};

export type FactOccurrenceRow = {
  id: string;
  fact_id: string;
  conversation_id: string;
  timestamp: number;
  context_snippet: string | null;
  sentiment: string | null;
};

export type FactRelationRow = {
  id: string;
  source_id: string;
  target_id: string;
  /** 'related_to' | 'elaborates' | 'contradicts' | 'supports' | 'caused_by' | 'part_of' | 'precondition_of' */
  relation_type: string;
  /** 0.0–1.0 edge weight */
  strength: number;
  /** Causal weight for boosting graph traversal on causal edges (DEFAULT 1.0) */
  causal_weight: number;
  created_at: number;
  /** 'extraction' | 'consolidation' | 'user_feedback' | null */
  created_by: string | null;
  metadata: string | null;
};

export type FactClusterRow = {
  id: string;
  agent_id: string;
  /** Human-readable one-line summary of what this cluster represents */
  summary: string;
  /** Longer description of the cluster's semantic scope */
  description: string | null;
  /** Abstraction level: 2 = group of facts, 3+ = group of clusters */
  layer: number;
  /** Inherited from most restrictive member visibility */
  visibility: string;
  confidence: number;
  created_at: number;
  updated_at: number;
  is_active: number;
  metadata: string | null;
};

export type ClusterMemberRow = {
  cluster_id: string;
  member_id: string;
  /** 'fact' or 'cluster' */
  member_type: string;
  added_at: number;
};

export type ExtractionLogRow = {
  conversation_id: string;
  extracted_at: number;
  model_used: string;
  facts_extracted: number;
  facts_updated: number;
  facts_deduplicated: number;
  error: string | null;
};

// ---------------------------------------------------------------------------
// Row types — Phase 3: Remote Ingest
// ---------------------------------------------------------------------------

export type IngestTokenRow = {
  id: string;
  name: string;
  token_hash: string;
  created_at: number;
  last_used_at: number | null;
  is_active: number;
};

export type IngestFileLogRow = {
  id: string;
  source: string;
  file_path: string;
  content_hash: string;
  ingested_at: number;
};
