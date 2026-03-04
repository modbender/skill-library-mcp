-- Add Moltbook verification columns to players table
-- Run with: wrangler d1 execute clawmd-db --file=scripts/migrate-moltbook.sql

ALTER TABLE players ADD COLUMN moltbook_username TEXT;
ALTER TABLE players ADD COLUMN moltbook_verified BOOLEAN DEFAULT FALSE;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_players_moltbook_username ON players(moltbook_username);
