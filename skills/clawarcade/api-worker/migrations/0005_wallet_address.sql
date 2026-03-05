-- Add wallet_address column for prize claims
ALTER TABLE players ADD COLUMN wallet_address TEXT;

-- Index for wallet lookups
CREATE INDEX IF NOT EXISTS idx_players_wallet ON players(wallet_address);
