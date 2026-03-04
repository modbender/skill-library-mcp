# OpenClaw Security Checklist

Use this checklist before considering deployment complete.

## Gate 1: Secrets Profile Validation (Mandatory)
Fail conditions:
- missing required keys for active profile
- placeholder values
- duplicate/malformed env keys
- weak gateway/setup tokens

Pass criteria:
- `scripts/validate_openclaw_env.py` exits 0 for active profile
- required model/provider alternatives are satisfied

## Gate 2: Network and Exposure Boundaries (Mandatory)
Fail conditions:
- public exposure without gateway auth token
- unnecessary open ports/routes
- debug/admin endpoints accessible from public internet

Pass criteria:
- TLS enforced for public exposure
- ingress routes scoped to required surfaces
- private mode uses restricted network boundaries

## Gate 3: Channel and Integration Auth Boundaries (Mandatory)
Fail conditions:
- channel/integration credentials stored in plaintext config committed to git
- missing signature/token checks where supported
- auth failure logs leak sensitive payloads

Pass criteria:
- channel + integration credentials sourced from secret manager/env
- smoke tests confirm authenticated message/event path

## Gate 4: Runtime and Persistence Safety (Mandatory)
Fail conditions:
- no persistent state configuration where required
- restart corrupts state/memory
- backups unencrypted or broadly accessible

Pass criteria:
- persistent path and permissions validated
- restart behavior tested and documented
- backup controls documented

## Gate 5: Incident Readiness (Mandatory)
Fail conditions:
- rollback path missing or owner undefined
- token revocation flow undefined
- no operator runbook for common outages

Pass criteria:
- rollback, revocation, and escalation path documented
- on-call owner/date captured in ops ledger

## Gate 6: Supply Chain and Patch Posture (Mandatory)
Fail conditions:
- untracked runtime image/dependency versions
- no policy for critical vulnerability updates

Pass criteria:
- deployment artifact version tracked
- critical vulnerability patch/redeploy process documented

## Gate 7: Ops Ledger Completeness (Mandatory)
Fail conditions:
- missing required ledger events (`scope_lock`, `predeploy_validation`, `deploy_complete`, `security_gate`, `handover`)
- missing required metadata fields for latest run

Pass criteria:
- ledger entries exist for all mandatory events
- blockers and next actions are recorded with owner/date

## Go/No-Go Rule
Production go-live is blocked unless **all mandatory gates pass**.
