# Wafeq API - Bills, Expenses, Credit Notes & Debit Notes

Base URL: `https://api.wafeq.com/v1`
Authentication: `Authorization: Api-Key {your_api_key}`
Optional idempotency header: `X-Wafeq-Idempotency-Key: {uuid}`

---

## Bills

### Bill Object Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| id | string | - | Yes | Unique identifier |
| bill_number | string | Yes | No | Unique bill reference number |
| bill_date | string (date) | Yes | No | Issue date |
| bill_due_date | string (date) | Yes | No | Payment deadline |
| currency | CurrencyEnum | Yes | No | ISO 4217 code |
| contact | string | Yes (update) | No | Vendor identifier |
| status | enum | No | No | DRAFT, AUTHORIZED, PAID (default: DRAFT) |
| amount | number | - | Yes | Total including taxes/discounts |
| balance | number | - | Yes | Remaining payment amount |
| tax_amount | number | - | Yes | Total tax applied |
| tax_amount_type | enum | No | No | TAX_INCLUSIVE or TAX_EXCLUSIVE |
| line_items | array[BillLineItem] | Yes | No | Individual line items |
| debit_notes | array[BillDebitNote] | No | No | Applied debit notes |
| branch | string/null | No | No | Branch reference |
| project | string/null | No | No | Project reference |
| order_number | string | No | No | Associated order (default: "") |
| reference | string | No | No | Reference info (default: "") |
| notes | string | No | No | Additional comments |
| language | enum | No | No | "ar" or "en" |
| attachments | array[string] | No | No | File references |
| created_ts | datetime | - | Yes | UTC creation timestamp |
| modified_ts | datetime | - | Yes | UTC modification timestamp |

#### BillDebitNote (nested)

| Field | Type | Required |
|-------|------|----------|
| debit_note | string | Yes |
| amount | double | Yes |
| date | string (date) | No |

### Create Bill

- **Method:** POST
- **Path:** `/bills/`
- **Request Body:** Bill object (JSON)
- **Response:** 201 Created - Bill object with computed fields

### List Bills

- **Method:** GET
- **Path:** `/bills/`
- **Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| bill_date | date | Bill date filter |
| bill_due_date | date | Due date filter |
| branch | string | Branch filter |
| contact | string | Contact filter |
| project | string | Project filter |
| reference | string | Reference filter |
| created_ts_after | datetime | Creation lower bound |
| created_ts_before | datetime | Creation upper bound |
| modified_ts_after | datetime | Modification lower bound |
| modified_ts_before | datetime | Modification upper bound |
| page | integer | Page number |
| page_size | integer | Results per page |

- **Response:** 200 OK - PaginatedBillList `{ count, next, previous, results: [Bill] }`

### Retrieve Bill

- **Method:** GET
- **Path:** `/bills/{id}/`
- **Path Params:** `id` (string, required)
- **Response:** 200 OK - Bill object

### Update Bill

- **Method:** PUT
- **Path:** `/bills/{id}/`
- **Path Params:** `id` (string, required)
- **Request Body:** Full Bill object
- **Response:** 200 OK - Updated Bill object

### Partial Update Bill

- **Method:** PATCH
- **Path:** `/bills/{id}/`
- **Path Params:** `id` (string, required)
- **Request Body:** PatchedBill (all fields optional)
- **Response:** 200 OK - Updated Bill object

### Delete Bill

- **Method:** DELETE
- **Path:** `/bills/{id}/`
- **Path Params:** `id` (string, required)
- **Response:** 204 No Content

### Download Bill PDF

- **Method:** GET
- **Path:** `/bills/{id}/download/`
- **Path Params:** `id` (string, required)
- **Response:** 200 OK - `application/pdf` binary

---

## Bill Line Items

### BillLineItem Object Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| id | string | - | Yes | Unique identifier |
| account | string | Yes | No | Associated account |
| description | string | Yes | No | Line item description |
| quantity | number | Yes | No | Item quantity |
| unit_amount | number | Yes | No | Price per unit |
| line_amount | number | - | Yes | quantity x unit_amount - discount |
| tax_amount | number | - | Yes | Calculated tax |
| discount | number/null | No | No | Discount percentage (0 to 1e18) |
| tax_rate | string | No | No | Tax rate applied |
| cost_center | string | No | No | Cost center reference |
| item | string | No | No | Item reference |
| created_ts | datetime | - | Yes | UTC creation timestamp |
| modified_ts | datetime | - | Yes | UTC modification timestamp |

### Create Bill Line Item

- **Method:** POST
- **Path:** `/bills/{bill_id}/line-items/`
- **Path Params:** `bill_id` (string, required)
- **Request Body:** BillLineItem object
- **Response:** 201 Created - BillLineItem object

### List Bill Line Items

- **Method:** GET
- **Path:** `/bills/{bill_id}/line-items/`
- **Path Params:** `bill_id` (string, required)
- **Query Params:** `page` (integer), `page_size` (integer)
- **Response:** 200 OK - PaginatedBillLineItemList `{ count, next, previous, results }`

### Retrieve Bill Line Item

- **Method:** GET
- **Path:** `/bills/{bill_id}/line-items/{id}/`
- **Path Params:** `bill_id` (string), `id` (string) - both required
- **Response:** 200 OK - BillLineItem object

### Update Bill Line Item

- **Method:** PUT
- **Path:** `/bills/{bill_id}/line-items/{id}/`
- **Path Params:** `bill_id` (string), `id` (string) - both required
- **Request Body:** Full BillLineItem object
- **Response:** 200 OK - Updated BillLineItem object

### Partial Update Bill Line Item

- **Method:** PATCH
- **Path:** `/bills/{bill_id}/line-items/{id}/`
- **Path Params:** `bill_id` (string), `id` (string) - both required
- **Request Body:** PatchedBillLineItem (all fields optional)
- **Response:** 200 OK - Updated BillLineItem object

### Delete Bill Line Item

- **Method:** DELETE
- **Path:** `/bills/{bill_id}/line-items/{id}/`
- **Path Params:** `bill_id` (string), `id` (string) - both required
- **Response:** 204 No Content

---

## Expenses

### Expense Object Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| id | string | - | Yes | Unique identifier |
| account | string | Yes | No | Associated account |
| amount | number (double) | Yes | No | Monetary value (range: +/-1e18) |
| currency | CurrencyEnum | Yes | No | ISO 4217 code |
| date | string (date) | Yes | No | Expense date |
| description | string | Yes | No | Expense description |
| paid_through_account | string | Yes | No | Payment account |
| contact | string | No | No | Associated contact |
| branch | string/null | No | No | Branch reference |
| cost_center | string/null | No | No | Cost center reference |
| project | string/null | No | No | Project reference |
| reference | string | No | No | Reference code (default: "") |
| tax_rate | string | No | No | Tax rate |
| tax_amount_type | enum | No | No | TAX_INCLUSIVE (default) or TAX_EXCLUSIVE |
| attachments | array[string] | No | No | File references |
| created_ts | datetime | - | Yes | UTC creation timestamp |
| modified_ts | datetime | - | Yes | UTC modification timestamp |

### Create Expense

- **Method:** POST
- **Path:** `/expenses/`
- **Request Body:** Expense object (JSON)
- **Response:** 201 Created - Expense object

### List Expenses

- **Method:** GET
- **Path:** `/expenses/`
- **Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| account | string | Account filter |
| branch | string | Branch filter |
| contact | string | Contact filter |
| date | date | Expense date filter |
| paid_through_account | string | Payment account filter |
| project | string | Project filter |
| reference | string | Reference filter |
| created_ts_after | datetime | Creation lower bound |
| created_ts_before | datetime | Creation upper bound |
| modified_ts_after | datetime | Modification lower bound |
| modified_ts_before | datetime | Modification upper bound |
| page | integer | Page number |
| page_size | integer | Results per page |

- **Response:** 200 OK - PaginatedExpenseList `{ count, next, previous, results: [Expense] }`

### Retrieve Expense

- **Method:** GET
- **Path:** `/expenses/{id}/`
- **Path Params:** `id` (string, required)
- **Response:** 200 OK - Expense object

### Update Expense

- **Method:** PUT
- **Path:** `/expenses/{id}/`
- **Path Params:** `id` (string, required)
- **Request Body:** Full Expense object
- **Response:** 200 OK - Updated Expense object

### Partial Update Expense

- **Method:** PATCH
- **Path:** `/expenses/{id}/`
- **Path Params:** `id` (string, required)
- **Request Body:** PatchedExpense (all fields optional)
- **Response:** 200 OK - Updated Expense object

### Delete Expense

- **Method:** DELETE
- **Path:** `/expenses/{id}/`
- **Path Params:** `id` (string, required)
- **Response:** 204 No Content

---

## Credit Notes

### CreditNote Object Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| id | string | - | Yes | Unique identifier |
| credit_note_number | string | Yes | No | Unique credit note number |
| credit_note_date | string (date) | Yes | No | Issue date |
| contact | string | Yes | No | Associated contact |
| currency | CurrencyEnum | Yes | No | ISO 4217 code |
| amount | number | - | Yes | Total including taxes |
| balance | number | - | Yes | Remaining balance |
| tax_amount | number | - | Yes | Total tax applied |
| status | enum | No | No | DRAFT, SENT, FINALIZED (default: DRAFT) |
| tax_amount_type | enum | No | No | TAX_INCLUSIVE or TAX_EXCLUSIVE |
| line_items | array[CreditNoteLineItem] | Yes | No | Line items |
| branch | string/null | No | No | Branch reference |
| project | string/null | No | No | Project reference |
| warehouse | string/null | No | No | Warehouse reference |
| discount_cost_center | string | No | No | Discount cost center |
| language | enum | No | No | "ar" or "en" |
| notes | string | No | No | Additional comments |
| reference | string | No | No | Reference code |
| place_of_supply | string | No | No | UAE location for VAT (ABU_DHABI, DUBAI, etc.) |
| attachments | array[string] | No | No | File references |
| created_ts | datetime | - | Yes | UTC creation timestamp |
| modified_ts | datetime | - | Yes | UTC modification timestamp |

### Create Credit Note

- **Method:** POST
- **Path:** `/credit-notes/`
- **Request Body:** CreditNote object (JSON)
- **Response:** 201 Created - CreditNote object

### List Credit Notes

- **Method:** GET
- **Path:** `/credit-notes/`
- **Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| branch | string | Branch filter |
| contact | string | Contact filter |
| credit_note_date | date | Date filter |
| project | string | Project filter |
| status | string | Status filter |
| created_ts_after | datetime | Creation lower bound |
| created_ts_before | datetime | Creation upper bound |
| modified_ts_after | datetime | Modification lower bound |
| modified_ts_before | datetime | Modification upper bound |
| page | integer | Page number |
| page_size | integer | Results per page |

- **Response:** 200 OK - PaginatedCreditNoteList `{ count, next, previous, results: [CreditNote] }`

### Retrieve Credit Note

- **Method:** GET
- **Path:** `/credit-notes/{id}/`
- **Path Params:** `id` (string, required)
- **Response:** 200 OK - CreditNote object

### Update Credit Note

- **Method:** PUT
- **Path:** `/credit-notes/{id}/`
- **Path Params:** `id` (string, required)
- **Request Body:** Full CreditNote object
- **Response:** 200 OK - Updated CreditNote object

### Partial Update Credit Note

- **Method:** PATCH
- **Path:** `/credit-notes/{id}/`
- **Path Params:** `id` (string, required)
- **Request Body:** PatchedCreditNote (all fields optional)
- **Response:** 200 OK - Updated CreditNote object

### Delete Credit Note

- **Method:** DELETE
- **Path:** `/credit-notes/{id}/`
- **Path Params:** `id` (string, required)
- **Response:** 204 No Content

### Download Credit Note PDF

- **Method:** GET
- **Path:** `/credit-notes/{id}/download/`
- **Path Params:** `id` (string, required)
- **Response:** 200 OK - `application/pdf` binary

### Report Credit Note to Tax Authority

- **Method:** POST
- **Path:** `/credit-notes/{id}/tax-authority/report/`
- **Path Params:** `id` (string, required)
- **Request Body:** None
- **Response:** 200 OK

```json
{
  "metadata": {
    "errors": [{}],
    "warnings": [{}]
  },
  "reported_ts": "2024-01-01T00:00:00Z",
  "status": "string"
}
```

---

## Credit Note Line Items

### CreditNoteLineItem Object Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| id | string | - | Yes | Unique identifier |
| account | string | Yes | No | Associated account |
| description | string | Yes | No | Line item description |
| quantity | number | Yes | No | Item quantity |
| unit_amount | number | Yes | No | Per-unit price |
| line_amount | number | - | Yes | Total line amount |
| tax_amount | number | - | Yes | Calculated tax |
| discount | number/null | No | No | Discount percentage (0-100) |
| tax_rate | string | No | No | Tax rate applied |
| cost_center | string | No | No | Cost center reference |
| item | string | No | No | Item reference |
| created_ts | datetime | - | Yes | UTC creation timestamp |
| modified_ts | datetime | - | Yes | UTC modification timestamp |

### Create Credit Note Line Item

- **Method:** POST
- **Path:** `/credit-notes/{credit_note_id}/line-items/`
- **Path Params:** `credit_note_id` (string, required)
- **Request Body:** CreditNoteLineItem object
- **Response:** 201 Created - CreditNoteLineItem object

### List Credit Note Line Items

- **Method:** GET
- **Path:** `/credit-notes/{credit_note_id}/line-items/`
- **Path Params:** `credit_note_id` (string, required)
- **Query Params:** `page` (integer), `page_size` (integer)
- **Response:** 200 OK - PaginatedCreditNoteLineItemList

### Retrieve Credit Note Line Item

- **Method:** GET
- **Path:** `/credit-notes/{credit_note_id}/line-items/{id}/`
- **Path Params:** `credit_note_id` (string), `id` (string) - both required
- **Response:** 200 OK - CreditNoteLineItem object

### Update Credit Note Line Item

- **Method:** PUT
- **Path:** `/credit-notes/{credit_note_id}/line-items/{id}/`
- **Path Params:** `credit_note_id` (string), `id` (string) - both required
- **Request Body:** Full CreditNoteLineItem object
- **Response:** 200 OK - Updated CreditNoteLineItem object

### Partial Update Credit Note Line Item

- **Method:** PATCH
- **Path:** `/credit-notes/{credit_note_id}/line-items/{id}/`
- **Path Params:** `credit_note_id` (string), `id` (string) - both required
- **Request Body:** PatchedCreditNoteLineItem (all fields optional)
- **Response:** 200 OK - Updated CreditNoteLineItem object

### Delete Credit Note Line Item

- **Method:** DELETE
- **Path:** `/credit-notes/{credit_note_id}/line-items/{id}/`
- **Path Params:** `credit_note_id` (string), `id` (string) - both required
- **Response:** 204 No Content

---

## Credit Notes (Bulk API)

The bulk API uses a different schema with inline contact objects and a different line item structure.

### APICreditNote Object Schema (Bulk)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier |
| amount | number | Yes | Total amount |
| credit_note_number | string | Yes | Document number |
| credit_note_date | datetime | Yes | Issue date |
| status | string | Yes | Status |
| currency | CurrencyEnum | Yes | Currency code |
| language | enum | Yes | "ar" or "en" |
| tax_amount_type | enum | Yes | TAX_INCLUSIVE or TAX_EXCLUSIVE |
| contact | APIEntityContact | Yes | Inline contact object |
| line_items | array (1-100) | Yes | Line items |
| created_at | datetime | Yes | Creation timestamp |
| notes | string | No | Default: "" |
| reference | string | No | Default: "" |
| paid_through_account | string | No | Account identifier |

#### APIEntityContact (inline)

| Field | Type | Required |
|-------|------|----------|
| name | string | Yes |
| email | string | No |
| address | string | No |
| city | string | No |
| country | string | No |
| tax_registration_number | string | No |

#### APICreditNoteLineItem

| Field | Type | Required |
|-------|------|----------|
| name | string | Yes |
| description | string | Yes |
| quantity | number | Yes |
| price | number | Yes |
| account | string | No |
| discount | APIEntityDiscount | No |
| tax_rate | APIEntityTaxRateFlat | No |

### Bulk Send Credit Notes

- **Method:** POST
- **Path:** `/api-credit-notes/bulk_send/`
- **Request Body:** Array of BulkSendAPICreditNote objects (JSON)

Each object includes `channels` array for email delivery:

```json
[
  {
    "channels": [
      {
        "medium": "email",
        "data": {
          "subject": "Credit Note from Company",
          "message": "<p>Please find attached your credit note.</p>",
          "recipients": {
            "to": ["email@example.com"],
            "cc": [],
            "bcc": []
          }
        }
      }
    ],
    "contact": { "name": "Client Name", "email": "client@example.com" },
    "credit_note_date": "2021-01-01",
    "credit_note_number": "CN-1234",
    "currency": "SAR",
    "language": "en",
    "tax_amount_type": "TAX_INCLUSIVE",
    "line_items": [
      {
        "name": "Item 1",
        "description": "Description",
        "quantity": 2,
        "price": 40,
        "account": "acc_xxx"
      }
    ]
  }
]
```

Email recipients: max 6 per field (to, cc, bcc).

- **Response:** 200 OK - No response body

### List Credit Notes (Bulk)

- **Method:** GET
- **Path:** `/api-credit-notes/`
- **Query Params:** `page` (integer), `page_size` (integer)
- **Response:** 200 OK - PaginatedAPICreditNoteList `{ count, next, previous, results }`

### Retrieve Credit Note (Bulk)

- **Method:** GET
- **Path:** `/api-credit-notes/{id}/`
- **Path Params:** `id` (string, required)
- **Response:** 200 OK - APICreditNote object

### Delete Credit Note (Bulk)

- **Method:** DELETE
- **Path:** `/api-credit-notes/{id}/`
- **Path Params:** `id` (string, required)
- **Response:** 204 No Content

### Download Credit Note PDF (Bulk)

- **Method:** GET
- **Path:** `/api-credit-notes/{id}/download/`
- **Path Params:** `id` (string, required)
- **Response:** 200 OK - `application/pdf` binary

---

## Debit Notes

### DebitNote Object Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| id | string | - | Yes | Unique identifier |
| debit_note_number | string | Yes | No | Unique debit note number |
| debit_note_date | string (date) | Yes | No | Issue date |
| contact | string | Yes | No | Customer identifier |
| currency | CurrencyEnum | Yes | No | ISO 4217 code |
| amount | number | - | Yes | Total including taxes |
| balance | number | - | Yes | Remaining balance |
| tax_amount | number | - | Yes | Total tax applied |
| status | enum | No | No | DRAFT or POSTED (default: DRAFT) |
| tax_amount_type | enum | No | No | TAX_INCLUSIVE or TAX_EXCLUSIVE |
| line_items | array[DebitNoteLineItem] | Yes | No | Line items |
| branch | string/null | No | No | Branch reference |
| project | string/null | No | No | Project reference |
| order_number | string | No | No | Order reference (max 100 chars) |
| reference | string | No | No | Reference code |
| notes | string | No | No | Additional comments |
| attachments | array[string] | No | No | File references |
| created_ts | datetime | - | Yes | UTC creation timestamp |
| modified_ts | datetime | - | Yes | UTC modification timestamp |

**Note:** Debit note statuses differ from bills (DRAFT/POSTED vs DRAFT/AUTHORIZED/PAID) and credit notes (DRAFT/SENT/FINALIZED).

### Create Debit Note

- **Method:** POST
- **Path:** `/debit-notes/`
- **Request Body:** DebitNote object (JSON)
- **Response:** 201 Created - DebitNote object

### List Debit Notes

- **Method:** GET
- **Path:** `/debit-notes/`
- **Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| branch | string | Branch filter |
| contact | string | Contact filter |
| debit_note_date | date | Date filter |
| project | string | Project filter |
| created_ts_after | datetime | Creation lower bound |
| created_ts_before | datetime | Creation upper bound |
| modified_ts_after | datetime | Modification lower bound |
| modified_ts_before | datetime | Modification upper bound |
| page | integer | Page number |
| page_size | integer | Results per page |

- **Response:** 200 OK - PaginatedDebitNoteList `{ count, next, previous, results: [DebitNote] }`

### Retrieve Debit Note

- **Method:** GET
- **Path:** `/debit-notes/{id}/`
- **Path Params:** `id` (string, required)
- **Response:** 200 OK - DebitNote object

### Update Debit Note

- **Method:** PUT
- **Path:** `/debit-notes/{id}/`
- **Path Params:** `id` (string, required)
- **Request Body:** Full DebitNote object
- **Response:** 200 OK - Updated DebitNote object

### Partial Update Debit Note

- **Method:** PATCH
- **Path:** `/debit-notes/{id}/`
- **Path Params:** `id` (string, required)
- **Request Body:** PatchedDebitNote (all fields optional)
- **Response:** 200 OK - Updated DebitNote object

### Delete Debit Note

- **Method:** DELETE
- **Path:** `/debit-notes/{id}/`
- **Path Params:** `id` (string, required)
- **Response:** 204 No Content

### Download Debit Note PDF

- **Method:** GET
- **Path:** `/debit-notes/{id}/download/`
- **Path Params:** `id` (string, required)
- **Response:** 200 OK - `application/pdf` binary

---

## Debit Note Line Items

### DebitNoteLineItem Object Schema

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| id | string | - | Yes | Unique identifier |
| account | string | Yes | No | Associated account |
| description | string | Yes | No | Line item description |
| quantity | number | Yes | No | Item quantity |
| unit_amount | number | Yes | No | Per-unit price |
| line_amount | number | - | Yes | quantity x unit_amount |
| tax_amount | number | - | Yes | Calculated tax |
| discount | number/null | No | No | Discount percentage (0 to 1e18) |
| tax_rate | string | No | No | Tax rate applied |
| cost_center | string | No | No | Cost center reference |
| item | string | No | No | Item reference |
| created_ts | datetime | - | Yes | UTC creation timestamp |
| modified_ts | datetime | - | Yes | UTC modification timestamp |

### Create Debit Note Line Item

- **Method:** POST
- **Path:** `/debit-notes/{debit_note_id}/line-items/`
- **Path Params:** `debit_note_id` (string, required)
- **Request Body:** DebitNoteLineItem object
- **Response:** 201 Created - DebitNoteLineItem object

### List Debit Note Line Items

- **Method:** GET
- **Path:** `/debit-notes/{debit_note_id}/line-items/`
- **Path Params:** `debit_note_id` (string, required)
- **Query Params:** `page` (integer), `page_size` (integer)
- **Response:** 200 OK - PaginatedDebitNoteLineItemList

### Retrieve Debit Note Line Item

- **Method:** GET
- **Path:** `/debit-notes/{debit_note_id}/line-items/{id}/`
- **Path Params:** `debit_note_id` (string), `id` (string) - both required
- **Response:** 200 OK - DebitNoteLineItem object

### Update Debit Note Line Item

- **Method:** PUT
- **Path:** `/debit-notes/{debit_note_id}/line-items/{id}/`
- **Path Params:** `debit_note_id` (string), `id` (string) - both required
- **Request Body:** Full DebitNoteLineItem object
- **Response:** 200 OK - Updated DebitNoteLineItem object

### Partial Update Debit Note Line Item

- **Method:** PATCH
- **Path:** `/debit-notes/{debit_note_id}/line-items/{id}/`
- **Path Params:** `debit_note_id` (string), `id` (string) - both required
- **Request Body:** PatchedDebitNoteLineItem (all fields optional)
- **Response:** 200 OK - Updated DebitNoteLineItem object

### Delete Debit Note Line Item

- **Method:** DELETE
- **Path:** `/debit-notes/{debit_note_id}/line-items/{id}/`
- **Path Params:** `debit_note_id` (string), `id` (string) - both required
- **Response:** 204 No Content

---

## Endpoint Summary

| Resource | Create | List | Retrieve | Update | Partial Update | Delete | Download | Other |
|----------|--------|------|----------|--------|----------------|--------|----------|-------|
| Bills | POST /bills/ | GET /bills/ | GET /bills/{id}/ | PUT /bills/{id}/ | PATCH /bills/{id}/ | DELETE /bills/{id}/ | GET /bills/{id}/download/ | - |
| Bill Line Items | POST /bills/{bill_id}/line-items/ | GET /bills/{bill_id}/line-items/ | GET /bills/{bill_id}/line-items/{id}/ | PUT .../{id}/ | PATCH .../{id}/ | DELETE .../{id}/ | - | - |
| Expenses | POST /expenses/ | GET /expenses/ | GET /expenses/{id}/ | PUT /expenses/{id}/ | PATCH /expenses/{id}/ | DELETE /expenses/{id}/ | - | - |
| Credit Notes | POST /credit-notes/ | GET /credit-notes/ | GET /credit-notes/{id}/ | PUT /credit-notes/{id}/ | PATCH /credit-notes/{id}/ | DELETE /credit-notes/{id}/ | GET .../download/ | POST .../tax-authority/report/ |
| CN Line Items | POST /credit-notes/{cn_id}/line-items/ | GET .../ | GET .../{id}/ | PUT .../{id}/ | PATCH .../{id}/ | DELETE .../{id}/ | - | - |
| CN Bulk | POST /api-credit-notes/bulk_send/ | GET /api-credit-notes/ | GET /api-credit-notes/{id}/ | - | - | DELETE /api-credit-notes/{id}/ | GET .../download/ | - |
| Debit Notes | POST /debit-notes/ | GET /debit-notes/ | GET /debit-notes/{id}/ | PUT /debit-notes/{id}/ | PATCH /debit-notes/{id}/ | DELETE /debit-notes/{id}/ | GET .../download/ | - |
| DN Line Items | POST /debit-notes/{dn_id}/line-items/ | GET .../ | GET .../{id}/ | PUT .../{id}/ | PATCH .../{id}/ | DELETE .../{id}/ | - | - |
