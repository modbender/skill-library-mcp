---
name: memory-transfer
description: Transfer memory files from one OpenClaw agent to another. Use when you need to migrate memory, configuration, or context from one agent to another agent.
metadata:
  {
    "openclaw": { "emoji": "📦" }
  }
---

# Memory Transfer Skill

Transfer memory files and context between OpenClaw agents.

## Use Cases

- Migrate memory from main agent to a sub-agent
- Copy user preferences to a new agent
- Share project context between agents
- Backup agent memory before resets

## How It Works

1. Read source agent's workspace memory files
2. Copy to target agent's workspace
3. Optionally merge with existing memory

## Commands

### List available agents

```bash
ls /home/node/.openclaw/
```

### Transfer memory from source to target

```bash
node memory-transfer.js transfer <source-agent-id> <target-agent-id>
```

### Transfer specific memory file

```bash
node memory-transfer.js transfer <source-agent-id> <target-agent-id> <memory-file>
```

### List agent memories

```bash
node memory-transfer.js list <agent-id>
```

### Preview transfer (dry run)

```bash
node memory-transfer.js transfer <source> <target> --dry-run
```

## Examples

### Transfer main agent memory to coder agent

```bash
node memory-transfer.js transfer main coder
```

### Transfer specific date memory

```bash
node memory-transfer.js transfer main coder 2026-03-01.md
```

### Preview what would be transferred

```bash
node memory-transfer.js transfer main coder --dry-run
```

## Agent Workspaces

OpenClaw agent workspaces are typically at:
- `/home/node/.openclaw/workspace-<agent-id>/`
- Main agent: `/home/node/.openclaw/workspace-main/`

Memory files:
- `MEMORY.md` - Long-term memory
- `memory/YYYY-MM-DD.md` - Daily memories
