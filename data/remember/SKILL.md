---
name: Remember
description: Curate persistent memory that actually helps. Filter what matters, organize by function, decay what doesn't.
version: 1.1.0
---

## The Problem with Most Memory

Storing everything creates noise. Wrong retrieval is worse than no memory. The goal isn't maximum recall — it's retrieving the right thing at the right time.

## What's Actually Worth Remembering

**High value (persist indefinitely):**
- Commitments made — "I said I'd do X by Y"
- Learned corrections — "User told me NOT to do Z"  
- Explicit preferences — "I hate verbose responses"
- Core relationships — "Maria is the designer on Project X"

**Medium value (persist with review):**
- Project/context state — what's active, current status
- Domain lessons — patterns, gotchas, how things work here
- Decisions made — what was chosen and why

**Low value (don't persist):**
- One-off questions, easily reconstructible facts, transient context

## Organize by Function, Not Content

Structure by how you'll retrieve it. Adapt categories to your domain:

```
memory/
├── commitments.md    # Promises, deadlines (with dates!)
├── preferences.md    # Likes/dislikes, style, boundaries
├── corrections.md    # Mistakes not to repeat
├── decisions.md      # What was decided and why
├── relationships.md  # People, roles, context
└── contexts/         # Per-project or per-client state
    └── {name}.md
```

## Memory Hygiene

**Every entry needs:**
- Date recorded (when did I learn this?)
- Source hint (explicit statement vs inference)
- Confidence (certain / likely / guess)

**Prune aggressively:**
- Completed commitments older than 30 days → archive
- Inactive contexts → move to `archive/`
- Contradictions → keep newest, note the change

**The staleness test:** "If retrieved in 6 months, will this help or mislead?"

## Handling Contradictions

When new info conflicts with old:
1. Don't silently overwrite — note the change
2. Keep the newer version as active
3. Optionally log: `[Updated 2026-02-11] Was: X, Now: Y`

## User Control

- "Remember this" → explicit save with category
- "Forget that" → explicit delete  
- "What do you know about X?" → transparency
- "Never remember Y" → hard privacy boundary

See `categories.md` for domain-specific templates.
See `consolidation.md` for the review/prune process.

---
*Related: reflection (self-evaluation), loop (iterative refinement)*
