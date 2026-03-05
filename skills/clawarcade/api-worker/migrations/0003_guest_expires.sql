-- Migration: Add guest expiration column only
-- Date: 2026-02-10

ALTER TABLE players ADD COLUMN guest_expires_at DATETIME;
CREATE INDEX IF NOT EXISTS idx_players_guest_expires ON players(guest_expires_at);
