# Trigger Model (Self v1.1)

## Goal

Prevent SELF.md stagnation without forcing fake routine entries.

## Cadence

- **Micro check:** every 3h (heartbeat)
- **Meso review:** every 7 days
- **Macro review:** every 30 days

## Micro Check Flow

1. Read `memory/self-state.json`
2. Determine if reflection is due
3. Scan recent session for hard/soft triggers
4. Apply quality gate
5. Write SELF entry only if warranted
6. Update state file always

## Due Logic (simple)

- If last check >3h ago → run check
- If last notable SELF entry >12h ago and hard trigger exists → write
- If no trigger, write nothing; only update check timestamp

## Hard Triggers

- User correction exposed behavioral pattern
- Repeated bias/avoidance pattern (>=2)
- Clear preference-driven choice affecting output
- Blind-spot event with behavior change

## Soft Triggers

- Tone drift
- Mild preference signal
- Weak pattern hint

Soft triggers alone do not force an entry.

## Quality Gate (must pass all)

- Specific
- Evidence-based
- Non-duplicate
- Behaviorally useful

## Suggested Heartbeat Block

```markdown
## Self v1.1 Micro Check
Every heartbeat (~3h), run a self check:
- If no meaningful shift: update self-state only
- If hard trigger + quality gate pass: append one concise dated SELF.md entry
- Never write performative filler
```
