-- Migration: Add wins tracking for chess tournaments
-- Stores individual match results for win-based tournaments

-- Create chess_matches table for tracking wins
CREATE TABLE IF NOT EXISTS chess_matches (
  id TEXT PRIMARY KEY,
  tournament_id TEXT,
  white_player_id TEXT NOT NULL,
  black_player_id TEXT NOT NULL,
  winner_player_id TEXT, -- NULL for draw
  result TEXT NOT NULL, -- 'white', 'black', 'draw', 'abandoned'
  moves_count INTEGER DEFAULT 0,
  game_duration_seconds INTEGER DEFAULT 0,
  end_reason TEXT, -- 'checkmate', 'resignation', 'timeout', 'stalemate', 'disconnect'
  white_nickname TEXT,
  black_nickname TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_chess_matches_tournament ON chess_matches(tournament_id);
CREATE INDEX IF NOT EXISTS idx_chess_matches_white ON chess_matches(white_player_id);
CREATE INDEX IF NOT EXISTS idx_chess_matches_black ON chess_matches(black_player_id);
CREATE INDEX IF NOT EXISTS idx_chess_matches_winner ON chess_matches(winner_player_id);
CREATE INDEX IF NOT EXISTS idx_chess_matches_created ON chess_matches(created_at);
