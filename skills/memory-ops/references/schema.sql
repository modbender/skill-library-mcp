-- Memory Ops schema
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS memories (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL DEFAULT 'ian',
  scope TEXT NOT NULL DEFAULT 'global',
  source TEXT NOT NULL DEFAULT 'chat',
  content TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  embedding vector(1536),
  importance SMALLINT NOT NULL DEFAULT 3,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_accessed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_memories_user_scope ON memories(user_id, scope);
CREATE INDEX IF NOT EXISTS idx_memories_metadata_gin ON memories USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_memories_embedding_cosine
ON memories USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS memory_audit (
  id BIGSERIAL PRIMARY KEY,
  event_type TEXT NOT NULL,
  agent TEXT NOT NULL DEFAULT 'jarvis',
  read_ok BOOLEAN NOT NULL DEFAULT false,
  write_ok BOOLEAN NOT NULL DEFAULT false,
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_memory_audit_created_at ON memory_audit(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_audit_event_type ON memory_audit(event_type);
