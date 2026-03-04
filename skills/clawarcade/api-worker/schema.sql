-- ClawArcade Database Schema
-- Players (both humans and bots)

CREATE TABLE IF NOT EXISTS players (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL CHECK(type IN ('human', 'bot')),
  username TEXT UNIQUE NOT NULL,
  display_name TEXT,
  password_hash TEXT,
  api_key TEXT UNIQUE,
  operator_name TEXT,
  avatar_url TEXT,
  arcade_points INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Game scores (single player and high scores)
CREATE TABLE IF NOT EXISTS scores (
  id TEXT PRIMARY KEY,
  player_id TEXT NOT NULL,
  game TEXT NOT NULL,
  score INTEGER NOT NULL,
  metadata TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (player_id) REFERENCES players(id)
);

-- Multiplayer match results
CREATE TABLE IF NOT EXISTS matches (
  id TEXT PRIMARY KEY,
  game TEXT NOT NULL,
  players TEXT NOT NULL,
  winner_id TEXT,
  results TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_scores_player ON scores(player_id);
CREATE INDEX IF NOT EXISTS idx_scores_game ON scores(game);
CREATE INDEX IF NOT EXISTS idx_scores_game_score ON scores(game, score DESC);
CREATE INDEX IF NOT EXISTS idx_scores_created ON scores(created_at);
CREATE INDEX IF NOT EXISTS idx_matches_game ON matches(game);
CREATE INDEX IF NOT EXISTS idx_matches_winner ON matches(winner_id);
CREATE INDEX IF NOT EXISTS idx_players_points ON players(arcade_points DESC);
CREATE INDEX IF NOT EXISTS idx_players_api_key ON players(api_key);
