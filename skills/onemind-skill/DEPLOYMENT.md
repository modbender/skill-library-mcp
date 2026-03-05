# OneMind submit-ratings Deployment Guide

## Production Deployment Checklist

### Phase 1: Database Changes

**1. Create the tracking table:**
```sql
-- Run in Supabase SQL Editor
CREATE TABLE IF NOT EXISTS round_participant_submissions (
  round_id integer NOT NULL,
  participant_id integer NOT NULL,
  submitted_at timestamptz DEFAULT now(),
  PRIMARY KEY (round_id, participant_id)
);

-- Index for fast lookup
CREATE INDEX IF NOT EXISTS idx_submissions_participant 
  ON round_participant_submissions(participant_id);

-- Enable RLS
ALTER TABLE round_participant_submissions ENABLE ROW LEVEL SECURITY;

-- Only allow reads (insert handled by Edge Function via service role)
CREATE POLICY "Allow read access" 
  ON round_participant_submissions 
  FOR SELECT USING (true);
```

**2. Modify grid_rankings table (if needed):**
```sql
-- Ensure insert allowed (Edge Function bypasses RLS)
-- No changes needed if using service role key
```

### Phase 2: Deploy Edge Function

**1. Create function file:**
```bash
mkdir -p supabase/functions/submit-ratings
```

Copy the full TypeScript code from `EDGE_FUNCTION_SPEC.md` → Section "Full Edge Function TypeScript"

**2. Add CORS shared module (if not exists):**
```bash
mkdir -p supabase/functions/_shared
```

Create `supabase/functions/_shared/cors.ts`:
```typescript
export const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}
```

**3. Deploy:**
```bash
supabase functions deploy submit-ratings
```

**4. Verify deployment:**
```bash
supabase functions list
```

### Phase 3: Disable Old Endpoint (After Testing)

**Option A: RLS Policy (Recommended)**
```sql
-- Block direct inserts via REST API (keeps GET for reading)
CREATE POLICY "Block direct rating submission" 
  ON grid_rankings 
  FOR INSERT 
  TO anon, authenticated 
  USING (false) 
  WITH CHECK (false);

-- Edge Function bypasses via service role, so this only affects direct REST calls
```

**Option B: Remove endpoint entirely** (breaks backward compatibility)

### Phase 4: Test

**1. Run the test script:**
```bash
chmod +x test_submit_ratings.sh
./test_submit_ratings.sh
```

**2. Manual test via curl:**
```bash
# Replace with real ANON_KEY and get fresh token
curl -s -X POST "https://ccyuxrtrklgpkzcryzpj.supabase.co/functions/v1/submit-ratings" \
  -H "apikey: $ANON_KEY" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "round_id": 112,
    "participant_id": 224,
    "ratings": [
      {"proposition_id": 440, "grid_position": 100},
      {"proposition_id": 441, "grid_position": 0},
      {"proposition_id": 442, "grid_position": 75}
    ]
  }'
```

### Phase 5: Verification

Check all validations work:
- [ ] Missing binary anchors (no 100 or no 0) → 400 error
- [ ] Already submitted for round → 400 error
- [ ] Not in rating phase → 400 error
- [ ] Rating own proposition → 400 error
- [ ] Invalid grid_position (< 0 or > 100) → 400 error
- [ ] Duplicate proposition IDs → 400 error
- [ ] Success case → 200 with ratings_submitted count

### Phase 6: Clean Up

**Update SKILL.md referencing:**
- ✅ Already updated with new endpoint
- ✅ Old endpoint marked as deprecated

**Files in this repo:**
- `SKILL.md` — Updated API documentation
- `EDGE_FUNCTION_SPEC.md` — Full implementation spec
- `DEPLOYMENT.md` — This file (deployment steps)
- `test_submit_ratings.sh` — Test script

---

## Rollback Plan

If issues occur:

**1. Re-enable individual ratings:**
```sql
DROP POLICY "Block direct rating submission" ON grid_rankings;
```

**2. Keep Edge Function running** (doesn't hurt to have both temporarily)

**3. Update SKILL.md** to reflect active endpoint

---

## Post-Deployment Monitoring

Watch for:
- Edge Function cold start latency
- Failed validation error logs
- Database constraint violations

Logs location:
```bash
supabase functions logs submit-ratings --tail
```

