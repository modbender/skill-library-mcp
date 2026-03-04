# Bunpro API Structure Reference

Community-documented API for Bunpro (reverse-engineered with permission).

**Base URL:** `https://api.bunpro.jp/api/frontend`

**Authentication:** Bearer token (JWT) from browser console/storage

## Authentication

The API requires a Bearer token obtained from the browser:

```bash
curl "https://api.bunpro.jp/api/frontend/user" \
  -H "Authorization: Bearer <token_from_browser>"
```

**To get token:**
1. Log into bunpro.jp
2. Open DevTools (F12)
3. Check Console for `FRONTEND_API_TOKEN`
4. Or check Network tab for `Authorization: Bearer` header on API calls
5. Or check Application → Local Storage

## Key Endpoints

### User

#### Get User
`GET /user`

Returns user profile:
```json
{
  "user": {
    "data": {
      "id": "12345",
      "type": "user",
      "attributes": {
        "id": 12345,
        "username": "NotARealUser",
        "level": 34,
        "xp": 64043,
        "is_lifetime": false,
        "buncoin": 10000,
        "created_at": "2025-06-16T22:34:42.092Z"
      }
    }
  }
}
```

#### Get User Furigana Settings
`GET /user/user_furigana`

#### Add Known Kanji
`POST /user/add_known_kanji`

Request body:
```json
{"kanji": "漢"}
```

#### Get Due Items
`GET /user/due`

Returns items available for review now:
```json
{
  "data": [
    {
      "id": "123",
      "type": "due_item",
      "attributes": {
        "reviewable_id": 456,
        "reviewable_type": "Grammar",
        "available_at": "2026-02-16T14:00:00Z",
        "is_leech": true,
        "streak": 3
      }
    }
  ]
}
```

#### Get Study Queue
`GET /user/queue`

Returns scheduled reviews:
```json
{
  "data": [
    {
      "id": "123",
      "type": "queue_item",
      "attributes": {
        "reviewable_id": 456,
        "reviewable_type": "Grammar",
        "available_at": "2026-02-16T15:00:00Z"
      }
    }
  ]
}
```

### Reviews

#### Get All Reviews
`GET /reviews?page=1&per_page=100`

Returns paginated list of your grammar reviews:
```json
{
  "data": [
    {
      "id": "123",
      "type": "review",
      "attributes": {
        "reviewable_id": 456,
        "reviewable_type": "Grammar",
        "grammar_point_id": 789,
        "srs_stage": 5,
        "srs_stage_string": "master",
        "next_review": "2026-02-16T20:00:00Z",
        "last_review": "2026-02-14T20:00:00Z",
        "burned": false,
        "created_at": "2025-06-16T22:34:42.092Z",
        "updated_at": "2026-02-14T20:00:00Z"
      }
    }
  ],
  "meta": {
    "total": 150
  }
}
```

#### Update Review
`POST /reviews/{reviewId}/update`

#### Add to Reviews
`PATCH /reviews/add_to_reviews`

### User Stats

#### Get Base Stats
`GET /user_stats/base_stats`

#### Get JLPT Progress
`GET /user_stats/jlpt_progress_mixed`

#### Get Daily Forecast
`GET /user_stats/forecast_daily`

Returns upcoming review counts by day:
```json
{
  "data": {
    "attributes": {
      "forecast": {
        "2026-02-16": 45,
        "2026-02-17": 32,
        "2026-02-18": 28
      }
    }
  }
}
```

#### Get Hourly Forecast
`GET /user_stats/forecast_hourly`

#### Get SRS Level Overview
`GET /user_stats/srs_level_overview`

Returns SRS distribution:
```json
{
  "data": {
    "attributes": {
      "srs_levels": {
        "apprentice": 25,
        "guru": 50,
        "master": 30,
        "enlightened": 20,
        "burned": 100
      },
      "burned_count": 100
    }
  }
}
```

#### Get Review Activity
`GET /user_stats/review_activity`

Returns daily review counts:
```json
{
  "data": {
    "attributes": {
      "activity": {
        "2026-02-15": {"total": 50, "correct": 45},
        "2026-02-14": {"total": 40, "correct": 38}
      }
    }
  }
}
```

#### Get SRS Level Details
`GET /user_stats/srs_level_details?level=expert&reviewable_type=Vocab&page=1`

#### Get SRS Self-Study Level Details
`GET /user_stats/srs_self_study_level_details?reviewable_type=Vocab&page=1`

#### Get SRS Ghost Level Details
`GET /user_stats/srs_ghost_level_details?reviewable_type=Vocab`

### Review Histories

#### Get Last Session
`GET /review_histories/last_session`

#### Get Last 24 Hours
`GET /review_histories/last_24_hours`

### Reviewables

#### Get Vocab
`GET /reviewables/vocab/{vocabSlugOrId}`

#### Get Prev/Next By Deck
`GET /reviewables/vocab/{vocabId}/prev_next_by_deck_id?deck_id=28`

### Search

#### Search
`POST /search/v1_1`

Request body:
```json
{"query": "string"}
```

### Settings

#### Update Settings
`PATCH /settings/update`

### Bookmarks

#### Add Bookmark
`POST /bookmarks`

#### Delete Bookmark
`DELETE /bookmarks/{bookmarkId}`

## Grammar Points

Note: The API structure for grammar points is still being documented. The `/reviews` endpoint includes `grammar_point_id` which can be cross-referenced.

## Data Types

### Reviewable Types
- `Grammar` - Grammar points
- `Vocab` - Vocabulary items

### SRS Stages
- `apprentice` - Learning (stages 1-4)
- `guru` - Passed (stages 5-6)
- `master` - Solid (stage 7)
- `enlightened` - Very solid (stage 8)
- `burned` - Complete (stage 9)

### JLPT Levels
- `N5` - Beginner
- `N4` - Elementary
- `N3` - Intermediate
- `N2` - Upper-intermediate
- `N1` - Advanced

## Important Notes

- **Unofficial API:** This is community-documented and may change
- **Token Source:** Must extract from browser, no official API key
- **Rate Limiting:** Unknown limits - be respectful
- **Permission:** Documented with permission from Bunpro team (see community forum)
- **Stability:** Bunpro may change endpoints without notice

## References

- [Bunpro Community API GitHub](https://github.com/cbullard-dev/bunpro-community-api)
- [Bunpro Community Forum API Discussion](https://community.bunpro.jp/t/bunpro-api-when/100574)
- [PyBunpro Documentation](https://patrickayoup.github.io/pybunpro/)
