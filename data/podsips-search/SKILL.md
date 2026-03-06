---
name: podsips-search
description: Search podcast transcripts and retrieve episode data via the PodSips API. Use when user asks to "search podcasts", "find podcast clips", "get transcript", "look up episode", "search what was said on", or needs podcast content for research, summarization, or citation. Requires PODSIPS_API_KEY environment variable.
version: 1.2.0
author: PodSips
homepage: https://developer.podsips.com
metadata: { "clawdbot": { "requires": { "env": ["PODSIPS_API_KEY"], "bins": ["curl", "jq"] }, "primaryEnv": "PODSIPS_API_KEY" } }
---

# PodSips Podcast Search API

Search across indexed podcast transcripts using semantic search, retrieve full transcripts, get episode and series metadata, and request new podcasts to be added.

## Important

- All requests require the `PODSIPS_API_KEY` environment variable. Pass it as `Authorization: Bearer $PODSIPS_API_KEY`.
- Base URL: `https://api.podsips.com/public/v1`
- All responses are JSON.
- Credit costs are deducted per request. Most endpoints cost 1 credit. Full transcripts cost 5 credits. Podcast requests are free.
- If the user does not have a PodSips API key, follow the steps in the **Getting an API Key** section below to walk them through setup.

## Getting an API Key

Before using any endpoint, the user needs a PodSips API key. If `PODSIPS_API_KEY` is not set, walk the user through these steps:

1. Go to **https://developer.podsips.com**
2. Click **Sign in with Google** to create an account (this is the only sign-in method).
3. After signing in, they will be prompted to register a developer account if they don't have one yet. Complete the registration form.
4. Once on the dashboard, navigate to the **API Keys** section.
5. Click **Generate API Key**. Copy the key — it is only shown once.
6. Set the key as an environment variable so this skill can use it:
   ```bash
   export PODSIPS_API_KEY="ps_live_..."
   ```

Every new account starts on the **Free tier** with 100 credits per month. If the user needs more credits, they can upgrade their plan on the dashboard at https://developer.podsips.com.

## Prerequisites

Verify the API key is set before making any requests:

```bash
test -n "$PODSIPS_API_KEY" && echo "API key is set" || echo "ERROR: Set PODSIPS_API_KEY first. See the 'Getting an API Key' section above."
```

## Instructions

### 1. Search podcast transcripts

Use semantic search to find relevant podcast clips matching a query. This is the primary endpoint.

```bash
curl -s -H "Authorization: Bearer $PODSIPS_API_KEY" \
  "https://api.podsips.com/public/v1/search?q=artificial+intelligence+ethics&top_k=5" | jq .
```

**Parameters:**
- `q` (required) — Search query text
- `top_k` (optional, default 10) — Number of results to return
- `series_id` (optional) — Filter to a specific podcast series UUID
- `episode_id` (optional) — Filter to a specific episode UUID
- `speakers` (optional) — Filter by speaker name

**Response shape:**
```json
{
  "groups": [
    {
      "episode": {
        "uuid": "episode-uuid",
        "name": "Episode Title",
        "description": "Episode description...",
        "date_published": "2025-01-15T00:00:00Z",
        "podcast_uuid": "series-uuid",
        "speakers": ["Host Name", "Guest Name"]
      },
      "podcast": {
        "uuid": "series-uuid",
        "name": "Series Title",
        "description": "Series description..."
      },
      "chunks": [
        {
          "uuid": "chunk-uuid",
          "text": "The transcript text of the matching segment...",
          "start_time": 120.5,
          "end_time": 185.3,
          "duration": 64.8,
          "episode_uuid": "episode-uuid",
          "podcast_uuid": "series-uuid",
          "speakers": ["Speaker Name"],
          "timestamped_podcast_link": "podsips://episode-uuid?t=120",
          "episode_image_url": "https://...",
          "podcast_image_url": "https://..."
        }
      ]
    }
  ],
  "chunks": [
    {
      "uuid": "chunk-uuid",
      "text": "...",
      "start_time": 120.5,
      "end_time": 185.3,
      "duration": 64.8,
      "episode_uuid": "episode-uuid",
      "podcast_uuid": "series-uuid",
      "speakers": ["Speaker Name"],
      "timestamped_podcast_link": "podsips://episode-uuid?t=120",
      "episode_image_url": "https://...",
      "podcast_image_url": "https://..."
    }
  ],
  "meta": {
    "total_chunks": 3,
    "episodes_represented": 3,
    "query": "artificial intelligence ethics"
  }
}
```

Results are returned in two formats: `groups` organizes chunks by episode (each group contains an `episode` object, a `podcast` object, and the matching `chunks`), while the top-level `chunks` array is a flat list of all matching chunks across episodes. The `meta` object provides summary information about the results.

Each chunk includes the transcript text, timestamps in seconds (`start_time`, `end_time`, `duration`), speaker names, and image URLs. Use `start_time` and `end_time` to reference specific moments.

**Speaker tags in transcript text:** Chunk `text` fields may contain raw speaker tags inline such as `<<SPEAKER_00>>`, `<<SPEAKER_01>>`, or `<<UNKNOWN>>`. Replace these with the actual speaker names from the `speakers` array, or strip them before displaying to the user.

**`timestamped_podcast_link`:** This is a `podsips://` deep link that opens the PodSips app at the specific episode and timestamp. It is intended for mobile app deep linking. If the user is not using the PodSips app, you can ignore this field and use `start_time` directly for timestamp references.

**Cost:** 1 credit per request.

### 2. Search for a podcast series

Search for a podcast series by name or description. Use this when the user asks about a specific podcast to check if it exists in the database before falling back to a podcast request.

```bash
curl -s -H "Authorization: Bearer $PODSIPS_API_KEY" \
  "https://api.podsips.com/public/v1/series/search?q=Y+Combinator&limit=5" | jq .
```

**Parameters:**
- `q` (required) — Search query text (searches series name and description)
- `genre` (optional) — Filter by genre (case-insensitive)
- `limit` (optional, default 20, max 100) — Number of results to return
- `offset` (optional, default 0) — Pagination offset

**Response shape:**
```json
[
  {
    "id": "uuid",
    "name": "Y Combinator Startup Podcast",
    "description": "We help founders make something people want...",
    "image_url": "https://...",
    "genre": "technology",
    "episode_count": 56
  }
]
```

Returns an empty array if no matching series are found.

**Cost:** 1 credit per request.

### 3. List available podcast series

Browse all podcast series in the database with optional genre filtering and pagination.

```bash
curl -s -H "Authorization: Bearer $PODSIPS_API_KEY" \
  "https://api.podsips.com/public/v1/series?limit=20&offset=0" | jq .
```

**Parameters:**
- `genre` (optional) — Filter by genre
- `limit` (optional) — Number of results
- `offset` (optional) — Pagination offset

**Response shape:**
```json
[
  {
    "id": "uuid",
    "name": "Podcast Name",
    "description": "Description of the podcast",
    "image_url": "https://...",
    "genre": "Technology",
    "episode_count": 42
  }
]
```

**Cost:** 1 credit per request.

### 4. Get series details with episodes

Retrieve a specific series and all its available episodes.

```bash
curl -s -H "Authorization: Bearer $PODSIPS_API_KEY" \
  "https://api.podsips.com/public/v1/series/{series_id}" | jq .
```

Replace `{series_id}` with the UUID from the series list or search results.

**Response shape:**
```json
{
  "id": "uuid",
  "name": "Podcast Name",
  "description": "...",
  "image_url": "https://...",
  "genre": "Technology",
  "rss_url": "https://...",
  "website_url": "https://...",
  "episodes": [
    {
      "id": "uuid",
      "name": "Episode Title",
      "description": "...",
      "date_published": "2025-01-15T00:00:00Z",
      "duration": 3600,
      "image_url": "https://...",
      "series_id": "uuid",
      "speakers": ["Host Name", "Guest Name"]
    }
  ]
}
```

Only episodes with complete transcripts are included.

**Cost:** 1 credit per request.

### 5. Get episode details

Retrieve metadata and speaker information for a specific episode.

```bash
curl -s -H "Authorization: Bearer $PODSIPS_API_KEY" \
  "https://api.podsips.com/public/v1/episodes/{episode_id}" | jq .
```

**Response shape:**
```json
{
  "id": "uuid",
  "name": "Episode Title",
  "description": "...",
  "date_published": "2025-01-15T00:00:00Z",
  "duration": 3600,
  "audio_url": "https://...",
  "image_url": "https://...",
  "series_id": "uuid",
  "series_name": "Podcast Name",
  "speakers": [
    {"generic_label": "Speaker 1", "identity": "Dr. Jane Smith"},
    {"generic_label": "Speaker 2", "identity": "John Doe"}
  ]
}
```

**Cost:** 1 credit per request.

### 6. Get transcript context around a timestamp

Retrieve transcript text around a specific moment in an episode. Useful for expanding context around a search result.

```bash
curl -s -H "Authorization: Bearer $PODSIPS_API_KEY" \
  "https://api.podsips.com/public/v1/episodes/{episode_id}/context?position=120&pre_seconds=60&post_seconds=15" | jq .
```

**Parameters:**
- `position` (required) — Timestamp in seconds
- `pre_seconds` (optional, default 60) — Seconds of context before the position
- `post_seconds` (optional, default 15) — Seconds of context after the position

**Response shape:**
```json
{
  "episode_id": "uuid",
  "position": 120.0,
  "pre_context_seconds": 60,
  "post_context_seconds": 15,
  "pre_context": [
    {"speaker": "Dr. Jane Smith", "text": "What they said before...", "start": 62.1, "end": 68.5}
  ],
  "post_context": [
    {"speaker": "John Doe", "text": "What they said after...", "start": 120.5, "end": 134.2}
  ]
}
```

**Cost:** 1 credit per request.

### 7. Get full episode transcript

Retrieve the complete transcript for an episode. All chunks are returned in chronological order.

```bash
curl -s -H "Authorization: Bearer $PODSIPS_API_KEY" \
  "https://api.podsips.com/public/v1/episodes/{episode_id}/transcript" | jq .
```

**Response shape:**
```json
{
  "episode_id": "uuid",
  "episode_name": "Episode Title",
  "total_chunks": 55,
  "chunks": [
    {
      "chunk_index": 0,
      "text": "Welcome to the show...",
      "start_time": 0.0,
      "end_time": 65.2,
      "word_count": 180,
      "speakers": ["Host Name"]
    }
  ]
}
```

**Cost:** 5 credits per request (higher cost due to large data volume).

### 8. Request a missing podcast

If the user's desired podcast is not in the database, submit a request to add it. This is free and does not consume credits.

```bash
curl -s -X POST -H "Authorization: Bearer $PODSIPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"podcast_name": "The Podcast Name", "rss_url": "https://feeds.example.com/podcast.xml"}' \
  "https://api.podsips.com/public/v1/podcast-requests" | jq .
```

**Parameters:**
- `podcast_name` (required) — Name of the podcast to add
- `rss_url` (optional) — RSS feed URL, if known

**Response:** Returns a request ID and status. Processing typically takes 24-48 hours.

**Cost:** Free (0 credits).

### 9. Check podcast request status

Check whether a previously submitted podcast request has been processed.

```bash
curl -s -H "Authorization: Bearer $PODSIPS_API_KEY" \
  "https://api.podsips.com/public/v1/podcast-requests/{request_id}" | jq .
```

**Response shape:**
```json
{
  "id": "uuid",
  "podcast_name": "The Podcast Name",
  "rss_url": "https://...",
  "status": "pending",
  "resulting_series_id": null,
  "created_at": "2025-06-01T12:00:00Z",
  "updated_at": "2025-06-01T12:00:00Z"
}
```

Status values: `pending`, `processing`, `complete`, `rejected`. When `status` is `complete`, `resulting_series_id` contains the UUID of the new series.

**Cost:** Free (0 credits).

## Recommended Workflow

When a user asks you to find information from podcasts:

1. **Search first.** Use the search endpoint with the user's query. If results are relevant, present the transcript excerpts with episode names, speaker names, and timestamps.

2. **Expand context if needed.** If a search result is interesting but the user wants more context around that moment, use the context endpoint with the `start_time` from the search result as the `position`.

3. **Get the full transcript when appropriate.** If the user wants a complete transcript or wants to analyze an entire episode, use the transcript endpoint. Note this costs 5 credits.

4. **Handle missing podcasts.** If search returns no results and the user is asking about a specific podcast:
   a. Use `GET /series/search?q=...` to check if the podcast exists in the database by name.
   b. If found, use the series UUID to filter transcript search results with `series_id`.
   c. If not found, use `POST /podcast-requests` to submit it.
   d. Tell the user: "This podcast is not in the PodSips database yet. I have submitted a request to add it. Processing typically takes 24-48 hours. No credits were used for this request."
   e. If the user asks again later, check the request status with `GET /podcast-requests/{id}`.

5. **Cite your sources.** When presenting information from podcast transcripts, include the episode name, series name, speaker, and timestamp so the user can verify or listen to the original audio.

## Error Handling

**HTTP 401 — Invalid or missing API key.** Verify `PODSIPS_API_KEY` is set and valid. The user may need to generate a new key at https://developer.podsips.com.

**HTTP 402 — Insufficient credits.** The developer account has run out of credits for the current billing cycle. The user needs to upgrade their plan or wait for the next billing cycle.

**HTTP 429 — Rate limit exceeded.** Too many requests in the current time window. Wait briefly and retry. Rate limits vary by subscription tier.

**HTTP 404 — Resource not found.** The series, episode, or podcast request ID does not exist.

## Credit Cost Summary

| Endpoint | Credits |
|----------|---------|
| Search | 1 |
| Series search | 1 |
| List series | 1 |
| Series detail | 1 |
| Episode detail | 1 |
| Transcript context | 1 |
| Full transcript | 5 |
| Submit podcast request | 0 |
| Check request status | 0 |
