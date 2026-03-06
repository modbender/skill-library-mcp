# OpenClaw Architecture Reference

Deep technical reference for OpenClaw's autonomous agent framework.
Load when researching OpenClaw architecture, debugging agent behavior, or designing autonomous systems.

## Table of Contents
1. Core Architecture (Gateway + Agent Runtime)
2. Heartbeat Daemon
3. Cron Scheduler
4. Memory Architecture
5. Session & Compaction
6. Multi-Model Failover
7. Sub-Agent System
8. Tool Execution & Sandboxing
9. Lobster Workflow Engine
10. Observability & Monitoring

---

## 1. Core Architecture

OpenClaw separates **Gateway** (control plane) from **Agent Runtime** (execution plane).

**Gateway (long-lived Node.js daemon):**
- WebSocket RPC at `ws://127.0.0.1:18789`
- Handles 12+ messaging channels (WhatsApp, Telegram, Discord, Slack, SMS, web, etc.)
- Session registry, lane-aware FIFO queue
- Heartbeat runner, cron scheduler
- Config hot-reload via chokidar (watches `openclaw.json`)
- `gateway.reload.mode: hybrid` (default) — hot-apply safe changes, auto-restart for infrastructure

**Agent Runtime (per-turn execution):**
- Reasoning loop (ReAct pattern)
- Tool invocation with policy filtering
- Context window management
- Memory flush/read operations

**Execution Pipeline:**
```
User Message → Session Resolution → Workspace Setup → Model Selection →
System Prompt Building → Tool Policy Resolution → Model Prompting →
Tool Execution → Response → Memory Flush
```

**System Prompt Assembly Order:**
1. Identity section (IDENTITY.md / SOUL.md)
2. Skills section (eligible skills XML)
3. Tools section (available tools per policy)
4. Memory section (MEMORY.md + short-term)
5. Context files (TASKS.md, etc.)

## 2. Heartbeat Daemon — The Autonomy Primitive

Periodic self-activation that transforms agent from reactive to proactive.

**Mechanism:**
- Configurable interval (default: 30 minutes)
- Reads `HEARTBEAT.md` checklist
- Evaluates current state against checklist
- Responds `HEARTBEAT_OK` if nothing needs attention, or takes action
- Duplicate suppression prevents overlapping beats

**Configuration (`openclaw.json`):**
```json
{
  "heartbeat": {
    "enabled": true,
    "intervalMs": 1800000,
    "activeHours": { "start": "08:00", "end": "22:00" },
    "targetChannel": "telegram",
    "suppressDuplicates": true
  }
}
```

**CRITICAL: Token Sink Problem**
Native heartbeat loads full main-session context: **170K-210K tokens per beat**.
At 30-minute intervals during 14-hour active window = ~28 beats/day = 4.76M-5.88M tokens/day on heartbeat alone.

**Community-Validated Mitigation:**
1. Disable native heartbeat
2. Replace with isolated cron heartbeat
3. Pair with `openclaw-mem` plugin for smart context without full history
4. Cron heartbeat runs in fresh session = minimal token cost

**HEARTBEAT.md Structure (example):**
```markdown
# Heartbeat Checklist
## Priority 1 — Immediate
- Check inbox for urgent messages requiring response
- Check calendar for upcoming events (next 2 hours)
## Priority 2 — Routine
- Review TASKS.md for pending items
- Check monitored repos for new issues/PRs
## Priority 3 — Background
- Scan news feeds for monitored topics
- Update research queue status
```

## 3. Cron Scheduler

Precise time-based task execution with isolated sessions.

**Key Difference from Heartbeat:**
- Heartbeat: regular interval, full conversational context, monitoring role
- Cron: precise 5-field scheduling, isolated sessions, specific actions

**Configuration (`cron/jobs.json`):**
```json
[
  {
    "pattern": "0 7 * * 1-5",
    "prompt": "Generate daily briefing from TASKS.md and inbox",
    "channel": "telegram",
    "session": "cron-daily-brief"
  },
  {
    "pattern": "0 9 * * 1",
    "prompt": "Weekly research review: check all monitored topics for updates",
    "channel": "telegram",
    "session": "cron-weekly-research"
  }
]
```

**Best Practice Pattern:**
- Heartbeat: batched monitoring (inbox/calendar/tasks every 30m)
- Cron: scheduled actions (daily reports 7 AM, weekly reviews Monday 9 AM)
- Cron heartbeat: lightweight state check in isolated session (replaces native)

## 4. Memory Architecture — Two-Tier File-Based

**Short-term memory:**
- Location: `memory/YYYY-MM-DD.md`
- Behavior: daily append-only logs
- Contains: conversation excerpts, decisions, observations
- Lifecycle: accumulates daily, feeds into long-term curation

**Long-term memory:**
- Location: `MEMORY.md`
- Behavior: curated knowledge base
- Contains: user preferences, established patterns, project context, learned behaviors
- Maintenance: agent periodically consolidates short-term into long-term

**Session transcripts:**
- Location: `~/.openclaw/agents/<agentId>/sessions/*.jsonl`
- Format: JSONL audit trail
- Contains: complete message history, tool calls, model responses

**Semantic search:**
- Hybrid BM25 + vector retrieval via sqlite-vec
- Enables context-aware memory recall without full history loading

**External Memory Solutions (compaction-proof):**

**Mem0 Plugin:**
- Stores memories outside context window
- Auto-capture and recall
- Survives compaction completely

**Five-Layer Protection (openclaw-memory):**
1. Observer agent compresses transcripts every 15 minutes
2. Reflector consolidates observations
3. Reactive watcher on file changes
4. Pre-compaction hook (flushes before context truncation)
5. Session recovery from durable store

**Cognee Knowledge Graph:**
- Adds relationship tracking (vector search finds similar text but can't reason about relationships)
- Entity-relationship modeling for complex investigations

**JSONL Fact Store:**
- Append-only extracted facts
- Cron-driven LLM extraction
- Queryable structured data

## 5. Session & Compaction

**Session Model:**
- JSON file: `~/.openclaw/sessions.json`
- Maps session keys to session entries
- Session key: `agent + channel + scope + peer`

**Compaction (Context Window Management):**
When sessions exceed context window, OpenClaw compacts (summarizes/truncates) older messages.

**What Compaction Destroys:**
- File paths and exact commands
- Detailed reasoning chains
- Specific numbers, dates, identifiers
- Tool call parameters and results

**Protection Strategy:**
1. Memory flush triggers BEFORE compaction to write durable notes
2. But this is best-effort, not guaranteed
3. Use external memory (Mem0, five-layer) for critical persistence
4. State files (`state/active-work.json`) for in-progress work

**Compaction Failure Risk:**
- GitHub issue #14543: Compaction lacks fallback support
- Only LLM operation with zero fault tolerance
- If compaction model fails, session may become unusable

## 6. Multi-Model Failover

**Hierarchical Configuration:**
```json
{
  "models": {
    "primary": "claude-opus-4-6",
    "fallbacks": ["claude-sonnet-4-5", "gemini-2.5-flash"]
  }
}
```

**Error Classification → Failover:**
- 401/429/503: trigger failover to next model
- 400 format errors: also trigger failover
- Exponential backoff cooldowns between retries

**Known Edge Cases (from GitHub issues):**
- #17478: Rate-limited primary doesn't auto-recover after window expires
- #19249: File-based cooldowns ignored by existing sessions
- #9549: Silent model switches with no `model_change` event
- #17465: Single attempt per model before fallback (doesn't wait on short retry windows)

**Recommended Multi-Model Stack:**
```
Main agent reasoning:    Opus 4.6 (best reasoning + prompt injection resistance)
Sub-agents:              Sonnet 4.5 / Gemini 2.5 Flash (cost-effective parallel work)
Heartbeat/monitoring:    Haiku 4.5 / rule-based scripts (minimize per-beat cost)
Compaction/summarization: Sonnet 4.5 (good summarization, lower cost)
Memory extraction:       Gemini 2.5 Flash (~$0.001/run)
```

## 7. Sub-Agent System

**Spawning:** `sessions_spawn` creates isolated child agents with restricted tools.

**Constraints:**
- `maxSpawnDepth`: default 1, max 2 (for orchestrator pattern)
- `maxChildrenPerAgent`: default 5
- `maxConcurrent` global: default 8
- Children cannot spawn children (unless depth 2 enabled)
- Children start with fresh context
- Results announced back to parent

**Sub-Agent Use Cases:**
- Parallel source gathering for research
- Isolated tool execution (sandboxed sub-tasks)
- Specialized model routing (cheaper model for simple tasks)
- Concurrent investigation threads

## 8. Tool Execution & Sandboxing

**Policy Precedence Chain:**
```
Tool Profile → Provider Profile → Global Policy →
Provider Policy → Agent Policy → Group Policy → Sandbox Policy
```

**Two Sandboxing Approaches:**
1. Full Gateway in Docker (heavy, complete isolation)
2. Tool sandboxing (recommended): Gateway on host, tools in Docker containers

**Security Invariants (production):**
1. Sandbox-first: All shell ops default to hardened sandbox
2. Least privilege: Allowlist mode, unlisted binaries trigger `ask:always`
3. Write scoping: Operations constrained to `$WORKSPACE_ROOT`
4. HITL for side-effects: Manual approval for state changes/network calls
5. Path traversal prevention: Strict workspace root prevents .ssh/.env access

**Prompt injection remains an unsolved problem across all agent frameworks.**

## 9. Lobster Workflow Engine

Deterministic YAML-defined pipelines bridging probabilistic (LLM) and deterministic (typed) orchestration.

**Core Concepts:**
- Explicit step sequencing
- JSON data piping between steps
- Approval checkpoints (hard stops)
- Resume tokens for continuation
- The `approve` primitive: workflow CANNOT continue until explicitly resumed

**Example Pipeline:**
```yaml
name: research-pipeline
steps:
  - id: gather-sources
    prompt: "Search for sources on {{topic}} using k-deep-research methodology"
  - id: review-sources
    approve: "Review gathered sources before analysis"
  - id: analyze
    prompt: "Analyze sources from previous step, apply credibility scoring"
  - id: compile-report
    prompt: "Compile final report with YAML frontmatter"
```

**Use Cases:**
- Multi-step research with human review gates
- Automated report generation with quality checkpoints
- Deployment workflows with approval requirements
- Any workflow needing deterministic sequencing + LLM reasoning

## 10. Observability & Monitoring

**Built-in:**
- JSONL transcripts per session
- Model snapshots (which model, which turn)
- Tool traces (what was called, parameters, results)
- Error classification logs
- Cost tracking per session/model

**ClawMetry (open-source dashboard):**
- Real-time token cost per session/model/tool
- Sub-agent monitoring
- Live flow visualization

**Knostic openclaw-detect:**
- Tool call logging with tamper-proof hash chains
- Syslog/SIEM forwarding
- Audit trail for compliance

**Autonomy Degradation Signals:**
1. Heartbeat silence ratio (all HEARTBEAT_OK = possible lost context)
2. Sub-agent completion rate decline
3. Token cost spikes (runaway loops)
4. Model fallback frequency increase
5. Memory file unbounded growth
6. Compaction frequency increase
7. Error classification drift (more 4xx, fewer 2xx)

---

## Key GitHub Issues for Tracking

| Issue | Description | Impact |
|-------|-------------|--------|
| #10036 | Agent Teams RFC: direct inter-agent communication | Eliminates parent relay bottleneck |
| #10467 | Multi-lane concurrency: per-lane maxConcurrent | Parallel processing with isolation |
| #17465 | Configurable model retry | Prevents unnecessary fallback |
| #17478 | Auto-recovery to primary after rate limit | Restores optimal model automatically |
| #14543 | Compaction failover | Brings compaction to parity with chat resilience |

## Source Credibility for OpenClaw Research

```
Tier 1 (9-10): docs.openclaw.ai, github.com/openclaw/openclaw, github.com/openclaw/lobster
Tier 2 (8):    DeepWiki analyses, Milvus Blog, DigitalOcean, Saulius.io, technical deep-dives
Tier 3 (7):    AnswerOverflow Discord, GitHub Issues, community experience reports
Tier 4 (8):    CrowdStrike, Semgrep, Auth0, AccuKnox security analyses
Tier 5 (6-7):  Industry trend articles, AWS agent evaluation, ArXiv survey
```
