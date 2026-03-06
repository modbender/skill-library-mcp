# Pipeline Framework — All-Agent Guide

> Every agent needs to understand this. Whether you're an Orchestrator, sub-agent, or department lead.
>
> Detailed design: `PROJECTS/pipeline-framework/DESIGN.md`

---

## What is Pipeline?

Pipeline is a project phase state machine. It breaks "from inception to delivery" into 8 phases, each with explicit entry conditions, artifacts, and exit conditions.

```
Constitute → Research → Specify → Plan+Tasks → Implement → Test → Review → Gap Analysis
```

- Phases pass context via files (not chat history)
- Each phase runs in an isolated session (clean context)
- Review failure can roll back to any earlier phase
- Each completed run archives to `pipeline_archive/run-{N}/`

---

## Who Needs Pipeline?

- **Must use**: Projects with clear goals and deliverables
- **Don't need**: Maintenance crons, patrol/healthcheck jobs, periodic reports

---

## Roles

### Orchestrator (scheduler)
- Triggered by cron on a timer
- Reads PIPELINE_STATE.json → determines phase → spawns sub-agent → checks output → advances phase
- **Does no actual work** — only scheduling and checking

### Sub-Agent (executor)
- Spawned by Orchestrator via `sessions_spawn`
- Runs in an isolated session
- Receives only the minimum file set needed for that phase
- Writes artifacts to `pipeline/` directory
- Session ends automatically on completion

### Consultant (Technical Advisor)
- When a sub-agent gets stuck and the model escalation chain is exhausted, Orchestrator spawns multiple consultants in parallel
- Each consultant uses a different model, analyzing the problem from a different perspective and providing an independent solution
- Does not directly modify project files — only provides suggestions

### Synthesizer (Solution Synthesizer)
- After all consultants return, synthesizes the optimal executable solution
- Synthesized solution is injected into the original phase prompt, retried with the strongest model

### Triage (Auto-Triage Judge)
- Triggered when all automated assistance (escalation chain + consult + synthesized retry) fails
- Makes one of three decisions: RELAX (loosen constraints and continue), DEFER (suspend to next iteration), BLOCK (wait for human)
- Prevents pipeline from stalling overnight when no human is available

---

## If You're Spawned as a Sub-Agent

When you receive a Pipeline phase task:

1. **Read the specified input files** (listed in the task) — don't read unrelated files
2. **Produce the required artifact** — write to the specified `pipeline/` path
3. **Meet the exit conditions** (stated in the task)
4. **Don't modify PIPELINE_STATE.json** (that's the Orchestrator's job)
5. **Don't modify system config / gateway**
6. **Output a brief summary** (3-5 lines) of what you did and what files you produced

---

## Directory Structure

```
ORG/PROJECTS/<project>/
├── STATUS.md              # Human-readable project status
├── DECISIONS.md           # Key decisions with rationale
├── RUNBOOK.md             # How to run / reproduce
├── PIPELINE_STATE.json    # Phase state machine (Orchestrator reads/writes)
├── PIPELINE_LOG.jsonl     # Full history log (append-only)
├── pipeline/              # Current run artifacts
│   ├── CONSTITUTION.md    # Phase 0: Principles & constraints
│   ├── RESEARCH.md        # Phase 1: Research report
│   ├── SPECIFICATION.md   # Phase 2: Requirements & acceptance criteria
│   ├── PLAN.md            # Phase 3: Implementation plan
│   ├── TASKS.md           # Phase 3: Atomic task list
│   ├── IMPL_STATUS.md     # Phase 4: Implementation progress
│   ├── TEST_REPORT.md     # Phase 5: Test report
│   ├── REVIEW_REPORT.md   # Phase 6: Review report
│   └── GAP_ANALYSIS.md    # Phase 7: Gap analysis
└── pipeline_archive/      # Historical run archives
    ├── run-001/
    ├── run-002/
    └── ...
```

---

## 8 Phases at a Glance

| # | Phase | Default Role | Artifact | Exit Condition |
|---|-------|-------------|----------|----------------|
| 0 | Constitute | architect | CONSTITUTION.md | Contains goals, tech stack, quality bar, boundaries |
| 1 | Research | researcher | RESEARCH.md | At least 5 sourced findings |
| 2 | Specify | designer | SPECIFICATION.md | Every requirement has acceptance criteria |
| 3 | Plan+Tasks | architect | PLAN.md + TASKS.md | Every task has a test plan |
| 4 | Implement | developer | Code + IMPL_STATUS.md | All tasks done or deferred (via Auto-Triage) |
| 5 | Test | developer | TEST_REPORT.md | Acceptance pass rate ≥ threshold |
| 6 | Review | reviewer | REVIEW_REPORT.md | PASS or FAIL + rollback target |
| 7 | Gap Analysis | researcher | GAP_ANALYSIS.md | Quantified completion + improvement suggestions |

---

## Relationship with ORG Charter

Pipeline extends the ORG charter, it doesn't replace it. All ORG rules still apply:

- Boot Sequence still required (read TASKBOARD → HANDOFF → ASSET_REGISTRY)
- Closeout still required (update HANDOFF / STATUS)
- Persistence rules still apply (Pipeline naturally satisfies this — all outputs are files)
- Change control still applies (Pipeline doesn't touch system config)

---

## FAQ

**Q: I'm a maintenance cron. Do I need Pipeline?**
A: No. Pipeline is for projects with clear goals and deliverables.

**Q: Can phases be skipped?**
A: Yes. Set `"status": "skipped"` in PIPELINE_STATE.json for phases you don't need.

**Q: What if I find a problem with the previous phase's output?**
A: Note it in your artifact. The Orchestrator or Review phase will handle rollback. Don't modify previous phase files yourself.

**Q: How often does the Pipeline trigger?**
A: Depends on the Orchestrator's cron config. Default is every 30 minutes. Adjustable per project.

**Q: What if the Pipeline gets stuck overnight with no one watching?**
A: Pipeline has a 3-layer automated assistance mechanism: ① Model Escalation (retry with stronger models) → ② Peer Consult (parallel multi-model consultation) → ③ Auto-Triage (automated triage). The third layer has a strong model judge whether to: loosen constraints and continue (RELAX), suspend the task and move on (DEFER), or truly wait for a human (BLOCK). Only BLOCK actually stalls the pipeline. RELAX and DEFER are temporary measures — the next iteration re-evaluates them.

**Q: Won't Auto-Triage loosen constraints too much?**
A: Multiple guardrails are in place: ① confidence < 0.6 forces BLOCK ② Safety red lines in CONSTITUTION cannot be RELAXed ③ Per-run RELAX limit defaults to 3 ④ Review phase audits all RELAX/DEFER records and can judge FAIL accordingly.
