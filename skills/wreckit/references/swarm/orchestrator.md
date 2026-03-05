# Swarm Orchestrator Pattern

> **CRITICAL:** Read `collect.md` completely before spawning any workers.
> The #1 failure mode is writing the proof bundle before all workers report back.
> This happened on midas-mcp (Feb 16, 2026). Never again.

---

## Architecture

```
Main agent → wreckit orchestrator (depth 1)
  ├─ PHASE 1: Planning
  │   └→ Architect worker (depth 2)
  ├─ PHASE 2: Building (sequential, one worker per task)
  │   ├→ Implementer-1 (depth 2)
  │   ├→ Implementer-2 (depth 2)
  │   └→ ...
  ├─ PHASE 3: Parallel Verification
  │   ├→ slop-scan worker (depth 2)
  │   ├→ type-check worker (depth 2)
  │   ├→ test-quality worker (depth 2)
  │   ├→ mutation-kill worker (depth 2)
  │   ├→ security worker (depth 2)
  │   ├→ dynamic-analysis worker (depth 2)
  │   ├→ perf-benchmark worker (depth 2)
  │   ├→ property-test worker (depth 2)
  │   ├→ design-review worker (depth 2) [AUDIT + REBUILD only]
  │   ├→ ci-integration worker (depth 2) [BUILD + REBUILD + AUDIT]
  │   └→ differential-test worker (depth 2) [BUILD + REBUILD only]
  ├─ PHASE 4: Sequential Verification
  │   ├→ cross-verify (if BUILD mode)
  │   ├→ regression (if REBUILD/FIX mode)
  │   └→ llm-judge (optional)
  └─ PHASE 5: Decision
      └→ Proof bundle → Ship / Caution / Blocked
```

---

## Config Required

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxSpawnDepth": 2,
        "maxChildrenPerAgent": 12,
        "maxConcurrent": 12
      }
    }
  }
}
```

If these aren't set, abort and tell the user to update their config.

---

## Model Selection Per Role

| Role | Model | Reason |
|------|-------|--------|
| Orchestrator | Opus | Ship/Caution/Blocked decisions require judgment |
| Architect | Opus | Planning + gap analysis needs quality |
| Implementer | Opus | Code quality matters for implementation |
| Slop scan | Sonnet | Pattern analysis, not generation |
| Type check | Haiku | Just runs a CLI command |
| Test quality | Sonnet | Analysis |
| Mutation kill | Sonnet | Simple mutations + test running |
| Security (SAST) | Sonnet | Pattern recognition |
| Dynamic Analysis | Sonnet | Script execution + analysis |
| Perf Benchmark | Sonnet | Script execution + analysis |
| Property-Based Testing | Sonnet | Test execution + analysis |
| Design Review | Sonnet | Pattern analysis (AUDIT + REBUILD only) |
| CI Integration | Sonnet | Pipeline execution (BUILD + REBUILD + AUDIT) |
| Differential Testing | Sonnet | Comparison analysis (BUILD + REBUILD only) |
| Cross-verify | Opus | Regenerating code for comparison needs quality |
| LLM-as-judge | Opus | Subjective judgment |

---

## Phase 1: Planning

Spawn ONE architect worker. Wait for it to complete before spawning builders.

```
sessions_spawn:
  task: "You are the Architect for a wreckit verification run.
    Project: [path]
    Mode: [BUILD/REBUILD/FIX/AUDIT]
    PRD/spec: [contents or path]

    1. Read the PRD or bug report
    2. Identify all tasks needed (list each discrete unit of work)
    3. Write IMPLEMENTATION_PLAN.md to the project root with:
       - Task list (numbered)
       - Acceptance criteria per task
       - Risk flags (potential failure modes)
       - Suggested test approach
    4. When done, your first line of response must be: ARCHITECT COMPLETE"
  label: wreckit-architect
  model: anthropic/claude-opus-4-6
```

**Wait for ARCHITECT COMPLETE before proceeding.**

---

## Phase 2: Building (Sequential)

Before building tasks (BUILD/REBUILD/FIX modes only), run these workers:

**Behavior Capture (REBUILD mode only):**
```
sessions_spawn:
  task: "wreckit gate: Behavior Capture.
    Project: [path]
    Run: ~/Projects/wreckit-ralph/scripts/behavior-capture.sh [path]
    Read references/gates/behavior-capture.md for pass/fail criteria.
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-BEHAVIOR: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-behavior
  model: anthropic/claude-sonnet-4-6
```

**Ralph Loop (BUILD/REBUILD/FIX modes only):**
```
sessions_spawn:
  task: "wreckit gate: Ralph Loop.
    Project: [path]
    Run: ~/Projects/wreckit-ralph/scripts/ralph-loop.sh [path]
    Then read references/gates/ralph-loop.md for additional AI-driven checks.
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-RALPH: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-ralph
  model: anthropic/claude-sonnet-4-6
```

For each task in IMPLEMENTATION_PLAN.md, spawn ONE implementer. Wait for each to complete before spawning the next.

```
sessions_spawn:
  task: "You are Implementer [N] for a wreckit verification run.
    Project: [path]
    Your task: [task description from IMPLEMENTATION_PLAN.md]
    Acceptance criteria: [criteria]

    1. Implement ONLY this one task
    2. Run type checker immediately after
    3. Run slop-scan.sh immediately after
    4. If either fails, fix before reporting back
    5. Commit your work: git add -A && git commit -m '[task name]'
    6. First line of response: IMPLEMENTER-[N] COMPLETE: [pass/fail] [brief summary]"
  label: wreckit-build-N
  model: anthropic/claude-opus-4-6
```

**Wait for each IMPLEMENTER-N COMPLETE before spawning the next.**

---

## Phase 3: Parallel Verification

Spawn ALL verification workers simultaneously. Then apply the collect pattern from `collect.md`.

### Pre-Spawn Checklist
Before spawning, write this checklist in your response:

```
VERIFICATION WORKERS CHECKLIST:
- wreckit-slop: PENDING
- wreckit-typecheck: PENDING
- wreckit-testquality: PENDING
- wreckit-mutation: PENDING
- wreckit-security: PENDING
- wreckit-dynamic: PENDING
- wreckit-perf: PENDING
- wreckit-property: PENDING
- wreckit-design: PENDING  [AUDIT + REBUILD only]
- wreckit-ci: PENDING  [BUILD + REBUILD + AUDIT]
- wreckit-differential: PENDING  [BUILD + REBUILD only]
```

### Spawn All Workers

**Slop Scan:**
```
sessions_spawn:
  task: "wreckit gate: AI Slop Scan.
    Project: [path]
    Run: ~/Projects/wreckit-ralph/scripts/slop-scan.sh [path]
    Then read references/gates/slop-scan.md and apply additional checks.
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-SLOP: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-slop
  model: anthropic/claude-sonnet-4-6
```

**Type Check:**
```
sessions_spawn:
  task: "wreckit gate: Type Check.
    Project: [path]
    Run: ~/Projects/wreckit-ralph/scripts/type-check.sh [path]
    (falls back to detect-stack.sh type checker command if needed)
    Read references/gates/type-check.md for pass/fail criteria.
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-TYPECHECK: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-typecheck
  model: anthropic/claude-haiku-3.5
```

**Test Quality:**
```
sessions_spawn:
  task: "wreckit gate: Test Quality.
    Project: [path]
    Run ~/Projects/wreckit-ralph/scripts/coverage-stats.sh [path]
    Read references/gates/test-quality.md for checks.
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-TESTQUALITY: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-testquality
  model: anthropic/claude-sonnet-4-6
```

**Mutation Kill:**
```
sessions_spawn:
  task: "wreckit gate: Mutation Kill.
    Project: [path]
    Run ~/Projects/wreckit-ralph/scripts/mutation-test.sh [path]
    Read references/gates/mutation-kill.md for thresholds (>=95% ship, 90-94 caution, <90 blocked).
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-MUTATION: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-mutation
  model: anthropic/claude-sonnet-4-6
```

**Security (SAST):**
```
sessions_spawn:
  task: "wreckit gate: Security / SAST.
    Project: [path]
    Read references/gates/sast.md and execute all checks.
    Run ~/Projects/wreckit-ralph/scripts/red-team.sh [path] if it exists.
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-SECURITY: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-security
  model: anthropic/claude-sonnet-4-6
```

**Dynamic Analysis:**
```
sessions_spawn:
  task: "wreckit gate: Dynamic Analysis.
    Project: [path]
    Run ~/Projects/wreckit-ralph/scripts/dynamic-analysis.sh [path]
    Read references/gates/dynamic-analysis.md for pass/fail criteria.
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-DYNAMIC: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-dynamic
  model: anthropic/claude-sonnet-4-6
```

**Performance Benchmark:**
```
sessions_spawn:
  task: "wreckit gate: Performance Benchmark.
    Project: [path]
    Run ~/Projects/wreckit-ralph/scripts/perf-benchmark.sh [path]
    Read references/gates/performance.md for pass/fail criteria.
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-PERF: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-perf
  model: anthropic/claude-sonnet-4-6
```

**Property-Based Testing:**
```
sessions_spawn:
  task: "wreckit gate: Property-Based Testing.
    Project: [path]
    Run ~/Projects/wreckit-ralph/scripts/property-test.sh [path]
    Read references/gates/property-based.md for pass/fail criteria.
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-PROPERTY: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-property
  model: anthropic/claude-sonnet-4-6
```

**Design Review (AUDIT + REBUILD only):**
```
sessions_spawn:
  task: "wreckit gate: Design Review.
    Project: [path]
    Run ~/Projects/wreckit-ralph/scripts/design-review.sh [path]
    Read references/gates/design-review.md for pass/fail criteria.
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-DESIGN: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-design
  model: anthropic/claude-sonnet-4-6
```

**CI Integration (BUILD + REBUILD + AUDIT):**
```
sessions_spawn:
  task: "wreckit gate: CI Integration.
    Project: [path]
    Run ~/Projects/wreckit-ralph/scripts/ci-integration.sh [path]
    Read references/gates/ci-integration.md for pass/fail criteria.
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-CI: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-ci
  model: anthropic/claude-sonnet-4-6
```

**Differential Testing (BUILD + REBUILD only):**
```
sessions_spawn:
  task: "wreckit gate: Differential Testing.
    Project: [path]
    Run ~/Projects/wreckit-ralph/scripts/differential-test.sh [path]
    Read references/gates/differential.md for pass/fail criteria.
    Report format: follow references/swarm/handoff.md exactly.
    First line: WRECKIT-DIFFERENTIAL: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-differential
  model: anthropic/claude-sonnet-4-6
```

### After Spawning: STOP AND WAIT — Explicit Collect Loop

**DO NOT proceed until all 11 workers report back.**
See `collect.md` for the full collect protocol.

#### Collect Loop Pseudocode

```
spawned = ["wreckit-slop", "wreckit-typecheck", "wreckit-testquality",
           "wreckit-mutation", "wreckit-security",
           "wreckit-dynamic", "wreckit-perf", "wreckit-property",
           "wreckit-design", "wreckit-ci", "wreckit-differential"]
# Note: wreckit-design spawned for AUDIT + REBUILD only
# Note: wreckit-ci spawned for BUILD + REBUILD + AUDIT
# Note: wreckit-differential spawned for BUILD + REBUILD only
results = {}
spawn_time = now()

WAIT_LOOP:
  completed = count(results)
  pending   = spawned - completed

  if completed == len(spawned):
    break  # all done → proceed to Phase 4

  # Poll sessions_list every 30 seconds
  sleep(30)
  active_sessions = sessions_list()

  for worker in pending:
    if worker NOT in active_sessions:
      # Worker exited — check if it sent a result
      if worker NOT in results:
        elapsed = now() - spawn_time
        if elapsed > 10 minutes:
          results[worker] = { status: "TIMED_OUT", gate_result: null }
          # DO NOT fabricate — mark explicitly as TIMED_OUT
        # else: keep waiting, may still announce

  # Validate each received result
  for worker, output in results:
    if "gate_result" NOT in output:
      results[worker].status = "FAILED"  # missing required field

  # Re-output updated checklist
  print_checklist(spawned, results)

# On timeout (worker silent > 10 min):
#   Mark status = TIMED_OUT, NOT fabricated
#   Proof bundle MUST note the incomplete gate
#   Verdict CANNOT be Ship with a TIMED_OUT gate
```

#### Timeout Rules

| Time since spawn | Action |
|-----------------|--------|
| 0–5 min | Wait normally |
| 5 min | Check `sessions_list` to confirm still running |
| 10 min | Mark silent worker as `TIMED_OUT` — do NOT fabricate |
| After timeout | Note in proof bundle; verdict ≤ CAUTION |

#### Worker Output Validation

Every worker result MUST contain `gate_result` field. If missing:
- Mark worker status as `FAILED` (not fabricated, explicitly failed)
- Record the missing field in the proof bundle
- Do NOT assume the gate passed

---

## Phase 4: Sequential Verification

After all parallel workers complete:

**Cross-verify (BUILD mode only):**
```
sessions_spawn:
  task: "wreckit gate: Cross-Verify (Independent Regeneration).
    Project: [path]
    Original code: [path]
    Read references/gates/cross-verify.md.
    Regenerate the core logic from scratch WITHOUT reading the implementation.
    Compare outputs on test cases. Report discrepancies.
    First line: WRECKIT-CROSSVERIFY: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-crossverify
  model: anthropic/claude-opus-4-6
```

**Regression (REBUILD/FIX mode only):**
```
sessions_spawn:
  task: "wreckit gate: Regression.
    Project: [path]
    Behavior snapshots: [path to snapshots]
    Read references/gates/regression.md.
    Run captured behavior tests against new implementation.
    First line: WRECKIT-REGRESSION: [PASS|FAIL|WARN|ERROR]"
  label: wreckit-regression
  model: anthropic/claude-sonnet-4-6
```

---

## Phase 5: Decision

Only after ALL workers from phases 3 and 4 have reported:

1. Collect all results
2. Apply decision framework from SKILL.md
3. Run: echo '[...gate-results-json-array...]' | ~/Projects/wreckit-ralph/scripts/proof-bundle.sh [path] [mode]
   (pipe the collected gate results JSON array to proof-bundle.sh — it calculates verdict deterministically)
4. Output final verdict: **Ship ✅ / Caution ⚠️ / Blocked 🚫**

---

## Failure Handling

| Scenario | Action |
|----------|--------|
| Worker hallucinated deps in slop scan | STOP everything → Blocked |
| One gate fails, others pass | Complete all gates, report all results |
| Mutation kill fails | Loop back to Ralph loop with "strengthen tests" |
| Worker times out (5 min) | Check subagents list, wait up to 10 min |
| Worker crashes/gone | Mark as ERROR, note in proof bundle, continue |
| Hard cap: 50 iterations | Still failing → Blocked with all evidence |

---

## ANTI-FABRICATION RULES (Never Do These)

❌ NEVER write the proof bundle before all workers report  
❌ NEVER assume a worker passed because it was spawned successfully  
❌ NEVER fill in missing results with "likely passed" or "expected pass"  
❌ NEVER skip a worker because you think it's unnecessary  
❌ NEVER report a kill rate you didn't actually measure  
❌ NEVER copy results from a previous run if this is a new run  

---

## Correct vs Wrong Behavior

### ✅ CORRECT
```
Spawned 11 workers.

VERIFICATION WORKERS CHECKLIST:
- wreckit-slop: PENDING
- wreckit-typecheck: PENDING
- wreckit-testquality: PENDING
- wreckit-mutation: PENDING
- wreckit-security: PENDING
- wreckit-dynamic: PENDING
- wreckit-perf: PENDING
- wreckit-property: PENDING
- wreckit-design: PENDING
- wreckit-ci: PENDING
- wreckit-differential: PENDING

[waiting...]

Received: WRECKIT-SLOP: PASS
Updated checklist:
- wreckit-slop: PASS ✅
- wreckit-typecheck: PENDING ⏳
- wreckit-testquality: PENDING ⏳
- wreckit-mutation: PENDING ⏳
- wreckit-security: PENDING ⏳
- wreckit-dynamic: PENDING ⏳
- wreckit-perf: PENDING ⏳
- wreckit-property: PENDING ⏳
- wreckit-design: PENDING ⏳
- wreckit-ci: PENDING ⏳
- wreckit-differential: PENDING ⏳

[still waiting for 10 more...]

Received: WRECKIT-TYPECHECK: PASS
...

All 11 workers complete. Writing proof bundle now.
```

### ❌ WRONG (what happened on midas-mcp)
```
Spawned 11 workers.

[1 worker responded]

All workers complete! Results:
- Slop scan: PASS (assumed)
- Type check: PASS (assumed)
- Test quality: PASS (assumed)
- Mutation kill: 97% kill rate (fabricated)
- Security: PASS (assumed)
- Dynamic Analysis: PASS (assumed)
- Perf Benchmark: PASS (assumed)
- Property-Based Testing: PASS (assumed)
- Design Review: PASS (assumed)
- CI Integration: PASS (assumed)
- Differential Testing: PASS (assumed)

Verdict: Ship ✅
```

## Adaptive Gate Behavior (added 2026-02-22)

Based on live runs against zod and chatbot-ui, the orchestrator should adapt:

### Skip gates when irrelevant:
- Skip `coverage_stats` and `mutation_kill` if `detect-stack.sh` returns `testRunner: none` or no test script
- Skip `ralph_loop` in AUDIT mode unless `IMPLEMENTATION_PLAN.md` exists
- Skip `behavior_capture` unless mode == REBUILD

### Early exit on critical failures:
- `check_deps` FAIL → BLOCKED immediately (hallucinated deps = unshippable)
- `slop_scan` finds >50 artifacts → BLOCKED immediately
- `type_check` > 10 errors → BLOCKED immediately
- Log reason in proof bundle

### Project size adaptation:
- >100 source files: set `WRECKIT_LARGE_PROJECT=1` (scripts should use sampling)
- Monorepos (multiple `package.json`): run detect-stack per sub-package

### Telemetry-driven gate ordering (fast-fail first):
After runs accumulate in `.wreckit/metrics.json`, reorder gates by:
1. check_deps (fast, catches hallucinated deps)
2. slop_scan (fast, catches obvious problems)
3. type_check (catches type errors)
4. coverage_stats / ci_integration (medium speed)
5. design_review / red_team (slower, run after fast gates pass)
6. mutation_kill (slowest — only if above all pass)
