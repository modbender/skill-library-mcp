---
name: jarvis-persona-style-calibrator-01
description: Calibrate assistant personality to voice, boundaries, and audience context. Use when handling personality work that needs repeatable steps, quality gates, and practical outputs.
---

# Jarvis Persona Style Calibrator 01

Deliver a concrete, reusable workflow for personality tasks.

## Inputs
- Desired outcome and deadline
- Constraints (time, tools, risk tolerance)
- Available artifacts (code, docs, screenshots, logs)

## Playbook
1. Define success and failure criteria in measurable terms.
2. Build a smallest-valid execution path before scaling effort.
3. Execute in checkpoints; record evidence at each checkpoint.
4. Apply quality gates before finalizing recommendations.
5. Return implementation-ready outputs and next actions.

## Quality Gates
- Evidence-backed claims only.
- Explicit assumptions and tradeoffs.
- Reversible changes preferred for risky operations.
- Clear owner + ETA for each next step.
- Include a fallback if the primary plan fails.

## Output Format
- Situation summary (5 lines max)
- Top findings (ranked by impact)
- Action plan (today / this week)
- Risks + mitigations
- Exact checklist or commands where useful

## Example prompts
- "Use this skill to turn my messy notes into a production-ready plan."
- "Run this skill and give me a risk-first action sequence with acceptance checks."
