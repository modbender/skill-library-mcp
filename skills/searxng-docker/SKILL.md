---
name: searxng
description: Search the web using a local SearXNG instance (privacy-respecting metasearch engine). Use when user asks to search, look something up, "搜索", "搜一下", "查一下", or when web_search returns poor results. Supports categories (news, images, videos, IT, science), time filters, language, and multiple engines (Google, Bing, DuckDuckGo, etc.). No API key needed — fully self-hosted.
---

# SearXNG Search Skill

Search the web using a self-hosted SearXNG instance.

## When to Use

- User asks to search, look something up: "搜索", "搜一下", "查一下", "search for", "look up"
- Need results from multiple engines (Google, Bing, DuckDuckGo, etc.)
- Need news, images, IT/science, or social media search
- `web_search` unavailable or returns poor results

## Deployment

### Quick Start (Docker Compose)

The `docker/` folder in this skill contains a ready-to-use Docker Compose setup. Run it directly — no need to copy files elsewhere.

```bash
# 1. Generate a random secret key
sed -i "s/CHANGE_ME_TO_A_RANDOM_STRING/$(openssl rand -hex 16)/" docker/settings.yml

# 2. Start
docker compose -f docker/docker-compose.yml up -d

# 3. Verify
curl -s "http://127.0.0.1:8888/search?q=test&format=json" | python3 -m json.tool | head -5
```

### Configuration

Edit files in the `docker/` folder:

- **Port**: Default `127.0.0.1:8888` → change in `docker-compose.yml` ports section
- **Engines**: Edit `settings.yml` engines list (Google, Bing, DuckDuckGo, Wikipedia, GitHub enabled by default)
- **Language**: `default_lang` in `settings.yml` (default: `auto`)

### Troubleshooting

```bash
# Check if running
docker ps | grep searxng

# Restart
docker compose -f docker/docker-compose.yml restart

# View logs
docker logs searxng --tail 50
```

## Usage

All commands use the script at `scripts/searxng_search.py` (relative to this skill directory). The script defaults to `http://127.0.0.1:8888` but accepts `--base-url` to point elsewhere.

```bash
# Basic search
python3 scripts/searxng_search.py "your query"

# Number of results
python3 scripts/searxng_search.py "your query" -n 5

# Language
python3 scripts/searxng_search.py "your query" -l zh    # Chinese
python3 scripts/searxng_search.py "your query" -l en    # English

# Category
python3 scripts/searxng_search.py "your query" -c news
python3 scripts/searxng_search.py "your query" -c images
python3 scripts/searxng_search.py "your query" -c it
python3 scripts/searxng_search.py "your query" -c science

# Time filter
python3 scripts/searxng_search.py "your query" -t day
python3 scripts/searxng_search.py "your query" -t week
python3 scripts/searxng_search.py "your query" -t month

# Specific engines
python3 scripts/searxng_search.py "your query" -e google,bing

# JSON output
python3 scripts/searxng_search.py "your query" --json

# Custom SearXNG URL
python3 scripts/searxng_search.py "your query" --base-url http://192.168.1.100:8888

# Combined
python3 scripts/searxng_search.py "最新科技新闻" -c news -l zh -t week -n 5
```

## Categories

| Category | Description |
|----------|-------------|
| `general` | Web search (default) |
| `news` | News articles |
| `images` | Image search |
| `videos` | Video search |
| `it` | IT / programming |
| `science` | Scientific articles |
| `files` | File search |
| `social media` | Social media posts |

## Notes

- SearXNG aggregates and deduplicates results from multiple engines
- The `score` field indicates cross-engine ranking confidence
- No API key needed — fully self-hosted and private
