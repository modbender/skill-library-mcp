-- Migration: Add guest bot/human support
-- Date: 2026-02-10

-- Add guest expiration column
ALTER TABLE players ADD COLUMN guest_expires_at DATETIME;

-- Add moltbook columns if missing
ALTER TABLE players ADD COLUMN moltbook_id TEXT;
ALTER TABLE players ADD COLUMN moltbook_username TEXT;
ALTER TABLE players ADD COLUMN moltbook_verified INTEGER DEFAULT 0;

-- Create index for guest cleanup
CREATE INDEX IF NOT EXISTS idx_players_guest_expires ON players(guest_expires_at);

-- Note: SQLite doesn't support modifying CHECK constraints
-- New valid types: 'human', 'bot', 'guest_human', 'guest_bot'
-- The CHECK constraint won't be enforced for new types, but INSERTs will work
