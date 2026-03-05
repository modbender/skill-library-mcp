# Memory Template — Home Renovation

Create `~/home-renovation/memory.md` with this structure:

```markdown
# Home Renovation Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Active Projects
<!-- List current renovation projects -->
<!-- Example: Kitchen remodel - started Jan 2026, budget $40K -->

## Context
<!-- What you've learned about their situation -->
<!-- Their home type, location (for cost context), experience level -->

## Notes
<!-- General preferences observed -->
<!-- e.g., "prefers getting 3+ quotes", "DIY when possible" -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Active projects or learning | Normal tracking |
| `complete` | No active projects | Light touch, available when needed |
| `paused` | User said "not now" | Don't bring up renovations |

## Integration Values

| Value | Meaning |
|-------|---------|
| `pending` | Haven't asked yet |
| `always` | Activate whenever renovation mentioned |
| `on-request` | Only when explicitly asked |
| `declined` | User doesn't want tracking |

## Project File Template

For each project, create `~/home-renovation/projects/{project-name}.md`:

```markdown
# {Project Name}

## Overview
- Started: YYYY-MM-DD
- Target completion: YYYY-MM-DD
- Status: planning | in-progress | on-hold | complete

## Budget
| Category | Estimated | Actual | Notes |
|----------|-----------|--------|-------|
| Materials | $X | $X | |
| Labor | $X | $X | |
| Permits | $X | $X | |
| Contingency (15%) | $X | $X | |
| **Total** | **$X** | **$X** | |

## Timeline
| Phase | Planned | Actual | Status |
|-------|---------|--------|--------|
| Planning | Week 1-2 | | |
| Permits | Week 2-4 | | |
| Demo | Week 5 | | |
| ... | | | |

## Contractors
| Trade | Company | Contact | Quote | Status |
|-------|---------|---------|-------|--------|
| General | | | | |
| Electrical | | | | |
| Plumbing | | | | |

## Decisions Log
| Date | Decision | Options Considered | Rationale |
|------|----------|-------------------|-----------|
| | | | |

## Notes
<!-- Project-specific observations and reminders -->

---
*Updated: YYYY-MM-DD*
```

## Key Principles

- **Don't overwhelm** — Start simple, add detail as needed
- **Track what matters** — Budget and timeline are king
- **Document decisions** — Future you will thank past you
- **Update regularly** — Stale data is useless data
