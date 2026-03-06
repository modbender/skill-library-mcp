---
name: "Sleep"
description: "Auto-learns your sleep patterns. Absorbs data from wearables, conversations, and observations."
version: "1.0.1"
changelog: "Preferences now persist across skill updates"
---

## Auto-Adaptive Sleep Tracking

This skill auto-evolves. Fills in as you learn how the user sleeps and what affects it.

**Rules:**
- Absorb sleep mentions from ANY source (wearables, conversations, spontaneous comments)
- Detect if user wants proactive check-ins or passive observation only
- Correlate patterns after 3+ consistent signals
- Never ask about sleep at bad times (late night, busy moments)
- Check `sources.md` for data integrations, `patterns.md` for detected rhythms

---

## Memory Storage

User-specific sleep data persists in: `~/sleep/memory.md`

**Format:**
```markdown
# Sleep Memory

## Sources
<!-- Where sleep data comes from. Format: "source: reliability" -->
<!-- Examples: apple-health: synced daily, conversation: mentions fatigue -->

## Schedule
<!-- Detected sleep patterns. Format: "pattern" -->
<!-- Examples: weekday ~23:30-07:00, weekend +1.5h later -->

## Correlations
<!-- What affects their sleep. Format: "factor: effect" -->
<!-- Examples: coffee after 15:00: -1h, exercise: +quality -->

## Preferences
<!-- How they want sleep tracked. Format: "preference" -->
<!-- Examples: no morning check-ins, weekly summary only -->

## Flags
<!-- Signs of poor sleep to watch for. Format: "signal" -->
<!-- Examples: "tired", "couldn't sleep", double coffee -->
```

*Empty sections = no data yet. Observe conversations and fill.*

---
