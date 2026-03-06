# Pipeline Orchestrator Framework Design Document

> Author: Architect | Status: APPROVED

---

## 0. Background & Motivation

### Current Issues
1. **Flat Cron Driver**: Each cron job = one agent + one isolated session. Cramming research/design/coding/testing/review into a single prompt leads to uncontrollable quality.
2. **No Phase Gates**: There is no mechanism to prevent proceeding to the next step if the previous one isn't done well. Agents decide for themselves how much to do.
3. **No Multi-Role Collaboration**: Chat bots cannot trigger each other (bot-to-bot messages blocked), so multi-role collaboration cannot happen at the messaging layer.
4. **Context Pollution**: The longer the conversation in a single session, the "dirtier" the context gets, degrading later output quality.

### Design Goals
- Introduce a Phase State Machine (Pipeline) where each phase has explicit entry conditions, artifacts, and exit conditions.
- Execute each phase in a clean isolated session, passing context via files (not chat).
- Multi-role collaboration happens inside OpenClaw (sessions_spawn), while messaging platforms serve only as result announcement panels.
- Fully compatible with existing ORG Charter (Boot/Closeout/Persistence/Change Control).
- Reusable: Any project can apply the same Pipeline framework.

---

## 1. Core Concepts

### 1.1 Pipeline = Phase State Machine

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Phase 0  │───▶│ Phase 1  │───▶│ Phase 2  │───▶│ Phase 3  │───▶│ Phase 4  │───▶│ Phase 5  │───▶│ Phase 6  │───▶│ Phase 7  │
│Constitute│    │ Research │    │ Specify  │    │Plan+Tasks│    │Implement │    │  Test    │    │ Review   │    │Gap Analys│
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
      │                                                               │                              │                │
      │                                                               │         ┌───────────┐        │                │
      │                                                               │◀────────│  Rollback  │◀───────│                │
      │                                                               │         └───────────┘        │                │
      ▼                                                                                              ▼                ▼
  CONSTITUTION.md                                                                              REVIEW_REPORT.md  GAP_ANALYSIS.md
                                                                                               → pass: Enter Phase 7
                                                                                               → fail: Rollback to specific phase
```

### 1.2 Orchestrator = Scheduling Agent

The Orchestrator is not a built-in OpenClaw tool, but an agent role triggered periodically by cron. Its responsibilities:

1. Read `PIPELINE_STATE.json` → Determine current phase.
2. Check if entry conditions for the current phase are met.
3. Use `sessions_spawn` to launch a sub-agent of the corresponding role to execute the current phase.
4. After the sub-agent finishes, check if the artifact meets exit conditions.
5. Met → Advance to next phase; Not met → Mark as blocker, wait for next trigger to retry.
6. Write phase transition events to `PIPELINE_LOG.jsonl`.
7. Broadcast progress summary to notification channel.

### 1.3 Role Assignment

| Phase | Recommended Role (agentId) | Recommended Model | Responsibilities |
|---|---|---|---|
| Phase 0: Constitute | <your-architect-agent> | opus | Define project principles, constraints, technical boundaries |
| Phase 1: Research | <your-researcher-agent> | gpro | Survey existing solutions, papers, open source implementations / or further research/background analysis |
| Phase 2: Specify | <your-designer-agent> | opus | Requirements specification, interface definition, acceptance criteria |
| Phase 3: Plan+Tasks | <your-architect-agent> | opus | Implementation plan, task breakdown, test plan design |
| Phase 4: Implement | <your-coder-agent> | codex/glm/sonnet | Task-by-task coding (one clean session per task) |
| Phase 5: Test | <your-coder-agent> | codex | Execute tests, generate test reports |
| Phase 6: Review | <your-reviewer-agent> | opus | Quality review, goal achievement analysis, pass/rollback decision |
| Phase 7: Gap Analysis | <your-researcher-agent> | gpro | Gap analysis, cross-run tracking, improvement suggestions for next run |

> Note: Roles and models can be adjusted per project needs. The above are default recommendations.

#### Auxiliary Roles (Not phase-bound, spawned on demand)

| Role | Trigger Condition | Recommended Model | Responsibilities |
|------|-------------------|-------------------|------------------|
| Consultant (Technical Advisor) | Peer Consult phase | gpro / glm / deepseek-v3 | Analyze stuck problems from different perspectives, provide independent solutions |
| Synthesizer (Solution Synthesizer) | After all Consultants return | opus | Compare consultant solutions, synthesize optimal executable plan |
| Triage (Auto-Triage Judge) | After all 3 layers of assistance fail | opus | Decide RELAX / DEFER / BLOCK |

---

## 2. File Structure

### 2.1 Project-Level Pipeline Directory

For every project using Pipeline, add the following under `ORG/PROJECTS/<project>/`:

```
ORG/PROJECTS/<project>/
├── STATUS.md              # Existing — Human-readable project status
├── DECISIONS.md           # Existing — Key decisions record
├── RUNBOOK.md             # Existing — Operation manual
├── PIPELINE_STATE.json    # New — Phase state machine (machine read/write)
├── PIPELINE_LOG.jsonl     # New — Full history phase transition log (append-only, cross-run)
├── pipeline/              # New — Current run artifacts (fixed path, Orchestrator reads/writes directly)
│   ├── CONSTITUTION.md    # Phase 0 Artifact
│   ├── RESEARCH.md        # Phase 1 Artifact
│   ├── SPECIFICATION.md   # Phase 2 Artifact
│   ├── PLAN.md            # Phase 3 Artifact
│   ├── TASKS.md           # Phase 3 Artifact
│   ├── IMPL_STATUS.md     # Phase 4 Progress tracking
│   ├── TEST_REPORT.md     # Phase 5 Artifact
│   └── REVIEW_REPORT.md   # Phase 6 Artifact
└── pipeline_archive/      # New — Historical run archives (auto-archived after each Review PASS)
    ├── run-001/           # Snapshot of 1st full run artifacts
    │   ├── CONSTITUTION.md
    │   ├── RESEARCH.md
    │   ├── SPECIFICATION.md
    │   ├── PLAN.md
    │   ├── TASKS.md
    │   ├── IMPL_STATUS.md
    │   ├── TEST_REPORT.md
    │   └── REVIEW_REPORT.md
    ├── run-002/
    └── ...
```

**Archival Mechanism**:
- `pipeline/` always represents "the current ongoing run". The path is fixed, so Orchestrator and sub-agents don't need to care about run numbers.
- After each Review PASS, Orchestrator automatically executes archival:
  1. Copy `pipeline/*` → `pipeline_archive/run-{N}/`
  2. Increment `runNumber` in PIPELINE_STATE.json, reset all phases to pending.
  3. Append `{"event": "run_archived", "run": N}` to PIPELINE_LOG.jsonl.
- PIPELINE_LOG.jsonl remains globally append-only and is not split by run, facilitating cross-run trend analysis.

### 2.2 PIPELINE_STATE.json Schema

```json
{
  "project": "example-project",
  "version": 1,
  "runNumber": 1,
  "currentPhase": "research",
  "phases": {
    "constitute": {
      "status": "done",
      "artifact": "pipeline/CONSTITUTION.md",
      "completedAt": "2026-02-13T10:00:00+08:00",
      "completedBy": "<your-architect-agent>"
    },
    "research": {
      "status": "in_progress",
      "artifact": "pipeline/RESEARCH.md",
      "startedAt": "2026-02-13T11:00:00+08:00",
      "assignedTo": "<your-researcher-agent>",
      "retryCount": 0
    },
    "specify": {
      "status": "pending",
      "artifact": "pipeline/SPECIFICATION.md"
    },
    "plan": {
      "status": "pending",
      "artifact": "pipeline/PLAN.md"
    },
    "implement": {
      "status": "pending",
      "artifact": "pipeline/IMPL_STATUS.md",
      "subtasks": []
    },
    "test": {
      "status": "pending",
      "artifact": "pipeline/TEST_REPORT.md"
    },
    "review": {
      "status": "pending",
      "artifact": "pipeline/REVIEW_REPORT.md"
    },
    "gap_analysis": {
      "status": "pending",
      "artifact": "pipeline/GAP_ANALYSIS.md"
    }
  },
  "blockers": [],
  "lastOrchestratorRun": "2026-02-13T11:00:00+08:00",
  "config": {
    "maxRetries": 3,
    "autoAdvance": true,
    "notifyTopic": "<your-notification-channel>",
    "roles": {
      "constitute": { "agentId": "<your-architect-agent>", "model": "opus" },
      "research":   { "agentId": "<your-researcher-agent>", "model": "gpro" },
      "specify":    { "agentId": "<your-designer-agent>",  "model": "opus" },
      "plan":       { "agentId": "<your-architect-agent>", "model": "opus" },
      "implement":  { "agentId": "<your-coder-agent>",     "model": "sonnet/codex/glm" },
      "test":       { "agentId": "<your-coder-agent>",     "model": "codex" },
      "review":     { "agentId": "<your-reviewer-agent>",  "model": "opus" },
      "gap_analysis":{ "agentId": "<your-researcher-agent>", "model": "gpro" }
    }
  }
}
```

### 2.3 PIPELINE_LOG.jsonl Format

One event per line, append-only:

```jsonl
{"ts":"2026-02-13T10:00:00+08:00\",\"event\":\"phase_complete\",\"phase\":\"constitute\",\"agent\":\"<your-architect-agent>\",\"duration_s\":120,\"artifact\":\"pipeline/CONSTITUTION.md\"}
{"ts":"2026-02-13T11:00:00+08:00\",\"event\":\"phase_start\",\"phase\":\"research\",\"agent\":\"<your-researcher-agent>\"}
{"ts":"2026-02-13T11:15:00+08:00\",\"event\":\"phase_complete\",\"phase\":\"research\",\"agent\":\"<your-researcher-agent>\",\"duration_s\":900,\"artifact\":\"pipeline/RESEARCH.md\"}
{"ts":"2026-02-13T12:00:00+08:00\",\"event\":\"review_reject\",\"phase\":\"review\",\"agent\":\"<your-reviewer-agent>\",\"reason\":\"Insufficient test coverage\",\"rollbackTo\":\"implement\"}
```

---

## 3. Phase Details

### Phase 0: Constitute

**Goal**: Define project principles, technical constraints, and quality standards. Similar to SpecKit's CONSTITUTION.

**Entry Condition**: Project directory exists under `ORG/PROJECTS/`.

**Artifact**: `pipeline/CONSTITUTION.md`, containing:
- Project Goal (1-3 sentences)
- Tech Stack Constraints (languages, frameworks, dependency limits)
- Quality Standards (test coverage requirements, performance metrics, documentation requirements)
- Boundary Constraints (what not to do, security red lines)
- Alignment Statement with ORG Charter

**Exit Condition**: CONSTITUTION.md exists and is not empty, containing all sections above.

---

### Phase 1: Research

**Goal**: Survey existing solutions, papers, open source implementations to build a knowledge base.

**Entry Condition**: Phase 0 Complete.

**Artifact**: `pipeline/RESEARCH.md`, containing:
- Research scope and methods
- Key Findings (at least 5, each with source links)
- Comparison table of existing solutions
- Technical risk identification
- Recommended direction (with reasoning)

**Exit Condition**: RESEARCH.md exists, containing at least 5 sourced findings.

---

### Phase 2: Specify

**Goal**: Define precise requirements and acceptance criteria based on research. Borrowed from SpecKit's SPECIFICATION.

**Entry Condition**: Phase 1 Complete.

**Input**: CONSTITUTION.md + RESEARCH.md

**Artifact**: `pipeline/SPECIFICATION.md`, containing:
- Functional Requirements list (each testable)
- Non-functional Requirements (performance, reliability, maintainability)
- Interface Definitions (input/output formats)
- Acceptance Criteria (acceptance condition for each requirement)
- Exclusions (explicitly what not to do)

**Exit Condition**: SPECIFICATION.md exists, every functional requirement has corresponding acceptance criteria.

---

### Phase 3: Plan + Tasks

**Goal**: Create implementation plan, break down into executable atomic tasks. Borrowed from SpecKit's PLAN + TASKS.

**Entry Condition**: Phase 2 Complete.

**Input**: CONSTITUTION.md + RESEARCH.md + SPECIFICATION.md

**Artifact**:
- `pipeline/PLAN.md`: Implementation roadmap (phased, dependencies)
- `pipeline/TASKS.md`: Atomic task list, each task containing:
  - Task ID (T-001, T-002...)
  - Description
  - Dependencies (which tasks must be done first)
  - Expected output files
  - Test Plan (how to verify this task is done)
  - Estimated Complexity (S/M/L)

**Exit Condition**: PLAN.md + TASKS.md exist, every task has a test plan.

---

### Phase 4: Implement

**Goal**: Code task by task. Each task executes in an independent clean session.

**Entry Condition**: Phase 3 Complete.

**Input**: Each sub-task is injected with only CONSTITUTION.md + SPECIFICATION.md + description of that task in TASKS.md + relevant code files.

**Execution Method**:
- Orchestrator picks the next incomplete task from TASKS.md in dependency order.
- `sessions_spawn` a sub-agent, giving it only the minimum context needed for that task.
- Sub-agent updates `pipeline/IMPL_STATUS.md` upon completion.
- Orchestrator triggers processing of 1-3 tasks at a time (to avoid timeout).

**Artifact**:
- Code files (in project repo)
- `pipeline/IMPL_STATUS.md`: Task completion status tracking

**Exit Condition**: All tasks in TASKS.md marked as done.

---

### Phase 5: Test

**Goal**: Execute tiered testing, generate test report.

**Entry Condition**: Phase 4 Complete (all tasks done).

**Testing Tiers**:
1. **Unit Test**: Independent test for each task.
2. **Integration Test**: Cross-task interface tests.
3. **Acceptance Test**: Verify against SPECIFICATION.md acceptance criteria item by item.

**Artifact**: `pipeline/TEST_REPORT.md`, containing:
- Test Execution Summary (pass/fail/skip counts)
- Pass status for each acceptance criterion
- Failure case details
- Test Coverage (if applicable)

**Exit Condition**: TEST_REPORT.md exists, acceptance test pass rate >= threshold (default 80%, adjustable in config).

---

### Phase 6: Review

**Goal**: Quality review + goal achievement analysis. This is the critical gate.

**Entry Condition**: Phase 5 Complete.

**Input**: All pipeline artifacts.

**Review Dimensions**:
1. **Spec Compliance**: Does code meet all requirements in SPECIFICATION.md?
2. **Quality Standards**: Does it meet quality standards defined in CONSTITUTION.md?
3. **Test Sufficiency**: Does TEST_REPORT.md cover all critical paths?
4. **Maintainability**: Are code structure, docs, comments sufficient?
5. **Goal Achievement**: Is the project goal achieved overall?

**Artifact**: `pipeline/REVIEW_REPORT.md`, containing:
- Scores for each dimension (1-5)
- Overall Verdict: `PASS` / `FAIL`
- If FAIL: Point out specific issues + suggest which phase to rollback to.
- If PASS: Project completion confirmation.

**Exit Condition**:
- PASS → Pipeline Complete, update `ORG/PROJECTS/<project>/STATUS.md`
- FAIL → Orchestrator rolls back currentPhase to specified phase, attaching review comments as extra input for that phase.

---

### Phase 7: Gap Analysis

**Goal**: Deep analysis of the gap between current run results and final project goals, providing structured improvement directions for the next Pipeline run. Review answers "Is this run good enough?", Gap Analysis answers "How to do better next run?".

**Entry Condition**: Phase 6 Review verdict is PASS.

**Input**: All pipeline artifacts + CONSTITUTION.md (final goal baseline) + Historical run archives (if any).

**Artifact**: `pipeline/GAP_ANALYSIS.md`, containing:
- **Quantified Completion**: Evaluate gap between current results and final goals per module (percentage or score).
- **Scenario Coverage Analysis**: Which scenarios covered, which boundary/extreme scenarios missing.
- **Chart Sufficiency Assessment**: Are existing charts sufficient to support conclusions, suggest new ones.
- **Cross-Run Progress Tracking**: Compare key metrics with previous run (if any), quantify improvement magnitude.
- **Next Run Improvement Suggestions**: List specific executable improvement items by priority (High/Medium/Low), each with reason and expected benefit.
- **Quality Standard Update Suggestions**: Whether to adjust acceptance thresholds or add new quality dimensions.

**Exit Condition**: GAP_ANALYSIS.md exists and is not empty, containing quantified completion and at least 3 prioritized improvement suggestions.

**Role Configuration**:
- Recommended agentId: `<your-researcher-agent>`
- Recommended model: `gpro` (Good at long-text deep analysis and structured output)

**Difference from Review**:
- Review (Phase 6) is a Gate — decides PASS/FAIL, focuses on "Is this run good enough".
- Gap Analysis (Phase 7) is Forward-looking — assumes PASS, focuses on "How to do better next run".
- Review executed by reviewer role (strict gatekeeping), Gap Analysis by professor role (deep analysis).

---

## 4. Orchestrator Logic (Pseudo-code)

```
Every cron trigger:

1. Read PIPELINE_STATE.json
2. current = state.currentPhase

3. if current.status == "pending":
     # Start this phase
     Check entry conditions (whether previous phase artifact exists and is valid)
     if entry condition not met:
       Record blocker, broadcast, exit
     role = state.config.roles[current]
     sessions_spawn(agentId=role.agentId, model=role.model, task=Build Phase Prompt)
     Update status → "in_progress"

4. if current.status == "in_progress":
     # Check artifact
     if artifact exists and meets exit condition:
       Update status → "done"
       Advance currentPhase → Next Phase
       Write PIPELINE_LOG.jsonl
       broadcast progress to notification channel
     elif retryCount >= maxRetries:
       Mark blocker, notify human intervention
     else:
       retryCount++
       Re-spawn this phase

5. if current == "review" && status == "done":
     Read REVIEW_REPORT.md
     if verdict == PASS:
       Advance currentPhase → gap_analysis (pending)
     if verdict == FAIL:
       Rollback currentPhase to specified phase
       Inject review comments into extra input of that phase

5b. if current == "gap_analysis" && status == "done":
     Pipeline Run Complete 🎉
     Archive: Copy pipeline/* → pipeline_archive/run-{runNumber}/
     Deferred persistence: Collect all deferredTasks → pipeline_archive/run-{N}/DEFERRED_TASKS.json
     Relaxed persistence: Collect all triageResult.decision=="RELAX" → pipeline_archive/run-{N}/RELAXED_CONSTRAINTS.json
     Update ORG/PROJECTS/<project>/STATUS.md
     PIPELINE_LOG.jsonl append {"event": "run_archived", "run": runNumber, "deferredCount": N, "relaxedCount": M}
     runNumber++, reset all phases to pending (deferredTasks cleared — already persisted to archive)
     Next run Constitution phase automatically gets GAP_ANALYSIS.md + DEFERRED_TASKS.json as input

6. Save PIPELINE_STATE.json
```

---

## 5. Orchestrator Cron Job Template

```json
{
  "name": "pipeline:<project>:orchestrator",
  "schedule": { "kind": "cron", "expr": "*/30 * * * *", "tz": "Asia/Shanghai" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "You are the Pipeline Orchestrator.\n\nYour ONLY responsibility is to advance the project pipeline. Do not do concrete work yourself.\n\nMandatory Reading:\n- Pipeline State: ORG/PROJECTS/<project>/PIPELINE_STATE.json\n- ORG Boot Sequence: Read TASKBOARD.md → Dept HANDOFF.md → ASSET_REGISTRY.md first\n\nExecution Logic:\n1. Read PIPELINE_STATE.json, determine currentPhase and runNumber\n2. Check entry conditions for current phase (previous artifact exists)\n3. If phase pending → sessions_spawn corresponding role to execute phase\n4. If phase in_progress → check if artifact meets exit conditions\n5. Met → Advance to next phase; Not met → Retry or mark blocker\n6. If Review PASS → Archive current run (copy pipeline/* → pipeline_archive/run-{N}/), runNumber++, reset all phases to pending\n7. If Review FAIL → Rollback to specified phase, inject review comments\n8. Update PIPELINE_STATE.json + Append PIPELINE_LOG.jsonl\n9. broadcast progress summary to notification channel\n\nHard Constraints:\n- Do not write code/research/test yourself, delegate ALL via sessions_spawn\n- Advance at most 1 phase per trigger\n- Do not modify system config/gateway\n- Observe ORG Closeout: Update Dept HANDOFF.md",
    "model": "gflash2",
    "timeoutSeconds": 600
  },
  "delivery": {
    "mode": "announce",
    "channel": "<your-channel>",
    "to": "<your-notification-channel>"
  }
}
```

> Orchestrator itself uses a lightweight model (gflash2/mini) because it only does judgment and scheduling, not heavy lifting.

---

## 6. Multi-Role Collaboration Mechanism

### 6.1 Internal Collaboration (sessions_spawn)

```
Orchestrator
  ├── spawn(<your-researcher-agent>, "Research XX field...")  → RESEARCH.md
  ├── spawn(<your-architect-agent>, "Design XX architecture...")   → PLAN.md
  ├── spawn(<your-coder-agent>, "Implement Task T-003...")     → code
  ├── spawn(<your-reviewer-agent>, "Review pipeline...")   → REVIEW_REPORT.md
  │
  │  ── Assistance Flow (when sub-agent gets stuck) ──
  ├── spawn(consultant, model=gpro,   task=consult)  → Solution A
  ├── spawn(consultant, model=glm,    task=consult)  → Solution B
  ├── spawn(consultant, model=sonnet, task=consult)  → Solution C
  ├── spawn(synthesizer, model=opus,  task=synthesize)→ Synthesized Solution
  └── spawn(triage,     model=opus,  task=triage)    → RELAX/DEFER/BLOCK decision
```

Each spawned sub-agent:
- Runs in an independent isolated session
- Receives only the file paths needed for that phase as input
- Writes artifacts to `pipeline/` directory
- Session ends automatically upon completion

### 6.2 External Broadcast (Notification Channel)

Orchestrator broadcasts a summary to the project notification channel on each phase transition:

```
📋 Pipeline [example-project] Progress Update
━━━━━━━━━━━━━━━━━━━━━━
✅ Phase 0: Constitute — Done
✅ Phase 1: Research — Done
🔄 Phase 2: Specify — In Progress (by @openclaw_designer_bot)
⬜ Phase 3: Plan+Tasks
⬜ Phase 4: Implement
⬜ Phase 5: Test
⬜ Phase 6: Review
━━━━━━━━━━━━━━━━━━━━━━
Next Check: in 30 mins
```

### 6.3 Human Intervention Points

Orchestrator will pause and notify CEO in these cases:
- A phase fails after all 3 layers of assistance (Model Escalation → Peer Consult → Auto-Triage) and is judged as BLOCK
- Review phase verdict is FAIL and requires rollback of more than 2 phases
- Encountering a blocker requiring system-level change
- Project Complete (PASS)
- Auto-Triage RELAX/DEFER count reaches per-run limit

---

## 7. Compatibility with Existing ORG Charter

| ORG Rule | How Pipeline Complies |
|---------|-----------------|\
| Boot Sequence (Read TASKBOARD → HANDOFF → ASSET_REGISTRY) | Enforced in Orchestrator prompt; injected into each sub-agent's prompt too |
| Closeout (Update HANDOFF/STATUS) | Automatically updated by Orchestrator after each phase transition |
| Persistence Rule (No \"done\" in chat only) | All phase artifacts are files, PIPELINE_LOG.jsonl records full process |
| Change Control (Only SRE modifies system config) | Orchestrator and sub-agents do not touch system config |
| Memory Layering (Org/Dept/Project/Agent) | Pipeline artifacts at Project level, state at Project level, no pollution |
| Reuse Policy (L0/L1/L2) | Pipeline framework itself is registered as L1 asset |

---

## 8. Observability

Borrowed suggestions from Effective Harnesses article:

### 8.1 PIPELINE_LOG.jsonl
- One record per phase transition (timestamp, event type, agent, duration, artifact path)
- Append-only, immutable, used for post-audit

### 8.2 Phase Checkpoint
- When each phase completes, record completedAt, completedBy, duration in PIPELINE_STATE.json
- If phase has multiple steps (like multiple subtasks in implement), track task-by-task in IMPL_STATUS.md

### 8.3 Guardrails
- Entry Condition Check: Previous artifact must exist and be non-empty
- Exit Condition Check: Artifact must meet minimum quality standards
- Retry Limit: Default 3, human intervention if exceeded
- Timeout Protection: Each sub-agent has timeoutSeconds limit

---

## 9. Flexibility Design

### 9.1 Phase Tailoring
Not all projects need 7 phases. Small projects can skip:
- Skip Phase 0 (Use Dept CHARTER instead)
- Merge Phase 1+2 (Research and Spec together)
- Skip Phase 6 (Small changes don't need formal review)

Set unwanted phases to `"status": "skipped"` in `phases` of `PIPELINE_STATE.json`.

### 9.2 Role Replaceability
`agentId` and `model` in `config.roles` can be adjusted per project. E.g., pure research projects can let professor do more phases.

### 9.3 Adjustable Trigger Frequency
Orchestrator cron frequency can range from 5 mins to 24 hours, depending on project urgency.

---

## 10. Migration from Existing Cron Jobs

Existing monolithic cron jobs (like example:iteration-loop) don't need immediate deprecation. Migration strategy:

1. **New Projects**: Use Pipeline framework directly.
2. **Existing Projects**: At the end of current iteration cycle, create Pipeline directory, map existing artifacts to corresponding phases, then switch to Pipeline mode.
3. **Maintenance Crons** (like example-maintenance): Don't need Pipeline, keep as is. Pipeline is for projects with clear goals and deliverables.

---

## Appendix A: Glossary

| Term | Meaning |
|------|------|
| Pipeline | Project phase state machine, defining full process from inception to delivery |
| Orchestrator | Scheduling agent, responsible for reading Pipeline state and advancing phases |
| Phase | One stage in the Pipeline |
| Artifact | Output product of a phase (file) |
| Gate | Gating condition between phases (Entry/Exit) |
| Spawn | Launch a sub-agent session via sessions_spawn |
| Rollback | Revert Pipeline to a specific phase when Review fails |

---

## 11. Dual-Layer Assistance Mechanism (Assistance Protocol)

> Added 2026-02-14 | Solves the problem of sub-agents getting stuck with no lateral help channel

### 11.1 Problem Scenario

Sub-agents may get stuck during phase tasks due to:
- Insufficient model capability (simple model can't solve complex problem)
- Need for different perspective (same model retrying same approach repeatedly)
- Parameter tuning tasks needing multi-solution comparison

Existing mechanism only has `maxRetries` retrying the same model, with no escalation or help channel.

### 11.2 Layer 1: Model Escalation (Escalation Chain)

When sub-agent execution fails, Orchestrator automatically retries with a stronger model along a predefined chain:

```
mini → glm → codex → sonnet → ⛔ Human Intervention
```

Configuration (in `config` of `PIPELINE_STATE.json`):

```json
"escalation": {
  "enabled": true,
  "chain": ["mini", "glm", "codex", "sonnet"],
  "escalateAfterFails": 1,
  "humanThreshold": "sonnet"
}
```

- `chain`: Model upgrade order, cheap to expensive
- `escalateAfterFails`: Upgrade after how many failures per model (default 1)
- `humanThreshold`: If this model still fails, trigger Layer 2 or human intervention

Logic:
1. Initial model (specified by config.roles) fails.
2. Orchestrator picks next model in chain, re-spawns.
3. Record each upgrade to PIPELINE_LOG.jsonl: `{"event":"model_escalated","fromModel":"...","toModel":"..."}`
4. If humanThreshold reached and still fails → Enter Layer 2.

### 11.3 Layer 2: Peer Consult (Parallel Multi-Model Consultation)

Simultaneously consult multiple different models, collect multi-perspective solutions, synthesize, then retry.

Configuration:

```json
"peerConsult": {
  "enabled": true,
  "triggerAfterEscalationFails": 2,
  "consultModels": ["gpro", "glm", "sonnet"],
  "consultTimeout": 300,
  "synthesizerModel": "opus",
  "maxConsultRounds": 1
}
```

Flow:

```
Sub-agent stuck (Escalation chain exhausted)
    │
    ▼
Orchestrator collects error context
    │
    ├── spawn(consultant, model=gpro,   task=consult_request prompt)
    ├── spawn(consultant, model=glm,    task=consult_request prompt)
    └── spawn(consultant, model=sonnet, task=consult_request prompt)
    │
    ▼ (Three consultants return in parallel)
    │
spawn(synthesizer, model=opus, task=consult_synthesize prompt)
    │
    ▼
Inject synthesized solution into original phase prompt
    │
    ▼
Re-spawn original task using strongest model in escalation chain
    │
    ├─ Success → Proceed normally ✅
    └─ Fail → Mark blocker, notify human 🚨
```

### 11.4 Sub-Agent Stuck Reporting Protocol

Sub-agents are instructed in Phase prompt: After 2 consecutive failures, do not persist blindly. Report stuck status in artifact file:

Implement Phase (IMPL_STATUS.md):
```
- T-xxx: stuck | Error Summary: <One sentence> | Tried: <List of approaches> | Relevant Files: <Path>
```

Test Phase (TEST_REPORT.md):
```
### Stuck Items
- Test Item: <FR-xxx> | Error Summary: <One sentence> | Tried: <List of approaches> | Relevant Files: <Path>
```

Orchestrator detects stuck flag and automatically enters assistance flow.

### 11.5 PIPELINE_STATE.json Extended Fields

Phase object adds `stuckInfo`:

```json
{
  "implement": {
    "status": "stuck",
    "stuckInfo": {
      "taskId": "T-003",
      "failCount": 4,
      "errorSummary": "PyBaMM Chen2020 model parameters not converging",
      "escalationLevel": 3,
      "consultRequested": true,
      "consultResults": [
        {"model": "gpro", "sessionKey": "...", "status": "done", "suggestion": "..."},
        {"model": "glm",  "sessionKey": "...", "status": "done", "suggestion": "..."},
        {"model": "sonnet","sessionKey": "...", "status": "done", "suggestion": "..."}
      ],
      "synthesizedSolution": "Synthesized Solution: ...",
      "retryWithSolution": false
    }
  }
}
```

### 11.6 New Log Event Types

```jsonl
{"ts":"...\",\"event\":\"model_escalated\",\"phase\":\"implement\",\"task\":\"T-003\",\"fromModel\":\"codex\",\"toModel\":\"sonnet\"}
{"ts":"...\",\"event\":\"consult_requested\",\"phase\":\"implement\",\"task\":\"T-003\",\"models\":[\"gpro\",\"glm\",\"sonnet\"]}
{"ts":"...\",\"event\":\"consult_complete\",\"phase\":\"implement\",\"task\":\"T-003\",\"model\":\"gpro\"}
{"ts":"...\",\"event\":\"solution_synthesized\",\"phase\":\"implement\",\"task\":\"T-003\",\"synthesizer\":\"opus\"}
{"ts":"...\",\"event\":\"retry_with_solution\",\"phase\":\"implement\",\"task\":\"T-003\",\"model\":\"sonnet\"}
{"ts":"...\",\"event\":\"human_escalation\",\"phase\":\"implement\",\"task\":\"T-003\",\"reason\":\"All automated assistance failed\"}
```

### 11.7 Cost Control

- Layer 1 escalation starts from cheapest model, upgrades gradually, avoiding expensive models upfront.
- Layer 2 Peer Consult consultants use medium models (gpro/glm/sonnet), only synthesis uses opus.
- `maxConsultRounds` limits consultation rounds (default 1) to prevent infinite loops.
- After humanThreshold, do not auto-upgrade to opus execution, wait for human decision.

### 11.8 Prompt Templates

New template files added:
- `templates/PHASE_PROMPTS/consult_request.md` — Consultant agent prompt
- `templates/PHASE_PROMPTS/consult_synthesize.md` — Solution synthesizer agent prompt

See template file contents for details.

### 11.9 Layer 3: Auto-Triage

> Added 2026-02-15 | Solves the problem of pipeline stalling when no human is available (e.g., overnight)

#### Problem Scenario

After the escalation chain + peer consult + synthesized solution retry all fail, the existing flow directly marks a blocker and waits for human intervention. If this happens overnight (or when the human is unavailable for an extended period), the pipeline stalls completely, wasting hours of available compute.

#### Design Approach

Before marking a blocker, insert an Auto-Triage step. A strong model (opus) acts as a judge, making one of three decisions based on the project CONSTITUTION and SPECIFICATION:

1. **RELAX (Loosen constraints and continue)** — Lower acceptance criteria, accept partial completion, skip non-critical items. Continue the current run.
2. **DEFER (Suspend, move on to other tasks)** — Mark the stuck task as deferred. Pipeline skips it and continues with remaining tasks. Deferred tasks are recorded in GAP_ANALYSIS for the next iteration.
3. **BLOCK (Truly needs human)** — Involves safety red lines, architectural decisions, etc. that cannot be auto-downgraded. Only then mark as blocker.

#### Flow

```
All automated assistance exhausted
    │
    ▼
Orchestrator spawns Auto-Triage agent (model=opus)
    │
    ▼ Returns JSON decision
    │
    ├── RELAX (confidence >= 0.6)
    │     → Write relaxed constraints into stuckInfo.triageResult
    │     → Re-spawn original phase task with relaxed constraints
    │     → Append PIPELINE_LOG: {"event":"triage_relax"}
    │     ├─ Success → Proceed normally ✅
    │     └─ Fail → Mark blocker (still fails after relaxing, must wait for human)
    │
    ├── DEFER (confidence >= 0.6)
    │     → Mark task as deferred (not stuck/blocked)
    │     → Pipeline continues with remaining tasks
    │     → Deferred task recorded as GAP_ANALYSIS input
    │     → Append PIPELINE_LOG: {"event":"triage_defer"}
    │     → Broadcast: Task T-xxx deferred, will be addressed in next iteration
    │
    └── BLOCK (or confidence < 0.6)
          → Mark blocker, notify human (same as existing behavior)
          → Append PIPELINE_LOG: {"event":"triage_block"}
```

#### Configuration

Add to `config` in PIPELINE_STATE.json:

```json
"autoTriage": {
  "enabled": true,
  "triageModel": "opus",
  "minConfidence": 0.6,
  "allowRelax": true,
  "allowDefer": true,
  "maxRelaxPerRun": 3,
  "maxDeferPerRun": 5
}
```

- `enabled`: Whether to enable auto-triage (default true)
- `triageModel`: Model for triage (needs strong reasoning capability)
- `minConfidence`: Below this threshold, force BLOCK
- `allowRelax`: Whether to allow constraint relaxation (conservative projects can set to false)
- `allowDefer`: Whether to allow task deferral
- `maxRelaxPerRun`: Max relaxations per run (prevents constraints from being gradually hollowed out)
- `maxDeferPerRun`: Max deferred tasks per run (prevents too many tasks being skipped, making the run meaningless)

#### PIPELINE_STATE.json Extensions

Phase object's stuckInfo gains triage-related fields:

```json
{
  "stuckInfo": {
    "...existing fields...",
    "triageRequested": true,
    "triageResult": {
      "decision": "RELAX",
      "confidence": 0.85,
      "reasoning": "...",
      "relaxedConstraints": [...],
      "executionInstructions": "..."
    }
  }
}
```

For DEFER decisions, task-level new status:

```json
{
  "implement": {
    "status": "in_progress",
    "deferredTasks": [
      {
        "taskId": "T-003",
        "reason": "Model parameters not converging, needs more research",
        "deferredAt": "2026-02-15T03:00:00+08:00",
        "gapAnalysisNote": "T-003 needs re-research on parameter ranges, suggest next run Research phase supplement"
      }
    ]
  }
}
```

When all non-deferred tasks are complete, the phase is considered done (with partial marker), and the pipeline continues.

#### New Log Event Types

```jsonl
{"ts":"...","event":"triage_requested","phase":"implement","task":"T-003"}
{"ts":"...","event":"triage_relax","phase":"implement","task":"T-003","relaxedConstraints":[...],"confidence":0.85}
{"ts":"...","event":"triage_defer","phase":"implement","task":"T-003","reason":"...","confidence":0.78}
{"ts":"...","event":"triage_block","phase":"implement","task":"T-003","reason":"...","confidence":0.45}
{"ts":"...","event":"relax_retry_success","phase":"implement","task":"T-003"}
{"ts":"...","event":"relax_retry_failed","phase":"implement","task":"T-003"}
```

#### Integration with Gap Analysis

When the current run has DEFER or RELAX tasks, Phase 7 Gap Analysis input automatically includes:

- List of all deferred tasks and reasons
- List of all relaxed constraints and degree of relaxation
- Recommendation to restore original constraints and re-attempt in the next run

This ensures relaxations and deferrals are not permanent — they are temporary measures for the current run, re-evaluated in the next.

#### Safety Guardrails

- confidence < 0.6 forces BLOCK, no automatic decisions allowed
- Items marked as "safety red lines" or "non-negotiable" in CONSTITUTION cannot be RELAXed
- Per-run RELAX count has an upper limit (default 3), preventing constraints from being gradually hollowed out
- Per-run DEFER count has an upper limit (default 5), preventing the run from becoming an empty shell
- All triage decisions are logged to PIPELINE_LOG, fully auditable
- Review phase (Phase 6) sees all RELAX/DEFER records and can judge FAIL accordingly

#### Prompt Template

New template file:
- `templates/PHASE_PROMPTS/auto_triage.md` — Triage agent prompt
