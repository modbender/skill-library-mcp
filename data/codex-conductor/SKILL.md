---
name: codex-orchestrator
description: Methodical end-to-end software delivery orchestrator for Codex CLI with dual project modes (greenfield for new builds, brownfield for existing systems) and dual execution modes (autonomous and gated). Use when users want full lifecycle delivery with strict stage gates, progress tracking, per-step manual/automated testing, continuous docs updates, change-impact management, and a reusable AGENTS.md workflow for any coding agent.
---

# Codex Orchestrator

Coordinate Codex as a disciplined delivery system, not a one-shot generator.

## Core Modes

Select both:

- `project_mode`
  - `greenfield`: build from scratch
  - `brownfield`: onboard and modernize an existing system
- `execution_mode`
  - `autonomous`: proceed automatically when gates pass
  - `gated`: pause at every gate for user approval

## Governing Principle: Spec-Driven Development

**No code without a spec.** This is non-negotiable.

Before any implementation, a written spec must exist with:
- What is being built
- Why it's needed
- Acceptance criteria (testable)
- Constraints and out-of-scope

The coding agent MUST NOT:
- Guess at requirements
- Make assumptions about behavior
- Add unrequested features
- Invent abstractions not in spec

If spec is unclear → STOP and ask. Never guess.

See `references/spec-driven-development.md` for full spec templates and enforcement rules.

## Non-Negotiable Sequence

1. Intake + planning questionnaire
2. **Spec creation + approval** (specs written BEFORE any code)
3. Docs scaffold + AGENTS.md contract
4. Mode-specific pre-architecture work
5. Architecture + ADR baseline (references specs)
6. Build by vertical slices (each task references spec)
7. Verification against spec acceptance criteria
8. Security/quality gates
9. Release readiness + handover

Never skip gates silently. Never implement without a spec.

## Required Resources

Read these references before running:

- `references/spec-driven-development.md` (MANDATORY FIRST - governs all work)
- `references/planning-questionnaire.md`
- `references/modes.md`
- `references/gate-checklists.md`
- `references/testing-matrix.md`
- `references/manual-test-templates.md`
- `references/codex-runbook.md`
- `references/gate-prompts.md`
- `scripts/agent_exec.py`
- `references/research-playbook.md` (if `research_mode=true`)

## Scaffolding

Initialize project artifacts:

```bash
python scripts/init_project_docs.py --root <project-path> --mode <greenfield|brownfield>
```

This creates/updates:

- `AGENTS.md` (project workflow contract)
- `docs/*.md` planning/architecture/test/progress/change docs
- brownfield docs (when mode is brownfield)
- `.orchestrator/status.json` (machine-readable state)
- `.orchestrator/context.json` (project/execution/research mode context)

## Planning Rules

Before anything else, ask the user which coding agent to use (`codex` | `claude` | `opencode` | `pi`) and fallback agent.
Then ask all required questions from `references/planning-questionnaire.md`.

Minimum required answers:

- mission
- top user journeys
- v1 scope
- hosting target
- stack preference (or explicit request for recommendation)
- `project_mode`
- `execution_mode`
- definition of done
- acceptance tests

If `research_mode=true`, produce `docs/research-notes.md` and architecture recommendation before G2.

## Mode-Specific Requirements

### Greenfield

Must complete before G2:

- requirements + DoD clarity
- architecture baseline
- ADR-0001 with alternatives
- CI/test baseline plan

### Brownfield

Must complete before G2 (and authored by coding agent, not orchestrator):

- as-is architecture and system inventory
- dependency map and risk register
- characterization-test baseline
- migration strategy + rollback approach
- compatibility boundaries documented

## Gate Engine

Use gates `G0` through `G7` defined in `references/gate-checklists.md`.

Update gate state via script:

```bash
python scripts/gate_status.py set --root <project-path> --gate G3 --state PASS --note "slice-1 verified"
```

Validate status schema:

```bash
python scripts/gate_status.py validate --root <project-path>
```

Allowed states: `PENDING | IN_PROGRESS | PASS | FAIL | BLOCKED`.
By default, gate preconditions are enforced (sequence + mode-aware docs checks).

## Validation Rules

Use `references/testing-matrix.md`.

Mandatory checks per progression:

- lint/type/build
- unit/integration/e2e (as applicable)
- API contract sanity (if API exists)
- security baseline
- docs sync verification

Also execute manual test scripts from `references/manual-test-templates.md`.

## Documentation Rules

For each meaningful step:

- update `docs/tasks.md`
- update `docs/progress.md`
- append `docs/change-log.md`
- update `docs/traceability.md`
- record test evidence in `docs/test-results.md`

For user-requested changes, run:

```bash
python scripts/change_impact.py --root <project-path> --request "<change request>"
```

Then complete all TODOs it emits in impacted docs.

## Codex Execution Pattern

Use PTY/background for long runs. Follow command patterns in `references/codex-runbook.md`.

Critical rule: each run executes ONE task, not a whole project in one prompt.
For G4, maintain `docs/g4-task-plan.md` checklist and process tasks one by one.

Generate gate-specific prompts with:

```bash
python scripts/generate_gate_prompt.py --gate <G1..G7> --agent <codex|claude|opencode|pi> --project-mode <greenfield|brownfield> --execution-mode <autonomous|gated> --research-mode <true|false> --task "<single task summary>" --spec-ref "<spec ref when applicable>"
```

`update_docs_step.py` is now a fallback utility for recovery/manual bookkeeping only.
Primary expectation: the coding agent updates docs directly during each task.

Required loop:

1. verify spec exists for the task (no spec = no implementation)
2. launch selected coding agent with spec-driven prompt template
3. coding agent updates docs immediately after task completion (including handoff checklist)
4. coding agent wakes OpenClaw with task summary + where verification steps are documented
5. OpenClaw agent runs verification itself:
   - CLI checks in terminal tools
   - Browser/manual checks in browser tools (for web flows)
6. verify output matches spec acceptance criteria
7. if validations fail, OpenClaw sends exact failures back to coding agent and re-runs fix cycle
8. write final gate status only after validations pass (or mark FAIL/BLOCKED)

Enforcement:
- `run_gate.py` requires `--spec-ref` for G3/G4 tasks (implementation gates).
- `run_gate.py` requires coding agent + fallback agent context.
- Each task requires validation evidence (`--validate-cmd` and/or `--ui-review-note`).
- Tasks flagged with `--requires-browser-check` must include `--ui-review-note`.
- `status=PASS` requires at least one `--validate-cmd`.
- `status=PASS` is blocked when `--agent-dry-run` is used.
- For G4, PASS is blocked until `docs/g4-task-plan.md` has no unchecked tasks.
- Validation output is recorded in `docs/validation-log.md`.
- Coding agent must update docs after every task, including `docs/agent-handoff.md`.
- In brownfield mode, G1/G2 fail if onboarding docs are not updated by the coding agent.
- Coding agent prompts MUST include spec preamble from `references/spec-driven-development.md`.
- Any implementation without spec reference = automatic FAIL.
- In autonomous mode, failed validations trigger automatic fix retries (default: 2) with failure details passed back to coding agent.
- Optional strict mode: `--auto-block-on-retry-exhaust` auto-classifies gate as BLOCKED when retries are exhausted.

## Progress Visibility

Generate a quick status board:

```bash
python scripts/progress_dashboard.py --root <project-path>
```

This summarizes current gate, completion %, blockers, and recent activity.

Run a single-task gate step with one command:

```bash
python scripts/run_gate.py --root <project-path> --gate G2 --agent codex --fallback-agent claude --project-mode brownfield --execution-mode gated --research-mode true --task "architecture baseline refined for API routing" --status IN_PROGRESS --validate-cmd "npm run -s typecheck" --ui-review-note "N/A for architecture-only task"
```

Mark PASS only after all gate-level checklist items are complete:

```bash
python scripts/run_gate.py --root <project-path> --gate G2 --agent codex --task "architecture gate complete" --status PASS --validate-cmd "npm run -s typecheck"
```

For web/UI tasks, require browser verification by OpenClaw agent:

```bash
python scripts/run_gate.py ... --requires-browser-check --ui-review-note "Verified login + CRUD manually in browser via OpenClaw browser tools"
```

Package distributable skill artifact:

```bash
python scripts/package_skill.py --skill-dir . --out dist
```

## End-State Deliverables

At completion provide:

- `docs/progress.md` at 100%
- final gate summary from `.orchestrator/status.json`
- test result summary + unresolved risks
- deployment + rollback notes
- next-iteration backlog

If blockers remain, mark as `PARTIAL_COMPLETE` with explicit blockers and owners.
