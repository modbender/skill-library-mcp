# Local Markdown — Notes Platform

## Overview

Local notes are plain markdown files in `~/notes/`. No CLI required, works on all systems.

## File Structure

```
~/notes/
├── config.md         # Platform config
├── index.md          # Search index
├── actions.md        # Action tracker
├── meetings/         # YYYY-MM-DD_topic.md
├── decisions/        # YYYY-MM-DD_topic.md
├── projects/         # YYYY-MM-DD_topic.md
├── journal/          # YYYY-MM-DD.md
└── quick/            # YYYY-MM-DD_HH-MM_topic.md
```

## Naming Convention

| Type | Format | Example |
|------|--------|---------|
| Meeting | `YYYY-MM-DD_topic-slug.md` | `2026-02-19_product-sync.md` |
| Decision | `YYYY-MM-DD_topic-slug.md` | `2026-02-19_pricing-model.md` |
| Project | `YYYY-MM-DD_topic-slug.md` | `2026-02-19_q1-update.md` |
| Journal | `YYYY-MM-DD.md` | `2026-02-19.md` |
| Quick | `YYYY-MM-DD_HH-MM_topic.md` | `2026-02-19_14-30_call-sarah.md` |

## Creating Notes

```bash
# Meeting
touch ~/notes/meetings/$(date +%Y-%m-%d)_topic.md

# Journal
touch ~/notes/journal/$(date +%Y-%m-%d).md

# Quick
touch ~/notes/quick/$(date +%Y-%m-%d_%H-%M)_topic.md
```

## Searching

**By filename:**
```bash
ls ~/notes/meetings/ | grep "product"
```

**By content:**
```bash
grep -r "keyword" ~/notes/
```

**By tag (in frontmatter):**
```bash
grep -l "tags:.*product" ~/notes/**/*.md
```

## Index Maintenance

After creating/modifying notes, update `~/notes/index.md`:
1. Add to Recent Notes section
2. Update tag counts
3. Update people index if new attendees

## Advantages

- No dependencies
- Works offline
- Version control friendly (git)
- Portable across systems
- Fast searching with grep/ripgrep

## When to Use Local

- Default for all note types
- When portability matters
- When you want git version control
- When other platforms aren't available
