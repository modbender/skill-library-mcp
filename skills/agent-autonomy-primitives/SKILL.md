---
name: agent-autonomy-primitives
description: Build long-running autonomous agent loops using ClawVault primitives (tasks, projects, memory types, templates, heartbeats). Use when setting up agent autonomy, creating task-driven execution loops, customizing primitive schemas, wiring heartbeat-based work queues, or teaching an agent to manage its own backlog. Also use when adapting primitives to an existing agent setup or designing multi-agent collaboration through shared vaults.
---

# Agent Autonomy Primitives

Turn any AI agent into a self-directing worker using five composable primitives: **typed memory**, **task files**, **project grouping**, **template schemas**, and **heartbeat loops**.

## Prerequisites

```bash
npm install -g clawvault
clawvault init
```

## The Five Primitives

### 1. Typed Memory

Every memory has a type. The type determines where it lives and how it's retrieved.

| Type | Directory | When to Use |
|------|-----------|-------------|
| `decision` | `decisions/` | Recording a choice with rationale |
| `lesson` | `lessons/` | Something learned from experience |
| `person` | `people/` | Contact info, relationship context |
| `commitment` | `commitments/` | Promise made, deliverable owed |
| `preference` | `preferences/` | How someone likes things done |
| `fact` | `inbox/` | Raw information to file later |
| `project` | `projects/` | Workstream with goals and status |

Store with type:
```bash
clawvault remember decision "Chose Resend over SendGrid" --content "Lower cost, better DX, webhook support"
clawvault remember lesson "LLMs rewrite keywords during compression" --content "Always post-process with regex"
```

**Rule:** If you know WHAT KIND of thing it is, use the right command. Dumping everything into daily notes defeats retrieval later.

### 2. Task Primitives

A task is a markdown file with YAML frontmatter in `tasks/`:

```yaml
---
status: open
priority: high
owner: your-agent-name
project: my-project
due: 2026-03-01
tags: [infrastructure, deploy]
estimate: 2h
---
# Deploy API to production

## Context
Server provisioned. Need Dockerfile fix.

## Next Steps
- Fix binding to 0.0.0.0
- Add health endpoint
- Push and verify
```

Create tasks:
```bash
clawvault task add "Deploy API to production" \
  --priority high \
  --owner my-agent \
  --project my-project \
  --due 2026-03-01 \
  --tags "infrastructure,deploy"
```

Update status:
```bash
clawvault task update deploy-api-to-production --status in-progress
clawvault task done deploy-api-to-production --reason "Deployed, health check passing"
```

**Statuses:** `open` → `in-progress` → `done` (or `blocked`)
**Priorities:** `critical` > `high` > `medium` > `low`

### 3. Project Grouping

Projects group related tasks with metadata:

```bash
clawvault project add "Outbound Engine" \
  --owner pedro \
  --client versatly \
  --tags "gtm,sales" \
  --deadline 2026-03-15
```

Tasks reference projects via the `project` field. Filter tasks by project:
```bash
clawvault task list --project outbound-engine
```

### 4. Template Schemas

Templates are YAML schema definitions that control what fields exist on every primitive. They live in `templates/` in your vault.

See [references/template-customization.md](references/template-customization.md) for full customization guide.

Key points:
- Vault templates override builtins — drop a `task.md` in `templates/` to change the schema
- Add fields (e.g., `sprint`, `effort`, `client`) by editing the template
- Remove fields you don't need
- Change defaults (e.g., default priority = `high`)
- Validation is advisory — warns but never blocks

### 5. Heartbeat Loop

The heartbeat is the autonomy mechanism. Wire it into your agent's periodic wake cycle.

**Every heartbeat (e.g., every 30 minutes):**

```
1. clawvault task list --owner <agent-name> --status open
2. Sort by: priority (critical first), then due date (soonest first)
3. Pick the highest-impact task executable RIGHT NOW
4. Execute it
5. On completion: clawvault task done <slug> --reason "what was done"
6. On blocker: clawvault task update <slug> --status blocked --blocked-by "reason"
7. If new work discovered: clawvault task add "new task" --priority <p> --project <proj>
8. If lesson learned: clawvault remember lesson "what happened"
9. Go back to sleep
```

**Implementation for OpenClaw agents:**

Add to your `HEARTBEAT.md`:
```markdown
## Task-Driven Autonomy

Every heartbeat:
1. `clawvault task list --owner <your-name> --status open` → your work queue
2. Sort by priority + due date
3. Pick highest-impact task you can execute NOW
4. Work it. Update status. Mark done. Report.
5. Check for tasks due within 24h — those get priority
```

For cron-based agents, schedule a recurring job:
```
Schedule: every 30 minutes
Action: Read task queue, pick highest priority, execute, report
```

## Composing Primitives into Autonomy

The power is in composition, not any single primitive:

```
Wake → Read memory → Check tasks → Execute → Learn → Update memory → Sleep
         ↑                                      |
         └──────────────────────────────────────┘
```

Each cycle compounds:
- **Memory** feeds context into task execution (decisions, lessons, preferences inform how work gets done)
- **Task execution** generates new memories (lessons learned, decisions made, commitments created)
- **Lessons** improve future execution (mistakes aren't repeated)
- **Wiki-links** (`[[entity-name]]`) build a knowledge graph across all files
- **Projects** provide scope boundaries so the agent doesn't drift

## Adapting to Your Setup

See [references/adaptation-guide.md](references/adaptation-guide.md) for detailed patterns on:
- Wiring primitives into existing agent frameworks (OpenClaw, LangChain, CrewAI, custom)
- Choosing which primitives to adopt (start minimal, add as needed)
- Multi-agent collaboration through shared vaults
- Migrating from other memory systems

## Quick Start: Zero to Autonomous in 5 Minutes

```bash
# 1. Install and init
npm install -g clawvault
clawvault init

# 2. Create your first project
clawvault project add "My Project" --owner my-agent

# 3. Create tasks
clawvault task add "Set up monitoring" --priority high --owner my-agent --project my-project
clawvault task add "Write API docs" --priority medium --owner my-agent --project my-project

# 4. Wire into heartbeat (add to HEARTBEAT.md or cron)
# "Every 30min: clawvault task list --owner my-agent --status open, pick top task, execute"

# 5. Start working
clawvault task update set-up-monitoring --status in-progress
# ... do the work ...
clawvault task done set-up-monitoring --reason "Prometheus + Grafana configured"
clawvault remember lesson "UptimeRobot free tier only checks every 5min" --content "Use Better Stack for <1min checks"
```

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Store everything in one big memory file | Use typed memory — decisions/, lessons/, people/ |
| Create tasks without owner/project | Always set `--owner` and `--project` |
| Ask "what should I work on?" | Read your task queue and decide |
| Forget lessons after learning them | `clawvault remember lesson` immediately |
| Skip marking tasks done | Always `task done --reason` — the ledger tracks transitions |
| Create tasks for vague ideas | Put ideas in `backlog/`, promote to `tasks/` when ready |
| Modify template schemas constantly | Stabilize schemas early — field renames break existing files |

## Obsidian Integration

Because everything is markdown + YAML frontmatter, Obsidian renders your agent's workspace as a human-readable dashboard:

- **Kanban board** — open `all-tasks.base` in Obsidian Bases, drag between status columns
- **Blocked view** — `blocked.base` shows what needs human input
- **By owner** — `by-owner.base` shows what each agent is working on
- **By project** — `by-project.base` scopes views per workstream

The same file is both the agent's data structure AND the human's UI. No sync layer needed.
