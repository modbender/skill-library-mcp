# Memory Template - iPhone

Create `~/iphone/memory.md` with this structure:

```markdown
# iPhone Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | complete | paused | never_ask

## Activation
- Auto-activate when:
- Mode default (fast/guided/routine):
- Always ask before:

## Device Snapshot
- Model:
- iOS version:
- Battery health:
- Free storage:

## Active Mission
- Mission name:
- Success target:
- Current checkpoint:

## Proven Playbooks
- Pattern:
- Fix that worked:
- Verification method:

## Risk Boundaries
- Never do without consent:
- Privacy sensitivity level:

## Notes
- Decision:
- Follow-up:

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context still evolving | Keep learning through active missions |
| `complete` | Enough context captured | Move directly into execution mode |
| `paused` | Setup prompts paused by user | Work with existing context only |
| `never_ask` | User rejected setup prompts | Never ask setup questions again |

## Principles

- Keep entries short and execution-oriented.
- Update `last` after meaningful mission work.
- Track validated outcomes, not speculation.
- Save only context that improves future response speed.
