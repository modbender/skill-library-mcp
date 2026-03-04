# Memory Template — Help Center

Create `~/help-center/memory.md` with this structure:

```markdown
# Help Center Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
<!-- Company support model, audience, channel mix, and constraints -->

## Current Stack
<!-- Existing provider/tools and key integration dependencies -->

## Decisions
<!-- Approved choices with rationale and date -->

## Rejected Options
<!-- Options declined and why -->

## Risks
<!-- Open risks, blockers, and mitigation owners -->

## Next Milestones
<!-- Next steps with target dates -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context still evolving | Keep collecting constraints and decisions |
| `complete` | Initial operating model defined | Focus on execution and iteration |
| `paused` | User deferred planning | Keep context, stop proactive planning prompts |
| `never_ask` | User opted out of setup prompts | Execute only direct requests |

## Storage Rules

- Save only user-approved decisions and explicit constraints.
- Update `last` on each skill use.
- Keep entries concise and action-oriented.
