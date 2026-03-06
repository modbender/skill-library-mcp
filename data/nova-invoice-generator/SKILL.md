---
name: invoice-generator
description: |
  Generate a professional invoice from natural language or structured input.

  USE WHEN:
  - User asks to create an invoice, bill, or payment request
  - User provides line items, client details, or says "invoice [client] for [work]"
  - User wants a receipt or proof of payment document

  DON'T USE WHEN:
  - User wants a quote, estimate, or proposal (different document structure and intent)
  - User wants to track invoices, manage accounts receivable, or build an invoicing system
  - User wants a contract or agreement (use a contract/legal template instead)
  - User wants to send an invoice via email (this generates the document; sending is a separate step)
  - User wants a recurring billing setup or subscription management

  OUTPUTS: Single self-contained .html file, print-ready. User opens in browser → Print → Save as PDF. Clean, professional layout.

  INPUTS: Sender info, client info, line items (description + qty + price). Optional: invoice number, dates, tax rate, notes, payment terms.
---

# Invoice Generator

Create professional invoices from text descriptions or structured data.

## Workflow

1. Collect invoice details from the user (or parse from prompt):
   - Sender (business name, address, email)
   - Recipient (client name, address, email)
   - Line items (description, quantity, unit price)
   - Invoice number, date, due date
   - Payment terms/methods
   - Tax rate (optional)
   - Notes (optional)
2. Read the template at `assets/invoice-template.html`
3. Replace placeholders with actual data, calculate totals
4. Save as `.html` file — user can open in browser and Print → PDF

## Calculations

- Subtotal = sum of (quantity × unit price) for each line item
- Tax = subtotal × tax rate
- Total = subtotal + tax
- Always format currency with 2 decimal places

## Template Placeholders

| Placeholder | Description |
|---|---|
| `{{INVOICE_NUMBER}}` | Unique invoice ID |
| `{{INVOICE_DATE}}` | Issue date |
| `{{DUE_DATE}}` | Payment due date |
| `{{SENDER_*}}` | Sender name, address, email, phone |
| `{{CLIENT_*}}` | Client name, address, email |
| `{{LINE_ITEMS}}` | HTML table rows for items |
| `{{SUBTOTAL}}` | Pre-tax total |
| `{{TAX_RATE}}` | Tax percentage |
| `{{TAX_AMOUNT}}` | Calculated tax |
| `{{TOTAL}}` | Final amount due |
| `{{PAYMENT_TERMS}}` | Payment instructions |
| `{{NOTES}}` | Additional notes |

## Defaults

- Currency: USD (configurable)
- Tax: 0% unless specified
- Due date: 30 days from invoice date unless specified
- Invoice number: auto-increment or user-specified

## Common Mistakes to Avoid

- **Don't guess line items** — if the user is vague ("invoice them for the work"), ask for specifics (hours, rate, deliverables)
- **Don't invent sender details** — use what the user provides or ask
- **Don't skip the math** — always verify subtotal + tax = total. Rounding errors on invoices are unprofessional
- **Don't add fake payment links** — only include payment methods the user explicitly provides
