---
name: memory-pruner
description: Automatically prune and compact agent memory files to prevent unbounded growth. Circular buffer for logs, importance-based retention for state, and configurable size limits.
user-invocable: true
metadata: {"openclaw": {"emoji": "🧹", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Memory Pruner

Keep your agent's memory lean. Automatically prune logs, compact state files, and enforce size limits so your agent never runs out of disk or context window.

## Why This Exists

Agents accumulate memory files over time. Logs grow unbounded. State files collect stale entries. Eventually your boot-up reads 50K tokens of memory and half of it is outdated. Memory Pruner enforces limits and keeps only what matters.

## Commands

### Prune a memory file (keep last N lines)
```bash
python3 {baseDir}/scripts/memory_pruner.py prune --file ~/wake-state.md --max-lines 200
```

### Prune a log directory (circular buffer, keep last N files)
```bash
python3 {baseDir}/scripts/memory_pruner.py prune-logs --dir ~/agents/logs/ --keep 7
```

### Compact a state file (remove sections matching a pattern)
```bash
python3 {baseDir}/scripts/memory_pruner.py compact --file ~/wake-state.md --remove-before "2026-02-14"
```

### Check memory sizes
```bash
python3 {baseDir}/scripts/memory_pruner.py stats --dir ~/
```

### Dry run (show what would be pruned)
```bash
python3 {baseDir}/scripts/memory_pruner.py prune --file ~/wake-state.md --max-lines 200 --dry-run
```

## Features

- **Line-based pruning**: Keep last N lines of any file
- **Log rotation**: Circular buffer for log directories (keep last N files, delete oldest)
- **Date-based compaction**: Remove entries older than a cutoff date
- **Size limits**: Enforce max file sizes in bytes
- **Dry run mode**: Preview changes before applying
- **Stats**: Overview of memory file sizes and growth rates
