# FIS 3.2 Examples

> **Updated for FIS 3.2.0-lite**

---

## Available Examples

### generate_badges.py
Generate visual badge images for subagents.

```bash
cd ~/.openclaw/workspace/skills/fis-architecture/lib
python3 badge_generator_v7.py
```

---

## Legacy Examples (FIS 3.1)

The following examples have been moved to `../archive/deprecated/`:

| Example | Status | Replacement |
|---------|--------|-------------|
| `init_fis31.py` | ❌ Deprecated | Manual directory creation |
| `setup_agent_extension.py` | ❌ Deprecated | Not needed in 3.2 |
| `subagent_pipeline.py` | ❌ Deprecated | Native `sessions_spawn` |

---

## Quick Snippets

### Create a Ticket

```bash
cat > tickets/active/TASK_001.json << 'EOF'
{
  "ticket_id": "TASK_001",
  "agent_id": "worker-001",
  "parent": "cybermao",
  "role": "worker",
  "task": "Analyze GPR signal patterns",
  "status": "active",
  "created_at": "2026-02-19T21:00:00",
  "timeout_minutes": 60
}
EOF
```

### Archive Completed Ticket

```bash
mv tickets/active/TASK_001.json tickets/completed/
```

### Search Knowledge (QMD)

```bash
mcporter call 'exa.web_search_exa(query: "GPR signal processing", numResults: 5)'
```

---

*FIS 3.2.0-lite — Minimal examples for minimal architecture*
