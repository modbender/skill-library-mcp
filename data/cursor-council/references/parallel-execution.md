# Parallel Execution Guide

Detailed guide for running multiple Cursor instances on independent tasks.

## Session Management

### Initialize Multiple Sessions
```bash
# Clean start
for i in 1 2 3; do
  tmux kill-session -t cursor-$i 2>/dev/null || true
  tmux new-session -d -s cursor-$i
  tmux send-keys -t cursor-$i "cd $PROJECT_DIR" Enter
done
```

### Session Naming Conventions
- `cursor-1`, `cursor-2`, `cursor-3` - Generic parallel workers
- `cursor-frontend`, `cursor-backend` - Module-based naming
- `cursor-feat-123`, `cursor-bug-456` - Task-based naming

## Task Decomposition Strategies

### By Module (No Conflicts)
```
cursor-1: src/frontend/**
cursor-2: src/backend/**
cursor-3: src/shared/** (wait for 1 & 2)
```

### By Feature Branch
```
cursor-1: git checkout feat/auth && agent -p '...'
cursor-2: git checkout feat/dashboard && agent -p '...'
```

### By File Type
```
cursor-1: *.test.ts (tests)
cursor-2: *.ts (implementation)
cursor-3: *.md (documentation)
```

## Monitoring Strategies

### Round-Robin Polling
```bash
while true; do
  for session in cursor-1 cursor-2 cursor-3; do
    echo "=== $session ==="
    tmux capture-pane -t $session -p | tail -10
  done
  sleep 30
done
```

### Completion Detection
Look for these patterns in output:
- `Agent completed` - Task finished
- `waiting for approval` - Needs intervention
- Percentage indicators (e.g., `78.9%`)
- Error messages

### Progress Dashboard
```bash
# One-liner status check
for s in cursor-{1,2,3}; do 
  echo -n "$s: "
  tmux capture-pane -t $s -p 2>/dev/null | grep -oE '[0-9]+\.[0-9]+%' | tail -1 || echo "running"
done
```

## Error Handling

### Common Issues

| Issue | Detection | Resolution |
|-------|-----------|------------|
| Session hung | No output for 5+ min | `tmux send-keys -t $session C-c` |
| Approval needed | "Waiting for approval" | `tmux send-keys -t $session y` |
| Git conflict | "CONFLICT" in output | Pause, resolve manually |
| OOM | Process killed | Reduce parallel count |

### Recovery Workflow
```bash
# 1. Check what went wrong
tmux capture-pane -t cursor-1 -p -S -200 > cursor-1-log.txt

# 2. Kill if stuck
tmux send-keys -t cursor-1 C-c
sleep 2

# 3. Restart with adjusted task
tmux send-keys -t cursor-1 "agent -p 'Revised task...' --force" Enter
```

## Resource Limits

### Recommended Parallelism
| Machine | Max Cursors | Notes |
|---------|-------------|-------|
| 8GB RAM | 2 | Conservative |
| 16GB RAM | 3-4 | Standard |
| 32GB+ RAM | 5-6 | Heavy workloads |

### API Rate Limits
- Claude Max: Check subscription tier
- Consider staggered starts (30s delay between launches)

## Best Practices

1. **Always use branches** - Each Cursor on its own branch if touching same repo
2. **Clear task boundaries** - Explicit file lists prevent conflicts
3. **Staged dependencies** - Don't launch dependent tasks until prerequisites complete
4. **Log everything** - Capture pane output before killing sessions
5. **Graceful shutdown** - Let tasks complete rather than killing mid-work
