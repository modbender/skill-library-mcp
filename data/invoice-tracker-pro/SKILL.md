---
name: invoice-tracker
description: Complete freelance billing workflow — generate professional invoices, track payment status, send automated reminders, and reconcile payments. Use when you need to bill clients, follow up on overdue payments, organize financial records, or prepare tax documentation for freelance income.
---

# Invoice Tracker

Get paid what you're owed. This skill handles the complete billing lifecycle — from invoice creation to payment reconciliation — with professional templates, automated reminders, and financial reporting.

## What It Does

- **Invoice Generation**: Professional invoices from project data
- **Payment Tracking**: Know who owes what and when
- **Automated Reminders**: Polite follow-ups for overdue payments
- **Payment Reconciliation**: Match payments to invoices
- **Financial Reporting**: Revenue, aging, tax summaries
- **Recurring Billing**: Retainers and subscription invoices
- **Late Fee Management**: Calculate and apply late fees

## Quick Start

### 1. Create Your First Invoice

```
"Create an invoice for:

Client: [Company Name]
Client Email: [email]
Project: [Project Name]
Invoice #: INV-2024-001
Issue Date: [date]
Due Date: Net 15

Line Items:
1. Website Design - $5,000
2. Development - $3,500
3. CMS Training - $500

Payment terms: Net 15, 1.5% late fee after 30 days
Payment methods: Bank transfer, PayPal, credit card"
```

### 2. Batch Invoice Creation

```
"Generate monthly invoices for my retainer clients:

Client A: $2,000/month - Website maintenance
Client B: $1,500/month - Ongoing consulting
Client C: $3,000/month - Marketing support

Period: January 2024
Terms: Net 30
Include: Hours summary, deliverables completed"
```

### 3. Overdue Payment Follow-Up

```
"Create follow-up emails for overdue invoices:

Invoice INV-2024-005 - $4,500 - 15 days overdue
Invoice INV-2024-008 - $2,200 - 30 days overdue
Invoice INV-2024-012 - $6,000 - 45 days overdue

Tone: Professional but firm
Include: Payment link, original invoice, late fee notice"
```

## Invoice Structure

### Required Elements

**Header**:
- Your business name/logo
- Invoice number (unique, sequential)
- Issue date
- Due date

**Parties**:
- From: Your business name, address, tax ID
- To: Client name, contact person, billing address

**Line Items**:
| Description | Quantity | Rate | Amount |
|-------------|----------|------|--------|
| Service name | 10 hours | $100/hr | $1,000 |
| Deliverable | 1 | $2,500 | $2,500 |

**Totals**:
- Subtotal
- Tax (if applicable)
- Discounts
- **Total Due**

**Footer**:
- Payment instructions
- Terms and conditions
- Thank you message

### Professional Invoice Template

```
┌─────────────────────────────────────────────────────────┐
│  [YOUR LOGO]                              INVOICE       │
│  Your Business Name                         #INV-2024-001│
│  123 Main Street                           Date: Jan 15 │
│  City, ST 12345                            Due: Feb 1   │
│  contact@yourbusiness.com                             │
├─────────────────────────────────────────────────────────┤
│  BILL TO:                                               │
│  Client Company Name                                    │
│  Attn: Accounts Payable                                 │
│  456 Business Ave                                       │
│  City, ST 67890                                         │
├─────────────────────────────────────────────────────────┤
│  PROJECT: Website Redesign                              │
├─────────────────────────────────────────────────────────┤
│  Description           │ Qty │ Rate      │ Amount      │
│  ──────────────────────┼─────┼───────────┼─────────────│
│  Discovery & Strategy  │ 1   │ $1,500.00 │ $1,500.00   │
│  UI/UX Design          │ 1   │ $3,000.00 │ $3,000.00   │
│  Frontend Development  │ 40  │ $100.00   │ $4,000.00   │
│  CMS Integration       │ 1   │ $1,500.00 │ $1,500.00   │
│  ──────────────────────┴─────┴───────────┼─────────────│
│                               Subtotal   │ $10,000.00  │
│                               Tax (0%)   │ $0.00       │
│                               ─────────────────────────│
│                               TOTAL DUE  │ $10,000.00  │
├─────────────────────────────────────────────────────────┤
│  PAYMENT OPTIONS:                                       │
│  • Bank Transfer: [Account details]                     │
│  • PayPal: [PayPal.me link]                             │
│  • Credit Card: [Stripe/PayPal link]                    │
│                                                         │
│  TERMS: Net 30. Late payments subject to 1.5% monthly   │
│  service charge after 30 days.                          │
│                                                         │
│  Questions? Contact: billing@yourbusiness.com           │
│  Thank you for your business!                           │
└─────────────────────────────────────────────────────────┘
```

## Payment Tracking System

### Invoice Status Categories

```
DRAFT        → Created but not sent
SENT         → Issued to client, awaiting payment
VIEWED       → Client opened invoice (if using online system)
PARTIAL      → Partial payment received
PAID         → Full payment received
OVERDUE      → Past due date, payment pending
COLLECTIONS  → Seriously overdue, escalation needed
VOID         → Cancelled/replaced
```

### Aging Report

Track overdue invoices by age:

```
Aging Report - February 2024

Client              Invoice     Amount    0-30    31-60   60+
─────────────────────────────────────────────────────────────
ABC Corp            INV-005     $4,500            $4,500
XYZ Inc             INV-008     $2,200    $2,200
123 LLC             INV-012     $6,000                    $6,000
─────────────────────────────────────────────────────────────
TOTALS                          $12,700   $2,200  $4,500  $6,000
```

## Automated Reminder Sequences

### Standard Follow-Up Schedule

**Day 0**: Invoice sent
**Day 7**: Friendly reminder (optional for Net 30)
**Day 25**: Payment due soon
**Day 31**: Overdue notice #1
**Day 45**: Overdue notice #2
**Day 60**: Final notice + late fee
**Day 75**: Collections consideration

### Email Templates

**Pre-Due Reminder (Day 25)**:
```
Subject: Payment Reminder: Invoice INV-2024-001 ($10,000)

Hi [Name],

Just a friendly reminder that invoice INV-2024-001 for $10,000 
is due on [due date] (5 days from now).

You can view and pay the invoice here: [link]

Payment options:
• Bank transfer (preferred)
• PayPal: [link]
• Credit card: [link]

Please let me know if you have any questions or need any 
additional information.

Thanks!
[Your name]
```

**First Overdue Notice (Day 31)**:
```
Subject: Overdue Invoice: INV-2024-001 ($10,000) - Action Needed

Hi [Name],

I wanted to follow up on invoice INV-2024-001 for $10,000, 
which was due on [due date] and is now overdue.

If you've already sent payment, please disregard this message 
and accept my thanks.

If not, you can pay online here: [link]

I'm happy to discuss any questions or concerns you may have. 
Please reply to this email or call me at [phone].

Best regards,
[Your name]
```

**Second Overdue Notice (Day 45)**:
```
Subject: Second Notice: Overdue Invoice INV-2024-001 ($10,000)

Hi [Name],

This is my second notice regarding invoice INV-2024-001 for 
$10,000, originally due on [due date].

Per our agreement, a late fee of $150 (1.5%) will be applied 
to this invoice if payment is not received by [date + 15 days].

I value our working relationship and want to resolve this 
amicably. Please contact me to discuss payment arrangements 
if needed.

Payment link: [link]

Regards,
[Your name]
```

**Final Notice (Day 60)**:
```
Subject: FINAL NOTICE: Overdue Invoice INV-2024-001 ($10,150)

Hi [Name],

This is a final notice regarding invoice INV-2024-001.

Original amount: $10,000
Late fees applied: $150
Current balance: $10,150

If payment is not received within 15 days, I will need to 
escalate this matter to collections and suspend any ongoing 
work.

I would prefer to avoid this. Please contact me immediately 
to discuss payment: [phone/email]

Payment link: [link]

[Your name]
```

## Financial Reporting

### Monthly Revenue Report

```
Revenue Report - January 2024

Invoiced:           $25,000
  - Services:       $20,000
  - Products:       $5,000

Collected:          $22,500
Outstanding:        $12,500
  - Current:        $5,000
  - Overdue:        $7,500

Top Clients:
1. ABC Corp:        $8,000
2. XYZ Inc:         $6,500
3. 123 LLC:         $4,500

Payment Methods:
- Bank transfer:    60%
- PayPal:           30%
- Credit card:      10%
```

### Tax Summary

```
Annual Tax Summary - 2024

Total Revenue:      $180,000
  - Q1:             $45,000
  - Q2:             $42,000
  - Q3:             $48,000
  - Q4:             $45,000

Taxable Income:     $165,000
  (after $15,000 expenses)

Estimated Tax:      ~$41,250 (25% effective rate)
Quarterly payments: $10,312

1099s Received:     3 clients ($95,000 total)
1099s Required:     2 contractors ($12,000 paid)
```

## Recurring Billing

### Retainer Setup

```
"Create a monthly retainer invoice template:

Client: [Name]
Service: Ongoing consulting
Amount: $3,000/month
Billing date: 1st of month
Payment terms: Net 15

Include:
- Hours included: 20
- Overage rate: $150/hr
- Rollover policy: Up to 5 hours
- Minimum commitment: 3 months"
```

### Subscription Invoicing

For productized services:

```
Tier: Starter ($99/month)
- Invoice auto-generated on subscription date
- Payment auto-charged (if using Stripe/PayPal)
- Failed payment → retry sequence
- Cancellation → final invoice prorated
```

## Best Practices

### Invoice Numbering

Use a consistent format:
- `INV-YYYY-NNN` (INV-2024-001)
- `YYYY-MM-NNN` (2024-01-001)
- `CLIENT-NNN` (ABC-001)

### Payment Terms

Standard options:
- **Net 15**: Large enterprises (they take forever anyway)
- **Net 30**: Standard for most clients
- **Due on receipt**: Small projects, new clients
- **50/50**: 50% deposit, 50% on completion
- **Milestone**: Payment at defined project stages

### Cash Flow Tips

1. **Invoice immediately** — don't wait until month-end
2. **Require deposits** — 50% upfront for new clients
3. **Offer early payment discounts** — 2/10 Net 30 (2% off if paid in 10 days)
4. **Charge late fees** — and enforce them
5. **Stop work on overdue accounts** — protect yourself
6. **Use online payments** — easier for clients = faster payment

### Red Flags

Watch for these warning signs:
- Client questions your rates after agreement
- "The check is in the mail" (repeatedly)
- Asks to pay after project completion (no deposit)
- Disappears when invoice is due
- Wants to change payment terms mid-project

## Tools Integration

**Accounting Software**:
- QuickBooks, Xero, FreshBooks — sync invoices
- Automatic reconciliation
- Tax reporting

**Payment Processors**:
- Stripe — credit cards, ACH
- PayPal — widely accepted
- Wise — international transfers
- Bank transfer — lowest fees

**Time Tracking**:
- Harvest, Toggl, Clockify
- Auto-generate invoices from time entries

## Common Mistakes

1. **Not invoicing promptly** — delays payment by weeks
2. **Unclear payment terms** — confusion leads to delays
3. **No late fees** — clients have no incentive to pay on time
4. **Ignoring overdue invoices** — they don't get better with age
5. **No deposit for new clients** — high risk of non-payment
6. **Mixing personal and business** — tax nightmare
7. **Not tracking 1099s** — IRS penalties

## Integration Ideas

- Connect to **proposal-generator** to convert accepted proposals to invoices
- Use with **client-intake-bot** to set payment expectations upfront
- Track project profitability alongside **content-repurposer** ROI

## Monetization Note

This skill is part of the **Freelancer Revenue Engine**. For maximum value, use alongside:
- `proposal-generator` — convert proposals to invoices
- `client-intake-bot` — set payment terms early

Bundle available: Freelancer Revenue Engine ($89)
