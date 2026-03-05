# Active Maintenance Skill

**Automated system health and memory metabolism for OpenClaw.**

Inspired by the `ClawIntelligentMemory` project, this skill ensures Kim Assistant's environment stays clean and its memory stays dense.

---

## Features

1. **System Health Checks**: Monitor disk usage and critical resources.
2. **Auto-Cleanup**: Remove aged temporary files and artifacts.
3. **Memory Metabolism (M3)**: 
   - Exact deduplication of memory fragments.
   - Resource distillation: Summarizing dense notes into core insights.
4. **Decision Logging**: Every maintenance cycle is logged to `MEMORY/DECISIONS/` for auditability.

---

## Usage

### Run Full Maintenance
```bash
python3 /root/.openclaw/workspace/scripts/nightly_optimizer.py
```

### Log a Decision
```python
from decision_logger import log_decision
log_decision(title="Example", ...)
```

---

## Configuration

Located in `scripts/nightly_optimizer.py`:
- `TEMP_DIRS`: List of directories to clean.
- `threshold`: Disk usage percentage to trigger warnings.
- `days`: Age of files to cleanup.

---
*Created: 2026-02-12 | By Kim Assistant*
