---
name: hn-daily
description: Fetch and filter Hacker News top stories. Use when user asks for tech news, HN updates, daily news digest, or wants to set up automated HN fetching. Supports keyword filtering (AI, programming, startups) and caching.
---

# Hacker News Daily

Fetch top stories from Hacker News with keyword filtering and caching.

## Quick Start

```bash
python3 scripts/fetch_hn.py
```

## Options

```bash
python3 scripts/fetch_hn.py --limit 5          # Return 5 stories
python3 scripts/fetch_hn.py --min-score 100    # Only stories with 100+ points
python3 scripts/fetch_hn.py --no-cache         # Force fresh fetch
python3 scripts/fetch_hn.py --format json      # JSON output
```

## Proxy

Set `HTTP_PROXY` or `HTTPS_PROXY` environment variable if needed:

```bash
export HTTPS_PROXY=http://127.0.0.1:7890
python3 scripts/fetch_hn.py
```

## Output

Text format (default):
```
📰 Hacker News 精选

1. [AI] OpenAI releases new model
   🔗 https://...
   👍 892 分 | 💬 234 评论
```

JSON format (`--format json`): Array of story objects with id, title, url, score, etc.

## Caching

Results cached for 4 hours at `~/.cache/hn-daily/hn_cache.json`. Use `--no-cache` to bypass.

## Keywords

Default filter keywords: ai, llm, gpt, claude, openai, programming, python, rust, startup, machine learning, github, etc.
