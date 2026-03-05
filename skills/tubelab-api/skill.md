---
name: tubelab
description: YouTube analytics and research API. Search channels, find video outliers, get video details/transcripts/comments, and run scans. Use for YouTube niche research, competitor analysis, and channel analytics.
metadata: {"openclaw":{"emoji":"📊","requires":{"bins":["curl","jq"],"env":["TUBELAB_API_KEY"]},"primaryEnv":"TUBELAB_API_KEY"}}
---

# TubeLab API

YouTube analytics and research API. Discover profitable niches, find viral outlier videos, analyze channels, get transcripts and comments, and run automated scans - all through REST endpoints returning JSON.

- **Base URL:** `https://public-api.tubelab.net/v1`
- **Auth:** API key in header
- **Rate limit:** 10 requests/minute per API key
- **Format:** JSON request/response
- **Docs:** https://tubelab.net/docs/api/introduction

## Authentication

Every request requires an `Authorization` header with your API key:

```
Authorization: Api-Key $TUBELAB_API_KEY
```

Get your API key at https://tubelab.net/developers - requires an [active subscription](https://tubelab.net/pricing).

## Rate Limits & Credits

Rate limited to **10 requests per minute** per API key. Exceeding this returns `429 Too Many Requests`.

Most endpoints cost credits. Cached responses (same request within a short window) are free.

| Endpoint | Cost |
| --- | --- |
| `GET /search/channels` | 10 credits |
| `GET /search/channels/related` | 10 credits |
| `GET /search/outliers` | 5 credits |
| `GET /search/outliers/related` | 5 credits |
| `GET /channel/videos/{id}` | free |
| `GET /channel/shorts/{id}` | free |
| `GET /video/{id}` | free |
| `GET /video/transcript/{id}` | free |
| `GET /video/comments/{id}` | free |
| `POST /scan` | 50–100 credits |
| `GET /scan/{id}` | free |

Scan cost depends on mode: **Fast** = 50 credits, **Standard** = 100 credits.

## Search Endpoints

Search for YouTube channels and viral videos (outliers). All search endpoints support pagination, sorting, and 30+ filters.

### GET /search/channels

**Channels**
Search for channels directly from the [YouTube Niche Finder](https://tubelab.net/youtube-niche-finder) with AI enhanced data and 30+ filters.
Cost: **10 credits** per request.

```bash
curl -s "https://public-api.tubelab.net/v1/search/channels?query=minecraft%20adventures" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

**Query parameters:**

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `query` | string[] | no | Search queries |
| `seed` | string \| number \| null | no | Randomize search results by passing a random seed |
| `filterBy` | "video" \| "short" | no | Filter by statistics of each content kind |
| `contentKind` | "video" \| "short" \| "long-form" \| "short-form" | no | Filter by type of content created by channel: - `video` - channel has videos; - `short` - channel has shorts; - `long-form` - channel has more... |
| `publishedAtFrom` | string | no | Filter by a channel's last parsed video upload date (from a sample of 100 videos) - Expects an ISO date time string. |
| `publishedAtTo` | string | no |  |
| `averageViewsFrom` | integer | no |  |
| `averageViewsTo` | integer | no |  |
| `medianViewsFrom` | integer | no |  |
| `medianViewsTo` | integer | no |  |
| `language` | string[] | no | ISO 639-1 language codes |
| `avgViewsToSubscribersRatioFrom` | number | no | Filter by the outlier score of a channel |
| `avgViewsToSubscribersRatioTo` | number | no |  |
| `subscribersFrom` | integer | no |  |
| `subscribersTo` | integer | no |  |
| `videosCountFrom` | integer | no |  |
| `videosCountTo` | integer | no |  |
| `viewVariationCoefficientFrom` | number | no |  |
| `viewVariationCoefficientTo` | number | no |  |
| `revenueMonthlyEstimationFrom` | number | no |  |
| `revenueMonthlyEstimationTo` | number | no |  |
| `rpmEstimationFrom` | number | no |  |
| `rpmEstimationTo` | number | no |  |
| `avgDurationFrom` | integer | no | Average duration of videos in seconds |
| `avgDurationTo` | integer | no |  |
| `monetizationAdsense` | boolean | no | Filter by whether the channel has AdSense enabled or not |
| `excludeNiche` | string[] | no | Exclude niches from search results by keywords |
| `classificationQuality` | "negative" \| "neutral" \| "positive" | no | **AI** classification of a channel quality. |
| `classificationIsFaceless` | boolean | no | **AI**  classification wether channel content has faceless potential or not |
| `from` | integer | no | Page to fetch |
| `size` | integer | no | Number of items per page |
| `sortBy` | "subscribers" \| "averageViews" \| "avgViewsToSubscribersRatio" \| "viewVariationCoefficient" \| "revenueMonthly" \| "rpm" \| "foundAt" \| "recency" | no | Sort results by a specific metric:  Beaware when using semantic search (applying a query with the `by` parameter set to `semantic`) the sorting... |
| `sortOrder` | "asc" \| "desc" | no | Sorting order of results, where asc is ascending and desc is descending |

**Response shape (abbreviated):**

```json
{
  "pagination": { "total": 100, "from": 0, "size": 20 },
  "hits": [
    {
      "id": "UChn5jutPQB_bRjnG80pzl5w",
      "snippet": { "handle": "@tubelabhq", "title": "TubeLab", "contentKind": ["video","long-form"] },
      "statistics": { "subscribers": 15000, "averageViews": 5000, "avgViewsToSubscribersRatio": 0.33 },
      "language": { "code": "en" },
      "monetization": { "adsense": true },
      "classification": { "quality": "positive", "isFaceless": false }
    }
  ]
}
```

### GET /search/channels/related

**Similar Channels**
Search for YouTube channels with **related content to another channel**.
Cost: **10 credits** per request.

```bash
curl -s "https://public-api.tubelab.net/v1/search/channels/related?relatedChannelId=UChn5jutPQB_bRjnG80pzl5w" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

**Query parameters:**

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `relatedChannelId` | string[] | yes |  |
| `filterBy` | "video" \| "short" | no | Filter by statistics of each content kind |
| `contentKind` | "video" \| "short" \| "long-form" \| "short-form" | no | Filter by type of content created by channel: - `video` - channel has videos; - `short` - channel has shorts; - `long-form` - channel has more... |
| `publishedAtFrom` | string | no | Filter by a channel's last parsed video upload date (from a sample of 100 videos) - Expects an ISO date time string. |
| `publishedAtTo` | string | no |  |
| `averageViewsFrom` | integer | no |  |
| `averageViewsTo` | integer | no |  |
| `medianViewsFrom` | integer | no |  |
| `medianViewsTo` | integer | no |  |
| `language` | string[] | no | ISO 639-1 language codes |
| `avgViewsToSubscribersRatioFrom` | number | no | Filter by the outlier score of a channel |
| `avgViewsToSubscribersRatioTo` | number | no |  |
| `subscribersFrom` | integer | no |  |
| `subscribersTo` | integer | no |  |
| `videosCountFrom` | integer | no |  |
| `videosCountTo` | integer | no |  |
| `viewVariationCoefficientFrom` | number | no |  |
| `viewVariationCoefficientTo` | number | no |  |
| `revenueMonthlyEstimationFrom` | number | no |  |
| `revenueMonthlyEstimationTo` | number | no |  |
| `rpmEstimationFrom` | number | no |  |
| `rpmEstimationTo` | number | no |  |
| `avgDurationFrom` | integer | no | Average duration of videos in seconds |
| `avgDurationTo` | integer | no |  |
| `monetizationAdsense` | boolean | no | Filter by whether the channel has AdSense enabled or not |
| `excludeNiche` | string[] | no | Exclude niches from search results by keywords |
| `classificationQuality` | "negative" \| "neutral" \| "positive" | no | **AI** classification of a channel quality. |
| `classificationIsFaceless` | boolean | no | **AI**  classification wether channel content has faceless potential or not |
| `from` | integer | no | Page to fetch |
| `size` | integer | no | Number of items per page |

**Response shape (abbreviated):**

```json
{
  "pagination": { "total": 50, "from": 0, "size": 20 },
  "hits": [
    {
      "id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
      "snippet": { "handle": "@example", "title": "Example Channel", "contentKind": ["video"] },
      "statistics": { "subscribers": 25000, "averageViews": 8000 },
      "language": { "code": "en" }
    }
  ]
}
```

### GET /search/outliers

**Outliers**
Search for videos directly from the [YouTube Outliers Finder](https://tubelab.net/youtube-outliers-finder) library with AI enhanced data and 30+ filters.
Cost: **5 credits** per request.

```bash
curl -s "https://public-api.tubelab.net/v1/search/outliers?query=minecraft%20adventures&type=video" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

**Query parameters:**

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `query` | string[] | no | Search queries |
| `seed` | string \| number \| null | no | Randomize search results by passing a random seed |
| `sortBy` | "views" \| "zScore" \| "averageViewsRatio" \| "publishedAt" \| "revenue" \| "rpm" | no | Sort results by a specific metric:  Beaware when using semantic search (applying a query with the `by` parameter set to `semantic`) the sorting... |
| `sortOrder` | "asc" \| "desc" | no | Sorting order of results, where asc is ascending and desc is descending |
| `type` | "video" \| "short" | no |  |
| `averageViewsRatioFrom` | number | no |  |
| `averageViewsRatioTo` | number | no |  |
| `zScoreFrom` | number | no |  |
| `zScoreTo` | number | no |  |
| `viewCountFrom` | integer | no |  |
| `viewCountTo` | integer | no |  |
| `language` | string[] | no | ISO 639-1 language codes |
| `durationFrom` | integer | no |  |
| `durationTo` | integer | no |  |
| `publishedAtFrom` | string \| string | no |  |
| `publishedAtTo` | string | no |  |
| `subscribersCountFrom` | integer | no |  |
| `subscribersCountTo` | integer | no |  |
| `channelAvgViewsFrom` | number | no |  |
| `channelAvgViewsTo` | number | no |  |
| `channelVideoCountFrom` | integer | no |  |
| `channelVideoCountTo` | integer | no |  |
| `channelId` | string | no |  |
| `channelAvgViewsToSubscribersRatioFrom` | number | no |  |
| `channelAvgViewsToSubscribersRatioTo` | number | no |  |
| `titlePattern` | string | no |  |
| `referenceId` | string | no |  |
| `rpmEstimationFrom` | number | no |  |
| `rpmEstimationTo` | number | no |  |
| `revenueEstimationFrom` | number | no |  |
| `revenueEstimationTo` | number | no |  |
| `channelMonetizationAdsense` | boolean | no |  |
| `classificationQuality` | "negative" \| "neutral" \| "positive" | no |  |
| `classificationIsFaceless` | boolean | no |  |
| `excludeKeyword` | string[] | no |  |
| `from` | integer | no | Page to fetch |
| `size` | integer | no | Number of items per page |
| `by` | "semantic" \| "lexical" | no | Search by semantics (meaning of words) or lexical (exact words) |

**Response shape (abbreviated):**

```json
{
  "pagination": { "total": 100, "from": 0, "size": 20 },
  "hits": [
    {
      "id": "SVeXR66hcIg",
      "kind": "video",
      "snippet": { "channelId": "UChn5jutPQB_bRjnG80pzl5w", "title": "Video Title", "channelTitle": "Channel Name", "publishedAt": "2025-01-15T00:00:00Z" },
      "statistics": { "viewCount": 500000, "zScore": 4.2, "averageViewsRatio": 10.5, "likeCount": 15000, "commentCount": 1200 },
      "classification": { "quality": "positive", "isFaceless": false }
    }
  ]
}
```

### GET /search/outliers/related

**Similar Outliers**
Search for YouTube outliers with **related content to another outlier(s)**.
Cost: **5 credits** per request.

```bash
curl -s "https://public-api.tubelab.net/v1/search/outliers/related?title=minecraft%20survival%20tutorial&type=video&by=semantic" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

**Query parameters:**

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `title` | string[] | no |  |
| `videoId` | string[] | no |  |
| `thumbnailVideoId` | string | no | A unique YouTube video identifier |
| `relatedChannelId` | string[] | no |  |
| `type` | "video" \| "short" | no |  |
| `averageViewsRatioFrom` | number | no |  |
| `averageViewsRatioTo` | number | no |  |
| `zScoreFrom` | number | no |  |
| `zScoreTo` | number | no |  |
| `viewCountFrom` | integer | no |  |
| `viewCountTo` | integer | no |  |
| `language` | string[] | no | ISO 639-1 language codes |
| `durationFrom` | integer | no |  |
| `durationTo` | integer | no |  |
| `publishedAtFrom` | string \| string | no |  |
| `publishedAtTo` | string | no |  |
| `subscribersCountFrom` | integer | no |  |
| `subscribersCountTo` | integer | no |  |
| `channelAvgViewsFrom` | number | no |  |
| `channelAvgViewsTo` | number | no |  |
| `channelVideoCountFrom` | integer | no |  |
| `channelVideoCountTo` | integer | no |  |
| `channelId` | string | no |  |
| `channelAvgViewsToSubscribersRatioFrom` | number | no |  |
| `channelAvgViewsToSubscribersRatioTo` | number | no |  |
| `titlePattern` | string | no |  |
| `referenceId` | string | no |  |
| `rpmEstimationFrom` | number | no |  |
| `rpmEstimationTo` | number | no |  |
| `revenueEstimationFrom` | number | no |  |
| `revenueEstimationTo` | number | no |  |
| `channelMonetizationAdsense` | boolean | no |  |
| `classificationQuality` | "negative" \| "neutral" \| "positive" | no |  |
| `classificationIsFaceless` | boolean | no |  |
| `excludeKeyword` | string[] | no |  |
| `from` | integer | no | Page to fetch |
| `size` | integer | no | Number of items per page |
| `by` | "semantic" \| "lexical" | no | Search by semantics (meaning of words) or lexical (exact words) |

**Response shape (abbreviated):**

```json
{
  "pagination": { "total": 50, "from": 0, "size": 20 },
  "hits": [
    {
      "id": "dQw4w9WgXcQ",
      "kind": "video",
      "snippet": { "channelId": "UChn5jutPQB_bRjnG80pzl5w", "title": "Similar Video", "publishedAt": "2025-02-01T00:00:00Z" },
      "statistics": { "viewCount": 120000, "zScore": 3.1, "averageViewsRatio": 5.2 }
    }
  ]
}
```

## Channel & Video Endpoints

Get detailed information about specific channels and videos.

### GET /channel/videos/{id}

**Channel Videos**
Get videos from a YouTube channel with sampled metrics.
Cost: **free** per request.

```bash
curl -s "https://public-api.tubelab.net/v1/channel/videos/UChn5jutPQB_bRjnG80pzl5w" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

**Path parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `id` | string | A unique YouTube channel identifier |

**Response shape (abbreviated):**

```json
{
  "id": "UChn5jutPQB_bRjnG80pzl5w",
  "time": "2025-06-15T12:00:00Z",
  "item": {
    "id": "UChn5jutPQB_bRjnG80pzl5w",
    "kind": "channel",
    "snippet": { "title": "TubeLab", "handle": "@tubelabhq" },
    "videos": [{ "id": "SVeXR66hcIg", "title": "Video Title", "viewCount": 50000, "publishedAt": "2025-01-15T00:00:00Z" }],
    "statistics": { "subscribers": 15000, "totalViews": 500000, "videoCount": 120 }
  }
}
```

### GET /channel/shorts/{id}

**Channel Shorts**
Get shorts from a YouTube channel with sampled metrics.
Cost: **free** per request.

```bash
curl -s "https://public-api.tubelab.net/v1/channel/shorts/UChn5jutPQB_bRjnG80pzl5w" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

**Path parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `id` | string | A unique YouTube channel identifier |

**Response shape (abbreviated):**

```json
{
  "id": "UChn5jutPQB_bRjnG80pzl5w",
  "time": "2025-06-15T12:00:00Z",
  "item": {
    "id": "UChn5jutPQB_bRjnG80pzl5w",
    "kind": "channel",
    "snippet": { "title": "TubeLab", "handle": "@tubelabhq" },
    "shorts": [{ "id": "abc123", "title": "Short Title", "viewCount": 100000, "publishedAt": "2025-03-01T00:00:00Z" }],
    "statistics": { "subscribers": 15000, "totalViews": 500000 }
  }
}
```

### GET /video/{id}

**Video Details**
Get details of a YouTube video.
Cost: **free** per request.

```bash
curl -s "https://public-api.tubelab.net/v1/video/SVeXR66hcIg" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

**Path parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `id` | string | A unique YouTube video identifier |

**Response shape (abbreviated):**

```json
{
  "ids": ["SVeXR66hcIg"],
  "time": "2025-06-15T12:00:00Z",
  "items": [
    {
      "id": "SVeXR66hcIg",
      "kind": "video",
      "snippet": { "channelId": "UChn5jutPQB_bRjnG80pzl5w", "title": "Video Title", "publishedAt": "2025-01-15T00:00:00Z" },
      "statistics": { "viewCount": 50000, "likeCount": 2000, "commentCount": 300 }
    }
  ]
}
```

### GET /video/transcript/{id}

**Video Transcript**
Get the transcript of a YouTube video.
Cost: **free** per request.

```bash
curl -s "https://public-api.tubelab.net/v1/video/transcript/SVeXR66hcIg" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

**Path parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `id` | string | A unique YouTube video identifier |

**Response shape (abbreviated):**

```json
{
  "ids": ["SVeXR66hcIg"],
  "items": [
    {
      "id": "SVeXR66hcIg",
      "events": [{ "startMs": 0, "durationMs": 5000, "endMs": 5000, "text": "Hello and welcome..." }],
      "transcript": "Hello and welcome to this video..."
    }
  ]
}
```

### GET /video/comments/{id}

**Video Comments**
Get the last 100 comments of a YouTube video.
Cost: **free** per request.

```bash
curl -s "https://public-api.tubelab.net/v1/video/comments/SVeXR66hcIg" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

**Path parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `id` | string | A unique YouTube video identifier |

**Response shape (abbreviated):**

```json
{
  "ids": ["SVeXR66hcIg"],
  "time": "2025-06-15T12:00:00Z",
  "items": [
    {
      "id": "SVeXR66hcIg",
      "comments": [{ "authorText": "User", "text": "Great video!", "likesCount": 42, "replyCount": 3, "publishedAt": "2025-01-16T00:00:00Z" }],
      "statistics": { "count": 300 }
    }
  ]
}
```

## Scanning Endpoints

Start YouTube scans to discover channels and outlier videos in any niche. Scans run asynchronously - start one, then poll for status.

### POST /scan

**Scan**
Start a YouTube scan to search for outliers and channels on any given topic.
Cost: **50–100 credits** per request.

```bash
curl -s -X POST "https://public-api.tubelab.net/v1/scan" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"findBy":"query","query":["UCUyeluBRhGPCW4rPe_UvBZQ","UCX6OQ3DkcsbYNE6H8uQQuVA"],"mode":"standard"}'
```

**Body parameters:**

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `findBy` | "channels" \| "query" | no | `query` | Start the scan from queries (search results) or channels |
| `query` | string[] | yes |  | Search queries or YouTube channel ids |
| `mode` | "fast" \| "standard" | no | `fast` | - **Fast**: 1000 outliers or 100 channels - **Standard**: 2500 outliers or 250 channels |

**Response shape (abbreviated):**

```json
{
  "id": "2a5e56f5-75f3-4f01-ac85-6e796f5cde87",
  "name": "minecraft, gaming",
  "status": "Queued",
  "input": { "query": ["minecraft", "gaming"], "threshold": 1000 },
  "endedAt": null,
  "createdAt": "2025-06-15T12:00:00Z",
  "updatedAt": "2025-06-15T12:00:00Z"
}
```

### GET /scan/{id}

**Scan**
Get a scan by id.
Cost: **free** per request.

```bash
curl -s "https://public-api.tubelab.net/v1/scan/2a5e56f5-75f3-4f01-ac85-6e796f5cde87" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

**Path parameters:**

| Name | Type | Description |
| --- | --- | --- |
| `id` | string | Scan id |

**Response shape (abbreviated):**

```json
{
  "id": "2a5e56f5-75f3-4f01-ac85-6e796f5cde87",
  "name": "minecraft, gaming",
  "status": "Completed",
  "input": { "query": ["minecraft", "gaming"], "threshold": 1000 },
  "endedAt": "2025-06-15T13:30:00Z",
  "createdAt": "2025-06-15T12:00:00Z",
  "updatedAt": "2025-06-15T13:30:00Z"
}
```

## Scan Workflow

Scans run asynchronously. Here's the typical flow:

1. **Start a scan** with `POST /scan` - returns a scan ID and status `Queued`
2. **Poll for status** with `GET /scan/{id}` - status progresses: `Queued` → `Running` → `Completed`
3. **Search results** with `GET /search/outliers?referenceId={scanId}` - returns discovered outlier videos

```bash
# 1. Start scan
SCAN_ID=$(curl -s -X POST "https://public-api.tubelab.net/v1/scan" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":["minecraft","gaming"],"mode":"fast"}' | jq -r '.id')

# 2. Poll until complete
curl -s "https://public-api.tubelab.net/v1/scan/$SCAN_ID" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY" | jq '.status'

# 3. Search results once completed
curl -s "https://public-api.tubelab.net/v1/search/outliers?referenceId=$SCAN_ID" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

| Mode | Outliers Limit | Channels Limit | Cost | Est. Time |
| --- | --- | --- | --- | --- |
| Fast | 1,000 | 100 | 50 credits | 30 min – 2 hrs |
| Standard | 2,500 | 250 | 100 credits | 2 – 4 hrs |

## Common Patterns

### Pagination

Search endpoints return `pagination.total`, `pagination.from`, and `pagination.size`. Use `from` and `size` query params to paginate:

```bash
# Page 1 (items 0-19)
curl -s "https://public-api.tubelab.net/v1/search/outliers?query=minecraft%20adventures&type=video&from=0&size=20" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"

# Page 2 (items 20-39)
curl -s "https://public-api.tubelab.net/v1/search/outliers?query=minecraft%20adventures&type=video&from=20&size=20" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

### Range Filters

Many numeric fields support `From`/`To` suffixes for range filtering:

```bash
# Channels with 10k-100k subscribers and avg views > 5000
curl -s "https://public-api.tubelab.net/v1/search/channels?query=cooking%20healthy%20recipes&subscribersFrom=10000&subscribersTo=100000&averageViewsFrom=5000" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

### Sorting

Use `sortBy` and `sortOrder` params. Available sort fields vary by endpoint.

**Important:** When using `query`, omit `sortBy` to get the default relevance-based ranking. Adding a sort like `sortBy=views` overrides relevance and returns results ordered by that field, which usually produces worse matches. Only add `sortBy` when you don't use `query` (e.g. filter-only searches).

```bash
# Filter-only search (no query) — sorting makes sense here
curl -s "https://public-api.tubelab.net/v1/search/outliers?type=video&classificationQuality=positive&sortBy=views&sortOrder=desc" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

### Array Parameters

Array params use repeated keys:

```bash
# Multiple search queries
curl -s "https://public-api.tubelab.net/v1/search/channels?query=minecraft%20adventures&query=gaming%20tutorials" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

## Search Recipes

Ready-to-use filter combinations for common research tasks. Date filters use ISO 8601 format - compute relative dates with `date` or substitute directly.

**Tip - queries:** Search is semantic — longer, descriptive queries return much better results than single keywords. Use `query=minecraft adventures` or `query=cooking healthy recipes` instead of just `query=minecraft` or `query=cooking`. Think 2-4 words that describe the niche.

**Tip - sorting:** When using `query`, do NOT add `sortBy` — the default sort is by relevance and gives the best matches. Only use `sortBy` for filter-only searches (no `query`), e.g. sorting by `foundAt` or `views`.

**Tip - `averageViewsRatio`:** When searching outliers, prefer `averageViewsRatioFrom=1` to find videos that outperformed the channel's average. A ratio of 2 means the video got 2x the channel's usual views. Values above 5 are very rare and indicate extreme virality - only use higher thresholds when you want to narrow results significantly.

**Tip - content type:** When searching outliers, prefer `type=video` to focus on long-form videos. Shorts tend to have inflated view counts and skew results. Only use `type=short` when specifically researching short-form content.

### Profitable channels (recently found)

Monetized channels found in the last year with estimated monthly revenue above $1,000 and at least 1,000 subscribers. Sorted by discovery date.

```bash
ONE_YEAR_AGO=$(date -u -d "1 year ago" +%Y-%m-%dT00:00:00Z 2>/dev/null || date -u -v-1y +%Y-%m-%dT00:00:00Z)
curl -s "https://public-api.tubelab.net/v1/search/channels?monetizationAdsense=true&revenueMonthlyEstimationFrom=1000&subscribersFrom=1000&publishedAtFrom=$ONE_YEAR_AGO&language=en&language=de&language=fr&excludeNiche=music&excludeNiche=song&excludeNiche=lofi&excludeNiche=movies&excludeNiche=kids&excludeNiche=news&excludeNiche=politic&sortBy=foundAt&size=20" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

### Trending channels

Channels with high engagement (avg views/subscribers ratio above 1) and at least 10,000 average views, found in the last 6 months. Good for spotting rising creators.

```bash
SIX_MONTHS_AGO=$(date -u -d "6 months ago" +%Y-%m-%dT00:00:00Z 2>/dev/null || date -u -v-6m +%Y-%m-%dT00:00:00Z)
curl -s "https://public-api.tubelab.net/v1/search/channels?avgViewsToSubscribersRatioFrom=1&averageViewsFrom=10000&subscribersFrom=100&publishedAtFrom=$SIX_MONTHS_AGO&language=en&language=de&language=fr&excludeNiche=music&excludeNiche=song&excludeNiche=lofi&excludeNiche=movies&sortBy=foundAt&size=20" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

### Faceless viral videos

AI-classified faceless videos with positive quality published in the last month. Useful for finding faceless niche ideas.

```bash
ONE_MONTH_AGO=$(date -u -d "1 month ago" +%Y-%m-%dT00:00:00Z 2>/dev/null || date -u -v-1m +%Y-%m-%dT00:00:00Z)
curl -s "https://public-api.tubelab.net/v1/search/outliers?type=video&classificationIsFaceless=true&classificationQuality=positive&publishedAtFrom=$ONE_MONTH_AGO&size=20" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

### High authenticity videos

Videos classified as positive quality by AI. Filters out low-effort and spammy content.

```bash
curl -s "https://public-api.tubelab.net/v1/search/outliers?type=video&classificationQuality=positive&size=20" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

### Monetized channel videos

Outlier videos from channels with AdSense enabled. Useful for researching niches that generate ad revenue.

```bash
curl -s "https://public-api.tubelab.net/v1/search/outliers?type=video&channelMonetizationAdsense=true&size=20" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY"
```

## Error Handling

All errors return JSON with an `error` object:

| Status | Meaning | Response |
| --- | --- | --- |
| 400 | Validation error | `{ "error": { "errors": [{ "code": "...", "message": "...", "path": ["param"] }] } }` |
| 401 | Invalid/missing API key | `{ "error": { "message": "Unauthorized" }, "status": "error" }` |
| 402 | Insufficient credits | `{ "error": { "message": "Insufficient credits" }, "status": "error" }` |
| 429 | Rate limited | `{ "error": { "message": "Rate limit exceeded", "rateLimit": { "limit": 10, "current": 11, "remaining": 0 } } }` |

## jq Recipes

```bash
# Profitable channels: extract name, subs, revenue, and views
ONE_YEAR_AGO=$(date -u -d "1 year ago" +%Y-%m-%dT00:00:00Z 2>/dev/null || date -u -v-1y +%Y-%m-%dT00:00:00Z)
curl -s "https://public-api.tubelab.net/v1/search/channels?monetizationAdsense=true&revenueMonthlyEstimationFrom=1000&subscribersFrom=1000&publishedAtFrom=$ONE_YEAR_AGO&sortBy=foundAt&size=10" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY" | jq '[.hits[] | {title: .snippet.title, handle: .snippet.handle, subs: .statistics.subscribers, avgViews: .statistics.averageViews}]'

# Trending channels: list titles with engagement ratio
SIX_MONTHS_AGO=$(date -u -d "6 months ago" +%Y-%m-%dT00:00:00Z 2>/dev/null || date -u -v-6m +%Y-%m-%dT00:00:00Z)
curl -s "https://public-api.tubelab.net/v1/search/channels?avgViewsToSubscribersRatioFrom=1&averageViewsFrom=10000&subscribersFrom=100&publishedAtFrom=$SIX_MONTHS_AGO&sortBy=foundAt&size=10" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY" | jq '[.hits[] | {title: .snippet.title, subs: .statistics.subscribers, ratio: .statistics.avgViewsToSubscribersRatio}]'

# Faceless viral videos: extract title, views, and z-score
ONE_MONTH_AGO=$(date -u -d "1 month ago" +%Y-%m-%dT00:00:00Z 2>/dev/null || date -u -v-1m +%Y-%m-%dT00:00:00Z)
curl -s "https://public-api.tubelab.net/v1/search/outliers?type=video&classificationIsFaceless=true&classificationQuality=positive&publishedAtFrom=$ONE_MONTH_AGO&size=10" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY" | jq '[.hits[] | {title: .snippet.title, views: .statistics.viewCount, zScore: .statistics.zScore, channel: .snippet.channelTitle}]'

# High-quality outliers: get top videos by views
curl -s "https://public-api.tubelab.net/v1/search/outliers?type=video&classificationQuality=positive&sortBy=views&sortOrder=desc&size=10" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY" | jq '[.hits[] | {title: .snippet.title, views: .statistics.viewCount, channel: .snippet.channelTitle}]'

# Get full transcript as plain text
curl -s "https://public-api.tubelab.net/v1/video/transcript/SVeXR66hcIg" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY" | jq -r '.items[0].transcript'

# Poll scan status until complete
curl -s "https://public-api.tubelab.net/v1/scan/2a5e56f5-75f3-4f01-ac85-6e796f5cde87" \
  -H "Authorization: Api-Key $TUBELAB_API_KEY" | jq '{status: .status, endedAt: .endedAt}'
```
