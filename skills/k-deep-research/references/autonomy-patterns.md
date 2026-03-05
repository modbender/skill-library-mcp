# Autonomy Patterns Reference

Comprehensive patterns for designing, deploying, and monitoring autonomous agent behavior.
Load when researching proactive agents, workflow orchestration, or autonomous system design.

## Table of Contents
1. Autonomy Spectrum
2. Heartbeat Patterns
3. Cron Patterns
4. Memory Persistence Strategies
5. Compaction Survival
6. Task Registry Patterns
7. Workflow Orchestration (Lobster)
8. Multi-Agent Coordination
9. Degradation Monitoring
10. Production Autonomy Checklist

---

## 1. Autonomy Spectrum

Agents exist on a spectrum from fully reactive to fully autonomous:

```
REACTIVE          SEMI-AUTONOMOUS        AUTONOMOUS
─────────────────────────────────────────────────────
Responds only     Heartbeat monitoring    Initiates actions
when messaged     Cron-scheduled tasks    Self-directed goals
No persistence    Basic memory            Full state management
No planning       Task queue processing   Strategic planning
Human-driven      Human-gated            Human-supervised
```

**OpenClaw's Current Position:** Semi-autonomous with pathways to full autonomy.
The heartbeat + cron + memory + sub-agent stack provides the primitives.
True autonomy requires: initiative scoring, goal decomposition, resource management, failure recovery.

**What's Missing for Full Autonomy:**
- No built-in initiative scoring (must be custom in HEARTBEAT.md)
- No goal decomposition framework (agent uses general reasoning)
- No resource budget management (token costs uncapped without external monitoring)
- Limited failure recovery (compaction has no failover)

## 2. Heartbeat Patterns

### Pattern A: Native Heartbeat (Simple, Expensive)
```
Agent ←[full context]← Gateway ←[interval timer]← System
```
- Loads entire main-session context every beat
- 170K-210K tokens per beat
- Good for: simple monitoring with few skills loaded
- Bad for: complex agents with large context

### Pattern B: Cron Heartbeat (Isolated, Efficient)
```
Agent ←[minimal context]← Cron Job ←[schedule]← System
         ↓
    openclaw-mem plugin → Smart context retrieval
```
- Fresh session per beat, minimal base cost
- Retrieves relevant context on-demand via memory plugin
- **Recommended for production**

### Pattern C: Tiered Heartbeat
```
Fast beat (5 min):  Check urgent flags only (email/calendar)
Normal beat (30 min): Review tasks, check sources
Slow beat (4 hours):  Deep research sweep, report generation
```
- Different cron jobs at different intervals
- Each with appropriate context loading
- Scales cost to urgency

### Pattern D: Event-Driven Heartbeat
```
Webhook → Gateway → Agent (only when triggered)
         ↓
    Heartbeat only fires on external signal
```
- GitHub webhooks, email notifications, file system watchers
- Zero cost during quiet periods
- Immediate response to relevant events

### HEARTBEAT.md Design Principles
1. Structured as prioritized checklist (not prose)
2. Clear criteria for HEARTBEAT_OK vs action
3. Include "do NOT" instructions (prevent runaway loops)
4. Time-bound actions (max 5 minutes per beat)
5. Escalation paths (when to alert human)

## 3. Cron Patterns

### Research Monitoring Cron
```json
{
  "pattern": "0 */6 * * *",
  "prompt": "Use k-deep-research skill. Check monitored topics in TASKS.md for new developments. If significant findings, write report to research/ and notify via telegram.",
  "session": "cron-research-monitor"
}
```

### Daily Digest Cron
```json
{
  "pattern": "0 7 * * 1-5",
  "prompt": "Generate daily briefing: 1) Overnight email/message summary 2) Today's calendar 3) Priority tasks from TASKS.md 4) Any research alerts",
  "session": "cron-daily-digest"
}
```

### Memory Maintenance Cron
```json
{
  "pattern": "0 2 * * *",
  "prompt": "Review today's memory logs in memory/. Consolidate significant findings into MEMORY.md. Archive or compress old daily logs.",
  "session": "cron-memory-maintenance"
}
```

### Skill Health Check Cron
```json
{
  "pattern": "0 3 * * 0",
  "prompt": "Audit installed skills: check for updates, verify dependencies still present, test critical skill operations, report any failures.",
  "session": "cron-skill-health"
}
```

**Cron Best Practices:**
- Each job gets its own session (isolation)
- Use skill references in prompts ("Use k-deep-research skill")
- Time jobs to avoid overlapping with active use
- Include failure reporting in every cron prompt
- Monitor cron execution logs for silent failures

## 4. Memory Persistence Strategies

### Strategy 1: File-Based (Built-in)
```
Short-term: memory/YYYY-MM-DD.md (daily logs)
Long-term:  MEMORY.md (curated knowledge)
State:      state/active-work.json (current context)
Tasks:      TASKS.md (task registry)
```
**Pros:** Simple, auditable, human-readable
**Cons:** No semantic search, no relationship tracking, compaction-vulnerable

### Strategy 2: Plugin-Enhanced (Mem0)
```
All memories → Mem0 store (outside context window)
Auto-capture on significant events
Auto-recall on relevant queries
```
**Pros:** Compaction-proof, semantic recall, low overhead
**Cons:** Additional dependency, opaque storage

### Strategy 3: Five-Layer Defense
```
Layer 1: Observer (compresses transcripts every 15 min)
Layer 2: Reflector (consolidates observations)
Layer 3: Reactive watcher (file change triggers)
Layer 4: Pre-compaction hook (emergency flush)
Layer 5: Session recovery (rebuild from durable store)
```
**Pros:** Maximum resilience, no single point of failure
**Cons:** Complex setup, higher overhead

### Strategy 4: Knowledge Graph (Cognee)
```
Entities → Relationships → Graph queries
"Who is connected to what, and how?"
```
**Pros:** Relationship reasoning, complex queries
**Cons:** Highest setup complexity, requires graph database

### Strategy 5: Hybrid (Recommended for Research Agents)
```
MEMORY.md:          Curated long-term knowledge
Mem0:               Semantic recall for conversational context
state/:             Active work state (JSON)
TASKS.md:           Task registry
research/:          Completed investigation outputs
memory/:            Daily logs (archived weekly)
```

## 5. Compaction Survival

**The Core Problem:** When context exceeds window, OpenClaw summarizes older messages. This destroys specifics.

**What Survives Compaction:**
- MEMORY.md (read fresh each turn)
- State files (read fresh)
- TASKS.md (read fresh)
- External memory stores (Mem0, etc.)
- Skill files (loaded per session)

**What Dies in Compaction:**
- Detailed conversation history
- Exact file paths discussed
- Specific reasoning chains
- Tool call parameters and results
- Nuanced context from early conversation

**Pre-Compaction Flush Pattern:**
```
Before context limit approached:
1. Write critical state to state/active-work.json
2. Update MEMORY.md with session learnings
3. Ensure TASKS.md reflects current status
4. Flush any in-progress research notes to research/
```

**Recovery After Compaction:**
```
1. Read MEMORY.md for established context
2. Read state/active-work.json for interrupted work
3. Read TASKS.md for pending items
4. Use Mem0/memory plugin for recent context
5. Resume work with reconstructed state
```

## 6. Task Registry Patterns

### Basic TASKS.md
```markdown
# Research Task Registry

## Active
- [ ] Monitor 3I/ATLAS developments (weekly sweep)
- [ ] Track OpenClaw v2.x release notes
- [x] Complete consciousness tech landscape analysis

## Pending
- [ ] Deep dive on Lobster workflow patterns
- [ ] Evaluate Mem0 vs five-layer memory

## Blocked
- [ ] FOIA response tracking (waiting on response, check monthly)

## Completed (Archive Monthly)
- [x] OpenClaw autonomous architecture analysis (2026-02-23)
```

### Structured TASKS.md (for autonomous agents)
```markdown
# Tasks

## task-001
- status: active
- priority: high
- topic: 3I/ATLAS monitoring
- schedule: weekly
- last_run: 2026-02-20
- next_run: 2026-02-27
- skill: k-deep-research
- output: research/3i-atlas/

## task-002
- status: pending
- priority: medium
- topic: Lobster workflow deep dive
- depends_on: task-001
- skill: k-deep-research
- output: research/lobster-patterns/
```

**Task Registry Limitations:**
- No built-in enforcement — entirely LLM discipline
- No priority scoring system — must be instructed
- No dependency resolution — agent must reason about order
- Can drift if not maintained — schedule regular audits

## 7. Workflow Orchestration (Lobster)

### Research Pipeline Pattern
```yaml
name: deep-research-pipeline
description: "Multi-phase research with human review gates"
steps:
  - id: scope
    prompt: |
      Define research scope for: {{topic}}
      Output: search strategy, source categories, expected depth
    output: scope.json

  - id: gather
    prompt: |
      Execute search strategy from {{scope.json}}
      Use k-deep-research sourcing-strategies
      Gather 40+ sources minimum
    output: sources.json

  - id: review-sources
    approve: "Review gathered sources. Approve to proceed with analysis."

  - id: analyze
    prompt: |
      Apply credibility scoring to all sources
      Cross-reference for patterns
      Identify contradictions and gaps
    output: analysis.json

  - id: synthesize
    prompt: |
      Compile final report with YAML frontmatter
      Follow k-deep-research output format
      Exhaust the topic — length is a feature
    output: report.md

  - id: review-report
    approve: "Review final report. Approve to publish."

  - id: publish
    prompt: |
      Save report to research/{{topic}}/
      Update TASKS.md status
      Notify via configured channel
```

### Monitoring Pipeline Pattern
```yaml
name: research-monitor
description: "Recurring topic monitoring sweep"
steps:
  - id: check-topics
    prompt: "Read TASKS.md, identify topics due for monitoring sweep"
    output: due-topics.json

  - id: sweep
    prompt: |
      For each topic in {{due-topics.json}}:
      - Search for new developments since last_run
      - Score new sources
      - Compare against established findings
    output: sweep-results.json

  - id: evaluate
    prompt: |
      If significant new findings:
      - Generate update report
      - Flag for deep investigation if warranted
      If no significant changes:
      - Update last_run in TASKS.md
      - Log "no significant developments"
    output: evaluation.json
```

### Key Lobster Concepts
- **`approve`** is a HARD STOP — pipeline cannot continue without explicit resume
- **JSON piping** between steps enables structured data flow
- **Resume tokens** allow continuation after approval
- Bridges **probabilistic** (LLM reasoning) and **deterministic** (typed pipeline) execution
- Each step can target different models (cheap for simple, expensive for reasoning)

## 8. Multi-Agent Coordination

### Orchestrator Pattern
```
Primary Agent (Opus 4.6) — Reasoning, planning, synthesis
  ├── Research Sub-Agent 1 (Sonnet 4.5) — Source gathering thread A
  ├── Research Sub-Agent 2 (Sonnet 4.5) — Source gathering thread B
  ├── Analysis Sub-Agent (Flash) — Data processing, extraction
  └── Report Sub-Agent (Sonnet 4.5) — Formatting, output generation
```

### Constraints
- Max spawn depth: 1 (default), 2 (orchestrator mode)
- Max children per agent: 5 (default)
- Max concurrent: 8 (global default)
- Children start with fresh context
- Children cannot spawn children (depth 1)

### Lane-Aware Queue
Each session type gets its own queue lane:
```
main:       Primary agent conversation
subagent:   Spawned child agents
cron:       Scheduled tasks
heartbeat:  Monitoring beats
webhook:    External triggers
```
- Per-session serial execution (prevents race conditions)
- Cross-session concurrency (different lanes run in parallel)
- No priority scoring within lanes — arrival order only

### Future: Agent Teams (RFC #10036)
- Direct inter-agent communication without parent relay
- Would eliminate single-parent bottleneck
- Enable peer-to-peer research collaboration
- Status: RFC stage, not yet implemented

## 9. Degradation Monitoring

### Signal Matrix

| Signal | Meaning | Action |
|--------|---------|--------|
| Heartbeat all HEARTBEAT_OK | Lost context or nothing to do | Verify checklist relevance |
| Sub-agent completion decline | Model degradation or task complexity | Check error logs, simplify tasks |
| Token cost spike | Runaway loop or bloated context | Kill loop, check for infinite cycles |
| Model fallback frequency up | Primary rate-limited or failing | Check rate limits, adjust timing |
| Memory file growth | Unmanaged accumulation | Run memory maintenance cron |
| Compaction frequency up | Context bloat | Reduce loaded context per turn |
| Error classification drift | Infrastructure issues | Check providers, network, deps |

### Automated Monitoring Pattern
```markdown
# HEARTBEAT.md — Health Check Section

## System Health (check every beat)
- Token cost this session: if > 500K, flag as potential runaway
- Last successful cron: if > 24h ago, alert
- Memory file size: if MEMORY.md > 50KB, schedule maintenance
- Model in use: if not primary, note fallback reason
- Sub-agent queue: if > 3 pending, consider sequencing
```

### Recovery Procedures
1. **Runaway Loop:** Kill session, review last prompt/tool chain
2. **Context Bloat:** Start fresh session, load only essential state
3. **Model Fallback Stuck:** Check rate limit recovery, manually trigger primary
4. **Memory Corruption:** Restore from daily backup, reconcile
5. **Cron Silence:** Check gateway status, verify cron config, restart if needed

## 10. Production Autonomy Checklist

### Before Deploying Autonomous Agent
- [ ] Replace native heartbeat with cron heartbeat (token efficiency)
- [ ] Implement memory persistence (at minimum: file-based + state files)
- [ ] Configure multi-model stack (Opus reasoning, cheaper for sub-tasks)
- [ ] Set up Lobster pipelines for repeatable workflows
- [ ] Define TASKS.md with clear task registry
- [ ] Write HEARTBEAT.md with prioritized checklist
- [ ] Deploy monitoring (ClawMetry or equivalent)
- [ ] Configure sandbox with strict workspace isolation
- [ ] Test compaction recovery (intentionally trigger, verify state survives)
- [ ] Set up daily memory maintenance cron
- [ ] Define escalation paths (when to alert human)
- [ ] Document all cron jobs with expected behavior

### Ongoing Maintenance
- [ ] Weekly: Review token costs, check for anomalies
- [ ] Weekly: Audit task completion rates
- [ ] Monthly: Archive old memory logs, consolidate MEMORY.md
- [ ] Monthly: Update skills, check for security advisories
- [ ] Quarterly: Review HEARTBEAT.md relevance
- [ ] Quarterly: Evaluate model stack (new models available?)

---

## Key Insight

True autonomy is not "set and forget." It's a continuous loop of:
```
Design → Deploy → Monitor → Adjust → Repeat
```

The agent that runs perfectly for 30 days will eventually degrade.
Build monitoring into the architecture from day one, not as an afterthought.
