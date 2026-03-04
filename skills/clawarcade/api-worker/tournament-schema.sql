-- Tournament Schema for ClawArcade
-- Run this after the main schema.sql

-- Tournaments table
CREATE TABLE IF NOT EXISTS tournaments (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  game TEXT NOT NULL, -- 'snake' or 'chess'
  format TEXT DEFAULT 'highscore', -- 'highscore' (competition) or 'bracket'
  status TEXT DEFAULT 'upcoming', -- upcoming, active, completed, cancelled
  prize_pool_usdc REAL,
  prize_1st REAL,
  prize_2nd REAL, 
  prize_3rd REAL,
  start_time DATETIME,
  end_time DATETIME,
  max_players INTEGER DEFAULT 32,
  description TEXT,
  rules TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tournament registrations
CREATE TABLE IF NOT EXISTS tournament_registrations (
  id TEXT PRIMARY KEY,
  tournament_id TEXT NOT NULL,
  player_id TEXT NOT NULL,
  wallet_address TEXT, -- Polygon wallet for prize payout
  registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(tournament_id, player_id),
  FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
  FOREIGN KEY (player_id) REFERENCES players(id)
);

-- Tournament scores (for highscore format)
CREATE TABLE IF NOT EXISTS tournament_scores (
  id TEXT PRIMARY KEY,
  tournament_id TEXT NOT NULL,
  player_id TEXT NOT NULL,
  score INTEGER NOT NULL,
  metadata TEXT, -- JSON with game details
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
  FOREIGN KEY (player_id) REFERENCES players(id)
);

-- Tournament matches (for bracket format, future use)
CREATE TABLE IF NOT EXISTS tournament_matches (
  id TEXT PRIMARY KEY,
  tournament_id TEXT NOT NULL,
  player1_id TEXT NOT NULL,
  player2_id TEXT NOT NULL,
  winner_id TEXT,
  score TEXT, -- JSON with details
  played_at DATETIME,
  round INTEGER,
  FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
);

-- Prize payouts tracking
CREATE TABLE IF NOT EXISTS tournament_payouts (
  id TEXT PRIMARY KEY,
  tournament_id TEXT NOT NULL,
  player_id TEXT NOT NULL,
  wallet_address TEXT NOT NULL,
  amount_usdc REAL NOT NULL,
  placement INTEGER NOT NULL,
  tx_hash TEXT,
  status TEXT DEFAULT 'pending', -- pending, sent, confirmed, failed
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
  FOREIGN KEY (player_id) REFERENCES players(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_tournament_status ON tournaments(status);
CREATE INDEX IF NOT EXISTS idx_tournament_game ON tournaments(game);
CREATE INDEX IF NOT EXISTS idx_tournament_reg_tournament ON tournament_registrations(tournament_id);
CREATE INDEX IF NOT EXISTS idx_tournament_reg_player ON tournament_registrations(player_id);
CREATE INDEX IF NOT EXISTS idx_tournament_scores_tournament ON tournament_scores(tournament_id);
CREATE INDEX IF NOT EXISTS idx_tournament_scores_score ON tournament_scores(tournament_id, score DESC);
CREATE INDEX IF NOT EXISTS idx_tournament_matches_tournament ON tournament_matches(tournament_id);
