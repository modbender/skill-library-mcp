---
name: intent-align
description: "Intent-alignment orchestration for OpenClaw agent teams across diverse host environments. Use when work must stay anchored to user goals while allowing flexible execution: (1) coding with repos/PRs/issues, (2) multi-phase delivery with checkpoints, (3) multi-agent or multi-repo coordination, (4) evolving requirements needing structured re-alignment and user clarification loops."
---

# Intent-Align v2 Core

Keep execution aligned to user intent while preserving agent autonomy.

## Quick Start
1. Read [references/core-contract.md](references/core-contract.md).
2. Create alignment hub from [references/alignment-hub-template.md](references/alignment-hub-template.md).
3. Run Intent Quality Gate before planning.
4. Select adapters from [references/adapters/](references/adapters).
5. Execute phases with realignment and verification gates.

## Workflow Contract
1. Build `intent_snapshot` and run `intent_lint` (see core contract).
2. Ask for strictness mode and scope overrides (project/repo/workflow/task).
3. Resolve effective strictness by precedence: `task > workflow > repo > project > default`.
4. Evaluate ambiguity action using severity + strictness + risk class.
5. Generate phase plan and Mermaid diagram with explicit dependencies and gates.
6. Bind available adapters through `capability_matrix`.
7. Execute phase-by-phase.
8. Before phase start, run Pre-Execution Clarification Gate.
9. On each phase end, run verification gates (including output conformance) and update drift evidence.
10. If intent or constraints change, apply `intent_delta` and re-plan only impacted phases.
11. Close with final alignment report and open ambiguity list (if any).

## Autonomy Levels
- `1 Strict`: Require user confirmation before each phase start.
- `2 Balanced`: Require user confirmation at phase end or any critical drift.
- `3 Aggressive`: Auto-continue on low drift; require confirmation on major deltas.
- `4 Exploratory`: Continue with log-only check-ins unless risk or ambiguity threshold is exceeded.

Override rule: high-risk ambiguity is never advisory-only; enforce at least `soft_gate`.
Strictness rule: strictness mode controls whether ambiguities block or proceed with guardrails.

## Required References
- [references/core-contract.md](references/core-contract.md)
- [references/alignment-hub-template.md](references/alignment-hub-template.md)
- [references/realignment-protocol.md](references/realignment-protocol.md)
- [references/verification-gates.md](references/verification-gates.md)
- [references/capability-taxonomy.md](references/capability-taxonomy.md)

## Adapter Selection
Use only adapters needed for the task:
- [references/adapters/github.md](references/adapters/github.md)
- [references/adapters/local-repo.md](references/adapters/local-repo.md)
- [references/adapters/tracker-generic.md](references/adapters/tracker-generic.md)
- [references/adapters/adapter-template.md](references/adapters/adapter-template.md)

If no adapter can satisfy a required capability:
1. Generate an ad-hoc adapter spec from `adapter-template.md`.
2. Add provenance metadata (`created_by`, `created_at`, `environment_assumptions`, `tool_access_required`).
3. Validate required fields before use.
4. Register the new adapter in `capability_matrix.adapters_selected`.
5. Continue in degraded mode only if validation fails or auth/capability remains unavailable.

## Anti-Bloat Rules
- Keep core contract tool-agnostic.
- Do not add tracker- or host-specific logic to core files.
- Add a new adapter only for a proven capability gap.
- Keep schemas single-source; do not duplicate fields across files.
- Tie each new feature to one concrete failure mode and one test scenario.
- Generate ad-hoc adapters only for current task scope; do not pre-generate broad catalogs.
- Use canonical capability IDs first; extend only when needed via namespaced custom IDs.

## Edge Cases
- Multi-repo: maintain one hub with per-repo adapter bindings and dependency graph.
- Non-git prototype: use local artifacts and explicit acceptance criteria checkpoints.
- Team swarm: assign owner per phase and keep decision log in hub.
