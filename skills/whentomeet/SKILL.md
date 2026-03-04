---
name: whentomeet
description: Create, list, fetch, and delete WhenToMeet planning events via the authenticated tRPC v1 API.
compatibility: Requires Python 3, internet access, and WHENTOMEET_API_KEY in environment.
metadata: {"openclaw":{"emoji":"📅","primaryEnv":"WHENTOMEET_API_KEY","requires":{"env":["WHENTOMEET_API_KEY"]}}}
---

# WhenToMeet Skill

Use this skill for authenticated management of planning events.
More info about whentomeet.io: https://whentomeet.io/llms.txt

## Activation criteria

Use when user asks to:

- Create an event with candidate time slots
- List their events
- Fetch details for one event
- Delete an event

Do not use if the request requires undocumented endpoints/fields.

## Required context

- Env var: `WHENTOMEET_API_KEY`
- Base URL: `https://whentomeet.io/api/trpc`
- Auth: `Authorization: Bearer $WHENTOMEET_API_KEY`
- tRPC payload envelope: `{"json": {...}}`
- For GET, pass URL-encoded `input=<encoded {"json": ...}>`

## Available scripts

- `scripts/w2m_events.py` — non-interactive CLI for `create`, `list`, `get`, `delete`, and `encode-input`.

## Supported procedures (v1)

- `v1.event.create` (POST)
- `v1.event.list` (GET)
- `v1.event.get` (GET)
- `v1.event.delete` (POST)

## Core data model

Event fields:

- `id` (UUID)
- `title` (string)
- `description` (optional string)
- `status` (`PLANNING` or `FINALIZED`)
- `publicUrl` (URL)

Slot fields:

- `startTime` (ISO-8601)
- `endTime` (ISO-8601)

## Preconditions

Before calling API:

1. Ensure API key exists.
2. Ensure each slot has valid ISO timestamps and `endTime > startTime`.
3. For delete, require explicit user confirmation with exact `eventId`.

## Preferred workflow (script-first)

Run commands from the skill root.

List events:

```bash
python3 scripts/w2m_events.py list
```

Create event:

```bash
python3 scripts/w2m_events.py create \
  --title "Team Sync" \
  --description "Optional description" \
  --slots-json '[{"startTime":"2026-03-02T12:00:00.000Z","endTime":"2026-03-02T13:00:00.000Z"}]' \
  --modification-policy EVERYONE
```

Get event:

```bash
python3 scripts/w2m_events.py get --event-id "uuid"
```

Delete event (requires explicit confirmation flag):

```bash
python3 scripts/w2m_events.py delete --event-id "uuid" --confirm
```

Encode GET input payload:

```bash
python3 scripts/w2m_events.py encode-input --json '{"eventId":"uuid"}'
```

## HTTP fallback examples

Use only when script execution is unavailable.

Create event (`v1.event.create`):

```bash
curl -sS -X POST "https://whentomeet.io/api/trpc/v1.event.create" \
  -H "Authorization: Bearer $WHENTOMEET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"json": {
    "title": "My Event",
    "description": "Optional description",
    "slots": [
      {"startTime": "2026-03-02T12:00:00.000Z", "endTime": "2026-03-02T14:00:00.000Z"},
      {"startTime": "2026-03-03T12:00:00.000Z", "endTime": "2026-03-03T14:00:00.000Z"}
    ],
    "modificationPolicy": "EVERYONE"
  }}'
```

List events (`v1.event.list`):

```bash
curl -sS -X GET "https://whentomeet.io/api/trpc/v1.event.list?input=%7B%22json%22%3A%7B%7D%7D" \
  -H "Authorization: Bearer $WHENTOMEET_API_KEY"
```

Get event (`v1.event.get`):

```bash
curl -sS -X GET "https://whentomeet.io/api/trpc/v1.event.get?input=%7B%22json%22%3A%7B%22eventId%22%3A%22uuid%22%7D%7D" \
  -H "Authorization: Bearer $WHENTOMEET_API_KEY"
```

Delete event (`v1.event.delete`):

```bash
curl -sS -X POST "https://whentomeet.io/api/trpc/v1.event.delete" \
  -H "Authorization: Bearer $WHENTOMEET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"json": {"eventId": "uuid"}}'
```

GET input encoding helper:

```bash
INPUT=$(python3 - <<'PY'
import json, urllib.parse
payload = {"json": {"eventId": "uuid"}}
print(urllib.parse.quote(json.dumps(payload, separators=(",", ":"))))
PY
)

curl -sS "https://whentomeet.io/api/trpc/v1.event.get?input=${INPUT}" \
  -H "Authorization: Bearer $WHENTOMEET_API_KEY"
```

## Agent execution contract

1. Use `scripts/w2m_events.py` first.
2. Use the smallest matching procedure.
3. Send exact input shape (no invented fields).
4. Parse `result.data.json` only.
5. Return concise results:
  - create: `id`, `status`, `publicUrl`
  - list: count + compact per-event summary
  - get: core fields + slots
  - delete: explicit success/failure
6. Include rate-limit context on failures.

## Errors and retries

- 400: invalid wrapper/shape/timestamps
- 401/403: invalid key or access restriction
- 404: event not found
- 429: throttle; wait until `X-RateLimit-Reset` before one retry

Never retry non-idempotent create/delete blindly more than once.

## Rate limits

- Free: 32 requests (lifetime)
- Plus: 1,000 requests/hour
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Safety rules

- Never log or echo raw API keys.
- Never fabricate event IDs, URLs, or statuses.
- Do not claim write success unless response confirms it.
- If response shape differs, report mismatch and return observed keys.

## References

- `references/quickstart.md` — copy/paste request flows for create/list/get/delete.
- `references/troubleshooting.md` — error diagnosis, retry behavior, and safety checks.
