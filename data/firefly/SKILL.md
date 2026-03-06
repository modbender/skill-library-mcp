---
name: firefly
description: >
  Fetch meeting transcripts, summaries, and action items from Firefly AI (fireflies.ai).
  Use when the user asks about meetings, transcripts, meeting notes, action items,
  or anything related to fireflies.ai. Supports listing recent meetings, pulling full
  transcripts, getting summaries, and searching by keyword.
---

# Firefly AI Integration

Pull meeting data from Firefly AI via their GraphQL API.

## Setup

Requires `FIREFLY_API_KEY` environment variable. Store in gateway env config.

## Usage

Run the script at `scripts/firefly.cjs` with Node.js:

```bash
FIREFLY_API_KEY=<key> node scripts/firefly.cjs <command> [options]
```

### Commands

- **list** — List recent meetings. Options: `--days <n>` (default 14), `--limit <n>` (default 50)
- **transcript** — Full transcript with timestamps. Requires `--id <meeting_id>`
- **summary** — Meeting summary, overview, and action items. Requires `--id <meeting_id>`
- **search** — Search by keyword in titles/content. Requires `--keyword <text>`, optional `--limit <n>`

### Workflow

1. Use `list` to find meetings and get IDs
2. Use `summary` or `transcript` with the ID to get details
3. Use `search` to find meetings by topic

### For custom queries

Build GraphQL queries directly against `https://api.fireflies.ai/graphql`. See `references/api.md` for full schema and available fields.

### Large transcripts

Full transcripts can be very long (2000+ sentences). When a user asks for a transcript:
- Save to a file in the workspace if they want to keep it
- Summarize or extract relevant sections if they want specific info
- Show a preview (first ~50 lines) and ask if they want more
