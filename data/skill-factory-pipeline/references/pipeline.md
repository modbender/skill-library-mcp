# Pipeline Reference

Detailed specification of the skill-factory pipeline: stage order, gate definitions, failure handling, and re-run strategies.

## Architecture principle

The pipeline is a **linear state machine**. Each stage:
1. Reads from the workspace filesystem
2. Calls one isolated agent via `openclaw agent --agent <id> -m "<prompt>"`
3. Waits for the call to return
4. Checks the gate (file existence and non-empty)
5. Marks the stage done in `.pipeline_state`
6. Proceeds to the next stage

**No parallelism. No nested sessions. No shared process state.**

---

## Stage order

```
idea.md (input)
    │
    ▼
[market] ──────────── market.md
    │
    ▼
[planner] ─────────── plan.md
    │
    ▼
[arch] ─────────────── arch.md
    │
    ▼
[builder] ──────────── skill/
    │
    ▼
[auditor] ──────────── audit.md
    │
    ▼
[docs] ─────────────── docs_review.md
    │
    ▼
[pricer] ───────────── pricing.md
```

Each arrow represents a file written to disk. No stage passes data in memory.

---

## Gate definitions

Gates run immediately after an agent call returns. A gate failure stops the pipeline.

| Stage   | Gate condition                             | Failure action       |
|---------|--------------------------------------------|----------------------|
| market  | `market.md` exists and non-empty           | Stop, report stage   |
| planner | `plan.md` exists and non-empty             | Stop, report stage   |
| arch    | `arch.md` exists and non-empty             | Stop, report stage   |
| builder | `skill/SKILL.md` exists and non-empty      | Stop, report stage   |
| auditor | `audit.md` exists and non-empty            | Stop, report stage   |
| docs    | `docs_review.md` exists and non-empty      | Stop, report stage   |
| pricer  | `pricing.md` exists and non-empty          | Stop, report stage   |

### Soft gates (checked by agents, not by the pipeline script)

These conditions are enforced by agent instructions, not bash file checks:

- **auditor** → OVERALL must be PASS or FAIL (not missing)
- **docs** → If audit OVERALL is FAIL, docs_review.md must contain "BLOCKED"
- **pricer** → pricing.md must include a USD price and positioning statement

If a soft gate is violated (e.g., auditor writes an empty OVERALL), the next stage will produce low-quality output. Review audit.md manually if outputs seem off.

---

## Re-running stages

If a stage fails or produces bad output, re-run from that stage:

```bash
# Re-run from a specific stage to the end
pipeline.sh --workspace /tmp/sf-stripe --from auditor

# Re-run a single stage only
pipeline.sh --workspace /tmp/sf-stripe --from builder --to builder

# Re-run the last two stages
pipeline.sh --workspace /tmp/sf-stripe --from docs
```

Re-running a stage **overwrites** its output file. Earlier stages are unaffected.

The `.pipeline_state` file logs timestamps of completed stages for reference but does not prevent re-runs. It is informational only.

---

## Failure scenarios and recovery

### Scenario 1: Agent produces empty output

**Symptom:** Gate fails immediately after agent call.

**Likely causes:**
- Agent hit a context or token limit
- Agent misunderstood the prompt

**Recovery:**
1. Check if the output file was partially written: `cat workspace/market.md`
2. If partially written: edit the file manually, then run from the next stage
3. If completely empty: re-run the stage with `--from <stage> --to <stage>`

---

### Scenario 2: Audit returns OVERALL: FAIL

**Symptom:** `audit.md` contains "OVERALL: FAIL" with a list of required fixes.

**This is expected behavior.** The docs stage will write "BLOCKED" and stop.

**Recovery:**
1. Read `audit.md` — find the numbered required fixes
2. Edit the skill files manually in `workspace/skill/`
3. Re-run from the auditor: `--from auditor`
4. Repeat until auditor returns OVERALL: PASS

---

### Scenario 3: Builder diverges from architecture

**Symptom:** `skill/` contains different files than what `arch.md` specified.

**Recovery (Option A — fix builder output):**
1. Compare `arch.md` against `ls workspace/skill/`
2. Manually create or correct the missing files
3. Re-run from auditor: `--from auditor`

**Recovery (Option B — re-run builder):**
1. Remove the divergent files: `rm -rf workspace/skill/`
2. Re-run builder: `--from builder --to builder`

---

### Scenario 4: Market returns NO-GO verdict

**Symptom:** `market.md` ends with "NO-GO".

**This is a valid outcome.** The pipeline will continue (it does not parse the verdict), but the pricer will note low market viability.

**Decision points:**
- Stop the pipeline and pivot the idea — edit `idea.md`, re-run from `--from market`
- Continue anyway — note that the skill may have limited commercial value
- Narrow the scope — edit `idea.md` to reduce scope, re-run from `--from market`

---

## Workspace layout

```
workspace/
├── idea.md              # Input — created by init_pipeline.py, edited by user
├── .pipeline_state      # Timestamps of completed stages (informational)
├── market.md            # Stage 1 output
├── plan.md              # Stage 2 output
├── arch.md              # Stage 3 output
├── skill/               # Stage 4 output
│   ├── SKILL.md
│   ├── scripts/
│   │   └── *.sh / *.py
│   └── references/
│       └── *.md
├── audit.md             # Stage 5 output
├── docs_review.md       # Stage 6 output
└── pricing.md           # Stage 7 output
```

All files are plain text (markdown or bash/python). No binary state.

---

## Design rationale

### Why sequential and not parallel?

Each stage consumes output from the previous stage. The planner needs market research before scoping. The builder needs the architecture before implementing. Parallelism would require complex dependency tracking with no benefit — the bottleneck is agent execution time, not orchestration overhead.

### Why no nested sessions?

Nested sessions (spawning agents from within an agent's session) create:
- Hidden state the orchestrator cannot observe
- Non-deterministic execution order
- Impossible re-runs (you'd need to reproduce the outer session state)

Every agent call in this pipeline goes to the OS process table, not to a parent agent's session. The pipeline script is the orchestrator. It is the only process that knows the full state.

### Why file-based communication?

Files are:
- Inspectable at any time with a text editor
- Persistent across crashes
- Trivially re-runnable (re-run a stage = overwrite a file)
- Usable as handoff artifacts to humans

Environment variables or in-memory state would disappear on failure and make debugging opaque.
