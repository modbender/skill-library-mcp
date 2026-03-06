# Indie Hacker Memory Setup

Create `~/indie-hacker/` on first use.

## Structure

```
~/indie-hacker/
├── memory.md              # HOT: active projects, week priorities
├── projects/
│   └── {project-name}.md  # Per-project tracking
└── archive/
    └── {killed-name}.md   # Post-mortems
```

## memory.md Template

```markdown
# Active Projects

| Project | Stage | MRR | Priority This Week |
|---------|-------|-----|-------------------|
| appname | launched | $500 | reduce churn |

# Decisions Log

- [date] chose Lemon Squeezy over Stripe (simpler for solo)
- [date] killing featureX — 0 usage after 30 days

# Current Focus
One sentence: what matters this week.
```

## projects/{name}.md Template

```markdown
# {Project Name}

## Vitals
- Stage: idea | validating | building | launched | scaling
- MRR: $X
- Churn: X%
- Users: X

## Stack
- Frontend: 
- Backend:
- Payments:
- Hosting:

## Validation Evidence
- [date] Talked to X, willing to pay $Y
- [date] Competitor Z charges $W

## Key Decisions
- [date] Why we chose A over B
- [date] Pivoted from X to Y because...

## Current Blockers
- Thing preventing progress

## Metrics History
| Month | MRR | Users | Churn |
|-------|-----|-------|-------|
| 2024-01 | $0 | 10 | - |
```

## archive/{name}.md Template

```markdown
# {Project Name} — Post-Mortem

## Timeline
- Started: date
- Killed: date
- Total invested: X hours, $Y

## What Happened
Why this didn't work.

## Lessons
What to do differently next time.

## Assets Salvaged
Code, domains, learnings reusable elsewhere.
```
