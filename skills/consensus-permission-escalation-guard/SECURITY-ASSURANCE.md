# consensus-permission-escalation-guard — Security Assurance Note

Status: Maintainer-authored review note
Scope: `consensus-permission-escalation-guard` package behavior and operational boundaries

## 1) Threat model

This skill is a deterministic pre-execution policy gate for IAM/permission escalation requests.

It is designed to:
- validate escalation inputs against strict schema
- evaluate hard-block/rewrite risk flags
- aggregate votes deterministically
- emit ALLOW/BLOCK/REQUIRE_REWRITE decisions
- write decision artifacts to configured state path

It is not designed to:
- call external model providers
- read unrelated host files
- mutate global system configuration

## 2) Network behavior

Expected behavior in shipped runtime path:
- no outbound network calls in guard decision logic.

Dependency boundary:
- imports `consensus-guard-core` helper functions for state/artifact operations.
- consumers should review/pin `consensus-guard-core` as part of trust boundary.

## 3) Env vars and credentials

No API credentials required.

Path configuration env vars used by dependency stack:
- `CONSENSUS_STATE_FILE`
- `CONSENSUS_STATE_ROOT`

Recommendation:
- run with minimal env allowlist and avoid exposing unrelated secrets.

## 4) Filesystem boundaries

Writes are expected to consensus board/state artifact path.

Recommendation:
- set `CONSENSUS_STATE_ROOT` to dedicated non-privileged directory.
- run as non-root user.
- avoid sensitive/system directories for state root.

## 5) Production hardening profile

- non-root runtime user
- dedicated writable state directory only
- default-deny outbound egress where feasible
- dependency pin + periodic lockfile audit
- run tests in isolated environment prior to promotion

## 6) Verification checklist

- [ ] `npm test` passes in isolated environment
- [ ] state root points to dedicated safe directory
- [ ] no unrelated sensitive env vars in runtime
- [ ] dependency versions reviewed and pinned
- [ ] agent filesystem permissions constrained

## 7) Scanner context

Stateful policy engines that write artifacts and import shared helpers are commonly flagged as “suspicious” by automated scanners. In this package, that flag should be treated as a dependency/runtime boundary review prompt, not evidence of malicious behavior.
