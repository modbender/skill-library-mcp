---
name: website-monitor
description: Lightweight website uptime monitor. Check if URLs are up, measure response times, detect content changes via hashing, and verify expected content. Zero dependencies.
triggers:
  - check website
  - is site up
  - monitor url
  - website status
  - uptime check
  - ping website
---

# Website Monitor

A zero-dependency Python tool for checking website availability, measuring response times, and detecting content changes. Uses only Python's standard library (urllib) — no requests, no aiohttp, no external packages.

## Features

- **Uptime checking**: Verify any URL returns the expected HTTP status code
- **Response time measurement**: Precise millisecond timing for each request
- **Content change detection**: SHA-256 based hashing to detect when page content changes between checks
- **Text verification**: Confirm that specific text appears in the response body
- **Multi-URL support**: Check multiple sites in a single command
- **JSON output**: Machine-readable output for integration with other tools and dashboards
- **Exit codes**: Returns exit code 1 if any site is down, making it perfect for shell scripts and cron jobs

## Usage Examples

Simple uptime check:
```bash
python main.py https://example.com
# ✅ https://example.com
#    Status: 200
#    Response: 142ms
#    Size: 1256 bytes
#    Hash: fb91d75a6bb43078
```

Check multiple sites at once:
```bash
python main.py example.com google.com github.com
```

Detect content changes (compare against a previous hash):
```bash
python main.py https://example.com --hash-check fb91d75a6bb43078
# Shows "Changed: YES ⚠️" or "Changed: No"
```

Verify a page contains expected text:
```bash
python main.py https://status.example.com --contains "All Systems Operational"
```

Expect a specific status code (e.g., redirect):
```bash
python main.py https://old.example.com --expect 301
```

JSON output for scripting:
```bash
python main.py example.com github.com --json | jq '.[] | select(.up == false)'
```

Use in a cron job or script:
```bash
python main.py https://mysite.com || echo "ALERT: Site is down!" | mail -s "Downtime Alert" admin@example.com
```

## Command Line Options

- `urls` — One or more URLs to check (auto-prepends https:// if missing)
- `--timeout N` — Request timeout in seconds (default: 10)
- `--expect N` — Expected HTTP status code (default: 200)
- `--contains TEXT` — Verify response body contains this string
- `--hash-check HASH` — Previous content hash to compare against for change detection
- `--json` — Output results as JSON array

## Exit Codes

- `0` — All sites are up and match expectations
- `1` — One or more sites are down or failed checks
