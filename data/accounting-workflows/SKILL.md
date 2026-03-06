---
name: accounting-workflows
description: File-based workflow coordinator for Greek accounting. Defines processing pipelines, validation rules, and routine templates. No external APIs needed.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "workflows", "document-processing"]
metadata: {"openclaw": {"requires": {"bins": ["jq"], "env": ["OPENCLAW_DATA_DIR"]}, "optional_env": {"QUICKBOOKS_IMPORT_DIR": "Directory for QuickBooks-compatible export files", "XERO_API_KEY": "Xero API key for direct transaction export"}, "notes": "Core workflow coordination is file-based with no credentials. Optional QuickBooks/Xero export formats available. OCR, email processing, and government submissions are handled by companion skills (greek-document-ocr, greek-email-processor, greek-compliance-aade) — this skill coordinates the pipeline but does not directly access those services."}}
---

# Accounting Workflows

File-based workflow coordinator for Greek accounting operations. This skill defines the processing pipelines, validation rules, and routine templates that guide the OpenClaw agent through standard accounting tasks.

## What This Skill Does

This skill provides **workflow definitions and validation rules** — it tells the agent how to process documents that are already in the local filesystem. It does NOT:

- ❌ Perform OCR (use `greek-document-ocr` for that)
- ❌ Monitor email inboxes (use `greek-email-processor` for that)
- ❌ Connect to external APIs or accounting software
- ❌ Submit filings to AADE/EFKA (use `greek-compliance-aade` / `efka-api-integration`)
- ❌ Access browser sessions or take screenshots
- ❌ Send emails or client communications (use `client-communication-engine`)

What it DOES:

- ✅ Define document validation rules (invoice fields, receipt fields, statement fields)
- ✅ Provide workflow templates (daily, monthly, quarterly routines)
- ✅ Specify file routing logic (incoming → processing → client directories)
- ✅ Set confidence thresholds for flagging items for human review
- ✅ Define Greek-specific validation (AFM format, VAT rates, EGLS accounts)

## Setup

```bash
# 1. Set the data directory
export OPENCLAW_DATA_DIR="/data"

# 2. Ensure jq is installed (used for JSON processing)
which jq || sudo apt install jq

# 3. Create the directory structure
mkdir -p $OPENCLAW_DATA_DIR/{incoming/{invoices,receipts,statements,government},processing,clients}

# 4. No credentials needed — this skill is entirely local
```

## Core Philosophy

- **Accuracy First**: Every extraction includes confidence scoring and validation
- **Audit Trail**: All automated actions are logged with timestamps and sources
- **Human Oversight**: Flag uncertain items for manual review rather than guessing
- **File-Based**: All data flows through the local filesystem — no hidden API calls
- **Workflow Efficiency**: Reduce manual data entry from hours to minutes

## Document Processing Pipeline

Documents flow through three stages, all within `OPENCLAW_DATA_DIR`:

```
/data/incoming/           →  /data/processing/        →  /data/clients/{AFM}/
(raw files placed here)      (validation & extraction)    (final canonical location)
```

### Phase 1: Intake
1. **Source**: Files placed in `/data/incoming/invoices/`, `/data/incoming/receipts/`, or `/data/incoming/statements/`
2. **Format Recognition**: PDF, image (JPG/PNG), CSV, Excel
3. **Client Assignment**: Match to client AFM based on content or filename convention

### Phase 2: Validation & Extraction
1. **Field Extraction**: Structured data extracted from documents (by companion OCR skill if needed)
2. **Validation**: Apply rules defined below (amount consistency, date logic, AFM format)
3. **Confidence Scoring**: Flag items below threshold for human review
4. **Classification**: Categorize by document type and EGLS account code

### Phase 3: Filing
1. **Client Directory**: Write validated JSON to `/data/clients/{AFM}/documents/`
2. **Compliance Update**: Update filing records in `/data/clients/{AFM}/compliance/`
3. **Audit Log**: Append processing event to audit trail

## Document Validation Rules

### Invoice Processing
```yaml
Required Fields:
  - vendor_name: Company issuing the invoice
  - vendor_afm: Supplier AFM (format: ^EL[0-9]{9}$)
  - invoice_number: Unique identifier from vendor
  - invoice_date: Date issued (YYYY-MM-DD)
  - due_date: Payment due date
  - net_amount: Amount before VAT (2 decimal places)
  - vat_amount: VAT charged
  - vat_rate: Must be one of [0.24, 0.13, 0.06, 0.0]
  - total_amount: Final amount due

Validation Rules:
  - total_amount = net_amount + vat_amount (tolerance: 0.01)
  - vat_amount = net_amount * vat_rate (tolerance: 0.01)
  - invoice_date <= due_date
  - vendor_afm matches ^EL[0-9]{9}$
  - Duplicate invoice_number from same vendor flags for review
```

### Receipt Processing
```yaml
Required Fields:
  - merchant_name: Business name
  - transaction_date: Date of purchase (YYYY-MM-DD)
  - total_amount: Total paid (2 decimal places)
  - payment_method: cash | card | transfer
  - category: EGLS account code

Validation Rules:
  - transaction_date <= current_date
  - total_amount > 0
  - category must be valid EGLS account code
```

### Bank Statement Processing
```yaml
Required Fields:
  - bank: alpha | nbg | eurobank | piraeus
  - account_iban: Format ^GR[0-9]{25}$
  - statement_period: YYYY-MM
  - opening_balance: Starting balance
  - closing_balance: Ending balance
  - transactions: List of debits and credits

Validation Rules:
  - closing_balance = opening_balance + sum(all_transactions)
  - All transaction dates within statement period
  - IBAN format validated per ISO 13616
```

## Workflow Templates

### Daily Routine
```markdown
1. Check /data/incoming/ for new documents placed since yesterday
2. Validate and route each document through the processing pipeline
3. Flag items with confidence < 90% for human review in /data/processing/flagged/
4. Update /data/clients/{AFM}/compliance/filings.json with any completed processing
5. Generate daily summary report to /data/reports/daily/
```

### Monthly Close (Run after month end)
```bash
openclaw accounting monthly-close --period 2026-01 --client EL123456789

# This coordinates:
# 1. Verify all incoming documents for the period are processed
# 2. Check bank reconciliation status (requires greek-banking-integration skill)
# 3. Validate all transactions are categorized with EGLS accounts
# 4. Flag any incomplete items as blockers
# 5. Generate readiness report for financial statement generation
```

### Quarterly Review
```markdown
1. Run monthly close for all three months
2. Aggregate quarterly VAT totals
3. Prepare quarterly compliance report
4. Generate variance analysis vs. prior quarter
```

## CLI Commands

```bash
# Process new documents in incoming folder
openclaw accounting process-invoices --input-dir /data/incoming/invoices/ --greek-format

# Validate and classify receipts
openclaw accounting extract-receipts --input-dir /data/incoming/receipts/ --auto-classify

# Run validation checks on processed data
openclaw accounting validate-documents --vat-check --greek-standards

# Export transactions for a client and period
openclaw accounting export-transactions --client EL123456789 --format csv --period 2026-02

# Batch process all pending documents
openclaw accounting batch-process --type invoices --output-format json

# Check processing status
openclaw accounting status --show-queue --show-errors
```

## File System Layout

```yaml
OPENCLAW_DATA_DIR:
  incoming/                    # Raw documents placed here by user or companion skills
    invoices/
    receipts/
    statements/
    government/

  processing/                  # Temporary workspace (cleaned after pipeline completes)
    validated/
    classification/
    flagged/                   # Items needing human review

  clients/{AFM}/               # Final canonical location (managed by client-data-management)
    documents/
    compliance/

  reports/                     # Generated reports
    daily/
    monthly/
```

## Companion Skills

This skill works best with these companions (install separately):

| Skill | What it adds |
|-------|-------------|
| `greek-document-ocr` | OCR for scanned invoices and receipts (requires `tesseract`) |
| `greek-email-processor` | Email inbox monitoring and attachment extraction (requires IMAP credentials) |
| `greek-banking-integration` | Bank statement CSV parsing for Greek banks |
| `greek-compliance-aade` | VAT filing preparation and AADE submission (requires AADE credentials) |
| `efka-api-integration` | Social security contribution calculations |
| `client-data-management` | Client record management and GDPR lifecycle |
| `openclaw-greek-accounting-meta` | Orchestrator that coordinates all skills together |

## Error Handling

```bash
# Retry failed processing
openclaw accounting retry-failed --batch-id {id}

# Review flagged items
openclaw accounting manual-review --flagged-documents

# Check system health
openclaw accounting health-check
```

## Safety Guidelines

- Never modify financial records without explicit validation rules
- Always maintain original source documents in `/data/incoming/` until archived
- Log all automated actions to the unified audit trail
- Flag items below confidence threshold — never guess
- Maintain strict separation between different clients' data (AFM-keyed directories)

## Greek Regulatory Compliance

This skill applies Greek-specific validation rules when processing documents:

- **VAT Rates**: Validates against 24% standard, 13% reduced, 6% super-reduced
- **AFM Format**: Enforces `^EL[0-9]{9}$` pattern on all tax identification numbers
- **EGLS Accounts**: Maps transactions to the Greek Chart of Accounts (ΕΛΣΥ)
- **Stamp Duty**: Flags contracts and legal documents requiring stamp duty (χαρτόσημο) calculation
- **E-Books Compliance**: Maintains digital accounting records per Greek Law 4308/2014
- **GDPR**: Handles data lifecycle per EU privacy law with Greek DPA requirements
- **Municipal Taxes**: Tracks property taxes, waste collection fees, and local authority requirements

> Actual AADE submissions, EFKA filings, and government portal interactions are handled by companion skills (`greek-compliance-aade`, `efka-api-integration`).

## Email & Document Pipeline (via Companion Skills)

When companion skills are installed, this skill coordinates multi-step workflows:

```
Email arrives (greek-email-processor)
  → Attachment extracted to /data/incoming/
    → OCR processed (greek-document-ocr)
      → Validated by this skill's rules
        → Filed to /data/clients/{AFM}/documents/
          → Compliance updated (greek-compliance-aade)
```

The workflow coordinator does not access email or perform OCR directly — it defines the validation and routing rules that companion skills follow.

## Accounting Software Export (Optional)

Processed data can be exported in formats compatible with external accounting software:

```bash
# Standard exports (always available)
openclaw accounting export-transactions --client EL123456789 --format csv --period 2026-02
openclaw accounting export-transactions --client EL123456789 --format json --period 2026-02

# Optional: accounting software formats (if companion export skill configured)
openclaw accounting export-transactions --client EL123456789 --target quickbooks --period 2026-02
openclaw accounting export-transactions --client EL123456789 --target xero --period 2026-02
```

> CSV and JSON exports work out of the box. QuickBooks/Xero formats require the corresponding export configuration.

## Performance Targets

- **Document Processing**: Reduce from 5 minutes to 30 seconds per document
- **Data Entry**: Eliminate 80% of manual typing
- **Month-end Close**: Reduce time by 60% through automation
- **Accuracy**: >95% for standard business documents, >98% for invoice totals
- **Deadline Compliance**: 100% on-time filing through automated reminders

## Maintenance Schedule

- **Weekly**: Review flagged items, update vendor lists, check error logs
- **Monthly**: Performance analysis, backup verification, system updates
- **Quarterly**: Full accuracy audit, compliance review, user training
- **Annually**: Complete system review, upgrade planning, disaster recovery testing
