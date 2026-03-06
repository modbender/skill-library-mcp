-- Run this in the Supabase SQL Editor to create all required tables

CREATE TABLE IF NOT EXISTS wallet_links (
  id BIGSERIAL PRIMARY KEY,
  x_handle TEXT UNIQUE NOT NULL,
  x_user_id TEXT UNIQUE NOT NULL,
  wallet_address TEXT NOT NULL,
  verified_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS token_events (
  id BIGSERIAL PRIMARY KEY,
  signature TEXT UNIQUE NOT NULL,
  event_type TEXT NOT NULL,
  wallet_address TEXT NOT NULL,
  amount DOUBLE PRECISION,
  sol_value DOUBLE PRECISION,
  timestamp TIMESTAMPTZ NOT NULL,
  metadata JSONB,
  processed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS processed_mentions (
  tweet_id TEXT PRIMARY KEY,
  feature TEXT NOT NULL,
  response_tweet_id TEXT,
  processed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS opinion_commits (
  id BIGSERIAL PRIMARY KEY,
  tweet_id TEXT NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  answer_hash TEXT NOT NULL,
  solana_signature TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rate_limits (
  key TEXT PRIMARY KEY,
  count INTEGER DEFAULT 0,
  window_start TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS price_snapshots (
  id BIGSERIAL PRIMARY KEY,
  price_usd DOUBLE PRECISION NOT NULL,
  volume_24h DOUBLE PRECISION,
  market_cap DOUBLE PRECISION,
  recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_token_events_processed ON token_events(processed);
CREATE INDEX IF NOT EXISTS idx_token_events_timestamp ON token_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_price_snapshots_recorded ON price_snapshots(recorded_at);

-- ============================================================
-- MEMORY SYSTEM: The Cortex
-- Episodic, Semantic, Procedural, and Self-Model memory
-- with hybrid vector + keyword retrieval
-- ============================================================

-- Enable trigram similarity for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable pgvector for semantic similarity search
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS memories (
  id BIGSERIAL PRIMARY KEY,
  memory_type TEXT NOT NULL CHECK (memory_type IN ('episodic', 'semantic', 'procedural', 'self_model')),
  content TEXT NOT NULL,
  summary TEXT NOT NULL,
  tags TEXT[] DEFAULT '{}',
  concepts TEXT[] DEFAULT '{}',           -- structured concept ontology labels
  emotional_valence REAL DEFAULT 0,       -- -1 (negative) to 1 (positive)
  importance REAL DEFAULT 0.5,            -- 0 to 1
  access_count INTEGER DEFAULT 0,
  source TEXT,                            -- trigger: mention, market, consolidation, reflection, emergence
  source_id TEXT,                         -- tweet ID, event ID, etc.
  related_user TEXT,                      -- X user ID if relevant
  related_wallet TEXT,                    -- wallet address if relevant
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_accessed TIMESTAMPTZ DEFAULT NOW(),
  decay_factor REAL DEFAULT 1.0,          -- type-specific decay (episodic=0.93, semantic=0.98, procedural=0.97, self_model=0.99)
  evidence_ids BIGINT[] DEFAULT '{}',    -- IDs of memories that support this one (Park et al. 2023)
  solana_signature TEXT,                  -- Solana tx signature if committed on-chain
  embedding vector(1024)                  -- vector embedding for semantic similarity search
);

-- Memory fragments: granular vector decomposition for precision retrieval
-- Each memory is split into semantic fragments (summary, content chunks, tag context)
-- so vector search matches against precise sub-memory content rather than the whole blob.
CREATE TABLE IF NOT EXISTS memory_fragments (
  id BIGSERIAL PRIMARY KEY,
  memory_id BIGINT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
  fragment_type TEXT NOT NULL,            -- 'summary', 'content_chunk', 'tag_context'
  content TEXT NOT NULL,
  embedding vector(1024),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Dream logs: consolidation, reflection, emergence sessions
CREATE TABLE IF NOT EXISTS dream_logs (
  id BIGSERIAL PRIMARY KEY,
  session_type TEXT NOT NULL CHECK (session_type IN ('consolidation', 'reflection', 'emergence')),
  input_memory_ids BIGINT[] DEFAULT '{}',
  output TEXT NOT NULL,
  new_memories_created BIGINT[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for memory retrieval
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_memories_concepts ON memories USING GIN(concepts);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance DESC);
CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(related_user);
CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memories_decay ON memories(decay_factor);
CREATE INDEX IF NOT EXISTS idx_memories_summary_trgm ON memories USING GIN(summary gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_memories_evidence ON memories USING GIN(evidence_ids);

-- Vector similarity indexes (HNSW for fast approximate nearest neighbor)
CREATE INDEX IF NOT EXISTS idx_memories_embedding ON memories USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_fragments_embedding ON memory_fragments USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_fragments_memory_id ON memory_fragments(memory_id);

CREATE INDEX IF NOT EXISTS idx_dream_logs_type ON dream_logs(session_type);
CREATE INDEX IF NOT EXISTS idx_dream_logs_created ON dream_logs(created_at DESC);

-- ============================================================
-- VECTOR SEARCH FUNCTIONS
-- Used by the hybrid retrieval system in memory.ts
-- ============================================================

-- Semantic search across memory-level embeddings with metadata filtering
CREATE OR REPLACE FUNCTION match_memories(
  query_embedding vector(1024),
  match_threshold float DEFAULT 0.3,
  match_count int DEFAULT 10,
  filter_types text[] DEFAULT NULL,
  filter_user text DEFAULT NULL,
  min_decay float DEFAULT 0.1
)
RETURNS TABLE (id bigint, similarity float)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT m.id, (1 - (m.embedding <=> query_embedding))::float AS similarity
  FROM memories m
  WHERE m.embedding IS NOT NULL
    AND m.decay_factor >= min_decay
    AND (filter_types IS NULL OR m.memory_type = ANY(filter_types))
    AND (filter_user IS NULL OR m.related_user = filter_user)
    AND (1 - (m.embedding <=> query_embedding)) > match_threshold
  ORDER BY m.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- ============================================================
-- MEMORY ASSOCIATION GRAPH
-- Bidirectional, typed, weighted links between memories.
-- Enables multi-hop retrieval, conflict detection, and
-- associative reasoning (A-Mem / MAGMA / SYNAPSE inspired).
-- ============================================================

CREATE TABLE IF NOT EXISTS memory_links (
  id BIGSERIAL PRIMARY KEY,
  source_id BIGINT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
  target_id BIGINT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
  link_type TEXT NOT NULL CHECK (link_type IN (
    'supports',     -- evidence-backed
    'contradicts',  -- conflicting information
    'elaborates',   -- adds detail to existing memory
    'causes',       -- causal chain
    'follows',      -- temporal sequence
    'relates'       -- general semantic association
  )),
  strength REAL DEFAULT 0.5,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(source_id, target_id, link_type)
);

CREATE INDEX IF NOT EXISTS idx_links_source ON memory_links(source_id);
CREATE INDEX IF NOT EXISTS idx_links_target ON memory_links(target_id);
CREATE INDEX IF NOT EXISTS idx_links_type ON memory_links(link_type);
CREATE INDEX IF NOT EXISTS idx_links_strength ON memory_links(strength DESC);

-- 1-hop traversal: get all memories linked to a set of IDs (both directions)
CREATE OR REPLACE FUNCTION get_linked_memories(
  seed_ids BIGINT[],
  min_strength FLOAT DEFAULT 0.1,
  max_results INT DEFAULT 20
)
RETURNS TABLE (
  memory_id BIGINT,
  linked_from BIGINT,
  link_type TEXT,
  strength FLOAT
)
LANGUAGE sql AS $$
  SELECT DISTINCT ON (ml.target_id, ml.link_type)
    ml.target_id AS memory_id,
    ml.source_id AS linked_from,
    ml.link_type,
    ml.strength::float
  FROM memory_links ml
  WHERE ml.source_id = ANY(seed_ids)
    AND ml.target_id != ALL(seed_ids)
    AND ml.strength >= min_strength
  UNION
  SELECT DISTINCT ON (ml.source_id, ml.link_type)
    ml.source_id AS memory_id,
    ml.target_id AS linked_from,
    ml.link_type,
    ml.strength::float
  FROM memory_links ml
  WHERE ml.target_id = ANY(seed_ids)
    AND ml.source_id != ALL(seed_ids)
    AND ml.strength >= min_strength
  ORDER BY strength DESC
  LIMIT max_results;
$$;

-- 2-hop traversal: from seeds, get connected memories up to depth 2
CREATE OR REPLACE FUNCTION get_memory_graph(
  seed_ids BIGINT[],
  min_strength FLOAT DEFAULT 0.2,
  max_results INT DEFAULT 30
)
RETURNS TABLE (
  memory_id BIGINT,
  hop INT,
  link_type TEXT,
  strength FLOAT
)
LANGUAGE plpgsql AS $$
DECLARE
  hop1_ids BIGINT[];
BEGIN
  RETURN QUERY
  SELECT g.memory_id, 1 AS hop, g.link_type, g.strength
  FROM get_linked_memories(seed_ids, min_strength, max_results) g;

  SELECT ARRAY_AGG(DISTINCT g.memory_id)
  INTO hop1_ids
  FROM get_linked_memories(seed_ids, min_strength, max_results) g;

  IF hop1_ids IS NOT NULL AND array_length(hop1_ids, 1) > 0 THEN
    RETURN QUERY
    SELECT g2.memory_id, 2 AS hop, g2.link_type, g2.strength * 0.5 AS strength
    FROM get_linked_memories(hop1_ids, min_strength, max_results / 2) g2
    WHERE g2.memory_id != ALL(seed_ids)
      AND g2.memory_id != ALL(hop1_ids);
  END IF;
END;
$$;

-- Hebbian reinforcement: boost link strength for co-retrieved memories
CREATE OR REPLACE FUNCTION boost_link_strength(
  memory_ids BIGINT[],
  boost_amount FLOAT DEFAULT 0.05
)
RETURNS INTEGER
LANGUAGE plpgsql AS $$
DECLARE affected INTEGER;
BEGIN
  UPDATE memory_links
  SET strength = LEAST(1.0, strength + boost_amount)
  WHERE source_id = ANY(memory_ids)
    AND target_id = ANY(memory_ids);
  GET DIAGNOSTICS affected = ROW_COUNT;
  RETURN affected;
END;
$$;

-- Fragment-level semantic search with deduplication to parent memory.
-- Returns the highest similarity fragment per memory, enabling precision
-- matching against individual facts/sentences rather than whole memories.
CREATE OR REPLACE FUNCTION match_memory_fragments(
  query_embedding vector(1024),
  match_threshold float DEFAULT 0.3,
  match_count int DEFAULT 10
)
RETURNS TABLE (memory_id bigint, max_similarity float)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT f.memory_id, MAX((1 - (f.embedding <=> query_embedding))::float) AS max_similarity
  FROM memory_fragments f
  WHERE f.embedding IS NOT NULL
    AND (1 - (f.embedding <=> query_embedding)) > match_threshold
  GROUP BY f.memory_id
  ORDER BY max_similarity DESC
  LIMIT match_count;
END;
$$;
