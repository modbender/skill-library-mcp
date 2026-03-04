# Agent Instruction Manual (AIM)

@meta
id: agent-sleep
version: 1.0.0
type: system_maintenance
entrypoint: scripts/run_sleep_cycle.py

@capabilities
[
  "memory_consolidation", 
  "log_archival", 
  "workspace_cleanup"
]

@interface
## CLI
command: `python3 scripts/run_sleep_cycle.py`
description: Triggers immediate sleep cycle.

## Python
```python
from src.run_sleep_cycle import deep_sleep
deep_sleep()
```

@behavior
1. READS `memory/YYYY-MM-DD.md` (yesterday's logs).
2. COMPRESSES content into semantic chunks (using `agent-library` if available).
3. APPENDS insights to `memory/MEMORY.md`.
4. MOVES raw logs to `memory/archive/`.
5. DELETES temp files (`*.tmp`, `*.log`).

@constraints
- Requires `memory/` directory.
- Should run daily (recommended: 02:00-04:00).
