# Wafeq API Reference: Accounts, Banking & Contacts

> Base URL: `https://api.wafeq.com/v1`
> Authentication: `Authorization: Api-Key {your_api_key}`
> Optional Idempotency: `X-Wafeq-Idempotency-Key: {uuid}` (POST/PUT/PATCH/DELETE)
> Response header `X-Wafeq-Idempotent-Replayed` indicates cached response.

---

## Table of Contents

1. [Accounts](#accounts)
2. [Bank Accounts](#bank-accounts)
3. [Bank Ledger Transactions](#bank-ledger-transactions)
4. [Bank Statement Transactions](#bank-statement-transactions)
5. [Contacts](#contacts)
6. [Beneficiaries](#beneficiaries)

---

## Accounts

### Account Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | string | - | Yes | Unique identifier |
| `account_code` | string | Yes | No | Unique code identifying this account |
| `name_en` | string | Yes | No | Account name in English |
| `name_ar` | string | No | No | Account name in Arabic (default: "") |
| `account_type` | AccountTypeEnum | No | No | Specific account category (44+ types) |
| `classification` | ClassificationEnum | Yes | No | REVENUE, EXPENSE, ASSET, LIABILITY, EQUITY |
| `sub_classification` | SubClassificationEnum | Yes | No | See enum values below |
| `is_posting` | boolean | No | No | Whether account can be used for posting |
| `is_payment_enabled` | boolean | Yes | No | Payment capability flag |
| `is_locked` | boolean | - | Yes | Modification restriction status |
| `is_system` | boolean | - | Yes | System-generated account indicator |
| `parent` | string or null | No | No | Parent account ID for sub-accounts |
| `created_ts` | datetime | - | Yes | UTC creation timestamp |
| `modified_ts` | datetime | - | Yes | UTC last modification timestamp |

**ClassificationEnum:** `REVENUE`, `EXPENSE`, `ASSET`, `LIABILITY`, `EQUITY`

**SubClassificationEnum:** `INCOME`, `COGS`, `OPERATING_EXPENSE`, `OTHER_INCOME`, `NON_OPERATING_EXPENSE`, `CASH_EQUIVALENTS`, `CURRENT_ASSET`, `NON_CURRENT_ASSET`, `FIXED_ASSET`, `CURRENT_LIABILITY`, `NON_CURRENT_LIABILITY`, `PAID_IN_CAPITAL`, `RETAINED_EARNINGS`, `ACCUMULATED_OTHER_COMPREHENSIVE_INCOME`, `TREASURY_STOCK`, `OWNERS_EQUITY`, `OPENING_BALANCE_EQUITY`

**AccountTypeEnum (44+ values):** `ACCOUNTS_RECEIVABLE`, `CASH_EQUIVALENTS`, `INVENTORY`, `PROPERTY_PLANT_AND_EQUIPMENT`, `ACCOUNTS_PAYABLE`, `TAX_PAYABLE`, `INTEREST_INCOME`, `DEPRECIATION_AND_AMORTIZATION`, etc.

---

### Create Account

```
POST /accounts/
```

**Request Body:** Account schema (required fields: `account_code`, `classification`, `name_en`, `sub_classification`, `is_payment_enabled`)

**Response:** `201 Created` - Full Account object with generated `id` and timestamps.

---

### List Accounts

```
GET /accounts/
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `classification` | enum | Filter: ASSET, EQUITY, EXPENSE, LIABILITY, REVENUE |
| `created_ts_after` | datetime | Created after UTC timestamp |
| `created_ts_before` | datetime | Created before UTC timestamp |
| `is_payment_enabled` | boolean | Filter by payment capability |
| `is_system` | boolean | Filter system-generated accounts |
| `modified_ts_after` | datetime | Modified after UTC timestamp |
| `modified_ts_before` | datetime | Modified before UTC timestamp |
| `page` | integer | Page number |
| `page_size` | integer | Results per page |

**Response:** `200 OK` - `PaginatedAccountList`

```json
{
  "count": 123,
  "next": "string|null",
  "previous": "string|null",
  "results": [Account]
}
```

---

### Retrieve Account

```
GET /accounts/{id}/
```

**Path Parameters:** `id` (string, required) - Account identifier

**Response:** `200 OK` - Account object

---

### Update Account (Full)

```
PUT /accounts/{id}/
```

**Path Parameters:** `id` (string, required)

**Request Body:** Full Account schema (all required fields must be provided)

**Response:** `200 OK` - Updated Account object

---

### Partial Update Account

```
PATCH /accounts/{id}/
```

**Path Parameters:** `id` (string, required)

**Request Body:** PatchedAccount schema (all fields optional)

**Response:** `200 OK` - Updated Account object

---

### Delete Account

```
DELETE /accounts/{id}/
```

**Path Parameters:** `id` (string, required)

**Response:** `204 No Content`

---

## Bank Accounts

### BankAccount Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | string | - | Yes | Unique identifier |
| `account` | string | - | Yes | Associated chart-of-accounts account |
| `name` | string | Yes | No | Bank account name |
| `classification` | string | - | Yes | Account classification (e.g., Asset) |
| `sub_classification` | enum | Yes | No | `BANK`, `PETTY_CASH`, `CREDIT_CARD` |
| `currency` | string | Yes | No | Currency code |
| `created_ts` | datetime | - | Yes | UTC creation timestamp |
| `modified_ts` | datetime | - | Yes | UTC modification timestamp |

---

### Create Bank Account

```
POST /bank-accounts/
```

**Request Body:** `name` (required), `currency` (required), `sub_classification` (required: BANK, PETTY_CASH, CREDIT_CARD)

**Response:** `201 Created` - BankAccount object

---

### List Bank Accounts

```
GET /bank-accounts/
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `classification` | enum | ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE |
| `created_ts_after` | datetime | Created after timestamp |
| `created_ts_before` | datetime | Created before timestamp |
| `currency` | enum | Filter by currency code (AED, SAR, USD, EUR, etc.) |
| `modified_ts_after` | datetime | Modified after timestamp |
| `modified_ts_before` | datetime | Modified before timestamp |
| `page` | integer | Page number |
| `page_size` | integer | Results per page |
| `sub_classification` | enum | BANK, CREDIT_CARD, PETTY_CASH |

**Response:** `200 OK` - `PaginatedBankAccountList`

```json
{
  "count": 123,
  "next": "string|null",
  "previous": "string|null",
  "results": [BankAccount]
}
```

---

### Retrieve Bank Account

```
GET /bank-accounts/{id}/
```

**Path Parameters:** `id` (string, required)

**Response:** `200 OK` - BankAccount object

---

### Update Bank Account (Full)

```
PUT /bank-accounts/{id}/
```

**Path Parameters:** `id` (string, required)

**Request Body:** Full BankAccount schema (required fields: `name`, `currency`, `sub_classification`)

**Response:** `200 OK` - Updated BankAccount object

---

### Partial Update Bank Account

```
PATCH /bank-accounts/{id}/
```

**Path Parameters:** `id` (string, required)

**Request Body:** PatchedBankAccount (all fields optional: `name`, `currency`, `sub_classification`)

**Response:** `200 OK` - Updated BankAccount object

---

### Delete Bank Account

```
DELETE /bank-accounts/{id}/
```

**Path Parameters:** `id` (string, required)

**Response:** `204 No Content`

---

## Bank Ledger Transactions

### BankLedgerTransaction Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | string | - | Yes | Unique transaction identifier |
| `bank_account` | string | - | Yes | Associated bank account ID |
| `account` | string | Yes | No | Chart-of-accounts account identifier |
| `amount` | number (double) | Yes | No | Amount; range: (-1e18, 1e18) exclusive |
| `date` | date | Yes | No | Transaction date (YYYY-MM-DD) |
| `description` | string | No | No | Transaction description (default: "") |
| `reference` | string | No | No | Reference identifier (default: "") |
| `project` | string or null | No | No | Associated project |
| `is_manual` | boolean | - | Yes | Manual entry indicator |
| `created_ts` | datetime | - | Yes | UTC creation timestamp |
| `modified_ts` | datetime | - | Yes | UTC modification timestamp |

---

### Create Bank Ledger Transaction

```
POST /bank-accounts/{bank_account_id}/ledger-transactions/
```

**Path Parameters:** `bank_account_id` (string, required)

**Request Body:** Required: `account`, `amount`, `date`. Optional: `description`, `reference`, `project`.

**Response:** `201 Created` - BankLedgerTransaction object

---

### List Bank Ledger Transactions

```
GET /bank-accounts/{bank_account_id}/ledger-transactions/
```

**Path Parameters:** `bank_account_id` (string, required)

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `page_size` | integer | Results per page |

**Response:** `200 OK` - `PaginatedBankLedgerTransactionList`

```json
{
  "count": 123,
  "next": "string|null",
  "previous": "string|null",
  "results": [BankLedgerTransaction]
}
```

---

### Retrieve Bank Ledger Transaction

```
GET /bank-accounts/{bank_account_id}/ledger-transactions/{id}/
```

**Path Parameters:** `bank_account_id` (string, required), `id` (string, required)

**Response:** `200 OK` - BankLedgerTransaction object

---

### Update Bank Ledger Transaction (Full)

```
PUT /bank-accounts/{bank_account_id}/ledger-transactions/{id}/
```

**Path Parameters:** `bank_account_id` (string, required), `id` (string, required)

**Request Body:** Full BankLedgerTransaction schema (required: `account`, `amount`, `date`)

**Response:** `200 OK` - Updated BankLedgerTransaction object

---

### Partial Update Bank Ledger Transaction

```
PATCH /bank-accounts/{bank_account_id}/ledger-transactions/{id}/
```

**Path Parameters:** `bank_account_id` (string, required), `id` (string, required)

**Request Body:** PatchedBankLedgerTransaction (all fields optional: `account`, `amount`, `date`, `description`, `reference`, `project`)

**Response:** `200 OK` - Updated BankLedgerTransaction object

---

### Delete Bank Ledger Transaction

```
DELETE /bank-accounts/{bank_account_id}/ledger-transactions/{id}/
```

**Path Parameters:** `bank_account_id` (string, required), `id` (string, required)

**Response:** `204 No Content`

---

## Bank Statement Transactions

### BankStatementTransaction Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | string | - | Yes | Unique transaction identifier |
| `bank_account` | string | - | Yes | Associated bank account ID |
| `amount` | number (double) | Yes | No | Amount; range: (-1e18, 1e18) exclusive |
| `date` | date | Yes | No | Transaction date |
| `statement_balance` | number (double) | Yes | No | Bank-reported post-transaction balance |
| `calculated_balance` | number (double) | - | Yes | Ledger-inclusive computed balance |
| `description` | string | No | No | Transaction description |
| `reference` | string | No | No | Reference identifier |
| `bank_reference` | string | No | No | Bank's reference code |
| `cost_center` | string or null | No | No | Cost allocation center |
| `project` | string or null | No | No | Associated project |
| `is_posted` | boolean | - | Yes | Ledger posting status |
| `created_ts` | datetime | - | Yes | UTC creation timestamp |
| `modified_ts` | datetime | - | Yes | UTC modification timestamp |

---

### Create Bank Statement Transaction

```
POST /bank-accounts/{bank_account_id}/statement-transactions/
```

**Path Parameters:** `bank_account_id` (string, required)

**Request Body:** Required: `amount`, `date`, `statement_balance`. Optional: `description`, `reference`, `bank_reference`, `cost_center`, `project`.

**Response:** `201 Created` - BankStatementTransaction object

---

### List Bank Statement Transactions

```
GET /bank-accounts/{bank_account_id}/statement-transactions/
```

**Path Parameters:** `bank_account_id` (string, required)

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `page_size` | integer | Results per page |

**Response:** `200 OK` - `PaginatedBankStatementTransactionList`

```json
{
  "count": 123,
  "next": "string|null",
  "previous": "string|null",
  "results": [BankStatementTransaction]
}
```

---

### Retrieve Bank Statement Transaction

```
GET /bank-accounts/{bank_account_id}/statement-transactions/{id}/
```

**Path Parameters:** `bank_account_id` (string, required), `id` (string, required)

**Response:** `200 OK` - BankStatementTransaction object

---

### Update Bank Statement Transaction (Full)

```
PUT /bank-accounts/{bank_account_id}/statement-transactions/{id}/
```

**Path Parameters:** `bank_account_id` (string, required), `id` (string, required)

**Request Body:** Required: `amount`, `date`, `statement_balance`. Optional: `description`, `reference`, `bank_reference`, `cost_center`, `project`.

**Response:** `200 OK` - Updated BankStatementTransaction object

---

### Partial Update Bank Statement Transaction

```
PATCH /bank-accounts/{bank_account_id}/statement-transactions/{id}/
```

**Path Parameters:** `bank_account_id` (string, required), `id` (string, required)

**Request Body:** PatchedBankStatementTransaction (all fields optional: `amount`, `date`, `statement_balance`, `description`, `reference`, `bank_reference`, `cost_center`, `project`)

**Response:** `200 OK` - Updated BankStatementTransaction object

---

### Delete Bank Statement Transaction

```
DELETE /bank-accounts/{bank_account_id}/statement-transactions/{id}/
```

**Path Parameters:** `bank_account_id` (string, required), `id` (string, required)

**Response:** `204 No Content`

---

## Contacts

### Contact Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | string | - | Yes | Unique identifier |
| `name` | string | Yes | No | Full name or business name |
| `code` | string | No | No | Unique contact code |
| `email` | string (email) | No | No | Email address |
| `phone` | string | No | No | Phone number |
| `address` | string | No | No | Street address |
| `building_number` | string | No | No | Building number (4 digits for KSA) |
| `additional_number` | string | No | No | Additional address number |
| `city` | string | No | No | City |
| `district` | string | No | No | District/neighborhood |
| `postal_code` | string | No | No | Postal/ZIP code (5 digits for KSA) |
| `country` | CountryEnum | No | No | ISO 3166 two-letter country code |
| `tax_registration_number` | string | No | No | Tax registration number |
| `company_identification` | array | No | No | Array of `{type, value}` objects |
| `relationship` | array | No | No | Tags: Customer, Supplier, Investor, Partner, Other |
| `attachments` | array of strings | No | No | File references |
| `beneficiaries` | array | - | Yes | Associated beneficiaries |
| `persons` | array | - | Yes | Associated persons |
| `legacy_id` | string | - | Yes | Deprecated legacy identifier |
| `created_ts` | datetime | - | Yes | UTC creation timestamp |
| `modified_ts` | datetime | - | Yes | UTC modification timestamp |

**CompanyIdentification type enum:** `CRN`, `GCC`, `IQA`, `MLS`, `SAG`, `MOM`, `NAT`, `700`, `OTH`, `PAS`, `TIN`, `TRD`

---

### Create Contact

```
POST /contacts/
```

**Request Body:** Required: `name`. All other fields optional.

**Response:** `201 Created` - Contact object

---

### List Contacts

```
GET /contacts/
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `country` | enum | ISO 3166 two-letter country code |
| `created_ts_after` | datetime | Created after timestamp |
| `created_ts_before` | datetime | Created before timestamp |
| `keyword` | string | Search term |
| `modified_ts_after` | datetime | Modified after timestamp |
| `modified_ts_before` | datetime | Modified before timestamp |
| `page` | integer | Page number |
| `page_size` | integer | Results per page |
| `relationship` | string[] | Comma-separated: Customer, Supplier, Investor, Partner, Other |

**Response:** `200 OK` - `PaginatedContactList`

```json
{
  "count": 123,
  "next": "string|null",
  "previous": "string|null",
  "results": [Contact]
}
```

---

### Retrieve Contact

```
GET /contacts/{id}/
```

**Path Parameters:** `id` (string, required)

**Response:** `200 OK` - Contact object

---

### Update Contact (Full)

```
PUT /contacts/{id}/
```

**Path Parameters:** `id` (string, required)

**Request Body:** Full Contact schema (required: `name`)

**Response:** `200 OK` - Updated Contact object

---

### Partial Update Contact

```
PATCH /contacts/{id}/
```

**Path Parameters:** `id` (string, required)

**Request Body:** PatchedContact (all fields optional)

**Response:** `200 OK` - Updated Contact object

---

### Delete Contact

```
DELETE /contacts/{id}/
```

**Path Parameters:** `id` (string, required)

**Response:** `204 No Content`

---

## Beneficiaries

### Beneficiary Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | string | - | Yes | Unique identifier |
| `name` | string | Yes | No | Beneficiary name (cannot be blank) |
| `address` | string | Yes | No | Full beneficiary address |
| `country` | CountryEnum | Yes | No | ISO 3166 two-letter country code |
| `currency` | CurrencyEnum | Yes | No | Currency code (AED, SAR, USD, EUR, etc.) |
| `iban` | string | Yes | No | IBAN (max 34 chars) |
| `bank_name` | string | No | No | Bank name (max 200 chars) |
| `swift` | string | No | No | SWIFT/BIC code (max 11 chars) |
| `charge_type` | ChargeTypeEnum | No | No | Fee handling: OUR, BEN, SHA |
| `contacts` | array of strings | No | No | Associated contact IDs |
| `created_ts` | datetime | - | Yes | UTC creation timestamp |
| `modified_ts` | datetime | - | Yes | UTC modification timestamp |

**ChargeTypeEnum:** `OUR` (Ours), `BEN` (Beneficiary), `SHA` (Shared)

---

### Create Beneficiary

```
POST /beneficiaries/
```

**Request Body:** Required: `name`, `address`, `country`, `currency`, `iban`. Optional: `bank_name`, `swift`, `charge_type`, `contacts`.

**Response:** `201 Created` - Beneficiary object

---

### List Beneficiaries

```
GET /beneficiaries/
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `charge_type` | enum | OUR, BEN, SHA, or __null__ |
| `contact` | string | Filter by contact |
| `country` | enum | ISO 3166 country code |
| `created_ts_after` | datetime | Created after timestamp |
| `created_ts_before` | datetime | Created before timestamp |
| `currency` | enum | Currency code filter |
| `keyword` | string | Search term |
| `modified_ts_after` | datetime | Modified after timestamp |
| `modified_ts_before` | datetime | Modified before timestamp |
| `page` | integer | Page number |
| `page_size` | integer | Results per page |

**Response:** `200 OK` - `PaginatedBeneficiaryList`

```json
{
  "count": 123,
  "next": "string|null",
  "previous": "string|null",
  "results": [Beneficiary]
}
```

---

### Retrieve Beneficiary

```
GET /beneficiaries/{id}/
```

**Path Parameters:** `id` (string, required)

**Response:** `200 OK` - Beneficiary object

---

### Update Beneficiary (Full)

```
PUT /beneficiaries/{id}/
```

**Path Parameters:** `id` (string, required)

**Request Body:** Required: `name`, `address`, `country`, `currency`, `iban`. Optional: `bank_name`, `swift`, `charge_type`, `contacts`.

**Response:** `200 OK` - Updated Beneficiary object

---

### Partial Update Beneficiary

```
PATCH /beneficiaries/{id}/
```

**Path Parameters:** `id` (string, required)

**Request Body:** PatchedBeneficiary (all fields optional)

**Response:** `200 OK` - Updated Beneficiary object

---

### Delete Beneficiary

```
DELETE /beneficiaries/{id}/
```

**Path Parameters:** `id` (string, required)

**Response:** `204 No Content`
