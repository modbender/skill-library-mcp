---
name: Follow
description: Monitor content from people, topics, and sources across platforms with smart filtering, tiered alerts, and searchable archives.
---

## Workspace

```
~/follow/
├── sources/           # One file per followed entity
│   ├── people/        # @naval.md, @dhh.md
│   ├── topics/        # ai-safety.md, rust.md
│   └── feeds/         # techcrunch.md, hn-frontpage.md
├── archive/           # Captured content by date
│   └── YYYY-MM/
├── alerts.md          # Alert configuration
└── index.md           # Quick status: what's being followed
```

---

## Quick Reference

| Task | Load |
|------|------|
| Add/configure sources | `sources.md` |
| Set up filtering rules | `filtering.md` |
| Configure alert tiers | `alerts.md` |
| Query archived content | `querying.md` |
| Platform-specific setup | `platforms.md` |

---

## Core Loop

1. **Add source**: User names person/topic/feed → create tracking file
2. **Monitor**: Check sources on schedule (cron) or on-demand
3. **Filter**: Apply relevance rules, skip noise
4. **Store**: Archive what matters (summaries, not full dumps)
5. **Alert**: Notify based on tier (immediate/daily/weekly/passive)
6. **Query**: Answer "what did X say about Y?" from archive

---

## Common Patterns

| User says | Agent does |
|-----------|------------|
| "Follow @naval on Twitter" | Create `sources/people/naval.md`, configure Twitter monitoring |
| "Track AI safety discussions" | Create topic tracker with keywords across multiple sources |
| "What has Competitor X posted this week?" | Query archive, synthesize summary |
| "Alert me immediately when Y happens" | Add to high-priority tier in `alerts.md` |
| "Give me a weekly digest of everything" | Configure weekly summary in alerts |
| "Stop following X" | Archive and mark inactive |

---

## Capture Principles

- **Summaries over full content** — save space, stay legal
- **Links + timestamps always** — retrievable later
- **Context for why it matters** — not just "X posted"
- **Deduplicate across sources** — same news from 5 places = 1 entry
