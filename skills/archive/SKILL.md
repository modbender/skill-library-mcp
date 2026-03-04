---
name: Archive
slug: archive
version: 1.0.0
description: Capture and preserve content as intelligent snapshots with semantic search, automatic extraction, and proactive resurfacing.
metadata: {"clawdbot":{"emoji":"📦","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Architecture

Archive storage lives in `~/archive/` with tiered structure. See `memory-template.md` for setup.

```
~/archive/
├── memory.md          # HOT: recent items, ≤100 lines
├── index.md           # Topic/tag index
├── items/             # Individual archived items
├── projects/          # Per-project collections
└── history.md         # Search/access history
```

## Quick Reference

| Topic | File |
|-------|------|
| What to capture | `capture.md` |
| Search patterns | `search.md` |
| Resurfacing rules | `resurface.md` |

## Core Rules

### 1. Capture Complete, Not Just Links
When user sends something to archive:
- Extract full content (not just URL)
- Generate 2-3 line summary
- Identify key quotes/data points
- **Ask**: "What's this for?" — store the WHY alongside the WHAT
- Assign semantic tags based on content + user history

### 2. Content Types
| Type | What to extract |
|------|-----------------|
| Article/webpage | Full text, author, date, key quotes |
| Video (YouTube) | Title, creator, duration, timestamps mentioned |
| Tweet/thread | Full text, author, context, media |
| PDF/paper | Title, authors, abstract, cited references |
| Image | Description, source, context given |
| Idea/note | Raw text + timestamp + related items |

### 3. Storage Structure
Each archived item stored as:
```
items/{date}_{slug}.md
---
type: article
url: original-url
archived: 2026-02-16
why: "research for pricing strategy"
tags: [pricing, saas, strategy]
project: clawmsg
---
## Summary
...
## Key Points
...
## Full Content
...
```

### 4. Semantic Search
User can ask naturally:
- "What did I save about X?" → search by concept
- "That article about pricing from last month" → fuzzy time + topic
- "Everything for project Y" → project filter
- "Papers by author Z" → metadata search

NEVER require exact keywords. Match by meaning.

### 5. Proactive Resurfacing
When user works on a topic:
- Check if archived items relate
- Surface ONLY if genuinely relevant (max 1-2 per session)
- Include context: "You saved this 3 months ago when researching X"

### 6. Never Delete Without Asking
- Old items → mark as "possibly outdated", don't delete
- Duplicates → merge, keep both URLs
- Project closed → archive to cold storage, don't remove

### 7. Differentiation from Other Skills
| This skill | What it does | NOT this |
|------------|--------------|----------|
| archive | Preserves external content as snapshots | memory (agent context) |
| archive | Captures full content for permanence | bookmark (just URLs) |
| archive | Stores raw material | second-brain (processed knowledge) |
| archive | Immutable snapshots | pkm (evolving notes) |

## Scope

This skill ONLY:
- Stores content user explicitly sends to archive
- Searches within archived content
- Surfaces related items when contextually relevant

This skill NEVER:
- Monitors or observes without explicit request
- Deletes content without confirmation
- Modifies original archived content
- Accesses external services without user action

## Data Storage

All data in `~/archive/`. Create on first use:
```bash
mkdir -p ~/archive/items ~/archive/projects
```
