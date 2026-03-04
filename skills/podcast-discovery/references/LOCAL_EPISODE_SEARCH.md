# Local Episode Search Tooling

Use `scripts/search_feed_episodes.py` for host-side feed parsing and compact results.

## Install

```bash
python -m pip install -r scripts/requirements.txt
```

## Commands

### 1) Search relevant episodes

```bash
python scripts/search_feed_episodes.py --mode search --rss-url "https://feeds.feedburner.com/radiolab" --query "space stories" --limit 5
```

Optional semantic rerank:

```bash
python scripts/search_feed_episodes.py --mode search --rss-url "https://feeds.feedburner.com/radiolab" --query "space stories" --limit 5 --semantic
```

Compact JSON schema:

- top-level: `ok`, `mode`, `rssUrl`, `query`, `semanticUsed`, `candidateCount`, `candidates`
- candidates: `guid`, `title`, `pubDate`, `fallbackLink`, `score`

Example:

```json
{
  "ok": true,
  "mode": "search",
  "rssUrl": "https://feeds.feedburner.com/radiolab",
  "query": "space stories",
  "semanticUsed": false,
  "candidateCount": 2,
  "candidates": [
    {
      "guid": "abc123",
      "title": "The Dark Side of the Sky",
      "pubDate": "2024-03-01T00:00:00Z",
      "fallbackLink": "https://radiolab.org/episode/the-dark-side-of-the-sky",
      "score": 88.1
    }
  ]
}
```

Ambiguity guidance:

- Auto-select when top score is clearly stronger than second place.
- Ask one disambiguation question when top results are near-tied.

### 2) Get newest N items

```bash
python scripts/search_feed_episodes.py --mode newest --rss-url "https://feeds.feedburner.com/radiolab" --limit 10
```

Compact JSON schema:

- top-level: `ok`, `mode`, `rssUrl`, `count`, `items`
- items: `guid`, `title`, `pubDate`, `fallbackLink`

### 3) Get feed overview metadata

```bash
python scripts/search_feed_episodes.py --mode overview --rss-url "https://feeds.feedburner.com/radiolab"
```

Compact JSON schema:

- `ok`, `mode`, `rssUrl`, `feedTitle`, `feedDescriptionShort`, `author`, `language`, `lastBuildDate`, `itemCount`

## Error output

Failures return compact JSON:

```json
{
  "ok": false,
  "mode": "search",
  "rssUrl": "https://example.com/feed.xml",
  "error": {
    "type": "network_error",
    "message": "..."
  }
}
```

Possible `error.type` values include:

- `invalid_input`
- `network_error`
- `fetch_error`
- `parse_error`
- `empty_feed`

## Troubleshooting

- If `semanticUsed` is `false` while `--semantic` was requested, optional semantic dependencies are unavailable; fuzzy ranking still works.
- If a feed has malformed dates, `pubDate` may be empty for some items, but GUID/link extraction still proceeds.
- If the feed has no usable items, use `overview` to verify feed-level metadata and source validity.
