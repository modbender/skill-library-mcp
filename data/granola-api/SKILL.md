---
name: granola-mcp
description: |
  Granola MCP integration with managed authentication. Use this skill when users want to search meeting content, get meeting summaries, find action items, or retrieve transcripts from Granola via MCP. For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Granola MCP

Access Granola via MCP (Model Context Protocol) with managed authentication.

## Quick Start

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'query': 'What action items came from my last meeting?'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/granola/query_granola_meetings', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/granola/{tool-name}
```

Replace `{tool-name}` with the MCP tool name (e.g., `query_granola_meetings`). The gateway proxies requests to `mcp.granola.ai` and automatically injects your credentials.

## Authentication

All requests require the Maton API key:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Granola MCP connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=granola&method=MCP&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'granola', 'method': 'MCP'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "8a413c45-6427-45d9-b69d-8118ce62ffce",
    "status": "PENDING",
    "creation_time": "2026-02-24T11:34:46.204677Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "granola",
    "method": "MCP",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Granola connections, you must specify which MCP connection to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'query': 'What were my action items?'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/granola/query_granola_meetings', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
req.add_header('Maton-Connection', '8a413c45-6427-45d9-b69d-8118ce62ffce')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

IMPORTANT: If omitted, the gateway uses the default (oldest) active connection, which may fail if it's not an MCP connection.

## MCP Reference

All MCP tools use `POST` method:

| Tool | Description | Schema |
|------|-------------|--------|
| `query_granola_meetings` | Chat with meeting notes using natural language | [schema](schemas/query_granola_meetings.json) |
| `list_meetings` | List meetings with metadata and attendees | [schema](schemas/list_meetings.json) |
| `get_meetings` | Retrieve detailed content for specific meetings | [schema](schemas/get_meetings.json) |
| `get_meeting_transcript` | Get raw transcript (paid tiers only) | [schema](schemas/get_meeting_transcript.json) |

### Query Meetings

Chat with your meeting notes using natural language queries:
```bash
POST /granola/query_granola_meetings
Content-Type: application/json

{
  "query": "What action items came from my meetings this week?"
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "You had 2 recent meetings:\n**Feb 4, 2026 at 7:30 PM** - \"Team sync\" [[0]](https://notes.granola.ai/d/abc123)\n- Action item: Review Q1 roadmap\n- Action item: Schedule follow-up with engineering\n**Jan 27, 2026 at 1:04 AM** - \"Finance integration\" [[1]](https://notes.granola.ai/d/def456)\n- Discussed workflow automation platforms\n- Action item: Evaluate n8n vs Zapier"
    }
  ],
  "isError": false
}
```

**Use cases:**
- "What action items were assigned to me?"
- "Summarize my meetings from last week"
- "What did we discuss about the product launch?"
- "Find all mentions of budget in my meetings"

### List Meetings

List your meetings with metadata including IDs, titles, dates, and attendees:
```bash
POST /granola/list_meetings
Content-Type: application/json

{}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "<meetings_data from=\"Jan 27, 2026\" to=\"Feb 4, 2026\" count=\"2\">\n<meeting id=\"0dba4400-50f1-4262-9ac7-89cd27b79371\" title=\"Team sync\" date=\"Feb 4, 2026 7:30 PM\">\n    <known_participants>\n    John Doe (note creator) from Acme <john@acme.com>\n    Jane Smith from Acme <jane@acme.com>\n    </known_participants>\n  </meeting>\n\n<meeting id=\"4ebc086f-ba8d-49e8-8cd1-ed81ac8f2e3b\" title=\"Finance integration\" date=\"Jan 27, 2026 1:04 AM\">\n    <known_participants>\n    John Doe (note creator) from Acme <john@acme.com>\n    </known_participants>\n  </meeting>\n</meetings_data>"
    }
  ],
  "isError": false
}
```

**Response fields in XML format:**
- `meetings_data`: Container with `from`, `to` date range and `count`
- `meeting`: Individual meeting with `id`, `title`, and `date` attributes
- `known_participants`: List of attendees with name, role, company, and email

### Get Meetings

Retrieve detailed content for specific meetings by ID:
```bash
POST /granola/get_meetings
Content-Type: application/json

{
  "meeting_ids": ["0dba4400-50f1-4262-9ac7-89cd27b79371"]
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "<meetings_data from=\"Feb 4, 2026\" to=\"Feb 4, 2026\" count=\"1\">\n<meeting id=\"0dba4400-50f1-4262-9ac7-89cd27b79371\" title=\"Team sync\" date=\"Feb 4, 2026 7:30 PM\">\n  <known_participants>\n  John Doe (note creator) from Acme <john@acme.com>\n  </known_participants>\n  \n  <summary>\n## Key Decisions\n- Approved Q1 roadmap\n- Budget increased by 15%\n\n## Action Items\n- @john: Review design specs by Friday\n- @jane: Schedule engineering sync\n</summary>\n</meeting>\n</meetings_data>"
    }
  ],
  "isError": false
}
```

**Response includes:**
- Meeting metadata (id, title, date, participants)
- `summary`: AI-generated meeting summary with key decisions and action items
- Enhanced notes and private notes (when available)

### Get Meeting Transcript

Retrieve the raw transcript for a specific meeting (paid tiers only):
```bash
POST /granola/get_meeting_transcript
Content-Type: application/json

{
  "meeting_id": "0dba4400-50f1-4262-9ac7-89cd27b79371"
}
```

**Response (paid tier):**
```json
{
  "content": [
    {
      "type": "text",
      "text": "<transcript meeting_id=\"0dba4400-50f1-4262-9ac7-89cd27b79371\">\n[00:00:15] John: Let's get started with the Q1 planning...\n[00:01:23] Jane: I've prepared the budget breakdown...\n[00:03:45] John: That looks good. What about the timeline?\n</transcript>"
    }
  ],
  "isError": false
}
```

**Response (free tier):**
```json
{
  "content": [
    {
      "type": "text",
      "text": "Transcripts are only available to paid Granola tiers"
    }
  ],
  "isError": true
}
```

## Code Examples

### JavaScript

```javascript
const response = await fetch('https://gateway.maton.ai/granola/query_granola_meetings', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.MATON_API_KEY}`
  },
  body: JSON.stringify({
    query: 'What were the action items from my last meeting?'
  })
});
const data = await response.json();
console.log(data.content[0].text);
```

### Python

```python
import os
import requests

# Query meeting notes
response = requests.post(
    'https://gateway.maton.ai/granola/query_granola_meetings',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'query': 'What were the action items from my last meeting?'
    }
)
print(response.json())
```

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Granola connection |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited (approx 100 req/min) |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `granola`. For example:

- Correct: `https://gateway.maton.ai/granola/query_granola_meetings`
- Incorrect: `https://gateway.maton.ai/query_granola_meetings`

### Troubleshooting: MCP Parameter Errors

MCP tools return validation errors when required parameters are missing:

```json
{
  "content": [
    {
      "type": "text",
      "text": "MCP error -32602: Input validation error: Invalid arguments for tool get_meetings: [\n  {\n    \"code\": \"invalid_type\",\n    \"expected\": \"array\",\n    \"received\": \"undefined\",\n    \"path\": [\"meeting_ids\"],\n    \"message\": \"Required\"\n  }\n]"
    }
  ],
  "isError": true
}
```

## Notes

- All IDs are UUIDs (with or without hyphens)
- MCP tool responses wrap content in `{"content": [{"type": "text", "text": "..."}], "isError": false}` format
- Users can only query their own meeting notes; shared notes from others are not accessible
- Basic (free) plan users are limited to notes from the last 30 days
- The `get_meeting_transcript` tool is only available on paid Granola tiers

## Resources

- [Granola MCP Documentation](https://docs.granola.ai/help-center/sharing/integrations/mcp)
- [Granola Help Center](https://docs.granola.ai)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
