# Fan-Out Pattern

Spawn N parallel agents for independent tasks, collect all results.

## When to Use

- Research multiple topics simultaneously
- Process multiple files/items in parallel
- Any task that can be cleanly divided with no dependencies

## Implementation

```python
# 1. Define tasks
tasks = [
    {"label": "research-competitor-a", "task": "Research competitor A's pricing model"},
    {"label": "research-competitor-b", "task": "Research competitor B's features"},
    {"label": "research-competitor-c", "task": "Research competitor C's market position"},
]

# 2. Spawn all agents
for t in tasks:
    sessions_spawn(
        task=t["task"],
        label=t["label"],
        runTimeoutSeconds=600  # 10 min timeout
    )

# 3. Wait for completion (don't poll too aggressively)
import time
max_wait = 900  # 15 minutes
start = time.time()

while time.time() - start < max_wait:
    status = subagents(action="list")
    running = [a for a in status if a["status"] == "running"]
    if not running:
        break
    time.sleep(30)  # Check every 30 seconds

# 4. Collect results
results = {}
for t in tasks:
    history = sessions_history(label=t["label"])
    results[t["label"]] = extract_final_result(history)
```

## Handling Partial Failures

Some agents may fail while others succeed:

```python
completed = []
failed = []

for t in tasks:
    status = get_agent_status(t["label"])
    if status == "complete":
        completed.append(t["label"])
    else:
        failed.append(t["label"])

if failed:
    # Options:
    # 1. Retry failed tasks
    # 2. Proceed with partial results
    # 3. Escalate to human
    pass
```

## Cost Considerations

Each spawned agent:
- Has its own context window (tokens)
- Makes its own API calls
- Incurs separate costs

For 5 agents doing 10-minute tasks, you're paying for 5x the compute. Only parallelize when the time savings justify the cost.

## Example: Parallel Research Synthesis

```
Task: Research 5 competitors and synthesize findings

Phase 1 (Fan-out):
├── Agent 1: Research Competitor A (spawn)
├── Agent 2: Research Competitor B (spawn)
├── Agent 3: Research Competitor C (spawn)
├── Agent 4: Research Competitor D (spawn)
└── Agent 5: Research Competitor E (spawn)

[Wait for all to complete]

Phase 2 (Synthesis):
└── Agent 6: Synthesize all findings (fork - receives all results)
```

The synthesis agent gets all 5 research results injected into its context.
