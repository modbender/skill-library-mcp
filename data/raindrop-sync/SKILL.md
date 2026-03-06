---
name: raindrop
description: Sync and process bookmarks from Raindrop.io. Use when fetching new bookmarks, analyzing saved content, or syncing bookmarks to knowledge base. Triggers on "raindrop", "bookmarks", "sync bookmarks", "new saves".
---

# Raindrop Bookmark Sync

Fetch bookmarks from Raindrop.io API and process them for knowledge base integration.

## Setup

1. Get API token from https://app.raindrop.io/settings/integrations
2. Create test token (read-only is fine)
3. Save to `.secrets/raindrop.env`:
   ```
   RAINDROP_TOKEN=your_token_here
   ```

## Usage

### Fetch new bookmarks
```bash
source .secrets/raindrop.env
python3 skills/raindrop/scripts/fetch.py --since 24h
```

### Fetch from specific collection
```bash
python3 skills/raindrop/scripts/fetch.py --collection 12345678
```

### Process and add to knowledge base
```bash
python3 skills/raindrop/scripts/fetch.py --since 24h --output /tmp/raindrop-new.json
# Then process each item with web_fetch and add to memory/knowledge-base.md
```

## API Reference

- **Base URL:** `https://api.raindrop.io/rest/v1`
- **Auth:** Bearer token in header
- **Rate limit:** 120 req/min

### Key Endpoints
- `GET /raindrops/{collectionId}` — List bookmarks (use `0` for all)
- `GET /collections` — List collections
- `GET /raindrop/{id}` — Single bookmark details

### Bookmark Object
```json
{
  "_id": 123456,
  "title": "Article Title",
  "link": "https://example.com/article",
  "excerpt": "Short description...",
  "tags": ["tag1", "tag2"],
  "created": "2026-02-15T10:00:00Z",
  "collection": {"$id": 12345678}
}
```

## Workflow

1. **Fetch** — Get new bookmarks since last sync
2. **Filter** — Skip already-processed URLs (check `memory/kb-index.json`)
3. **Extract** — Use `web_fetch` to get content
4. **Analyze** — Summarize and tag
5. **Store** — Append to `memory/knowledge-base.md`
6. **Update index** — Add URL to `memory/kb-index.json`

## Cron Integration

Add to heartbeat or cron for automatic sync:
```
每天检查一次 Raindrop 新书签，处理后存入知识库
```
