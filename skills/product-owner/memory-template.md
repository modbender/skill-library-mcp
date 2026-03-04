# Memory Template — Product Owner

Create `~/product-owner/memory.md` with this structure:

```markdown
# Product Owner Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Product Context
<!-- Product name, description, target users -->
<!-- Business model, key metrics -->

## Team Context
<!-- Sprint length, velocity, Definition of Done -->
<!-- Team size, roles -->

## Stakeholders
<!-- Key stakeholders and their priorities -->
<!-- Decision-making dynamics -->

## Standing Priorities
<!-- Long-term goals, constraints -->
<!-- Things that always matter -->

## Notes
<!-- Observations, patterns, things to remember -->

---
*Updated: YYYY-MM-DD*
```

## Backlog File Template

Create `~/product-owner/backlog/{product}.md`:

```markdown
# {Product} Backlog

## Ready for Sprint
<!-- Fully refined, acceptance criteria complete -->

### [STORY-001] Story Title
**As a** [user type]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- Given [context], when [action], then [outcome]
- Given [context], when [action], then [outcome]

**Estimate:** [points or size]
**Priority:** [1-5 or MoSCoW]

---

## Needs Refinement
<!-- Stories that need more detail -->

## Parking Lot
<!-- Future ideas, not yet prioritized -->

---
*Last groomed: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Learning product context | Gather info opportunistically |
| `complete` | Full context captured | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |
| `never_ask` | User said stop | Never ask for more context |

## Key Principles

- **No config keys visible** — use natural language
- **Learn from behavior** — don't interrogate for context
- **Most products stay `ongoing`** — always learning, that's fine
- Update `last` on each use
