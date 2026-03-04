---
name: pipedrive-crm-openclaw
description: Manage Pipedrive CRM from OpenClaw using API v1, including people, organizations, deals, leads, activities, notes, pipelines, and custom endpoint actions. Use when a user wants to perform CRM operations by API instead of the Pipedrive UI.
---

# Pipedrive CRM for OpenClaw

Use this skill to run day-to-day CRM operations in Pipedrive through API calls, including CRUD, search, pipeline movement, activity logging, and any unsupported operation via raw endpoint requests.

## Required Environment

Set one authentication mode:

- `PIPEDRIVE_API_TOKEN` for API token auth (simplest)
- `PIPEDRIVE_ACCESS_TOKEN` for OAuth bearer auth

Set base routing:

- `PIPEDRIVE_COMPANY_DOMAIN` (for example: `acme` for `https://acme.pipedrive.com`)

Optional:

- `PIPEDRIVE_API_BASE` to override full API base URL (defaults to `https://<company>.pipedrive.com/api/v1`)
- `PIPEDRIVE_TIMEOUT` request timeout in seconds (default `30`)

## Setup

If the user asks to connect or validate credentials:

```bash
python3 skills/pipedrive-crm-openclaw/scripts/setup-wizard.py
```

## Primary Script

Run:

```bash
python3 skills/pipedrive-crm-openclaw/scripts/pipedrive-api.py <command> [args]
```

Core commands:

- `test_connection`
- `list <entity> [--start N] [--limit N]`
- `get <entity> <id>`
- `create <entity> <json_payload>`
- `update <entity> <id> <json_payload> [--method PUT|PATCH]`
- `delete <entity> <id>`
- `search <entity> <term> [--limit N] [--fields csv] [--exact-match]`
- `move_deal_stage <deal_id> <stage_id> [--status open|won|lost|deleted]`
- `add_note <content> [--deal-id ID] [--person-id ID] [--org-id ID] [--lead-id UUID]`
- `request <METHOD> <path> [--query '{...}'] [--body '{...}']`

Supported entities:

- `persons`
- `organizations`
- `deals`
- `leads`
- `activities`
- `notes`
- `products`
- `users`
- `pipelines`
- `stages`

## Practical OpenClaw Playbooks

### Lead Intake and Qualification

1. `search persons "name or email"` to deduplicate.
2. `create persons '{...}'` if no match.
3. `create deals '{...}'` and link person/org.
4. `add_note "summary" --deal-id <id>` to preserve context.

### Pipeline Management

1. `list deals` with filters through `request` query.
2. `move_deal_stage <deal_id> <stage_id>`.
3. `create activities '{...}'` for next follow-up.

### Daily Follow-Up Queue

1. `list activities` and `search persons`.
2. `update activities <id> '{"done":1}'` after completion.
3. Log interaction with `add_note`.

## Safety Rules

- Never print or echo raw tokens in chat output.
- Read before write when user intent is ambiguous.
- Validate IDs from API responses before destructive actions.
- If response is `401` or `403`, stop and request corrected credentials/scopes.
- Use `request` for endpoints not yet wrapped by helper commands.

## References

Load as needed:

- `references/entity-playbooks.md`
- `references/pipedrive-v1-notes.md`
