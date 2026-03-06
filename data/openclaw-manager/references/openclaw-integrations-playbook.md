# OpenClaw Integrations Playbook

This playbook covers integration onboarding for `email` and `calendar`.

## Integration Status Vocabulary
- `configured`
- `pending_credentials`
- `blocked`

## Email (Gmail) Path
Reference: https://docs.openclaw.ai/integrations/gmail

Checklist:
1. Confirm OAuth/API credentials are provisioned for active environment.
2. Store secrets in env/provider secret manager.
3. Validate account authorization and token refresh behavior.
4. Run a smoke test (fetch inbox metadata only).
5. Verify logs avoid sensitive payload/token leakage.

Blockers:
- OAuth/client credentials missing
- refresh token flow failing
- auth errors not observable in logs

## Calendar (Google Calendar) Path
Reference: https://docs.openclaw.ai/integrations/google-calendar

Checklist:
1. Confirm calendar API credentials are provisioned for active environment.
2. Store credentials in env/provider secret manager.
3. Validate authorization scope minimums.
4. Run a smoke test (list upcoming events metadata only).
5. Verify logs avoid sensitive payload/token leakage.

Blockers:
- missing API access/scope
- failed refresh/consent flow
- unbounded privileged scopes

## Recording Requirements
For each selected integration, record in the ops ledger:
- status
- credentials source (name only)
- smoke-test result
- blockers and owner
