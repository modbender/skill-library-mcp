---
name: presale-service-bootstrap
description: Scaffold a new presale service foundation (docs/config/plans/readiness) before coding. Use when starting a new presale automation service, rebuilding project context, or preparing reusable one-pass execution artifacts.
---

Create the service foundation before any implementation.

## Execute
1. Create the minimal repo structure: `docs/`, `config/`, `src/`, `tests/`, `prompts/`, `scripts/`.
2. Build canonical context docs from templates.
3. Build at least one implementation plan with gap-check, acceptance scenarios, verification matrix, and summary snapshots.
4. Build one-pass launch docs and readiness checklist.
5. Freeze non-goals and constraints in writing.

## Use deterministic scaffold tool first
Run `tools/new-presale-service.ps1` from this skill pack when possible.

## Then fill definitions
Read and apply:
- `references/workflow.md`
- `references/artifacts.md`

## Required quality gates
- No definitions -> no coding.
- No readiness checklist -> no one-pass launch.
- No verification matrix template in plans -> no implementation approval.