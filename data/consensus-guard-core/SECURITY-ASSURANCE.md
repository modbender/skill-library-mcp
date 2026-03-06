# consensus-guard-core — Security Assurance Note

Status: Maintainer-authored review note
Scope: `consensus-guard-core` primitives, runtime boundaries, and safe deployment posture

## 1) Threat model

`consensus-guard-core` is a deterministic policy primitives library.

Designed to:
- aggregate votes deterministically
- compute bounded reputation updates
- generate idempotency keys
- resolve/read/write board artifacts through explicit helper calls
- resolve state path safely for local artifact storage

Not designed to:
- call external model providers
- require API credentials
- mutate global/system configuration

## 2) Network behavior

Expected behavior in shipped core primitives:
- no outbound network calls in policy/state-path helpers.

Dependency boundary:
- depends on `@consensus-tools/consensus-tools` for local storage/engine helpers.
- consumers should pin and review transitive dependencies as part of supply-chain policy.

## 3) Env vars and credentials

No API credentials required.

Path config env vars used by state-path resolution:
- `CONSENSUS_STATE_FILE`
- `CONSENSUS_STATE_ROOT`

Recommendation:
- run with minimal env allowlist and avoid exposing unrelated secrets.

## 4) Filesystem boundaries

Writes occur only when callers invoke write helpers.

Recommended setup:
- set `CONSENSUS_STATE_ROOT` to dedicated, non-privileged directory.
- run as non-root user.
- avoid system or secret directories for state root.

## 5) Production hardening profile

- non-root runtime user
- dedicated writable state directory only
- egress-deny by default where feasible
- lockfile pin + periodic transitive dependency audit
- test and verify in isolated environment prior to promotion

## 6) Verification checklist

- [ ] `npm test` passes in isolated environment
- [ ] state root points to dedicated safe path
- [ ] no unrelated sensitive env vars at runtime
- [ ] dependency versions pinned/reviewed
- [ ] consumers import stable package root API (`consensus-guard-core`), not internal paths

## 7) Scanner context

Automated scanners often flag stateful local-write policy libraries as “suspicious” due to filesystem capability and dependency trust boundaries. For this package, treat that as a runtime/dependency review prompt rather than evidence of malicious behavior.
