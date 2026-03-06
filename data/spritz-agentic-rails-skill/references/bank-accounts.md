# Bank Accounts

Manage bank account destinations for off-ramp payments.

<!-- TODO: Replace placeholder endpoints/shapes with actual Spritz API once finalized -->

## Add Bank Account

```bash
POST /v1/bank-accounts
```

### Request

```json
{
  "name": "Primary checking",
  "routing_number": "021000021",
  "account_number": "123456789",
  "account_type": "checking"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Friendly label for this account |
| `routing_number` | string | Yes | 9-digit ABA routing number |
| `account_number` | string | Yes | Bank account number |
| `account_type` | string | Yes | `checking` or `savings` |

### Response

```json
{
  "id": "ba_xyz789",
  "name": "Primary checking",
  "routing_number_last4": "0021",
  "account_number_last4": "6789",
  "account_type": "checking",
  "status": "active",
  "created_at": "2026-02-24T10:00:00Z"
}
```

**Note:** Full account numbers are never returned in API responses. Only the last 4 digits are shown.

## List Bank Accounts

```bash
GET /v1/bank-accounts
```

Returns all saved bank accounts for the authenticated user.

## Get Bank Account

```bash
GET /v1/bank-accounts/{bank_account_id}
```

## Delete Bank Account

```bash
DELETE /v1/bank-accounts/{bank_account_id}
```

Cannot delete a bank account with in-flight payments.

---

## Validation Rules

Before adding a bank account, verify:

- **Routing number** — Must be exactly 9 digits. Validate with the user.
- **Account number** — Varies in length. Confirm with user.
- **Account type** — Must be `checking` or `savings`.
- **Name** — Use a descriptive label the user will recognize.

**Always confirm bank details with the user before saving.** Incorrect routing/account numbers can cause payments to fail or go to the wrong account.

---

## Security Notes

- Never log or display full account/routing numbers in responses
- Always show only last 4 digits when referencing bank accounts
- Confirm bank account details with user before creating
- Bank accounts can only be used by the authenticated API key
