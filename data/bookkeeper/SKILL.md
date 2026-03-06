---
name: autonomous-bookkeeper
description: Meta-skill for pre-accounting automation by orchestrating gmail, deepread-ocr, stripe-api, and xero. Use when users need invoice intake from email, structured field extraction, payment verification, and accounting entry creation with reconciliation-ready status.
homepage: https://clawhub.ai
user-invocable: true
disable-model-invocation: false
metadata: {"openclaw":{"emoji":"ledger","requires":{"bins":["python3","npx"],"env":["MATON_API_KEY","DEEPREAD_API_KEY"],"config":[]},"note":"Requires local installation of gmail, deepread-ocr, stripe-api, and xero."}}
---

# Purpose

Automate preparatory bookkeeping from incoming email to accounting records.

Core objective:
1. detect invoice email,
2. extract structured invoice data,
3. verify payment event,
4. create accounting entry and reconciliation status.

This is orchestration logic across upstream tools; it is not a replacement for financial controls.

# Required Installed Skills

- `gmail` (inspected latest: `1.0.6`)
- `deepread-ocr` (inspected latest: `1.0.6`)
- `stripe-api` (inspected latest: `1.0.8`)
- `xero` (inspected latest: `1.0.4`)

Install/update:

```bash
npx -y clawhub@latest install gmail
npx -y clawhub@latest install deepread-ocr
npx -y clawhub@latest install stripe-api
npx -y clawhub@latest install xero
npx -y clawhub@latest update --all
```

# Required Credentials

- `MATON_API_KEY` (for Gmail, Stripe, Xero through Maton gateway)
- `DEEPREAD_API_KEY` (for OCR extraction)

Preflight:

```bash
echo "$MATON_API_KEY" | wc -c
echo "$DEEPREAD_API_KEY" | wc -c
```

If missing, stop before any bookkeeping action.

# Inputs the LM Must Collect First

- `company_base_currency`
- `invoice_keywords` (default: invoice, rechnung, receipt, quittung)
- `vendor_rules` (for example AWS -> Hosting expense account)
- `date_tolerance_days` for matching (default: 3)
- `amount_tolerance` (default: exact, or configurable small tolerance)
- `auto_post_policy` (`manual-review`, `auto-if-high-confidence`)
- `attachment_policy` (`store-link`, `attach-binary-if-supported`)

Do not auto-post financial records without explicit policy.

# Tool Responsibilities

## Gmail (`gmail`)

Use for intake and attachment discovery.

Relevant behavior:
- query messages with Gmail operators (for example `has:attachment`, `subject:invoice`, sender filters)
- fetch message metadata and full payload for parsing
- label/update messages after processing (for traceability)

## DeepRead OCR (`deepread-ocr`)

Use for extracting structured fields from invoice PDFs/images.

Relevant behavior:
- async processing (`queued` -> `completed`/`failed`)
- schema-driven extraction
- field-level `hil_flag` and reason for uncertainty
- webhook or polling modes

## Stripe (`stripe-api`)

Use for payment-side verification.

Relevant behavior:
- query charges/payment_intents/invoices/balance transactions
- verify amount, currency, status, and date proximity

## Xero (`xero`)

Use for accounting record creation and payment/reconciliation visibility.

Relevant behavior:
- create contacts if missing
- create invoices/bills (`ACCPAY` for payable bills)
- list payments and bank transactions

# Canonical Signal Chain

## Stage 1: Inbox detection

Scan Gmail for candidate invoice emails.

Recommended query pattern:
- `has:attachment (subject:invoice OR subject:rechnung OR subject:receipt OR subject:quittung)`
- optional sender constraint for known vendors (for example `from:aws`)

Output:
- message ID
- sender
- received date
- attachment candidates

## Stage 2: Attachment extraction

For each invoice candidate attachment:
1. send file to DeepRead OCR with invoice schema
2. wait for async completion (webhook preferred; polling fallback)
3. parse structured result

Minimum extracted fields:
- vendor
- invoice_date
- invoice_number
- total_amount
- tax_amount
- currency

Quality gate:
- if critical fields have `hil_flag=true`, route to review queue before posting.

## Stage 3: Payment verification

Use Stripe to check whether corresponding payment occurred.

Matching policy:
- amount equals invoice total (within tolerance)
- currency matches
- date within tolerance window
- status is successful/paid

If multiple candidates match, mark as `ambiguous_match` and require review.

## Stage 4: Accounting write

Use Xero for booking.

Default payable flow:
1. ensure vendor contact exists (create if needed)
2. create bill entry (`Type: ACCPAY`) with line item category (for example Hosting)
3. mark as paid/reconciled state only when Stripe verification is confident
4. include reference fields: invoice number, source message ID, payment reference

Attachment handling:
- if binary attachment endpoint/path is available in the active integration, attach file
- otherwise store durable file reference and include link/reference in description/metadata

## Stage 5: Traceability updates

After successful processing:
- apply Gmail processed label
- store processing log (source email, extraction confidence, matching evidence, xero IDs)
- keep idempotency key to avoid duplicate posting

# Scenario Mapping (AWS Invoice)

For the scenario "AWS invoice by email -> Xero + card match":

1. Gmail finds AWS email with PDF attachment.
2. DeepRead OCR extracts structured fields (vendor/date/total/tax/invoice number).
3. Stripe check confirms payment event around invoice date and amount.
4. Xero creates payable entry (`ACCPAY`) under Hosting category.
5. Record is marked paid only after confident match; source PDF linked/attached per policy.

# Data Contract

Normalize to one transaction record before posting:

```json
{
  "source": {
    "gmail_message_id": "...",
    "sender": "billing@aws.amazon.com",
    "attachment_name": "invoice.pdf"
  },
  "invoice": {
    "vendor": "AWS",
    "invoice_number": "INV-123",
    "invoice_date": "2024-05-01",
    "total": 53.20,
    "tax": 0.00,
    "currency": "USD",
    "ocr_confidence_ok": true
  },
  "payment_match": {
    "provider": "stripe",
    "matched": true,
    "transaction_id": "ch_...",
    "amount": 53.20,
    "date": "2024-05-01"
  },
  "accounting": {
    "system": "xero",
    "entry_type": "ACCPAY",
    "category": "Hosting",
    "status": "Paid"
  }
}
```

# Output Contract

Always return:

- `IntakeSummary`
  - emails scanned, invoice candidates found

- `ExtractionSummary`
  - extracted fields and `hil_flag` status

- `PaymentVerification`
  - matched/not matched + evidence

- `AccountingAction`
  - created/updated records and IDs

- `ReviewQueue`
  - any records requiring manual validation

# Quality Gates

Before auto-posting:
- vendor identified
- invoice number/date/total present
- no critical `hil_flag` unresolved
- payment match confidence above policy threshold
- duplicate check passed (same vendor + invoice number + total)

If any gate fails, return `Needs Review` and do not auto-post.

# Guardrails

- Never mark invoice as paid without payment evidence.
- Never silently overwrite existing accounting records.
- Never drop uncertain OCR fields; surface them explicitly.
- Prefer manual review when amount/date ambiguity exists.
- Preserve source audit trail for every booking action.

# Failure Handling

- Gmail unavailable: stop intake and report connection issue.
- OCR job failed/timeout: keep email queued for retry.
- Stripe no match: post as unpaid bill or route to review per policy.
- Xero write failed: keep normalized record and retry safely with idempotency key.

# Known Limits from Inspected Upstream Skills

- DeepRead OCR is asynchronous and may require webhook/polling orchestration.
- The inspected Xero skill docs emphasize core accounting endpoints but do not fully document attachment upload flow; attachment behavior depends on supported endpoint path in active integration.
- Stripe/Xero matching is orchestration logic here, not a single native "auto-reconcile" endpoint in these inspected skill docs.
- QuickBooks is not part of this researched stack; this meta-skill is Xero-first.

Treat these limits as mandatory operator disclosures.
