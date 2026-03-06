# consensus-permission-escalation-guard

Pre-execution governance for IAM and privilege escalation requests.

`consensus-permission-escalation-guard` evaluates access-change proposals (grant, scope expansion, role assumption) and returns:

- `ALLOW`
- `BLOCK`
- `REQUIRE_REWRITE`

## Ideal use cases

- temporary admin elevation
- service-account scope expansion
- break-glass access requests
- production IAM permission changes

## Core capabilities

- strict schema validation (Ajv 2020)
- deterministic policy flags (hard-block + rewrite)
- persona mode + external-agent vote mode
- idempotent retries and stable replay
- board-native audit artifacts

## Example policy checks

Hard block examples:
- wildcard permissions
- missing ticket/justification (when required)
- break-glass without incident reference
- separation-of-duties conflicts

Rewrite examples:
- weak justification
- temporary duration too long
- production change without explicit human confirmation

## Environment + state path

This package reads state-path configuration from:
- `CONSENSUS_STATE_FILE`
- `CONSENSUS_STATE_ROOT`

Use a dedicated non-privileged directory for state; do not point state paths at system or secrets directories.

## Quick start

```bash
npm i
node --import tsx run.js --input ./examples/input.json
```

## Test

```bash
npm test
```

## Notes

- Built on `consensus-guard-core` for shared deterministic semantics
- Designed for auditability, replayability, and minimal policy drift across guard domains
