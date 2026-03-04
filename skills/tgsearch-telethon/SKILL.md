# tg_search

Search public Telegram channels and groups by keyword using an already-authorized Telethon session on this VPS.

## What it does
- Runs global Telegram search for public channels/groups matching a query
- Returns up to `limit` results as JSON

## Command executed
`/usr/local/bin/tg_search "<query>" <limit>`

## Inputs
- query (string, required): e.g. "crypto", "здоровье", "ai agents"
- limit (int, optional, default 10, max 50)

## Output (JSON)
[
  { "type": "channel|group", "title": "...", "username": "...", "id": 123456789 },
  ...
]

## Notes / limitations
- Only public channels/groups discoverable by Telegram search.
- No access to private groups/chats without an invite.
- `username` can be null if there is no public @username.
