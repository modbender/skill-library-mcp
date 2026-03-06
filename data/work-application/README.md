# 📄 openclaw-skill-work-application

> OpenClaw skill - Job search automation: scraping, CV rendering, offer analysis and candidate tracking via Playwright + stdlib

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-skill-blue)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-work--application-green)](https://clawhub.ai/Romain-Grosos/work-application)
[![Python](https://img.shields.io/badge/Python-3.9+-brightgreen)](https://python.org)
[![Playwright](https://img.shields.io/badge/deps-Playwright%20(optional)-informational)](https://playwright.dev/python/)

Job search automation for OpenClaw agents. 4 HTML CV templates, scraping across 5 French job platforms, keyword-based scoring, deep analysis with page scraping, full multi-dimension report (skills/company/location/salary), and candidature tracking. Stdlib only (except optional Playwright for scraping and analysis). Supports local and Nextcloud storage. Includes interactive setup wizard, validation script, and a behavior restriction system via `config.json`.

- All capabilities disabled or restricted by default - opt-in via `config.json`
- `readonly_mode` blocks all writes regardless of individual permissions
- No secrets stored - this skill requires no credentials, no API keys, no environment variables
- Nextcloud storage (optional) delegates authentication to the [`nextcloud-files`](https://clawhub.ai/Romain-Grosos/nextcloud-files) skill - credentials are never handled here
- No external HTTP calls unless `allow_scrape=true` (Playwright only, no background network)
- Path traversal protection on all storage operations (local and Nextcloud)
- HTML output escaped to prevent injection (`html.escape` on all profile fields)

## Install

```bash
clawhub install work-application
```

Or manually:

```bash
git clone https://github.com/rwx-g/openclaw-skill-work-application \
  ~/.openclaw/workspace/skills/work-application
```

## Setup

```bash
python3 scripts/setup.py       # profile + permissions + scraper config
python3 scripts/init.py        # validate configuration
```

## Quick start

```bash
# Show your profile
python3 scripts/work_application.py profile show

# Generate a CV
python3 scripts/work_application.py render --template classic --output cv.html

# Scrape job offers (requires allow_scrape=true + Playwright)
python3 scripts/work_application.py scrape --platforms free-work,wttj

# Analyze and rank scraped offers
python3 scripts/work_application.py analyze

# Deep analyze top offers (scrapes actual pages)
python3 scripts/work_application.py deep-analyze --max 10

# Full report for a single offer
python3 scripts/work_application.py report "https://example.com/job-offer"

# Track candidatures
python3 scripts/work_application.py track list
python3 scripts/work_application.py track add "Thales" "DevOps Engineer" --location Paris
```

## What it can do

| Category | Operations |
|----------|-----------|
| CV Generation | render 4 templates (classic, modern-sidebar, two-column, creative), adapt profile, validate |
| Job Scraping | scrape 5 platforms (Free-Work, WTTJ, Apec, HelloWork, LeHibou) |
| Job Analysis | score, rank, filter, select top matches |
| Deep Analysis | scrape job pages, match skills against full content |
| Report | full multi-dimension analysis of a single offer (skills, company, location, salary) with market data |
| Tracking | log applications, update status, list candidatures |
| Profile | load/save master and adapted profiles, validate structure |
| Storage | local filesystem or Nextcloud via WebDAV |

## Configuration

Config → `~/.openclaw/config/work-application/config.json` (created by `setup.py`):

```json
{
  "allow_write": false,
  "allow_export": true,
  "allow_scrape": false,
  "allow_tracking": true,
  "default_template": "classic",
  "default_color": "#2563eb",
  "default_lang": "fr",
  "report_mode": "analysis",
  "readonly_mode": false
}
```

All `allow_*` flags default to `false` except `allow_export` and `allow_tracking`. Set `readonly_mode: true` to block all writes regardless of individual flags.

A `config.example.json` with safe defaults and example scraper searches is included.

## Security

- **Stdlib for core features** - CV generation, ranking, and tracking require no pip install; Playwright is optional (scraping, deep analysis, reports)
- **All capabilities disabled by default** - `allow_scrape` and `allow_write` are `false` out of the box
- **No credentials, no secrets, no env vars** - `config.json` contains only behavioral flags and defaults. This skill never stores or handles passwords, tokens, or API keys
- **Nextcloud credential delegation** - optional Nextcloud storage delegates all authentication to the separate [`nextcloud-files`](https://clawhub.ai/Romain-Grosos/nextcloud-files) skill, which manages its own credentials (`~/.openclaw/secrets/nc_creds`). This skill only imports `NextcloudClient` at runtime
- **No external HTTP calls** unless `allow_scrape=true` - scraping uses Playwright only (headless Chromium), contacting job platforms and optionally `glassdoor.fr`/`fr.indeed.com` for company reviews. No background network activity, no telemetry
- **Path traversal protection** - all storage operations validate filenames against `../`, absolute paths, and null bytes; resolved paths are checked against the storage root
- **HTML injection prevention** - all profile fields passed through `html.escape()` before rendering
- **URL encoding** - external URLs built from user data (company names) are properly encoded
- **JSON deserialization validation** - `read_json()` validates the returned type before use
- **readonly_mode** - master kill-switch that blocks all write operations regardless of individual permissions
- **No eval / no shell execution** - no user-controlled strings are passed to `eval()`, `exec()`, or shell commands

## Requirements

- Python 3.9+
- No pip install needed for core features (CV generation, ranking, tracking - stdlib only)
- Optional: `pip install playwright playwright-stealth && playwright install chromium` (for job scraping, deep analysis, and reports)
- Optional: `playwright-stealth` - stealth plugin for anti-bot bypass (gracefully ignored if absent)

## Documentation

- [SKILL.md](SKILL.md) - full skill instructions, CLI reference, templates
- [references/api.md](references/api.md) - CLI command reference and profile schema
- [references/troubleshooting.md](references/troubleshooting.md) - common errors and fixes

## Uninstall

```bash
python3 scripts/setup.py --cleanup    # remove config + master profile
```

Full removal:

```bash
rm -rf ~/.openclaw/data/work-application/
rm -rf ~/.openclaw/config/work-application/
```

## License

[MIT](LICENSE)
