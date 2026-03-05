# OpenClaw Compatibility - FIS 3.2.0-lite

> **FIS works with all OpenClaw versions supporting file operations**

---

## Current Status

| OpenClaw Version | FIS Version | Compatibility | Notes |
|-----------------|-------------|---------------|-------|
| 2026.2.15+ | 3.2.0-lite | ✅ Fully Compatible | Simplified architecture |
| 2026.2.15 | 3.1.3 | ✅ Compatible | Legacy |
| 2026.2.12 | 3.0.x | ⚠️ Deprecated | Upgrade recommended |

---

## What's New in 3.2.0

### Simplified Architecture

**FIS 3.2** removes components that overlapped with QMD:

| Feature | FIS 3.1 | FIS 3.2 | Handler |
|---------|---------|---------|---------|
| Task Management | Python API | **JSON files** | FIS |
| Memory/Search | memory_manager.py | **QMD** | QMD |
| Skill Discovery | skill_registry.py | **SKILL.md + QMD** | QMD |
| Knowledge Graph | experimental/kg/ | **QMD** | QMD |
| Badge Generation | ✅ Python | ✅ Python | FIS |

### Benefits

- ✅ **No Python setup required** for core functionality
- ✅ **File-first** — tickets are simple JSON
- ✅ **QMD integration** — semantic search built-in
- ✅ **Git-friendly** — all files are text

---

## Compatibility with OpenClaw Features

### 1. Nested SubAgents (2026.2.15+)

**Status:** ✅ Compatible

FIS 3.2 ticket system works with OpenClaw's native nesting:

```json
{
  "ticket_id": "TASK_PARENT",
  "child_tickets": ["TASK_CHILD_1", "TASK_CHILD_2"]
}
```

### 2. Sessions Spawn (Native)

**Status:** ✅ Recommended over FIS subagents

For new projects, consider OpenClaw's native `sessions_spawn`:

```python
# OpenClaw native
sessions_spawn(
    task="Research task",
    agentId="researcher"
)
```

FIS tickets can track these native spawns:

```json
{
  "ticket_id": "TASK_001",
  "openclaw_session": "sess_abc123",
  "status": "active"
}
```

### 3. Memory Search (QMD)

**Status:** ✅ Primary content retrieval

Use OpenClaw's memory search instead of custom registries:

```
# Native OpenClaw
Search my memory for GPR signal processing info...

# Or via QMD
mcporter call 'exa.web_search_exa(query: "GPR signal", numResults: 5)'
```

---

## Migration from FIS 3.1

If using FIS 3.1 components:

| Old Component | New Approach |
|--------------|--------------|
| `memory_manager.py` | Use QMD / OpenClaw memory search |
| `skill_registry.py` | Use SKILL.md + QMD |
| `deadlock_detector.py` | Set `timeout_minutes` in tickets |
| `subagent_lifecycle.py` (3.1) | **JSON tickets directly** |

---

## Recommended Setup

### For New Projects

```bash
# 1. Create minimal structure
mkdir -p ~/.openclaw/my-project/{tickets/active,tickets/completed,knowledge}

# 2. Create tickets as JSON files
# 3. Use QMD for content/search
# 4. Use OpenClaw native sessions_spawn for subagents
```

### For Existing FIS 3.1 Projects

1. Keep existing tickets (format unchanged)
2. Migrate to QMD for queries
3. Archive old Python components
4. Continue using badge generator if desired

---

## Version Matrix

| FIS Version | OpenClaw Min | Status |
|-------------|--------------|--------|
| 3.2.0-lite | 2026.2.15 | ✅ Current |
| 3.1.3 | 2026.2.15 | ⚠️ Legacy |
| 3.0.x | 2026.2.12 | ❌ Deprecated |

---

## Future Roadmap

### 3.2.x (Planned)
- [ ] Discord interactive badges
- [ ] Enhanced ticket templates
- [ ] Native session tracking

### 3.3.0 (Future)
- [ ] Web UI for ticket management
- [ ] Real-time collaboration
- [ ] Integration with OpenClaw dashboard

---

*FIS 3.2.0-lite — Evolving with OpenClaw 🐱⚡*
