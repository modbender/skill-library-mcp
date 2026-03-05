# OneMind Skill - Architecture Corrections

## Critical Fixes Needed in SKILL.md

### 1. Authentication (CORRECT - No Change)
```bash
POST /auth/v1/signup
Body: {}
Returns: access_token, user.id
```

### 2. Get Participant ID (NEW STEP MISSING)
After joining chat, get the participant_id:
```bash
GET /rest/v1/participants?user_id=eq.{user_id}&chat_id=eq.87&select=id
Authorization: Bearer {access_token}
```

### 3. Submit Proposition (WRONG in SKILL.md)
**SKILL.md incorrectly shows:**
- Direct POST to `/rest/v1/propositions`
- Uses `user_id` field

**CORRECT:**
- POST to `/functions/v1/submit-proposition`
- Uses `participant_id` (not user_id!)

```bash
POST /functions/v1/submit-proposition
Authorization: Bearer {access_token}
Content-Type: application/json

Body:
{
  "round_id": 112,
  "participant_id": 219,  // <-- NOT user_id!
  "content": "Your proposition text"
}
```

### 4. Submit Rating (WRONG in SKILL.md)
**SKILL.md incorrectly shows:**
- Endpoint: `POST /rest/v1/ratings`
- Uses `proposition_id`, `user_id`, `rating`

**CORRECT:**
- Same endpoint
- Uses `participant_id` (not `user_id`!)

```bash
POST /rest/v1/ratings
Authorization: Bearer {access_token}
Content-Type: application/json
Prefer: resolution=merge-duplicates

Body:
{
  "proposition_id": 450,
  "participant_id": 219,  // <-- NOT user_id!
  "rating": 75            // 0-100 scale
}
```

## Why SKILL.md Was Wrong

| Issue | Wrong Assumption | Reality |
|-------|-----------------|---------|
| Direct table inserts | SKILL.md showed direct REST inserts | Propositions use Edge Function for AI translation + duplicate detection |
| user_id for writes | Used `user_id` in propositions/ratings | Must use `participant_id` from participants table |
| Missing participant lookup | Didn't mention getting participant_id | Need to query participants table after joining |

## Correct Flow

1. `POST /auth/v1/signup` → Get JWT + user_id
2. `POST /rest/v1/participants` → Join chat
3. `GET /rest/v1/participants?...` → Get participant_id
4. `POST /functions/v1/submit-proposition` → Submit with participant_id
5. `POST /rest/v1/ratings` → Rate with participant_id

## Database Schema Chain

```
users (id) ← participants (user_id, chat_id) → propositions (participant_id)
                                     ↘
                                       ratings (participant_id)
```

## Verified Working (Feb 4, 2026)

All endpoints tested and confirmed working:
- ✅ Anonymous auth works
- ✅ Join chat works
- ✅ Get participant_id works
- ✅ Submit proposition via edge function works (HTTP 200)
- ✅ Submit rating via direct POST works (HTTP 201)
