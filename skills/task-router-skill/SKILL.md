---
name: task-router
description: Distributed task queue and agent coordinator for OpenClaw multi-agent systems. Route tasks to specialized agents by capability matching, track task lifecycle, handle async handoffs, rebalance loads, and manage dead letters. Use when: (1) Creating tasks programmatically or from heartbeats, (2) Routing work to specialized agents based on capabilities, (3) Monitoring task status and completion, (4) Coordinating multi-step workflows across agents, (5) Handling async agent work without blocking main sessions.
---

# Task Router

Distributed task queue for OpenClaw multi-agent systems. Central coordination, async handoffs, capability-based routing.

## Quick Start

```bash
# Install skill
clawhub install task-router

# Register an agent
task agent register watson --capabilities "research analysis" --max-concurrent 3

# Create a task
task create --type research --title "Competitor analysis" --priority high

# Router runs automatically via heartbeat
# Check task status
task list --status pending
task show task-abc123
```

## What This Does

**Core Functions:**
- **Enqueue**: Create tasks from any session (main or sub-agent)
- **Route**: Match tasks to agents by capabilities
- **Track**: Monitor task lifecycle (pending → active → complete/failed)
- **Async Coordination**: Hand off work, check back later
- **Dead Letter**: Handle timeouts and failures
- **Rebalance**: Move stuck tasks, retry with fallbacks

**Use Cases:**
- Heartbeat creates research task → auto-routes to research agent
- Main agent spawns work → goes async, checks later
- Multi-step workflows: Task A output → Task B input
- Agent failure → task reassigned to backup agent
- Load balancing across multiple agents with same capabilities

## Configuration

### File Layout
```
~/.openclaw/task-router/
├── config.yaml           # Router settings, timeouts
├── agents.yaml           # Agent registry + capabilities
├── queue/                # Task state
│   ├── pending/          # Waiting for assignment
│   ├── active/           # Assigned to agent
│   ├── completed/        # Finished successfully
│   └── failed/           # Failed, exhausted retries
└── logs/
    └── router.log        # Routing decisions
```

### config.yaml
```yaml
router:
  check_interval: 30           # Seconds between router runs
  default_ttl: 3600            # Default task timeout
  max_retries: 2
  
  strategies:
    default: least-loaded      # round-robin | least-loaded | priority
    by_type:
      research: least-loaded
      image_gen: round-robin
      urgent: priority

  health:
    agent_timeout: 300           # Mark agent unhealthy after seconds
    task_timeout:
      warning: 1800              # Alert at 30 min
      critical: 3600             # Fail at 1 hour

  notifications:
    on_complete: true
    on_fail: true
    channels: [main_session]   # Could add Discord, etc.
```

### agents.yaml (auto-maintained)
```yaml
agents:
  watson:
    id: watson
    emoji: 🔬
    capabilities: [research, analysis, web_search]
    max_concurrent: 3
    current_tasks: [task-abc123, task-def456]
    stats:
      completed: 47
      failed: 2
      avg_duration: 180
    health:
      last_ping: 2026-02-13T09:15:00Z
      status: healthy
    
  picasso:
    id: picasso
    emoji: 🎨
    capabilities: [image_gen, image_edit]
    max_concurrent: 2
    current_tasks: []
```

## Task Schema

```yaml
id: task-abc123
type: research               # Matches agent capability
title: Research Gameye competitors
description: Deep competitive analysis

payload:
  query: Gameye vs competitors
  sources: [web, apollo]
  output_format: markdown
  
created_by: main             # Session label that created it
assigned_to: watson          # null until routed
assigned_by: router          # router | manual | agent

created_at: 2026-02-13T09:00:00Z
assigned_at: 2026-02-13T09:05:00Z
started_at: 2026-02-13T09:06:00Z
completed_at: null
expires_at: 2026-02-13T10:00:00Z  # created_at + ttl

priority: high               # low | normal | high | urgent
ttl: 3600                    # Seconds
retries: 0
max_retries: 2

dependencies: []             # Block until these complete
blocked_by: []               # Populated by router

status: assigned             # pending | assigned | running | complete | failed
result: null                 # Path to result file
error: null                  # Error message if failed

metadata:
  source: heartbeat
  tags: [gameye, competitors]
```

## CLI Commands

### Task Management
```bash
# Create task
task create --type research \
  --title "Research Gameye competitors" \
  --data '{"query": "Gameye pricing"}' \
  --priority high \
  --ttl 3600

# Create with dependencies
task create --type analysis \
  --title "Analyze research results" \
  --depends-on task-abc123

# List tasks
task list                    # All non-completed
task list --status pending
task list --assigned-to watson
task list --type research --limit 10
task list --created-after 2026-02-13

# Show task
task show task-abc123        # Full details + result preview

# Manage tasks
task cancel task-abc123      # Cancel pending or active
task retry task-abc123       # Move failed back to pending
task reprioritize task-abc123 --priority urgent

# Results
task result task-abc123      # View result file
task export --status completed --since 2026-02-13 > ~/reports/tasks.ndjson
```

### Agent Management
```bash
# Register agent (required before routing)
task agent register watson \
  --capabilities "research analysis web_search" \
  --max-concurrent 3 \
  --emoji 🔬

# Update agent
task agent update watson --add-capability "competitive-analysis"
task agent update watson --max-concurrent 5

# Check agent health
task agent status watson     # Current tasks, health, stats
task agent ping watson       # Health check ping

# List agents
task agent list              # All agents
task agent list --capable-of research

# Unregister
task agent unregister watson --reassign-tasks
```

### Router Control
```bash
# Status
task router status           # Queue depth, agent health

# Control flow
task router pause            # Stop new assignments
task router resume           # Resume routing
task router rebalance        # Redistribute stuck tasks

# Maintenance  
task router cleanup          # Archive old completed tasks
task router drain            # Finish active, no new pending
```

## Programmatic API

```typescript
import * as Task from "~/.openclaw/task-router/sdk";

// === Creating Tasks ===

// Simple create
const task = await Task.create({
  type: "research",
  title: "Competitor analysis",
  payload: { query: "Gameye vs competitors" }
});

// With options
const task = await Task.create({
  type: "image_gen",
  title: "Generate hero image",
  payload: { prompt: "Futuristic game server...", size: "1024x1024" },
  priority: "high",
  ttl: 1800,
  max_retries: 1,
  dependencies: [previousTaskId],  // Waits for these first
  created_by: "main"
});

// === Querying ===

// Get status
const status = await Task.status(task.id);
// { id, status, assigned_to, created_at, expires_at }

// Wait for completion (blocking)
const result = await Task.wait(task.id, { timeout: 300, pollInterval: 5 });

// List with filters
const pending = await Task.query({
  status: "pending",
  type: "research",
  priority: "high",
  limit: 10
});

const myTasks = await Task.query({
  created_by: "main",
  status: ["assigned", "running"]
});

// === Agent Integration ===

// Agent picks up work (if auto-assign disabled)
await Task.claim({
  agentId: "watson",
  capableOf: "research",
  limit: 1
});

// Complete task
await Task.complete(task.id, {
  result_path: "~/agents/watson/memory/results/competitors.md",
  summary: "Found 5 competitors: GameLift, Multiplay, Hathora, Edgegap, Agones",
  metadata: { competitors_count: 5 }
});

// Fail task
await Task.fail(task.id, {
  reason: "API quota exceeded",
  retryable: true  // Will auto-retry
});

// === Multi-Step Workflows ===

// Chain tasks
const analysisTask = await Task.chain(researchTask.id, {
  type: "analysis",
  title: "Analyze research findings",
  payload: { input_task: researchTask.id }
});

// Parallel tasks
const tasks = await Task.parallel([
  { type: "research", title: "Research A", payload: {} },
  { type: "research", title: "Research B", payload: {} },
  { type: "research", title: "Research C", payload: {} }
]);
await Task.waitAll(tasks.map(t => t.id));

// === Agent Session Integration ===

// Spawn via task router (recommended for async work)
const spawnResult = await Task.spawn({
  taskId: task.id,
  agentId: "watson",      // Optional: auto-route if omitted
  useSession: true      // Use sessions_spawn vs sessions_send
});

// Router will call:
// sessions_spawn({ agentId, task, label: task.id })
```

## HEARTBEAT Integration

Create `~/.openclaw/workspace/HEARTBEAT.md`:

```markdown
# Task Router Heartbeat

## Router Cycle (runs every 30s)
```typescript
import * as Task from "~/.openclaw/task-router/sdk";

// 1. Auto-route pending tasks
const routed = await Task.router.cycle();
if (routed.length > 0) {
  Task.log(`Routed ${routed.length} tasks:`, routed.map(t => `${t.id} → ${t.assigned_to}`));
}

// 2. Check for timeouts
const timeouts = await Task.router.checkTimeouts();
for (const task of timeouts) {
  if (task.retries < task.max_retries) {
    Task.log(`Retrying ${task.id} after timeout`);
    await Task.retry(task.id);
  } else {
    Task.log(`Dead lettering ${task.id}`);
    await Task.router.moveToDeadLetter(task);
  }
}

// 3. Check agent health
const unhealthy = await Task.agents.checkHealth();
for (const agent of unhealthy) {
  // Reassign their tasks
  await Task.router.reassignFrom(agent.id);
}

// 4. Notify on completions
const recent = await Task.query({
  status: "completed",
  completed_after: Date.now() - 60000  // Last minute
});
for (const task of recent) {
  if (task.created_by === "main") {
    sessions_send({
      message: `✅ Task complete: ${task.title}\nResult: ${task.result}`
    });
  }
}
```

## Routing Strategies

| Strategy | Use Case | Description |
|----------|----------|-------------|
| **round-robin** | Even load | Cycle through agents |
| **least-loaded** | Prevent overload | Agent with fewest active tasks |
| **fastest** | Latency critical | Agent with best completion time |
| **priority** | Urgent tasks | Sort by priority first |
| **sticky** | Sequential work | Same agent for related tasks |

```yaml
# config.yaml
strategies:
  default: least-loaded
  
  # Per-task-type strategies
  by_type:
    research: least-loaded      # Don't overwhelm one researcher
    image_gen: round-robin      # Even GPU utilization
    urgent: priority             # Always pick best agent
    
  # Custom rules
  rules:
    - if: priority == urgent
      then: fastest
    - if: tags includes "sticky"
      then: sticky
```

## Task Lifecycle Details

```
PENDING ──assign──→ ASSIGNED ──ack──→ RUNNING ──complete──→ COMPLETE
   │           │          │              │                      │
   │           │          │              └──fail────┐            │
   │           │          │                        ↓            │
   │           │          │                     FAILED ──retry──┘
 timeout      │       timeout        (if retries < max)        │
   │           │          │                (else dead letter)    │
   │           │          │                                     │
   └───────────┴──────────┘─────────────────────────────────────┘
```

**State Definitions:**
- `pending`: Created, waiting for router
- `assigned`: Routed to agent, waiting for acceptance
- `running`: Agent acknowledged, working on it
- `complete`: Success, result available
- `failed`: Final failure (retries exhausted)
- `dead_letter`: Failed permanently, needs manual review

## Dead Letter Queue

When a task exhausts retries:

```
~/.openclaw/task-router/dead-letter/
├── task-failed-001.yaml       # Task with final error state
├── task-failed-002.yaml
└── index.yaml                 # Summary for admin review
```

```bash
# Review failed tasks
task dead-letter list
task dead-letter show task-failed-001

# Actions
task dead-letter retry task-failed-001      # Force retry
task dead-letter reassign task-failed-001 --to watson
task dead-letter archive task-failed-001   # Ack and archive
```

## Best Practices

**Task Design:**
- Keep payloads JSON-serializable (no circular refs)
- Include output format hints in payload
- Use dependencies for true sequencing
- Set reasonable TTLs (don't block forever)

**Agent Design:**
- Register capabilities narrowly at first
- Set conservative max_concurrent
- Heartbeat should check for assigned tasks
- Always acknowledge → complete/fail cleanly

**Coordination Patterns:**
- Use `Task.spawn()` for fire-and-forget
- Use `Task.wait()` when user needs result now
- Chain dependent tasks vs one mega-task
- Let router handle retries, not agents

## Multi-Agent Example

```typescript
// User asks: "Research competitors and create a presentation"

// Main agent (you) orchestrates:

// 1. Create research tasks
const research = await Task.create({
  type: "research",
  title: "Research Gameye competitors",
  payload: { query: "Gameye vs competitors" }
});

// 2. Create analysis task (depends on research)
const analysis = await Task.create({
  type: "analysis",
  title: "Analyze competitive landscape",
  dependencies: [research.id],
  payload: { input_task: research.id }
});

// 3. Create image task (independent, async)
const images = await Task.parallel([
  { type: "image_gen", title: "Competitor comparison chart", payload: {} },
  { type: "image_gen", title: "Market positioning diagram", payload: {} }
]);

// 4. Create presentation task (depends on all above)
const deck = await Task.create({
  type: "presentation",
  title: "Gameye competitive analysis deck",
  dependencies: [analysis.id, ...images.map(i => i.id)],
  payload: { 
    research: analysis.id,
    images: images.map(i => i.result)
  }
});

// 5. Wait for final result
const result = await Task.wait(deck.id, { timeout: 600 });

// Result: orchestrated 4 agents, 5 tasks, handled dependencies
```

## Troubleshooting

```bash
# Nothing routing?
task router status           # Check paused?
task agent list             # Any healthy agents?
task list --status pending  # Tasks waiting?

# Task stuck?
task show task-abc123        # Check assigned_to, started_at
task agent status watson     # Is agent healthy?

# Agent not picking up?
# - Check agent's HEARTBEAT checks for tasks
# - Verify sessions_send to agent works

# Too many failures?
task dead-letter list       # Review patterns
task router logs            # See routing decisions

# Clear everything (nuke)
task router drain           # Wait for active
task list --status pending | xargs task cancel
task dead-letter clear
```

## Requirements

- OpenClaw with sessions_send/sessions_spawn/sessions_list
- Agents with proper HEARTBEAT.md checking for tasks
- Optional: cron job for router if heartbeat not reliable

## Future Extensions

- **Metrics**: Prometheus-compatible stats
- **Web UI**: Dashboard at localhost:3333
- **Plugins**: Slack/Discord notifications
- **Priority Queues
