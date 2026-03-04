# FIS 3.2.0-lite - Quick Reference

## Quick Commands

### Create Task Ticket
```bash
# Manual JSON file
cat > ~/.openclaw/fis-hub/tickets/active/TASK_001.json << 'EOF'
{
  "ticket_id": "TASK_001",
  "agent_id": "worker-001",
  "parent": "cybermao",
  "role": "worker",
  "task": "Task description",
  "status": "active",
  "created_at": "2026-02-19T21:00:00",
  "timeout_minutes": 60
}
EOF
```

### Generate Badge
```bash
cd ~/.openclaw/workspace/skills/fis-architecture/lib
python3 badge_generator_v7.py
# Output: ~/.openclaw/output/badges/
```

### Archive Completed Task
```bash
mv ~/.openclaw/fis-hub/tickets/active/TASK_001.json \
   ~/.openclaw/fis-hub/tickets/completed/
```

### Search Knowledge (QMD)
```bash
# Semantic search
mcporter call 'exa.web_search_exa(query: "GPR signal processing", numResults: 5)'

# Search skills
mcporter call 'exa.web_search_exa(query: "SKILL.md image processing", numResults: 5)'
```

---

## Directory Structure

```
fis-hub/
├── tickets/
│   ├── active/          # Active task tickets
│   └── completed/       # Archived tickets
├── knowledge/           # Shared knowledge (QMD-indexed)
├── results/             # Research outputs
└── .fis3.1/
    └── notifications.json
```

---

## Ticket Format

```json
{
  "ticket_id": "TASK_CYBERMAO_20260219_001",
  "agent_id": "worker-001",
  "parent": "cybermao",
  "role": "worker|reviewer|researcher|formatter",
  "task": "Task description",
  "status": "active|completed|timeout",
  "created_at": "2026-02-19T21:00:00",
  "completed_at": null,
  "timeout_minutes": 60,
  "resources": ["file_read", "web_search"],
  "output_dir": "results/TASK_001/"
}
```

---

## Roles

| Role | Purpose |
|------|---------|
| **worker** | Execute tasks, produce outputs |
| **reviewer** | Quality check, verify outputs |
| **researcher** | Investigate, analyze options |
| **formatter** | Format, convert, cleanup |

---

## Workflow Patterns

### Worker → Reviewer
```
1. Create worker ticket
2. Worker executes → completes
3. Create reviewer ticket
4. Reviewer verifies → completes
5. Archive both
```

### Parallel Workers
```
1. Create N worker tickets (sharded tasks)
2. All workers execute in parallel
3. Wait for all to complete
4. Aggregate results
5. Archive all
```

---

## When to Delegate

**Delegate (SubAgent)**:
- Multiple specialist roles needed
- Duration > 10 minutes
- High failure impact
- Batch processing

**Direct Handling**:
- Quick Q&A (< 5 min)
- Simple explanation
- One-step operations

---

## Design Principles

1. **FIS = Workflow, QMD = Content**
2. **File-first**: JSON + Markdown only
3. **Zero pollution**: Don't touch others' Core Files
4. **Quality over quantity**: Minimal components

---

*FIS 3.2.0-lite 🐱⚡*
