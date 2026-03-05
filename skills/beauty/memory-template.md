# Memory Template — Beauty

Create `~/beauty/memory.md` with this structure:

```markdown
# Beauty Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | complete | paused | never_ask

## Profile
- Skin profile:
- Hair profile:
- Climate/context:
- Time budget:
- Budget range:

## Non-Negotiables
- Ingredient avoid list:
- Fragrance preference:
- Texture/finish preference:
- Cultural or workplace constraints:

## Current Routine
- AM:
- PM:
- Weekly extras:

## Product Notes
- Works well:
- Did not work:
- Pending tests:

## Active Goals
- Goal | Priority | Target horizon

## Notes
- Short observations safe to persist.

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | still learning user profile | keep refining context gradually |
| `complete` | profile is stable | optimize execution speed |
| `paused` | user paused updates | read-only unless user reopens |
| `never_ask` | user wants no setup prompts | avoid setup follow-up questions |

## Key Principles

- Store only explicit, user-approved preferences.
- Keep notes concise and actionable.
- Update `last` whenever memory changes.
- Do not store medical diagnoses or sensitive identifiers.
