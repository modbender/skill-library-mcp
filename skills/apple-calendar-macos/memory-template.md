# Memory Template - Apple Calendar

Create `~/apple-calendar-macos/memory.md` with this structure:

```markdown
# Apple Calendar Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
- Accounts already synced in Calendar.app
- Preferred command path and fallback
- Preferred calendars and naming patterns
- Timezone and date formatting defaults

## Command Reliability
- Working command path with last verified date
- Known permission prompts and outcomes
- Fallback behavior when primary path fails

## Safety Defaults
- Confirmation required for delete: yes/no
- Confirmation required for bulk edits: yes/no
- Read-back fields required after writes

## Notes
- Repeated user preferences inferred from behavior
- Common failure modes and proven fixes

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context still evolving | Keep learning while operating |
| `complete` | Defaults are stable | Operate using known preferences |
| `paused` | User wants minimal setup | Avoid extra discovery questions |
| `never_ask` | User asked to stop setup prompts | Use only explicit instructions |

## Rules

- Keep notes in natural language and avoid exposed config-key style outside status fields.
- Update `last` whenever defaults or command reliability changes.
- Record destructive-operation confirmations as safety evidence.
- Never remove prior notes without explicit user instruction.
