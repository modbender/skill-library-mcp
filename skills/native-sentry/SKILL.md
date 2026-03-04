---
name: sentry
description: Read Sentry issues, events, and production errors via the Sentry REST API. Use when the user wants to inspect errors, list recent issues, get stack traces, or summarize production health. Requires SENTRY_AUTH_TOKEN with read-only scopes.
allowed-tools: Bash(python3:*), Bash(export:*)
metadata: {"openclaw":{"emoji":"🐛","primaryEnv":"SENTRY_AUTH_TOKEN","requires":{"bins":["python3"],"env":["SENTRY_AUTH_TOKEN"]}}}
---

# Sentry (Read-only)

Read production errors and issues from Sentry.

## Setup

```bash
# Check token is set (does not print the value)
[ -n "$SENTRY_AUTH_TOKEN" ] && echo "SENTRY_AUTH_TOKEN: set" || echo "SENTRY_AUTH_TOKEN: MISSING"
echo "ORG=${SENTRY_ORG:-not set}"
echo "PROJECT=${SENTRY_PROJECT:-not set}"
```

If `SENTRY_AUTH_TOKEN` is missing:
1. Go to https://sentry.io/settings/account/api/auth-tokens/
2. Create a token with scopes: `project:read`, `event:read`, `org:read`
3. Set `SENTRY_AUTH_TOKEN` in your environment

Set optional defaults to avoid passing flags every time:
```bash
export SENTRY_ORG=your-org-slug
export SENTRY_PROJECT=your-project-slug
```

## Script path

```bash
SKILL_DIR="$(python3 -c "import os; print(os.path.dirname(os.path.realpath('$0')))" 2>/dev/null || echo "$HOME/.claude/skills/sentry")"
SENTRY_API="$SKILL_DIR/scripts/sentry_api.py"
```

## Commands

### List recent issues

```bash
python3 "$SENTRY_API" list-issues \
  --org "$SENTRY_ORG" \
  --project "$SENTRY_PROJECT" \
  --time-range 24h \
  --environment prod \
  --limit 20 \
  --query "is:unresolved"
```

### Get issue detail

```bash
python3 "$SENTRY_API" issue-detail ISSUE_ID
```

### Get events for an issue

```bash
python3 "$SENTRY_API" issue-events ISSUE_ID --limit 10
```

### Get event detail (no stack traces by default)

```bash
python3 "$SENTRY_API" event-detail \
  --org "$SENTRY_ORG" \
  --project "$SENTRY_PROJECT" \
  EVENT_ID
```

Add `--include-entries` to include stack traces.

### Resolve a short ID (e.g. ABC-123) to issue ID

```bash
python3 "$SENTRY_API" list-issues \
  --org "$SENTRY_ORG" \
  --project "$SENTRY_PROJECT" \
  --query "ABC-123" \
  --limit 1
```

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--org` | `$SENTRY_ORG` | Org slug |
| `--project` | `$SENTRY_PROJECT` | Project slug |
| `--time-range` | `24h` | Stats period (e.g. `7d`, `30d`) |
| `--environment` | `prod` | Environment filter |
| `--limit` | `20` | Max results (max 50) |
| `--query` | | Sentry search query |
| `--base-url` | `https://sentry.io` | For self-hosted Sentry |
| `--no-redact` | | Disable PII redaction — **avoid in shared/logged environments** |

## Notes

- PII (emails, IPs) is redacted by default
- Stack traces are excluded from event detail by default — add `--include-entries` only when you need them and trust the environment
- `--no-redact` disables PII redaction — avoid in shared or logged environments
- For self-hosted Sentry, set `SENTRY_BASE_URL` or use `--base-url`
