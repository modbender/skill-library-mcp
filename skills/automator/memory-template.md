# Memory Template - Automator

Create `~/automator/memory.md` with this structure:

```markdown
# Automator Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
- User goals for Automator usage
- Preferred activation behavior
- Read-only boundaries and sensitive locations

## Workflow Profiles
- Workflow path
- Purpose and expected inputs
- Last verified run result
- Known side effects

## Action Catalog Notes
- Verified action names
- Required settings and safe defaults
- Actions to avoid for this user context

## Safety Defaults
- Confirm before write workflows: yes/no
- Confirm before destructive runs: yes/no
- Require read-back verification: yes/no

## Notes
- Reusable command templates
- Frequent failure patterns and fixes

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context still evolving | Keep learning while operating |
| `complete` | Stable defaults exist | Reuse defaults and ask only on ambiguity |
| `paused` | User wants fewer setup questions | Execute with minimal prompts |
| `never_ask` | User requested no preference questions | Use explicit instructions only |

## Rules

- Keep notes in natural language outside the status block.
- Update `last` whenever preferences or workflow profiles change.
- Do not remove prior safety constraints without explicit user request.
