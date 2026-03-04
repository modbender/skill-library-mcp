-- Pending bot registrations for post-based verification
CREATE TABLE IF NOT EXISTS pending_registrations (
  id TEXT PRIMARY KEY,
  bot_name TEXT NOT NULL,
  operator_name TEXT NOT NULL,
  moltbook_username TEXT NOT NULL,
  verify_code TEXT NOT NULL UNIQUE,
  expires_at DATETIME NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for cleanup
CREATE INDEX IF NOT EXISTS idx_pending_expires ON pending_registrations(expires_at);
