# WaniKani API Structure Reference

Quick reference for working with WaniKani API v2 (revision 20170710).

## Authentication

```bash
curl "https://api.wanikani.com/v2/user" \
  -H "Authorization: Bearer <token>" \
  -H "Wanikani-Revision: 20170710"
```

## Key Endpoints

### User
`GET /user`

Returns user profile including:
- `id`, `username`, `level`
- `subscription`: max_level_granted, active, type, period_ends_at
- `started_at`: when they began WaniKani

### Assignments
`GET /assignments`

User progress on subjects. Key fields:
- `subject_id`, `subject_type` (radical/kanji/vocabulary/kana_vocabulary)
- `srs_stage` (0-9: locked→apprentice→guru→master→enlightened→burned)
- `unlocked_at`, `started_at`, `passed_at`, `burned_at`
- `available_at`: next review time

Filters: `updated_after`, `srs_stages`, `subject_types`, `levels`, `started`, `passed`, `burned`

### Level Progressions
`GET /level_progressions`

Tracks level unlock/start/pass/completion:
- `level` (1-60)
- `unlocked_at`, `started_at`, `passed_at`, `completed_at`, `abandoned_at`

### Reviews
`GET /reviews`

Individual review records:
- `assignment_id`, `subject_id`
- `starting_srs_stage`, `ending_srs_stage`
- `incorrect_meaning_answers`, `incorrect_reading_answers`
- `created_at`

Max 1000 per page (vs 500 for other endpoints).

### Review Statistics
`GET /review_statistics`

Aggregated per-subject statistics:
- `subject_id`, `subject_type`
- `meaning_correct`, `meaning_incorrect`, `meaning_current_streak`, `meaning_max_streak`
- `reading_correct`, `reading_incorrect`, `reading_current_streak`, `reading_max_streak`
- `percentage_correct`

### Resets
`GET /resets`

Account reset history:
- `original_level`, `target_level`
- `confirmed_at`, `created_at`

## Response Structure

### Collection Response
```json
{
  "object": "collection",
  "url": "...",
  "pages": {
    "per_page": 500,
    "next_url": "...",
    "previous_url": null
  },
  "total_count": 1600,
  "data_updated_at": "...",
  "data": [...]
}
```

### Resource Response
```json
{
  "id": 123,
  "object": "assignment",
  "url": "...",
  "data_updated_at": "...",
  "data": {...}
}
```

## Pagination

Cursor-based using `page_after_id` or `page_before_id`:
- Collections return `pages.next_url` when more data exists
- Extract `page_after_id` from URL to continue

## Incremental Sync

Use `updated_after` filter (ISO8601 timestamp) to fetch only changed records:
```
GET /assignments?updated_after=2024-01-15T10:30:00.000000Z
```

## SRS Stages

| Stage | Name | Description |
|-------|------|-------------|
| 0 | Locked | Not available yet |
| 1 | Apprentice I | Just started lessons |
| 2 | Apprentice II | First review correct |
| 3 | Apprentice III | |
| 4 | Apprentice IV | |
| 5 | Guru I | Passed - unlocks new items |
| 6 | Guru II | |
| 7 | Master | |
| 8 | Enlightened | |
| 9 | Burned | Complete - no more reviews |

## Subject Types

- `radical`: Visual building blocks
- `kanji`: Characters with readings
- `vocabulary`: Words using kanji
- `kana_vocabulary`: Words using only kana

## Rate Limits

- 60 requests per minute
- Headers include: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`

## Error Codes

- 401: Unauthorized (bad token)
- 429: Rate limit exceeded
- 304: Not Modified (for conditional requests with If-Modified-Since/If-None-Match)
