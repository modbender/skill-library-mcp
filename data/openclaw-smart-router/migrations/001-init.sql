-- OpenClaw Smart Router - Core Schema
-- Tracks model routing decisions, learned patterns, and performance metrics

-- Routing decisions (track model selection)
CREATE TABLE IF NOT EXISTS routing_decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  decision_id TEXT UNIQUE NOT NULL,
  agent_wallet TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

  -- Task characteristics
  task_complexity REAL, -- 0.0-1.0 score
  context_length INTEGER, -- Tokens
  task_type TEXT, -- 'code', 'query', 'reasoning', 'writing', 'debugging'
  has_code BOOLEAN DEFAULT 0,
  has_errors BOOLEAN DEFAULT 0,
  has_data BOOLEAN DEFAULT 0,

  -- Model selection
  selected_model TEXT NOT NULL, -- 'claude-opus-4-5', 'claude-haiku-4-5', etc.
  selected_provider TEXT NOT NULL, -- 'anthropic', 'openai', 'google'
  selection_reason TEXT, -- 'budget_constrained', 'complexity_high', 'pattern_match'
  confidence_score REAL, -- 0.0-1.0

  -- Alternative models considered
  alternatives_json TEXT, -- JSON array of {model, score, reason}

  -- Outcome tracking
  was_successful BOOLEAN,
  actual_tokens INTEGER,
  actual_cost_usd REAL,
  response_quality REAL, -- 0.0-1.0
  response_time_ms INTEGER,

  -- Learning
  pattern_id TEXT -- Link to learned pattern if applicable
);

-- Learned routing patterns
CREATE TABLE IF NOT EXISTS routing_patterns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pattern_id TEXT UNIQUE NOT NULL,
  agent_wallet TEXT,

  -- Pattern definition
  pattern_type TEXT NOT NULL, -- 'task_based', 'complexity_based', 'budget_based'
  pattern_description TEXT,

  -- Matching criteria
  task_type TEXT,
  complexity_min REAL,
  complexity_max REAL,
  context_length_min INTEGER,
  context_length_max INTEGER,
  keywords_json TEXT, -- JSON array of keywords

  -- Recommended model
  recommended_model TEXT NOT NULL,
  recommended_provider TEXT NOT NULL,

  -- Pattern performance
  success_count INTEGER DEFAULT 0,
  failure_count INTEGER DEFAULT 0,
  avg_cost_saved REAL DEFAULT 0.0,
  avg_quality REAL DEFAULT 0.0,
  confidence REAL DEFAULT 0.5, -- Pattern reliability

  -- Metadata
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_used DATETIME,
  last_updated DATETIME
);

-- Model performance stats (aggregated)
CREATE TABLE IF NOT EXISTS model_performance (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_wallet TEXT,
  model TEXT NOT NULL,
  provider TEXT NOT NULL,
  task_type TEXT,

  -- Aggregated metrics
  total_requests INTEGER DEFAULT 0,
  successful_requests INTEGER DEFAULT 0,
  avg_response_time_ms INTEGER,
  avg_quality_score REAL,
  avg_cost_per_request REAL,
  total_cost_usd REAL,

  -- Last update
  last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,

  UNIQUE(agent_wallet, model, provider, task_type)
);

-- Agent router quotas (licensing)
CREATE TABLE IF NOT EXISTS agent_router_quotas (
  agent_wallet TEXT PRIMARY KEY,
  tier TEXT DEFAULT 'free' NOT NULL, -- 'free' or 'pro'
  decisions_limit INTEGER DEFAULT 100, -- 100/day for free, -1 for unlimited
  decisions_today INTEGER DEFAULT 0,
  last_reset_date DATE,
  paid_until DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_routing_decisions_agent ON routing_decisions(agent_wallet);
CREATE INDEX IF NOT EXISTS idx_routing_decisions_timestamp ON routing_decisions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_routing_decisions_task_type ON routing_decisions(task_type);
CREATE INDEX IF NOT EXISTS idx_routing_decisions_model ON routing_decisions(selected_model);
CREATE INDEX IF NOT EXISTS idx_routing_decisions_decision_id ON routing_decisions(decision_id);

CREATE INDEX IF NOT EXISTS idx_routing_patterns_agent ON routing_patterns(agent_wallet);
CREATE INDEX IF NOT EXISTS idx_routing_patterns_type ON routing_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_routing_patterns_task_type ON routing_patterns(task_type);
CREATE INDEX IF NOT EXISTS idx_routing_patterns_pattern_id ON routing_patterns(pattern_id);
CREATE INDEX IF NOT EXISTS idx_routing_patterns_confidence ON routing_patterns(confidence DESC);

CREATE INDEX IF NOT EXISTS idx_model_performance_agent ON model_performance(agent_wallet);
CREATE INDEX IF NOT EXISTS idx_model_performance_model ON model_performance(model);
CREATE INDEX IF NOT EXISTS idx_model_performance_provider ON model_performance(provider);
CREATE INDEX IF NOT EXISTS idx_model_performance_task_type ON model_performance(task_type);

CREATE INDEX IF NOT EXISTS idx_router_quotas_tier ON agent_router_quotas(tier);
CREATE INDEX IF NOT EXISTS idx_router_quotas_paid_until ON agent_router_quotas(paid_until);
