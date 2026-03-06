---
name: transistor-fm
description: Manage podcasts on Transistor.fm via their API. Use when creating, publishing, updating, or deleting podcast episodes, uploading audio files, listing shows/episodes, checking analytics, or managing private podcast subscribers. Triggers on any Transistor.fm podcast management task.
---

# Transistor.fm Podcast Management

Manage podcasts hosted on Transistor.fm through their REST API.

## Prerequisites

- Transistor.fm API key (from Dashboard → Account)
- Store as environment variable `TRANSISTOR_API_KEY` or retrieve from a secrets manager

## Quick Reference

All requests use base URL `https://api.transistor.fm/v1` with header `x-api-key: <key>`.
Rate limit: 10 requests per 10 seconds.

For full endpoint details, parameters, and response formats, see [references/api.md](references/api.md).

## Core Workflows

### List shows and episodes

```bash
# Get all shows
curl -s "$BASE/shows" -H "x-api-key: $KEY"

# Get episodes for a show
curl -s "$BASE/episodes?show_id=SHOW_ID" -H "x-api-key: $KEY"
```

### Upload audio and create an episode

Three-step process:

```bash
# 1. Get authorized upload URL
UPLOAD=$(curl -s "$BASE/episodes/authorize_upload?filename=episode.mp3" -H "x-api-key: $KEY")
# Extract upload_url and audio_url from response

# 2. Upload the audio file
curl -X PUT -H "Content-Type: audio/mpeg" -T /path/to/episode.mp3 "$UPLOAD_URL"

# 3. Create episode with the audio_url
curl -s "$BASE/episodes" -X POST -H "x-api-key: $KEY" \
  -d "episode[show_id]=SHOW_ID" \
  -d "episode[title]=My Episode" \
  -d "episode[summary]=Short description" \
  -d "episode[audio_url]=$AUDIO_URL"
```

Episode is created as **draft**. Publish separately.

### Publish an episode

```bash
# Publish now
curl -s "$BASE/episodes/EPISODE_ID/publish" -X PATCH -H "x-api-key: $KEY" \
  -d "episode[status]=published"

# Schedule for future
curl -s "$BASE/episodes/EPISODE_ID/publish" -X PATCH -H "x-api-key: $KEY" \
  -d "episode[status]=scheduled" \
  -d "episode[published_at]=2026-03-01 09:00:00"
```

### Check analytics

```bash
# Show-level (last 14 days default)
curl -s "$BASE/analytics/SHOW_ID" -H "x-api-key: $KEY"

# Episode-level
curl -s "$BASE/analytics/episodes/EPISODE_ID" -H "x-api-key: $KEY"

# Custom date range (dd-mm-yyyy)
curl -s "$BASE/analytics/SHOW_ID?start_date=01-01-2026&end_date=31-01-2026" -H "x-api-key: $KEY"
```

## Tips

- Episodes are always created as drafts — publish is a separate step, allowing review before going live
- Use `episode[increment_number]=true` to auto-assign the next episode number
- `episode[description]` supports HTML; `episode[summary]` is plain text
- Audio upload URLs expire in 600 seconds — upload promptly after authorizing
- Use sparse fieldsets to reduce response size: `fields[episode][]=title&fields[episode][]=status`
