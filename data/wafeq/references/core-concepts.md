# Wafeq API - Core Concepts & Guides

## Base URL

```
https://api.wafeq.com/v1/
```

---

## Authentication

Two supported methods:

### 1. Private Key (API Key) - Recommended for Own Organization

- **Header:** `Authorization: Api-Key $WAFEQ_API_KEY`
- **Obtain keys from:** `https://app.wafeq.com/c/api-keys`

```bash
curl --location --request GET 'https://api.wafeq.com/v1/organization/' \
  --header 'Authorization: Api-Key $WAFEQ_API_KEY'
```

### 2. OAuth2 - Recommended for Third-Party Integrations

- **Header:** `Authorization: Bearer <access_token>`
- Setup: Contact Wafeq support to get `client_id` and `client_secret`
- Demo apps: Available at oauth2-client-examples GitLab repository

```bash
curl --location --request GET 'https://api.wafeq.com/v1/organization/' \
  --header 'Authorization: Bearer <access_token>'
```

---

## Authorization (OAuth 2.0)

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `https://app.wafeq.com/oauth/authorize/` | GET | User authorization request |
| `https://app.wafeq.com/oauth/token/` | POST | Token exchange and refresh |
| `https://app.wafeq.com/oauth/token/revoke/` | POST | Token revocation |

### Authorization Code Flow Parameters

**Authorization Request (GET):**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `client_id` | Yes | Application identifier |
| `response_type` | Yes | Must be `"code"` |
| `redirect_uri` | Yes | Callback URL, must match registered URI exactly |
| `scope` | Yes | Space-separated permission list |
| `state` | Recommended | CSRF protection parameter |

**PKCE Extension (optional):**

| Parameter | Description |
|-----------|-------------|
| `code_challenge_method` | Set to `"S256"` |
| `code_challenge` | SHA256-hashed code verifier (43-128 characters) |

### Token Lifecycle

| Token | Validity |
|-------|----------|
| Access token | 30 days |
| Refresh token | 6 months |
| Authorization code | 1 hour |

**Token Response Fields:** `access_token`, `refresh_token`, `token_type` (always "Bearer"), `expires_in`

### Token Refresh

POST to token endpoint with:
- `grant_type`: `"refresh_token"`
- `refresh_token`: Original token from authorization
- `client_id`: Required for PKCE implementations
- **Header:** `Authorization: Basic <base64(client_id:client_secret)>`
- **Content-Type:** `application/x-www-form-urlencoded`

### Token Revocation

POST to revoke endpoint with:
- `client_id`, `client_secret`, `token`, `token_type_hint` (`access_token` or `refresh_token`)

### Permission Scopes (29 total)

**Core Access:**
- `basic` - Organization information
- `users` - User list access
- `bulk_invoices` - Bulk invoice sending

**Financial Data (read/write pairs):**
- Chart of accounts, bank accounts, tax rates, invoices, expenses, bills, journals, payments
- `reports` - Read-only access

**Entity Management:**
- Beneficiaries, contacts, employees (each with read/write variants)

**Payroll:**
- `payroll.read` and `payroll.write`

---

## Idempotency

- **Header:** `X-Wafeq-Idempotency-Key`
- **Format:** UUID v4 (valid UUID required; invalid format returns `400 Bad Request`)
- **Applies to:** POST, PUT, PATCH, DELETE requests
- **Cache Duration:** 1 hour - reusing the same key for identical requests within 1 hour returns the cached original response
- **Replay Indicator:** Response includes `X-Wafeq-Idempotent-Replayed: true` header for cached responses
- **Scope:** Key operates at the specific HTTP method + endpoint level

**Best Practices:**
- Generate unique UUIDs for each distinct operation
- Maintain idempotency key records alongside request tracking data
- Retain the same key when retrying failed requests

---

## Error Handling

- Failed requests return HTTP status codes >= 300
- Error responses include status code and error message text
- Response validation should check for successful status before parsing JSON

---

## Pagination

- List endpoints return paginated results
- Response structure includes paginated results with object details

---

## Rate Limits

Not explicitly documented in core reference pages. Use idempotency keys and reasonable request pacing.

---

## Quickstart Guide: Send Your First E-Invoice

### Endpoint

```
POST https://api.wafeq.com/v1/api-invoices/bulk_send/
```

### Authentication

```
Authorization: Api-Key $WAFEQ_API_KEY
Content-Type: application/json
```

### Request Body (array of invoices)

**Invoice-level required fields:**
- `reference` - Unique identifier
- `invoice_number` - Invoice ID
- `invoice_date` - Format: `YYYY-MM-DD`
- `currency` - Currency code (e.g., `SAR`)
- `paid_through_account` - Account ID receiving payment
- `language` - Language preference
- `tax_amount_type` - Tax configuration (e.g., `TAX_INCLUSIVE`)
- `contact` - Recipient details (name, address, email)
- `channels` - Distribution method configuration
- `line_items` - Product/service details

**Line item fields:**
- `name`, `description`, `quantity`, `price`
- `account` - Revenue categorization for P&L
- `tax_rate` - Applicable tax rate ID

**Channel configuration:**
- `medium`: `"email"`
- Email data: `subject`, `message`, recipient addresses (`to`/`cc`/`bcc`)

### Success Response

```json
{
  "queued": 1
}
```

### Prerequisite API Calls

- **List accounts:** Filter by `is_payment_enabled` for payment accounts
- **List tax rates:** Retrieve applicable tax configurations

---

## Invoice Creation Example (Detailed Walkthrough)

### Step 1: Create a Contact

```
POST https://api.wafeq.com/v1/contacts/
Authorization: Api-Key $WAFEQ_API_KEY
```

```json
{
  "name": "Acme Trading LLC",
  "email": "billing@acme.example",
  "phone": "+971500000000"
}
```

### Step 2: List Accounts

```
GET https://api.wafeq.com/v1/accounts/
Authorization: Api-Key $WAFEQ_API_KEY
```

Filter by code (e.g., `"4000"`), exact name match, or classification type (`revenue`/`asset`).

### Step 3: Create Invoice

```
POST https://api.wafeq.com/v1/invoices/
Authorization: Api-Key $WAFEQ_API_KEY
X-Wafeq-Idempotency-Key: <uuid-v4>
```

```json
{
  "contact": "cnt_7c2f2a1f-1f7e-4c2f-9f8a-1c2a0b9e3d11",
  "currency": "AED",
  "invoice_date": "2025-10-30",
  "invoice_due_date": "2025-11-14",
  "invoice_number": "INV-1001",
  "notes": "Thanks for your business!",
  "line_items": [
    {
      "account": "acc_9a1c7f3b-2d4e-4a53-9a3b-b5f7e2c4e9d0",
      "description": "Consulting services",
      "quantity": 10,
      "unit_amount": 250,
      "tax_rate": null
    }
  ]
}
```

### Step 4: Record Payment

```
POST https://api.wafeq.com/v1/payments/
Authorization: Api-Key $WAFEQ_API_KEY
X-Wafeq-Idempotency-Key: <uuid-v4>
```

```json
{
  "amount": 2500.0,
  "contact": "cnt_7c2f2a1f-1f7e-4c2f-9f8a-1c2a0b9e3d11",
  "currency": "AED",
  "date": "2025-10-31",
  "paid_through_account": "acc_bank_123",
  "reference": "Bank transfer FT-92831",
  "invoice_payments": [
    {
      "invoice": "inv_2af9a6e1-2c10-4b2a-b111-0d7b2f2f0e9a",
      "amount": 2500.0,
      "amount_to_pcy": 2500.0
    }
  ]
}
```

**Key Notes:**
- Use idempotency keys (UUID v4) for all POST operations
- Contact creation must precede invoice creation
- Revenue account retrieval supports flexible filtering

---

## Use Case: B2B E-Invoicing

- Send compliant B2B e-invoices via the e-invoicing API
- `tax_registration_number` field is optional on the Contact object (include if customer has one)
- See Contact object in API reference for full field details

---

## Use Case: B2C E-Invoicing

- Send compliant B2C e-invoices through API integration
- Simplified invoices for consumer transactions
- Call the API from your application code when billing occurs

---

## Use Case: E-Commerce

- Invoke the API at **order dispatch** time
- Works with platforms: Salla, Shopify, Zid, WooCommerce, WordPress, or custom-built stores
- **Important:** Provide a unique `invoice_number` for each transaction
  - Ensures invoice uniqueness
  - Enables subsequent retrieval (customer resends, historical reference)

---

## Use Case: Expense Management

### Integration Overview

Push approved expenses from expense management software (e.g., Expensico) into Wafeq for accounting.

### Relevant API Endpoints

1. **Authorization** - OAuth connect and store access tokens
2. **Accounts List** - `GET /v1/accounts/` filtered on `EXPENSE` classification
3. **Expenses Create** - `POST /v1/expenses/` for individual approved expenses
4. **Bank Statement Transactions** - Create statement transactions for reconciliation
5. **Ledger Bank Transactions** - Record money movements between accounts

### Setup Workflow (6 Steps)

1. OAuth authentication and token storage
2. Retrieve expense category accounts filtered by `EXPENSE` classification
3. Map retrieved accounts to software expense categories
4. Select or create a `CURRENT_LIABILITY` account for employee claims (`is_payment_enabled: true`)
5. Select or create a `CURRENT_ASSET` account for card balances (`is_payment_enabled: true`)
6. Select or create a bank account representing the funding source

### Syncing Expenses

- Use `reference` field as unique identifier to prevent duplicates
- Set `paid_through_account` based on transaction type:
  - **Employee reimbursement:** Use the Employee Claims (CURRENT_LIABILITY) account
  - **Corporate card:** Use the Employees Balance (CURRENT_ASSET) account

### Bank Transactions

Two transaction types:
- **Reimbursements:** Connected to Employee Claims account
- **Card Funding:** Connected to Employees Balance account

### Historical Sync

- Users select date ranges for previously approved expense reports
- Check for existing entries by `reference` before creation to avoid duplicates
