# Access & Credentials Requirements

This skill is instruction-only. It does not include connectors or secrets.

## Runtime access prerequisites
The hosting agent/platform must provide one of:
1. Native Home Assistant connector/API integration, or
2. Browser relay access to an authenticated Home Assistant session, or
3. A platform-approved secure token flow.

## Credential handling policy
- Never ask users to paste long-lived secrets in public/group chats.
- Store credentials only in platform secret storage (never in skill files).
- Use least-privilege scopes/tokens where possible.
- Mask/redact sensitive values in output.
- Rotate/revoke tokens immediately if exposure is suspected.

## Operational boundary
Without runtime access, the skill provides planning/audit guidance only.
With runtime access, the skill still remains read-first and approval-gated for writes.

## Verification checklist
- Access path confirmed (connector/browser/token)
- Secret storage method confirmed
- Environment is private and approved for operational actions
- User confirmed write policy and risk tiering behavior
