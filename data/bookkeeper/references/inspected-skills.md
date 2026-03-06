# Inspected Upstream Skills

Directly inspected from ClawHub:

- `gmail` latest `1.0.6`
- `deepread-ocr` latest `1.0.6`
- `stripe-api` latest `1.0.8`
- `xero` latest `1.0.4`

## Capability notes used in this meta-skill

- Gmail: query/filter/list/read mail, thread and label operations via managed OAuth.
- DeepRead OCR: async OCR + structured extraction + field-level `hil_flag` confidence routing.
- Stripe: payment, charge, payment_intent, invoice, and balance transaction retrieval via managed OAuth.
- Xero: contacts, invoices (including `ACCPAY` for bills), payments and bank transactions APIs.

## Scope constraints

- DeepRead OCR is asynchronous (2–5 min typical) and should use webhook or polling.
- Attachment handling and binary transfer to accounting systems may require explicit endpoint support beyond simplified examples.
- Exact "invoice-to-card-transaction match" behavior is orchestration logic here, not a single native endpoint call.
