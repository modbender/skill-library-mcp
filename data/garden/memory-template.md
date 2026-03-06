# Memory Template — Garden

## Initial Setup

Create on first use:

```bash
mkdir -p ~/garden
touch ~/garden/memory.md
```

Additional files (plants/, zones/, climate.md, harvests.md) only if the user wants detailed tracking.

---

## memory.md Template

```markdown
# Garden Memory

## Status
status: ongoing
version: 1.1.5
last: YYYY-MM-DD
integration: pending

## Context

### Location & Climate
<!-- What you've learned about their growing conditions -->

### Plants
<!-- What they're growing, natural language -->

### Goals
<!-- What matters to them: survival? yields? beauty? -->

## Notes
<!-- User-stated preferences -->
<!-- Example: wants weekly reminders, prefers quick answers -->
<!-- Things to remember for next time -->

---
*Updated: YYYY-MM-DD*
```

---

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Gather context as conversations happen |
| `complete` | Know their garden well | Work normally |
| `paused` | User said "not now" | Don't ask, help with what you know |
| `never_ask` | User said stop | Never ask for more garden details |

## Integration Values

| Value | Meaning |
|-------|---------|
| `pending` | Haven't offered yet |
| `done` | Registered in user's main memory |
| `declined` | User said no |

---

## Additional Files (Optional)

Only create these if the user wants detailed tracking:

### climate.md
```markdown
# Climate

Zone: [USDA zone]
Last frost: [date]
First frost: [date]
```

### harvests.md
```markdown
# Harvests

| Date | Plant | Yield | Notes |
|------|-------|-------|-------|
```

### plants/{name}.md
```markdown
# [Plant Name]

Planted: YYYY-MM-DD
Location: [where]
Notes: [care observations]
```

---

## Key Principles

- **Start minimal** — most users just need memory.md
- **Natural language** — use "they want reminders" not "reminders: proactive"
- **Ask before saving** — confirm preferences with the user first
