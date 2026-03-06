# Colony Documentation

**Multi-Agent Orchestration for OpenClaw**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Agents](#agents)
4. [Processes](#processes)
5. [Commands Reference](#commands-reference)
6. [File Structure](#file-structure)
7. [Configuration](#configuration)
8. [Learning System](#learning-system)
9. [Examples](#examples)

---

## Overview

### What is Colony?

Colony is a multi-agent orchestration system for OpenClaw. It enables complex tasks to be broken down and delegated to specialized AI agents, each with their own expertise, memory, and learning capabilities.

Think of it as a virtual team where:
- **Clutch** acts as the coordinator (you, the main agent)
- **Specialized agents** handle specific types of work
- **Processes** define multi-stage workflows that chain agents together

### Philosophy

Colony is built on three core principles:

1. **Specialization** - Each agent excels at one thing. A researcher researches. A coder codes. A copywriter writes copy. No jack-of-all-trades.

2. **Composability** - Complex workflows are built by chaining simple agent tasks. The output of one becomes the input to the next.

3. **Learning** - Agents remember lessons from past tasks. The system improves over time through feedback and retrospectives.

### When to Use Colony

| Use Colony When... | Don't Use Colony When... |
|-------------------|-------------------------|
| Task requires multiple skill sets | Simple, single-skill task |
| You need structured multi-stage workflows | Quick one-off questions |
| You want audit trails and accountability | Informal brainstorming |
| Task benefits from specialized expertise | Time-critical responses needed |
| You need parallel research/development | Task needs real-time interaction |

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLUTCH                              │
│                   (Main Coordinator)                        │
│                                                             │
│  • Receives user requests                                   │
│  • Dispatches tasks to agents                               │
│  • Manages process workflows                                │
│  • Reviews and approves checkpoints                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Colony ROUTER                            │
│                                                             │
│  • Analyzes task keywords (triggers)                        │
│  • Routes to best-fit agent                                 │
│  • Falls back to default (scuttle) if no match              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌─────────┐           ┌─────────┐           ┌─────────┐
   │  Agent  │           │  Agent  │           │  Agent  │
   │ Memory  │           │ Memory  │           │ Memory  │
   └─────────┘           └─────────┘           └─────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
               ┌─────────────────────────┐
               │      AUDIT SYSTEM       │
               │                         │
               │  • Event logging        │
               │  • Performance stats    │
               │  • Failure tracking     │
               └─────────────────────────┘
```

### How Routing Works

When you dispatch a task, the router:

1. **Scans the task description** for trigger keywords
2. **Scores each agent** based on how many triggers match
3. **Routes to the highest scorer** (or default agent if no matches)

Example: *"research best practices for API rate limiting"*
- Matches `scuttle` triggers: "research" ✓
- Matches `scout` triggers: none
- **Result**: Routes to `scuttle`

Example: *"deep dive competitor landscape for meal prep apps"*
- Matches `scout` triggers: "deep dive" ✓, "competitor" ✓, "landscape" ✓
- **Result**: Routes to `scout`

### Process Pipelines

Processes chain multiple agents in sequence:

```
┌──────────────────────────────────────────────────────────────┐
│                    VALIDATE-IDEA PROCESS                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────┐    ┌────────┐    ┌──────────┐    ┌──────────┐   │
│  │  MUSE  │───▶│ SCOUT  │───▶│ FORECAST │───▶│  FORGE   │   │
│  │brainstorm│  │research │    │ analyze  │    │   spec   │   │
│  └────────┘    └────────┘    └──────────┘    └──────────┘   │
│                                    │                         │
│                              ⏸️ CHECKPOINT                   │
│                              (human reviews)                 │
│                                    │                         │
│                                    ▼                         │
│                              ┌──────────┐                    │
│                              │  LEDGER  │                    │
│                              │ estimate │                    │
│                              └──────────┘                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

Each stage:
- Receives inputs from previous stages
- Produces outputs for next stages
- Can pause at checkpoints for human review

---

## Agents

Colony includes 13 specialized agents across 6 domains.

### Research & Analysis

| Agent | Role | Description | Trigger Keywords |
|-------|------|-------------|-----------------|
| **scuttle** | Researcher | Quick searches, lookups, fact-finding, summarizing | research, search, find, lookup, summarize, compare, what is, who is, how does, explain, investigate, gather, analyze data, report on |
| **scout** | Deep Researcher | Market research, competitor analysis, intelligence gathering | market research, competitor, landscape, industry, trends, intelligence, deep dive, investigate, analysis |
| **forecast** | Analyst | Data analysis, trend forecasting, opportunity sizing | forecast, predict, trend, size, opportunity, project, estimate, model, data, insight, pattern |

### Development

| Agent | Role | Description | Trigger Keywords |
|-------|------|-------------|-----------------|
| **pincer** | Coder | Writing clean code, debugging, refactoring, building features | code, write, debug, fix, refactor, implement, build, function, class, module, script, test, api, bug, error, create a |
| **shell** | Ops | Git workflows, deployments, file management, DevOps | git, deploy, commit, push, pull, merge, branch, file, folder, directory, move, copy, delete, backup, restore, ssh, server, docker, npm, install |

### Product & Strategy

| Agent | Role | Description | Trigger Keywords |
|-------|------|-------------|-----------------|
| **forge** | Product | PRDs, specs, requirements, roadmaps, feature definition | prd, spec, requirement, feature, roadmap, prioritize, product, scope, mvp, epic, story |
| **ledger** | Finance | Costs, margins, pricing, ROI, business cases, budgets | cost, price, pricing, margin, roi, budget, revenue, profit, financial, business case, unit economics |

### Creative & Content

| Agent | Role | Description | Trigger Keywords |
|-------|------|-------------|-----------------|
| **muse** | Creative | Brainstorming, naming, ideation, lateral thinking | brainstorm, ideas, name, naming, creative, angle, variation, possibilities, alternatives, what if |
| **scribe** | Writer | Blog posts, articles, documentation, guides, tutorials | blog, article, post, documentation, guide, tutorial, explain, content, write about |
| **quill** | Copywriter | Landing pages, ads, emails, headlines, persuasive copy | landing page, copy, headline, ad, email, cta, sales, convert, persuade, marketing |
| **echo** | Social | Tweets, threads, LinkedIn posts, social content | tweet, thread, linkedin, social, post, viral, engagement, share, promote |

### Quality & Governance

| Agent | Role | Description | Trigger Keywords |
|-------|------|-------------|-----------------|
| **sentry** | QA | Bug reproduction, test cases, fix verification | test, qa, quality, verify, reproduce, bug report, edge case, regression, validate |
| **doctor** | Auditor | System health checks, performance reviews, meta-analysis | audit, health check, diagnose, review performance, check system, evaluate, assess, blind spots, improvement, governance, self-audit, meta-review |

### Agent Examples

**scuttle** - Quick Research
```bash
colony dispatch "compare PostgreSQL vs MySQL for time-series data"
```

**scout** - Deep Research
```bash
colony dispatch "competitor landscape for AI-powered meal planning apps"
```

**pincer** - Code
```bash
colony assign pincer "refactor the auth module to use JWT tokens"
```

**forge** - Product
```bash
colony dispatch "write MVP spec for subscription billing feature"
```

**quill** - Copy
```bash
colony dispatch "write landing page copy for a productivity app"
```

**doctor** - Audit
```bash
colony dispatch "audit the colony - which agents are underperforming?"
```

---

## Processes

Colony includes 9 pre-built processes for common workflows.

### Product & Strategy Processes

#### validate-idea
**Validate a business idea end-to-end**

| Stage | Agent | Task | Output |
|-------|-------|------|--------|
| brainstorm | muse | Brainstorm angles and variations | ideas.md |
| research | scout | Market research - competitors? | market-research.md |
| analyze | forecast | Size opportunity, analyze trends | analysis.md |
| ⏸️ *checkpoint* | - | Human reviews analysis | - |
| spec | forge | Define MVP scope | mvp-spec.md |
| estimate | ledger | Cost vs potential return | business-case.md |

```bash
colony process validate-idea --context "AI-powered meal planning for busy parents"
```

#### product-launch
**End-to-end product launch**

| Stage | Agent | Task | Output |
|-------|-------|------|--------|
| research | scout | Analyze market, competitors, positioning | market-brief.md |
| spec | forge | Write PRD based on research | prd.md |
| ⏸️ *checkpoint* | - | Human reviews PRD | - |
| build | pincer | Implement MVP per PRD | code/ |
| copy | quill | Write landing page copy | landing-copy.md |
| ⏸️ *checkpoint* | - | Human reviews copy | - |

```bash
colony process product-launch --context "Life Lunch ritual kit for parents"
```

#### landing-page
**Create a full landing page**

| Stage | Agent | Task | Output |
|-------|-------|------|--------|
| strategy | scout | Research competitor pages, best practices | strategy.md |
| copy | quill | Write headline, sections, CTA | copy.md |
| ⏸️ *checkpoint* | - | Human reviews copy | - |
| build | pincer | Implement in HTML/CSS | landing.html, landing.css |

```bash
colony process landing-page --context "SaaS dashboard for small business analytics"
```

### Content Processes

#### content-pipeline
**Research, write, publish, promote**

| Stage | Agent | Task | Output |
|-------|-------|------|--------|
| research | scout | Research the topic | research.md |
| draft | scribe | Write full article | draft.md |
| ⏸️ *checkpoint* | - | Human reviews draft | - |
| publish | shell | Deploy article | - |
| promote | echo | Create social posts | social-posts.md |

```bash
colony process content-pipeline --context "Why RAG is eating traditional search"
```

### Engineering Processes

#### bug-triage
**Reproduce, fix, deploy bug fixes** (no checkpoints - fast path)

| Stage | Agent | Task | Output |
|-------|-------|------|--------|
| reproduce | sentry | Reproduce and document bug | bug-report.md |
| fix | pincer | Implement fix | fix-summary.md |
| test | sentry | Verify fix works | - |
| deploy | shell | Deploy the fix | - |

```bash
colony process bug-triage --context "Login fails with OAuth on mobile Safari"
```

### Research Processes

#### customer-research
**Deep dive on a customer segment** (no checkpoints)

| Stage | Agent | Task | Output |
|-------|-------|------|--------|
| identify | scout | Profile the target customer | customer-profile.md |
| pain-points | muse | Brainstorm pain points, jobs-to-be-done | pain-points.md |
| validate | scout | Find evidence - forums, reviews | validation.md |
| synthesize | forecast | Synthesize into insights | insights.md |

```bash
colony process customer-research --context "small business owners who hate accounting"
```

### Governance Processes

#### system-health
**Full system health audit by Doctor**

| Stage | Agent | Task | Output |
|-------|-------|------|--------|
| coordinator-review | doctor | Audit Clutch (coordinator) | coordinator-audit.md |
| colony-review | doctor | Audit all colony agents | colony-audit.md |
| audit-review | doctor | Audit the audit system itself | meta-audit.md |
| recommendations | doctor | Synthesize findings, grade A-F | health-report.md |

```bash
colony process system-health --context "quarterly review"
```

#### colony-review
**Quick colony performance review**

| Stage | Agent | Task | Output |
|-------|-------|------|--------|
| review | doctor | Quick performance review | colony-review.md |

```bash
colony process colony-review --context "check after busy week"
```

#### process-retrospective
**Review a completed process and extract learnings**

| Stage | Agent | Task | Output |
|-------|-------|------|--------|
| gather | scuttle | Gather all context and results | process-data.md |
| analyze | doctor | Analyze what went well/poorly | retro-analysis.md |
| learn | doctor | Extract learnings for agents | learnings-to-add.md |
| ⏸️ *checkpoint* | - | Human reviews learnings | - |

```bash
colony process process-retrospective --context "run-abc123 (validate-idea for meal planning)"
```

---

## Commands Reference

### Task Commands

| Command | Description | Example |
|---------|-------------|---------|
| `dispatch "<task>"` | Auto-route to best agent | `colony dispatch "research API rate limiting"` |
| `assign <agent> "<task>"` | Assign to specific agent | `colony assign pincer "fix the auth bug"` |
| `status` | Show all agents and current tasks | `colony status` |
| `queue` | Show pending (queued) tasks | `colony queue` |
| `results [task-id]` | Show task results (latest or specific) | `colony results abc123` |
| `history [--limit N]` | Show completed/failed tasks | `colony history --limit 20` |

### Process Commands

| Command | Description | Example |
|---------|-------------|---------|
| `processes` | List all available processes | `colony processes` |
| `process <name> --context "..."` | Start a process | `colony process validate-idea --context "meal kit app"` |
| `process-status [run-id]` | Show process run status | `colony process-status abc123` |
| `runs [--limit N]` | Show process run history | `colony runs --limit 5` |
| `approve <run-id>` | Approve checkpoint / retry failed | `colony approve abc123` |
| `cancel <run-id>` | Cancel a running process | `colony cancel abc123` |

### Audit Commands

| Command | Description | Example |
|---------|-------------|---------|
| `audit` | Summary dashboard | `colony audit` |
| `audit agent <name>` | Detailed stats for one agent | `colony audit agent scout` |
| `audit log [--limit N]` | Recent events (default 20) | `colony audit log --limit 50` |
| `audit slow [--limit N]` | Slowest tasks | `colony audit slow` |
| `audit failures [--limit N]` | Recent failures | `colony audit failures --limit 20` |

### Learning Commands

| Command | Description | Example |
|---------|-------------|---------|
| `feedback <task-id> "text"` | Record feedback for a task | `colony feedback abc123 "needed more pricing data"` |
| `memory <agent>` | View agent's memory | `colony memory scout` |
| `memory <agent> add "lesson"` | Add to agent's memory | `colony memory scout add "Always check dates"` |
| `memory <agent> add "..." --pattern` | Add to "Patterns That Work" | `colony memory pincer add "Use TypeScript" --pattern` |
| `memory <agent> add "..." --mistake` | Add to "Mistakes Made" | `colony memory scout add "Missed competitor X" --mistake` |
| `memory <agent> add "..." --pref` | Add to "Preferences" | `colony memory scribe add "Use headers" --pref` |
| `learn` | Show shared learnings | `colony learn` |
| `learn add "..." --category <cat>` | Add shared learning | `colony learn add "Always verify limits" --category technical` |
| `context` | Show global context | `colony context` |
| `context set <key> <value>` | Update global context | `colony context set preferences.codeStyle "TypeScript"` |
| `context add-fact "fact"` | Add to activeFacts | `colony context add-fact "Targeting enterprise"` |
| `context add-decision "dec" --project <name>` | Add decision | `colony context add-decision "Use Postgres" --project life-lunch` |
| `context add-project "name"` | Add project | `colony context add-project "life-lunch"` |
| `retro [--days N]` | Review recent tasks | `colony retro --days 14` |

### Config Commands

| Command | Description | Example |
|---------|-------------|---------|
| `config` | Show current configuration | `colony config` |
| `config set <key> <value>` | Update configuration value | `colony config set notifications.enabled false` |

**Configurable Settings:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `notifications.enabled` | boolean | `true` | Enable/disable all notifications |
| `notifications.on_checkpoint` | boolean | `true` | Notify when process hits checkpoint |
| `notifications.on_complete` | boolean | `true` | Notify when process completes |
| `notifications.on_failure` | boolean | `true` | Notify when task/process fails |
| `notifications.target` | string | *(required)* | Telegram phone number for notifications |

**Examples:**
```bash
# Disable all notifications
colony config set notifications.enabled false

# Change notification target
colony config set notifications.target "1234567890"

# Only notify on failures
colony config set notifications.on_checkpoint false
colony config set notifications.on_complete false
```

---

## File Structure

```
skills/colony/
├── SKILL.md                    # Skill documentation
├── COLONY-DOCS.md              # This comprehensive guide
├── package.json                # Dependencies (js-yaml)
│
├── colony/
│   ├── agents.yaml             # Agent definitions
│   ├── processes.yaml          # Process definitions
│   ├── config.yaml             # Notification and system config
│   ├── tasks.json              # Task queue and history
│   ├── runs.json               # Process run tracking
│   ├── feedback.json           # Task feedback storage
│   ├── learnings.yaml          # Shared cross-agent learnings
│   ├── global-context.json     # Shared context for all agents
│   │
│   ├── audit/
│   │   ├── log.jsonl           # Append-only event log
│   │   ├── global.json         # Aggregate statistics
│   │   └── agents/             # Per-agent statistics
│   │       ├── scout.json
│   │       ├── pincer.json
│   │       └── ...
│   │
│   ├── memory/                 # Per-agent persistent memory
│   │   ├── scout.md
│   │   ├── pincer.md
│   │   └── ...
│   │
│   └── context/                # Per-task and per-run outputs
│       └── <run-id>/
│           ├── context.md
│           ├── market-brief.md
│           └── ...
│
└── scripts/
    ├── colony.mjs               # Main CLI
    ├── colony-worker.mjs        # Background agent executor
    ├── agent-wrapper.mjs       # Task lifecycle utilities
    ├── audit.mjs               # Audit system functions
    └── learning.mjs            # Learning system functions
```

### Key Files Explained

#### agents.yaml
Defines all agents with their:
- **role** - Category (researcher, coder, ops, etc.)
- **description** - Full description injected into prompts
- **model** - Which LLM to use
- **thinking** - Whether to enable extended thinking
- **triggers** - Keywords for auto-routing

#### processes.yaml
Defines multi-stage workflows with:
- **description** - What the process does
- **triggers** - Keywords for auto-detection
- **stages** - Ordered list of agent tasks
- **checkpoints** - Where to pause for human review

#### config.yaml
System configuration including:
- **notifications.enabled** - Master switch for notifications
- **notifications.on_checkpoint** - Notify on checkpoint pause
- **notifications.on_complete** - Notify on process completion
- **notifications.on_failure** - Notify on failures
- **notifications.target** - Telegram phone number for notifications

#### tasks.json
Tracks all tasks:
- **queue** - Pending tasks (rarely used, async dispatch)
- **active** - Currently running tasks (keyed by agent)
- **completed** - Finished tasks (last 100)
- **failed** - Failed tasks

#### runs.json
Tracks process runs:
- **active** - Currently running processes
- **paused** - Processes waiting at checkpoints
- **completed** - Finished processes (last 50)

#### audit/log.jsonl
Append-only event log with entries for:
- `task_started` / `task_completed` / `task_failed`
- `checkpoint_waiting` / `checkpoint_approved`
- `process_started` / `process_completed`
- `feedback_received`

#### memory/<agent>.md
Each agent's personal memory file with sections:
- **Lessons Learned** - General insights
- **Patterns That Work** - Successful approaches
- **Mistakes Made** - Things to avoid
- **Preferences** - User preferences for this agent

---

## Configuration

Colony uses `config.yaml` to manage system-wide settings, primarily for notifications.

### Initial Setup

Before using notifications, configure your target:

```bash
# Set your Telegram phone number for notifications
colony config set notifications.target "YOUR_PHONE_NUMBER"
```

> ⚠️ **Important:** The notification target must be configured before notifications will work. Do not commit your phone number to version control.

### Notification System

Colony can send Telegram notifications at key points during process execution:

| Event | Setting | When it fires |
|-------|---------|---------------|
| Checkpoint | `notifications.on_checkpoint` | Process pauses and needs approval |
| Complete | `notifications.on_complete` | Process finishes successfully |
| Failure | `notifications.on_failure` | Task or process fails |

**Example notifications:**
- `🛑 Colony checkpoint: Process "validate-idea" paused after stage "analyze". To continue: colony approve abc123`
- `✅ Colony complete: Process "validate-idea" finished in 245s. Run ID: abc123`
- `❌ Colony failed: Process "bug-triage" failed at stage "fix". Error: Timeout. Run ID: abc123`

### config.yaml Structure

```yaml
notifications:
  enabled: true           # Master switch for all notifications
  on_checkpoint: true     # Notify when process hits checkpoint
  on_complete: true       # Notify when process completes
  on_failure: true        # Notify when task/process fails
  target: "YOUR_NUMBER"   # Telegram phone number (configure this!)
```

### Configuration Commands

```bash
# View current configuration
colony config

# Disable all notifications
colony config set notifications.enabled false

# Only get notified on failures
colony config set notifications.on_checkpoint false
colony config set notifications.on_complete false
colony config set notifications.on_failure true

# Update notification target
colony config set notifications.target "1234567890"
```

---

## Learning System

Colony has a multi-layered learning system that helps agents improve over time.

### Layer 1: Agent Memory

Each agent has a personal memory file (`memory/<agent>.md`) that persists across tasks.

**How it works:**
1. Memory is loaded and injected into every prompt
2. After tasks, you can add lessons with `colony memory <agent> add "lesson"`
3. Agents see their own lessons in future tasks

**Example memory file:**
```markdown
# Scout's Memory

## Lessons Learned
- Always verify source publication dates
- Check for pricing on competitor websites
- LinkedIn is often more current than company websites

## Patterns That Work
- Start with the 3 biggest competitors
- Use tables for comparison data

## Mistakes Made
- Missed European competitors in previous analysis

## Preferences
- User prefers markdown tables over bullet lists
```

### Layer 2: Global Context

Shared context that all agents can access (`global-context.json`).

**What it contains:**
- **currentProjects** - Active project names
- **activeFacts** - Temporary facts (e.g., "targeting enterprise")
- **preferences** - User preferences (timezone, code style, etc.)
- **recentDecisions** - Decisions made (with project tags)

**How to use:**
```bash
colony context add-fact "We're in stealth mode"
colony context set preferences.codeStyle "TypeScript, functional"
colony context add-decision "Use Stripe for payments" --project life-lunch
```

### Layer 3: Shared Learnings

Cross-agent insights stored in `learnings.yaml`.

**Categories:**
- `general` - Universal lessons
- `process` - Process-level insights
- `technical` - Technical lessons
- `communication` - Communication insights

**How to add:**
```bash
colony learn add "validate-idea works better with 3 competitors max" --category process
```

### Layer 4: Feedback

Task-specific feedback stored in `feedback.json`.

**How it works:**
1. After any task, add feedback: `colony feedback <task-id> "text"`
2. Feedback is logged for analysis
3. Retrospectives surface patterns from feedback

### Layer 5: Retrospectives

Periodic review of task history to surface insights.

```bash
colony retro --days 7
```

**What it shows:**
- Task completion summary
- Per-agent success rates
- Failure patterns
- Suggested learnings

### Learning Flow

```
┌─────────────────────────────────────────────────────────────┐
│                       TASK EXECUTION                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      POST-TASK REVIEW                        │
│                                                              │
│  "Was this good?"                                            │
│                                                              │
│  YES ──▶ colony feedback abc123 "Great job, concise"          │
│                                                              │
│  NO ───▶ colony feedback abc123 "Missed competitor X"         │
│          colony memory scout add "Check EU competitors"       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   PERIODIC RETROSPECTIVE                     │
│                                                              │
│  colony retro --days 7                                        │
│                                                              │
│  • Identify failure patterns                                 │
│  • Surface common feedback themes                            │
│  • Update agent memories                                     │
│  • Add shared learnings                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Examples

### Example 1: Dispatching a Simple Task

**Scenario:** You need quick research on vector databases.

```bash
# Dispatch with auto-routing
node scripts/colony.mjs dispatch "compare Pinecone vs Weaviate vs Milvus for RAG"

# Output:
# → Agent: scout (researcher)
# → Model: anthropic/claude-sonnet-4
# → Task ID: x7k2m9p4
# → Spawning agent (async mode)...
# → Task x7k2m9p4 dispatched (running in background)
# → Check status: colony status
# → View results: colony results x7k2m9p4
```

```bash
# Check status
node scripts/colony.mjs status

# View results when done
node scripts/colony.mjs results x7k2m9p4
```

### Example 2: Running a Full Process

**Scenario:** Validate a startup idea with full analysis.

```bash
# Start the process
node scripts/colony.mjs process validate-idea \
  --context "Subscription box for home coffee brewing experiments"

# Output:
# 🚀 Starting process: validate-idea
#    Run ID: abc12345
#    Context: Subscription box for home coffee brewing experiments
#    Stages: 5
#
# --- Stage 1/5: brainstorm ---
# → Agent: muse (creative)
# → Task ID: m3n8k2...
# ...
# → Task completed (45231ms)
#
# --- Stage 2/5: research ---
# → Agent: scout (researcher)
# ...
#
# --- Stage 3/5: analyze ---
# ...
# → Task completed
#
# ⏸️  Process paused at checkpoint after: analyze
#    To continue: colony approve abc12345
```

```bash
# Review the analysis output
cat colony/context/abc12345/analysis.md

# If satisfied, approve to continue
node scripts/colony.mjs approve abc12345

# Process continues through spec and estimate stages
```

### Example 3: Checking Audit Stats

**Scenario:** Review colony performance after a busy week.

```bash
# Dashboard view
node scripts/colony.mjs audit

# Output:
# === Colony Audit Dashboard ===
#
# Global Stats:
#   Total Tasks: 47
#   Success Rate: 91.5%
#   Avg Duration: 32.4s
#   Total Tokens: 1.2M
#
# Per-Agent Summary:
#   scout     | 12 tasks | 100% success | avg 45.2s
#   pincer    |  8 tasks |  87% success | avg 28.1s
#   scribe    |  6 tasks | 100% success | avg 52.3s
#   ...
```

```bash
# Deep dive into struggling agent
node scripts/colony.mjs audit agent pincer

# Output:
# === Agent: pincer ===
#
# Stats:
#   Total Tasks: 8
#   Completed: 7
#   Failed: 1
#   Success Rate: 87.5%
#   Avg Duration: 28.1s
#
# Recent Failures:
#   [k2m9x4] "refactor auth module" - Timeout after 300s
```

```bash
# View all recent failures
node scripts/colony.mjs audit failures

# View slowest tasks
node scripts/colony.mjs audit slow
```

### Example 4: Adding Feedback and Learnings

**Scenario:** A task completed but could have been better.

```bash
# View the task result
node scripts/colony.mjs results abc123

# Add feedback
node scripts/colony.mjs feedback abc123 \
  "Good research but missed European competitors entirely"

# Add a lesson to the agent's memory
node scripts/colony.mjs memory scout add \
  "Always include European competitors in market research" \
  --mistake

# Add a shared learning for all agents
node scripts/colony.mjs learn add \
  "Market research should cover US, EU, and APAC regions" \
  --category general
```

### Example 5: Running a Governance Audit

**Scenario:** Quarterly health check of the entire system.

```bash
# Run full system health audit
node scripts/colony.mjs process system-health --context "Q1 2024 review"

# This runs 4 stages:
# 1. coordinator-review - Audits Clutch
# 2. colony-review - Audits all agents
# 3. audit-review - Audits the audit system
# 4. recommendations - Synthesizes everything

# View the final health report
cat colony/context/<run-id>/health-report.md
```

### Example 6: Creating a Landing Page

**Scenario:** Need a complete landing page for a new product.

```bash
# Start the landing page process
node scripts/colony.mjs process landing-page \
  --context "AI-powered expense tracking for freelancers"

# Stage 1: scout researches competitor pages
# Stage 2: quill writes the copy
# Stage 3: CHECKPOINT - you review the copy

# Review and approve
cat colony/context/<run-id>/copy.md
node scripts/colony.mjs approve <run-id>

# Stage 4: pincer builds the HTML/CSS

# Final outputs:
# - colony/context/<run-id>/landing.html
# - colony/context/<run-id>/landing.css
```

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│                    COLONY QUICK REFERENCE                   │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  DISPATCH TASKS                                             │
│    colony dispatch "task"     Auto-route                    │
│    colony assign scout "task" Specific agent                │
│    colony status              Check progress                │
│    colony results [id]        View output                   │
│                                                             │
│  RUN PROCESSES                                              │
│    colony processes           List available                │
│    colony process <name> --context "..."                    │
│    colony process-status      Check progress                │
│    colony approve <run-id>    Continue past checkpoint      │
│                                                             │
│  CHECK HEALTH                                               │
│    colony audit               Dashboard                     │
│    colony audit agent <name>  Agent details                 │
│    colony audit failures      Recent failures               │
│    colony retro               Review last 7 days            │
│                                                             │
│  CONFIGURATION                                              │
│    colony config              Show current config           │
│    colony config set <k> <v>  Update setting                │
│                                                             │
│  ADD LEARNINGS                                              │
│    colony feedback <id> "text"                              │
│    colony memory <agent> add "lesson"                       │
│    colony learn add "lesson" --category <cat>               │
│                                                             │
│  AGENTS                                                     │
│    Research:  scuttle, scout, forecast                      │
│    Code:      pincer                                        │
│    Ops:       shell                                         │
│    Product:   forge, ledger                                 │
│    Content:   muse, scribe, quill, echo                     │
│    Quality:   sentry, doctor                                │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---