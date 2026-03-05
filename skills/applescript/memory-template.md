# Memory Template - AppleScript

Create `~/applescript/memory.md` with this structure:

```markdown
# AppleScript Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
- Main app domains automated by the user
- Preferred output format and response style
- Read-only vs write-allowed boundaries

## App Profiles
- App name
- Verified dictionary terms
- Known command patterns that work
- Known failures and fixes

## Safety Defaults
- Confirm before destructive actions: yes/no
- Confirm before bulk edits: yes/no
- Require read-back after writes: yes/no

## Notes
- Reusable snippets worth keeping
- Common edge cases from repeated tasks

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context still evolving | Keep learning while operating |
| `complete` | Stable defaults exist | Use defaults and ask only for ambiguity |
| `paused` | User wants fewer setup questions | Operate with minimal prompts |
| `never_ask` | User asked to stop preference questions | Use explicit instructions only |

## Rules

- Keep notes in natural language outside the status block.
- Update `last` whenever preferences or app profiles change.
- Never delete prior safety notes without explicit user request.
