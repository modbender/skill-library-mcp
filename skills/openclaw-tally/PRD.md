# Product Requirements Document: Task-Level Efficiency Analytics

**Product:** OpenClaw Task Metrics System
**Author:** Product Team
**Version:** 1.1
**Date:** 2026-02-23
**Status:** Decisions Locked — Ready for Engineering

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision & Goals](#3-product-vision--goals)
4. [User Personas](#4-user-personas)
5. [Requirements (P0/P1/P2)](#5-requirements)
6. [Technical Architecture](#6-technical-architecture)
7. [Task Complexity Framework](#7-task-complexity-framework)
8. [TES Metric Design](#8-tes-metric-design)
9. [Analytics Dimensions](#9-analytics-dimensions)
10. [Implementation Phases](#10-implementation-phases)
11. [Success Metrics](#11-success-metrics)
12. [Open Questions](#12-open-questions)
13. [Appendix](#13-appendix)

---

## 1. Executive Summary

### What We're Building

A **Task-Level Efficiency Analytics System** for OpenClaw that reframes AI assistant usage from token-counting to task-completion economics. Instead of asking "how many tokens did I use?", users will ask "how much did it cost to get X done, and was that a good deal?"

### Core Value Proposition

| For | Value |
|-----|-------|
| **Individual users** | Understand what you're paying for — per task, not per token |
| **Developers** | Optimize model selection and agent architecture by real task ROI |
| **Enterprise** | Budget forecasting, cost governance, and productivity measurement at the task level |

### Success Definition

The system is successful when:
- **80%+ of tasks** are automatically detected and bounded without user intervention
- Users can answer "what did my AI spend money on this week?" in under 10 seconds
- Model routing decisions improve TES by **≥20%** within 3 months of deployment

<!-- 核心洞见：用户不关心 token，关心的是「完成了什么事、花了多少钱」。
     这个系统把 OpenClaw 从「Token 计量器」变成「任务完成引擎」。 -->

---

## 2. Problem Statement

### Current State

OpenClaw tracks usage in **tokens and messages** — the unit of measure that LLM providers care about, not users. This creates several problems:

1. **Opaque costs.** A user sees "50,000 tokens consumed today" but has no idea whether that went toward a productive task or idle conversation. There's no mapping between spend and outcome.

2. **No task-level attribution.** A single user intent (e.g., "set up a daily job market scan") may span multiple sessions, sub-agents, and cron triggers. Today, these costs are siloed — there is no unified "task" ledger.

3. **Blind model selection.** Users and the system have no data on which model delivers the best cost/quality ratio for different task types. A simple lookup is routed the same as a complex multi-step mission.

4. **Cron black holes.** Scheduled automations run silently. Some deliver value daily; others burn tokens producing nothing useful. There is no visibility into cron ROI.

### User Need

> "I want to know: what tasks did my AI complete, how well, and at what cost — so I can decide if it's worth it and where to optimize."

### Market Opportunity

No AI assistant framework currently offers task-level unit economics. Usage dashboards exist (OpenAI, Anthropic), but they report raw consumption, not outcome-attributed cost. This is an opportunity to define a new category: **AI productivity accounting**.

---

## 3. Product Vision & Goals

### Vision

> OpenClaw becomes the first AI assistant framework where every dollar spent is attributable to a completed task, and every task has a measurable efficiency score.

### 6-Month Goals

| Goal | Metric |
|------|--------|
| Ship Task Detector (Layer 1) with ≥80% boundary accuracy | Precision/recall on labeled dataset |
| Ship Task Ledger (Layer 2) with full cost attribution | 100% of token spend attributed to a task_id |
| Launch basic analytics dashboard | Users can view task history, cost, and TES |

### 12-Month Goals

| Goal | Metric |
|------|--------|
| Automated model routing based on TES data | ≥20% TES improvement vs. static routing |
| Cron health scoring and auto-recommendations | ≥50% of users act on cron optimization suggestions |
| Enterprise cost governance API | API available, ≥2 enterprise pilots |

---

## 4. User Personas

### Persona 1: Solo Power User — "Alex"

- **Profile:** Individual using OpenClaw as a daily productivity assistant. Non-technical. Pays monthly subscription.
- **Pain:** "My bill went up 40% this month. Was it worth it? I have no idea."
- **Need:** A simple dashboard showing: tasks completed, cost per task, trends over time.
- **Success:** Alex can open a weekly summary and say "I completed 47 tasks for $12.30 — the daily news briefing alone was $4, maybe I should simplify it."

### Persona 2: Developer / Tinkerer — "Sam"

- **Profile:** Technical user building custom agents and cron jobs on OpenClaw. Cares deeply about optimization.
- **Pain:** "I have 6 cron jobs running but no idea which ones are worth their cost. My sub-agent architecture might be wasteful."
- **Need:** Per-model TES breakdowns, cron efficiency scores, complexity-level analytics. API access to raw task data.
- **Success:** Sam discovers that switching L2 tasks from Opus to Sonnet saves 60% cost with identical quality, and that one cron job has a 0.0 quality score (never produces useful output).

### Persona 3: Enterprise Admin — "Jordan"

- **Profile:** Manages OpenClaw deployment for a 50-person team. Responsible for AI budget and governance.
- **Pain:** "I can't justify the AI spend to finance because I can't tie it to business outcomes."
- **Need:** Team-level dashboards, cost allocation by department/project, budget alerts, exportable reports.
- **Success:** Jordan presents a quarterly report: "Engineering completed 1,200 L3 tasks at $0.18 avg cost, 94% success rate. Marketing's cron automations saved 120 hours."

---

## 5. Requirements

### P0 — Must Have (MVP)

| ID | Requirement | Description |
|----|-------------|-------------|
| P0-1 | **Task boundary detection** | Automatically detect TASK_START, TASK_END, TASK_FAILED from message stream using lightweight LLM |
| P0-2 | **Task cost attribution** | Attribute all token consumption (main session, sub-agents, cron) to a task_id |
| P0-3 | **Complexity classification** | Auto-classify tasks as L1–L4 with complexity score (0–100) |
| P0-4 | **TES calculation** | Compute Task Efficiency Score for every completed task |
| P0-5 | **Task history storage** | Persistent task records with full metadata (see Appendix A) |
| P0-6 | **Basic task list view** | User can see recent tasks with status, cost, and TES |

### P1 — Should Have (V1.1)

| ID | Requirement | Description |
|----|-------------|-------------|
| P1-1 | **Model efficiency breakdown** | Per-model TES at each complexity level |
| P1-2 | **Session efficiency view** | Identify high-cost/low-output sessions |
| P1-3 | **Cron efficiency scoring** | Per-cron TES, success rate, cost trends |
| P1-4 | **Weekly summary report** | Auto-generated digest: tasks, spend, highlights |
| P1-5 | **Cost anomaly alerts** | Notify when a task or cron exceeds cost thresholds |
| P1-6 | **CLI analytics commands** | `openclaw tasks list`, `openclaw tasks stats` |

### P2 — Nice to Have (V2+)

| ID | Requirement | Description |
|----|-------------|-------------|
| P2-1 | **Smart model routing** | Auto-select model based on historical TES for task complexity |
| P2-2 | **Team/org dashboards** | Multi-user cost allocation and governance |
| P2-3 | **Budget caps per task type** | Set spending limits by complexity level or cron |
| P2-4 | **Task quality feedback loop** | User can rate task quality; improves quality_score accuracy |
| P2-5 | **Export & API** | REST API for task data; CSV/JSON export |
| P2-6 | **Predictive cost estimation** | "This task will likely cost ~$0.15" before execution |

---

## 6. Technical Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────────────────────┐
│                    User / Cron Trigger                    │
└──────────────────────────┬──────────────────────────────┘
                           │ messages
                           ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: Task Detector                                  │
│                                                          │
│  • Lightweight LLM (Flash-class) per message             │
│  • Emits: TASK_START / TASK_PROGRESS /                   │
│           TASK_COMPLETE / TASK_FAILED                     │
│  • Assigns task_id, links sub-agents & cron to parent    │
│  • Computes complexity_score + complexity_level           │
└──────────────────────────┬──────────────────────────────┘
                           │ task events
                           ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: Task Ledger                                    │
│                                                          │
│  • Accumulates token usage per task_id                   │
│  • Sources: main session, sub-agents, cron triggers,     │
│             tool calls, external API calls                │
│  • Stores: TaskRecord (see Appendix A)                   │
│  • Storage: SQLite (local) / PostgreSQL (enterprise)     │
└──────────────────────────┬──────────────────────────────┘
                           │ task records
                           ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: Analytics Engine                               │
│                                                          │
│  • Computes TES, Density, Utility per task               │
│  • Aggregates by: model / session / cron                 │
│  • Powers: dashboard, reports, alerts, routing hints     │
└─────────────────────────────────────────────────────────┘
```

### Data Flow (End-to-End)

```
User msg ──► Gateway ──► Agent (executes) ──► Tool calls
                │                                  │
                │ [every message]                   │ [token counts]
                ▼                                  ▼
         Task Detector ◄──── token usage events ────┘
              │
              │ emit task event
              ▼
         Task Ledger ──► persist TaskRecord
              │
              │ on TASK_COMPLETE / TASK_FAILED
              ▼
       Analytics Engine ──► compute TES
              │                │
              ▼                ▼
         Dashboard        Alerts / Reports
```

### Layer 1: Task Detector — Design Details

**Input:** Every user message and agent response in the message stream.

**Processing model:** A lightweight, fast LLM (e.g., Gemini Flash, Haiku) classifies each message with one of:

| Label | Trigger |
|-------|---------|
| `TASK_START` | User expresses intent ("帮我…", "create…", "fix…") or cron payload begins |
| `TASK_PROGRESS` | Ongoing work — tool calls, intermediate outputs, follow-up questions |
| `TASK_COMPLETE` | Output delivered + user confirms, agent declares done, or silence timeout |
| `TASK_FAILED` | Agent error, user rejects ("不对", "重来") |

**Key design decisions:**

<!-- 决策：用轻量 LLM 做语义检测而不是规则引擎。
     原因：用户表达意图的方式太多样，规则无法覆盖。
     成本：Flash 模型每条消息 ~0.001 美分，可忽略不计。 -->

- **Semantic over rule-based.** User intent is expressed in too many ways for regex. A small LLM handles ambiguity.
- **Cost budget:** Detector LLM cost must be <1% of the task's own cost. Use the cheapest capable model.
- **Cross-session linking:** When a sub-agent is spawned, the parent task_id is propagated via session metadata. Cron-triggered tasks inherit the cron's task_id lineage.
- **Timeout heuristic:** If no user message follows a delivered output for >5 minutes, mark TASK_COMPLETE (configurable).

### Layer 2: Task Ledger — Design Details

**Responsibility:** Single source of truth for "how much did task X cost?"

**Token attribution rules:**
1. All tokens in a message exchange tagged with a task_id are attributed to that task.
2. Sub-agent tokens are attributed to the parent task that spawned them.
3. Cron-triggered tokens are attributed to the cron's task lineage.
4. Detector LLM tokens are overhead — tracked separately, not attributed to any user task.

**Storage:**
- Local: SQLite database at `~/.openclaw/data/task-ledger.db`
- Enterprise: PostgreSQL with partitioning by month

### Layer 3: Analytics Engine — Design Details

**Responsibility:** Compute derived metrics and power all analytics surfaces.

**Core computations:**
- TES per task (see §8)
- Aggregated TES by model, session, cron
- Cost trends (daily/weekly/monthly)
- Anomaly detection (cost spikes, quality drops)

**Execution:** Runs on-demand (when dashboard is viewed) and on schedule (weekly summary generation).

---

## 7. Task Complexity Framework

### Level Definitions

| Level | Name | Characteristics | Typical Complexity Score | Examples |
|-------|------|----------------|--------------------------|----------|
| **L1** | Reflex | Single-turn, text-only, no tool calls | 0–10 | "What time is it in Tokyo?", "Translate this sentence" |
| **L2** | Routine | Multi-turn OR 1–3 tool calls | 11–30 | "Check this PR status", "Search for X and summarize" |
| **L3** | Mission | Multiple tools + file I/O + external APIs | 31–60 | "Save this article to Notion and analyze it", "Write a PRD and save to file" |
| **L4** | Campaign | Sub-agents + cron + cross-session continuity | 61–100 | "Scan job market daily and send briefing", "Monitor competitor pricing weekly" |

### Complexity Scoring Formula

```
complexity_score = min(100,
    tool_calls × 5
  + sub_agents × 15
  + cross_session_count × 10
  + external_api_calls × 3
  + cron_triggered × 20
  + user_turns × 2
)
```

**Level assignment:**

| Score Range | Level |
|-------------|-------|
| 0–10 | L1 |
| 11–30 | L2 |
| 31–60 | L3 |
| 61–100 | L4 |

### Boundary Cases & Rules

<!-- 边界案例很重要：这些是系统容易出错的地方。 -->

| Scenario | Resolution |
|----------|------------|
| User asks a simple question, then pivots to a complex task | Split into two tasks at the pivot point. Detector emits TASK_COMPLETE for Q&A, then TASK_START for the new intent. |
| A task has 0 tool calls but involves a very long, thoughtful response (e.g., essay writing) | Stays L1 by formula. This is intentional — complexity measures *system resource usage*, not intellectual depth. |
| Sub-agent spawns another sub-agent | Both count toward the parent task's sub_agent tally. Depth doesn't multiply — we count total sub-agents. |
| Cron triggers but produces no output (no-op) | Still a task. Complexity = 20 (cron weight). Quality = 0.0 if no useful output. This surfaces cron waste. |
| User says "never mind" mid-task | TASK_FAILED. Tokens consumed so far are fully attributed. Quality = 0.0. |
| Ambiguous — is it one task or two? | Detector decides. In ambiguous cases, prefer fewer, larger tasks (lumping over splitting). |

---

## 8. TES Metric Design

### Formula

```
TES = Task_Quality / (Normalized_Cost × Complexity_Weight)
```

Where:

| Component | Definition | Range |
|-----------|-----------|-------|
| **Task_Quality** | Outcome quality score | 0.0 – 1.0 |
| **Normalized_Cost** | `total_cost_usd / median_cost_for_level` | 0.01 – ∞ |
| **Complexity_Weight** | `1.0 / (1.0 + ln(complexity_score + 1))` | ~0.2 – 1.0 |

### Task Quality Scoring

| Outcome | Quality Score | Definition |
|---------|--------------|------------|
| First-attempt success | **1.0** | Task completed with no corrections or retries |
| Success after revision | **0.7** | User requested changes; task completed on 2nd+ attempt |
| Partial success | **0.4** | Some deliverables produced, but user abandoned or pivoted |
| Failure | **0.0** | Task explicitly failed or was rejected |

<!-- 质量评分先用规则，后续 P2 加入用户反馈校准。 -->

### Normalized Cost

Raw USD cost is meaningless without context — $0.50 is cheap for an L4 campaign but expensive for an L1 lookup. We normalize against the **rolling median cost for that complexity level**:

```
Normalized_Cost = task_cost_usd / median_cost_usd[task.complexity_level]
```

- A task at exactly median cost → Normalized_Cost = 1.0
- A task costing 2× median → Normalized_Cost = 2.0
- Cheaper than median → Normalized_Cost < 1.0

During cold-start (insufficient data), use hardcoded defaults:

| Level | Default Median Cost |
|-------|-------------------|
| L1 | $0.005 |
| L2 | $0.03 |
| L3 | $0.15 |
| L4 | $0.80 |

### Complexity Weight

Higher-complexity tasks are inherently harder — we don't want to penalize them unfairly:

```
Complexity_Weight = 1.0 / (1.0 + ln(complexity_score + 1))
```

This means L4 tasks get a "discount" on cost in TES — they're expected to cost more.

### TES Interpretation Guide

| TES Range | Interpretation |
|-----------|---------------|
| > 2.0 | 🟢 Excellent — task completed well, below-average cost |
| 1.0 – 2.0 | 🟡 Good — normal efficiency |
| 0.5 – 1.0 | 🟠 Below average — cost higher than typical for this complexity |
| < 0.5 | 🔴 Poor — expensive and/or low quality |
| 0.0 | ⚫ Failed task — no value delivered |

### Example Calculations

**Example 1: Quick lookup (L1)**
- Quality: 1.0 (answered correctly, first try)
- Cost: $0.003 → Normalized: 0.003/0.005 = 0.6
- Complexity score: 2 → Weight: 1/(1+ln(3)) ≈ 0.48
- **TES = 1.0 / (0.6 × 0.48) = 3.47** → 🟢 Excellent

**Example 2: Multi-step mission (L3)**
- Quality: 0.7 (needed one revision)
- Cost: $0.23 → Normalized: 0.23/0.15 = 1.53
- Complexity score: 42 → Weight: 1/(1+ln(43)) ≈ 0.21
- **TES = 0.7 / (1.53 × 0.21) = 2.18** → 🟢 Excellent

---

## 9. Analytics Dimensions

### Dimension 1: Model Efficiency

**Question answered:** "Which model gives the best bang for buck at each complexity level?"

| Metric | Formula | Purpose |
|--------|---------|---------|
| **Model TES by Level** | avg(TES) grouped by model × complexity_level | Find optimal model per task type |
| **Model Cost per Quality Point** | avg(cost) / avg(quality) per model | Raw cost-effectiveness |
| **Model Success Rate** | count(quality > 0) / count(*) per model | Reliability |
| **Model Speed** | avg(task_duration) per model | Latency impact |

**Target output:**

```
Model Efficiency Report (Last 30 Days)
────────────────────────────────────────
                  L1      L2      L3      L4
Sonnet 4.6     ★ 3.2    ★ 2.1    1.4     0.9
Opus 4.6         2.8      2.3   ★ 2.0   ★ 1.8
Flash 2.0      ★ 3.5      1.5    0.7     N/A
Haiku 3.5      ★ 3.4      1.2    N/A     N/A

★ = Recommended for this level
```

### Dimension 2: Session Efficiency

**Question answered:** "Which sessions are productive vs. just burning tokens on chat?"

| Metric | Formula | Purpose |
|--------|---------|---------|
| **Task Density** | tasks_completed / session_duration_hours | Productivity rate |
| **Session TES** | avg(TES) across all tasks in session | Overall session quality |
| **Idle Ratio** | tokens_outside_tasks / total_tokens | How much is "overhead" |
| **Cost per Task** | session_total_cost / tasks_completed | Average task cost in session |

<!-- Session 分析的价值：找出"闲聊型"session（高 token、低任务密度）和"高效型"session。 -->

### Dimension 3: Cron Efficiency

**Question answered:** "Which automations are worth their cost?"

| Metric | Formula | Purpose |
|--------|---------|---------|
| **Cron TES** | avg(TES) for all tasks triggered by this cron | Is this cron efficient? |
| **Cron Success Rate** | successful_runs / total_runs | Reliability |
| **Cron Monthly Cost** | sum(cost) for 30-day window | Budget impact |
| **Cron Utility Score** | success_rate × avg(quality) / monthly_cost | Overall ROI |
| **Dud Rate** | runs_with_zero_quality / total_runs | How often does it produce nothing? |

**Cron Health Classification:**

| Category | Criteria | Action |
|----------|----------|--------|
| 🟢 Healthy | Utility > 1.0, success rate > 80% | Keep running |
| 🟡 Underperforming | Utility 0.3–1.0 or success rate 50–80% | Review and optimize |
| 🔴 Wasteful | Utility < 0.3 or success rate < 50% | Recommend disable/rewrite |
| ⚫ Dead | 0% success rate over 7+ days | Auto-pause with notification |

---

## 10. Implementation Phases

### Phase 0: Instrumentation Foundation (Weeks 1–3)

**Goal:** Get the raw data flowing.

- [ ] Add token-usage event emission at the gateway level (per message, per tool call)
- [ ] Add session/sub-agent/cron lineage tracking (propagate parent IDs)
- [ ] Design and create SQLite schema for task records
- [ ] Build event bus for inter-layer communication

**Deliverable:** Every token spent is observable and attributable to a session + cron context.

### Phase 1: Task Detection + Ledger (Weeks 4–8)

**Goal:** Automatically identify tasks and attribute costs.

- [ ] Implement Task Detector (Layer 1) with Flash-class LLM
- [ ] Build labeled dataset (~500 conversations) for accuracy benchmarking
- [ ] Achieve ≥80% boundary detection accuracy (precision + recall)
- [ ] Implement Task Ledger (Layer 2) — aggregate tokens → task_id
- [ ] Handle cross-session and sub-agent attribution
- [ ] CLI: `openclaw tasks list` — show recent tasks with cost and status

**Deliverable:** Users can run `openclaw tasks list` and see their task history with costs.

### Phase 2: Analytics + Dashboard (Weeks 9–14)

**Goal:** Compute TES and surface insights.

- [ ] Implement Analytics Engine (Layer 3)
- [ ] Compute TES for all historical tasks
- [ ] Build model efficiency report
- [ ] Build session efficiency report
- [ ] Build cron efficiency report with health classification
- [ ] Weekly auto-generated summary (delivered via configured channel)
- [ ] Cost anomaly alerts
- [ ] CLI: `openclaw tasks stats`, `openclaw tasks report`

**Deliverable:** Full analytics suite. Users get weekly reports and can drill into any dimension.

### Phase 3: Intelligence + Governance (Weeks 15–22)

**Goal:** Act on insights automatically.

- [ ] Smart model routing based on TES data (auto-select cheapest model that maintains quality)
- [ ] Cron auto-pause for dead automations
- [ ] Budget caps and alerts per task type
- [ ] User quality feedback integration (thumbs up/down → quality_score calibration)
- [ ] Enterprise: multi-user dashboards, cost allocation, export API
- [ ] Predictive cost estimation ("this task will likely cost ~$X")

**Deliverable:** OpenClaw actively optimizes its own cost-efficiency based on task data.

---

## 11. Success Metrics

### North Star Metric

> **Average TES across all tasks** — trending upward over time means the system is getting more efficient at completing tasks per dollar spent.

### KPIs

| KPI | Target (6mo) | Target (12mo) |
|-----|--------------|---------------|
| Task detection accuracy (F1) | ≥ 0.80 | ≥ 0.90 |
| % of token spend attributed to a task | ≥ 90% | ≥ 98% |
| Average TES (all tasks) | Establish baseline | ≥ 20% improvement |
| User engagement with task analytics | ≥ 30% weekly active | ≥ 50% weekly active |
| Cron waste reduction | Identify top 3 wasteful crons per user | ≥ 30% cost reduction in cron spend |

### Guardrails

<!-- Guardrails = 不能突破的底线，防止优化一个指标时牺牲另一个。 -->

| Guardrail | Threshold | Rationale |
|-----------|-----------|-----------|
| Detector overhead cost | < 1% of total spend | Detection shouldn't cost more than it saves |
| False TASK_FAILED rate | < 5% | Don't penalize tasks that actually succeeded |
| Analytics latency | < 2s for dashboard load | Real-time feel |
| Data retention | ≥ 90 days task history | Users need trend data |
| Privacy | No task content stored — only metadata | Task records contain metrics, not conversation content |

---

## 12. Design Decisions (Previously Open Questions)

<!-- 2026-02-23: 所有问题已在产品讨论中拍板，更新为 Decisions Locked 状态。 -->

| # | Question | Options | Decision | Rationale |
|---|----------|---------|----------|-----------|
| 1 | **Should the Task Detector run synchronously (blocking) or async?** | Sync adds latency; async may miss rapid-fire messages. | ✅ **Async** | UX-first. Latency is a hard failure mode (ref: Relay learnings). Compensate with accuracy tuning if needed, not by adding latency. |
| 2 | **How to handle "compound tasks"?** E.g., user says "do A, B, and C" in one message. | (a) One task with sub-deliverables. (b) Three separate tasks. | ✅ **One task + sub-deliverables via `parent_task_id`** | Simpler for P0. Use `parent_task_id` chaining for granular tracking. Revisit in P1 if users request per-deliverable cost breakdown. |
| 3 | **Quality score: rules-only or LLM-judged?** | Rules are deterministic and free. LLM judgment is more accurate but adds cost. | ✅ **Rules for P0; LLM judgment as P2** | Rules must be user-configurable (no hardcoding). LLM judge added in P2 as opt-in enhancement. |
| 4 | **What's the right timeout for "silent completion"?** | 2min / 5min / 10min / configurable. | ✅ **Complexity-tiered timeouts** | L1=2min / L2=5min / L3=15min / L4=60min. User-configurable per level. Flat timeout fails for long-running L4 tasks. |
| 5 | **Should TES be visible to the user by default, or opt-in?** | Always-on may overwhelm casual users; opt-in reduces adoption. | ✅ **Default-on in CLI + Dashboard; no push notifications** | TES is the core product differentiator. Hiding it defeats the purpose. Notifications opt-in only. |
| 6 | **Enterprise: multi-tenant or single-tenant?** | Multi-tenant is cheaper to operate; single-tenant gives data isolation. | ✅ **Single-tenant (local SQLite) for V1** | Directly aligns with OpenClaw's "personal assistant" security model ("It's not a bus" — steipete, 2026-02-22). Multi-tenant for future cloud offering only. |
| 7 | **How to bootstrap complexity_level medians with no historical data?** | Hardcoded defaults vs. global anonymized benchmarks. | ✅ **Hardcoded defaults → user medians after 50+ tasks** | Community opt-in for anonymized benchmarks as future enhancement (clawhub telemetry). |
| 8 | **Should failed tasks count toward model efficiency scores?** | Including penalizes models used for hard tasks; excluding hides reliability. | ✅ **Include failed tasks** | A model that fails frequently should score lower. Reliability is part of efficiency. |

---

## 13. Appendix

### Appendix A: Task Record Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TaskRecord",
  "type": "object",
  "required": ["task_id", "started_at", "status", "complexity_level"],
  "properties": {
    "task_id": {
      "type": "string",
      "pattern": "^tsk_[a-zA-Z0-9]{12,}$",
      "description": "Unique task identifier"
    },
    "parent_task_id": {
      "type": ["string", "null"],
      "description": "Parent task ID if this is a sub-task"
    },
    "started_at": {
      "type": "string",
      "format": "date-time"
    },
    "completed_at": {
      "type": ["string", "null"],
      "format": "date-time"
    },
    "status": {
      "type": "string",
      "enum": ["in_progress", "completed", "failed", "abandoned"]
    },
    "complexity_score": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100
    },
    "complexity_level": {
      "type": "string",
      "enum": ["L1", "L2", "L3", "L4"]
    },
    "quality_score": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "total_tokens": {
      "type": "integer",
      "description": "Total tokens consumed (input + output, all sessions)"
    },
    "total_cost_usd": {
      "type": "number",
      "description": "Total cost in USD"
    },
    "tes": {
      "type": ["number", "null"],
      "description": "Computed Task Efficiency Score"
    },
    "models_used": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of model identifiers used"
    },
    "sessions": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Session IDs involved"
    },
    "sub_agents": {
      "type": "integer",
      "description": "Number of sub-agents spawned"
    },
    "cron_id": {
      "type": ["string", "null"],
      "description": "Cron job ID if triggered by cron"
    },
    "cron_triggered": {
      "type": "boolean"
    },
    "tools_called": {
      "type": "integer",
      "description": "Total tool invocations"
    },
    "tool_names": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Distinct tool names used"
    },
    "external_api_calls": {
      "type": "integer"
    },
    "user_turns": {
      "type": "integer",
      "description": "Number of user messages in the task"
    },
    "intent_summary": {
      "type": "string",
      "description": "One-line summary of what the user wanted (generated by detector)"
    },
    "outcome_summary": {
      "type": "string",
      "description": "One-line summary of what was delivered"
    }
  }
}
```

### Appendix B: API Design (Draft)

#### List Tasks

```
GET /api/v1/tasks
  ?status=completed|failed|in_progress
  &level=L1|L2|L3|L4
  &from=2026-01-01
  &to=2026-02-23
  &limit=50
  &offset=0

Response: {
  "tasks": [TaskRecord],
  "total": 1234,
  "aggregates": {
    "avg_tes": 1.82,
    "total_cost_usd": 45.67,
    "total_tasks": 1234,
    "success_rate": 0.91
  }
}
```

#### Get Task Detail

```
GET /api/v1/tasks/:task_id

Response: TaskRecord (full, with token breakdown per session/model)
```

#### Analytics Summary

```
GET /api/v1/analytics/summary
  ?period=7d|30d|90d
  &dimension=model|session|cron

Response: {
  "period": "30d",
  "dimension": "model",
  "breakdown": [
    {
      "key": "claude-sonnet-4-6",
      "tasks": 450,
      "avg_tes": 2.1,
      "total_cost": 12.30,
      "success_rate": 0.94,
      "by_level": {
        "L1": { "avg_tes": 3.2, "count": 200 },
        "L2": { "avg_tes": 2.1, "count": 150 },
        "L3": { "avg_tes": 1.4, "count": 80 },
        "L4": { "avg_tes": 0.9, "count": 20 }
      }
    }
  ]
}
```

#### Cron Health

```
GET /api/v1/analytics/cron-health

Response: {
  "crons": [
    {
      "cron_id": "cron_abc",
      "name": "Daily job market scan",
      "health": "healthy",
      "runs_30d": 30,
      "success_rate": 0.93,
      "monthly_cost": 4.20,
      "avg_tes": 1.8,
      "utility_score": 1.5
    }
  ]
}
```

### Appendix C: CLI Commands (Draft)

```bash
# List recent tasks
openclaw tasks list [--limit 20] [--level L3] [--status completed]

# Show task detail
openclaw tasks show tsk_xxx

# Summary statistics
openclaw tasks stats [--period 30d]

# Model efficiency report
openclaw tasks report --dimension model

# Cron health check
openclaw tasks cron-health

# Weekly report (manual trigger)
openclaw tasks report --weekly
```

---

*End of document. For questions or feedback, open an issue in the task-metrics repository.*
