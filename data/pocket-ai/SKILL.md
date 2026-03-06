---
name: Pocket AI Skill
description: Pocket AI captures your meetings, calls, and thoughts via a
  wearable device, then transcribes and indexes everything for semantic search.
---

# Pocket AI Skill

**Voice recording transcription, semantic search, and meeting intelligence across all conversations.**

Pocket AI captures your meetings, calls, and thoughts via a wearable device, then transcribes and indexes everything for semantic search.

## Quick Reference

| What | Value |
|------|-------|
| API Base | `https://public.heypocketai.com/api/v1` |
| API Key | `~/.config/pocket-ai/api_key` |
| Auth | Bearer token |
| Docs | https://docs.heypocketai.com/docs/api |

## Core Capabilities

### 1. Semantic Search (Most Powerful)
Search across ALL recordings by meaning, not just keywords.

```bash
curl -s -X POST \
  -H "Authorization: Bearer $(cat ~/.config/pocket-ai/api_key)" \
  -H "Content-Type: application/json" \
  -d '{"query": "your company manufacturing decisions"}' \
  "https://public.heypocketai.com/api/v1/public/search"
```

**Returns:**
- `userProfile.dynamicContext[]` — AI-built insights from all recordings
- `relevantMemories[]` — Matching transcripts, action items, meeting sections
- Speaker identification, timestamps, relevance scores

### 2. Action Item Extraction
Pocket AI auto-extracts action items from meetings. Search for them:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $(cat ~/.config/pocket-ai/api_key)" \
  -H "Content-Type: application/json" \
  -d '{"query": "action items tasks follow up"}' \
  "https://public.heypocketai.com/api/v1/public/search"
```

### 3. List Tags
```bash
curl -s -H "Authorization: Bearer $(cat ~/.config/pocket-ai/api_key)" \
  "https://public.heypocketai.com/api/v1/public/tags"
```

### 4. List Recordings
```bash
curl -s -H "Authorization: Bearer $(cat ~/.config/pocket-ai/api_key)" \
  "https://public.heypocketai.com/api/v1/public/recordings"
```

### 5. Get Recording Details
```bash
curl -s -H "Authorization: Bearer $(cat ~/.config/pocket-ai/api_key)" \
  "https://public.heypocketai.com/api/v1/public/recordings/{recording_id}"
```

### 6. Download Audio
```bash
curl -s -H "Authorization: Bearer $(cat ~/.config/pocket-ai/api_key)" \
  "https://public.heypocketai.com/api/v1/public/recordings/{recording_id}/audio"
```

---

## High-Value Query Patterns

### Contact Context
*"What has been discussed with [person]?"*
```json
{"query": "conversations with Dylan Acquisition.com"}
{"query": "Adrienne intercompany invoices discussion"}
{"query": "meetings with Charlene"}
```

### Business Decisions
*"What decisions were made about [topic]?"*
```json
{"query": "your company manufacturing team restructuring decisions"}
{"query": "entity streamlining strategy"}
{"query": "trading system rules discussed"}
```

### Action Items & Follow-ups
*"What needs to be done?"*
```json
{"query": "action items tasks todo follow up"}
{"query": "scheduled meetings upcoming"}
{"query": "things to review or approve"}
```

### Personal Insights
*"What have I said about [topic]?"*
```json
{"query": "trading psychology patience discipline"}
{"query": "family financial planning kids college"}
{"query": "team performance frustrations"}
```

### Meeting Summaries
*"What happened in [meeting type]?"*
```json
{"query": "your company staff meeting summary"}
{"query": "financial review discussion"}
{"query": "geopolitical analysis conversation"}
```

---

## Response Structure

### Search Response
```json
{
  "success": true,
  "data": {
    "userProfile": {
      "dynamicContext": [
        "AI-built insight from recordings...",
        "Another pattern detected..."
      ],
      "staticFacts": []
    },
    "relevantMemories": [
      {
        "content": "Transcript segment or action item...",
        "metadata": {"source": "turbopuffer", "sources": ["transcript_segment", "action_item"]},
        "recordingDate": "2026-01-28 01:16:14",
        "recordingId": "uuid",
        "recordingTitle": "Untitled Recording",
        "relevanceScore": 8.19,
        "speakers": "SPEAKER_00, SPEAKER_01",
        "transcriptionId": "uuid"
      }
    ],
    "total": 8,
    "timing": 490
  }
}
```

### Memory Content Types
- **Transcript segment:** `[timestamp] SPEAKER_XX: actual words spoken`
- **Action item:** `Action item: Do the thing`
- **Meeting section:** `(start-end) Section Title - Summary of what was discussed`

---

## Integration Points

### Athena (Family Agent)
- Query meeting context to understand your bandwidth
- "Am I free?" → Check if recent recordings show heavy commitments
- Feed meeting insights into scheduling decisions

### Daily Briefings
- Pull action items from yesterday's meetings
- Summarize key decisions made
- Flag urgent follow-ups

### Task Management
- Auto-surface action items as potential tasks
- Cross-reference with existing todo lists
- Track what's been mentioned but not yet acted on

### Operations Channel
- Post important decisions to #operations
- Alert on critical discussions (team changes, financial decisions)

---

## Tags (Your Categories)

Current tags: `ai`, `business`, `call`, `economy`, `finance`, `game`, `geopolitics`, `hockey`, `outlook`, `personal`, `sales`, `summary`, `test`, `victory`, `weather`, `work`

Use tags to filter or categorize queries.

---

## Heartbeat Integration

During heartbeats, optionally check for new action items:

```python
# Check for recent action items (last 24h)
query = "action items from today"
# Parse response for new follow-ups
# Surface anything urgent
```

---

## Privacy & Security

- All recordings encrypted end-to-end
- Stored on US servers
- API key should remain in `~/.config/pocket-ai/api_key`
- Never log full transcripts to public channels

---

## Troubleshooting

**Empty recordings list?**
- Recordings may need device sync before API access
- Use search endpoint instead (works with synced transcripts)

**Auth errors?**
- Check Bearer token format: `Authorization: Bearer pk_xxx`
- Verify key in `~/.config/pocket-ai/api_key`

**Search returns nothing?**
- Try broader query terms
- Check if recordings have been synced recently

---

## Helper Scripts

### search.sh
```bash
#!/bin/bash
# Usage: ./search.sh "your query"
API_KEY=$(cat ~/.config/pocket-ai/api_key)
curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$1\"}" \
  "https://public.heypocketai.com/api/v1/public/search"
```

### Python Helper
See `pocket_api.py` for full Python integration.
