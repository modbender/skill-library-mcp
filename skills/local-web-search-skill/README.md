# local-web-search-skill

Free local web search skill for OpenClaw using DuckDuckGo HTML (no API key).

## Features
- API-key free search
- Trust scoring per result
- Retry/backoff for transient errors
- Security note + disclaimer in output

## Skill files
- `SKILL.md`
- `scripts/local_search.py`

## Quick usage
```bash
./scripts/local_search.py "polymarket maker strategy" --max 5
```
