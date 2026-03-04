-- Add first_play_time and duration_minutes to tournaments
-- Timer starts when first agent plays, not at creation time

ALTER TABLE tournaments ADD COLUMN first_play_time DATETIME;
ALTER TABLE tournaments ADD COLUMN duration_minutes INTEGER DEFAULT 1440; -- 24 hours default

-- Also add flagged columns to tournament_scores if not exists
-- (may already exist from snake server updates)
