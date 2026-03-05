---
name: posthog-query
description: Run SQL queries against PostHog product analytics data using the PostHog CLI. Use when checking pageviews, event counts, trends, or any analytics data from PostHog.
metadata: {"openclaw": {"emoji": "🦔", "requires": {"bins": ["posthog-cli"]}, "install": "npm install -g posthog-cli"}}
---

# PostHog Query Skill

Run HogQL (ClickHouse-compatible SQL) queries against PostHog via the CLI.

## One-Time Setup

```bash
posthog-cli login  # authenticate interactively; stores token in ~/.posthog/credentials.json
```

Requires API key scope: `query:read`.

## Command

```bash
posthog-cli exp query run "<SQL>"
```

Results are printed as JSON lines to stdout. The CLI reads auth from `~/.posthog/credentials.json` (set up via `posthog-cli login`).

## Property Access Syntax

Use bracket notation for event properties — dot notation with quoted keys does not work:

```sql
-- ✅ Correct
properties['$current_url']
properties['$browser']

-- ❌ Wrong
properties.'$current_url'
```

## Examples

**Count all pageviews:**
```bash
posthog-cli exp query run "SELECT count() as pageviews FROM events WHERE event = '\$pageview'"
```

**Filter by URL:**
```bash
posthog-cli exp query run "SELECT count() as pageviews FROM events WHERE event = '\$pageview' AND properties['\$current_url'] LIKE 'https://example.com/%'"
```

**7-day daily trend:**
```bash
posthog-cli exp query run "SELECT toDate(timestamp) as date, count() as pageviews FROM events WHERE event = '\$pageview' AND timestamp >= now() - INTERVAL 7 DAY GROUP BY date ORDER BY date"
```

**Recent events:**
```bash
posthog-cli exp query run "SELECT event, timestamp FROM events ORDER BY timestamp DESC LIMIT 10"
```

## Other Subcommands

- `posthog-cli exp query editor` — interactive query editor
- `posthog-cli exp query check "<SQL>"` — syntax/type check without running
- Append `--debug` to `run` to get the full JSON response (columns, types, cache info)

## Notes

- HogQL is ClickHouse-compatible SQL — standard ClickHouse functions apply
- Shell-escape `$` in event names: `'\$pageview'` or use double quotes carefully
- The `--debug` flag returns full metadata including column types and cache status
