---
name: sentry
description: Fetch and analyze issues from Sentry error tracking. Use when asked to check Sentry errors, pull issues, investigate exceptions, review error trends, or get crash reports from a Sentry project.
version: 1.0.0
---

# Sentry Issue Tracker

Fetch and analyze issues from Sentry using the Sentry API.

## Prerequisites

- Sentry API token with `project:read` and `event:read` scopes
- Organization slug and project slug

## Authentication

Set the `SENTRY_AUTH_TOKEN` environment variable, or pass `--token` to the script.

```bash
export SENTRY_AUTH_TOKEN="your-token-here"
```

To create a token: Sentry → Settings → Auth Tokens → Create New Token

## Quick Start

List recent unresolved issues:
```bash
python3 scripts/sentry_issues.py --org <org-slug> --project <project-slug>
```

Get issue details with stack trace:
```bash
python3 scripts/sentry_issues.py --org <org-slug> --project <project-slug> --issue <issue-id> --details
```

## Script Reference

### `scripts/sentry_issues.py`

Fetches issues from Sentry API.

**Arguments:**
- `--org` (required): Sentry organization slug
- `--project` (required): Project slug  
- `--token`: Auth token (defaults to `SENTRY_AUTH_TOKEN` env var)
- `--issue`: Specific issue ID to fetch details
- `--details`: Include stack trace and event details
- `--query`: Filter query (e.g., `is:unresolved`, `level:error`)
- `--limit`: Max issues to return (default: 25)
- `--sort`: Sort by `date`, `new`, `priority`, `freq`, or `user` (default: date)

**Examples:**
```bash
# List 10 most recent unresolved errors
python3 scripts/sentry_issues.py --org myorg --project myproject --query "is:unresolved level:error" --limit 10

# Get details for specific issue
python3 scripts/sentry_issues.py --org myorg --project myproject --issue 12345 --details

# Sort by most users affected
python3 scripts/sentry_issues.py --org myorg --project myproject --sort user --limit 5
```

## Common Queries

| Query | Description |
|-------|-------------|
| `is:unresolved` | Open issues only |
| `is:resolved` | Resolved issues |
| `is:ignored` | Ignored issues |
| `level:error` | Error-level issues |
| `level:warning` | Warning-level issues |
| `firstSeen:>-24h` | New in last 24 hours |
| `lastSeen:>-1h` | Active in last hour |
| `assigned:me` | Assigned to current user |
| `has:release` | Issues with release info |

Combine queries: `is:unresolved level:error firstSeen:>-24h`

## Output Format

Issues are returned as JSON with key fields:
- `id`: Issue ID for fetching details
- `title`: Error message/title
- `culprit`: Source location
- `count`: Number of events
- `userCount`: Affected users
- `firstSeen` / `lastSeen`: Timestamps
- `level`: error/warning/info
- `status`: unresolved/resolved/ignored

When `--details` is used, includes:
- Full stack trace
- Latest event context
- Tags and metadata
- Browser/OS info (if available)
