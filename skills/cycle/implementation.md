# Implementing Cycles

Cycles become skills with this structure:

```
cycle-name/
├── SKILL.md          # Main workflow (short)
├── phases/
│   ├── plan.md       # How to execute Plan
│   ├── execute.md    # How to execute Execute
│   └── verify.md     # How to execute Verify
└── state.md          # Persistent preferences
```

## SKILL.md Template

```markdown
---
name: [Cycle Name]
description: [What it produces]
---

## Workflow
[Phase] → [Phase] → [Phase] → [Phase]

## Phases
- **[Phase 1]** — [input] → [output]
- **[Phase 2]** — [input] → [output]
...

Read `phases/[name].md` for each phase details.
```

## State Persistence

The `state.md` file tracks:
- **Preferences** — User's style, tools, constraints
- **Patterns** — What works for this user
- **Never** — Things that consistently fail
