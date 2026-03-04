---
name: wanikani-sync
description: Sync WaniKani Japanese learning progress data from the API to local storage for analysis and insights. Use when the user wants to backup their WaniKani progress, generate statistics about their learning, analyze review patterns, track level progression, or access their WaniKani data offline. Handles incremental sync to minimize API calls and stores data in SQLite for easy querying.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - WANIKANI_API_TOKEN
      bins:
        - python3
    primaryEnv: WANIKANI_API_TOKEN
    emoji: 🈴
    homepage: https://www.wanikani.com
---

# WaniKani Sync

Sync your WaniKani progress data locally for analysis and insights generation.

## Overview

This skill provides tools to fetch your WaniKani learning progress via the API and store it locally in SQLite. Once synced, you (or other services) can query the data to generate statistics, track learning patterns, visualize progress, and more.

## Getting Your API Token

1. Log into [WaniKani](https://www.wanikani.com)
2. Go to [Settings → API Tokens](https://www.wanikani.com/settings/personal_access_tokens)
3. Generate a new token (or use existing one)
4. Copy the token (looks like a long alphanumeric string)

**Security Note:** Keep your token private. Never commit it to git or share it publicly.

## Quick Start

### Sync All Data

```bash
# Using environment variable (recommended)
export WANIKANI_API_TOKEN="your-token-here"
python3 scripts/sync.py

# Or pass token directly (less secure)
python3 scripts/sync.py --token "your-token-here"

# Store in specific directory
python3 scripts/sync.py --data-dir ~/wanikani-data
```

### Sync Specific Data

```bash
# Only user info
python3 scripts/sync.py --user-only

# Only assignments (your progress on subjects)
python3 scripts/sync.py --assignments-only

# Only reviews
python3 scripts/sync.py --reviews-only
```

### Force Full Sync

By default, the script does incremental sync (only fetching data updated since last sync). To force a full refresh:

```bash
python3 scripts/sync.py --full
```

## Database Schema

The sync creates a `wanikani.db` SQLite database with these tables:

### `user`
Your account info including level, subscription status, and start date.

### `assignments`
Your progress on each subject (radicals, kanji, vocabulary). Tracks SRS stage, unlock/start/pass/burn timestamps.

### `level_progressions`
Your journey through WaniKani levels with unlock/start/pass/completion timestamps.

### `reviews`
Your review history with correctness counts and SRS stage changes.

### `review_statistics`
Aggregated statistics per subject (correct/incorrect counts, streaks, percentages).

### `resets`
Account reset history.

### `subjects`
The actual learning content (kanji, vocabulary, radicals) with characters, meanings, readings, and mnemonics.

**Sync subjects with:**
```bash
# Sync all subjects (can be large!)
python3 scripts/sync.py --subjects-only

# Sync only specific levels (recommended)
python3 scripts/sync.py --with-subjects --subject-levels 1,2,3,4,5

# Include subjects in full sync
python3 scripts/sync.py --with-subjects
```

### `sync_meta`
Internal table tracking last sync timestamps for incremental updates.

## Common Queries

```sql
-- Current SRS stage distribution
SELECT srs_stage, COUNT(*) FROM assignments GROUP BY srs_stage;

-- Items burned per level
SELECT level, COUNT(*) FROM assignments WHERE burned_at IS NOT NULL GROUP BY level;

-- Average accuracy by subject type
SELECT subject_type, AVG(percentage_correct) FROM review_statistics GROUP BY subject_type;

-- Reviews done in last 7 days
SELECT DATE(created_at) as day, COUNT(*) FROM reviews
WHERE created_at > datetime('now', '-7 days') GROUP BY day;

-- Time spent at each level
SELECT level, started_at, passed_at,
       CASE WHEN passed_at IS NOT NULL
            THEN julianday(passed_at) - julianday(started_at)
            ELSE NULL END as days_to_pass
FROM level_progressions WHERE started_at IS NOT NULL;

-- Most problematic items (with subject characters)
SELECT 
    s.characters,
    s.object as type,
    rs.meaning_incorrect + rs.reading_incorrect as fails,
    rs.percentage_correct as accuracy
FROM review_statistics rs
JOIN subjects s ON rs.subject_id = s.id
WHERE rs.percentage_correct < 75
ORDER BY fails DESC
LIMIT 20;

-- Current leeches (Apprentice stage, failing often, with kanji)
SELECT 
    s.characters,
    s.object as type,
    a.srs_stage,
    rs.meaning_incorrect + rs.reading_incorrect as total_fails,
    rs.percentage_correct
FROM review_statistics rs
JOIN assignments a ON rs.subject_id = a.subject_id
JOIN subjects s ON rs.subject_id = s.id
WHERE a.srs_stage BETWEEN 1 AND 4
  AND rs.percentage_correct < 80
ORDER BY total_fails DESC
LIMIT 15;
```

## API Notes

- Rate limit: 60 requests/minute
- All API requests use the v2 revision `20170710`
- Incremental sync uses `updated_after` filter to minimize API calls
- See `references/api-structure.md` for complete endpoint documentation

## Query Tools

After syncing, use the query helper for common reports:

```bash
# Show your worst leeches (items that keep falling back)
python3 scripts/queries.py leeches

# Show SRS distribution (Apprentice/Guru/Master/etc counts)
python3 scripts/queries.py srs

# Show level progression timeline
python3 scripts/queries.py levels

# Show critical items at risk of falling back
python3 scripts/queries.py critical

# Show accuracy by subject type
python3 scripts/queries.py accuracy
```

See `references/example-queries.sql` for raw SQL you can run directly on the database.

## Files

- `scripts/sync.py` - Main sync tool with CLI
- `scripts/queries.py` - Query helper with common reports
- `references/api-structure.md` - WaniKani API reference
- `references/example-queries.sql` - SQL query examples
