# API Templates

Base path:
- `/api/partner/v1/core-chat`

Auth header (use one):
- `x-partner-api-key: <key>`
- `Authorization: Bearer <key>`

## Create session

`POST /sessions`

```json
{
  "actor": {
    "actorId": "partner_user_001",
    "timezoneOffsetMinutes": -480
  },
  "channel": {
    "workspaceId": "partner-workspace"
  },
  "conversation": {
    "channelId": "partner-chat"
  }
}
```

## Send event

`POST /events`

```json
{
  "sessionId": "sess_xxx",
  "actor": {
    "actorId": "partner_user_001"
  },
  "text": "Seattle Mar 20-23 1 room refundable",
  "kind": "action_book_option",
  "payload": {
    "optionId": "opt_123"
  },
  "idempotencyKey": "partner:sess_xxx:action_book_option:click_001"
}
```

## Get session

`GET /sessions/{sessionId}`

## Minimal transport wrapper

```ts
async function brekRequest(path: string, init?: RequestInit) {
  const response = await fetch(`${BREK_BASE_URL}${path}`, {
    ...init,
    headers: {
      'content-type': 'application/json',
      'x-partner-api-key': BREK_PARTNER_API_KEY,
      ...(init?.headers || {})
    }
  });

  const body = await response.json().catch(() => ({}));
  const requestId = response.headers.get('x-request-id') || '';

  return { response, body, requestId };
}
```
