---
name: rails-agent-gateway
description: Configure and operate a Ruby On Rails Agent Gateway integration
  from the OpenClaw side for briefing pull workflows. Use when setting
  up OpenClaw to read app data through a Rails
  `/agent-gateway/:secret/briefing` endpoint, validating tokens/URL env
  vars, testing connectivity, and generating summary pulls for reports
  or automations.
---

# Rails Agent Gateway

This skill works in tandem with the
[agent_gateway](https://github.com/jessewaites/agent-gateway) Ruby gem,
a mountable Rails engine that must be installed and configured on the
Rails side (`gem "agent_gateway"` + initializer). This skill handles
the OpenClaw-side setup and usage for pulling data from that endpoint.

## Quick Workflow

1. Confirm required env vars are available.
2. Validate endpoint connectivity with a non-destructive briefing fetch.
3. Pull briefing data for a selected period/resources.
4. Summarize result counts, aggregations, and latest records.
5. If requested, prepare commands suitable for cron/automation.

## Required Environment

Require these variables before any live fetch:

- `AGENT_GATEWAY_TOKEN` (bearer token — set in the Rails app initializer as `c.auth_token`)
- `AGENT_GATEWAY_SECRET` (path secret — set as `c.path_secret`)

The OpenClaw helper script may also read:

- `RAILS_GATEWAY_URL` (full `/briefing` URL, e.g. `https://myapp.com/agent-gateway/<secret>/briefing`)
- `RAILS_GATEWAY_TOKEN` (maps to bearer token)

If env vars are missing, stop and show the exact export commands needed.

## Authentication

The gem uses two-layer auth:

1. **Path secret** — embedded in the URL (`/agent-gateway/<secret>/briefing`). Wrong value returns **404** (endpoint appears nonexistent).
2. **Bearer token** — sent via `Authorization` header. Wrong/missing value returns **401**.

Both are compared using timing-safe `secure_compare`.

## Command Patterns

### Direct curl

```bash
curl -H "Authorization: Bearer $AGENT_GATEWAY_TOKEN" \
  "https://myapp.com/agent-gateway/$AGENT_GATEWAY_SECRET/briefing?period=7d&resources=users,orders"
```

### Helper script

Prefer the local helper script when present:

```bash
/home/node/.openclaw/workspace/scripts/rails-gateway-briefing --period 7d
```

With explicit env vars:

```bash
RAILS_GATEWAY_URL='https://myapp.com/agent-gateway/<secret>/briefing' \
RAILS_GATEWAY_TOKEN='***' \
/home/node/.openclaw/workspace/scripts/rails-gateway-briefing --period 7d --resources users,orders
```

## Query Parameters

| Param | Description | Example |
|-------|-------------|---------|
| `period` | Time window: `1d`, `7d`, `30d`, `90d`, `1y`, `all` | `?period=30d` |
| `resources` | Comma-separated resource keys | `?resources=users,orders` |
| `latest` | Override latest count for all resources | `?latest=10` |

## Resource-Scoped Pulls

Resources are configured per-app via the gem's DSL. Common examples:

- `--resources users`
- `--resources orders`

Use `--latest N` to cap detailed rows while keeping counts.

The gem DSL also supports aggregations (`count`, `sum`, `avg`) on numeric
columns — these appear in the response alongside `count` and `latest`.

## Safety Rules

- Never print or echo live tokens in user-visible output.
- Redact secrets in pasted commands.
- Do not perform external write actions unless explicitly asked.
- Keep pulls read-only (`briefing` endpoint usage only).

## Troubleshooting

If calls fail:

1. Confirm helper script exists and is executable.
2. Confirm endpoint URL includes `/agent-gateway/<secret>/briefing`.
3. Confirm bearer token is current (`AGENT_GATEWAY_TOKEN`).
4. Check two-layer auth: 404 = bad path secret, 401 = bad bearer token.
5. Retry with minimal scope (`--resources users --period 7d --latest 1`).
6. Report exact error class (auth/network/format), then propose a fix.

For reusable command snippets and output interpretation, read
`references/usage.md`.
