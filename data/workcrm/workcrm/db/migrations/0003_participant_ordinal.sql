-- version: 3
-- Add ordinal to participant to preserve deterministic participant ordering.

PRAGMA foreign_keys = ON;

ALTER TABLE participant ADD COLUMN ordinal INTEGER;

-- Backfill existing rows deterministically (by created_at then id) within each parent.
WITH ranked AS (
  SELECT
    id,
    ROW_NUMBER() OVER (PARTITION BY parent_kind, parent_id ORDER BY created_at, id) - 1 AS rn
  FROM participant
)
UPDATE participant
SET ordinal = (SELECT rn FROM ranked WHERE ranked.id = participant.id)
WHERE ordinal IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_participant_parent_ordinal
  ON participant(parent_kind, parent_id, ordinal);
