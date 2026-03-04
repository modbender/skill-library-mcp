# Ops Checklist (OpenClaw ↔ ACP)

## Before go-live

- [ ] `scripts/smoke_test.sh` passes
- [ ] control-plane `/v2/version` returns 200
- [ ] ACP service `/v2/version` returns 200
- [ ] proof issue (`/v3/onboarding/proofs/issue`) returns 201
- [ ] setup-url issue (`/v3/onboarding/setup-url/issue`) returns 201
- [ ] offering execute URL is configured for paid path
- [ ] one buyer machine completed runner setup + login once

## Real-user test

1. OpenClaw installs skill from ClawHub
2. `scripts/preflight.sh`
3. If `RUNNER_NOT_READY`, run `scripts/setup_runner.sh` and login once
4. `scripts/publish.sh --title ... --body ...`
5. Verify deliverable has `published_url`
6. Verify ACP job appears as completed in marketplace records

## Incident quick actions

- `RUNNER_NOT_READY`: issue setup_url, run setup/login
- `AUTH_EXPIRED`: run thin-runner login again
- `ATTESTATION_ALREADY_USED`: ensure fresh `/v1/local/identity` for each job
- `PUBLISH_CONFIRM_TIMEOUT`: retry with new idempotency key
