---
name: cord-trees
description: |
  Dynamic task tree orchestration inspired by Cord protocol. Agent builds its own coordination tree at runtime — deciding decomposition, parallelism, and dependencies dynamically. Implements spawn (isolated context) vs fork (inherited context) as first-class primitives, plus ask (human elicitation) and serial (ordered sequences).
  
  Use when: complex goals that need dynamic decomposition, tasks where the agent should decide how to break down work, multi-agent coordination with runtime flexibility, human-in-the-loop checkpoints.
  
  Triggers: "figure out how to do X", "decompose this task", "build a task tree for", "dynamic orchestration", "cord-style", "self-organizing agents"
version: 1.0.0
license: MIT
metadata:
  openclaw:
    requires:
      tools: ["sessions_spawn", "subagents", "read", "write"]
---

# Cord Trees — Dynamic Task Tree Orchestration

Build coordination trees at runtime. You decide the decomposition, not the developer.

Inspired by [Cord](https://github.com/kimjune01/cord) by June Kim.

## Core Concept

Instead of following a pre-defined workflow, you analyze the goal and build your own task tree:

```
Goal: "Evaluate whether to migrate from REST to GraphQL"

You decide:
├── #1 spawn: Audit current REST API surface
├── #2 spawn: Research GraphQL trade-offs  
├── #3 ask: How many concurrent users? (blocked-by: #1)
├── #4 fork: Comparative analysis (blocked-by: #2, #3)
└── #5 fork: Write recommendation (blocked-by: #4)
```

The tree emerges from your analysis, not from hardcoded logic.

## Five Primitives

### 1. SPAWN — Isolated Context

Child gets only its task prompt. Clean slate.

```python
spawn(
    goal="Research GraphQL adoption patterns",
    prompt="Search for case studies of REST→GraphQL migrations...",
    blocked_by=[]  # Can start immediately
)
```

**Use when:** Task is self-contained, doesn't need sibling context.

### 2. FORK — Inherited Context

Child receives all completed sibling results injected into prompt.

```python
fork(
    goal="Synthesize findings into recommendation",
    prompt="Based on the research, write a recommendation...",
    blocked_by=["research-rest", "research-graphql", "user-scale"]
)
```

**Use when:** Synthesis, analysis, or integration requiring prior work.

### 3. ASK — Human Elicitation

Pause for human input. Creates a checkpoint.

```python
ask(
    question="How many concurrent users do you serve?",
    options=["<1K", "1K-10K", "10K-100K", ">100K"],
    blocked_by=["audit-api"]  # Ask after audit provides context
)
```

**Use when:** Decision requires human knowledge or approval.

### 4. SERIAL — Ordered Sequence

Children execute in order. Implicit dependencies.

```python
serial([
    {"goal": "Draft report", "type": "spawn"},
    {"goal": "Review draft", "type": "ask"},
    {"goal": "Finalize report", "type": "fork"}
])
```

**Use when:** Strict ordering required.

### 5. GOAL — Root Node

The top-level objective. You decompose it into children.

## Implementation with OpenClaw

Map Cord primitives to OpenClaw tools:

| Cord Primitive | OpenClaw Implementation |
|----------------|-------------------------|
| `spawn` | `sessions_spawn(task=prompt, label=id)` |
| `fork` | `sessions_spawn` with sibling results in task |
| `ask` | Message human, wait for response |
| `serial` | Spawn sequentially, wait between each |
| `read_tree` | Read state file + `subagents list` |
| `complete` | Write result to state file |

## State File

Track the tree in `cord-state.json`:

```json
{
  "goal": "Evaluate REST to GraphQL migration",
  "nodes": {
    "#1": {
      "type": "spawn",
      "goal": "Audit REST API",
      "status": "complete",
      "result": "47 endpoints, 12 nested...",
      "blockedBy": [],
      "sessionKey": "abc123"
    },
    "#2": {
      "type": "spawn",
      "goal": "Research GraphQL",
      "status": "running",
      "blockedBy": [],
      "sessionKey": "def456"
    },
    "#3": {
      "type": "ask",
      "goal": "Get user scale",
      "status": "waiting",
      "question": "How many concurrent users?",
      "options": ["<1K", "1K-10K", "10K-100K", ">100K"],
      "blockedBy": ["#1"]
    },
    "#4": {
      "type": "fork",
      "goal": "Comparative analysis",
      "status": "blocked",
      "blockedBy": ["#2", "#3"]
    }
  },
  "nextId": 5
}
```

## Workflow

### Phase 1: Analyze Goal

Read the goal. Think about:
- What are the major components?
- What can run in parallel?
- What has dependencies?
- Where do I need human input?
- What needs synthesis (fork) vs isolation (spawn)?

### Phase 2: Build Initial Tree

Create nodes for the first level of decomposition:

```python
# Initialize state
state = {
    "goal": user_goal,
    "nodes": {},
    "nextId": 1
}

# Add initial nodes
add_node(state, type="spawn", goal="Research A", blockedBy=[])
add_node(state, type="spawn", goal="Research B", blockedBy=[])
add_node(state, type="fork", goal="Synthesize", blockedBy=["#1", "#2"])

write("cord-state.json", state)
```

### Phase 3: Execute Ready Nodes

Find nodes that are ready (all blockedBy complete):

```python
def get_ready_nodes(state):
    ready = []
    for id, node in state["nodes"].items():
        if node["status"] != "blocked":
            continue
        deps = node["blockedBy"]
        if all(state["nodes"][d]["status"] == "complete" for d in deps):
            ready.append(id)
    return ready
```

For each ready node:

**If spawn:**
```python
sessions_spawn(
    task=node["prompt"],
    label=node_id,
    runTimeoutSeconds=600
)
node["status"] = "running"
```

**If fork:**
```python
# Inject sibling results
sibling_context = collect_sibling_results(state, node)
full_prompt = f"{node['prompt']}\n\nContext from prior work:\n{sibling_context}"

sessions_spawn(task=full_prompt, label=node_id)
node["status"] = "running"
```

**If ask:**
```python
# Message human
message(action="send", message=f"Question: {node['question']}\nOptions: {node['options']}")
node["status"] = "waiting"
# Wait for response, then mark complete with answer
```

### Phase 4: Monitor & Update

Poll running agents, update state on completion:

```python
while has_running_or_blocked(state):
    # Check agent status
    agents = subagents(action="list")
    
    for agent in agents:
        node = find_node_by_session(state, agent["sessionKey"])
        if agent["status"] == "complete":
            # Get result from session history
            result = get_agent_result(agent)
            node["status"] = "complete"
            node["result"] = result
    
    # Dispatch newly ready nodes
    for node_id in get_ready_nodes(state):
        dispatch_node(state, node_id)
    
    save_state(state)
    wait(30)  # Don't poll too aggressively
```

### Phase 5: Synthesize

When all nodes complete, the final fork node produces the result.

## Dynamic Restructuring

Agents can modify their own subtree at runtime:

```python
# Child agent realizes it needs more research
add_child_node(
    parent="#2",
    type="spawn",
    goal="Deep dive on performance implications",
    blockedBy=[]
)
```

This is what makes Cord-style orchestration powerful — the tree evolves based on what agents discover.

## Spawn vs Fork Decision Guide

| Situation | Use |
|-----------|-----|
| Independent research task | spawn |
| Task that doesn't need sibling context | spawn |
| Cheap to restart if it fails | spawn |
| Synthesis or analysis across prior work | fork |
| Final integration step | fork |
| Task that builds on discoveries | fork |

**Default to spawn.** Use fork only when context inheritance is required.

## Human-in-the-Loop Patterns

### Approval Gate
```
#1 spawn: Draft proposal
#2 ask: "Approve this proposal?" (blocked-by: #1)
#3 fork: Implement approved proposal (blocked-by: #2)
```

### Clarification
```
#1 spawn: Initial analysis
#2 ask: "Which direction should we focus?" (blocked-by: #1)
#3 spawn: Deep dive on chosen direction (blocked-by: #2)
```

### Periodic Checkpoints
```
#1 spawn: Phase 1
#2 ask: "Continue to phase 2?" (blocked-by: #1)
#3 spawn: Phase 2 (blocked-by: #2)
#4 ask: "Continue to phase 3?" (blocked-by: #3)
...
```

## Example: Full Decomposition

Goal: "Create a comprehensive competitor analysis report"

```
#1 [spawn] List top 5 competitors
    └── No dependencies, starts immediately

#2 [spawn] Research Competitor A (blocked-by: #1)
#3 [spawn] Research Competitor B (blocked-by: #1)
#4 [spawn] Research Competitor C (blocked-by: #1)
#5 [spawn] Research Competitor D (blocked-by: #1)
#6 [spawn] Research Competitor E (blocked-by: #1)
    └── All parallel, isolated research

#7 [fork] Identify patterns across competitors (blocked-by: #2-#6)
    └── Needs all research results

#8 [ask] "Focus on pricing, features, or positioning?" (blocked-by: #7)
    └── Human steers direction

#9 [fork] Deep analysis on chosen focus (blocked-by: #8)
    └── Builds on patterns + human input

#10 [fork] Write final report (blocked-by: #9)
    └── Synthesis of everything
```

## Error Handling

```python
if node["status"] == "failed":
    # Options:
    # 1. Retry (reset to blocked)
    node["status"] = "blocked"
    node["retries"] = node.get("retries", 0) + 1
    
    # 2. Skip (mark complete with error)
    node["status"] = "complete"
    node["result"] = f"FAILED: {error}"
    
    # 3. Escalate (ask human)
    add_node(state, type="ask", 
             question=f"Node {id} failed. Retry, skip, or abort?",
             blockedBy=[])
```

## Attribution

This skill implements patterns from the [Cord protocol](https://github.com/kimjune01/cord) by June Kim, adapted for OpenClaw's `sessions_spawn` and `subagents` primitives.
