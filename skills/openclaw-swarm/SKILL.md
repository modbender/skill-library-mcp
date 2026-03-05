# openclaw-swarm

Use OpenClaw Swarm features for advanced subagent orchestration.

## About

This skill provides access to **OpenClaw Swarm** - a fork of OpenClaw with enhanced subagent orchestration:

- **Fork:** https://github.com/Heldinhow/openclaw-swarm
- **Docs:** [SWARM.md](https://github.com/Heldinhow/openclaw-swarm/blob/main/SWARM.md)

## When to Use

Use this skill when:
- Spawning subagents with context sharing
- Coordinating multiple subagents
- Sharing state between subagents
- Running parallel tasks

## Tools Available

### 1. sessions_spawn with contextSharing

Share parent session context with subagents:

```json
{
  "sessions_spawn": {
    "label": "my-task",
    "task": "Do something",
    "contextSharing": "recent"
  }
}
```

**Values:**
- `none` - No context
- `summary` - Compressed summary  
- `recent` - Last messages
- `full` - Complete history

### 2. context_store

Share data between subagents:

```json
// Write
{ "context_store": { "action": "set", "namespace": "project", "key": "data", "value": {...} } }

// Read
{ "context_store": { "action": "get", "namespace": "project", "key": "data" } }
```

**Actions:** `get`, `set`, `delete`, `list`, `subscribe`, `broadcast`

### 3. context_publish

Notify when subagent completes:

```json
{ "context_publish": {
    "action": "publish",
    "eventType": "task_complete",
    "target": "orchestrator",
    "data": { "result": "..." }
  }
}
```

### 4. parallel_spawn

Run multiple subagents in parallel:

```json
{ "parallel_spawn": {
    "tasks": [
      { "label": "task1", "task": "Do this" },
      { "label": "task2", "task": "Do that" }
    ],
    "wait": "all"
  }
}
```

**Wait strategies:**
- `all` - Wait for all
- `any` - Return on first, others continue
- `race` - Return on first

## Patterns

### Parallel Research
```json
{
  "parallel_spawn": {
    "tasks": [
      { "label": "web-search", "task": "Search X" },
      { "label": "docs-search", "task": "Find docs about X" }
    ],
    "wait": "all"
  }
}
```

### Chain Workflow
1. First subagent writes to context_store
2. Second subagent reads from context_store
3. Both notify via context_publish

### Context Pipeline
```json
{
  "sessions_spawn": {
    "label": "processor",
    "task": "Process data",
    "contextSharing": "recent"
  }
}
```

## Auto-Announce

Subagents automatically announce completion:
```
✅ Sub-agent completed: label
   task: ...
   result: ...
   runtime: Xs
```

No polling needed!
