# close-loop

End-of-session workflow for shipping work cleanly and retaining high-value memory.

## What it does

- Runs a 4-phase wrap-up: Ship State, Consolidate Memory, Review & Apply, Publish Queue.
- Uses typed memory buckets: working, episodic, semantic, procedural.
- Uses two-pass consolidation (extract then verify/dedupe/resolve conflicts).
- Applies a persistence filter plus confidence calibration and TTL retention.
- Enforces action gates for commit, push, deploy, and publish.
- Supports `dry-run` mode and emits a machine-readable JSON report.

## Use this skill when

- You want to end a coding session with clean repo state.
- You want structured memory updates instead of ad-hoc notes.
- You want repeatable self-improvement and publication triage.

## Files

- `SKILL.md` - Entry point + execution order.
- `components/01-design-principles.md` - Execution policy and action gates.
- `components/02-phase-1-ship-state.md` - Ship State phase steps.
- `components/03-phase-2-memory.md` - Memory consolidation and safety rules.
- `components/04-phase-3-4-and-output.md` - Improvements, publish queue, and output contract.
- `references/memory-frameworks.md` - Framework references and update checklist.
- `assets/templates/wrap-report-template.md` - Output template for session wrap reports.

## Quick usage

Trigger phrases:

- `wrap up`
- `close session`
- `end session`
- `/wrap-up`

Execution order:

1. Ship State
2. Consolidate Memory
3. Review and Apply Improvements
4. Publish Queue

## Design goals

- High signal memory only
- Deterministic end-of-session behavior
- Minimal irreversible actions without approval
- Clear output contract with evidence and confidence labels
- Memory security against poisoning/injection patterns
