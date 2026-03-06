---
name: crash-fixer
description: "Autonomous crash analysis and bug fixing. Monitors crash reports from Cloudflare D1, deduplicates, analyzes with Codex 5.3 High, generates fixes, and creates PRs. Usage: /crash-fixer [--hours 24] [--limit 5] [--dry-run]"
user-invocable: true
metadata:
  { "openclaw": { "requires": { "env": ["GH_TOKEN", "CRASH_REPORTER_API_KEY", "CRASH_REPORTER_URL", "TARGET_REPO"] } } }
---

# crash-fixer

Full autonomous crash-fixing loop. Fetches crashes, deduplicates, analyzes with AI, generates fixes, and creates PRs.

## Trigger

```
/crash-fixer [--hours 24] [--limit 5] [--dry-run]
```

## How It Works

1. **Fetch** - Query crash reporter for new crashes
2. **Deduplicate** - Check fingerprint for identical crashes already fixed
3. **Analyze** - Use Codex 5.3 High (o3-high) to understand crash
4. **Fix** - Generate code fix
5. **PR** - Create branch → commit → PR
6. **Update** - Mark status in crash reporter

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--hours N` | 24 | Only fetch crashes from last N hours |
| `--limit N` | 3 | Max crashes to process per run |
| `--dry-run` | false | Analyze but don't create PRs |

## Required Environment

| Variable | Description |
|----------|-------------|
| `GH_TOKEN` | GitHub API token |
| `CRASH_REPORTER_API_KEY` | API key for crash reporter worker |
| `CRASH_REPORTER_URL` | URL of crash reporter worker |
| `TARGET_REPO` | GitHub repo to fix (owner/name) |

Note: Uses MiniMax M2.5 (available in OpenClaw) for AI analysis - no extra API key needed.

## Example

```
/crash-fixer --dry-run
```
