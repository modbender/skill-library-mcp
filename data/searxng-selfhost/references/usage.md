# SearXNG Search — Usage Reference

## Basic usage

```bash
python3 /path/to/search.py "query"                  # 10 results, human-readable
python3 /path/to/search.py "query" --count 5        # limit results
python3 /path/to/search.py "query" --json           # JSON output (for parsing)
python3 /path/to/search.py "query" --count 5 --json # both
```

## Result format

Each result has:
- `title` — page/document title
- `url` — full URL
- `snippet` — up to 200 chars of content
- `engine` — which engine returned it (google, bing, brave, startpage, duckduckgo, wikipedia)

## Fallback behaviour

If SearXNG is unavailable (service down, wrong port), the script falls back automatically to:
1. Wikipedia API (always works, no IP restrictions)
2. GitHub Search API (10 req/min unauthenticated)

Fallback is logged to stderr. Results still return — just fewer, narrower sources.

## Service management

```bash
systemctl status searxng        # check status
systemctl restart searxng       # restart
journalctl -u searxng -f        # live logs
```

## Health check

```bash
curl 'http://127.0.0.1:8888/search?q=test&format=json' | python3 -m json.tool | head -30
```

## Configuration

Config lives at `/etc/searxng/settings.yml`.
To add/remove engines, edit the `engines:` block and restart.

Port default: `8888`. To change, update `settings.yml` + update `SEARXNG_URL` in `search.py`.

## Common query patterns

| Goal | Query example |
|------|---------------|
| Current events | "topic site:reuters.com OR site:bbc.com" |
| GitHub repos | "project language python" — then follow with GitHub API for details |
| Docs lookup | "function name site:docs.python.org" |
| Price/availability | product name + "price" or "review 2025" |
| Technical errors | paste the exact error message in quotes |

## Resource usage

~85MB RAM. Negligible CPU at rest. Safe to run on a 2GB VPS alongside other services.
