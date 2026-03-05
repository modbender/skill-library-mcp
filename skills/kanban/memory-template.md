# Memory Template - Kanban

Create `~/kanban/memory.md`:

```markdown
# Kanban Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | complete | paused | never_ask

## Integration
- Activation mode: always | explicit-only | selected-projects
- Default board mode: workspace-local | home-shared
- Default lane model: basic | custom

## Context
- Stable preferences learned from user behavior
- Planning cadence and review style

## Notes
- Operational reminders safe to persist

---
*Updated: YYYY-MM-DD*
```

Create `~/kanban/index.md`:

```markdown
# Kanban Index

## Projects
| project_id | aliases | workspace_root | board_mode | board_path | rules_path | log_path | last_used |
|------------|---------|----------------|------------|------------|------------|----------|-----------|
| api-core | backend, core-api | /abs/path/api-core | workspace-local | /abs/path/api-core/.kanban/board.md | /abs/path/api-core/.kanban/rules.md | /abs/path/api-core/.kanban/log.md | YYYY-MM-DD |
| marketing | growth | - | home-shared | ~/kanban/projects/marketing/board.md | ~/kanban/projects/marketing/rules.md | ~/kanban/projects/marketing/log.md | YYYY-MM-DD |

## Resolution Order
1. exact workspace_root match
2. alias match from user message
3. explicit project_id in request
4. fallback to last_used project with confirmation
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | still calibrating | keep learning defaults through usage |
| `complete` | reliable routing and board norms | run without setup prompts |
| `paused` | user paused Kanban setup changes | read existing board only |
| `never_ask` | user does not want setup prompts | never request configuration questions |

## Key Principles

- Keep the index machine-readable and human-readable.
- Update `last` and `last_used` on every successful board write.
- Never store secrets in board or memory files.
- Preserve user custom lane names while keeping core card fields stable.
