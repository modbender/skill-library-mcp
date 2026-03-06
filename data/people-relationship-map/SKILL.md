---
name: people-relationship-map
description: >
  Personal CRM and relationship graph for OpenClaw. Tracks people, their
  connections to each other, and what you know about them. Stores everything
  as Obsidian-friendly Markdown + a JSON graph index. Use when you want to
  remember who knows who, prepare for meetings, or get nudged about stale
  relationships.
version: 0.1.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
    homepage: https://github.com/gobiraj/people-relationship-map
---

# People Relationship Map

A lightweight personal CRM that tracks people as nodes and their connections
as edges. Everything is stored as Obsidian-compatible Markdown files (one per
person) with a JSON graph index for fast querying.

## Workspace layout

```
<workspace>/people/
├── _graph.json          # Node + edge index (source of truth for connections)
├── _alex-chen.md        # One Markdown file per person
├── _jordan-lee.md
└── ...
```

Each person file uses this template:

```markdown
# Alex Chen

- **Tags:** #colleague #engineering
- **Org:** Acme Corp
- **Role:** Staff Engineer
- **Met:** 2025-06-15
- **Last contact:** 2026-02-20
- **Tier:** close

## Notes
- 2026-02-20 — Mentioned looking for a new apartment in Brooklyn
- 2026-01-10 — Helped me debug the auth migration

## Connections
- [[Jordan Lee]] — same team at Acme
- [[Sam Patel]] — college roommates
```

The `_graph.json` file stores the machine-readable graph:

```json
{
  "nodes": {
    "alex-chen": {
      "displayName": "Alex Chen",
      "tags": ["colleague", "engineering"],
      "org": "Acme Corp",
      "role": "Staff Engineer",
      "met": "2025-06-15",
      "lastContact": "2026-02-20",
      "tier": "close",
      "file": "_alex-chen.md"
    }
  },
  "edges": [
    {
      "from": "alex-chen",
      "to": "jordan-lee",
      "label": "same team at Acme"
    }
  ]
}
```

## Commands

All commands go through the Python script. Run them via:

```bash
python3 {baseDir}/scripts/relmap.py <command> [options]
```

### Add a person

```bash
python3 {baseDir}/scripts/relmap.py add \
  --name "Alex Chen" \
  --tags colleague,engineering \
  --org "Acme Corp" \
  --role "Staff Engineer" \
  --tier close \
  --note "Met at the offsite in Denver"
```

Tiers: `close`, `regular`, `acquaintance` (default: `acquaintance`).

### Link two people

```bash
python3 {baseDir}/scripts/relmap.py link \
  --from "Alex Chen" \
  --to "Jordan Lee" \
  --label "same team at Acme"
```

### Add a note to a person

```bash
python3 {baseDir}/scripts/relmap.py note \
  --person "Alex Chen" \
  --text "Mentioned looking for a new apartment in Brooklyn"
```

This also bumps `lastContact` to today.

### Touch (update last contact without a note)

```bash
python3 {baseDir}/scripts/relmap.py touch --person "Alex Chen"
```

### Query commands

```bash
# Show everything about a person
python3 {baseDir}/scripts/relmap.py show --person "Alex Chen"

# Find who is connected to a person
python3 {baseDir}/scripts/relmap.py connections --person "Alex Chen"

# Find all people at an org
python3 {baseDir}/scripts/relmap.py query --org "Acme Corp"

# Find by tag
python3 {baseDir}/scripts/relmap.py query --tag engineering

# Find by tier
python3 {baseDir}/scripts/relmap.py query --tier close

# Search notes for a keyword
python3 {baseDir}/scripts/relmap.py search --query "apartment"

# List all people
python3 {baseDir}/scripts/relmap.py list
```

### Relationship staleness report

```bash
python3 {baseDir}/scripts/relmap.py stale \
  --close-days 14 \
  --regular-days 30 \
  --acquaintance-days 90 \
  --format message
```

Returns a ready-to-send digest of people you haven't contacted within
their tier threshold.

### Export graph as Mermaid (optional utility)

```bash
python3 {baseDir}/scripts/relmap.py mermaid
```

Prints a Mermaid `graph LR` diagram you can paste into any Markdown
renderer.

## Auto-capture behavior

When the user mentions a person in conversation and provides relational
context, the agent SHOULD silently run the appropriate command:

- "I just had coffee with Alex Chen" → `touch --person "Alex Chen"` +
  `note --person "Alex Chen" --text "Had coffee together"`
- "Alex and Jordan work on the same team" → `link --from "Alex" --to "Jordan" --label "same team"`
- "Remember that Sam's birthday is March 12" → `note --person "Sam" --text "Birthday: March 12"`

Only auto-capture when the intent is clear. If ambiguous, ask the user
before persisting. Keep confirmations brief: "Noted for Alex ✓" style.

## Cron — weekly relationship digest

A cron job should run the staleness report weekly and deliver results to
the user's primary channel (WhatsApp/Telegram). Recommended schedule:
every Sunday at 9:00 AM.

```
python3 {baseDir}/scripts/relmap.py stale --format message
```

The `--format message` flag produces a concise, chat-friendly digest.

## Tips for the agent

- Normalize names: "Alex", "Alex Chen", "alex chen" should all resolve
  to the same node. The script does fuzzy matching on the stored names.
- When the user says "who do I know at [Company]?", use `query --org`.
- When the user says "tell me about [Person]", use `show --person`.
- When the user says "who is connected to [Person]?", use `connections`.
- Before a meeting, offer to pull up the person's card with `show`.
- The Markdown files are designed for Obsidian — wikilinks, tags, and
  frontmatter all work natively if the user syncs the people/ folder.
