---
name: bunpro-sync
description: Sync Bunpro Japanese grammar learning progress from the API to local storage for analysis and insights. Use when the user wants to backup their Bunpro progress, track grammar mastery, analyze review patterns, or monitor JLPT level progression. Works with the community-documented Bunpro Frontend API.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - BUNPRO_FRONTEND_API_TOKEN
      bins:
        - python3
    primaryEnv: BUNPRO_FRONTEND_API_TOKEN
    emoji: 📚
    homepage: https://www.bunpro.jp
---

# Bunpro Sync

Sync your Bunpro grammar learning progress locally for analysis and insights.

**⚠️ Important:** This uses a community-documented API. The official Bunpro API Key from settings does NOT work - you need the Frontend API Token from your browser.

## Overview

This skill fetches your Japanese grammar progress from Bunpro and stores it in a local SQLite database. Track SRS stages, review forecasts, JLPT progress, and identify grammar leeches (items that keep falling back).

## API Keys: The Two Different Tokens

Bunpro has **two different API tokens** that serve different purposes:

### ❌ DO NOT USE: "Official" API Key (from Settings)

- Found at: `bunpro.jp/settings/account`
- Looks like: `d406663ff421af27c87caaa62eefdb7a` (32 hex characters)
- **Does NOT work** with the Frontend API endpoints this skill uses
- Returns 401 Unauthorized errors

### ✅ USE THIS: Frontend API Token (from Browser)

- Found in: Browser DevTools → Console or Application Storage
- Looks like: `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...` (long JWT, 200+ chars)
- **This is what the skill requires**
- Expires periodically (you'll need to refresh it)

### How to Get the Frontend API Token

**Method 1: Console (Recommended)**
1. Go to [bunpro.jp](https://bunpro.jp) and log in
2. Press **F12** to open DevTools
3. Click the **Console** tab
4. Paste this JavaScript and press Enter:
   ```javascript
   Object.fromEntries(
     new URLSearchParams(
       document.cookie.replace(/; /g, '&')
     )
   ).frontend_api_token
   ```
5. Copy the long string that appears (starts with `eyJ`)

**Method 2: Local Storage**
1. Go to bunpro.jp and log in
2. Press F12 → **Application** tab (or **Storage** in Firefox)
3. In the left sidebar, expand **Local Storage** → **https://bunpro.jp**
4. Look for `token`, `authToken`, or `frontend_api_token`
5. Copy the value (starts with `eyJ`)

**Method 3: Network Tab**
1. Go to bunpro.jp and log in
2. Press F12 → **Network** tab
3. Refresh the page
4. Look for any API call (like `/user` or `/queue`)
5. Click it → **Headers** → **Request Headers**
6. Find `Authorization: Bearer eyJ...`
7. Copy the part after "Bearer "

**⚠️ Token Expiry:**
The Frontend API Token expires eventually (days/weeks). When you get 401 errors, repeat the steps above to get a fresh token.

## Quick Start

### Sync All Data

```bash
# Using environment variable (recommended)
export BUNPRO_FRONTEND_API_TOKEN="eyJ0eXAiOiJKV1Qi..."
python3 scripts/sync.py

# Or pass token directly (less secure)
python3 scripts/sync.py --token "eyJ0eXAiOiJKV1Qi..."

# Store in specific directory
python3 scripts/sync.py --data-dir ~/bunpro-data
```

### Sync Specific Data

```bash
# Only user info
python3 scripts/sync.py --user-only

# Only study queue
python3 scripts/sync.py --queue-only

# Only reviews
python3 scripts/sync.py --reviews-only
```

### Force Full Sync

```bash
python3 scripts/sync.py --full
```

## Database Schema

### `user`
Your account info including level, XP, buncoin, lifetime status.

### `grammar_points`
Grammar content including title, meaning, structure, JLPT level, unit/lesson.

### `reviews`
Your SRS progress on each grammar point (stage, next review, burned status).

### `study_queue`
Items scheduled for future review.

### `due_items`
Items currently available for review (includes `is_leech` flag).

### `user_stats`
Aggregated statistics (SRS overview, forecasts, JLPT progress, activity).

### `review_histories`
Review session history (last session, last 24h).

### `sync_meta`
Internal table tracking last sync timestamps.

## Common Queries

```sql
-- Grammar mastery by JLPT level
SELECT jlpt_level, COUNT(*) as total,
       SUM(CASE WHEN burned = 1 THEN 1 ELSE 0 END) as burned
FROM reviews r
JOIN grammar_points g ON r.grammar_point_id = g.id
GROUP BY jlpt_level;

-- Upcoming reviews
SELECT DATE(next_review) as day, COUNT(*)
FROM reviews
WHERE next_review > datetime('now')
GROUP BY day
ORDER BY day
LIMIT 7;

-- Grammar leeches
SELECT g.title, g.meaning, d.streak, r.srs_stage_string
FROM due_items d
JOIN grammar_points g ON d.reviewable_id = g.id
LEFT JOIN reviews r ON d.reviewable_id = r.reviewable_id
WHERE d.is_leech = 1
ORDER BY d.streak ASC;
```

## Query Tools

```bash
# Show SRS distribution
python3 scripts/queries.py srs

# Show upcoming review forecast
python3 scripts/queries.py forecast

# Show grammar mastery by JLPT level
python3 scripts/queries.py grammar --jlpt 5

# Show currently due reviews
python3 scripts/queries.py due

# Show grammar leeches
python3 scripts/queries.py leeches

# Show overall progress
python3 scripts/queries.py progress

# Show recent activity
python3 scripts/queries.py activity
```

## API Notes

- **Base URL:** `https://api.bunpro.jp/api/frontend`
- **Auth:** Bearer JWT token from browser (not settings API key)
- **Rate limits:** Unknown - be reasonable
- **Stability:** Community-documented, may change without notice
- **Permission:** Reverse-engineered with permission from Bunpro team

## Troubleshooting

**401 Unauthorized:**
- Token expired (get fresh one from browser)
- Using wrong token type (need Frontend API Token, not settings API key)
- Token format should be JWT (`eyJ0eXAi...`)

**500 Server Error:**
- Bunpro API may be down
- Endpoint may have changed
- Check [Bunpro Community API docs](https://github.com/cbullard-dev/bunpro-community-api)

**Empty data:**
- You're in vacation mode (check bunpro.jp)
- No reviews done yet
- Different endpoint structure than expected

## References

- [Bunpro Community API GitHub](https://github.com/cbullard-dev/bunpro-community-api)
- [Bunpro Community Forum API Discussion](https://community.bunpro.jp/t/bunpro-api-when/100574)
- [Postman Collection](https://www.postman.com/technical-meteorologist-63813544/bunpro-api/collection/a7eufz9/bunpro-frontend-api)
- `references/api-structure.md` - Full endpoint documentation

## Files

- `scripts/sync.py` - Main sync tool with CLI
- `scripts/queries.py` - Query helper with common reports
- `references/api-structure.md` - Bunpro API reference
