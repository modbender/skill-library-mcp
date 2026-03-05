# Curated Search Skill

## Summary
Domain-restricted full-text search over a curated whitelist of technical documentation (MDN, Python docs, etc.). Provides clean, authoritative results without web spam.

## Tool: curated-search.search

Search the curated index.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `query` | string | yes | — | Search query terms |
| `limit` | number | no | 5 | Maximum results (capped by config.max_limit, typically 100) |
| `domain` | string | no | null | Filter to specific domain (e.g., `docs.python.org`) |
| `min_score` | number | no | 0.0 | Minimum relevance score (0.0–1.0); filters out low-quality matches |
| `offset` | number | no | 0 | Pagination offset (skip first N results) |

### Response

JSON array of result objects:

```json
[
  {
    "title": "Python Tutorial",
    "url": "https://docs.python.org/3/tutorial/",
    "snippet": "Python is an easy to learn, powerful programming language...",
    "domain": "docs.python.org",
    "score": 0.87,
    "crawled_at": 1707712345678
  }
]
```

**Fields:**
- `title` — Document title (cleaned)
- `url` — Source URL (canonical)
- `snippet` — Excerpt (~200 chars) from content
- `domain` — Hostname of source
- `score` — BM25 relevance score (higher is better; not normalized 0–1 but typically 0–1 range)
- `crawled_at` — Unix timestamp when page was crawled

### Example Agent Calls

```
search CuratedSearch for "python tutorial"
search CuratedSearch for "async await" limit=3 domain=developer.mozilla.org
search CuratedSearch for "linux man page" min_score=0.3
```

### Errors

If an error occurs, the tool exits non-zero and prints a JSON error object to stderr, e.g.:

```json
{
  "error": "index_not_found",
  "message": "Search index not found. The index has not been built yet.",
  "suggestion": "Run the crawler first: npm run crawl",
  "details": { "path": "data/index.json" }
}
```

Common error codes:

| Code | Meaning | Suggested Fix |
|------|---------|---------------|
| `config_missing` | Configuration file not found | Specify `--config` path or ensure config.yaml exists |
| `config_invalid` | YAML parsing failed | Check syntax in config.yaml |
| `config_missing_index_path` | `index.path` not set | Add index.path to config |
| `index_not_found` | Index file missing | Run `npm run crawl` to build index |
| `index_corrupted` | Index file incompatible or corrupted | Rebuild index with `npm run crawl` |
| `index_init_failed` | Unexpected index initialization error | Check permissions, reinstall dependencies |
| `missing_query` | No query provided | Provide `--query` argument |
| `query_too_long` | Query exceeds 1000 characters | Shorten the query |
| `limit_exceeded` | Limit > config.max_limit | Use a smaller limit |
| `invalid_domain` | Domain filter malformed | Use format like `docs.python.org` |
| `conflicting_flags` | Mutually exclusive flags used (e.g., `--stats` with `--query`) | Use flags correctly |
| `stats_failed` | Could not retrieve index stats | Ensure index is accessible |
| `search_failed` | Search execution threw an error | Check query and index integrity |

## Configuration

Edit `config.yaml` in the skill directory. Key sections:

- `domains` — whitelist of allowed domains (required)
- `seeds` — starting URLs for crawling
- `crawl` — depth, delay, timeout, max_documents
- `content` — min_content_length, max_content_length
- `index` — path to index files
- `search` — default_limit, max_limit, min_score

See `README.md` for full configuration docs.

## Support

- Full documentation: `README.md`
- Technical specs: `specs/`
- Build plan: `PLAN.md`
- Contributor guide: `CONTRIBUTING.md`
- Issues: Report on GitHub (or via OpenClaw maintainers)
