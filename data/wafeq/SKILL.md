---
name: wafeq-api
description: Complete Wafeq accounting & e-invoicing API reference for the Middle East (UAE, Saudi Arabia). Use when building integrations with Wafeq, creating/managing invoices (standard, simplified, bulk), contacts, accounts, bills, expenses, credit/debit notes, payments, payslips, quotes, items, files, manual journals, reports (P&L, balance sheet, cash flow, trial balance), branches, cost centers, employees, projects, warehouses, or any task involving the Wafeq REST API.
metadata: {"openclaw":{"emoji":"🧾","homepage":"https://wafeq.com","primaryEnv":"WAFEQ_API_KEY","requires":{"env":["WAFEQ_API_KEY"]}}}
---

# Wafeq API Skill

Complete API reference for the Wafeq accounting and e-invoicing platform.

## Setup

To use this skill, you need a Wafeq API key:

1. Log in to [Wafeq](https://app.wafeq.com)
2. Go to **Settings → API Keys** ([direct link](https://app.wafeq.com/c/api-keys))
3. Create a new API key
4. Set the environment variable:
   ```bash
   export WAFEQ_API_KEY='your-key-here'
   ```
   Or configure in `~/.openclaw/openclaw.json`:
   ```json
   { "skills": { "entries": { "wafeq-api": { "apiKey": "your-key-here" } } } }
   ```

> ⚠️ **Security:** Never hardcode your API key in code, prompts, or skill files. Always use the `WAFEQ_API_KEY` environment variable or configure it via `skills.entries.wafeq-api.apiKey` in `~/.openclaw/openclaw.json`.

You can validate your setup by running `scripts/setup.sh` from the plugin root.

## Quick Reference

- **Base URL:** `https://api.wafeq.com/v1/`
- **Auth (API Key):** `Authorization: Api-Key $WAFEQ_API_KEY` — get keys at `https://app.wafeq.com/c/api-keys`
- **Auth (OAuth2):** `Authorization: Bearer <access_token>` — contact Wafeq for client credentials
- **Idempotency:** `X-Wafeq-Idempotency-Key: <uuid-v4>` on POST/PUT/PATCH/DELETE (1hr cache, replayed response includes `X-Wafeq-Idempotent-Replayed: true`)
- **Pagination:** `?page=1&page_size=25` — response: `{ count, next, previous, results[] }`
- **Content-Type:** `application/json`
- **Currency codes:** ISO 4217 (full list in [references/enums.md](references/enums.md))
- **Entity IDs:** Prefixed strings (e.g. `cnt_...`, `acc_...`, `inv_...`)

## Standard CRUD Pattern

Most resources follow: POST `/{resource}/`, GET `/{resource}/`, GET `/{resource}/{id}/`, PUT `/{resource}/{id}/`, PATCH `/{resource}/{id}/`, DELETE `/{resource}/{id}/`. Some also have GET `/{resource}/{id}/download/` for PDF.

Line items are nested: `/{resource}/{parent_id}/line-items/` with the same CRUD pattern.

## Reference Files

| File | Contents |
|------|----------|
| [references/core-concepts.md](references/core-concepts.md) | Authentication (API Key + OAuth2), idempotency, error handling, quickstart guide, invoice creation walkthrough, use cases (B2B, B2C, e-commerce, expense management) |
| [references/enums.md](references/enums.md) | All 18 enum types: currencies, statuses, classifications, tax types, discount types, languages |
| [references/invoices.md](references/invoices.md) | Standard invoices, invoice line items, bulk invoices (api-invoices), simplified invoices, simplified invoice line items — full CRUD + schemas |
| [references/accounts-banking-contacts.md](references/accounts-banking-contacts.md) | Chart of accounts, bank accounts, bank ledger transactions, bank statement transactions, contacts, beneficiaries — full CRUD + schemas |
| [references/bills-expenses-notes.md](references/bills-expenses-notes.md) | Bills, bill line items, expenses, credit notes, credit note line items, bulk credit notes, debit notes, debit note line items — full CRUD + schemas |
| [references/quotes-payments-remaining.md](references/quotes-payments-remaining.md) | Quotes, payments, payment requests, payslips, items, files, manual journals, journal line items, reports (balance sheet, P&L, cash flow, trial balance), organization, tax rates, branches, cost centers, employees, projects, warehouses — full CRUD + schemas |

## Common Workflows

### Create and Send an Invoice
1. Create contact: `POST /contacts/`
2. Get revenue account: `GET /accounts/?classification=REVENUE`
3. Get tax rates: `GET /tax-rates/`
4. Create invoice: `POST /invoices/` (with `line_items`, `contact`, `currency`, `invoice_date`, `invoice_due_date`, `invoice_number`)
5. Report to tax authority: `POST /invoices/{id}/tax-authority/report/`
6. Download PDF: `GET /invoices/{id}/download/`

### Bulk Send Invoices (E-Commerce / High Volume)
1. `POST /api-invoices/bulk_send/` with array of invoice objects including `channels` for email delivery
2. Response: `{ "queued": N }`
3. Generate summary: `GET /api-invoices/summary/`

### Record Expense
1. Get expense account: `GET /accounts/?classification=EXPENSE`
2. Create expense: `POST /expenses/` with `paid_through_account`, `contact`, `date`, `currency`, `tax_amount_type`, `line_items`

### Record Payment Against Invoice
1. `POST /payments/` with `invoice_payments` array linking to invoice IDs and amounts

### Generate Financial Reports
- Balance Sheet: `GET /reports/balance-sheet/?currency=SAR&date=2025-12-31`
- Profit & Loss: `GET /reports/profit-and-loss/?currency=SAR&date_after=2025-01-01&date_before=2025-12-31`
- Cash Flow: `GET /reports/cash-flow/?currency=SAR&date_after=2025-01-01&date_before=2025-12-31`
- Trial Balance: `GET /reports/trial-balance/?from_date=2025-01-01&to_date=2025-12-31`

### Quote to Invoice Conversion
1. Create quote: `POST /quotes/`
2. Convert to invoice: `POST /quotes/{id}/invoice/`

## Important Notes

- **Tax authority reporting** is available for invoices, simplified invoices, and credit notes via `POST /{resource}/{id}/tax-authority/report/`
- **Simplified invoices** are for B2C transactions (no buyer tax registration required)
- **Standard invoices** are for B2B transactions
- **Place of supply** field is UAE-specific (emirate codes or `OUTSIDE_UAE`)
- Use `reference` fields as unique identifiers to prevent duplicate creation
