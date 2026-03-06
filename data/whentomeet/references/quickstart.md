# WhenToMeet Quickstart (v1 tRPC)

## Prerequisites

- Env var: `WHENTOMEET_API_KEY`
- Python 3 available

## Preferred: script-first commands

All commands are non-interactive and return JSON to stdout.

### List events

```bash
python3 scripts/w2m_events.py list
```

### Create event

```bash
python3 scripts/w2m_events.py create \
  --title "Team Sync" \
  --slots-json '[{"startTime":"2026-03-02T12:00:00.000Z","endTime":"2026-03-02T13:00:00.000Z"}]' \
  --modification-policy EVERYONE
```

### Get event by id

```bash
python3 scripts/w2m_events.py get --event-id "uuid"
```

### Delete event (safe flag required)

```bash
python3 scripts/w2m_events.py delete --event-id "uuid" --confirm
```

### Encode GET input payload

```bash
python3 scripts/w2m_events.py encode-input --json '{"eventId":"uuid"}'
```

## HTTP fallback (raw API)

Use this section only if script execution is unavailable.

- Base URL: `https://whentomeet.io/api/trpc`
- Auth header: `Authorization: Bearer $WHENTOMEET_API_KEY`
- Input wrapper: `{"json": {...}}`

### Minimal create flow

### 1) Create event

```bash
curl -sS -X POST "https://whentomeet.io/api/trpc/v1.event.create" \
  -H "Authorization: Bearer $WHENTOMEET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"json": {
    "title": "Team Sync",
    "slots": [
      {"startTime": "2026-03-02T12:00:00.000Z", "endTime": "2026-03-02T13:00:00.000Z"}
    ],
    "modificationPolicy": "EVERYONE"
  }}'
```

### 2) Read key output fields

- `result.data.json.id`
- `result.data.json.status`
- `result.data.json.publicUrl`

### 3) Share event URL

Share `publicUrl` with participants.

## Fetch and list

### List events

```bash
curl -sS "https://whentomeet.io/api/trpc/v1.event.list?input=%7B%22json%22%3A%7B%7D%7D" \
  -H "Authorization: Bearer $WHENTOMEET_API_KEY"
```

### Get event by id

```bash
curl -sS "https://whentomeet.io/api/trpc/v1.event.get?input=%7B%22json%22%3A%7B%22eventId%22%3A%22uuid%22%7D%7D" \
  -H "Authorization: Bearer $WHENTOMEET_API_KEY"
```

## Safe delete flow

1. Show user the exact event (`id`, `title`, `status`).
2. Ask for explicit confirmation.
3. Delete only the confirmed `eventId`.

```bash
curl -sS -X POST "https://whentomeet.io/api/trpc/v1.event.delete" \
  -H "Authorization: Bearer $WHENTOMEET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"json": {"eventId": "uuid"}}'
```

## GET input encoding helper

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
