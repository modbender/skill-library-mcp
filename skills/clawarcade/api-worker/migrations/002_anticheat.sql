-- Anti-cheat and API key verification migration
-- Adds response time tracking and Moltbook ID storage

-- Add moltbook_id column (more reliable than username)
ALTER TABLE players ADD COLUMN moltbook_id TEXT;

-- Add response time tracking columns to tournament_scores
ALTER TABLE tournament_scores ADD COLUMN avg_response_time REAL;
ALTER TABLE tournament_scores ADD COLUMN std_dev_response_time REAL;
ALTER TABLE tournament_scores ADD COLUMN total_moves INTEGER;
ALTER TABLE tournament_scores ADD COLUMN flagged BOOLEAN DEFAULT FALSE;
ALTER TABLE tournament_scores ADD COLUMN flag_reason TEXT;

-- Index for finding flagged scores
CREATE INDEX IF NOT EXISTS idx_tournament_scores_flagged ON tournament_scores(tournament_id, flagged);

-- Index for Moltbook ID lookups
CREATE INDEX IF NOT EXISTS idx_players_moltbook_id ON players(moltbook_id);
