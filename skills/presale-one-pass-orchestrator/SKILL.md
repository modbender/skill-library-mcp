---
name: presale-one-pass-orchestrator
description: Run or supervise a one-pass Codex implementation with preflight gates, stepwise plan execution, and strict QA defect loop. Use when executing approved presale plans end-to-end in one controlled run.
---

Run one-pass only after readiness is explicitly approved.

## Preflight
1. Validate all mandatory docs/configs from `project-context`.
2. Validate readiness checklist decision = YES.
3. Validate no open review comments.
4. Stop immediately on any failed gate.

## Execution protocol
1. Follow plan steps in order.
2. After each step, update plan `verification matrix` and `mid-summary`.
3. Keep scope locked; reject out-of-scope additions.

## QA defect loop (mandatory)
Apply process from `references/qa-defect-loop.md`.

## Completion
1. Ensure final summaries exist in all plan files.
2. Produce changed files + reproducible check commands.
3. List risks/debts and open questions.