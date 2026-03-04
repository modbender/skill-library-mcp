---
name: dispatching-parallel-agents
description: Spawn multiple subagents simultaneously for independent tasks with no shared state — maximize throughput safely
---

# Dispatching Parallel Agents

## When to Use

Use when you have 2+ tasks that are truly independent:
- Different codebases or subsystems
- No shared file modifications
- No shared database migrations
- No dependency between tasks
- Can be tested independently

## When NOT to Use

- Tasks share the same files
- One task depends on another's output
- Schema changes that affect multiple components
- Sequential deployment steps

## Process

### Step 1: Identify Independent Tasks

Verify independence:
- Different directories or repos?
- No shared schema changes?
- No API contract dependencies?
- Can be tested independently?

### Step 2: Spawn Subagents in Parallel

```
# Subagent 1
PARALLEL TASK [1 of 2]: [description]
[Full context, files, code, test commands]
Note: Another agent is working on [other task] in parallel.
No coordination needed.

# Subagent 2
PARALLEL TASK [2 of 2]: [description]
[Full context, files, code, test commands]
Note: Another agent is working on [other task] in parallel.
No coordination needed.
```

### Step 3: Review Each Independently

As each subagent completes, review their output independently using `craftwork:requesting-code-review`.

### Step 4: Merge in Dependency Order

Even if both tasks are independent, merge in logical order:
1. Schema/backend changes first
2. Frontend changes second
3. Infrastructure/deployment last

## Key Principle

When in doubt, run sequentially. Parallel execution saves time but wrong parallelization causes merge conflicts and broken state.
