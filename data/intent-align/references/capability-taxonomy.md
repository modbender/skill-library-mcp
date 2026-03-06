# Capability Taxonomy

Use canonical capability IDs in `capability_matrix.required|available|missing`.

## Core IDs
- `intent.capture`
- `intent.lint`
- `intent.clarify`
- `plan.phase`
- `research.external`
- `context.retrieve`
- `repo.local.read`
- `repo.local.write`
- `repo.github.read`
- `repo.github.write`
- `tracker.read`
- `tracker.write`
- `verify.run`
- `report.emit`
- `user.checkin`

## Extension Pattern
If a needed capability is not covered by core IDs, define a namespaced custom ID:
- `x.<agent_or_team>.<capability>`

Examples:
- `x.openclaw.market.regime_detect`
- `x.teamalpha.simulator.batch_run`

## Rules
- Prefer core IDs whenever possible.
- Use custom IDs only for truly missing capabilities.
- Keep custom IDs stable within a hub run and across related runs.
