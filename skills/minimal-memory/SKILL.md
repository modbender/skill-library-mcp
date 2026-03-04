---
name: minimal-memory
description: Maintain clean, efficient memory files with GOOD/BAD/NEUTRAL categorization and semantic search. Use when managing agent memory, deciding what to store, searching past memories, or organizing knowledge. Triggers on: memory cleanup requests, "remember this", "search memory", memory organization discussions, or when MEMORY.md grows too large.
---

# Minimal Memory Management

Keep agent memory lean, searchable, and actionable through structured categorization and two-tier storage.

## Core Principle

**MEMORY.md = Long-term essentials (GOOD/BAD learnings only)**
**memory/YYYY-MM-DD.md = Daily operations (GOOD/BAD/NEUTRAL tagged)**

## Information Categorization

Tag every memory entry with its value:

| Tag | Meaning | Keep in MEMORY.md? | Example |
|-----|---------|-------------------|---------|
| `[GOOD]` | Worked well, repeat | ✅ Yes | `[GOOD] CSV batch format prevents duplicates` |
| `[BAD]` | Failed, avoid | ✅ Yes | `[BAD] Bird CLI blocked by X anti-automation` |
| `[NEUTRAL]` | Facts, context, state | ❌ No | `[NEUTRAL] Day 5 of 30-day media plan` |

### Writing Rules
1. **Always tag** new entries in daily files
2. **Be specific**: What worked/failed and why
3. **One tag per entry** - pick the strongest category
4. **NEUTRAL expires**: Archive after 30 days unless promoted to GOOD/BAD

## What Goes Where

### MEMORY.md (Categorized Learnings)
Keep under 150 lines. Only GOOD and BAD entries:

```markdown
## GOOD - What Works
- `[GOOD]` Cron jobs with CSV batching = zero duplicates
- `[GOOD]` Browser tool > CLI for X.com automation
- `[GOOD]` Moltbook "crypto" submolt for token posts

## BAD - What to Avoid  
- `[BAD]` Never use bird CLI for X (anti-bot blocks it)
- `[BAD]` Don't post identical content across platforms
```

### memory/YYYY-MM-DD.md (Daily Log)
All three categories with full context:

```markdown
# 2026-02-15

## [GOOD]
- Fixed duplicate posting with 4-batch CSV structure
- Created 10 cron jobs for complete automation

## [BAD]  
- Old CSV format caused content duplication (now deprecated)

## [NEUTRAL]
- Day 5 of 30-day media plan
- Posted $ZEN token shill at 07:00 batch
```

## Quick Commands

### Search Memory
```bash
# Search all memory files
~/.openclaw/skills/minimal-memory/scripts/search.sh "duplicate posting"

# Search only GOOD learnings
~/.openclaw/skills/minimal-memory/scripts/search.sh --good "CSV"

# Search only BAD learnings  
~/.openclaw/skills/minimal-memory/scripts/search.sh --bad "CLI"

# Recent entries only (last 7 days)
~/.openclaw/skills/minimal-memory/scripts/search.sh --recent "cron job"
```

### Daily Memory
```bash
# Create today's memory file with template
~/.openclaw/skills/minimal-memory/scripts/daily.sh

# Add entry with auto-tagging
~/.openclaw/skills/minimal-memory/scripts/add.sh GOOD "Browser tool works better than CLI"
```

### Cleanup
```bash
# Review and migrate GOOD/BAD to MEMORY.md
~/.openclaw/skills/minimal-memory/scripts/cleanup.sh

# Archive old NEUTRAL entries (>30 days)
~/.openclaw/skills/minimal-memory/scripts/archive.sh
```

## Workflow

### When Writing a Memory
1. **Tag it**: Is this GOOD, BAD, or NEUTRAL?
2. **Write to daily file** with tag prefix
3. **Weekly review**: Promote GOOD/BAD to MEMORY.md
4. **Archive NEUTRAL** after 30 days

### When Searching
1. **Use search script** for fast grep across all files
2. **Check MEMORY.md first** for established patterns
3. **Fall back to daily files** for specific context
4. **Prefer recent entries** unless looking for historical

### Weekly Cleanup
1. Read last 7 days of daily files
2. Extract `[GOOD]` and `[BAD]` entries
3. Add to MEMORY.md "GOOD" and "BAD" sections
4. Remove duplicates, condense similar items
5. Ensure MEMORY.md < 150 lines

## Anti-Patterns

❌ **Don't** skip tagging - every entry needs a category
❌ **Don't** put NEUTRAL in MEMORY.md
❌ **Don't** let MEMORY.md grow past 200 lines
❌ **Don't** keep NEUTRAL entries forever (30 day max)
❌ **Don't** create topical files - use daily + search

✅ **Do** search before asking user "did we try this?"
✅ **Do** migrate GOOD/BAD weekly
✅ **Do** be specific in failure/success descriptions
✅ **Do** trust the search script to find context

## Migration from Old System

If MEMORY.md has untagged content:

1. Read entire MEMORY.md
2. Categorize each entry: GOOD/BAD/NEUTRAL
3. Move NEUTRAL to appropriate daily file
4. Keep GOOD/BAD in MEMORY.md with tags
5. Future entries: always tag in daily files first
