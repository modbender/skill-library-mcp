# Mercury Payments Skill

## Overview
Pay invoices via Mercury bank API, notify Zeni (bookkeeper) and the vendor, and always attach the invoice PDF.

## Prerequisites
- Mercury API token (write access): `$MERCURY_API_TOKEN` or `pass show <vault-path>`
- Auth: `Authorization: Bearer <token>` (Basic auth also works: `token:` base64)
- Base URL: `https://api.mercury.com/api/v1`

## Accounts
Discover account IDs dynamically (do not hardcode organization-specific IDs):

```bash
curl -s -H "Authorization: Bearer $TOKEN" "https://api.mercury.com/api/v1/accounts"
```

Default payment account should be confirmed at payment time.

## Known Recipients
Keep recipient IDs in your own secure records or resolve by recipient name at runtime.

## Payment Flow

### 1. Get explicit approval
**NEVER send money without explicit approval from the authorized operator.** Present: amount, recipient, invoice #, account.

### 2. Download the invoice PDF
Find the invoice email, download the attachment to `/tmp/`.

### 3. Check for existing recipient
```bash
curl -s -H "Authorization: Bearer $TOKEN" "https://api.mercury.com/api/v1/recipients" | python3 -c "..."
```

### 4. Create recipient if needed
```bash
curl -s -X POST "https://api.mercury.com/api/v1/recipients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "...",
    "emails": ["..."],
    "defaultPaymentMethod": "ach",
    "electronicRoutingInfo": {
      "accountNumber": "...",
      "routingNumber": "...",
      "electronicAccountType": "businessChecking",
      "address": { "address1": "...", "city": "...", "region": "...", "postalCode": "...", "country": "US" }
    },
    "defaultAddress": { ... }
  }'
```

### 5. Send payment

**ACH payment:**
```bash
curl -s -X POST "https://api.mercury.com/api/v1/account/{accountId}/transactions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipientId": "...",
    "amount": 533.13,
    "paymentMethod": "ach",
    "note": "INV123 - Vendor - Period",
    "idempotencyKey": "unique-key-here"
  }'
```

**Domestic wire payment:**
```bash
curl -s -X POST "https://api.mercury.com/api/v1/account/{accountId}/transactions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipientId": "...",
    "amount": 1080.00,
    "paymentMethod": "domesticWire",
    "purpose": {"simple": {"category": "vendor", "additionalInfo": "Invoice TRC37332 TRACE Data"}},
    "note": "INV-001 - Vendor - Jan 2026",
    "idempotencyKey": "unique-key-here"
  }'
```

**Wire `purpose` is required.** Format: `{"simple": {"category": "<cat>", "additionalInfo": "<desc>"}}`
Categories: `employee`, `landlord`, `vendor`, `contractor`, `subsidiary`, `transferToMyExternalAccount`, `familyMemberOrFriend`, `forGoodsOrServices`, `angelInvestment`, `savingsOrInvestments`, `expenses`, `travel`, `other`

### 6. Email bookkeeper (always)
Send to your bookkeeping inbox (e.g., `bookkeeping@example.com`) with:
- Subject: `<Vendor> Invoice <number> — Paid`
- Body: amount, method, estimated delivery
- **Attach the invoice PDF**

### 7. Email vendor (always)
Reply in the existing email thread if possible. Include:
- Confirmation of payment with amount
- **Attach the invoice PDF**
- Estimated delivery date

## Internal Transfers (Between Mercury Accounts)

```bash
curl -s -X POST "https://api.mercury.com/api/v1/transfer" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sourceAccountId": "YOUR_SOURCE_ACCOUNT_ID",
    "destinationAccountId": "YOUR_DESTINATION_ACCOUNT_ID",
    "amount": 465.00,
    "idempotencyKey": "unique-key-here"
  }'
```

Required fields: `sourceAccountId`, `destinationAccountId`, `amount`, `idempotencyKey`.
Transfers post instantly. Response contains both `creditTransaction` and `debitTransaction`.

## Querying Transactions
```bash
# Recent (default ~30 days)
curl -s -H "Authorization: Bearer $TOKEN" "https://api.mercury.com/api/v1/account/{id}/transactions?limit=500"

# Date range (goes further back)
curl -s -H "Authorization: Bearer $TOKEN" "https://api.mercury.com/api/v1/account/{id}/transactions?start=2025-12-01&end=2026-01-18&limit=500"
```
Note: Without date params, API only returns ~30 days. Use `start`/`end` to go further back.

## Idempotency Keys
Use descriptive keys: `{vendor}-{invoice}-{period}` (e.g., `finra-trc37332-nov2025`)

## Checklist
- [ ] Explicit approval received from authorized operator
- [ ] Invoice PDF downloaded
- [ ] Recipient exists (or created)
- [ ] Payment sent with correct amount, method, and note
- [ ] Zeni emailed with invoice attached
- [ ] Vendor emailed with invoice attached
- [ ] Payment logged in daily memory file
