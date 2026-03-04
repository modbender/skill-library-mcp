---
name: fathom
description: Access Fathom AI meeting recordings, transcripts, summaries, and action items via the Fathom API. Use when the user asks about meeting notes, call summaries, action items from calls, follow-ups from meetings, or anything related to Fathom recordings. Also use for syncing Fathom data with calendars or building meeting accountability workflows.
---

# Fathom

Pull meeting recordings, transcripts, summaries, and action items from Fathom AI Notetaker.

## Setup

Store the API key in `~/.openclaw/secrets/fathom.env`:
```
FATHOM_API_KEY=your-api-key-here
FATHOM_WEBHOOK_SECRET=your-webhook-secret-here
```

Get API key from Fathom: Settings → Integrations → API → Generate Key.

## API Reference

Base URL: `https://api.fathom.ai/external/v1`
Auth header: `X-Api-Key: <FATHOM_API_KEY>`

### List Meetings

```bash
curl "https://api.fathom.ai/external/v1/meetings?limit=20" \
  -H "X-Api-Key: $FATHOM_API_KEY"
```

Key query params:
- `limit` (1-100, default 10)
- `created_after` / `created_before` (ISO 8601)
- `recorded_by[]` (email filter)
- `include_transcript=true` (include full transcript)
- `include_action_items=true` (include action items)
- `include_summary=true` (include AI summary)

Response shape:
```json
{
  "items": [{
    "title": "Meeting Name",
    "meeting_title": "Calendar Event Name",
    "url": "https://fathom.video/calls/123",
    "share_url": "https://fathom.video/share/abc",
    "created_at": "2026-02-17T20:00:00Z",
    "scheduled_start_time": "...",
    "scheduled_end_time": "...",
    "recording_start_time": "...",
    "recording_end_time": "...",
    "recording_id": 123,
    "transcript": "...",
    "default_summary": "...",
    "action_items": ["..."],
    "calendar_invitees": [{"name": "...", "email": "...", "is_external": true}],
    "recorded_by": {"name": "...", "email": "..."}
  }],
  "next_cursor": "..."
}
```

### Pagination

Use `next_cursor` from response as `cursor` param in next request.

### Matching Fathom to Calendar

Match by time overlap (recording_start_time within event window ± 15 min) or by title similarity. The `calendar_invitees` field shows who was invited; `is_external` flags non-org attendees.

## Common Workflows

### Pull action items from recent calls

```bash
source ~/.openclaw/secrets/fathom.env
curl -s "https://api.fathom.ai/external/v1/meetings?include_action_items=true&limit=20" \
  -H "X-Api-Key: $FATHOM_API_KEY"
```

### Get full transcript for a specific date range

```bash
curl -s "https://api.fathom.ai/external/v1/meetings?include_transcript=true&created_after=2026-02-17T00:00:00Z&created_before=2026-02-18T00:00:00Z" \
  -H "X-Api-Key: $FATHOM_API_KEY"
```

### Filter to external meetings only

After fetching, filter meetings where at least one `calendar_invitees` entry has `is_external: true`, or check the `calendar_invitees_domains_type` field for `"one_or_more_external"`.

### Sync script (calendar + Fathom → database)

See `scripts/sync-fathom.js` for a complete local sync script that:
1. Refreshes Google OAuth token
2. Pulls Google Calendar events for a date range
3. Pulls Fathom meetings with action items
4. Matches Fathom recordings to calendar events
5. Upserts everything to Supabase (or any database)

Adapt the database layer to your needs.

## Webhooks

Fathom can POST to your endpoint when recordings complete. Verify with `FATHOM_WEBHOOK_SECRET`. Use this for real-time sync instead of polling.

## Tips

- Action items from Fathom are AI-generated — review for accuracy
- `recorded_by` shows who ran the Fathom bot, not necessarily the meeting organizer
- Duplicate recordings happen when multiple team members run Fathom on the same call — deduplicate by matching `scheduled_start_time` + similar titles
- The API returns meetings from all team members if using a team API key
