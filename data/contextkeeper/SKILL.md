---
name: contextkeeper
description: ContextKeeper — Safe project state tracking for AI agents. Manual checkpoint creation with validated inputs. No background processes, no PID manipulation, no command execution.
metadata:
  openclaw:
    requires:
      bins: []
    install: []
---

# ContextKeeper 🔮

> Safe project state tracking for AI agents

Keeps track of what you're working on across sessions. Create checkpoints manually, view status in dashboard.

---

## Security

| Risk | Mitigation |
|------|------------|
| Remote Code Execution | No command substitution with user data |
| PID manipulation | No PID files, no process management |
| Background processes | No watchers, no daemons |
| Injection attacks | Input validated and escaped |

---

## Scripts

Two simple foreground scripts:

| Script | Purpose |
|--------|---------|
| `ckpt.sh` | Create checkpoint with message |
| `dashboard.sh` | View project status |

---

## Usage

```bash
# Create checkpoint
./ckpt.sh "Fixed auth issue"

# View status
./dashboard.sh
```

---

## Requirements

- bash
- git (for project detection)

---

**Part of:** [TheOrionAI](https://github.com/TheOrionAI)
