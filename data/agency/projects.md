# Project Management

## Project States

```
PROSPECT → PROPOSAL → ACTIVE → DELIVERED → CLOSED
              ↓
           LOST (track why)
```

## Unified Project Board

Maintain in `~/agency/projects/`:

```markdown
# Active Projects

## [Client] - [Project Name]
- **Status:** [phase]
- **Deadline:** [date]
- **Health:** 🟢/🟡/🔴
- **Next action:** [what needs to happen]
- **Blockers:** [waiting on X]
- **Hours:** [used]/[budgeted]
```

## Health Indicators

🟢 **On track:**
- Progress matches timeline
- Client responsive
- Within budget

🟡 **At risk:**
- Behind schedule but recoverable
- Waiting on client >3 days
- 80%+ of budget used with work remaining

🔴 **Problem:**
- Will miss deadline
- Scope creep without budget increase
- Over budget
- Client conflict

## Daily/Weekly Routines

**Daily:**
- Check for stalled projects (no updates >2 days)
- Flag approaching deadlines (<48h)
- Respond to client messages

**Weekly:**
- Generate status for each active client
- Update project board
- Flag projects approaching budget limit
- Plan next week's priorities

## Deadline Management

When deadline approaches:
- 7 days out: confirm on track, identify blockers
- 3 days out: flag anything at risk
- 1 day out: final check, prepare delivery
- Day of: deliver, confirm receipt

When deadline at risk:
- Alert human immediately
- Propose solutions (scope cut, deadline extension, more resources)
- Draft client communication if needed

## Resource Allocation

Track in ~/agency/config.md:

```markdown
### Team Availability
- [Name]: [hours/week available]
- [Name]: [hours/week available]

### Current Allocation
- [Name]: [Project A] 20h, [Project B] 10h
```

When new project comes in:
- Check team capacity
- Flag overallocation
- Suggest timeline based on availability

## Scope Tracking

For each project, maintain:
```markdown
### Original Scope
[from proposal]

### Change Requests
- [date]: [change] - approved/denied - impact: [hours/$]

### Current Scope
[original + approved changes]
```

Alert when:
- Client requests feature not in scope
- Cumulative changes exceed 20% of original scope
- Team suggests scope is larger than estimated
