# consensus-agent-action-guard

Pre-execution governance for high-risk autonomous actions.

`consensus-agent-action-guard` evaluates a proposed agent action *before* side effects occur and returns a deterministic verdict:

- `ALLOW`
- `BLOCK`
- `REQUIRE_REWRITE`

This package is designed for real automation paths where a bad action is expensive or irreversible.

## Where it fits

Use this guard right before execution in agent pipelines, tool routers, and workflow engines.

Typical protected actions:
- destructive operations (`delete`, bulk mutation, irreversible toggles)
- outbound communication/posting
- privileged tool usage
- external side-effecting operations

## Decision model

The guard combines:
1. strict schema validation,
2. hard-block flag detection,
3. persona-weighted voting (or `external_agent` votes),
4. deterministic aggregation,
5. idempotent replay via request hashing,
6. board-native artifact writes.

## Input highlights

Top-level contract includes:
- `board_id`
- `proposed_action` (`action_type`, `target`, `summary`, `irreversible`, `external_side_effect`, `risk_level`)
- optional `constraints`
- optional `persona_set_id`
- `mode`: `persona | external_agent`

## Output highlights

- `final_decision`
- vote breakdown + weighted aggregation
- required follow-up actions
- `board_writes[]` references for audit trail

## Why teams adopt it

- consistent behavior across retries
- explicit governance under pressure
- easier incident forensics through artifact history
- interoperable semantics with the broader Consensus guard family

## Quick start

```bash
npm i
node --import tsx run.js --input ./examples/input.json
```

## Test

```bash
npm test
```

## Related docs

- `SKILL.md` for skill/runtime integration
- `AI-SELF-IMPROVEMENT.md` for reliability iteration loops
