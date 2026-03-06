---
name: scrapling
description: "Web scraping using Scrapling — a Python framework with anti-bot bypass (Cloudflare Turnstile, fingerprint spoofing), adaptive element tracking, stealth headless browser, and full CSS/XPath extraction. Use when web_fetch fails (Cloudflare, JS-rendered pages), or when extracting structured data from websites (prices, articles, lists). Supports HTTP, stealth, and full browser modes. Source: github.com/D4Vinci/Scrapling (PyPI: scrapling). Only use on sites you have permission to scrape."
license: MIT
metadata:
  source: https://github.com/D4Vinci/Scrapling
  pypi: https://pypi.org/project/scrapling/
---

# Scrapling Skill

**Source:** https://github.com/D4Vinci/Scrapling (open source, MIT-like license)
**PyPI:** `scrapling` — install before first use (see below)

> ⚠️ Only scrape sites you have permission to access. Respect `robots.txt` and Terms of Service. Do not use stealth modes to bypass paywalls or access restricted content without authorization.

## Installation (one-time, confirm with user before running)

```bash
pip install scrapling[all]
patchright install chromium  # required for stealth/dynamic modes
```

- `scrapling[all]` installs `patchright` (a stealth fork of Playwright, bundled as a PyPI package — not a typo), `curl_cffi`, MCP server deps, and IPython shell.
- `patchright install chromium` downloads Chromium (~100 MB) via patchright's own installer (same mechanism as `playwright install chromium`).
- Confirm with user before running — installs ~200 MB of dependencies and browser binaries.

## Script

`scripts/scrape.py` — CLI wrapper for all three fetcher modes.

```bash
# Basic fetch (text output)
python3 ~/skills/scrapling/scripts/scrape.py <url> -q

# CSS selector extraction
python3 ~/skills/scrapling/scripts/scrape.py <url> --selector ".class" -q

# Stealth mode (Cloudflare bypass) — only on sites you're authorized to access
python3 ~/skills/scrapling/scripts/scrape.py <url> --mode stealth -q

# JSON output
python3 ~/skills/scrapling/scripts/scrape.py <url> --selector "h2" --json -q
```

## Fetcher Modes

- **http** (default) — Fast HTTP with browser TLS fingerprint spoofing. Most sites.
- **stealth** — Headless Chrome with anti-detect. For Cloudflare/anti-bot.
- **dynamic** — Full Playwright browser. For heavy JS SPAs.

## When to Use Each Mode

- `web_fetch` returns 403/429/Cloudflare challenge → use `--mode stealth`
- Page content requires JS execution → use `--mode dynamic`
- Regular site, just need text/data → use `--mode http` (default)

## Python Inline Usage

For custom logic beyond the CLI, write inline Python. See `references/patterns.md` for:
- Adaptive scraping (`auto_save` / `adaptive` — saves element fingerprints locally)
- Session/cookie handling
- Async usage
- XPath, find_similar, attribute extraction

## Notes

- **MCP server** (`scrapling mcp`): starts a local network service for AI-native scraping. Only start if explicitly needed and trusted — it exposes a local HTTP server.
- **`auto_save=True`**: persists element fingerprints to disk for adaptive re-scraping. Creates local state in working directory.
- Stealth/dynamic modes use Chromium headless — no `xvfb-run` needed.
- For large-scale crawls, use the Spider API (see Scrapling docs).
