---
name: agent-orchestrate
description: |
  Multi-agent orchestration patterns for OpenClaw. Quick reference for spawning sub-agents, parallel work, and basic coordination.
  
  Use when: simple parallel tasks, fan-out/fan-in, basic pipelines.
  
  For advanced dynamic orchestration (agent-built task trees, spawn vs fork, human-in-the-loop), see cord-trees skill instead.
version: 1.0.0
license: MIT
---

# Agent Orchestration — Quick Reference

Simple patterns for multi-agent coordination. For advanced dynamic orchestration, see **cord-trees**.

## Core Primitives

| Tool | Purpose |
|------|---------|
| `sessions_spawn` | Create isolated sub-agent with task |
| `subagents list` | Check status of running agents |
| `subagents steer` | Send guidance to running agent |
| `subagents kill` | Terminate an agent |
| `sessions_send` | Message another session |

## Spawn vs Fork

Two context strategies for sub-agents:

### Spawn (Clean Slate)
Sub-agent gets only its task prompt. No parent context.

```
Use when:
- Task is self-contained
- You want isolation (no context bleed)
- Subtask doesn't need sibling results
- Cheaper/faster (smaller context)
```

Example: "Research competitor X" — doesn't need to know about competitors Y and Z.

### Fork (Context-Inheriting)
Sub-agent receives accumulated results from siblings.

```
Use when:
- Synthesis/analysis across prior work
- Task builds on what others discovered
- Final integration step
```

Implementation: Include sibling results in the task prompt:
```
Task: Synthesize findings into recommendation.

Prior research:
- Competitor A: [result from agent 1]
- Competitor B: [result from agent 2]
- Market trends: [result from agent 3]
```

## Patterns

### 1. Parallel Fan-Out

Spawn N independent agents, wait for all to complete.

```python
# Pseudocode
tasks = ["research A", "research B", "research C"]
for task in tasks:
    sessions_spawn(task=task, label=f"research-{i}")

# Poll until all complete
while not all_complete(subagents list):
    wait(30s)

# Collect results from session histories
```

See: [references/fan-out.md](references/fan-out.md)

### 2. Pipeline (Sequential)

Each agent's output feeds the next.

```
Agent 1: Research → 
  Agent 2: Analyze (using research) → 
    Agent 3: Write (using analysis)
```

Implementation: Spawn agent 1, wait for completion, spawn agent 2 with agent 1's result, etc.

See: [references/pipeline.md](references/pipeline.md)

### 3. Dependency Tree

Tasks with explicit dependencies. Don't start X until Y completes.

```
#1 Research API surface
#2 Research GraphQL tradeoffs  
#3 Analysis (blocked-by: #1, #2)
#4 Recommendation (blocked-by: #3)
```

Implementation: Track state in a JSON file. Poll and spawn when dependencies clear.

See: [references/dependency-tree.md](references/dependency-tree.md)

### 4. Human-in-the-Loop

Pause workflow for human input at checkpoints.

```
Agent 1: Draft proposal →
  [CHECKPOINT: Human approves/rejects] →
    Agent 2: Implement approved proposal
```

Implementation: Agent 1 completes, orchestrator messages human via `sessions_send` or channel message, waits for response before spawning agent 2.

### 5. Supervisor Pattern

Orchestrator monitors agents and intervenes when stuck.

```python
while agents_running:
    status = subagents list
    for agent in status:
        if stuck_too_long(agent):
            subagents steer(target=agent, message="Try alternative approach...")
        if clearly_failed(agent):
            subagents kill(target=agent)
            # Retry or escalate
```

## State Management

For complex orchestrations, track state in a file:

```json
// orchestration-state.json
{
  "tasks": {
    "research-a": {"status": "complete", "result": "...", "sessionKey": "..."},
    "research-b": {"status": "running", "sessionKey": "..."},
    "synthesis": {"status": "blocked", "blockedBy": ["research-a", "research-b"]}
  }
}
```

Update after each spawn, completion check, or state change.

## Best Practices

1. **Label agents clearly** — Use descriptive labels for `subagents list` readability
2. **Set timeouts** — Use `runTimeoutSeconds` to prevent runaways
3. **Don't over-parallelize** — More agents ≠ better. Consider token costs.
4. **Checkpoint expensive work** — Write intermediate results to files
5. **Handle failures** — Decide: retry, skip, or escalate to human
6. **Keep tasks focused** — One clear goal per agent. Easier to debug.

## Anti-Patterns

❌ Polling in tight loops — Use reasonable intervals (30s+)
❌ Spawning agents for trivial tasks — Just do it yourself
❌ Giant context dumps — Summarize, don't copy entire histories
❌ No failure handling — Agents fail. Plan for it.

## Choosing a Pattern

| Situation | Pattern |
|-----------|---------|
| N independent research tasks | Fan-out |
| Step A → Step B → Step C | Pipeline |
| Complex task with prerequisites | Dependency tree |
| Need human approval mid-flow | Human-in-the-loop |
| Long-running with potential issues | Supervisor |
| Simple one-off subtask | Just spawn one agent |

## Quick Reference

```bash
# Spawn a sub-agent
sessions_spawn(task="Do X", label="my-task", runTimeoutSeconds=300)

# Check status
subagents(action="list")

# Send guidance
subagents(action="steer", target="my-task", message="Focus on Y instead")

# Kill runaway
subagents(action="kill", target="my-task")
```
