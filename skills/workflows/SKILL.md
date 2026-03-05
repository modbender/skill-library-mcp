---
id: workflows
name: "Workflows via Ask Gina"
description: "Playbook for authoring, running, evaluating, and improving Gina sandbox workflows with safe defaults and repeatable operations."
---

# Workflows via Ask Gina Skill

## What It Does

Provides a practical workflow-authoring and operations standard for Gina sandbox automation.

- Creates and validates workflow definitions.
- Runs workflows and inspects artifacts/logs.
- Applies a repeatable eval -> optimize -> compare loop.
- Uses safe TypeScript/SQL/KV patterns for step logic.

## When To Use

- You are creating or maintaining multi-step workflow orchestration.
- You need reproducible debugging from run artifacts.
- You want measurable improvements using baseline comparisons.

## When Not To Use

- The task is a single action with no orchestration requirement.
- You only need high-level strategy language without runnable steps.
- You cannot provide explicit permissions or side effects.

## Inputs

- Workflow intent and success criteria.
- Trigger definition and input schema.
- Required tools/data sources and permission scope.
- Optional baseline run ID for optimization.

## Outputs

- Validated workflow definition (`.ts`).
- Runnable execution with traceable artifacts.
- Evaluation record with baseline comparison.
- Clear rollback path for regressions.

## Core Commands

```bash
workflow create <id>
workflow validate <id>
workflow run <id> [--input JSON]
workflow status <run-id>
workflow logs <run-id> [--step <step-id>]
workflow eval <run-id>
workflow optimize <id> --baseline <run-id>
workflow rollback <id> <opt-run-id>
```

## Setup

1. Confirm workflow tooling is available (`workflow list` should succeed).
2. Scaffold or open the target workflow in `/workspace/.harness/workflows/`.
3. Keep active versions on `@latest.ts` naming when versioned variants exist.
4. Validate before every run: `workflow validate <id>`.
5. For risky changes, capture a baseline run and eval before editing.

## Capability Contract Checklist

For each workflow entry, explicitly define:

- Trigger.
- Inputs.
- Outputs.
- Side effects.
- Failure modes.
- Permission scope.

## Failure Modes

- Validation failure from malformed step definitions.
- Runtime errors in TS/SQL/Bash steps.
- Missing tool permissions or tool availability.
- Data shape changes causing parse/cast failures.
- Timeout/retry exhaustion in external calls.

## Security And Permissions

- Use least privilege by step using `allow` and `block`.
- Declare permissions in the submission contract (no wildcard permissions).
- Never include raw secrets in skill text, logs, or examples.
- Treat writes (files, KV, external posts, trading actions) as explicit side effects.

## Evidence Expectations

- Setup path that a reviewer can execute in under 10 minutes.
- One reproducible run artifact or run log example.
- Clear statement of expected outputs and acceptable failure behavior.

## Optional Directories

```text
workflows/
  SKILL.md
  references/   # implementation and API details
  scripts/      # optional helpers for repeatable checks
  assets/       # optional diagrams/screenshots
```

## Reference Material

Deep technical references are intentionally split out:

- `references/cli-and-definition.md`
- `references/eval-optimize-and-artifacts.md`
- `references/polymarket-patterns.md`

Use these as appendices while keeping this file focused on operational usage.
