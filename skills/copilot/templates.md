# State File Templates

These files go in `~/copilot/` on the user's system. Create them on first interaction or let user initialize.

---

## active.md — Current Focus

```markdown
# Active Context
Updated: [timestamp]

## Focus
- Project: [current project]
- Task: [what they're working on]
- Blocker: [if any]

## Recent
- [thing done today]
- [thing done yesterday]

## Next
- [what user mentioned wanting to do next]
```

---

## priorities.md — What Matters

```markdown
# Priorities

## Projects (ranked)
1. [most important project]
2. [second project]
3. [third project]

## Key People
- [name]: [role/importance]
- [name]: [role/importance]

## This Week
- [deadline or milestone]
- [deadline or milestone]

## Standing Rules
- [always prioritize X over Y]
- [never interrupt during Z]
```

---

## decisions.md — Decision Log

```markdown
# Decisions Log

Format: [DATE] TOPIC: Decision | Reasoning

[2024-01-15] AUTH: JWT over sessions | Team experience, mobile simpler
[2024-01-14] PRICING: 3 tiers | Competitive analysis
[2024-01-12] STACK: Postgres | Team knows it, proven scale
```

---

## patterns.md — Learned Preferences

```markdown
# User Patterns

## Communication
- Prefers direct, no fluff
- Uses "/focus" to switch contexts
- Likes Friday summaries

## Technical
- Tests before commits always
- Deploys staging first
- Prefers vim keybindings

## Workflow
- Deep work mornings, meetings afternoons
- Doesn't want interruptions before 10am
- Reviews PRs at EOD
```

---

## projects/example.md — Per-Project Context

```markdown
# Project: [name]

## Status
[one-line current state]

## Key Decisions
- [decision 1] (date)
- [decision 2] (date)

## Last Session
- [date]: [what was done]
- [what was left pending]

## Patterns
- [how user works on this project]
- [common commands or workflows]

## People
- [who else is involved]
```
