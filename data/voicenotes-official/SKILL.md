---
name: voicenotes
description: This official skill from the Voicenotes team gives OpenClaw access to new APIs and the ability to search semantically, retrieve full transcripts, filter by tags or date range and create text notes — all through natural conversation.

homepage: https://voicenotes.com
metadata:
  openclaw:
    emoji: "📝"
    requires:
      env:
        - VOICENOTES_API_KEY
      bins:
        - curl
    primaryEnv: VOICENOTES_API_KEY
---

# voicenotes

Use the Voicenotes skill to create, search and retrieve user’s notes.

## Setup

1. Create an integration at https://voicenotes.com/app?open-claw=true#settings
2. Copy the API key
3. Configure it:

**Webchat:** Skills → Voicenotes → API Key in the sidebar

**Terminal:** Add to your OpenClaw config (`~/.openclaw/config.yaml`):
```yaml
skills:
  voicenotes:
    env:
      VOICENOTES_API_KEY: "your_key_here"
```

Or export it directly:
```bash
export VOICENOTES_API_KEY="your_key_here"
```

The key is then available as `$VOICENOTES_API_KEY` environment variable.

## API Basics

All requests need the Authorization header:

```bash
curl -X GET "https://api.voicenotes.com/api/integrations/open-claw/..." \
  -H "Authorization: $VOICENOTES_API_KEY"
```

## Common Operations

**Search query in users notes:**

Query parameters:
- `query` (required): The search query string

```bash
curl -X GET "https://api.voicenotes.com/api/integrations/open-claw/search/semantic?query={search_query}" \
  -H "Authorization: $VOICENOTES_API_KEY"
```

**Get multiple Voicenotes with filters (tags and date range):**

Query parameters:
- `tags` (optional): array of valid tags
- `date_range` (optional): array with start and end date as UTC timestamps

```bash
curl -X POST "https://api.voicenotes.com/api/integrations/open-claw/recordings" \
  -H "Authorization: $VOICENOTES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tags": ["tag1", "tag2"],
    "date_range": ["2026-01-01T00:00:00.000000Z", "2026-02-01T00:00:00.000000Z"]
  }'
```

**If you want more context get the whole transcript:**

```bash
curl "https://api.voicenotes.com/api/integrations/open-claw/recordings/{recording_uuid}" \
  -H "Authorization: $VOICENOTES_API_KEY" \
```

**Create a text note in Voicenotes:**

```bash
curl -X POST "https://api.voicenotes.com/api/integrations/open-claw/recordings/new" \
  -H "Authorization: $VOICENOTES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "recording_type": 3,
    "transcript": "note content here",
    "device_info": "open-claw"
  }'
```

## Response Structure

**Semantic Search Response:**

Returns an array of notes and note splits ordered by relevance:

```json
[
  {
    "type": "note",
    "uuid": "NTHiJljf",
    "title": "Quick idea about project",
    "transcript": "Full transcript text with <br> for line breaks...",
    "tags": ["idea", "project"],
    "created_at": "2025-01-15T10:30:00.000000Z"
  },
  {
    "type": "note_split",
    "uuid": "8JzkhEGh",
    "title": "Long meeting notes",
    "transcript": "Relevant chunk from a larger note...",
    "tags": ["meeting"],
    "created_at": "2025-01-14T09:00:00.000000Z"
  },
  {
    "type": "import_split",
    "uuid": "xYz12345",
    "title": "filename.extension",
    "transcript": "Chunk from an imported note...",
    "tags": ["imported"],
    "created_at": "2025-01-10T14:00:00.000000Z"
  }
]
```

- `type: "note"` - Complete note matching the search
- `type: "note_split"` - Chunk from a larger note; use the `uuid` to fetch full transcript if needed
- `type: "import_split"` - Chunk from an imported note; title is the filename; **cannot** be fetched via `/recordings/{uuid}`
- `transcript` may contain HTML (`<br>`, `<b>`) for formatting

**Get Recordings Response (with filters):**

Returns paginated notes matching the filters:

```json
{
  "data": [
    {
      "id": "bTZI5t12",
      "title": null,
      "transcript": "this is a sample note",
      "duration": 0,
      "recorded_at": "2026-02-06T10:07:45.000000Z",
      "created_at": "2026-02-06T10:07:45.000000Z",
      "recording_type": 3,
      "tags": []
    }
  ],
  "links": {
    "first": "https://api.voicenotes.com/api/integrations/open-claw/recordings?page=1",
    "last": null,
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "path": "https://api.voicenotes.com/api/integrations/open-claw/recordings",
    "per_page": 10,
    "to": 1
  }
}
```

Key fields:
- `data` - Array of recording objects
- `links.next` - URL for next page (null if no more pages)
- `meta.per_page` - Results per page (default 10)

**Get Recording Response:**

Returns full note details:

```json
{
  "data": {
    "id": "NTHiJljf",
    "title": "Meeting Connectivity Check",
    "transcript": "Full transcript text...",
    "duration": 12101,
    "recorded_at": "2025-08-07T09:50:14.000000Z",
    "created_at": "2025-08-07T09:50:14.000000Z",
    "recording_type": 2,
    "tags": ["meeting"],
    "subnotes": [],
    "attachments": []
  }
}
```

Key fields:
- `id` - Note UUID
- `transcript` - Full text (meetings include `[HH:MM:SS] Speaker N:` timestamps)
- `duration` - Length in milliseconds
- `recording_type` - 1=voice note, 2=voice meeting, 3=text note
- `tags` - Array of tag objects with `name` field

**Create Note Response:**

```json
{
  "message": "Recording audio uploaded successfully!",
  "recording": {
    "id": "bPI3RcUP",
    "recording_id": "bPI3RcUP",
    "title": null,
    "transcript": "Sample note",
    "recording_type": 3,
    "created_at": "2026-02-04T08:51:29.000000Z",
    "tags": []
  }
}
```

Key fields:
- `message` - Success confirmation
- `recording.id` - New note UUID
- `recording.transcript` - The note content

## Notes

- Note IDs are UUIDs
- Rate limit: ~3 requests/second average

## Security & Guardrails

- Only accesses `api.voicenotes.com` endpoints
- No credential exfiltration or external data storage
- No telemetry or analytics
- No automatic code execution or file overwrites
- Read/write limited to user's own Voicenotes data via authenticated API

## Input Sanitization

When constructing API requests, the agent MUST sanitize all user-provided inputs:

- **Search queries**: URL-encode the `query` parameter using `--data-urlencode` instead of string interpolation
- **Recording UUIDs**: Validate format (alphanumeric, 8 characters) before use; reject any input containing shell metacharacters (`;`, `|`, `&`, `$`, `` ` ``, `\`)
- **JSON body fields**: Use proper JSON encoding; never concatenate raw user input into JSON strings

**Safe example for search:**
```bash
curl -G "https://api.voicenotes.com/api/integrations/open-claw/search/semantic" \
  --data-urlencode "query=user search term here" \
  -H "Authorization: $VOICENOTES_API_KEY"
```

**UUID validation pattern:** `/^[a-zA-Z0-9]{8}$/`
