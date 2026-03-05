# PodSips Public API — Detailed Reference

## Base URL

```
https://api.podsips.com/public/v1
```

## Authentication

Every request must include the API key in the Authorization header:

```
Authorization: Bearer <your-api-key>
```

API keys are generated at https://developer.podsips.com after creating a developer account. Each key has a prefix (first 8 characters) for identification. Keys can be revoked but not recovered — store them securely.

## Subscription Tiers

**Free** — 100 credits per billing cycle, 60 requests/hour, $0/month
**Starter** — 5,000 credits per billing cycle, 600 requests/hour, $4.99/month
**Pro** — 50,000 credits per billing cycle, 6,000 requests/hour, $49/month
**Enterprise** — 500,000 credits per billing cycle, 6,000 requests/hour, $199/month

Credits reset each billing cycle. Rate limits are per API key.

## OpenAPI Schema

The machine-readable OpenAPI 3.0 schema is available at:

```
GET /public/v1/schema/
```

This can be used for auto-generating client libraries or importing into API tools.

## Detailed Endpoint Reference

### GET /public/v1/search

Performs semantic search across all indexed podcast transcripts. The query is embedded using OpenAI's text-embedding-3-small model and compared against transcript chunk vectors stored in Pinecone.

**Query Parameters:**

- `q` (string, required) — The search query. Natural language works best. Example: "the future of renewable energy"
- `top_k` (integer, optional, default 10) — Number of results to return. Range: 1-50.
- `series_id` (UUID, optional) — Restrict search to episodes within a specific series.
- `episode_id` (UUID, optional) — Restrict search to chunks within a specific episode.
- `speakers` (string, optional) — Filter by speaker name.

**Response:** Results are grouped by episode. Each group contains an array of matching transcript chunks with relevance scores. Chunks include the full text, timestamps, speaker names, and word count.

**Tips:**
- Use natural, conversational queries rather than keyword-based searches for best results.
- Combine with `series_id` to search within a specific podcast.
- The `score` field ranges from 0 to 1, where higher values indicate stronger semantic matches.
- Use `start_time` from results as the `position` parameter for the context endpoint to expand surrounding text.

---

### GET /public/v1/series

Lists all podcast series in the database. Only series with at least one episode that has a complete transcript are included.

**Query Parameters:**

- `genre` (string, optional) — Filter by genre. Example: "Technology", "Business", "Science"
- `limit` (integer, optional) — Number of series to return.
- `offset` (integer, optional) — Skip this many series (for pagination).

**Response:** Array of series objects with `id`, `name`, `description`, `image_url`, `genre`, and `episode_count`.

---

### GET /public/v1/series/{series_id}

Returns details for a specific series including all its complete episodes.

**Path Parameters:**

- `series_id` (UUID, required) — The series UUID.

**Response:** Series metadata including `rss_url`, `website_url`, and an `episodes` array. Each episode includes `id`, `name`, `description`, `date_published`, `duration` (in seconds), `image_url`, `series_id`, and `speakers` (array of speaker identity strings).

---

### GET /public/v1/episodes/{episode_id}

Returns full metadata for a specific episode including speaker details.

**Path Parameters:**

- `episode_id` (UUID, required) — The episode UUID.

**Response:** Episode metadata including `audio_url`, `series_id`, `series_name`, and `speakers` array. Each speaker object has `generic_label` (e.g., "Speaker 1") and `identity` (e.g., "Dr. Jane Smith").

---

### GET /public/v1/episodes/{episode_id}/context

Returns transcript text around a specific timestamp. Useful for expanding context around search results.

**Path Parameters:**

- `episode_id` (UUID, required) — The episode UUID.

**Query Parameters:**

- `position` (float, required) — The timestamp in seconds to center the context around.
- `pre_seconds` (integer, optional, default 60) — How many seconds of transcript to include before the position.
- `post_seconds` (integer, optional, default 15) — How many seconds of transcript to include after the position.

**Response:** Two arrays: `pre_context` (utterances before the position) and `post_context` (utterances after). Each utterance has `speaker`, `text`, `start`, and `end` timestamps.

---

### GET /public/v1/episodes/{episode_id}/transcript

Returns the complete transcript for an episode as an array of chronological chunks.

**Path Parameters:**

- `episode_id` (UUID, required) — The episode UUID.

**Response:** Contains `episode_id`, `episode_name`, `total_chunks`, and a `chunks` array. Each chunk has `chunk_index`, `text`, `start_time`, `end_time`, `word_count`, and `speakers`.

A typical 1-hour episode has 50-60 chunks. Each chunk covers approximately 65 seconds of audio.

---

### POST /public/v1/podcast-requests

Submit a request to add a new podcast to the PodSips database. This endpoint is free.

**Request Body (JSON):**

- `podcast_name` (string, required) — The name of the podcast.
- `rss_url` (string, optional) — The RSS feed URL if known. Providing this speeds up processing.

**Response:** Returns the created request with an `id` (UUID), `status` ("pending"), and timestamps.

**Processing:** The PodSips team receives a Slack notification and reviews the request. If approved, the podcast is added to the processing pipeline. New episodes are transcribed, chunked, and embedded automatically. Typical turnaround is 24-48 hours.

---

### GET /public/v1/podcast-requests/{request_id}

Check the status of a previously submitted podcast request.

**Path Parameters:**

- `request_id` (UUID, required) — The request UUID returned when the request was created.

**Response:** Request details including `status` and `resulting_series_id`. Status values:

- `pending` — Waiting for review
- `processing` — Approved and being processed
- `complete` — Done. `resulting_series_id` contains the UUID of the new series.
- `rejected` — The request was not approved.

## Error Response Format

All error responses follow this shape:

```json
{
  "detail": "Human-readable error message"
}
```

HTTP status codes:
- 400 — Bad request (invalid parameters)
- 401 — Unauthorized (invalid or missing API key)
- 402 — Payment required (insufficient credits)
- 404 — Not found (resource does not exist)
- 429 — Too many requests (rate limit exceeded)
- 500 — Internal server error
