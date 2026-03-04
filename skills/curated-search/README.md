# Curated Search

A domain-restricted search skill for OpenClaw that indexes only trusted technical documentation. Replace generic web search with authoritative, spam-free results.

[![Tests](https://github.com/openclaw/curated-search/actions/workflows/test.yml/badge.svg)](https://github.com/openclaw/curated-search/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Whitelist-based crawling** — only trusted domains (MDN, Python docs, Node.js, etc.)
- **Respects robots.txt** — polite crawling with configurable delay
- **BM25 full-text search** — powered by MiniSearch (pure JavaScript, no DB)
- **No persistent server** — CLI tool invoked per query (simple, reliable)
- **Works offline** — after initial crawl, no external calls needed
- **OpenClaw native** — seamless agent integration

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Edit config.yaml (optional — customize domains/ seeds)
# 3. Build the index (crawl whitelisted sites)
npm run crawl

# 4. Test search
node scripts/search.js --query="python tutorial" --limit=5
```

Expected output (JSON):
```json
[
  {
    "title": "Python Tutorial",
    "url": "https://docs.python.org/3/tutorial/",
    "snippet": "Python is an easy to learn...",
    "domain": "docs.python.org",
    "score": 0.87,
    "crawled_at": 1707712345678
  }
]
```

**Real example from a populated index:**
```json
{
  "query": "python",
  "total": 56,
  "results": [
    {
      "title": "What’s new in Python 3.14 — Python 3.14.3 documentation",
      "url": "https://docs.python.org/whatsnew/3.14.html",
      "domain": "docs.python.org",
      "snippet": "What’s new in Python 3.14¶ Editors: Adam Turner and Hugo van Kemenade This article explains the new features in Python 3.14...",
      "score": 8.809,
      "crawled_at": 1771044132217
    }
  ],
  "took_ms": 4,
  "limit": 5,
  "offset": 0
}
```

## OpenClaw Integration

1. Copy/link skill to OpenClaw skills directory:
   ```bash
   # Already in workspace: ~/.openclaw/workspace/skills/curated-search/
   # Ensure OpenClaw is configured to load workspace skills
   ```

2. Reload OpenClaw:
   ```bash
   openclaw gateway restart
   ```

3. Verify tool is discovered:
   ```bash
   openclaw tools list | grep curated
   # Should show: curated-search.search
   ```

4. Use in chat:
   ```
   User: search CuratedSearch for "python async await"
   Agent: [calls tool and returns results]
   ```

## Configuration

Edit `config.yaml` to customize behavior:

```yaml
# ====================
# DOMAIN WHITELIST
# ====================
# Only these domains will be crawled and indexed.
domains:
  - docs.python.org
  - developer.mozilla.org
  - nodejs.org
  - man7.org
  - en.wikipedia.org
  - github.com
  - docs.openclaw.ai
  # ... add more

# ====================
# SEED URLS
# ====================
# Starting points for crawling. Use specific docs pages not just homepages.
seeds:
  - "https://docs.python.org/3/tutorial/"
  - "https://developer.mozilla.org/en-US/docs/Web/JavaScript"
  - "https://nodejs.org/api/"

# ====================
# CRAWL SETTINGS
# ====================
crawl:
  depth: 2                  # 0 = seeds only, 1 = immediate links, 2 = recommended
  delay: 1000               # milliseconds between requests to same host (polite)
  timeout: 30               # HTTP request timeout (seconds)
  user_agent: "CuratedSearch/1.0 (OpenClaw Bot; +https://github.com/openclaw/openclaw)"
  max_documents: 10000      # stop after indexing this many pages
  concurrent_requests: 1    # keep 1 for politeness
  respect_robots: true      # obey robots.txt

# ====================
# SEARCH SETTINGS
# ====================
search:
  default_limit: 10
  max_limit: 100
  min_score: 0.0

# ====================
# LOGGING
# ====================
logging:
  level: "info"             # debug, info, warn, error
  file: "logs/curated-search.log"
  console: true
```

After editing `config.yaml`, the **search tool** picks up changes immediately. The **crawler** (`npm run crawl`) uses the config on next run.

## How It Works

```
OpenClaw Agent
    ↓ (tool call)
node scripts/search.js --query="python" --limit=5
    ↓
loads data/index.json (MiniSearch)
    ↓
BM25 search with optional filters (domain, minScore)
    ↓
returns JSON array of results
```

The crawler (`npm run crawl`) populates the index:

```
seeds → fetch → extract content → index → save → repeat until depth or max_documents
```

No server is running between queries — each tool invocation loads the index fresh (fast, <500ms on warm cache).

## Performance

- Index load (cold): ~200–500ms (10k docs)
- Search latency: <50ms (10k docs)
- Index size: ~100–200 KB per 1k documents
- Crawl time: depends on delay and depth (e.g., 10k docs @ delay=1s ≈ 3 hours)

## Troubleshooting

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| "Index not found" | No `data/index.json` | Run `npm run crawl` first |
| Empty results | Index doesn't contain query terms | Check domain whitelist, seeds, increase depth |
| Slow first query | Cold OS cache | Subsequent queries faster; consider warm-up |
| Tool not listed | Skill not in OpenClaw path or `skill.yaml` syntax error | `openclaw gateway restart`, check `skill.yaml` |
| Permission denied | OpenClaw user can't read skill dir | `chmod o+rx` skill directory or run OpenClaw as same user |

## Development

### Run Tests

```bash
# Install dev dependencies first
npm install

# Unit + integration (fast)
npm test

# Unit with coverage
npm run test:unit

# Integration only
npm run test:integration

# End-to-end (requires crawler implemented)
npm run test:e2e

# Benchmarks
npm run bench
```

### Project Structure

```
curated-search/
├── config.yaml           # Domain whitelist, crawl & search settings
├── skill.yaml            # OpenClaw skill manifest
├── package.json
├── README.md
├── SKILL.md              # Agent reference
├── PLAN.md               # Build plan (phases)
├── specs/                # Detailed technical specs
│   ├── PHASE-3-1-URL-DISCOVERY.md
│   ├── PHASE-3-2-CONTENT-EXTRACTION.md
│   ├── PHASE-3-3-POLITENESS-CONTROLS.md
│   ├── PHASE-3-4-ORCHESTRATION.md
│   ├── PHASE-4-SEARCH-TOOL-INTERFACE.md
│   ├── PHASE-5-OPENCLAW-INTEGRATION.md
│   ├── PHASE-6-TESTING-VALIDATION.md
│   ├── PHASE-7-DOCUMENTATION.md
│   └── PHASE-8-DEPLOYMENT-OPERATIONS.md
├── scripts/
│   └── search.js         # CLI tool (OpenClaw invokes this)
├── src/
│   ├── indexer.js        # MiniSearch wrapper, persistence
│   ├── crawler.js        # Domain-restricted crawler with politeness
│   ├── content-extractor.js
│   ├── url-normalizer.js
│   └── rate-limiter.js
├── test/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── benchmarks/
├── data/
│   ├── index.json        # Search index (MiniSearch)
│   ├── index-docs.json   # Full documents (persisted)
│   └── crawl-state.json  # Crawler state for resume
└── logs/
    └── curated-search.log
```

## Adding New Domains

1. Edit `config.yaml`: add domain to `domains:` list (e.g., `- react.dev`)
2. Add corresponding seed URLs under `seeds:` (e.g., `"https://react.dev/learn"`)
3. Re-run crawl: `npm run crawl`

## License

MIT — see `LICENSE` file.

## Credits

- Built for OpenClaw
- Full-text search by [MiniSearch](https://github.com/lucaong/minisearch)
- Design: whitelist curation as the product
