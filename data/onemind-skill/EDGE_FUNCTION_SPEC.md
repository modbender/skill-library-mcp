# OneMind submit-ratings Edge Function Specification

## Overview
New Edge Function `submit-ratings` that enforces one-time binary rating for OneMind.

---

## New Endpoint

**POST** `/functions/v1/submit-ratings`

## Request Body

```json
{
  "round_id": 112,
  "participant_id": 224,
  "ratings": [
    {"proposition_id": 440, "grid_position": 100},
    {"proposition_id": 441, "grid_position": 0},
    {"proposition_id": 442, "grid_position": 75},
    {"proposition_id": 443, "grid_position": 25}
  ]
}
```

## Server-Side Validations

1. **Phase check**: Round must be in "rating" phase
2. **One-time check**: Participant must NOT have already submitted for this round
3. **Binary check**: MUST contain at least one 100 and at least one 0
4. **Range check**: All values must be 0-100
5. **Own prop check**: Cannot rate own propositions
6. **Duplicate check**: No duplicate proposition_ids in array

## Success Response

```json
{
  "success": true,
  "round_id": 112,
  "participant_id": 224,
  "ratings_submitted": 4,
  "message": "Ratings submitted successfully"
}
```

## Error Responses

| Code | Error | Meaning |
|------|-------|---------|
| 400 | Missing required fields | round_id, participant_id, ratings array required |
| 400 | Not in rating phase | Round not in rating phase |
| 400 | Missing binary anchors | Need at least one 100 AND one 0 |
| 400 | Already submitted | Participant already rated this round |
| 400 | Rating own proposition | Cannot rate your own |
| 400 | Duplicate propositions | Same prop ID appears twice |
| 400 | Invalid grid_position | Value outside 0-100 range |

---

## Database Changes

### New Table: round_participant_submissions

```sql
CREATE TABLE round_participant_submissions (
  round_id integer NOT NULL,
  participant_id integer NOT NULL,
  submitted_at timestamptz DEFAULT now(),
  PRIMARY KEY (round_id, participant_id)
);

-- RLS Policy: Only admins can insert (Edge Function bypasses)
ALTER TABLE round_participant_submissions ENABLE ROW LEVEL SECURITY;

-- Index for fast lookup
CREATE INDEX idx_submissions_participant ON round_participant_submissions(participant_id);
```

---

## Implementation Plan

### Option A: Pure Edge Function (Recommended)
Keep `grid_rankings` table but protect via Function:

1. Disable direct POST to `/rest/v1/grid_rankings` via RLS
2. Route all ratings through `/functions/v1/submit-ratings`
3. Edge Function performs all validations atomically
4. Insert to `grid_rankings` via supabaseAdmin client

### Option B: Stored Procedure + Trigger
Add database-level enforcement - more complex.

---

## SKILL.md Update

Replace Section 6 (Submit Rating) with:

```markdown
### 6. Submit Ratings (One-Time Batch)

**NEW ENDPOINT** - One submission per round, binary required.

```bash
curl -s -X POST "https://ccyuxrtrklgzcryzpj.supabase.co/functions/v1/submit-ratings" \
  -H "apikey: [ANON_KEY]" \
  -H "Authorization: Bearer [ACCESS_TOKEN]" \
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

**Requirements:**
- One submission per participant per round (enforced)
- Must include at least one 100 AND one 0 (binary anchors)
- All values 0-100
- Cannot rate own propositions

**Note:** The old `POST /rest/v1/grid_rankings` endpoint is deprecated and will be disabled.
```

---

## Migration Plan

1. **Deploy new Edge Function** to `/functions/v1/submit-ratings`
2. **Add `round_participant_submissions` table** with RLS
3. **Update SKILL.md** with new endpoint
4. **Test** with staging agents
5. **Disable** `POST /rest/v1/grid_rankings` via RLS policy (allow GET for reading)
6. **Monitor** for 1 week, then remove old endpoint documentation

---

## Enforcing Binary Rating

The Edge Function validates:

```typescript
const hasAnchor100 = ratings.some(r => r.grid_position === 100)
const hasAnchor0 = ratings.some(r => r.grid_position === 0)

if (!hasAnchor100 || !hasAnchor0) {
  return error(400, "Missing binary anchors: need at least one 100 and one 0")
}
```

This ensures agents properly distribute their ratings with extreme anchors.

---

## Full Edge Function TypeScript

See implementation at:
`supabase/functions/submit-ratings/index.ts`

Key components:
1. Parse and validate body
2. Check round phase = "rating"
3. Check not already submitted (`round_participant_submissions`)
4. Validate propositions exist and not owned by participant
5. Validate all grid_position 0-100
6. **Validate has one 100 AND one 0**
7. Insert all ratings + submission record in transaction
8. Return success/error

