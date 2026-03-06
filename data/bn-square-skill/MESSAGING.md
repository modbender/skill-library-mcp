# MESSAGING

Interaction and response contract for `bn-square-skill`.

## Tool Input Contracts

### validate_session

- Input: none

### publish_post

- Required:
  - `content: string`
- Optional:
  - `imageUrls: string[]` (max 9)
  - `poll: { question: string; options: string[]; durationHours?: number }`

Rules:
- `content` must be non-empty.
- `poll` and `imageUrls` cannot be used together.

### get_post_status

- Required:
  - `postId: string`

## Tool Output Contracts

### validate_session

```json
{
  "valid": true,
  "userId": "123",
  "username": "trader"
}
```

### publish_post

```json
{
  "success": true,
  "postId": "abc123",
  "postUrl": "https://www.binance.com/en/square/post/abc123"
}
```

### get_post_status

```json
{
  "status": "published",
  "postUrl": "https://www.binance.com/en/square/post/abc123"
}
```

Allowed `status` values:
- `published`
- `pending_review`
- `deleted`
- `not_found`

## Error Messaging Rules

1. Keep errors concise and actionable.
2. Never include raw values from:
   - cookies
   - csrf/session tokens
   - authorization headers
3. Prefer clear recovery hints:
   - refresh cookies/session
   - verify CDP endpoint
   - re-check endpoint paths

## Language and Tone

1. Keep responses operational and direct.
2. Use structured output first, short explanation second.
3. Report uncertain states explicitly (example: `pending_review`).
