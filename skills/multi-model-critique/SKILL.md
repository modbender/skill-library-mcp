---
name: multi-model-critique
description: Run complex prompts through a multi-model deliberation pipeline with structured self-improvement. Use when the user sets a complex flag (e.g., complex=true/complex) or asks for high-stakes, ambiguous, or long-form reasoning where one model is not enough. Produces outputs by: (1) parallel model runs, (2) cross-critique, (3) critique-driven revision, and (4) final synthesized answer with uncertainties and evidence notes.
metadata: {"openclaw":{"emoji":"🧠"}}
---

# Multi-Model Critique

## Overview
Use this skill only for complex tasks. Route multiple models through the same 4-step loop (`Plan -> Execute -> Review -> Improve`), then run cross-critique and synthesis to produce a higher-quality final answer than any single-model draft.

## Trigger rule
Enable this skill only when the request explicitly sets `complex` to true (or equivalent wording such as “this is complex/deep”).

If `complex` is false, skip this skill and respond with normal single-model behavior.

## Inputs
Collect or confirm these inputs before execution:
- `complex`: boolean flag (must be true)
- `question`: user request
- `models`: list of ACP `agentId` values (typically 3)
- `constraints`: output format, language, length, deadlines, forbidden assumptions
- `ops`: optional runtime controls (`timeoutSec`, `maxRetries`, `maxRounds`, `budgetUsd`)

## File map (what each file does)
- `SKILL.md` (this file): orchestration policy, trigger conditions, and execution sequence.
- `references/prompt-templates.md`: reusable prompts for draft, critique, revision, and final synthesis (includes scoring rubric usage).
- `references/orchestration-template.md`: practical OpenClaw orchestration flow using `sessions_spawn`, `sessions_send`, and `sessions_history`.
- `references/output-schema.md`: machine-parseable JSON output schema for final result and per-model scoring.
- `scripts/build_round_prompts.py`: utility to generate per-model prompt files for repeated runs.
- `scripts/run_orchestration.py`: local helper that builds a run plan JSON (model mapping, round prompts, runtime settings).

## Workflow

### Step 1) Parallel draft round
Spawn one ACP session per model with the same task and constraints.

Per-model requirements:
- Follow the exact internal sequence: `Plan -> Execute -> Review -> Improve`
- Print all four sections explicitly
- End with `Draft Answer`

Use `sessions_spawn` with `runtime:"acp"` and explicit `agentId`.

### Step 2) Cross-critique round
Share peer `Draft Answer` outputs with each model and require structured critique:
- Strengths
- Weaknesses
- Missing assumptions/data
- Hallucination and confidence risks
- Concrete fix suggestions

Also require ranking of peer drafts with rationale.

### Step 3) Revision round
Send critique feedback back to each original model and request revision:
- Keep `Plan -> Execute -> Review -> Improve`
- Include `Changes from Critique`
- End with `Revised Answer`

### Step 4) Final synthesis round
Integrate revised answers into one user-facing output:
- Best final answer
- Why the synthesis is stronger than individual drafts
- Remaining uncertainties
- Optional next actions

## Scoring rubric (required in critique + synthesis)
Score each draft on a 1-5 scale:
- `accuracy`: factual correctness and internal consistency
- `coverage`: completeness against user request and constraints
- `evidence`: quality of assumptions and support
- `actionability`: usefulness for concrete decision/action

Default weighted score:
`0.40 * accuracy + 0.25 * coverage + 0.20 * evidence + 0.15 * actionability`

Use this score to justify rankings and the final selected direction.

## Prompting resources
- Use `references/prompt-templates.md` for canonical prompts.
- Use `scripts/build_round_prompts.py` when you need file-based prompt generation for repeated or batched runs.
- Use `scripts/run_orchestration.py` to generate a deterministic run-plan artifact for reproducible execution.
- Use `references/orchestration-template.md` for concrete OpenClaw tool-call flow.

## Required user-facing output shape
1. `Final Answer`
2. `Key Improvements from Critique`
3. `Uncertainties`
4. `Next Steps` (optional)

When machine consumption is needed, return JSON matching `references/output-schema.md`.

Do not expose private chain-of-thought. Provide concise reasoning summaries only.

## Failure handling
- One model fails: continue with remaining models and note reduced diversity.
- Two or more models fail: ask whether to retry or switch to single-model mode.
- Strong disagreement remains: present competing hypotheses and state what evidence would resolve them.

## Runtime defaults (recommended)
- `timeoutSec`: 180 per round per model
- `maxRetries`: 1 per failed model turn
- `maxRounds`: fixed at 4 (draft, critique, revision, synthesis)
- `budgetUsd`: optional hard stop when cost-sensitive
