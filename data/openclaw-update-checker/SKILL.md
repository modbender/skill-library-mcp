---
name: openclaw-update-checker
description: "Check for OpenClaw updates by comparing installed version against the npm registry. Use when: user asks about updates, version status, or 'is openclaw up to date'. Also useful in heartbeats/cron for periodic update monitoring. Read-only — reports status only, does not modify the system."
---

# OpenClaw Update Checker

Read-only version checker. Compares the installed OpenClaw version against the npm registry and reports whether updates are available. Does not install, modify, or restart anything.

## Usage

```bash
# Human-readable output
python3 scripts/check_update.py

# Machine-readable JSON (for dashboards, cron, integrations)
python3 scripts/check_update.py --format json
```

## Output

**Text mode:** One-liner if current, or a summary showing installed vs latest version and number of versions behind.

**JSON mode:**
```json
{
  "installed": "2026.2.21-2",
  "latest": "2026.2.21-2",
  "up_to_date": true,
  "newer_versions": [],
  "changelog_url": "https://github.com/openclaw/openclaw/releases/tag/v2026.2.21"
}
```

## How It Works

1. **Reads the installed version** from the local `package.json` file at known npm global install paths (`/usr/lib/node_modules/openclaw/package.json` or `/usr/local/lib/node_modules/openclaw/package.json`)
2. **Queries the npm registry** via an HTTPS GET request to `https://registry.npmjs.org/openclaw` using Python's `urllib.request` (stdlib)
3. **Compares versions** and reports the result

## What It Does NOT Do

- Does not install or update any packages
- Does not write to any files
- Does not restart any services
- Does not execute any subprocesses or shell commands

## System Access

- **File reads:** `/usr/lib/node_modules/openclaw/package.json` and `/usr/local/lib/node_modules/openclaw/package.json` (read-only, to determine installed version)
- **Network:** Single HTTPS GET to `https://registry.npmjs.org/openclaw` (read-only, no authentication, to fetch available versions)

## Requirements

- Python 3.10+ (uses `str | None` type union syntax)
- OpenClaw installed globally via npm
- Outbound HTTPS access to `registry.npmjs.org`
