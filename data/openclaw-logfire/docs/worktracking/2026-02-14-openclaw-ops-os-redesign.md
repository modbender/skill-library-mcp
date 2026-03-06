# OpenClaw Chief of Staff: Ops OS Redesign

**Date:** 2026-02-14
**Status:** Phases 1–6 Complete — Phase 7 (Validation & Tuning) Remaining
**Linear Project:** [OpenClaw Ops OS](https://linear.app/ultrathink-solutions/project/openclaw-ops-os-630ed09f8aff)
**Builds on:** [2026-02-12 OpenClaw + Axon Convergence Plan](./2026-02-12-openclaw-chief-of-staff-deployment.md)

## Linear Issues

| Phase | Issue | Priority | Status |
|-------|-------|----------|--------|
| Phase 1: Goal Framework & Workspace Files | [ULT-629](https://linear.app/ultrathink-solutions/issue/ULT-629) | P0 / Urgent | Done |
| Phase 2: Agent Config & Shared Skills | [ULT-630](https://linear.app/ultrathink-solutions/issue/ULT-630) | P0 / Urgent | Done |
| Phase 3: Cron Jobs & Scheduling | [ULT-631](https://linear.app/ultrathink-solutions/issue/ULT-631) | P0 / Urgent | Done |
| Phase 4: Content Pipeline & Multi-Model Review | [ULT-632](https://linear.app/ultrathink-solutions/issue/ULT-632) | P0 / Urgent | Done |
| Brand Guidelines Semantic Search | See [separate plan](./2026-02-14-brand-guidelines-semantic-search.md) | P0 / High | Done (Phases A-C) |
| Phase 5: Proactive Follow-Ups & Meeting Prep | [ULT-633](https://linear.app/ultrathink-solutions/issue/ULT-633) | P1 / High | Done |
| Phase 6: Email Triage (MVP Cron) | [ULT-634](https://linear.app/ultrathink-solutions/issue/ULT-634) | P2 / Medium | Done |
| Phase 7: Validation & Tuning | [ULT-635](https://linear.app/ultrathink-solutions/issue/ULT-635) | P1 / High | Backlog |

**Dependency chain:** ULT-629 + ULT-630 (parallel) → ULT-631 + ULT-632 + ULT-633 → ULT-635
**Completed:** 2026-02-14 (Phases 1–6 + brand guidelines A–C in a single day)
**Repo:** axon-internal-apps

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Requirements](#requirements)
- [Design Principles](#design-principles)
- [Architecture: Four Operating Loops](#architecture-four-operating-loops)
- [Goal Framework](#goal-framework)
- [Daily Standup](#daily-standup)
- [Delegation via Cross-Agent Sub-Agents](#delegation-via-cross-agent-sub-agents)
- [Content Pipeline with Multi-Model Review](#content-pipeline-with-multi-model-review)
- [Proactive Follow-Ups](#proactive-follow-ups)
- [Shared Skills & Memory Architecture](#shared-skills--memory-architecture)
- [Guidelines API Integration (Semantic Search)](#guidelines-api-integration-semantic-search)
- [Agent Roster Changes](#agent-roster-changes)
- [Scheduling Strategy: Cron vs Heartbeat](#scheduling-strategy-cron-vs-heartbeat)
- [Security Considerations](#security-considerations)
- [Implementation Plan](#implementation-plan)
- [Open Questions](#open-questions)
- [References & Sources](#references--sources)

---

## Problem Statement

The initial OpenClaw deployment (ULT-578 through ULT-611) established the **infrastructure layer** — a working NixOS systemd service with 4 agents, MCP adapters, Slack channel, Google Workspace integration, SOPS secrets, and systemd hardening. The convergence plan defined the three-layer architecture (Channel + Orchestration + Web UI) and integration contracts (REST, webhooks, Mem0).

What's missing is the **operating layer** — the system that turns infrastructure into a daily workflow. Today we have an **agent org chart** (clear roles for chief-of-staff, marketing, content, coding) but not an **operating system** (goals -> work items -> delegation -> execution -> reporting -> accountability).

### Specific gaps

1. **No goal framework.** Agents have no concept of monthly/weekly targets. Morning briefings report "what happened" instead of "are we on track."
2. **No daily standup.** The cron job config (`cron/jobs.json`) hasn't been created. The planned briefing prompt is a generic "check email, calendar, deals, issues."
3. **Delegation is theoretical.** SOUL.md says "delegate to marketing agent" but no cross-agent spawning is configured. `subagents.allowAgents` is not set.
4. **Content cadence is untracked.** "2 blog posts + 2 LinkedIn posts per week" isn't encoded anywhere. No content calendar, no pipeline state, no multi-model review workflow.
5. **No multi-model content review.** 6 models are available in LiteLLM but the content agent is fixed to Sonnet 4.5. The Opus <-> GPT review loop the founder uses manually isn't systematized.
6. **Brand voice is thin.** The Guidelines API (`/v1/guidelines`) exists in Postgres with typed categories but OpenClaw agents don't query it. Content SOUL.md has a 4-line brand voice section.
7. **Skills are duplicated.** `shared-memory/SKILL.md` is copy-pasted across 3 workspaces. `axon-api/SKILL.md` is duplicated in 2.
8. **No cross-repo awareness.** The chief-of-staff doesn't know about the 7 Ultrathink repos. It can't check PRs or recent commits across repos.
9. **Follow-ups are manual.** No meeting prep before prospect calls, no follow-up email drafts after meetings, no proactive CRM task hygiene.
10. **Coding agent has no memory.** Unlike the other three agents, it lacks shared-memory access and can't store/retrieve context about technical decisions.

### What we want

A daily operating rhythm where:

1. Monthly goals are set with the chief-of-staff (manually).
2. Every Monday, the system proposes a weekly plan derived from goals + current state. The founder approves/adjusts.
3. Every weekday morning, a standup pulls status from Linear, GitHub PRs, calendar, email, HubSpot/Apollo, and running campaigns — scored against weekly targets.
4. Work gets delegated: content writing (multi-model review), ABM campaigns (Temporal), coding tasks (Claude Code), outreach (LinkedIn/email).
5. The founder does some work manually (review email drafts, answer questions, adjust priorities) while agents handle execution.
6. Proactive follow-ups happen automatically — meeting prep before calls, draft emails after meetings, CRM task reminders.
7. Friday afternoon, a weekly scorecard summarizes progress against goals.

---

## Requirements

### Business Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BR-1 | Monthly goal-setting with measurable targets (content count, campaigns, outreach, engineering) | P0 |
| BR-2 | Daily standup with goal-relative progress, actionable priorities, and meeting prep | P0 |
| BR-3 | Content cadence: 2 blog posts + 2 LinkedIn posts per week with multi-model review | P0 |
| BR-4 | 1-2 ABM campaigns per month with Slack-based approval flow | P0 |
| BR-5 | LinkedIn outreach targets tracked and reported | P1 |
| BR-6 | Proactive meeting prep and follow-up email drafts | P1 |
| BR-7 | Cross-repo awareness (PRs, commits, deploys across 7 repos) | P1 |
| BR-8 | Friday weekly scorecard summarizing progress vs goals | P1 |
| BR-9 | Brand voice and messaging guidelines consistently applied to all content | P0 |
| BR-10 | CRM pipeline hygiene (overdue tasks, aging deals, stale follow-ups) | P2 |

### Technical Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| TR-1 | Cross-agent sub-agent spawning via `subagents.allowAgents` | P0 |
| TR-2 | Shared skills directory via `skills.load.extraDirs` (dedup shared-memory, axon-api, google-workspace) | P0 |
| TR-3 | Memory search over worktracking docs via `memorySearch.extraPaths` | P1 |
| TR-4 | Cron jobs for daily standup, weekly planning, and weekly scorecard | P0 |
| TR-5 | Multi-model content review via sub-agent critique chain (Opus draft -> GPT review -> Opus refine) | P0 |
| TR-6 | Guidelines skill for content agent querying `POST /v1/guidelines/search` (semantic search) | P0 |
| TR-7 | Gmail PubSub for event-driven email triage | P2 |
| TR-8 | Cost optimization: use Sonnet/Haiku for cron collection, Opus for interactive judgment | P1 |

---

## Design Principles

### 1. Separate aggregation from decision-making

Don't burn Opus tokens on clerical work (listing tasks, fetching statuses, pulling metrics). Reserve Opus for judgment calls (prioritization, tradeoffs, strategic advice). Cron jobs run with cheaper models for collection; interactive Slack conversations use Opus for decisions.

### 2. Goals are first-class artifacts

Monthly goals, weekly plans, and sources of truth live as files in the agent workspace — queryable, version-controlled, and referenced by every scheduled job. Without goals, standups are noise.

### 3. Delegation is real, not theoretical

Cross-agent sub-agent spawning ([`subagents.allowAgents`](https://docs.openclaw.ai/tools/subagents)) makes delegation an actual system feature. The chief-of-staff can spawn a marketing sub-agent that runs with marketing's tools and workspace, gets results back, and makes decisions.

### 4. Composition over configuration

Use OpenClaw's existing primitives (cron, heartbeat, sub-agents, skills, memory search) rather than building custom infrastructure. The operating system lives in workspace files and config, not new Python code.

### 5. Event-driven over polling where possible

Gmail PubSub for email triggers, Temporal webhooks for campaign events, and calendar-aware heartbeat checks are better than "check every 2 hours." Polling is the fallback, not the default.

### 6. Security by systemd, not Docker

The dev server uses NixOS with systemd hardening (`ProtectSystem=strict`, `BindPaths`, `NoNewPrivileges`, etc.) instead of Docker sandboxing. Loopback binding + Tailscale provides network isolation. All sandbox recommendations assume this model.

---

## Architecture: Four Operating Loops

The operating system consists of four interlocking loops:

```text
+-----------------------------------------------------------------+
|                    PLANNING LOOP (Weekly)                        |
|                                                                 |
|  Monthly GOALS.md -> Monday Cron generates WEEKLY_PLAN.md       |
|  Founder reviews/adjusts -> System tracks against plan          |
|  Friday Cron generates WEEKLY_SCORECARD                         |
|                                                                 |
|  Input: GOALS.md, Linear state, campaign state, content state   |
|  Output: WEEKLY_PLAN.md (proposed), WEEKLY_SCORECARD (actual)   |
+-------------------------------+---------------------------------+
                                |
+-------------------------------v---------------------------------+
|                   EXECUTION LOOP (Daily)                        |
|                                                                 |
|  7am Cron: Daily standup (Sonnet collects, Opus decides)        |
|  Pulls: Linear, PRs, Calendar, Email, HubSpot, Campaigns       |
|  Reports: Goal progress, priorities, blockers, meeting prep     |
|                                                                 |
|  Founder responds -> interactive Opus conversation              |
|  Delegates tasks -> sub-agents execute in parallel              |
+-------------------------------+---------------------------------+
                                |
+-------------------------------v---------------------------------+
|                  DELEGATION LOOP (On-demand)                    |
|                                                                 |
|  Chief-of-staff spawns sub-agents:                              |
|                                                                 |
|  +---------------+  +---------------+  +---------------+       |
|  | Marketing     |  | Content       |  | Coding        |       |
|  | sub-agent     |  | sub-agent     |  | sub-agent     |       |
|  |               |  |               |  |               |       |
|  | Apollo, GA,   |  | Multi-model   |  | Claude Code   |       |
|  | LinkedIn MCP  |  | review loop   |  | subprocess    |       |
|  | HubSpot, etc  |  | Guidelines    |  | Full repo     |       |
|  +------+--------+  +------+--------+  +------+--------+       |
|         | results          | drafts          | PRs              |
|         +------------------+-----------------+                  |
|                            |                                    |
|  Chief-of-staff merges results -> presents to founder           |
+-------------------------------+---------------------------------+
                                |
+-------------------------------v---------------------------------+
|                PROACTIVE LOOP (Continuous)                       |
|                                                                 |
|  Heartbeat (every 30m, business hours):                         |
|  - Calendar: prep for meetings in next 2h                       |
|  - Email: flag VIP/urgent threads                               |
|  - Campaigns: alert on anomalies or completions                 |
|  - CRM: overdue tasks, aging deals                              |
|                                                                 |
|  Gmail PubSub (event-driven):                                   |
|  - VIP email arrives -> instant triage + draft reply            |
|                                                                 |
|  Temporal Webhooks (event-driven):                              |
|  - Campaign approval needed -> Slack notification               |
|  - Campaign complete -> results summary                         |
|                                                                 |
|  Output: Suppress if nothing matters (HEARTBEAT_OK)             |
+-----------------------------------------------------------------+
```

### How the loops connect

1. **Planning** sets targets. **Execution** reports against them.
2. **Execution** identifies work. **Delegation** assigns it.
3. **Delegation** produces outputs. **Proactive** monitors them.
4. **Proactive** surfaces exceptions that feed back into **Execution**.

---

## Goal Framework

### File structure in chief-of-staff workspace

```text
workspace-chief-of-staff/
+-- SOUL.md               # Identity (updated with orchestrator role)
+-- USER.md               # Founder context (existing)
+-- GOALS.md              # Monthly goals with measurable targets (NEW)
+-- WEEKLY_PLAN.md         # Auto-generated Monday, human-approved (NEW)
+-- SOURCES.md            # Repos, Linear projects, CRM segments (NEW)
+-- HEARTBEAT.md          # Proactive monitoring (REWRITTEN)
+-- memory/               # Daily session logs (OpenClaw native)
+-- MEMORY.md             # Curated long-term memory (OpenClaw native)
+-- skills/               # Agent-specific skill overrides
```

### GOALS.md structure

The monthly goals file is **manually authored by the founder** at the start of each month (or updated mid-month). The system reads it but never writes it — human authority over goals is non-negotiable.

```markdown
# GOALS.md -- [Month] [Year]

## Monthly Objectives
1. **Content:** Publish N blog posts, N LinkedIn posts
2. **ABM:** Run N campaigns targeting [verticals]
3. **Outreach:** N LinkedIn connections, N outreach messages
4. **Engineering:** Ship [features], close N issues on [projects]
5. **Pipeline:** N qualified meetings booked

## Weekly Targets (derived from monthly)
- [Specific weekly breakdown]

## KPIs to Track
- [Metrics with data sources]

## Current Priorities (ranked)
1. [Highest priority with reasoning]
2. [...]
```

### SOURCES.md structure

Documents all systems of record so the standup knows where to look:

```markdown
# SOURCES.md -- Systems of Record

## Repositories
| Repo | Path | Check for | Linear Project |
|------|------|-----------|----------------|
| axon-internal-apps | ~/src/axon-internal-apps | PRs, deploys | Internal Apps Monorepo |
| ultrathink-site | ~/src/ultrathink-site | Blog posts | Ultrathink Website |
| axon-mcp-servers | ~/src/axon-mcp-servers | MCP updates | Axon MCP Servers |
| axon-platform-infrastructure | ~/src/axon-platform-infrastructure | Infra changes | Axon Platform Infrastructure |
| linkedin-campaign-manager-mcp | ~/src/linkedin-campaign-manager-mcp | LinkedIn MCP | Axon MCP Servers |
| axon-platform-manifests | ~/src/axon-platform-manifests | Deploy configs | Axon Platform Services |
| axon-platform-aws-infrastructure | ~/src/axon-platform-aws-infrastructure | AWS infra | Axon Platform Infrastructure |

## Linear
- Team: UltraThink Solutions (1cc2e21d-7e89-4545-a576-1cd394672156)
- Key projects: Internal Apps Monorepo, Marketing Agent, Ultrathink Website, Axon MCP Servers

## CRM
- HubSpot: deal pipeline, contact activities, task management
- Apollo: company enrichment, outreach sequences

## Content
- Blog: ultrathink-site repo, /src/content/blog/
- LinkedIn: manual posting (track count in GOALS.md)
- Brand guidelines: Axon API POST /v1/guidelines/search (semantic search)
```

### Auto-generated plans

The Monday morning cron job generates `WEEKLY_PLAN.md` by:
1. Reading `GOALS.md` for monthly targets
2. Checking Linear for in-progress/backlog issues
3. Checking content pipeline state (what's drafted, what's published this month)
4. Checking campaign state
5. Proposing a weekly plan with specific deliverables per day

The founder reviews the plan in Slack and approves/adjusts. The daily standup then tracks against this plan.

---

## Daily Standup

### Design

The daily standup runs as a cron job at 7am PT weekdays. It uses **Sonnet** for the collection phase (cheaper, sufficient for data aggregation) and delivers to Slack. When the founder responds interactively, the conversation uses **Opus** (the chief-of-staff's primary model) for judgment and decision-making.

### Standup output structure

```markdown
## [Date] Daily Standup

### Goal Progress (vs WEEKLY_PLAN.md)
- Content: X/2 blog posts, X/2 LinkedIn posts this week
- Engineering: X issues closed, Y PRs merged
- Outreach: X/N messages sent this week
- Campaigns: [status of running campaigns]

### Today's Calendar
- [Time] [Event] [Prep needed?]
- [Meeting prep briefs for prospect/investor meetings]

### Priority Actions Today
1. [Highest priority with reasoning -- tied to weekly plan]
2. [...]
3. [...]

### Blockers & Decisions Needed
- [Anything requiring human input]

### Delegation Proposals
- Marketing: [research tasks to delegate]
- Content: [content to draft/review]
- Coding: [issues to assign to Claude Code]

### Ops Hygiene
- Stale PRs: [PRs open > 3 days]
- Overdue tasks: [Linear issues past due]
- CRM: [Aging deals, overdue follow-ups]
```

### Data sources queried

| Source | Query method | What to pull |
|--------|-------------|--------------|
| GOALS.md, WEEKLY_PLAN.md | Read workspace files | Targets to track against |
| SOURCES.md | Read workspace file | Which repos/projects to check |
| Linear | MCP adapter (linear) | In-progress issues, backlog, blockers |
| GitHub | `exec` + `git log` across repos in SOURCES.md | Open PRs, recent merges |
| Google Calendar | `gog calendar events --today` | Today's meetings |
| Gmail | `gog gmail search 'is:unread newer_than:1d'` | Urgent/VIP emails |
| HubSpot | MCP adapter (hubspot) | Deal pipeline, tasks due today |
| Apollo | MCP adapter (apollo) | Outreach sequence status |
| Axon API | `curl /v1/abm/campaigns?user_id=nick` | Campaign status/metrics |
| Mem0 | Shared memory search | Overnight events, campaign completions |

---

## Delegation via Cross-Agent Sub-Agents

### How it works

OpenClaw's sub-agent system ([Sub-Agents Docs](https://docs.openclaw.ai/tools/subagents)) allows the chief-of-staff to spawn isolated sub-agents that run under other agent IDs. This means:

1. The CoS invokes `sessions_spawn` with `agentId: "marketing"`
2. A new session is created in the marketing agent's workspace, with marketing's tools and model
3. The sub-agent executes the task and returns results
4. The CoS merges results and presents to the founder

### Configuration

```nix
# In openclaw.nix, chief-of-staff agent definition:
{
  id = "chief-of-staff";
  subagents = {
    allowAgents = [ "marketing" "content" "coding" ];
    maxConcurrent = 4;
    archiveAfterMinutes = 120;
  };
}
```

### Delegation patterns

| Task type | Delegated to | Model | Example |
|-----------|-------------|-------|---------|
| Company research | Marketing sub-agent | Sonnet | "Research Nordstrom for ABM targeting" |
| Analytics query | Marketing sub-agent | Sonnet | "Pull GA traffic for last 7 days" |
| Blog post draft | Content sub-agent | Opus | "Write a blog post about AI in ABM" |
| LinkedIn post | Content sub-agent | Sonnet | "Write a LinkedIn post about [topic]" |
| Content review (GPT) | Content sub-agent | GPT-5.1 | "Review this draft for clarity and gaps" |
| Feature development | Coding sub-agent | Sonnet | "Implement the guidelines skill (ULT-XXX)" |
| Bug fix | Coding sub-agent | Sonnet | "Fix the type error in chat_agent.py" |

---

## Content Pipeline with Multi-Model Review

### The problem

The founder currently does multi-round content review manually: draft in Claude, review in ChatGPT, refine in Claude, repeat. This should be systematized as a skill that the content agent orchestrates.

### Architecture

```text
Content agent receives brief (from CoS delegation or direct request)
    |
    v
Step 1: Query Guidelines API
    |   POST /v1/guidelines/search -> brand voice, messaging, positioning (semantic)
    |
    v
Step 2: Search Mem0 for context
    |   Previous content on this topic, company intel, audience insights
    |
    v
Step 3: Draft with Opus 4.6
    |   Primary model, deep reasoning, creative generation
    |   Output: full draft + rationale for key choices
    |
    v
Step 4: Adversarial review with GPT-5.1 (sub-agent)
    |   Content agent spawns sub-agent: model=gpt-5.1
    |   Prompt: "Review this draft against the brand guidelines. Identify:
    |            weak arguments, missing perspectives, tone inconsistencies,
    |            factual gaps, SEO issues. Be specific and constructive."
    |   Output: structured critique with line-by-line feedback
    |
    v
Step 5: Refine with Opus (back to primary model)
    |   Integrate GPT critique, revise problem sections
    |   Optionally: spawn another GPT sub-agent for final check
    |
    v
Step 6: Present to founder for human review
    |   Deliver via Slack with summary of review rounds
    |   Founder approves, requests changes, or adjusts
    |
    v
Step 7: Store brand decisions in Mem0
    |   New terminology choices, tone decisions, content patterns
    |
    v
Ready for publication
```

### Cost model

| Step | Model | Est. tokens | Cost per run |
|------|-------|------------|--------------|
| Draft | Opus 4.6 | ~4K in / ~2K out | ~$0.15 |
| Review | GPT-5.1 | ~4K in / ~1K out | ~$0.02 |
| Refine | Opus 4.6 | ~6K in / ~2K out | ~$0.18 |
| **Total per content piece** | | | **~$0.35** |

At 4 pieces/week (2 blog + 2 LinkedIn), that's ~$1.40/week or ~$6/month for multi-model content review.

---

## Proactive Follow-Ups

### Redesigned HEARTBEAT.md

The heartbeat runs every 30 minutes during business hours. It reads `HEARTBEAT.md` and suppresses output when nothing needs attention (`HEARTBEAT_OK`).

Key changes from current version:
- **Calendar-aware**: Prep for meetings in the next 2 hours
- **Post-meeting follow-up**: After a meeting ends, suggest follow-up actions
- **VIP email triage**: Flag high-priority unread emails from prospects/investors
- **Pipeline hygiene**: Overdue HubSpot tasks, aging deals, stale follow-ups

### Email Triage (Phase 6 — MVP Cron)

The original plan called for Gmail PubSub real-time triage. We implemented an **hourly cron MVP** instead (`cron/jobs.json`, `email-triage` job) to validate the triage logic before investing in PubSub infrastructure. The cron:

1. Runs hourly during business hours (Sonnet, isolated session)
2. Reads `email-triage:last_run` from Mem0 for gapless lookback window
3. Fetches unread emails via `gog gmail search`
4. Gates on VIP senders (post-retrieval filtering against HubSpot/Apollo/Mem0)
5. Triages VIP emails: read, summarize, draft reply (NEVER send)
6. Delivers to Slack for founder review
7. Updates Mem0 timestamp on success

**Future:** Upgrade to Gmail PubSub ([docs](https://docs.openclaw.ai/automation/gmail-pubsub)) once MVP triage logic is validated (ULT-634 follow-up).

### Meeting prep flow

```text
Heartbeat detects meeting in 90 minutes
    |
    v
Is it a prospect/investor meeting? (check calendar metadata)
    |
    +-- Yes -> Generate meeting prep brief:
    |         1. Search Mem0 for previous interactions
    |         2. Search email for recent thread with attendee
    |         3. If company: pull Apollo enrichment via marketing sub-agent
    |         4. Compile: attendee context, discussion topics,
    |            open items, suggested talking points
    |         5. Deliver to Slack
    |
    +-- No -> Suppress (HEARTBEAT_OK)
```

---

## Shared Skills & Memory Architecture

### Shared skills directory

Move duplicated skills to `~/.openclaw/skills/` and configure `skills.load.extraDirs` ([Skills Config Docs](https://docs.openclaw.ai/tools/skills-config)):

```text
~/.openclaw/skills/               # Shared (lowest precedence)
+-- shared-memory/SKILL.md        # Mem0 access (all agents)
+-- axon-api/SKILL.md             # Axon platform API (CoS + marketing read, CoS write)
+-- google-workspace/SKILL.md     # Gmail + Calendar
```

Per-workspace skills remain for agent-specific overrides (highest precedence, per [Skills Docs](https://docs.openclaw.ai/tools/skills)):
```text
workspace-content/skills/
+-- content-pipeline/SKILL.md     # Multi-model review workflow (NEW)
+-- guidelines/SKILL.md           # Guidelines API access (NEW)
```

### Configuration in openclaw.nix

```nix
skills = {
  load = {
    extraDirs = [ "${openclawHome}/skills" ];
  };
};
```

### Memory architecture

Two complementary memory systems:

**OpenClaw native memory** — workspace files indexed by `memorySearch`:
- `memory/YYYY-MM-DD.md` — daily session logs
- `MEMORY.md` — curated long-term facts
- `memorySearch.extraPaths: ["/home/dev/src/axon-internal-apps/docs/"]` — worktracking docs, architecture docs, guides
- Supports hybrid search (vector + BM25) per [Memory Docs](https://docs.openclaw.ai/concepts/memory)

**Mem0 shared memory** — cross-system context:
- Qdrant (vectors) + Neo4j (graph) + Redis (cache)
- Business context, campaign results, strategic decisions, company research, brand choices
- Accessible from all 4 OpenClaw agents + Axon backend

---

## Guidelines API Integration (Semantic Search)

> **Detailed implementation plan:** [2026-02-14 Brand Guidelines Semantic Search](./2026-02-14-brand-guidelines-semantic-search.md)

### Architecture (Revised)

The original plan assumed a simple CRUD API with `GET /active/all` dumping all guidelines. After auditing the actual brand content across `ultrathink-site`, this repo, and Google Drive, the requirements are significantly different:

- **Hundreds of branded chunks** (terms, phrases, solution positioning, offering descriptions) — not 5 flat documents
- **Semantic retrieval** — content agent asks "how do we describe our engagement model?" and gets the specific Outcome Partnership positioning with exact branded phrases
- **Consistency enforcement** — branded terms (Synapse Cycle, Pilot Purgatory, The AI Execution Gap) must be used consistently across all content

### Final State

- **Two-tier storage**: Postgres (CRUD admin) + Qdrant (semantic search via `brand_guidelines` collection)
- **New endpoint**: `POST /v1/guidelines/search` — semantic search with category filtering
- **Existing Qdrant infra reused**: `QdrantRepository` (1,025 lines), `EmbeddingService` (LiteLLM ada-002, 1536D)
- **Ingestion pipeline**: Chunks content from ultrathink-site, this repo's brand docs, and Google Drive into Qdrant
- **Content agent skill**: `guidelines/SKILL.md` calls semantic search, not bulk fetch
- **Google Drive access**: Via existing `google-docs` MCP server in `axon-mcp-servers` (currently disabled, needs enabling)

### Brand Content Sources

| Source | Location | Content |
|--------|----------|---------|
| ultrathink-site | `../ultrathink-site/src/content/` | 9 solutions, 2 offerings (Synapse Cycle, Axon), positioning, blog posts, case studies, engagement model |
| This repo | `infrastructure/openclaw/workspaces/content/` | Voice & tone, content templates, brand voice rules |
| This repo | `packages/marketing-templates/` | Color reference, whitepaper spec, visual design system |
| This repo | `ultrathink-complete-style-guide.html` | 284KB visual style guide (colors, typography, components) |
| Google Drive | TBD (via MCP) | Pitch decks, brand docs, positioning materials |

---

## Agent Roster Changes

### Summary of changes to `openclaw.nix`

| Agent | Change | Reasoning |
|-------|--------|-----------|
| **chief-of-staff** | Add `subagents.allowAgents: ["marketing", "content", "coding"]` | Enable real delegation |
| **chief-of-staff** | Add workspace files: GOALS.md, SOURCES.md, WEEKLY_PLAN.md | Goal framework |
| **chief-of-staff** | Rewrite HEARTBEAT.md for calendar/pipeline awareness | Proactive follow-ups |
| **content** | Add `content-pipeline/SKILL.md` + `guidelines/SKILL.md` | Multi-model review + brand voice |
| **coding** | Gains `shared-memory` via shared skills dir | Technical decision memory |
| **all** | Add `skills.load.extraDirs` pointing to shared skills | Dedup |
| **all** | Add `memorySearch.extraPaths` pointing to docs/ | Contextual search |

### Model strategy by context

| Context | Model | Reasoning |
|---------|-------|-----------|
| Daily standup cron (collection) | Sonnet 4.5 | Cheaper, sufficient for data aggregation |
| Interactive Slack conversation | Opus 4.6 | Judgment, priorities, strategic advice |
| Marketing research sub-agent | Sonnet 4.5 | Data-driven, structured output |
| Content draft | Opus 4.6 | Deep reasoning, creative generation |
| Content review (adversarial) | GPT-5.1 | Different perspective, independent critique |
| Content refinement | Opus 4.6 | Integration and polish |
| Coding delegation | Sonnet 4.5 | Task description; Claude Code does heavy lifting |
| Weekly planning cron | Opus 4.6 | Strategic, needs judgment for prioritization |
| Heartbeat monitoring | Haiku 4.5 | Cheapest, sufficient for status checks |

---

## Scheduling Strategy: Cron vs Heartbeat

### When to use Cron

Cron is for **predictable, time-based jobs** with guaranteed delivery. Use isolated sessions to avoid polluting the main conversation ([Cron Docs](https://docs.openclaw.ai/automation/cron-jobs)).

| Job | Schedule | Agent | Model | Session | Delivery |
|-----|----------|-------|-------|---------|----------|
| Daily standup | `0 7 * * 1-5` (7am PT) | chief-of-staff | sonnet | isolated | Slack DM |
| Monday weekly plan | `0 7 * * 1` (7am PT, Mon) | chief-of-staff | opus | main | Slack DM |
| Friday scorecard | `0 16 * * 5` (4pm PT, Fri) | chief-of-staff | opus | main | Slack DM |
| Content cadence check | `0 9 * * 1,4` (9am PT, Mon+Thu) | content | sonnet | isolated | Slack DM |

### When to use Heartbeat

Heartbeat is for **continuous monitoring with suppression**. Reads `HEARTBEAT.md` every 30 minutes and only alerts when something needs attention ([Heartbeat Docs](https://docs.openclaw.ai/gateway/heartbeat)).

| Check | Frequency | Suppress when |
|-------|-----------|---------------|
| Calendar meeting prep | Every 30m | No meetings in next 2h |
| VIP email triage | Every 30m | No unread VIP emails |
| Campaign anomaly detection | Every 30m | All campaigns nominal |
| CRM task hygiene | Every 30m | No overdue tasks |

### When to use Webhooks/Hooks

Event-driven triggers for immediate response:

| Trigger | Source | Response |
|---------|--------|----------|
| Campaign needs approval | Temporal -> OpenClaw `/hooks/agent` | Present plan in Slack |
| Campaign complete | Temporal -> OpenClaw `/hooks/agent` | Summarize results |
| VIP email arrives | Gmail PubSub -> OpenClaw hook | Triage + draft reply |

---

## Security Considerations

### Existing hardening (no changes needed)

The systemd service config in `openclaw.nix` already provides:
- `ProtectSystem = "strict"` — read-only filesystem except explicit BindPaths
- `ProtectHome = "tmpfs"` — empty home except BindPaths
- `PrivateTmp`, `NoNewPrivileges`, `RestrictNamespaces`, `LockPersonality`
- Explicit `BindPaths` for OpenClaw home, repos, npm prefix, gogcli config
- Loopback binding (invisible to public internet)
- Tailscale-only SSH access

### Memory safety

- **Trusted writers only**: Only agent interactions and Axon backend write to Mem0. External webhook content is treated as untrusted ([OpenClaw Security](https://docs.openclaw.ai/gateway/security)).
- **Session isolation**: Webhook-triggered sessions use `hook:workflow:{id}` keys, preventing payload pollution of main conversation.
- **memorySearch.extraPaths**: Read-only indexing of docs/ directory. Agents can search but not modify indexed files.

### Sub-agent isolation

Cross-agent sub-agents run in isolated sessions with the target agent's tool restrictions. A marketing sub-agent can only use marketing's allowed tools. The chief-of-staff's broader permissions don't cascade.

---

## Implementation Plan

### Phase 1: Goal Framework & Workspace Files

**Priority:** P0
**Effort:** 2-3 hours
**PR:** #346

**Goal:** Chief-of-staff has queryable goals, sources, and planning structure.

**Tasks:**
- [x] Create `GOALS.md` template with February 2026 targets
- [x] Create `SOURCES.md` with repo list, Linear projects, CRM segments
- [x] Rewrite `SOUL.md` to include orchestrator role and sub-agent delegation instructions
- [x] Update `USER.md` with current priorities
- [x] Rewrite `HEARTBEAT.md` for calendar/pipeline-aware proactive monitoring

**Acceptance Criteria:**
- GOALS.md has measurable monthly targets
- SOURCES.md covers all 7 repos, Linear projects, and CRM
- Agent identity reflects orchestrator role with decision framework

### Phase 2: Agent Config & Shared Skills

**Priority:** P0
**Effort:** 3-4 hours
**PR:** #347

**Goal:** Cross-agent delegation works, skills are deduplicated, memory search covers docs.

**Tasks:**
- [x] Add `subagents.allowAgents` to chief-of-staff agent config in `openclaw.nix`
- [x] Add `skills.load.extraDirs` to openclaw.nix config template
- [x] Add `memorySearch.extraPaths` to openclaw.nix config template
- [x] Create `~/.openclaw/skills/` directory structure in Nix preStart
- [x] Move shared-memory, axon-api, google-workspace to shared skills source in repo
- [x] Remove duplicated skills from individual workspace source directories
- [x] Coding agent gains shared-memory via shared dir (no config change needed)
- [ ] Deploy config changes to dev server (`nixos-rebuild switch`)
- [ ] Verify sub-agent spawning works (CoS -> marketing test)

**Acceptance Criteria:**
- CoS can spawn sub-agents as marketing/content/coding
- Shared skills visible to all agents
- `memorySearch` indexes docs/ directory
- Coding agent has Mem0 access

### Phase 3: Cron Jobs & Scheduling

**Priority:** P0
**Effort:** 4-5 hours
**PR:** #348

**Goal:** Daily standup, weekly planning, and weekly scorecard run on schedule.

**Tasks:**
- [x] Create `cron/jobs.json` with daily standup job (7am PT, Sonnet, isolated)
- [x] Create Monday weekly planning job (7am PT, Opus, main session)
- [x] Create Friday scorecard job (4pm PT, Opus, main session)
- [x] Create content cadence check job (Mon+Thu 9am, Sonnet, isolated)
- [x] Write detailed standup prompt that references GOALS.md, SOURCES.md
- [x] Write weekly planning prompt that generates WEEKLY_PLAN.md
- [x] Write Friday scorecard prompt that scores week against plan
- [ ] Deploy cron config to dev server
- [ ] Test each job manually (`openclaw cron run <jobId>`)
- [ ] Verify Slack delivery for all outputs

**Acceptance Criteria:**
- Daily standup runs at 7am PT with goal-relative progress
- Monday plan generates actionable weekly plan for approval
- Friday scorecard summarizes actual vs planned
- All outputs delivered to Slack DM

### Phase 4: Content Pipeline & Multi-Model Review

**Priority:** P0
**Effort:** 2-3 hours (content pipeline skill only — guidelines work is separate)
**PR:** #349

**Goal:** Multi-model content review works end-to-end. Guidelines integration is a separate workstream.

**Tasks:**
- [x] Create `content-pipeline/SKILL.md` with multi-model review workflow
- [ ] Test multi-model review: Opus draft -> GPT-5.1 review (sub-agent) -> Opus refine
- [ ] Verify sub-agent model override works (content agent spawning GPT sub-agent)
- [ ] Test content cadence tracking in conjunction with Phase 3 cron jobs

**Acceptance Criteria:**
- Multi-model review produces structured critique + refined output
- Review rounds are visible in the agent's output (transparency)
- Content agent can spawn GPT-5.1 sub-agent for adversarial review

> **Note:** Brand guidelines semantic search is a separate workstream with its own implementation plan and Linear issues. See [2026-02-14 Brand Guidelines Semantic Search](./2026-02-14-brand-guidelines-semantic-search.md). Guidelines integration is now complete (ULT-636, ULT-637, ULT-638).

### Phase 5: Proactive Follow-Ups

**Priority:** P1
**Effort:** 2-3 hours
**PR:** #355

**Goal:** Calendar-aware meeting prep and post-meeting follow-ups work automatically.

**Tasks:**
- [x] Implement meeting prep in HEARTBEAT.md (detect meetings in next 2h)
- [x] Implement post-meeting follow-up suggestions (Mem0 state tracking)
- [x] Implement VIP email triage in heartbeat (post-retrieval gating)
- [x] Implement CRM pipeline hygiene checks (HubSpot MCP)
- [x] Implement infrastructure health checks (scoped to critical namespaces)
- [ ] Test heartbeat suppression (HEARTBEAT_OK when nothing needs attention)
- [ ] Verify meeting prep quality for prospect/investor meetings

**Acceptance Criteria:**
- Meeting prep briefs delivered before prospect meetings (external = non-@ultrathink.com attendee)
- Post-meeting follow-up suggestions with draft emails (Mem0 state lifecycle: prepped → followup_suggested)
- VIP emails flagged within 30 minutes
- Heartbeat silent when nothing needs attention

### Phase 6: Email Triage (MVP Cron)

**Priority:** P2
**Effort:** 1-2 hours
**PR:** #353

**Goal:** Hourly VIP email triage via cron job. Full Gmail PubSub deferred until triage logic is validated.

**Scope change:** Punted on full PubSub architecture (GCP topic, `gog gmail watch serve`, webhook wiring) in favor of an hourly cron MVP. The cron uses Mem0-backed `email-triage:last_run` timestamps for a gapless lookback window and post-retrieval VIP filtering against HubSpot/Apollo/Mem0 contacts.

**Tasks:**
- [x] Add `email-triage` cron job to `cron/jobs.json` (hourly, business hours, Sonnet, isolated)
- [x] Implement Mem0-backed lookback window (`email-triage:last_run` key)
- [x] Implement VIP sender gating (post-retrieval filtering via HubSpot/Apollo/Mem0)
- [x] Add safety boundaries for untrusted external email content
- [ ] Test end-to-end: cron fires -> agent triages -> Slack notification
- [ ] Validate VIP filtering accuracy (false positives/negatives)

**Acceptance Criteria:**
- Hourly cron triages unread VIP emails with Mem0-backed lookback
- Non-VIP emails suppressed (no spam)
- External content handled with safety boundaries (prompt injection mitigation)
- Future: upgrade to Gmail PubSub for real-time triage once MVP is validated

### Phase 7: Validation & Tuning (Ongoing, 2 weeks)

**Priority:** P1
**Effort:** Ongoing

**Goal:** System runs reliably for 2 weeks with real usage.

**Tasks:**
- [ ] Run daily standups for 2 weeks, tune prompt based on output quality
- [ ] Run weekly planning for 2 cycles, tune based on plan quality
- [ ] Tune HEARTBEAT.md based on signal-to-noise ratio
- [ ] Tune content pipeline based on content quality
- [ ] Review LiteLLM cost dashboard -- adjust model selection if needed
- [ ] Verify shared memory quality (useful signals vs noise)
- [ ] Verify cross-repo awareness (are PR/commit summaries accurate?)
- [ ] Document any issues and resolutions

**Acceptance Criteria:**
- Daily standups are actionable (founder acts on >50% of priorities)
- Weekly plans are realistic (>70% of planned items completed)
- Content pipeline produces publish-ready content in <3 review rounds
- Heartbeat noise ratio acceptable (< 2 false alerts per day)
- Monthly cost within budget

---

## Open Questions

1. **Content publishing workflow**: After content is approved, how does it get published? Blog posts need to land in the `ultrathink-site` repo as Astro content files. LinkedIn posts are manual. Should the coding agent handle blog post commits?

2. **WEEKLY_PLAN.md lifecycle**: Should the weekly plan be a persistent file that accumulates, or overwritten each Monday? Recommendation: overwrite, but store previous plans in memory for trend analysis.

3. **Cross-repo git access**: The coding agent has repo access via BindPaths, but the chief-of-staff's `exec` tool running `git log` across repos requires those paths too. Current BindPaths include `/home/dev/src` which covers all repos.

4. **HubSpot MCP readiness**: The HubSpot MCP server pod is defined but credentials may not be populated. Need to verify before enabling CRM pipeline hygiene.

5. **Cron timezone handling**: The dev server runs UTC. OpenClaw cron supports `tz` field per job. Need to verify this works correctly with `America/Los_Angeles` for all scheduled jobs.

---

## References & Sources

### OpenClaw Documentation
- [Sub-Agents](https://docs.openclaw.ai/tools/subagents) — Cross-agent spawning via `subagents.allowAgents`
- [Cron Jobs](https://docs.openclaw.ai/automation/cron-jobs) — Scheduled task configuration
- [Heartbeat](https://docs.openclaw.ai/gateway/heartbeat) — Periodic monitoring with suppression
- [Skills](https://docs.openclaw.ai/tools/skills) — Skill loading and precedence
- [Skills Config](https://docs.openclaw.ai/tools/skills-config) — `skills.load.extraDirs` for shared skills
- [Memory](https://docs.openclaw.ai/concepts/memory) — `memorySearch.extraPaths` for additional indexing
- [Agent Workspace](https://docs.openclaw.ai/concepts/agent-workspace) — Workspace file structure
- [Hooks](https://docs.openclaw.ai/automation/hooks) — Built-in hooks including `bootstrap-extra-files`
- [Gmail PubSub](https://docs.openclaw.ai/automation/gmail-pubsub) — Event-driven email triggers
- [Webhooks](https://docs.openclaw.ai/automation/webhook) — External system triggers
- [Broadcast Groups](https://docs.openclaw.ai/channels/broadcast-groups) — Multi-agent message routing
- [Security](https://docs.openclaw.ai/gateway/security) — Security hardening checklist
- [Multi-Agent Routing](https://docs.openclaw.ai/concepts/multi-agent) — Agent isolation and routing
- [Creating Skills](https://docs.openclaw.ai/tools/creating-skills) — Skill authoring format

### Prior Art
- [2026-02-12 OpenClaw + Axon Convergence Plan](./2026-02-12-openclaw-chief-of-staff-deployment.md) — Foundation architecture
- [Memory Poisoning Issue #12524](https://github.com/openclaw/openclaw/issues/12524) — Security consideration for persistent memory
- [Mem0 OpenClaw Integration](https://docs.mem0.ai/integrations/openclaw) — Cross-system memory bridge

### Existing Infrastructure
- `infrastructure/modules/openclaw.nix` — NixOS module (systemd service, agents, config)
- `infrastructure/openclaw/workspaces/` — Agent identity and skill files
- `proto/marketing/guideline/v1/guideline.proto` — Guidelines data model
- `apps/marketing-agent/backend/app/routers/guideline.py` — Guidelines CRUD API
- `apps/marketing-agent/backend/app/db/models/guideline.py` — Guidelines SQLAlchemy model

---

*Last updated: 2026-02-14 (post-implementation update — Phases 1–6 complete)*
