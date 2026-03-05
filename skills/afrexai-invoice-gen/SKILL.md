---
name: Invoice Generator
description: Creates professional invoices in markdown and HTML
---

# Invoice Generator

You create professional invoices. Clean, clear, and ready to send.

## What to Ask

1. **Your business info:** Name, address, email, phone (save for reuse)
2. **Client info:** Company name, contact name, address
3. **Invoice number:** Or auto-generate (INV-YYYY-NNN format)
4. **Line items:** Description, quantity, unit price
5. **Payment terms:** Net 30, Net 15, Due on receipt, etc.
6. **Payment methods:** Bank transfer, PayPal, Stripe link, etc.
7. **Currency:** Default USD
8. **Tax rate:** If applicable (percentage)
9. **Notes:** Any special terms, late payment fees, etc.

## Invoice Template

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    INVOICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FROM:                          INVOICE #: [INV-2024-001]
[Your Business Name]           DATE: [2024-01-15]
[Address]                      DUE DATE: [2024-02-14]
[Email] | [Phone]

TO:
[Client Company]
[Contact Name]
[Address]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESCRIPTION              QTY    RATE      AMOUNT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Service/Product]        [1]    [$X]      [$X]
[Service/Product]        [2]    [$Y]      [$2Y]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                          SUBTOTAL:    $[X]
                          TAX ([X]%):  $[X]
                          ━━━━━━━━━━━━━━━━
                          TOTAL:       $[X]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PAYMENT TERMS: [Net 30]

PAYMENT METHODS:
• Bank Transfer: [Details]
• PayPal: [email]
• [Other]

NOTES:
[Late payment fee: 1.5% per month on overdue balances]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Thank you for your business.
```

## Output Formats

### Markdown (default)
Clean markdown table format, easy to paste into emails or docs.

### HTML
Generate a styled HTML file the user can open in a browser and print/save as PDF:
- Clean, professional styling
- Print-friendly (no background colors that waste ink)
- Save as `invoice-[number].html`

## Rules

- Always calculate totals correctly. Double-check math.
- Invoice numbers should be sequential. Check for existing invoices if possible.
- Due date = invoice date + payment terms (Net 30 = 30 days, etc.)
- Include all legally required info (varies by jurisdiction — ask if unsure)
- Save invoices to an `invoices/` directory for record-keeping
- If the user has sent invoices before, reuse their business details
- Currency formatting: use proper symbols and decimal places ($1,234.56)

## Recurring Invoices

If the user bills the same client regularly:
- "Create this month's invoice for [client]" → Copy previous invoice, update date/number/period
- Track invoice history per client

## Quick Commands

- "Invoice [client] for [amount] for [description]" → Generate with defaults
- "Show my invoices" → List all invoices in the invoices/ directory
- "What's outstanding?" → Show unpaid invoices past due date


---

## 🔗 More AfrexAI Skills (Free on ClawHub)

| Skill | Install |
|-------|---------|
| AI Humanizer | `clawhub install afrexai-humanizer` |
| SEO Writer | `clawhub install afrexai-seo-writer` |
| Email Crafter | `clawhub install afrexai-email-crafter` |
| Proposal Generator | `clawhub install afrexai-proposal-gen` |
| Invoice Generator | `clawhub install afrexai-invoice-gen` |
| Lead Scorer | `clawhub install afrexai-lead-scorer` |
| Client Onboarding | `clawhub install afrexai-onboarding` |
| Meeting Prep | `clawhub install afrexai-meeting-prep` |
| Social Repurposer | `clawhub install afrexai-social-repurposer` |
| FAQ Builder | `clawhub install afrexai-faq-builder` |
| Review Responder | `clawhub install afrexai-review-responder` |
| Report Builder | `clawhub install afrexai-report-builder` |
| CRM Updater | `clawhub install afrexai-crm-updater` |
| Pitch Deck Reviewer | `clawhub install afrexai-pitch-deck-reviewer` |
| Contract Analyzer | `clawhub install afrexai-contract-analyzer` |
| Pricing Optimizer | `clawhub install afrexai-pricing-optimizer` |
| Testimonial Collector | `clawhub install afrexai-testimonial-collector` |
| Competitor Monitor | `clawhub install afrexai-competitor-monitor` |

## 🚀 Go Pro: Industry Context Packs ($47/pack)

Make your AI agent a true industry expert with deep domain knowledge.

→ **[Browse Context Packs](https://afrexai-cto.github.io/context-packs/)**

**Free tools:** [AI Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) | [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) 🖤💛*
