---
name: virlo
description: Virlo social media intelligence — viral video analytics, hashtag rankings, trend digests, and social listening across YouTube, TikTok, and Instagram. Use for content strategy, trend discovery, competitive analysis, and niche monitoring.
license: MIT
metadata:
  {
    "openclaw":
      {
        "emoji": "☄️",
        "requires": { "bins": ["curl"], "env": ["VIRLO_API_KEY"] },
        "primaryEnv": "VIRLO_API_KEY",
        "homepage": "https://dev.virlo.ai",
        "source": "https://github.com/CalciferFriend/virlo-skill",
      },
  }
---

# Virlo

Social media intelligence for short-form video — Bloomberg for viral content.

Homepage: https://dev.virlo.ai
Source: https://github.com/CalciferFriend/virlo-skill
Full API docs: https://dev.virlo.ai/docs | Playground: https://dev.virlo.ai/docs/playground

## Config

Set `VIRLO_API_KEY` environment variable. Your API key has the format `virlo_tkn_<your_key>` and can be obtained from the [Virlo dashboard](https://dev.virlo.ai/dashboard).

## Context

The Virlo API provides cross-platform analytics across YouTube, TikTok, and Instagram. Key capabilities:

- **Hashtags** — 500K+ hashtags ranked by usage count and total views
- **Trends** — Daily curated trending topics updated at 1am UTC
- **Videos** — 2M+ viral video performance data (views, likes, shares, comments)
- **Orbit** — Keyword-based social listening with async analysis jobs
- **Comet** — Automated niche monitoring with scheduled scraping

## API Access

All endpoints use base URL `https://api.virlo.ai/v1`, `snake_case` naming, and return data in a `{ "data": ... }` envelope.

### Making Requests

Use `curl` directly with the `VIRLO_API_KEY` environment variable:

```bash
# GET request
curl -s -X GET "https://api.virlo.ai<endpoint>" \
  -H "Authorization: Bearer ${VIRLO_API_KEY}" \
  -H "Content-Type: application/json"

# POST request with JSON body
curl -s -X POST "https://api.virlo.ai<endpoint>" \
  -H "Authorization: Bearer ${VIRLO_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '<json-body>'
```

### Examples

```bash
# List top hashtags
curl -s -X GET "https://api.virlo.ai/v1/hashtags" \
  -H "Authorization: Bearer ${VIRLO_API_KEY}" \
  -H "Content-Type: application/json"

# Top 10 viral videos
curl -s -X GET "https://api.virlo.ai/v1/videos?limit=10" \
  -H "Authorization: Bearer ${VIRLO_API_KEY}" \
  -H "Content-Type: application/json"

# Daily trend digest
curl -s -X GET "https://api.virlo.ai/v1/trends" \
  -H "Authorization: Bearer ${VIRLO_API_KEY}" \
  -H "Content-Type: application/json"

# Create an Orbit search
curl -s -X POST "https://api.virlo.ai/v1/orbit" \
  -H "Authorization: Bearer ${VIRLO_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"name":"AI research","keywords":["artificial intelligence","AI tools"]}'
```

---

## API Reference

### Authentication

All requests require a Bearer token:

```
Authorization: Bearer virlo_tkn_<your_key>
```

Never commit API keys to version control. Regenerate compromised keys from the dashboard.

### Response Envelope

All responses use a `{ "data": ... }` envelope. List endpoints include pagination metadata:

```json
{
  "data": {
    "total": 500,
    "limit": 50,
    "offset": 0,
    "items": [ ... ]
  }
}
```

### Pagination

List endpoints use offset-based pagination via `limit` and `page` query parameters:

| Parameter | Type    | Default | Description             |
| --------- | ------- | ------- | ----------------------- |
| `limit`   | integer | 50      | Items per page (1-100)  |
| `page`    | integer | 1       | Page number (1-indexed) |

Maximum of 1000 total results accessible via pagination.

### Common Query Parameters

Many video-related endpoints support these filters:

| Parameter    | Type    | Description                                       |
| ------------ | ------- | ------------------------------------------------- |
| `min_views`  | integer | Minimum view count threshold                      |
| `platforms`  | string  | Comma-separated: `youtube`, `tiktok`, `instagram` |
| `start_date` | string  | ISO 8601 date filter (earliest publish date)      |
| `end_date`   | string  | ISO 8601 date filter (latest publish date)        |
| `order_by`   | string  | Sort field (varies per endpoint)                  |
| `sort`       | string  | Sort direction: `asc` or `desc` (default: `desc`) |

### Platforms

- `youtube` — YouTube Shorts and videos
- `tiktok` — TikTok videos
- `instagram` — Instagram Reels

---

### Hashtags

Virlo tracks 500K+ hashtags ranked by usage count and total views.

#### List Hashtags

```
GET /v1/hashtags
```

Standard pagination (`limit`, `page`).

**Response:**
```json
{
  "data": [
    {
      "hashtag": "#shorts",
      "count": 10926,
      "total_views": 869912593
    }
  ]
}
```

| Field         | Type    | Description                                   |
| ------------- | ------- | --------------------------------------------- |
| `hashtag`     | string  | The hashtag text (may or may not include `#`)  |
| `count`       | integer | Number of videos using this hashtag           |
| `total_views` | integer | Sum of views across all videos with this tag  |

---

### Trends

Daily curated trending topics updated at 1am UTC.

#### List Trend Groups

```
GET /v1/trends
```

Standard pagination (`limit`, `page`).

**Response:**
```json
{
  "data": [
    {
      "id": "b88c0c23-8501-4975-a1e9-b7c1160c6342",
      "title": "Trends for Oct 15th",
      "trends": [
        {
          "id": "132ea402-804d-4515-b706-f3ff9c698c5e",
          "trend_id": "8ab75d1a-cb50-4885-b9b3-2e4ede2a3620",
          "trend_group_id": "b88c0c23-8501-4975-a1e9-b7c1160c6342",
          "ranking": 1,
          "trend": {
            "id": "8ab75d1a-cb50-4885-b9b3-2e4ede2a3620",
            "name": "NBA Season Opening Night",
            "description": "The 2025-26 NBA season officially tipped off...",
            "trend_type": "content"
          }
        }
      ]
    }
  ]
}
```

| Field    | Type   | Description                                      |
| -------- | ------ | ------------------------------------------------ |
| `id`     | string | UUID of the trend group                          |
| `title`  | string | Display title (e.g., "Trends for Oct 15th")      |
| `trends` | array  | Array of ranked trend entries                    |

Trend entry fields: `id`, `trend_id`, `trend_group_id`, `ranking`, `trend` (object with `id`, `name`, `description`, `trend_type`).

---

### Videos

2M+ viral videos across YouTube, TikTok, and Instagram.

#### List Top Videos (Cross-Platform)

```
GET /v1/videos
```

| Parameter    | Type    | Description                                       |
| ------------ | ------- | ------------------------------------------------- |
| `limit`      | integer | Items per page (1-100, default 50)                |
| `page`       | integer | Page number (1-indexed, default 1)                |
| `min_views`  | integer | Minimum view count filter                         |
| `platforms`  | string  | Comma-separated: `youtube`, `tiktok`, `instagram` |
| `start_date` | string  | ISO 8601 earliest publish date                    |
| `end_date`   | string  | ISO 8601 latest publish date                      |
| `order_by`   | string  | `publish_date`, `views`, `created_at`             |
| `sort`       | string  | `asc` or `desc` (default: `desc`)                 |

#### Platform-Specific Endpoints

```
GET /v1/youtube-videos
GET /v1/tiktok-videos
GET /v1/instagram-videos
```

Same parameters and response shape as `/v1/videos`, filtered to a single platform.

#### Video Object Fields

| Field                | Type         | Description                                |
| -------------------- | ------------ | ------------------------------------------ |
| `id`                 | string       | Virlo UUID                                 |
| `url`                | string       | Original video URL                         |
| `publish_date`       | string       | ISO 8601 publish timestamp                 |
| `views`              | integer      | View count                                 |
| `number_of_likes`    | integer      | Like count                                 |
| `number_of_comments` | integer      | Comment count                              |
| `description`        | string       | Video description                          |
| `thumbnail_url`      | string       | Thumbnail image URL                        |
| `hashtags`           | string[]     | Extracted hashtags                         |
| `type`               | string       | Platform: `youtube`, `tiktok`, `instagram` |
| `niche`              | string       | Content niche category                     |
| `author_id`          | string       | UUID of the video author                   |
| `bookmarks`          | integer      | Bookmark/save count                        |
| `external_id`        | string       | Platform-specific video ID                 |
| `region`             | string/null  | Geographic region code                     |
| `duration`           | integer      | Duration in seconds                        |
| `transcript_raw`     | string/null  | Raw video transcript (when available)      |

---

### Orbit — Social Listening

Queue keyword-based video discovery jobs that search across platforms. Supports async analysis, Meta ads collection, and creator outlier detection.

#### Create Orbit Search

```
POST /v1/orbit
```

| Field                     | Type     | Required | Description                                                    |
| ------------------------- | -------- | -------- | -------------------------------------------------------------- |
| `name`                    | string   | Yes      | Descriptive name for the search job                            |
| `keywords`                | string[] | Yes      | Keywords to search (1-10)                                      |
| `platforms`               | string[] | No       | Platforms: `youtube`, `tiktok`, `instagram`. Default: all      |
| `min_views`               | integer  | No       | Minimum view count threshold                                   |
| `time_period`             | string   | No       | `today`, `this_week`, `this_month`, `this_year`                |
| `run_analysis`            | boolean  | No       | Enable AI social intelligence analysis (default: false)        |
| `enable_meta_ads`         | boolean  | No       | Enable Meta ads collection (default: false)                    |
| `exclude_keywords`        | string[] | No       | Keywords to exclude from results                               |
| `exclude_keywords_strict` | boolean  | No       | Also check transcripts for exclusions (default: false)         |

#### List Orbit Searches

```
GET /v1/orbit
```

Paginated list of all search jobs. Standard `limit`/`page` parameters.

#### Get Orbit Results

```
GET /v1/orbit/:orbit_id
```

Poll until job completes. When `run_analysis: true`, includes AI analysis report.

Query params: `order_by` (`views`, `likes`, `shares`, `comments`, `bookmarks`, `publish_date`, `author.followers`), `sort` (`asc`/`desc`).

Response fields: `name`, `keywords`, `analysis` (markdown AI report when ready), `results` (contains `total_videos`, platform counts, `trends`, `videos`, `ads`, `creators`).

#### Get Orbit Videos (Paginated)

```
GET /v1/orbit/:orbit_id/videos
```

Standard pagination plus `min_views`, `platforms`, `start_date`, `end_date`, `order_by`, `sort`.

#### Get Orbit Ads

```
GET /v1/orbit/:orbit_id/ads
```

Meta ads collected (requires `enable_meta_ads: true`). Pagination plus `order_by` (`created_at`, `page_like_count`), `sort`.

#### Get Creator Outliers

```
GET /v1/orbit/:orbit_id/creators/outliers
```

Creators outperforming their follower count. High `outlier_ratio` = content reaching far beyond follower base. Standard pagination.

---

### Comet — Automated Niche Monitoring

Create niche configs that automatically discover videos, ads, and creator outliers on a schedule.

#### Create Comet Config

```
POST /v1/comet
```

| Field                     | Type     | Required | Description                                            |
| ------------------------- | -------- | -------- | ------------------------------------------------------ |
| `name`                    | string   | Yes      | Descriptive name (e.g., "Tech Reviews")                |
| `keywords`                | string[] | Yes      | Keywords to search (1-20)                              |
| `platforms`               | string[] | Yes      | Platforms: `youtube`, `tiktok`, `instagram`             |
| `cadence`                 | string   | Yes      | `daily`, `weekly`, `monthly`, or cron expression       |
| `min_views`               | integer  | Yes      | Minimum view count threshold                           |
| `time_range`              | string   | Yes      | `today`, `this_week`, `this_month`, `this_year`        |
| `is_active`               | boolean  | No       | Default: true. Set false to create paused              |
| `meta_ads_enabled`        | boolean  | No       | Enable Meta ads collection (default: false)            |
| `exclude_keywords`        | string[] | No       | Keywords to exclude                                    |
| `exclude_keywords_strict` | boolean  | No       | Also check transcripts for exclusions (default: false) |

#### List Comet Configs

```
GET /v1/comet
```

Add `?include_inactive=true` to include deactivated configs.

#### Get / Update / Delete Comet Config

```
GET /v1/comet/:id
PUT /v1/comet/:id       # Full replacement — all required fields must be provided
DELETE /v1/comet/:id     # Soft-delete, returns 204
```

#### Get Comet Videos

```
GET /v1/comet/:id/videos
```

Standard pagination plus `min_views`, `platforms`, `start_date`, `end_date`, `order_by`, `sort`.

#### Get Comet Ads

```
GET /v1/comet/:id/ads
```

Requires `meta_ads_enabled: true`. Standard pagination plus `order_by` (`created_at`, `page_like_count`), `sort`.

#### Get Creator Outliers

```
GET /v1/comet/:id/creators/outliers
```

Standard pagination.

---

### Error Handling

| Code | Name                  | Description                           |
| ---- | --------------------- | ------------------------------------- |
| 200  | OK                    | Request processed successfully        |
| 201  | Created               | Resource created                      |
| 202  | Accepted              | Async job queued (e.g., Orbit search) |
| 204  | No Content            | Successful deletion                   |
| 400  | Bad Request           | Invalid request parameters            |
| 401  | Unauthorized          | Missing or invalid API key            |
| 403  | Forbidden             | Insufficient permissions              |
| 404  | Not Found             | Resource not found                    |
| 422  | Unprocessable Entity  | Valid syntax but cannot process        |
| 429  | Too Many Requests     | Rate limit exceeded                   |
| 500  | Internal Server Error | Server error                          |

Error response format:
```json
{
  "error": {
    "type": "validation_error",
    "message": "keywords is required",
    "param": "keywords"
  }
}
```

### Rate Limits

- Max `limit` per request: 100 items
- Max total accessible results: 1,000 items per query
- On `429`, back off and retry after the `retry_after` value (in seconds)
