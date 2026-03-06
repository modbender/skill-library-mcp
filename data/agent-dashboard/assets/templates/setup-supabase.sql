-- Mission Control Dashboard — Supabase Setup
-- Run this in your Supabase SQL Editor (Dashboard → SQL Editor → New Query)
--
-- This creates a single table for storing dashboard state with:
-- - Realtime enabled for instant websocket updates
-- - RLS policies: anon can read AND update this table only
-- - No service_role key required — the anon key handles everything
--
-- Security model:
-- - The anon key can read and update ONLY this one table
-- - All other tables in your project are unaffected
-- - No DELETE allowed — the dashboard row cannot be removed via anon key
-- - Worst case: someone overwrites your dashboard status (not sensitive data)

-- 1. Create the dashboard_state table
CREATE TABLE IF NOT EXISTS dashboard_state (
    id TEXT PRIMARY KEY DEFAULT 'main',
    data JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Enable Row Level Security
ALTER TABLE dashboard_state ENABLE ROW LEVEL SECURITY;

-- 3. Allow anon to read dashboard data
CREATE POLICY "Allow public read"
    ON dashboard_state
    FOR SELECT
    USING (true);

-- 4. Allow anon to update dashboard data (for push script)
-- This is scoped to this single table only — other tables are unaffected
CREATE POLICY "Allow public update"
    ON dashboard_state
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- 5. Allow anon to insert initial row if needed
CREATE POLICY "Allow public insert"
    ON dashboard_state
    FOR INSERT
    WITH CHECK (true);

-- NOTE: No DELETE policy — anon cannot delete rows from this table

-- 6. Enable Realtime for instant updates
ALTER PUBLICATION supabase_realtime ADD TABLE dashboard_state;

-- 7. Insert the initial row (required before first push)
INSERT INTO dashboard_state (id, data)
VALUES ('main', '{"actionRequired":[],"activeNow":[],"products":[],"crons":[],"recentActivity":[]}')
ON CONFLICT (id) DO NOTHING;

-- Done! Your dashboard_state table is ready.
--
-- Next steps:
-- 1. Copy your SUPABASE_URL from Settings → API → Project URL
-- 2. Copy your SUPABASE_ANON_KEY from Settings → API → anon public
-- 3. Update tier3-realtime.html with your URL and anon key
-- 4. Set SUPABASE_URL and SUPABASE_ANON_KEY as env vars for the push script
-- 5. No service_role key needed!
