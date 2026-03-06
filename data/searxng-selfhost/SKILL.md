---
name: searxng
description: Self-hosted web search aggregator for OpenClaw agents. Use this skill to (1) install SearXNG on a VPS/server so the agent can search the web without API keys, or (2) run web searches using an existing local SearXNG instance. Covers installation, configuration, the search.py CLI tool, and fallback behaviour. Use when the agent needs web search capability, when setting up a new OpenClaw instance, or when diagnosing search failures.
---

# SearXNG

SearXNG is a self-hosted search aggregator that queries Google, Bing, Brave, Startpage, DuckDuckGo, and Wikipedia simultaneously. No API keys required. Results returned as JSON.

## Quick start (already installed)

```bash
python3 scripts/search.py "your query"             # human-readable
python3 scripts/search.py "your query" --json      # JSON (for parsing)
python3 scripts/search.py "query" --count 5 --json # limit + JSON
```

Place `search.py` anywhere convenient — typically `tools/search.py` in the workspace.

For detailed usage patterns and service management: see `references/usage.md`.

## Installation (new instance)

Run as root on Ubuntu 22.04/24.04:

```bash
bash scripts/install_searxng.sh
```

This installs SearXNG, creates a `searxng` system user, writes `/etc/searxng/settings.yml`, and starts a systemd service on `http://127.0.0.1:8888`.

Verify:
```bash
curl 'http://127.0.0.1:8888/search?q=test&format=json' | python3 -m json.tool | head -20
systemctl status searxng
```

## Connecting search.py to the instance

`search.py` targets `http://127.0.0.1:8888` by default. If the port differs, update `SEARXNG_URL` at the top of the script.

## Fallback

If SearXNG is down, `search.py` falls back to Wikipedia + GitHub APIs automatically. No action needed — results still return, just from narrower sources.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `[SearXNG unavailable]` in stderr | `systemctl restart searxng` |
| Port conflict on 8888 | Change `port:` in `/etc/searxng/settings.yml` + update `SEARXNG_URL` in script |
| Empty results from all engines | Check `/etc/searxng/settings.yml` engines block; restart service |
| Connection refused | Service not running — `systemctl start searxng` |
