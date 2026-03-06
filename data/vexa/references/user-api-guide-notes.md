# Vexa API reference notes (repo research)

Primary docs reviewed:
- `docs/user_api_guide.md`
- `docs/websocket.md`
- `README.md`

## Auth + base URL

- Header: `X-API-Key: <key>`
- Hosted base URL: `https://api.cloud.vexa.ai`
- Self-hosted base URL: your Vexa deployment URL

## REST endpoints used by this skill

- `POST /bots` — request bot (`platform`, `native_meeting_id`, optional `language`, `bot_name`; Teams also needs `passcode`)
- `GET /bots/status` — list running bots
- `PUT /bots/{platform}/{native_meeting_id}/config` — update active bot config (e.g., language)
- `DELETE /bots/{platform}/{native_meeting_id}` — stop bot
- `GET /transcripts/{platform}/{native_meeting_id}` — transcript (during or after meeting)
- `POST /transcripts/{platform}/{native_meeting_id}/share` — temporary share URL
- `GET /meetings` — meeting history
- `PATCH /meetings/{platform}/{native_meeting_id}` — update metadata (`data.name`, `data.participants`, `data.languages`, `data.notes`)
- `DELETE /meetings/{platform}/{native_meeting_id}` — purge transcript + anonymize finalized meeting only
- `PUT /user/webhook` — set user webhook URL

## Meeting ID normalization

- Google Meet: code like `abc-defg-hij`
- Teams: numeric meeting ID from `/meet/<id>` and passcode from `?p=...`

## Real-time transcripts

- For low-latency updates, connect to `/ws` with the same API key header.
- Subscribe payload:
  - `{ "action": "subscribe", "meetings": [{ "platform": "google_meet", "native_id": "abc-defg-hij" }] }`
- Main stream event to process: `transcript.mutable`
- Recommended flow from docs:
  1. Bootstrap from REST transcript endpoint.
  2. Merge WebSocket segments by `absolute_start_time`.
  3. Prefer latest `updated_at` when segment versions conflict.

## Safety

- Treat `DELETE /meetings/...` as destructive.
- Require explicit user confirmation for exact meeting identity.
- If delete returns `409`, the meeting is not finalized yet.
