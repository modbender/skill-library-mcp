-- x402 Payment Protocol Integration
-- Enables AI agents to autonomously pay for Pro tier (unlimited compressions)

-- Payment requests (pending x402 transactions)
CREATE TABLE IF NOT EXISTS payment_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_id TEXT UNIQUE NOT NULL,
  agent_wallet TEXT NOT NULL,
  amount_requested REAL NOT NULL,
  token TEXT NOT NULL, -- 'USDT', 'USDC', 'SOL'
  status TEXT DEFAULT 'pending' NOT NULL, -- 'pending', 'completed', 'expired'
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME,
  tx_hash TEXT
);

-- Completed payment transactions
CREATE TABLE IF NOT EXISTS payment_transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_wallet TEXT NOT NULL,
  tx_hash TEXT UNIQUE NOT NULL,
  amount REAL NOT NULL,
  token TEXT NOT NULL,
  chain TEXT NOT NULL, -- 'base', 'solana', 'ethereum'
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  verified BOOLEAN DEFAULT 0,
  tier_granted TEXT, -- 'pro'
  duration_months INTEGER DEFAULT 1
);

-- Indexes for payment queries
CREATE INDEX IF NOT EXISTS idx_payment_requests_id ON payment_requests(request_id);
CREATE INDEX IF NOT EXISTS idx_payment_requests_wallet ON payment_requests(agent_wallet);
CREATE INDEX IF NOT EXISTS idx_payment_requests_status ON payment_requests(status);

CREATE INDEX IF NOT EXISTS idx_payment_tx_hash ON payment_transactions(tx_hash);
CREATE INDEX IF NOT EXISTS idx_payment_wallet ON payment_transactions(agent_wallet);
CREATE INDEX IF NOT EXISTS idx_payment_timestamp ON payment_transactions(timestamp);
