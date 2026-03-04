---
name: stealthy-google-search
description: Google search via Scrapling’s StealthyFetcher/StealthySession. Use to run Google queries and return clean top-result titles + links (plain text or JSON). Includes a deterministic install script that sets up a local venv and installs Scrapling fetchers + browsers.
metadata: {"openclaw":{"homepage":"https://github.com/D4Vinci/Scrapling","requires":{"bins":["python3"]}}}
---

# Stealthy Google Search (Scrapling)

This skill provides **one job**: do Google searches reliably and return the top result titles + URLs.

It ships two scripts:
- `{baseDir}/scripts/install.sh` → installs dependencies into a local venv (recommended).
- `{baseDir}/scripts/google_search.py` → runs the search and prints results.

## Install (recommended)

Run:

```bash
bash {baseDir}/scripts/install.sh
```

What it does:
- Creates a venv at `{baseDir}/.venv`
- Installs `scrapling[fetchers]`
- Runs `scrapling install` (downloads Playwright browsers + system deps)

## Usage (plain text)

```bash
{baseDir}/.venv/bin/python {baseDir}/scripts/google_search.py \
  --query "Top Indian universities" \
  --top 10 \
  --hl en \
  --gl in
```

## Usage (JSON)

```bash
{baseDir}/.venv/bin/python {baseDir}/scripts/google_search.py \
  --query "Top Indian universities" \
  --top 10 \
  --hl en \
  --gl in \
  --json
```

## Requirements / gotchas

- Python **3.10+**
- Disk space for Playwright browsers (the install step downloads them)
- Some environments require `sudo` for Playwright **system** dependencies. The installer will attempt `sudo` if available.
- Google can rate-limit/block; this skill uses Scrapling’s stealth browser fetcher, but no scraper is 100% unblockable.
