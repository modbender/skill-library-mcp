---
name: brave-rotator
description: >
  Brave Search API with automatic key rotation across multiple API keys to maximize free tier limits
  (2000 req/month per key). Use when performing web, news, or image searches via Brave Search API,
  especially when multiple API keys are available and you want to avoid rate limits.
  Triggers on web search requests, news lookups, image searches, any task requiring
  Brave Search API calls with key rotation or fallback.
---

# Brave Rotator

Multi-key Brave Search with automatic round-robin rotation and rate-limit fallback.

## Setup

Set env var with comma-separated keys:
```bash
export BRAVE_API_KEYS=key1,key2,key3
```

Optionally set state file path (default: `~/.brave_key_state.json`):
```bash
export BRAVE_KEY_STATE_FILE=/path/to/state.json
```

## Script: `scripts/brave_search.py`

Run directly or import as module.

### CLI usage
```bash
python3 brave_search.py "your query" [--count 5] [--type web|news|image] [--country us] [--lang en] [--json]
```

### Import usage
```python
import sys, os
sys.path.insert(0, "path/to/skill/scripts")
from brave_search import search, format_results

data, used_key, key_idx = search("your query", count=5, search_type="web")
results = format_results(data, "web")
# results = [{"title": ..., "url": ..., "snippet": ...}, ...]
```

## Rotation Logic

- Maintains state in `~/.brave_key_state.json`
- Round-robin across all keys
- On HTTP 429/403: blocks key for 60s, retries with next key
- All keys exhausted: uses least recently blocked key

## Key State Inspection

```bash
cat ~/.brave_key_state.json
```

Shows per-key request count, last success, and blocked_until timestamps.

## Search Types

| Type  | Endpoint              | Result fields                        |
|-------|-----------------------|--------------------------------------|
| web   | /web/search           | title, url, snippet                  |
| news  | /news/search          | title, url, snippet, age             |
| image | /images/search        | title, url, thumbnail                |

## Notes

- Free plan: 2000 req/month/key, 1 req/sec
- With N keys: effectively N×2000 req/month
- See `references/brave-api.md` for full API params and plan details
