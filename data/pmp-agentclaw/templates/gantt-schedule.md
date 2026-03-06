# Project Schedule

## Gantt Chart

```mermaid
gantt
    title {{PROJECT_NAME}} Schedule
    dateFormat  YYYY-MM-DD
    axisFormat  %d %b

    section {{PHASE_1}}
    {{TASK_1}}     :a1, {{START_DATE}}, {{DURATION}}d
    {{TASK_2}}     :a2, after a1, {{DURATION}}d

    section {{PHASE_2}}
    {{TASK_3}}     :a3, after a2, {{DURATION}}d
    {{TASK_4}}     :a4, {{START_DATE}}, {{DURATION}}d

    section {{PHASE_3}}
    {{TASK_5}}     :{{START_DATE}}, {{DURATION}}d
    {{MILESTONE}}  :milestone, {{DATE}}, 0d
```

---

## Task Details

### Critical Path Tasks

| Task ID | Task Name | Duration | Start | End | Dependencies | Owner |
|---------|-----------|----------|-------|-----|--------------|-------|
| T-001 | {{TASK}} | {{DAYS}}d | {{DATE}} | {{DATE}} | None | {{OWNER}} |
| T-002 | {{TASK}} | {{DAYS}}d | {{DATE}} | {{DATE}} | T-001 | {{OWNER}} |
| crit | {{TASK}} | {{DAYS}}d | {{DATE}} | {{DATE}} | T-001, T-002 | {{OWNER}} |
| ... | ... | ... | ... | ... | ... | ... |

**Critical Path:** {{PATH_TASKS}}
**Total Duration:** {{TOTAL_DAYS}} days
**Float Available:** {{FLOAT_DAYS}} days

---

## Milestones

| Milestone | Date | Criteria | Status |
|-----------|------|----------|--------|
| M-001 | {{DATE}} | {{DESCRIPTION}} | 🟡 Planned |
| M-002 | {{DATE}} | {{DESCRIPTION}} | ⚪ Not Started |
| M-003 | {{DATE}} | {{DESCRIPTION}} | ⚪ Not Started |

---

## Three-Point Estimates

For critical tasks:

| Task | Optimistic (O) | Most Likely (M) | Pessimistic (P) | PERT (O+4M+P)/6 |
|------|----------------|-----------------|-----------------|-----------------|
| {{TASK}} | {{DAYS}} | {{DAYS}} | {{DAYS}} | {{DAYS}} |

---

**Last Updated:** {{DATE}}