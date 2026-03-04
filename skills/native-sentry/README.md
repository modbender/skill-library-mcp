# sentry

Read production errors and issues from [Sentry](https://sentry.io) via the Sentry REST API.

## What it does

- List recent unresolved issues
- Get issue details
- List events for an issue
- Get event detail (with optional stack traces)
- Resolve short IDs (e.g. `MYAPP-123`) to internal IDs
- PII redacted by default (emails, IPs)

## Requirements

- Python 3 (stdlib only, no pip needed)
- A Sentry auth token with read-only scopes

## Auth token setup

1. Go to https://sentry.io/settings/account/api/auth-tokens/
2. Create a token with scopes: `project:read`, `event:read`, `org:read`
3. Export it:
   ```bash
   export SENTRY_AUTH_TOKEN=sntrys_...
   export SENTRY_ORG=your-org-slug
   export SENTRY_PROJECT=your-project-slug
   ```

## Usage

```bash
# List recent issues
python3 scripts/sentry_api.py list-issues --time-range 24h --limit 20

# Issue detail
python3 scripts/sentry_api.py issue-detail 1234567890

# Events for an issue
python3 scripts/sentry_api.py issue-events 1234567890 --limit 10

# Event detail (no stack traces)
python3 scripts/sentry_api.py event-detail abcdef1234567890

# Event detail (with stack traces)
python3 scripts/sentry_api.py event-detail abcdef1234567890 --include-entries
```

## Self-hosted Sentry

```bash
export SENTRY_BASE_URL=https://sentry.yourcompany.com
```

## Notes

- Works with OpenClaw and other Claude Code-compatible skill runners
- Script is pure Python stdlib — no dependencies to install
