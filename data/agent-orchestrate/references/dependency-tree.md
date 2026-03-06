# Dependency Tree Pattern

Complex task graphs with explicit prerequisites. Tasks only start when their dependencies complete.

## When to Use

- Tasks have partial ordering (some parallel, some sequential)
- Complex projects with multiple workstreams
- When you need explicit "blocked-by" relationships

## Data Structure

```json
{
  "tasks": {
    "research-api": {
      "task": "Audit current REST API surface",
      "status": "complete",
      "result": "47 endpoints, 12 nested resources...",
      "blockedBy": []
    },
    "research-graphql": {
      "task": "Research GraphQL trade-offs",
      "status": "complete",
      "result": "Key advantages: reduced over-fetching...",
      "blockedBy": []
    },
    "get-scale": {
      "task": "ASK: How many concurrent users?",
      "status": "complete",
      "result": "10K-100K",
      "blockedBy": ["research-api"]
    },
    "analysis": {
      "task": "Comparative analysis",
      "status": "running",
      "blockedBy": ["research-graphql", "get-scale"]
    },
    "recommendation": {
      "task": "Write migration recommendation",
      "status": "pending",
      "blockedBy": ["analysis"]
    }
  }
}
```

## Implementation

```python
import json

STATE_FILE = "orchestration-state.json"

def load_state():
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_ready_tasks(state):
    """Tasks with all dependencies complete."""
    ready = []
    for name, task in state["tasks"].items():
        if task["status"] != "pending":
            continue
        deps = task["blockedBy"]
        if all(state["tasks"][d]["status"] == "complete" for d in deps):
            ready.append(name)
    return ready

def run_orchestration():
    state = load_state()
    
    while True:
        # Find tasks ready to run
        ready = get_ready_tasks(state)
        
        if not ready:
            # Check if all done or deadlocked
            pending = [t for t, v in state["tasks"].items() if v["status"] == "pending"]
            running = [t for t, v in state["tasks"].items() if v["status"] == "running"]
            
            if not pending and not running:
                print("All tasks complete!")
                break
            elif not running:
                print("Deadlock detected - pending tasks have unmet dependencies")
                break
            else:
                # Wait for running tasks
                time.sleep(30)
                update_running_status(state)
                continue
        
        # Spawn ready tasks
        for task_name in ready:
            task = state["tasks"][task_name]
            
            # Build context from dependencies (fork pattern)
            dep_context = build_dependency_context(state, task["blockedBy"])
            full_task = f"{task['task']}\n\nContext from prior work:\n{dep_context}"
            
            sessions_spawn(task=full_task, label=task_name)
            task["status"] = "running"
        
        save_state(state)
        time.sleep(30)
        update_running_status(state)

def build_dependency_context(state, deps):
    """Collect results from completed dependencies."""
    context = []
    for dep in deps:
        result = state["tasks"][dep].get("result", "")
        context.append(f"[{dep}]: {result}")
    return "\n\n".join(context)
```

## Visualization

```
#1 [complete] Research API surface
#2 [complete] Research GraphQL trade-offs
#3 [complete] ASK: concurrent users? (blocked-by: #1)
#4 [running]  Comparative analysis (blocked-by: #2, #3)
#5 [pending]  Write recommendation (blocked-by: #4)
```

## Human Tasks (ASK nodes)

Some tasks require human input:

```json
{
  "get-scale": {
    "task": "ASK: How many concurrent users?",
    "type": "ask",
    "options": ["<1K", "1K-10K", "10K-100K", ">100K"],
    "status": "waiting",
    "blockedBy": ["research-api"]
  }
}
```

When an ASK task becomes ready:
1. Pause orchestration
2. Message human with question
3. Wait for response
4. Store response as result
5. Mark complete, resume orchestration

## Error Recovery

```python
def handle_failure(state, task_name):
    task = state["tasks"][task_name]
    
    # Option 1: Retry
    task["status"] = "pending"
    task["retries"] = task.get("retries", 0) + 1
    
    # Option 2: Skip (mark as complete with error)
    task["status"] = "complete"
    task["result"] = "SKIPPED: {error}"
    
    # Option 3: Escalate
    notify_human(f"Task {task_name} failed, manual intervention needed")
    task["status"] = "blocked_manual"
```

## Design Tips

1. **Keep the tree shallow** — Deep trees are hard to debug
2. **Make dependencies explicit** — Don't assume ordering
3. **Plan for human checkpoints** — Not everything can be automated
4. **Persist state frequently** — Recovery is easier with checkpoints
5. **Visualize the tree** — Print status regularly for debugging
