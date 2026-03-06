-- OpenClaw Memory System - Core Schema
-- Persistent memory storage with semantic search capabilities

-- Core memories table
CREATE TABLE IF NOT EXISTS memories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  memory_id TEXT UNIQUE NOT NULL,
  agent_wallet TEXT,
  session_id TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  memory_type TEXT NOT NULL, -- 'fact', 'conversation', 'preference', 'pattern'
  content TEXT NOT NULL,
  embedding_vector BLOB, -- Serialized Float32Array for semantic search
  importance_score REAL DEFAULT 0.5 CHECK (importance_score >= 0.0 AND importance_score <= 1.0),
  context_metadata TEXT, -- JSON: {tags: [], entities: [], keywords: []}
  accessed_count INTEGER DEFAULT 0,
  last_accessed DATETIME,
  expires_at DATETIME
);

-- Memory relationships (graph connections)
CREATE TABLE IF NOT EXISTS memory_relations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_memory_id TEXT NOT NULL,
  to_memory_id TEXT NOT NULL,
  relation_type TEXT NOT NULL, -- 'caused_by', 'related_to', 'contradicts', 'updates'
  strength REAL DEFAULT 1.0 CHECK (strength >= 0.0 AND strength <= 1.0),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (from_memory_id) REFERENCES memories(memory_id) ON DELETE CASCADE,
  FOREIGN KEY (to_memory_id) REFERENCES memories(memory_id) ON DELETE CASCADE
);

-- Access log for pruning decisions
CREATE TABLE IF NOT EXISTS memory_access_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  memory_id TEXT NOT NULL,
  accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  access_type TEXT NOT NULL, -- 'read', 'updated', 'created'
  context TEXT, -- Query or operation context
  FOREIGN KEY (memory_id) REFERENCES memories(memory_id) ON DELETE CASCADE
);

-- Agent memory quotas (licensing)
CREATE TABLE IF NOT EXISTS agent_memory_quotas (
  agent_wallet TEXT PRIMARY KEY,
  tier TEXT DEFAULT 'free' NOT NULL, -- 'free' or 'pro'
  memory_count INTEGER DEFAULT 0,
  memory_limit INTEGER DEFAULT 100, -- 100 for free, -1 for unlimited (pro)
  paid_until DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_memories_agent_wallet ON memories(agent_wallet);
CREATE INDEX IF NOT EXISTS idx_memories_session_id ON memories(session_id);
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance_score DESC);
CREATE INDEX IF NOT EXISTS idx_memories_expires ON memories(expires_at);
CREATE INDEX IF NOT EXISTS idx_memories_accessed_count ON memories(accessed_count);

CREATE INDEX IF NOT EXISTS idx_memory_relations_from ON memory_relations(from_memory_id);
CREATE INDEX IF NOT EXISTS idx_memory_relations_to ON memory_relations(to_memory_id);

CREATE INDEX IF NOT EXISTS idx_access_log_memory_id ON memory_access_log(memory_id);
CREATE INDEX IF NOT EXISTS idx_access_log_accessed_at ON memory_access_log(accessed_at);

CREATE INDEX IF NOT EXISTS idx_agent_quotas_tier ON agent_memory_quotas(tier);
CREATE INDEX IF NOT EXISTS idx_agent_quotas_paid_until ON agent_memory_quotas(paid_until);
