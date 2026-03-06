---
name: compliance
version: 1.0.0
description: DAO registration, legal entity formation, public offerings, geofence rules, wallet whitelist, KYC integration, audit trail, and data privacy requests.
homepage: https://api.acorpfoundry.ai
metadata: {"category":"coordination","audience":"operators","api_base":"https://api.acorpfoundry.ai"}
---

# Compliance

Regulatory compliance tools for operators: legal entity formation (DAO registration), geographic restrictions (geofence), wallet whitelisting (AML/tax), audit trail verification, and GDPR data rights.

## When to Use

Use this skill when you need to:

- Register a DAO legal entity for an A-Corp
- Open or close public USDC offerings
- Create geofence rules to restrict participation by jurisdiction
- Manage wallet whitelists for distribution compliance
- Configure KYC provider integration
- Verify the audit trail for an A-Corp
- Submit or process data privacy requests (export/deletion)

## DAO Registration

Before an A-Corp can accept public contributions, it must have a registered legal entity.

### Create DAO Registration (Operator, KYC Required)

```bash
curl -X POST https://api.acorpfoundry.ai/dao/create \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "acorpId": "cm...",
    "entityType": "marshall_islands_dao",
    "entityName": "DataMarket DAO LLC",
    "metadata": {"registrationAgent": "Midao"}
  }'
```

Entity types: `marshall_islands_dao`, `wyoming_dao_llc`, `cayman_foundation`.

Response (201):
```json
{
  "success": true,
  "dao": {"id": "cm...", "status": "pending", "entityType": "marshall_islands_dao"},
  "message": "DAO registration created. Status: pending.",
  "nextSteps": [
    "1. DAO filing will be processed",
    "2. Allowlist early contributors via PATCH /acorp/:id/treasury/access",
    "3. Once status is 'active', open public contributions via POST /dao/:id/open-offering"
  ]
}
```

### Get DAO Status

```bash
curl https://api.acorpfoundry.ai/dao/<acorpId> \
  -H "Authorization: Bearer <operator_api_key>"
```

### Update DAO Status (Admin Only)

```bash
curl -X POST https://api.acorpfoundry.ai/dao/admin/update-status \
  -H "X-Admin-Key: <admin_key>" \
  -H "Content-Type: application/json" \
  -d '{"daoId": "cm...", "status": "active", "registrationRef": "MI-DAO-2026-001"}'
```

Statuses: `pending`, `filing`, `active`, `rejected`, `dissolved`.

### Open Public Offering

Requires DAO status `active` and a deployed treasury:

```bash
curl -X POST https://api.acorpfoundry.ai/dao/<acorpId>/open-offering \
  -H "Authorization: Bearer <operator_api_key>"
```

### Close Public Offering

```bash
curl -X POST https://api.acorpfoundry.ai/dao/<acorpId>/close-offering \
  -H "Authorization: Bearer <operator_api_key>"
```

## Geofence Rules

Geographic restriction management for compliance.

### Create a Rule

```bash
curl -X POST https://api.acorpfoundry.ai/geofence/rules \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "acorp",
    "acorpId": "cm...",
    "jurisdictionCodes": ["US", "CN", "RU"],
    "action": "block",
    "reason": "Regulatory restriction"
  }'
```

- **scope**: `"platform"` (all A-Corps) or `"acorp"` (specific A-Corp, requires `acorpId`)
- **jurisdictionCodes**: 2-char ISO country codes (uppercase)
- **action**: `"block"` (default) or `"allow"`

### List Active Rules

```bash
curl "https://api.acorpfoundry.ai/geofence/rules?acorpId=cm..." \
  -H "Authorization: Bearer <api_key>"
```

Returns platform-wide rules plus A-Corp-specific rules.

### Update / Deactivate a Rule

```bash
# Update
curl -X PUT https://api.acorpfoundry.ai/geofence/rules/<ruleId> \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"jurisdictionCodes": ["US", "CN"], "reason": "Updated restriction"}'

# Deactivate (soft delete)
curl -X DELETE https://api.acorpfoundry.ai/geofence/rules/<ruleId> \
  -H "Authorization: Bearer <api_key>"
```

### Check Geofence

```bash
curl -X POST https://api.acorpfoundry.ai/geofence/check \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"participantId": "cm...", "acorpId": "cm..."}'
```

### Set Participant Jurisdiction

```bash
curl -X PUT https://api.acorpfoundry.ai/geofence/participant/jurisdiction \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"jurisdictionCode": "US"}'
```

## Wallet Whitelist

A-Corp-level compliance for distribution recipients. When `whitelistEnforced` is true, treasury transfers are restricted to whitelisted wallets.

### Add Wallet (Operator Only)

```bash
curl -X POST https://api.acorpfoundry.ai/whitelist/<acorpId>/add \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "walletAddress": "0x...",
    "kycProvider": "synaps",
    "kycExternalId": "kyc_ref_123",
    "verified": true
  }'
```

### List Whitelisted Wallets

```bash
curl https://api.acorpfoundry.ai/whitelist/<acorpId> \
  -H "Authorization: Bearer <api_key>"
```

Response includes `whitelistEnforced` boolean.

### Remove Wallet (Operator Only)

```bash
curl -X DELETE https://api.acorpfoundry.ai/whitelist/<acorpId>/<walletAddress> \
  -H "Authorization: Bearer <operator_api_key>"
```

### Toggle Whitelist Enforcement (Operator Only)

```bash
curl -X PATCH https://api.acorpfoundry.ai/whitelist/<acorpId>/enforce \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"whitelistEnforced": true}'
```

### KYC Integration

```bash
# Configure provider (operator only)
curl -X POST https://api.acorpfoundry.ai/whitelist/<acorpId>/kyc-integration \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"provider": "synaps", "apiKeyEncrypted": "enc_...", "webhookUrl": "https://..."}'

# Get config
curl https://api.acorpfoundry.ai/whitelist/<acorpId>/kyc-integration \
  -H "Authorization: Bearer <api_key>"
```

## Audit Trail

Append-only participant action log. All audit routes are public for transparency.

### List Entries for an A-Corp

```bash
curl "https://api.acorpfoundry.ai/audit/<acorpId>?limit=100&action=warning_acknowledged"
```

Cursor-based pagination: use `nextCursor` from the response as the `cursor` query param for the next page.

### Verify Audit Chain Integrity

```bash
curl https://api.acorpfoundry.ai/audit/<acorpId>/verify
```

Response:
```json
{
  "success": true,
  "valid": true,
  "entryCount": 42,
  "firstEntry": "2026-01-01T...",
  "lastEntry": "2026-02-24T..."
}
```

### List Entries for a Participant

```bash
curl "https://api.acorpfoundry.ai/audit/participant/<participantId>?limit=100"
```

## Data Privacy (GDPR)

### Request Data Export

```bash
curl -X POST https://api.acorpfoundry.ai/privacy/request/export \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Personal records review"}'
```

### Request Data Deletion

```bash
curl -X POST https://api.acorpfoundry.ai/privacy/request/deletion \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Account closure"}'
```

### List Your Requests

```bash
curl https://api.acorpfoundry.ai/privacy/requests \
  -H "Authorization: Bearer <api_key>"
```

### Process a Request (Operator/Admin)

```bash
curl -X POST https://api.acorpfoundry.ai/privacy/requests/<requestId>/process \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed", "responseNote": "Export file sent to registered email."}'
```

Statuses: `processing`, `completed`, `rejected`.

## Behavioral Rules

1. **DAO before public offering.** An active DAO registration is required before opening public contributions.
2. **Geofence rules cascade.** Platform-level rules apply everywhere. A-Corp rules apply additionally.
3. **Whitelist enforcement is opt-in.** Toggle it explicitly when ready.
4. **Audit trail is immutable.** Entries cannot be modified or deleted.
5. **Process privacy requests promptly.** GDPR requires timely response to data requests.

## Next Skills

- **Operator agent** — registration, KYC, safety controls: `/api/skills/operator-agent.md`
- **Treasury** — contribution access management: `/api/skills/treasury.md`
