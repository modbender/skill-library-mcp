# Colony Orchestration Skill

Multi-agent task delegation and process orchestration with audit logging and agent learning capabilities.

## Quick Start

```bash
# Single task - auto-routed
node scripts/colony.mjs dispatch "find top 5 time-series databases"

# Multi-stage process
node scripts/colony.mjs process validate-idea --context "AI meal planning for parents"
node scripts/colony.mjs process-status  # check progress
node scripts/colony.mjs approve abc123  # continue past checkpoint

# Check audit stats
node scripts/colony.mjs audit

# View agent memory
node scripts/colony.mjs memory scout
```

## Agents

| Agent | Role | Specialization |
|-------|------|----------------|
| **scuttle** | researcher | Quick searches, lookups, fact-finding |
| **scout** | researcher | Deep market/competitor research, intelligence |
| **forecast** | analyst | Data analysis, trends, projections |
| **pincer** | coder | Writing, debugging, refactoring code |
| **shell** | ops | Git, deployments, system tasks |
| **forge** | product | PRDs, specs, roadmaps |
| **ledger** | finance | Pricing, costs, business cases |
| **muse** | creative | Brainstorming, naming, ideas |
| **scribe** | writer | Blog posts, docs, long-form content |
| **quill** | copywriter | Landing pages, sales copy, ads |
| **echo** | social | Tweets, social posts, promotion |
| **sentry** | qa | Testing, bug verification |

## Task Commands

### Dispatch (Auto-Route)
```bash
node scripts/colony.mjs dispatch "research best practices for API rate limiting"
```
Automatically detects the best agent based on task keywords.

### Assign to Specific Agent
```bash
node scripts/colony.mjs assign scout "find top 5 time-series databases"
node scripts/colony.mjs assign pincer "refactor the auth module to use JWT"
node scripts/colony.mjs assign shell "deploy the staging branch"
```

### Check Status
```bash
node scripts/colony.mjs status
```
Shows all agents and their current tasks.

### Get Results
```bash
node scripts/colony.mjs results              # Latest completed task
node scripts/colony.mjs results abc123       # Specific task by ID
```

### View History
```bash
node scripts/colony.mjs history              # Last 10 completed/failed
node scripts/colony.mjs history --limit 20   # Custom limit
```

## Process Commands

Processes are multi-stage workflows that chain agents together.

### List Available Processes
```bash
node scripts/colony.mjs processes
```

### Start a Process
```bash
node scripts/colony.mjs process <process-name> --context "description"
```

Examples:
```bash
node scripts/colony.mjs process validate-idea --context "AI-powered meal planning for busy parents"
node scripts/colony.mjs process content-pipeline --context "How to use vector databases for RAG"
node scripts/colony.mjs process product-launch --context "Life Lunch ritual kit for parents"
node scripts/colony.mjs process bug-triage --context "Login fails with OAuth on mobile"
```

### Check Process Status
```bash
node scripts/colony.mjs process-status           # Show latest run
node scripts/colony.mjs process-status abc123    # Specific run
```

Shows: current stage, completed stages, checkpoints, output files.

### View Process Runs
```bash
node scripts/colony.mjs runs                 # All runs (active, paused, completed)
node scripts/colony.mjs runs --limit 5       # Last 5
```

### Approve Checkpoint
When a process hits a checkpoint, it pauses for human approval:
```bash
node scripts/colony.mjs approve abc123
```

Also used to retry a failed stage.

### Cancel a Process
```bash
node scripts/colony.mjs cancel abc123
```

## Audit Commands

Track agent performance, task statistics, and system health.

### Dashboard
```bash
node scripts/colony.mjs audit
```
Shows global stats, per-agent summary, and recent events.

### Agent Details
```bash
node scripts/colony.mjs audit agent scout
node scripts/colony.mjs audit agent pincer
```
Shows detailed stats for a specific agent including:
- Total tasks, success rate
- Average duration
- Token usage
- Recent failures

### Event Log
```bash
node scripts/colony.mjs audit log              # Last 20 events
node scripts/colony.mjs audit log --limit 50   # More events
```

### Slowest Tasks
```bash
node scripts/colony.mjs audit slow             # Top 10 slowest
node scripts/colony.mjs audit slow --limit 20
```

### Recent Failures
```bash
node scripts/colony.mjs audit failures         # Last 10 failures
node scripts/colony.mjs audit failures --limit 20
```

## Learning Commands

Agents learn from experience and share knowledge.

### Feedback
Record feedback for completed tasks:
```bash
node scripts/colony.mjs feedback abc123 "Great research, but needed more pricing data"
```

### Agent Memory
Each agent has a persistent memory file with lessons learned:

```bash
# View an agent's memory
node scripts/colony.mjs memory scout

# Add a lesson
node scripts/colony.mjs memory scout add "Always check publication dates on research sources"

# Add to specific sections
node scripts/colony.mjs memory scout add "Use bullet points for clarity" --pattern
node scripts/colony.mjs memory scout add "Missed competitor X in analysis" --mistake
node scripts/colony.mjs memory scout add "Prefers markdown tables over lists" --pref
```

### Shared Learnings
Cross-agent insights and lessons:

```bash
# View all shared learnings
node scripts/colony.mjs learn

# Add a learning
node scripts/colony.mjs learn add "validate-idea works better with 3 competitors max" --category process
node scripts/colony.mjs learn add "Always verify API rate limits early" --category technical --source run-abc123
```

### Global Context
Shared context all agents can access:

```bash
# View global context
node scripts/colony.mjs context

# Set preferences
node scripts/colony.mjs context set preferences.codeStyle "TypeScript, functional"
node scripts/colony.mjs context set preferences.timezone "America/Chicago"

# Add active facts (temporary context)
node scripts/colony.mjs context add-fact "We're targeting enterprise customers"
node scripts/colony.mjs context add-fact "Launch deadline is Q2 2024"

# Add decisions
node scripts/colony.mjs context add-decision "Use Postgres over MySQL" --project "life-lunch"

# Add projects
node scripts/colony.mjs context add-project "life-lunch"
```

### Retrospective
Review recent activity and generate insights:

```bash
node scripts/colony.mjs retro              # Last 7 days
node scripts/colony.mjs retro --days 14    # Last 14 days
```

Shows:
- Task completion summary
- Per-agent stats
- Failure patterns
- Suggested learnings

## Available Processes

### validate-idea
**Validate a business idea end-to-end**
- Stages: brainstorm → research → analyze → spec → estimate
- Checkpoints: after analyze
- Output: business-case.md

### product-launch
**End-to-end product launch**
- Stages: research → spec → build → copy
- Checkpoints: after spec, after copy
- Output: market-brief.md, prd.md, code/, landing-copy.md

### content-pipeline
**Research, write, publish, promote content**
- Stages: research → draft → review → publish → promote
- Checkpoints: review (human reviews draft)
- Output: research.md, draft.md, social-posts.md

### bug-triage
**Reproduce, fix, deploy bug fixes**
- Stages: reproduce → fix → test → deploy
- Checkpoints: none (fast path)
- Output: bug-report.md, fix-summary.md

### customer-research
**Deep dive on a customer segment**
- Stages: identify → pain-points → validate → synthesize
- Checkpoints: none
- Output: customer-profile.md, insights.md

### landing-page
**Create a full landing page**
- Stages: strategy → copy → review → build
- Checkpoints: after copy review
- Output: strategy.md, copy.md, landing.html, landing.css

## How Processes Work

1. **Start** - Process creates a run entry and spawns first stage agent
2. **Execute** - Each stage runs with inputs from previous stages
3. **Checkpoint** - If stage is a checkpoint, process pauses for approval
4. **Continue** - After approval, next stage runs
5. **Complete** - All stages done, outputs in `colony/context/<run-id>/`

### Context Passing

- `{context}` in task templates is replaced with your --context value
- Stage outputs are saved to `colony/context/<run-id>/<output-file>`
- Next stage reads inputs from previous stage's output files
- Agent memory and global context are injected into prompts
- Full task history in `tasks.json`

### Parallel Stages

Stages that share the same `parallel_group` run concurrently:

```yaml
stages:
  - id: spec
    agent: forge
    inputs: [analysis.md]
    parallel_group: "final"  # Stages with same group run together
    
  - id: estimate
    agent: ledger
    inputs: [analysis.md]
    parallel_group: "final"  # Same group = parallel execution
```

When the process reaches a parallel group:
1. All consecutive stages with the same `parallel_group` are collected
2. All stages spawn concurrently (using `Promise.all()`)
3. Process waits for ALL parallel stages to complete
4. If any stage fails, the entire group fails
5. Checkpoints work per-group (pause after all parallel stages complete)

Output shows parallel execution clearly:
```
═══ Parallel Group: final (2 stages) ═══
    → Stage 4: spec (forge)
    → Stage 5: estimate (ledger)

--- [PARALLEL] Stage 4/5: spec ---
--- [PARALLEL] Stage 5/5: estimate ---

═══ Parallel Group: final completed ═══
```

**When to use parallel groups:**
- Stages that read the same inputs (no dependencies on each other)
- Build + copy tasks (both depend on spec, not on each other)
- Multiple analyses of the same data
- Independent research threads

**Processes with parallel stages:**
- `validate-idea`: spec + estimate run in parallel
- `product-launch`: build + copy run in parallel

### Notifications

Colony can send notifications when processes hit checkpoints, complete, or fail. Notifications use `openclaw cron wake` to alert you.

**Configuration** (`colony/config.yaml`):
```yaml
notifications:
  enabled: true         # Master switch for all notifications
  on_checkpoint: true   # Notify when process pauses at checkpoint
  on_complete: true     # Notify when process finishes
  on_failure: true      # Notify when process/stage fails
```

**Manage via CLI:**
```bash
# View current config
node scripts/colony.mjs config

# Disable all notifications
node scripts/colony.mjs config set notifications.enabled false

# Enable only failure notifications
node scripts/colony.mjs config set notifications.on_checkpoint false
node scripts/colony.mjs config set notifications.on_complete false
node scripts/colony.mjs config set notifications.on_failure true
```

**Notification examples:**
- 🛑 `Colony checkpoint: Process "validate-idea" paused after stage "analyze". To continue: colony approve abc123`
- ✅ `Colony complete: Process "validate-idea" finished in 120s. Run ID: abc123`
- ❌ `Colony failed: Process "validate-idea" failed at stage "research". Error: Agent timed out. Run ID: abc123`

### Checkpoints

Checkpoints pause the process for human review. Two ways to define:

1. In process `checkpoints` array (after that stage completes)
2. As a standalone stage with `checkpoint: true` (human-only review step)

## File Structure

```
skills/colony/
├── SKILL.md              # This file
├── package.json          # Dependencies (js-yaml)
├── colony/
│   ├── agents.yaml       # Agent definitions
│   ├── processes.yaml    # Process definitions
│   ├── config.yaml       # Notification & behavior config
│   ├── tasks.json        # Task queue and history
│   ├── runs.json         # Process run tracking
│   ├── feedback.json     # Task feedback storage
│   ├── learnings.yaml    # Shared cross-agent learnings
│   ├── global-context.json  # Shared context for all agents
│   ├── audit/
│   │   ├── log.jsonl     # Append-only event log
│   │   ├── global.json   # Aggregate statistics
│   │   └── agents/       # Per-agent statistics
│   │       ├── scout.json
│   │       ├── pincer.json
│   │       └── ...
│   ├── memory/           # Per-agent persistent memory
│   │   ├── scout.md
│   │   ├── pincer.md
│   │   └── ...
│   └── context/          # Per-task and per-run outputs
│       └── <run-id>/
└── scripts/
    ├── colony.mjs         # Main CLI
    ├── colony-worker.mjs  # Background agent executor
    ├── agent-wrapper.mjs # Task lifecycle utilities
    ├── audit.mjs         # Audit system functions
    └── learning.mjs      # Learning system functions
```

## Audit Events

The audit log tracks these events:

| Event | Fields |
|-------|--------|
| `task_started` | taskId, agent, processRunId?, stage? |
| `task_completed` | taskId, agent, durationMs, tokens, success |
| `task_failed` | taskId, agent, durationMs, error |
| `checkpoint_waiting` | runId, stage |
| `checkpoint_approved` | runId, stage |
| `checkpoint_rejected` | runId, stage, reason |
| `process_started` | runId, processId, context |
| `process_completed` | runId, processId, durationMs |
| `feedback_received` | taskId, agent, feedback |

## Customization

### Add New Agents
Edit `colony/agents.yaml`:
```yaml
agents:
  myagent:
    role: specialist
    description: >
      What this agent does...
    model: anthropic/claude-sonnet-4
    triggers:
      - keyword1
      - keyword2
```

After adding, create their memory file:
```bash
touch colony/memory/myagent.md
```

### Add New Processes
Edit `colony/processes.yaml`:
```yaml
processes:
  my-process:
    description: "What this process does"
    triggers: [keyword1, keyword2]
    stages:
      - id: stage1
        agent: scout
        task: "Do something with: {context}"
        outputs: [output1.md]
      - id: stage2
        agent: pincer
        task: "Next step based on previous"
        inputs: [output1.md]
        outputs: [output2.md]
    checkpoints: [stage1]  # Optional: pause after these stages
```

## Integration

Works with OpenClaw's agent sessions.

**Dispatch/Assign (async):** Tasks are spawned in the background and the CLI returns immediately. Use `colony status` to monitor progress and `colony results <task-id>` to view output.

**Process stages (blocking):** Multi-stage processes run sequentially, waiting for each stage to complete before proceeding. This ensures proper data flow between stages and checkpoint handling.

Each agent receives:
- Their role description
- Lessons from their memory file
- Active facts from global context
- Project/preference context

## Examples

### Validate a Startup Idea
```bash
node scripts/colony.mjs process validate-idea \
  --context "Subscription box for home coffee brewing experiments"
```

Watch as it flows: brainstorm → research → analyze → (checkpoint) → spec → estimate

### Write and Publish a Blog Post
```bash
node scripts/colony.mjs process content-pipeline \
  --context "Why RAG is eating traditional search"
```

Stages: research → draft → (human review) → publish → promote

### Quick Research Task
```bash
node scripts/colony.mjs dispatch "compare Pinecone vs Weaviate vs Milvus"
```

Auto-routes to scout, returns comparison.

### Track Performance
```bash
# After several tasks, check overall health
node scripts/colony.mjs audit

# Deep dive into a struggling agent
node scripts/colony.mjs audit agent pincer
node scripts/colony.mjs audit failures

# Add learnings from issues
node scripts/colony.mjs memory pincer add "Handle file not found errors gracefully" --mistake
```
