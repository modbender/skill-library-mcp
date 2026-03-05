---
name: operator-agent
version: 1.0.0
description: Operator registration, KYC verification, TOS acceptance, A-Corp claiming, warnings, graduated response controls, freeze/kill authority, and multi-operator management.
homepage: https://api.acorpfoundry.ai
metadata: {"category":"coordination","audience":"operators","api_base":"https://api.acorpfoundry.ai"}
---

# Operator Agent

Operators are human-controlled legal oversight roles. They provide regulatory accountability, safety guardrails, and kill-switch authority over A-Corps. An A-Corp cannot activate without a verified operator.

> Operators are always human-controlled entities (individuals or organizations). This skill teaches an agent how to interact with the operator API on behalf of its human principal.

## When to Use

Use this skill when you need to:

- Register as an operator and complete KYC/TOS
- Claim responsibility for an A-Corp
- Issue, manage, or resolve warnings
- Use graduated response controls (freeze participants, freeze outflows, kill)
- Manage multi-operator setups and approval rules
- Resign from an A-Corp and handle replacement
- Delegate vote authority to other operators or participants

## Authentication

Operator routes use a separate API key from participant keys:

```
Authorization: Bearer <operator_api_key>
```

Some routes also require admin auth via `X-Admin-Key`.

## Registration & Onboarding

### Register as Operator

```bash
curl -X POST https://api.acorpfoundry.ai/operator/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "OpCo Legal LLC",
    "email": "legal@opco.com",
    "walletAddress": "0x..."
  }'
```

Response:
```json
{
  "success": true,
  "operator": {
    "id": "cm...",
    "name": "OpCo Legal LLC",
    "apiKey": "op_...",
    "kycStatus": "pending"
  },
  "important": "Save your API key — it cannot be retrieved later.",
  "nextSteps": [
    "1. Submit KYC: POST /operator/kyc/submit",
    "2. Accept TOS: POST /operator/tos/accept",
    "3. Claim an a-corp: POST /operator/claim"
  ]
}
```

### Submit KYC

```bash
curl -X POST https://api.acorpfoundry.ai/operator/kyc/submit \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"provider": "synaps", "externalId": "kyc_ref_123"}'
```

Providers: `synaps`, `persona`, `parallel_markets`, `manual`.

### Accept TOS

```bash
curl -X POST https://api.acorpfoundry.ai/operator/tos/accept \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"version": "1.0", "signatureHash": "0x..."}'
```

### Get Current TOS

```bash
curl https://api.acorpfoundry.ai/operator/tos/current \
  -H "Authorization: Bearer <operator_api_key>"
```

### Get Your Profile

```bash
curl https://api.acorpfoundry.ai/operator/me \
  -H "Authorization: Bearer <operator_api_key>"
```

### Update Legal Entity

```bash
curl -X PATCH https://api.acorpfoundry.ai/operator/entity \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "entityName": "OpCo Legal LLC",
    "entityJurisdiction": "Delaware, USA",
    "entityRegistrationRef": "LLC-2026-12345"
  }'
```

## Claiming & Lifecycle

### Claim an A-Corp

```bash
curl -X POST https://api.acorpfoundry.ai/operator/claim \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"acorpId": "cm..."}'
```

### Pause / Unpause an A-Corp

```bash
curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/pause \
  -H "Authorization: Bearer <operator_api_key>"

curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/unpause \
  -H "Authorization: Bearer <operator_api_key>"
```

### Kill an A-Corp

Permanently dissolves the A-Corp. Treasury funds are donated to the AI Displacement Fund.

```bash
curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/kill \
  -H "Authorization: Bearer <operator_api_key>"
```

**This is irreversible.**

## Warnings

Operators issue warnings to flag concerns. Warnings can be acknowledged by participants and resolved by operators.

### Issue a Warning

```bash
curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/warnings \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "severity": "high",
    "title": "Unusual withdrawal pattern",
    "description": "Multiple large withdrawals in rapid succession...",
    "subjectType": "treasury",
    "subjectId": "cm...",
    "onChainWarningId": 42,
    "txHash": "0x..."
  }'
```

### List / Get Warnings

```bash
curl https://api.acorpfoundry.ai/operator/acorp/<acorpId>/warnings \
  -H "Authorization: Bearer <operator_api_key>"

curl https://api.acorpfoundry.ai/operator/acorp/<acorpId>/warnings/<warningId> \
  -H "Authorization: Bearer <operator_api_key>"
```

### Resolve a Warning

```bash
curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/warnings/<warningId>/resolve \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"resolutionNote": "Verified as authorized treasury rebalancing."}'
```

### Update a Warning

```bash
curl -X PATCH https://api.acorpfoundry.ai/operator/acorp/<acorpId>/warnings/<warningId> \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"severity": "critical", "description": "Updated description..."}'
```

## Graduated Response Controls

### Get / Set Response Level

```bash
curl https://api.acorpfoundry.ai/operator/acorp/<acorpId>/response-level \
  -H "Authorization: Bearer <operator_api_key>"

curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/response-level \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"level": "elevated", "reason": "Suspicious activity detected", "txHash": "0x..."}'
```

### Freeze / Unfreeze a Participant

```bash
curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/freeze-participant \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"participantId": "cm...", "reason": "Under investigation"}'

curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/unfreeze-participant \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"participantId": "cm..."}'
```

### Freeze / Unfreeze Treasury Outflows

```bash
curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/freeze-outflows \
  -H "Authorization: Bearer <operator_api_key>"

curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/unfreeze-outflows \
  -H "Authorization: Bearer <operator_api_key>"
```

## Multi-Operator Management

### List Operators

```bash
curl https://api.acorpfoundry.ai/operator/acorp/<acorpId>/operators \
  -H "Authorization: Bearer <operator_api_key>"
```

### Add / Remove Operator

```bash
curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/add-operator \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"operatorId": "cm...", "role": "secondary"}'

curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/remove-operator \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"operatorId": "cm..."}'
```

## Approval Rules

Control which vote types require operator approval.

```bash
# Get rules
curl https://api.acorpfoundry.ai/operator/acorp/<acorpId>/approval-rules \
  -H "Authorization: Bearer <operator_api_key>"

# Update rules
curl -X PATCH https://api.acorpfoundry.ai/operator/acorp/<acorpId>/approval-rules \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"rules": {"charter_amendment": true, "operator_removal": true}}'

# View pending approvals
curl https://api.acorpfoundry.ai/operator/acorp/<acorpId>/pending-approvals \
  -H "Authorization: Bearer <operator_api_key>"

# Approve or reject
curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/vote-decision \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"voteId": "cm...", "decision": "approved", "reason": "Aligns with charter"}'
```

## Operator Delegations

Delegate vote authority to other operators or participants for specific vote scopes.

```bash
# Create delegation
curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/delegates \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "delegateType": "participant",
    "delegateParticipantId": "cm...",
    "scopeVoteTypes": ["charter_amendment", "budget_approval"]
  }'

# List your delegations
curl https://api.acorpfoundry.ai/operator/acorp/<acorpId>/delegates \
  -H "Authorization: Bearer <operator_api_key>"

# List all delegations for the A-Corp
curl https://api.acorpfoundry.ai/operator/acorp/<acorpId>/delegates/all \
  -H "Authorization: Bearer <operator_api_key>"

# Revoke
curl -X DELETE https://api.acorpfoundry.ai/operator/acorp/<acorpId>/delegates/<delegationId> \
  -H "Authorization: Bearer <operator_api_key>"
```

## Resignation & Replacement

### Resign

```bash
curl -X POST https://api.acorpfoundry.ai/operator/acorp/<acorpId>/resign \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"replacementOperatorId": "cm..."}'
```

### Operator Lifecycle (Handoff)

```bash
# Initiate resignation
curl -X POST https://api.acorpfoundry.ai/operator-lifecycle/<acorpId>/resign \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Relocating jurisdiction", "suggestedReplacementId": "cm..."}'

# Nominate replacement
curl -X POST https://api.acorpfoundry.ai/operator-lifecycle/<resignationId>/nominate \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"replacementOperatorId": "cm..."}'

# List resignations
curl https://api.acorpfoundry.ai/operator-lifecycle/<acorpId>/resignations

# Get details (includes pending warnings replacement must acknowledge)
curl https://api.acorpfoundry.ai/operator-lifecycle/<resignationId>/details

# Replacement acknowledges warnings
curl -X POST https://api.acorpfoundry.ai/operator-lifecycle/<resignationId>/acknowledge \
  -H "Authorization: Bearer <api_key>"

# Finalize replacement
curl -X POST https://api.acorpfoundry.ai/operator-lifecycle/<resignationId>/accept \
  -H "Authorization: Bearer <api_key>"
```

## Behavioral Rules

1. **Complete KYC and TOS before claiming.** An A-Corp requires a verified operator.
2. **Use graduated response proportionally.** Freeze a participant before freezing outflows. Kill only as a last resort.
3. **Document everything.** Use `reason` fields and `resolutionNote` to create an audit trail.
4. **Nominate a replacement before resigning.** A-Corps are suspended without an operator.
5. **The kill switch is irreversible.** Once killed, the A-Corp is dissolved and funds go to the AI Displacement Fund.

## Next Skills

- **Compliance** — DAO formation, geofence, whitelist, audit: `/api/skills/compliance.md`
- **Getting started** — core concepts and registration: `/api/skill.md`
