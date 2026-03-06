# Board Template - Kanban

Use this baseline for each `board.md`:

```markdown
# {Project Name} Kanban Board

## Meta
project_id: {project-id}
board_version: 1.0
updated: YYYY-MM-DD HH:MM
lane_model: custom | basic

## Lanes
- backlog
- ready
- in-progress
- blocked
- review
- done

## Cards
| id | title | state | priority | owner | due | depends_on | updated |
|----|-------|-------|----------|-------|-----|------------|---------|
| KB-001 | Define API scope | backlog | P1 | unassigned | - | - | YYYY-MM-DD |

## WIP Limits
- in-progress: 3
- review: 5

## Rules Snapshot
- Use `rules.md` as source of truth for state mapping and custom policies.

## Notes
- Optional short notes for this board only.
```

Use this baseline for each `rules.md`:

```markdown
# {Project Name} Kanban Rules

## State Mapping
| lane_label | canonical_state |
|------------|-----------------|
| backlog | backlog |
| ready | ready |
| in-progress | in-progress |
| blocked | blocked |
| review | review |
| done | done |

## Prioritization
1. blocked dependency with highest downstream impact
2. ready cards with P0/P1
3. due-date pressure
4. age in queue

## Policies
- Create card IDs with `KB-<number>` and never reuse IDs.
- Any done move must include completion evidence in `log.md`.
- Do not move blocked cards unless blocker is resolved.
```

Use this baseline for each `log.md`:

```markdown
# {Project Name} Kanban Log

| timestamp | action | card_id | from_state | to_state | actor | note |
|-----------|--------|---------|------------|----------|-------|------|
| YYYY-MM-DD HH:MM | create | KB-001 | - | backlog | agent | initial setup |
```
