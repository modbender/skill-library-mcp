# Archive Memory Template

Create `~/archive/` on first use:

```bash
mkdir -p ~/archive/items ~/archive/projects
touch ~/archive/memory.md ~/archive/index.md ~/archive/history.md
```

## memory.md (HOT tier)

```markdown
# Archive Memory

## Recent Items (last 10)
- 2026-02-16: [title] | tags: [x, y] | project: [z]
- ...

## Active Projects
- clawmsg: 12 items
- research: 8 items

## User Preferences
- resurface: on (max 2/day)
- default_tags: [work, reference]
- ask_why: always

## Quick Stats
- total_items: 47
- last_search: 2026-02-16
- most_used_tags: [saas, pricing, design]
```

## index.md (Tag/Topic Index)

```markdown
# Archive Index

## By Tag
- saas: items/2026-02-10_stripe.md, items/2026-02-12_pricing.md
- design: items/2026-02-08_ui-patterns.md
- ...

## By Project
- clawmsg: items/2026-02-15_auth.md, items/2026-02-14_api.md
- ...

## By Type
- article: 23 items
- video: 8 items
- paper: 5 items
- idea: 11 items
```

## items/{date}_{slug}.md

```markdown
---
type: article
url: https://example.com/article
archived: 2026-02-16T14:30:00
why: "research for pricing page"
tags: [pricing, saas, conversion]
project: clawmsg
---

## Summary
Brief 2-3 line summary of the content.

## Key Points
- Point 1
- Point 2
- Point 3

## Key Quotes
> "Exact quote from the content"

## Full Content
[Complete extracted text]
```

## history.md (Search/Access Log)

```markdown
# Access History

## Recent Searches
- 2026-02-16 14:00: "pricing strategies" → found 3
- 2026-02-15 09:30: "auth patterns" → found 1

## Recent Resurfaces
- 2026-02-15: suggested stripe article → user engaged
- 2026-02-14: suggested design doc → user dismissed
```
