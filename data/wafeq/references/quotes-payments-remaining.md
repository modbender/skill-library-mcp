# Wafeq API: Quotes, Payments, Payslips, Items, Files, Journals, Reports & Entity Management

Base URL: `https://api.wafeq.com/v1`
Auth: `Authorization: Api-Key {your_api_key}`
Idempotency: `X-Wafeq-Idempotency-Key: {uuid}` (optional on write operations)

---

## 1. Quotes

### Quote Object (Estimate)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| quote_number | string | yes | Quote reference |
| quote_date | date | yes | Issuance date |
| contact | string | yes | Customer identifier |
| currency | CurrencyEnum | yes | ISO 4217 code |
| amount | number | read-only | Total including taxes |
| tax_amount | number | read-only | Total tax |
| tax_amount_type | enum | no | TAX_INCLUSIVE, TAX_EXCLUSIVE |
| status | enum | no | DRAFT (default), SENT, INVOICED |
| language | enum | no | en (default), ar |
| line_items | array | yes | EstimateLineItem objects |
| notes | string | no | Additional comments |
| purchase_order | string | no | PO reference |
| reference | string | no | Reference code |
| discount_amount | number | no | Discount value |
| discount_account | string | no | Discount booking account |
| discount_cost_center | string | no | Cost center for discount |
| discount_tax_rate | string | no | Tax rate on discount |
| branch | string/null | no | Branch association |
| project | string/null | no | Project association |
| attachments | array[string] | no | File references |
| created_ts | datetime | read-only | UTC creation timestamp |
| modified_ts | datetime | read-only | UTC modification timestamp |

### EstimateLineItem Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| description | string | yes | Item description |
| quantity | number | yes | Quantity |
| unit_amount | number | yes | Price per unit |
| line_amount | number | read-only | quantity x unit_amount |
| tax_amount | number | read-only | Tax calculated |
| discount | number/null | no | Percentage discount (min: 0) |
| tax_rate | string | no | Applied tax rate |
| item | string | no | Item reference |
| cost_center | string | no | Cost center |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### Quote Endpoints

#### POST /quotes/ -- Create Quote
- **Request:** Estimate object (JSON, form-urlencoded, multipart)
- **Response:** 201 Created -- full Estimate object

#### GET /quotes/ -- List Quotes
- **Query params:** branch, contact, created_ts_after, created_ts_before, estimate_date, modified_ts_after, modified_ts_before, page, page_size, project, quote_date, status
- **Response:** 200 -- PaginatedEstimateList {count, next, previous, results[]}

#### GET /quotes/{id}/ -- Retrieve Quote
- **Path:** id (string, required)
- **Response:** 200 -- Estimate object

#### PUT /quotes/{id}/ -- Update Quote
- **Path:** id (string, required)
- **Request:** Estimate object (contact required)
- **Response:** 200 -- Updated Estimate

#### PATCH /quotes/{id}/ -- Partial Update Quote
- **Path:** id (string, required)
- **Request:** PatchedEstimate (all fields optional)
- **Response:** 200 -- Updated Estimate

#### DELETE /quotes/{id}/ -- Delete Quote
- **Path:** id (string, required)
- **Response:** 204 No Content

#### GET /quotes/{id}/download/ -- Download Quote PDF
- **Path:** id (string, required)
- **Response:** 200 -- application/pdf binary

#### POST /quotes/{id}/invoice/ -- Convert Quote to Invoice
- **Path:** id (string, required)
- **Request:** No body required
- **Response:** 201 Created -- Invoice object (with invoice_number, balance, invoice_date, invoice_due_date, etc.)

### Quote Line Item Endpoints

#### POST /quotes/{quote_id}/line-items/ -- Create Line Item
- **Path:** quote_id (string, required)
- **Request:** EstimateLineItem (description, quantity, unit_amount required)
- **Response:** 201 Created

#### GET /quotes/{quote_id}/line-items/ -- List Line Items
- **Path:** quote_id (string, required)
- **Query:** page, page_size
- **Response:** 200 -- PaginatedEstimateLineItemList

#### GET /quotes/{quote_id}/line-items/{id}/ -- Retrieve Line Item
- **Path:** quote_id, id (both required)
- **Response:** 200 -- EstimateLineItem

#### PUT /quotes/{quote_id}/line-items/{id}/ -- Update Line Item
- **Path:** quote_id, id (both required)
- **Request:** EstimateLineItem (description, quantity, unit_amount required)
- **Response:** 200

#### PATCH /quotes/{quote_id}/line-items/{id}/ -- Partial Update Line Item
- **Path:** quote_id, id (both required)
- **Request:** PatchedEstimateLineItem (all optional)
- **Response:** 200

#### DELETE /quotes/{quote_id}/line-items/{id}/ -- Delete Line Item
- **Path:** quote_id, id (both required)
- **Response:** 204 No Content

---

## 2. Payments

### Payment Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| amount | number | yes | Total including fees (must exceed 0) |
| currency | CurrencyEnum | yes | ISO 4217 code |
| date | date | yes | Payment date |
| paid_through_account | string | yes | Valid payment account |
| contact | string | no | Contact identifier |
| employee | string | no | Employee (required for payslip payments) |
| cost_center | string/null | no | Cost center |
| project | string/null | no | Project |
| reference | string | no | Payment reference |
| payment_fees | number | no | Must exceed 0 if set |
| payment_fees_account | string/null | no | Required if payment_fees set |
| invoice_payments | array | no | InvoicePayment objects |
| bill_payments | array | no | BillPayment objects |
| credit_note_payments | array | no | CreditNotePayment objects |
| debit_note_payments | array | no | DebitNotePayment objects |
| payslip_payments | array | no | PayslipPayment objects |
| payment_request | string | read-only | Associated payment request |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### Nested Payment Objects (InvoicePayment, BillPayment, CreditNotePayment, DebitNotePayment, PayslipPayment)

| Field | Type | Required |
|-------|------|----------|
| amount | number | yes |
| amount_to_pcy | number | yes |
| invoice/bill/credit_note/debit_note/payslip | string | yes (respective doc ID) |
| created_ts | datetime | read-only |
| modified_ts | datetime | read-only |

### Payment Endpoints

#### POST /payments/ -- Create Payment
- **Request:** Payment object
- **Response:** 201 Created

#### GET /payments/ -- List Payments
- **Query:** contact, created_ts_after, created_ts_before, date, modified_ts_after, modified_ts_before, page, page_size, paid_through_account, payment_fees_account, project, reference
- **Response:** 200 -- PaginatedPaymentList

#### GET /payments/{id}/ -- Retrieve Payment
- **Response:** 200 -- Payment object

#### PUT /payments/{id}/ -- Update Payment
- **Request:** Payment object (amount, date, currency, paid_through_account required)
- **Response:** 200

#### PATCH /payments/{id}/ -- Partial Update Payment
- **Request:** PatchedPayment (all optional)
- **Response:** 200

#### DELETE /payments/{id}/ -- Delete Payment
- **Response:** 204 No Content

#### GET /payments/{id}/download/ -- Download Payment PDF
- **Response:** 200 -- application/pdf binary

---

## 3. Payment Requests

### PaymentRequest Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| amount | number/null | yes | Non-negative, max <10^16 |
| currency | CurrencyEnum | yes | ISO 4217 code |
| charge_type | enum | yes | OUR, BEN, SHA |
| bank_account | string | yes | Associated bank account |
| beneficiary | string | yes | Beneficiary identifier |
| beneficiary_name | string | read-only | Full name |
| beneficiary_address | string | read-only | Full address |
| contact | string | yes | Contact identifier |
| details_of_payment | string | yes | Max 200 chars |
| reference | string | yes | Tracking reference |
| send_payment_advice | boolean | yes | Email flag |
| iban | string | read-only | IBAN |
| swift | string | read-only | SWIFT/BIC |
| status | enum | read-only | DRAFT, PENDING_APPROVAL, PENDING_RELEASE, VALIDATED, QUEUED, PROCESSING, RELEASED, PROCESSED, ERROR, REJECTED, NOT_FOUND, FETCHING_STATUS, DELETED |
| date | date | read-only | Auto-set creation date |
| attachments | array[string] | no | Attachment IDs |
| bills | array[string] | no | Max 1 bill |
| cost_center | string/null | no | Cost center |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### Payment Request Endpoints

#### POST /payment_requests/ -- Create Payment Request
- **Response:** 201 Created

#### GET /payment_requests/ -- List Payment Requests
- **Query:** amount_min, amount_max, created_ts_after, created_ts_before, currency, date_after, date_before, modified_ts_after, modified_ts_before, status, page, page_size
- **Response:** 200 -- PaginatedPaymentRequestList

#### GET /payment_requests/{id}/ -- Retrieve Payment Request
- **Response:** 200 -- PaymentRequest

#### PUT /payment_requests/{id}/ -- Update Payment Request
- **Response:** 200

#### PATCH /payment_requests/{id}/ -- Partial Update Payment Request
- **Response:** 200

#### DELETE /payment_requests/{id}/ -- Delete Payment Request
- **Response:** 204 No Content

---

## 4. Payslips

### Payslip Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| employee | string | yes | Employee reference |
| payslip_number | string | yes | Unique number |
| payslip_date | date | yes | Issuance date |
| currency | CurrencyEnum | yes | ISO 4217 |
| amount | number | read-only | Total amount |
| balance | number | read-only | Remaining balance |
| status | enum | no | DRAFT (default), POSTED |
| branch | string/null | no | Branch association |
| language | enum | no | ar, en |
| pay_items | array | yes | PayItem objects |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### PayItem Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| description | string | yes | Line description |
| amount | number | yes | Unit amount (-10^16 to 10^16) |
| account | string | yes | Associated account |
| cost_center | string/null | no | Cost center |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### Payslip Endpoints

#### POST /payslips/ -- Create Payslip
- **Response:** 201 Created

#### GET /payslips/ -- List Payslips
- **Query:** branch, employee, project, payslip_date, created_ts_after, created_ts_before, modified_ts_after, modified_ts_before, page, page_size
- **Response:** 200 -- PaginatedPayslipList

#### GET /payslips/{id}/ -- Retrieve Payslip
- **Response:** 200 -- Payslip

#### PUT /payslips/{id}/ -- Update Payslip
- **Response:** 200

#### PATCH /payslips/{id}/ -- Partial Update Payslip
- **Response:** 200

#### DELETE /payslips/{id}/ -- Delete Payslip
- **Response:** 204 No Content

#### GET /payslips/{id}/download/ -- Download Payslip PDF
- **Response:** 200 -- application/pdf binary

### Pay Item Endpoints

#### POST /payslips/{payslip_id}/pay-items/ -- Create Pay Item
- **Request:** PayItem (account, amount, description required)
- **Response:** 201 Created

#### GET /payslips/{payslip_id}/pay-items/ -- List Pay Items
- **Query:** page, page_size
- **Response:** 200 -- PaginatedPayItemList

#### GET /payslips/{payslip_id}/pay-items/{id}/ -- Retrieve Pay Item
- **Response:** 200 -- PayItem

#### PUT /payslips/{payslip_id}/pay-items/{id}/ -- Update Pay Item
- **Request:** PayItem (account, amount, description required)
- **Response:** 200

#### PATCH /payslips/{payslip_id}/pay-items/{id}/ -- Partial Update Pay Item
- **Request:** PatchedPayItem (all optional)
- **Response:** 200

#### DELETE /payslips/{payslip_id}/pay-items/{id}/ -- Delete Pay Item
- **Response:** 204 No Content

---

## 5. Items (Products/Services)

### Item Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| name | string | yes | Max 200 chars |
| description | string | no | Item description |
| sku | string | no | Max 200 chars |
| external_id | string | no | Max 255 chars |
| unit_cost | number/null | no | Cost per unit |
| unit_price | number/null | no | Selling price |
| is_active | boolean | no | Default: true |
| is_tracked_inventory | boolean | no | Default: false |
| expense_account | string/null | no | Expense account |
| revenue_account | string/null | no | Revenue account |
| purchase_tax_rate | string/null | no | Tax on purchases |
| revenue_tax_rate | string/null | no | Tax on sales |
| tax_authority | object/null | no | Tax authority with metadata (default_exemption_reason) |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### Item Endpoints

#### POST /items/ -- Create Item
- **Request:** Item (name required)
- **Response:** 201 Created

#### GET /items/ -- List Items
- **Query:** page, page_size
- **Response:** 200 -- PaginatedItemList

#### GET /items/{id}/ -- Retrieve Item
- **Response:** 200 -- Item

#### PUT /items/{id}/ -- Update Item
- **Request:** Item (name required)
- **Response:** 200

#### PATCH /items/{id}/ -- Partial Update Item
- **Request:** PatchedItem (all optional)
- **Response:** 200

#### DELETE /items/{id}/ -- Delete Item
- **Response:** 204 No Content

---

## 6. Files

### File Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier (e.g. att_MB8Qx...) |
| mime_type | string | yes | Max 100 chars |
| file | URI | no | File content URL |
| file_size | integer/null | no | Size in bytes |
| original_filename | string | no | Max 200 chars |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### File Endpoints

#### POST /files/ -- Upload File (multipart)
- **Content-Type:** multipart/form-data
- **Request body:** file (binary, required)
- **Response:** 201 Created -- File object

#### POST /files/raw/ -- Upload File (raw/advance)
- **Content-Type:** */* (any binary)
- **Header:** Content-Disposition: "attachment; filename=invoice.pdf"
- **Request body:** raw binary file content
- **Response:** 201 Created -- File object

#### GET /files/ -- List Files
- **Query:** created_ts_after, created_ts_before, file_size_min, file_size_max, mime_type, modified_ts_after, modified_ts_before, original_filename, page, page_size
- **Response:** 200 -- PaginatedFileList

#### GET /files/{id}/ -- Retrieve File
- **Response:** 200 -- File object

#### DELETE /files/{id}/ -- Delete File
- **Response:** 204 No Content

---

## 7. Manual Journals

### ManualJournal Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| serial_number | string | read-only | Auto-generated |
| date | date | yes | Journal date |
| notes | string | no | Default: "" |
| reference | string | no | Default: "" |
| tax_amount_type | enum | no | TAX_EXCLUSIVE (default), TAX_INCLUSIVE |
| line_items | array | no | ManualJournalLineItem objects |
| attachments | array[string] | no | Attachment IDs |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### ManualJournalLineItem Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| account | string | yes | Account identifier |
| amount | number | yes | Line amount |
| amount_to_bcy | number | yes | Base currency amount |
| currency | CurrencyEnum | yes | ISO 4217 |
| description | string | yes | Description |
| exchange_rate | number | no | Conversion rate |
| tax_rate | string | no | Tax rate ID |
| tax_amount | number | no | Tax calculated |
| cost_center | string | no | Cost center |
| contact | string | no | Contact ID |
| branch | string/null | no | Branch |
| project | string/null | no | Project |
| place_of_supply | enum | no | UAE emirates or OUTSIDE_UAE |
| manual_journal | string | read-only | Parent journal ID |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### Manual Journal Endpoints

#### POST /manual-journals/ -- Create Manual Journal
- **Response:** 201 Created

#### GET /manual-journals/ -- List Manual Journals
- **Query:** created_ts_after, created_ts_before, date_after, date_before, modified_ts_after, modified_ts_before, page, page_size, reference
- **Response:** 200 -- PaginatedManualJournalList

#### GET /manual-journals/{id}/ -- Retrieve Manual Journal
- **Response:** 200 -- ManualJournal

#### PUT /manual-journals/{id}/ -- Update Manual Journal
- **Request:** ManualJournal (date required)
- **Response:** 200

#### PATCH /manual-journals/{id}/ -- Partial Update Manual Journal
- **Request:** PatchedManualJournal (all optional)
- **Response:** 200

#### DELETE /manual-journals/{id}/ -- Delete Manual Journal
- **Response:** 204 No Content

---

## 8. Journal Line Items (Read-Only)

These are system-level journal entries from all document types (invoices, bills, payments, manual journals, etc.).

### JournalLineItem Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| account | string | yes | Account ID |
| amount | number | yes | Monetary amount |
| amount_to_bcy | number | read-only | Base currency amount |
| currency | CurrencyEnum | read-only | ISO 4217 |
| description | string | yes | Description |
| journal | string | yes | Journal identifier |
| contact | string | yes | Contact ID |
| branch | string/null | no | Branch |
| project | string/null | no | Project |
| cost_center | string | no | Cost center |
| item | string | no | Item reference |
| tax_rate | string | no | Tax rate |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### Journal Line Item Endpoints

#### GET /journal-line-items/ -- List Journal Line Items
- **Pagination:** cursor-based (cursor param instead of page)
- **Query:** account, account_classification (ASSET/EQUITY/EXPENSE/LIABILITY/REVENUE), branch, contact, created_ts_after, created_ts_before, currency, cursor, date_after, date_before, journal, modified_ts_after, modified_ts_before, page_size, project, tax_rate
- **Response:** 200 -- {next, previous, results[]}

#### GET /journal-line-items/{id}/ -- Retrieve Journal Line Item
- **Response:** 200 -- JournalLineItem

---

## 9. Reports

### GET /reports/balance-sheet/ -- Balance Sheet
- **Required query:** date (date, must be last day of month/year), period_count (integer, 0-11)
- **Optional query:** currency, group_by (month/year), branch__in, contact__in, cost_center__in, project__in
- **Response:** 200 -- Array of report objects with overview, columns, rows (hierarchical with group: ASSET/LIABILITY/EQUITY)

### GET /reports/cash-flow/ -- Cash Flow Statement
- **Required query:** date_after (first day of month/year), date_before (last day of month/year)
- **Optional query:** currency, group_by (month/year), branch__in, contact__in, cost_center__in, project__in
- **Response:** 200 -- Report with overview, columns, rows (group: CFO/CFI/CFF/FREE_CASH_FLOW)

### GET /reports/profit-and-loss/ -- Profit and Loss
- **Required query:** date_after (first day), date_before (last day)
- **Optional query:** currency, group_by (month/year), branch__in, contact__in, cost_center__in, project__in
- **Response:** 200 -- Report with overview, columns, rows (revenue/expense hierarchy)

### GET /reports/trial-balance/ -- Trial Balance
- **Optional query:** from_date, to_date, include_zero_balances (bool), with_pnl_openings (bool), branch__in, contact__in, cost_center__in, project__in
- **Response:** 200 -- Report with overview, rows (accounts with opening_balance_to_bcy, debit_to_bcy, credit_to_bcy, running_balance_to_bcy)

### Report Response Structure (common)

```
{
  "overview": { id, label, created_ts, currency, date/date_from/date_to, filters, group_by },
  "columns": [{ id, label, metadata }],
  "rows": [
    {
      id, label, group, metadata,
      summary: { id, label, sub_totals: [number] },
      children: [{ id, label, values: [number], children: [], summary }]
    }
  ]
}
```

---

## 10. Organization

### GET /organization/ -- Retrieve Organization
- **Response:** 200 -- Organization object (all fields read-only)

| Field | Type | Description |
|-------|------|-------------|
| id | string | Organization ID |
| name | {en, ar} | Dual-language name |
| branches | array[Branch] | Organization branches |
| warehouses | array[Warehouse] | Organization warehouses |
| users | array[{id, email}] | Organization users |
| financial_settings | object | Base currency, tax numbers, country, location |
| created_ts | datetime | UTC timestamp |
| modified_ts | datetime | UTC timestamp |

---

## 11. Tax Rates

### TaxRate Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| name | string | yes | Concise identifier |
| friendly_name | string | read-only | Display name |
| description | string | no | Default: "" |
| rate | number | yes | Decimal value (-10000 to 10000) |
| tax_type | enum | yes | SALES, PURCHASES, REVERSE_CHARGE, OUT_OF_SCOPE |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### GET /tax-rates/ -- List Tax Rates
- **Query:** created_ts_after, created_ts_before, modified_ts_after, modified_ts_before, tax_type, page, page_size
- **Response:** 200 -- PaginatedTaxRateList

---

## 12. Branches

### Branch Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| name | {en, ar} | yes | Dual-language name |
| address | {en, ar} | yes | Full address |
| city | {en, ar} | yes | City |
| district | {en, ar} | yes | District/area |
| building_number | string | yes | Building ID |
| postal_code | string | yes | ZIP/postal |
| phone | string | yes | Contact number |
| state | string | read-only | Emirate (UAE) |
| is_active | boolean | no | Default: true |

Dual-language model: `{ en: string (required), ar: string (optional) }`

### Branch Endpoints

#### POST /branches/ -- Create Branch
- **Response:** 201 Created

#### GET /branches/ -- List Branches
- **Query:** page, page_size
- **Response:** 200 -- PaginatedBranchList

#### GET /branches/{id}/ -- Retrieve Branch
- **Response:** 200 -- Branch

#### PUT /branches/{id}/ -- Update Branch
- **Response:** 200

#### PATCH /branches/{id}/ -- Partial Update Branch
- **Response:** 200

#### DELETE /branches/{id}/ -- Delete Branch
- **Response:** 204 No Content

---

## 13. Cost Centers

### CostCenter Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| name_en | string | yes | Max 200 chars |
| name_ar | string | yes | Max 200 chars |
| is_active | boolean | yes | Active status |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### Cost Center Endpoints

#### POST /cost-centers/ -- Create Cost Center
- **Request:** name_en, name_ar, is_active (all required)
- **Response:** 201 Created

#### GET /cost-centers/ -- List Cost Centers
- **Query:** page, page_size
- **Response:** 200 -- PaginatedCostCenterList

#### GET /cost-centers/{id}/ -- Retrieve Cost Center
- **Response:** 200 -- CostCenter

#### PUT /cost-centers/{id}/ -- Update Cost Center
- **Response:** 200

#### PATCH /cost-centers/{id}/ -- Partial Update Cost Center
- **Response:** 200

#### DELETE /cost-centers/{id}/ -- Delete Cost Center
- **Response:** 204 No Content

---

## 14. Employees

### Employee Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| name | string | yes | Full name |
| email | string | no | Email format |
| address | string | no | Street address |
| city | string | no | City |
| country | CountryEnum | no | ISO 3166-1 alpha-2 (250+ codes: SA, AE, US, GB, etc.) |
| date_hired | date | no | YYYY-MM-DD |
| user | string/null | no | Linked user ID |
| reimbursements_account | string | read-only | Reimbursement account |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### Employee Endpoints

#### POST /employees/ -- Create Employee
- **Request:** name required
- **Response:** 201 Created

#### GET /employees/ -- List Employees
- **Query:** country, created_ts_after, created_ts_before, modified_ts_after, modified_ts_before, page, page_size
- **Response:** 200 -- PaginatedEmployeeList

#### GET /employees/{id}/ -- Retrieve Employee
- **Response:** 200 -- Employee

#### PUT /employees/{id}/ -- Update Employee
- **Request:** name required
- **Response:** 200

#### PATCH /employees/{id}/ -- Partial Update Employee
- **Response:** 200

#### DELETE /employees/{id}/ -- Delete Employee
- **Response:** 204 No Content

---

## 15. Projects

### Project Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| name | string | yes | Max 200 chars |
| attachments | array[string] | no | Linked attachments |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### Project Endpoints

#### POST /projects/ -- Create Project
- **Request:** name required
- **Response:** 201 Created

#### GET /projects/ -- List Projects
- **Query:** page, page_size
- **Response:** 200 -- PaginatedProjectList

#### GET /projects/{id}/ -- Retrieve Project
- **Response:** 200 -- Project

#### PUT /projects/{id}/ -- Update Project
- **Response:** 200

#### PATCH /projects/{id}/ -- Partial Update Project
- **Response:** 200

#### DELETE /projects/{id}/ -- Delete Project
- **Response:** 204 No Content

---

## 16. Warehouses

### Warehouse Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | read-only | Unique identifier |
| code | string | yes | Unique code |
| name | {en, ar} | yes | Dual-language |
| account | string | yes | Associated account |
| address | {en, ar} | yes | Full address |
| city | {en, ar} | yes | City location |
| district | {en, ar} | yes | District/area |
| building_number | string | yes | Building ID |
| postal_code | string | yes | ZIP/postal |
| phone | string | yes | Contact number |
| state | string | read-only | Emirate (UAE) |
| is_active | boolean | no | Default: true |
| created_ts | datetime | read-only | UTC timestamp |
| modified_ts | datetime | read-only | UTC timestamp |

### Warehouse Endpoints

#### POST /warehouses/ -- Create Warehouse
- **Response:** 201 Created

#### GET /warehouses/ -- List Warehouses
- **Query:** page, page_size
- **Response:** 200 -- PaginatedWarehouseList

#### GET /warehouses/{id}/ -- Retrieve Warehouse
- **Response:** 200 -- Warehouse

#### PUT /warehouses/{id}/ -- Update Warehouse
- **Response:** 200

#### PATCH /warehouses/{id}/ -- Partial Update Warehouse
- **Response:** 200

#### DELETE /warehouses/{id}/ -- Delete Warehouse
- **Response:** 204 No Content
