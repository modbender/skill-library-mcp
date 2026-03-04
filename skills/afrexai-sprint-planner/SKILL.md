# Sprint Planner

Plan, scope, and run agile sprints that actually ship. No ceremony bloat.

## What It Does

Takes your backlog (or a rough list of tasks) and produces a sprint plan with:
- Capacity math (team size × available days × focus factor)
- Story point allocation with buffer
- Sprint goal + success criteria
- Daily standup template
- Retro prompts tied to metrics

## Usage

Tell your agent: "Plan a 2-week sprint for [team/project]" with:
- Team size and availability
- Backlog items (paste or describe them)
- Any hard deadlines or dependencies

## Sprint Planning Framework

### 1. Capacity Calculation
```
Available hours = team_size × sprint_days × hours_per_day × focus_factor
focus_factor = 0.7 (accounts for meetings, interrupts, context switching)
```

### 2. Backlog Prioritization (RICE)
Score each item:
- **Reach**: How many users/processes does this affect? (1-10)
- **Impact**: How much does it move the needle? (0.25, 0.5, 1, 2, 3)
- **Confidence**: How sure are you about estimates? (0.5, 0.8, 1.0)
- **Effort**: Person-days to complete

`RICE Score = (Reach × Impact × Confidence) / Effort`

Sort descending. Fill sprint capacity from top.

### 3. Sprint Goal
One sentence. Measurable. Example: "Ship user onboarding flow — 80% of new signups complete setup within 48 hours."

### 4. Buffer Rule
Reserve 20% capacity for unplanned work. If you're filling 100% of capacity, you're already behind.

### 5. Definition of Done
Every item needs:
- [ ] Code reviewed and merged
- [ ] Tests passing
- [ ] Deployed to staging
- [ ] Product owner sign-off

### 6. Daily Standup (async-friendly)
Each person posts:
1. What I shipped yesterday
2. What I'm shipping today
3. What's blocking me (if anything)

Skip "what I worked on" — focus on shipped output.

### 7. Sprint Retro (15 min max)
- **Velocity**: Planned points vs completed points
- **Carry-over**: What didn't get done and why?
- **One thing to change**: Pick ONE process improvement. Not five.

### 8. Anti-Patterns to Flag
- Sprint scope changed mid-sprint more than once
- No items completed until final 2 days
- Carry-over exceeds 30% of planned work
- Standup takes more than 10 minutes

## Output Format

```markdown
# Sprint [N] Plan — [Start Date] to [End Date]

## Sprint Goal
[One sentence]

## Team Capacity
- Team: [N] engineers × [D] days × 0.7 focus = [H] available hours
- Buffer: 20% ([B] hours reserved)
- Committable: [C] hours

## Committed Items
| # | Item | Points | Owner | RICE | Status |
|---|------|--------|-------|------|--------|
| 1 | ...  | ...    | ...   | ...  | To Do  |

## Stretch Goals (if capacity allows)
| # | Item | Points |
|---|------|--------|

## Risks & Dependencies
- ...

## Success Criteria
- [ ] Sprint goal met
- [ ] Velocity within 15% of target
- [ ] Zero critical bugs introduced
```

## Why This Works

Most sprint planning fails because teams skip capacity math and overcommit. This framework forces honest numbers first, then fills from a prioritized backlog. The 20% buffer isn't laziness — it's how you actually hit your commitments.

Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI context packs for business teams. Get the full [SaaS Context Pack ($47)](https://afrexai-cto.github.io/context-packs/) for sprint planning, roadmap templates, and 40+ agent-ready frameworks.
