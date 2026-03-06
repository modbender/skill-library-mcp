---
name: aoi-hackathon-scout-lite
version: 0.1.6
description: Public-safe hackathon source registry + filtering output (no crawling, no submissions).
author: Aoineco & Co.
license: MIT
---

# AOI Hackathon Scout (Lite)

S-DNA: `AOI-2026-0215-SDNA-HACK01`

## Quick Start (copy/paste)
```bash
# 1) install
clawhub install aoi-hackathon-scout-lite

# 2) shortlist view / best-effort recommendations
# (reads context/HACKATHON_SHORTLIST.md)
aoi-hackathon recommend --n 5

# 3) browse sources (no API keys)
aoi-hackathon sources
openclaw browser start
openclaw browser open https://devpost.com/c/artificial-intelligence
openclaw browser snapshot --efficient
```

## Scope (public-safe)
- ✅ Outputs curated **source list** for hackathons / builder programs / grants
- ✅ Provides a filtering view: online-only preference, type tags
- ✅ Provides a paste-ready summary template for the user
- ❌ No crawling, no login, no form-fill, no submission automation
- ❌ No Notion API usage in the public skill (paste template only)

## Data source
- Uses the local registry file:
  - `context/HACKATHON_SOURCES_REGISTRY.md`

## Commands
### Show sources
```bash
aoi-hackathon sources
```

### Filter (best-effort)
```bash
# show only likely-online sources
# (filters Online-only fit = ✅ or ⚠️)
aoi-hackathon sources --online ok

# show only web3 sources
aoi-hackathon sources --type web3
```

### Recommend from shortlist (best-effort)
```bash
# reads context/HACKATHON_SHORTLIST.md and prints top N online-eligible items
# (excludes rejected; prioritizes 🔥 markers and 'applying/watching')
aoi-hackathon recommend --n 5
```

### Print Notion paste template (text only)
```bash
aoi-hackathon template
```

## Setup (early users)
This skill is **public-safe** and does not require API keys by default.

### Recommended default: Browser/web_fetch (no keys)
- Use OpenClaw Browser to open sources and inspect deadlines/details.
- Quick start:
  ```bash
  openclaw browser start
  openclaw browser open https://devpost.com/c/artificial-intelligence
  openclaw browser snapshot --efficient
  ```

### Optional: Brave Search API (fast keyword search)
If you want ultra-fast keyword search, you can enable Brave Search for `web_search`.

- Get key: https://brave.com/search/api/ (choose **Data for Search** plan)
- Configure (example):
  ```bash
  openclaw config set tools.web.search.provider brave
  openclaw config set tools.web.search.apiKey "BRAVE_API_KEY_HERE"
  openclaw config set tools.web.search.enabled true
  ```
- Disable again:
  ```bash
  openclaw config set tools.web.search.enabled false
  ```

(Full setup guide in repo SSOT: `context/HACKATHON_SEARCH_SETUP_GUIDE_V0_1.md`)

## Support
- Issues / bugs / requests: https://github.com/edmonddantesj/aoi-skills/issues
- Please include the skill slug: `aoi-hackathon-scout-lite`

## Provenance / originality
- AOI implementation is original code.
- Registry content is a curated link list.
