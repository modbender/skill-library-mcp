# Memory Template - Apple Maps (MacOS)

Create `~/apple-maps/memory.md` with this structure:

```markdown
# Apple Maps Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
- Preferred search patterns (for example categories, addresses, neighborhoods)
- Preferred route mode defaults (driving, walking, transit)
- Typical location scope (city, region, travel context)

## Command Reliability
- Working command path with last verified date
- Known permission prompts and outcomes
- Fallback behavior when primary path fails

## Safety Defaults
- Confirmation required before sharing links: yes/no
- Confirmation required before opening multiple links: yes/no
- Preferred preview detail level before launch

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
- Update `last` whenever command reliability or safety defaults change.
- Record confirmations for sharing and bulk actions as safety evidence.
- Never remove prior notes without explicit user instruction.
