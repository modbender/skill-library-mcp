# consensus-deployment-guard — Security Assurance Note

Status: Maintainer-authored review note
Scope: `consensus-deployment-guard` package behavior and operational boundaries

## 1) Threat model (what this skill is / is not)

`consensus-deployment-guard` is a deterministic pre-deployment policy gate.

It is designed to:
- validate deployment inputs
- evaluate policy flags
- aggregate votes (internal deterministic personas or external votes)
- emit ALLOW/BLOCK/REQUIRE_REWRITE decisions
- write board decision artifacts to a configured state path

It is **not** designed to:
- fetch remote prompts/models
- call external LLM providers
- perform arbitrary system mutation outside configured state writes

## 2) Network behavior

Expected behavior of this package itself:
- No outbound network calls in guard decision path.

Dependency note:
- This skill depends on `consensus-guard-core` for aggregation/state helpers.
- `consensus-guard-core` should be reviewed/pinned as part of trust boundary.

Operational recommendation:
- Run in an environment with default-deny egress when possible.
- If egress must be allowed, monitor outbound destinations and alert on non-approved hosts.

## 3) Environment variables and credentials

This skill requires no API keys.

Path-related env vars used by dependency stack for state path resolution:
- `CONSENSUS_STATE_FILE`
- `CONSENSUS_STATE_ROOT`

Security recommendation:
- Do not expose unrelated sensitive env vars to this runtime.
- Use a minimal env allowlist in production execution contexts.

## 4) Filesystem boundaries

The skill writes board artifacts under configured state path.

Recommended safe setup:
- Set `CONSENSUS_STATE_ROOT` to a dedicated non-privileged directory.
- Prefer containerized execution with a scoped writable mount.
- Run as non-root user.

Do **not** point state path to:
- system config dirs (`/etc`, `/usr`, etc.)
- user secrets directories
- shared sensitive volumes

## 5) Recommended production profile

- Execution user: non-root service account
- FS permissions: write only to dedicated state directory
- Network policy: deny-by-default egress
- Runtime env: explicit allowlist
- Dependency policy: pin and periodically audit `consensus-guard-core` + lockfile
- CI gate: run `npm test` + schema/idempotency cases before promotion

## 6) Verification checklist (quick)

Before enabling in automation:
- [ ] `npm test` passes in isolated environment
- [ ] `CONSENSUS_STATE_ROOT` points to dedicated safe dir
- [ ] no sensitive env vars present at runtime
- [ ] dependency versions pinned and reviewed
- [ ] agent sandbox permissions constrained

## 7) Why scanners may still mark “suspicious”

This package is stateful and imports a shared core dependency. Automated scanners often flag these patterns by default when:
- transitive behavior is not fully inlined in the scanned package
- filesystem write capability is present

This should be interpreted as a prompt for dependency and runtime review, not automatic maliciousness.
