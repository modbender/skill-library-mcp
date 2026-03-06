-- OpenClaw Context Optimizer - Core Schema
-- Tracks context compression, token savings, and optimization patterns

-- Context compression sessions
CREATE TABLE IF NOT EXISTS compression_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT UNIQUE NOT NULL,
  agent_wallet TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  original_tokens INTEGER NOT NULL,
  compressed_tokens INTEGER NOT NULL,
  compression_ratio REAL NOT NULL, -- compressed / original
  tokens_saved INTEGER NOT NULL,
  cost_saved_usd REAL DEFAULT 0.0,
  strategy_used TEXT NOT NULL, -- 'summary', 'dedup', 'prune', 'hybrid'
  quality_score REAL DEFAULT 1.0, -- 0.0-1.0, based on response quality
  original_context TEXT,
  compressed_context TEXT
);

-- Context compression patterns (learns what to keep/remove)
CREATE TABLE IF NOT EXISTS compression_patterns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pattern_id TEXT UNIQUE NOT NULL,
  agent_wallet TEXT,
  pattern_type TEXT NOT NULL, -- 'redundant', 'low_value', 'high_value', 'template'
  pattern_text TEXT NOT NULL,
  frequency INTEGER DEFAULT 1,
  token_impact INTEGER DEFAULT 0, -- Average tokens saved/used
  importance_score REAL DEFAULT 0.5, -- 0.0-1.0
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Token usage statistics
CREATE TABLE IF NOT EXISTS token_stats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_wallet TEXT NOT NULL,
  date DATE NOT NULL,
  original_tokens INTEGER DEFAULT 0,
  compressed_tokens INTEGER DEFAULT 0,
  tokens_saved INTEGER DEFAULT 0,
  cost_saved_usd REAL DEFAULT 0.0,
  compression_count INTEGER DEFAULT 0,
  average_ratio REAL DEFAULT 1.0,
  UNIQUE(agent_wallet, date)
);

-- Agent optimizer quotas (licensing)
CREATE TABLE IF NOT EXISTS agent_optimizer_quotas (
  agent_wallet TEXT PRIMARY KEY,
  tier TEXT DEFAULT 'free' NOT NULL, -- 'free' or 'pro'
  compression_limit INTEGER DEFAULT 100, -- 100 compressions/day for free, -1 for unlimited
  compressions_today INTEGER DEFAULT 0,
  last_reset_date DATE,
  paid_until DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Compression quality feedback (learns from results)
CREATE TABLE IF NOT EXISTS compression_feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  feedback_type TEXT NOT NULL, -- 'success', 'hallucination', 'missing_info', 'good'
  feedback_score REAL DEFAULT 0.5, -- 0.0-1.0
  notes TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES compression_sessions(session_id) ON DELETE CASCADE
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_compression_sessions_timestamp ON compression_sessions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_compression_sessions_agent ON compression_sessions(agent_wallet);
CREATE INDEX IF NOT EXISTS idx_compression_sessions_session ON compression_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_compression_sessions_ratio ON compression_sessions(compression_ratio);

CREATE INDEX IF NOT EXISTS idx_patterns_agent ON compression_patterns(agent_wallet);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON compression_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_importance ON compression_patterns(importance_score DESC);

CREATE INDEX IF NOT EXISTS idx_token_stats_agent ON token_stats(agent_wallet);
CREATE INDEX IF NOT EXISTS idx_token_stats_date ON token_stats(date DESC);

CREATE INDEX IF NOT EXISTS idx_quotas_tier ON agent_optimizer_quotas(tier);
CREATE INDEX IF NOT EXISTS idx_quotas_paid_until ON agent_optimizer_quotas(paid_until);

CREATE INDEX IF NOT EXISTS idx_feedback_session ON compression_feedback(session_id);
CREATE INDEX IF NOT EXISTS idx_feedback_type ON compression_feedback(feedback_type);
