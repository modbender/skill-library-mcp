# HEARTBEAT.md - Periodic Task Checklist

## Memory Extraction (Every 24 Hours)

```bash
python3 /home/node/.openclaw/workspace/scripts/extract_memory.py
```

Scans for unprocessed daily memory files and auto-extracts to database + MEMORY.md.

## Rotating Checks (Execute 2-3 per heartbeat)

- [ ] **Database Query Test**: `python3 scripts/db_query.py | head -5`
- [ ] **Workspace Status**: `git status --short`
- [ ] **Backup Verification**: `ls -lt system_backup/ | head -3`
- [ ] **Skill Health**: Check for any skill errors in recent sessions

## Priority Order

1. Memory extraction (highest priority)
2. Database health check
3. Workspace/git status
4. Backup verification
5. Other maintenance tasks

---

*Execute tasks in priority order. If time-constrained, prioritize memory extraction.*
