# Wafeq Invoices API Reference

Base URL: `https://api.wafeq.com/v1`

Authentication: `Authorization: Api-Key {your_api_key}`

Optional idempotency header: `X-Wafeq-Idempotency-Key: {uuid}` (POST/PUT/PATCH/DELETE)

---

## Table of Contents

- [Standard Invoices](#standard-invoices)
  - [Create Invoice](#create-invoice)
  - [List Invoices](#list-invoices)
  - [Retrieve Invoice](#retrieve-invoice)
  - [Update Invoice](#update-invoice)
  - [Partial Update Invoice](#partial-update-invoice)
  - [Delete Invoice](#delete-invoice)
  - [Download Invoice PDF](#download-invoice-pdf)
  - [Report Invoice to Tax Authority](#report-invoice-to-tax-authority)
- [Invoice Line Items](#invoice-line-items)
  - [Create Line Item](#create-invoice-line-item)
  - [List Line Items](#list-invoice-line-items)
  - [Retrieve Line Item](#retrieve-invoice-line-item)
  - [Update Line Item](#update-invoice-line-item)
  - [Partial Update Line Item](#partial-update-invoice-line-item)
  - [Delete Line Item](#delete-invoice-line-item)
- [Bulk Invoices](#bulk-invoices)
  - [Bulk Send Invoices](#bulk-send-invoices)
  - [List Bulk Invoices](#list-bulk-invoices)
  - [Retrieve Bulk Invoice](#retrieve-bulk-invoice)
  - [Delete Bulk Invoice](#delete-bulk-invoice)
  - [Download Bulk Invoice PDF](#download-bulk-invoice-pdf)
  - [Summary Invoice](#summary-invoice)
- [Simplified Invoices](#simplified-invoices)
  - [Create Simplified Invoice](#create-simplified-invoice)
  - [List Simplified Invoices](#list-simplified-invoices)
  - [Retrieve Simplified Invoice](#retrieve-simplified-invoice)
  - [Update Simplified Invoice](#update-simplified-invoice)
  - [Partial Update Simplified Invoice](#partial-update-simplified-invoice)
  - [Delete Simplified Invoice](#delete-simplified-invoice)
  - [Download Simplified Invoice PDF](#download-simplified-invoice-pdf)
  - [Report Simplified Invoice to Tax Authority](#report-simplified-invoice-to-tax-authority)
- [Simplified Invoice Line Items](#simplified-invoice-line-items)
  - [Create Simplified Line Item](#create-simplified-invoice-line-item)
  - [List Simplified Line Items](#list-simplified-invoice-line-items)
  - [Retrieve Simplified Line Item](#retrieve-simplified-invoice-line-item)
  - [Update Simplified Line Item](#update-simplified-invoice-line-item)
  - [Partial Update Simplified Line Item](#partial-update-simplified-invoice-line-item)
  - [Delete Simplified Line Item](#delete-simplified-invoice-line-item)
- [Schemas](#schemas)

---

## Standard Invoices

### Create Invoice

**POST** `/invoices/`

Creates a new standard invoice.

**Request Body** (`application/json`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contact` | string | Yes | Customer identifier |
| `currency` | CurrencyEnum | Yes | ISO currency code (AED, USD, EUR, etc.) |
| `invoice_date` | date | Yes | Issue date (YYYY-MM-DD) |
| `invoice_due_date` | date | Yes | Payment deadline (YYYY-MM-DD) |
| `invoice_number` | string | Yes | Unique invoice identifier |
| `line_items` | array[InvoiceLineItem] | Yes | Line item objects |
| `attachments` | array[string] | No | File/document URLs |
| `branch` | string or null | No | Branch identifier |
| `discount_account` | string | No | Account for discount booking |
| `discount_amount` | number | No | Discount amount (0 to 10^16) |
| `discount_cost_center` | string | No | Cost center for discount |
| `discount_tax_rate` | string | No | Tax rate on discount |
| `language` | LanguageEnum | No | "ar" or "en" (default: "en") |
| `notes` | string | No | Additional comments |
| `place_of_supply` | string | No | UAE emirate or OUTSIDE_UAE |
| `project` | string or null | No | Project identifier |
| `purchase_order` | string | No | PO reference |
| `reference` | string | No | Reference code |
| `status` | Status730Enum | No | DRAFT, SENT, FINALIZED (default: DRAFT) |
| `tax_amount_type` | TaxAmountTypeEnum | No | TAX_INCLUSIVE or TAX_EXCLUSIVE |
| `warehouse` | string or null | No | Warehouse identifier |

**Response:** `201 Created` -- Returns full Invoice object with read-only fields (`id`, `amount`, `balance`, `tax_amount`, `created_ts`, `modified_ts`).

**Response Header:** `X-Wafeq-Idempotent-Replayed` -- indicates cache status.

---

### List Invoices

**GET** `/invoices/`

Returns a paginated list of invoices.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `branch` | string | Filter by branch identifier |
| `contact` | string | Filter by contact identifier |
| `created_ts_after` | date-time | Created after this UTC timestamp |
| `created_ts_before` | date-time | Created before this UTC timestamp |
| `invoice_date` | date | Filter by invoice date |
| `modified_ts_after` | date-time | Modified after this UTC timestamp |
| `modified_ts_before` | date-time | Modified before this UTC timestamp |
| `page` | integer | Page number |
| `page_size` | integer | Results per page |
| `project` | string | Filter by project identifier |
| `status` | string | DRAFT, SENT, or FINALIZED |

**Response:** `200 OK`

```json
{
  "count": 123,
  "next": "https://api.wafeq.com/v1/invoices/?page=2",
  "previous": null,
  "results": [Invoice, ...]
}
```

---

### Retrieve Invoice

**GET** `/invoices/{id}/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Response:** `200 OK` -- Returns full Invoice object.

---

### Update Invoice

**PUT** `/invoices/{id}/`

Full update of an invoice. All required fields must be provided.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Request Body:** Same schema as Create Invoice (all required fields must be provided).

**Response:** `200 OK` -- Returns updated Invoice object.

---

### Partial Update Invoice

**PATCH** `/invoices/{id}/`

Partial update -- only provided fields are modified.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Request Body:** PatchedInvoice -- all fields optional. Same field definitions as Create Invoice.

**Response:** `200 OK` -- Returns updated Invoice object.

---

### Delete Invoice

**DELETE** `/invoices/{id}/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Response:** `204 No Content` -- Empty response body.

---

### Download Invoice PDF

**GET** `/invoices/{id}/download/`

Downloads the invoice as a PDF file.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Response:** `200 OK` -- `Content-Type: application/pdf` -- Binary PDF file.

---

### Report Invoice to Tax Authority

**POST** `/invoices/{id}/tax-authority/report/`

Submits the invoice to the tax authority for reporting.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Request Body:** None.

**Response:** `200 OK`

```json
{
  "status": "string",
  "reported_ts": "2024-01-15T10:30:00Z",
  "metadata": {
    "errors": [],
    "warnings": []
  }
}
```

---

## Invoice Line Items

### Create Invoice Line Item

**POST** `/invoices/{invoice_id}/line-items/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Parent invoice identifier |

**Request Body** (`application/json`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account` | string | Yes | Associated account identifier |
| `description` | string | Yes | Line item description |
| `quantity` | number | Yes | Item quantity |
| `unit_amount` | number | Yes | Price per unit |
| `cost_center` | string | No | Associated cost center |
| `discount` | number or null | No | Discount percentage (0 to 10^18) |
| `item` | string | No | Associated item identifier |
| `tax_rate` | string | No | Tax rate applied |

**Response:** `201 Created` -- Returns InvoiceLineItem with read-only fields (`id`, `line_amount`, `tax_amount`, `created_ts`, `modified_ts`).

---

### List Invoice Line Items

**GET** `/invoices/{invoice_id}/line-items/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Parent invoice identifier |

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `page_size` | integer | Results per page |

**Response:** `200 OK`

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [InvoiceLineItem, ...]
}
```

---

### Retrieve Invoice Line Item

**GET** `/invoices/{invoice_id}/line-items/{id}/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Parent invoice identifier |
| `id` | string | Yes | Line item identifier |

**Response:** `200 OK` -- Returns InvoiceLineItem object.

---

### Update Invoice Line Item

**PUT** `/invoices/{invoice_id}/line-items/{id}/`

Full update of a line item. All required fields must be provided.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Parent invoice identifier |
| `id` | string | Yes | Line item identifier |

**Request Body:** Same as Create Invoice Line Item (required fields: `account`, `description`, `quantity`, `unit_amount`).

**Response:** `200 OK` -- Returns updated InvoiceLineItem object.

---

### Partial Update Invoice Line Item

**PATCH** `/invoices/{invoice_id}/line-items/{id}/`

Partial update -- only provided fields are modified.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Parent invoice identifier |
| `id` | string | Yes | Line item identifier |

**Request Body:** PatchedInvoiceLineItem -- all fields optional. Same field definitions as Create.

**Response:** `200 OK` -- Returns updated InvoiceLineItem object.

---

### Delete Invoice Line Item

**DELETE** `/invoices/{invoice_id}/line-items/{id}/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Parent invoice identifier |
| `id` | string | Yes | Line item identifier |

**Response:** `204 No Content` -- Empty response body.

---

## Bulk Invoices

The Bulk Invoices API uses a different path prefix (`/api-invoices/`) and a slightly different schema (`APIInvoice`) compared to standard invoices.

### Bulk Send Invoices

**POST** `/api-invoices/bulk_send/`

Sends one or more invoices via email in a single request.

**Request Body** (`application/json`): Array of `BulkSendAPIInvoice` objects.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contact` | APIEntityContact | Yes | Recipient contact details |
| `currency` | CurrencyEnum | Yes | Currency code |
| `invoice_date` | date | Yes | Invoice date (YYYY-MM-DD) |
| `invoice_number` | string | Yes | Invoice identifier |
| `language` | LanguageEnum | Yes | "ar" or "en" |
| `line_items` | array[BulkSendLineItem] (1-100) | Yes | Line items |
| `tax_amount_type` | TaxAmountTypeEnum | Yes | TAX_INCLUSIVE or TAX_EXCLUSIVE |
| `channels` | array (0-1) | Yes | Delivery channels |
| `notes` | string | No | Default: "" |
| `paid_through_account` | string | No | Payment account |
| `reference` | string | No | Default: "" |

**APIEntityContact:**

| Field | Type | Required |
|-------|------|----------|
| `name` | string | Yes |
| `email` | string | No |
| `address` | string | No (default: "") |
| `city` | string | No (default: "") |
| `country` | string | No (default: "") |
| `tax_registration_number` | string | No (default: "") |

**BulkSendLineItem:**

| Field | Type | Required |
|-------|------|----------|
| `name` | string | Yes |
| `description` | string | Yes |
| `price` | number | Yes |
| `quantity` | number | Yes |
| `account` | string | No |
| `discount` | object (`type`: "percent"/"amount", `value`: number) | No |
| `tax_rate` | object (`name`: string, `rate`: number, `suid`: string) | No |

**Channels:**

| Field | Type | Required |
|-------|------|----------|
| `medium` | string | Yes (only "email") |
| `data.recipients.to` | array[email] (max 6) | Yes |
| `data.recipients.cc` | array[email] (max 6) | No |
| `data.recipients.bcc` | array[email] (max 6) | No |
| `data.subject` | string | Yes |
| `data.message` | string | Yes |

**Response:** `200 OK` -- Empty body on success.

**Example Request Body:**

```json
[
  {
    "channels": [
      {
        "medium": "email",
        "data": {
          "subject": "Invoice X from Company",
          "message": "<p>Please find attached your invoice.</p>",
          "recipients": {
            "to": ["ahmed@example.com"],
            "cc": [],
            "bcc": []
          }
        }
      }
    ],
    "contact": {
      "name": "Ahmed A.",
      "email": "ahmed@example.com",
      "address": "123 Street, Riyadh, Saudi Arabia"
    },
    "currency": "SAR",
    "invoice_date": "2021-01-01",
    "invoice_number": "TEST-INV-1234",
    "language": "en",
    "tax_amount_type": "TAX_INCLUSIVE",
    "line_items": [
      {
        "name": "Item 1",
        "description": "Item description 1",
        "price": 40,
        "quantity": 2,
        "account": "acc_DTbQSMR374gSSbdPy3mrBr",
        "tax_rate": "tax_3WgEt9y9BrcnxNAveZPTea"
      }
    ],
    "paid_through_account": "acc_7YpiBvkKRkpX9zkwZnXryJ",
    "reference": "test"
  }
]
```

---

### List Bulk Invoices

**GET** `/api-invoices/`

Returns a paginated list of bulk invoices.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `page_size` | integer | Results per page |

**Response:** `200 OK`

```json
{
  "count": 123,
  "next": "https://api.wafeq.com/v1/api-invoices/?page=2",
  "previous": null,
  "results": [APIInvoice, ...]
}
```

**APIInvoice Fields:**

| Field | Type | Required |
|-------|------|----------|
| `id` | string | Yes |
| `invoice_number` | string | Yes |
| `amount` | number | Yes |
| `currency` | CurrencyEnum | Yes |
| `invoice_date` | date-time | Yes |
| `created_at` | date-time | Yes |
| `status` | string | Yes |
| `language` | LanguageEnum | Yes |
| `tax_amount_type` | TaxAmountTypeEnum | Yes |
| `contact` | APIEntityContact | Yes |
| `line_items` | array (1-100) | Yes |
| `notes` | string | No (default: "") |
| `reference` | string | No (default: "") |
| `paid_through_account` | string | No |

---

### Retrieve Bulk Invoice

**GET** `/api-invoices/{id}/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Response:** `200 OK` -- Returns APIInvoice object.

---

### Delete Bulk Invoice

**DELETE** `/api-invoices/{id}/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Response:** `204 No Content` -- Empty response body.

---

### Download Bulk Invoice PDF

**GET** `/api-invoices/{id}/download/`

Downloads the bulk invoice as a PDF file.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Response:** `200 OK` -- `Content-Type: application/pdf` -- Binary PDF file.

---

### Summary Invoice

**GET** `/api-invoices/summary/`

Generates a summary invoice equivalent to all bulk invoices.

**Parameters:** None.

**Response:** `200 OK` -- Returns a single APIInvoice object representing the summary.

---

## Simplified Invoices

Simplified invoices use the `/simplified-invoices/` path and have a `paid_through_account` field (required). Status values differ: DRAFT or PAID (instead of DRAFT/SENT/FINALIZED). There is no `invoice_due_date` or `balance` field.

### Create Simplified Invoice

**POST** `/simplified-invoices/`

**Request Body** (`application/json`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contact` | string | Yes | Contact identifier |
| `currency` | CurrencyEnum | Yes | ISO currency code |
| `invoice_date` | date | Yes | Issue date (YYYY-MM-DD) |
| `line_items` | array[SimplifiedInvoiceLineItem] | Yes | Line items |
| `paid_through_account` | string | Yes | Account identifier for payment |
| `branch` | string or null | No | Branch identifier |
| `invoice_number` | string | No | Max 100 chars |
| `language` | LanguageEnum | No | "ar" or "en" (default: "en") |
| `notes` | string | No | Additional comments |
| `place_of_supply` | string | No | UAE emirate or OUTSIDE_UAE |
| `project` | string or null | No | Project identifier |
| `reference` | string | No | Default: "" |
| `status` | SimplifiedInvoiceStatusEnum | No | DRAFT or PAID (default: DRAFT) |
| `tax_amount_type` | TaxAmountTypeEnum | No | TAX_INCLUSIVE or TAX_EXCLUSIVE |
| `warehouse` | string or null | No | Warehouse identifier |

**Response:** `201 Created` -- Returns full SimplifiedInvoice with read-only fields (`id`, `amount`, `tax_amount`, `created_ts`, `modified_ts`).

---

### List Simplified Invoices

**GET** `/simplified-invoices/`

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `branch` | string | Filter by branch |
| `contact` | string | Filter by contact |
| `created_ts_after` | date-time | Created after UTC timestamp |
| `created_ts_before` | date-time | Created before UTC timestamp |
| `invoice_date` | date | Filter by invoice date |
| `modified_ts_after` | date-time | Modified after UTC timestamp |
| `modified_ts_before` | date-time | Modified before UTC timestamp |
| `page` | integer | Page number |
| `page_size` | integer | Results per page |
| `project` | string | Filter by project |

**Response:** `200 OK`

```json
{
  "count": 123,
  "next": "https://api.wafeq.com/v1/simplified-invoices/?page=2",
  "previous": null,
  "results": [SimplifiedInvoice, ...]
}
```

---

### Retrieve Simplified Invoice

**GET** `/simplified-invoices/{id}/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Response:** `200 OK` -- Returns SimplifiedInvoice object.

---

### Update Simplified Invoice

**PUT** `/simplified-invoices/{id}/`

Full update. All required fields must be provided.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Request Body:** Same schema as Create Simplified Invoice.

**Response:** `200 OK` -- Returns updated SimplifiedInvoice.

---

### Partial Update Simplified Invoice

**PATCH** `/simplified-invoices/{id}/`

Partial update -- only provided fields are modified.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Request Body:** PatchedSimplifiedInvoice -- all fields optional.

**Response:** `200 OK` -- Returns updated SimplifiedInvoice.

---

### Delete Simplified Invoice

**DELETE** `/simplified-invoices/{id}/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Response:** `204 No Content` -- Empty response body.

---

### Download Simplified Invoice PDF

**GET** `/simplified-invoices/{id}/download/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Response:** `200 OK` -- `Content-Type: application/pdf` -- Binary PDF file.

---

### Report Simplified Invoice to Tax Authority

**POST** `/simplified-invoices/{id}/tax-authority/report/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Invoice identifier |

**Request Body:** None.

**Response:** `200 OK`

```json
{
  "status": "string",
  "reported_ts": "2024-01-15T10:30:00Z",
  "metadata": {
    "errors": [],
    "warnings": []
  }
}
```

---

## Simplified Invoice Line Items

### Create Simplified Invoice Line Item

**POST** `/simplified-invoices/{invoice_id}/line-items/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Parent invoice identifier |

**Request Body** (`application/json`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account` | string | Yes | Associated account identifier |
| `description` | string | Yes | Line item description |
| `quantity` | number | Yes | Item quantity |
| `unit_amount` | number | Yes | Price per unit |
| `cost_center` | string | No | Associated cost center |
| `discount` | number or null | No | Discount percentage (>= 0) |
| `item` | string | No | Associated item identifier |
| `tax_rate` | string | No | Tax rate applied |

**Response:** `201 Created` -- Returns SimplifiedInvoiceLineItem with read-only fields (`id`, `line_amount`, `tax_amount`, `created_ts`, `modified_ts`).

---

### List Simplified Invoice Line Items

**GET** `/simplified-invoices/{invoice_id}/line-items/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Parent invoice identifier |

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `page_size` | integer | Results per page |

**Response:** `200 OK`

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [SimplifiedInvoiceLineItem, ...]
}
```

---

### Retrieve Simplified Invoice Line Item

**GET** `/simplified-invoices/{invoice_id}/line-items/{id}/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Parent invoice identifier |
| `id` | string | Yes | Line item identifier |

**Response:** `200 OK` -- Returns SimplifiedInvoiceLineItem object.

---

### Update Simplified Invoice Line Item

**PUT** `/simplified-invoices/{invoice_id}/line-items/{id}/`

Full update. All required fields must be provided.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Parent invoice identifier |
| `id` | string | Yes | Line item identifier |

**Request Body:** Same as Create Simplified Invoice Line Item (required: `account`, `description`, `quantity`, `unit_amount`).

**Response:** `200 OK` -- Returns updated SimplifiedInvoiceLineItem.

---

### Partial Update Simplified Invoice Line Item

**PATCH** `/simplified-invoices/{invoice_id}/line-items/{id}/`

Partial update -- only provided fields are modified.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Parent invoice identifier |
| `id` | string | Yes | Line item identifier |

**Request Body:** PatchedSimplifiedInvoiceLineItem -- all fields optional.

**Response:** `200 OK` -- Returns updated SimplifiedInvoiceLineItem.

---

### Delete Simplified Invoice Line Item

**DELETE** `/simplified-invoices/{invoice_id}/line-items/{id}/`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | string | Yes | Parent invoice identifier |
| `id` | string | Yes | Line item identifier |

**Response:** `204 No Content` -- Empty response body.

---

## Schemas

### Invoice Object

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | string | Yes | Unique identifier |
| `amount` | number | Yes | Total amount including taxes |
| `balance` | number | Yes | Remaining balance |
| `tax_amount` | number | Yes | Total tax amount |
| `contact` | string | No | Customer identifier |
| `currency` | CurrencyEnum | No | ISO currency code |
| `invoice_date` | date | No | Issue date |
| `invoice_due_date` | date | No | Payment deadline |
| `invoice_number` | string | No | Unique invoice number |
| `status` | string | No | DRAFT, SENT, or FINALIZED |
| `language` | string | No | "ar" or "en" |
| `tax_amount_type` | string | No | TAX_INCLUSIVE or TAX_EXCLUSIVE |
| `line_items` | array | No | InvoiceLineItem objects |
| `credit_notes` | array | No | InvoiceCreditNote objects |
| `attachments` | array | No | File/document URLs |
| `branch` | string or null | No | Branch identifier |
| `project` | string or null | No | Project identifier |
| `warehouse` | string or null | No | Warehouse identifier |
| `discount_amount` | number | No | Discount (0 to 10^16) |
| `discount_account` | string | No | Account for discount |
| `discount_cost_center` | string | No | Cost center for discount |
| `discount_tax_rate` | string | No | Tax rate on discount |
| `notes` | string | No | Additional comments |
| `reference` | string | No | Reference code |
| `purchase_order` | string | No | PO number |
| `place_of_supply` | string | No | UAE emirate or OUTSIDE_UAE |
| `created_ts` | date-time | Yes | UTC creation timestamp |
| `modified_ts` | date-time | Yes | UTC modification timestamp |

### InvoiceLineItem Object

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | string | Yes | Unique identifier |
| `account` | string | No | Associated account |
| `description` | string | No | Line item description |
| `quantity` | number | No | Item quantity |
| `unit_amount` | number | No | Price per unit |
| `line_amount` | number | Yes | Total (quantity x unit_amount) |
| `tax_amount` | number | Yes | Tax amount for line |
| `discount` | number or null | No | Discount percentage |
| `tax_rate` | string | No | Applied tax rate |
| `cost_center` | string | No | Associated cost center |
| `item` | string | No | Associated item |
| `created_ts` | date-time | Yes | UTC creation timestamp |
| `modified_ts` | date-time | Yes | UTC modification timestamp |

### InvoiceCreditNote Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `credit_note` | string | Yes | Credit note identifier |
| `amount` | number | Yes | Applied amount |
| `date` | date | No | Application date |

### SimplifiedInvoice Object

Same as Invoice with these differences:
- **No** `invoice_due_date` field
- **No** `balance` field
- **No** `credit_notes` field
- **Has** `paid_through_account` (string, required) -- payment account
- **Status values:** DRAFT or PAID (not SENT/FINALIZED)
- **No** `purchase_order` field
- **No** `discount_amount`/`discount_account`/`discount_cost_center`/`discount_tax_rate` fields

### SimplifiedInvoiceLineItem Object

Same schema as InvoiceLineItem.

### APIInvoice Object (Bulk)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `invoice_number` | string | Invoice number |
| `amount` | number | Total amount |
| `currency` | CurrencyEnum | Currency code |
| `invoice_date` | date-time | Invoice date |
| `created_at` | date-time | Creation timestamp |
| `status` | string | Invoice status |
| `language` | LanguageEnum | "ar" or "en" |
| `tax_amount_type` | TaxAmountTypeEnum | TAX_INCLUSIVE or TAX_EXCLUSIVE |
| `contact` | APIEntityContact | Contact details |
| `line_items` | array (1-100) | APIInvoiceLineItem objects |
| `notes` | string | Additional notes |
| `reference` | string | Reference |
| `paid_through_account` | string | Payment account |

### APIEntityContact Object

| Field | Type | Required |
|-------|------|----------|
| `name` | string | Yes |
| `email` | string | No |
| `address` | string | No |
| `city` | string | No |
| `country` | string | No |
| `tax_registration_number` | string | No |

### APIInvoiceLineItem Object

| Field | Type | Required |
|-------|------|----------|
| `name` | string | Yes |
| `description` | string | Yes |
| `price` | number | Yes |
| `quantity` | number | Yes |
| `account` | string | No |
| `discount` | object | No |
| `tax_rate` | object | No |

### TaxAuthorityReport Response

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Reporting status |
| `reported_ts` | date-time | When reported |
| `metadata.errors` | array | Error objects |
| `metadata.warnings` | array | Warning objects |

### Key Enums

- **CurrencyEnum:** AED, SAR, USD, EUR, GBP, CAD, CHF, JPY, INR, CNY, AUD, and 150+ more ISO currency codes
- **LanguageEnum:** `ar` (Arabic), `en` (English)
- **TaxAmountTypeEnum:** `TAX_INCLUSIVE`, `TAX_EXCLUSIVE`
- **Status730Enum** (Standard Invoice): `DRAFT`, `SENT`, `FINALIZED`
- **SimplifiedInvoiceStatusEnum:** `DRAFT`, `PAID`
- **PlaceOfSupply:** `ABU_DHABI`, `AJMAN`, `DUBAI`, `FUJAIRAH`, `RAS_AL_KHAIMAH`, `SHARJAH`, `UMM_AL_QUWAIN`, `OUTSIDE_UAE`
