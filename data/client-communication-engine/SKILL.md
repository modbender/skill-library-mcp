---
name: client-communication-engine
description: Greek-language client correspondence — submission confirmations, summaries, document requests, reminders. Human review required before sending.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "client-communications", "bilingual", "email"]
metadata: {"openclaw": {"requires": {"bins": ["jq", "curl"], "env": ["OPENCLAW_DATA_DIR", "SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"]}, "optional_env": {"SLACK_WEBHOOK_URL": "Internal team notifications when client communications are sent"}, "notes": "SMTP credentials required for sending client correspondence. All communications require human review and approval before sending. Slack notification is optional for internal team awareness."}}
---

# Client Communication Engine

This skill handles all outgoing communication from the accounting firm to its clients. It produces professional Greek-language letters, summaries, and notifications — the documents and emails that clients actually receive. Every piece of outgoing communication follows Greek business correspondence conventions, references the correct regulatory terminology, and is drafted for human review before anything is sent.

The skill pairs with `greek-email-processor` (Skill 4), which handles inbound. Together they form the complete communication layer: Skill 4 reads the inbox, Skill 16 writes the outbox.


## Setup

```bash
export OPENCLAW_DATA_DIR="/data"
export SMTP_HOST="smtp.your-provider.com" # e.g. smtp.gmail.com, smtp.outlook.com
export SMTP_USER="accounting@yourfirm.gr"
export SMTP_PASSWORD="app-specific-password"
which jq curl || sudo apt install jq curl
```

SMTP credentials are required for sending client correspondence. All communications are drafted locally and require human review and approval before sending. Use app-specific passwords.


## Core Philosophy

- **Draft First, Send Second**: Nothing is sent automatically. Every communication is drafted, shown for review, and requires explicit approval before dispatch. This applies to all communication types without exception
- **Greek Business Standards**: Output matches what a professional Greek accounting firm would send — correct formal register, appropriate regulatory terminology, proper salutations and closings for Greek business correspondence
- **Data-Driven Content**: Letters are generated from real system data — actual submission reference numbers, actual VAT amounts, actual deadlines. Nothing is fabricated or approximated
- **Logged Against Client Record**: Every sent communication is recorded in `/data/clients/{AFM}/correspondence/` with timestamp, type, recipient, and content hash. The firm always knows what was said to whom and when
- **Context-Aware Tone**: Document request letters are polite but clear. Deadline reminders escalate appropriately (informative → reminder → urgent → critical) without being aggressive. Submission confirmations are formal and precise
- **Language Boundary**: Communications to clients are in Greek. Internal summaries and draft previews shown to firm staff are in English. The skill never sends English to a Greek client

---

## OpenClaw Commands

### Drafting Communications
```bash
# Draft a submission confirmation letter
openclaw comms draft --type submission-confirmation --afm EL123456789 --filing-type VAT --period 2026-01
openclaw comms draft --type submission-confirmation --afm EL123456789 --filing-type EFKA --period 2026-01

# Draft a monthly accounting summary
openclaw comms draft --type monthly-summary --afm EL123456789 --period 2026-01
openclaw comms draft --type monthly-summary --afm EL123456789 --period 2026-01 --include-statements

# Draft a document request
openclaw comms draft --type document-request --afm EL123456789 --missing "bank-statements" --period 2026-01
openclaw comms draft --type document-request --afm EL123456789 --missing "october-invoices,payroll-hours" --deadline 2026-02-20
openclaw comms draft --type document-request --afm EL123456789 --from-pending-list  # auto-reads pending.json

# Draft a deadline reminder
openclaw comms draft --type deadline-reminder --afm EL123456789 --deadline-type VAT --due-date 2026-02-25
openclaw comms draft --type deadline-reminder --afm EL123456789 --deadline-type VAT --due-date 2026-02-25 --urgency critical
openclaw comms draft --type deadline-reminder --all-clients --deadline-type VAT --due-within 7-days

# Draft an annual tax summary
openclaw comms draft --type annual-tax-summary --afm EL123456789 --year 2025
openclaw comms draft --type annual-tax-summary --afm EL123456789 --year 2025 --include-e1-status

# Draft a payment reminder (for clients with outstanding fees to the firm)
openclaw comms draft --type payment-reminder --afm EL123456789 --invoice-ref INV-2026-001

# Free-form draft with prompt
openclaw comms draft --type custom --afm EL123456789 --prompt "inform client that their ENFIA property tax instalment is due next month and we need their payment confirmation"
```

### Reviewing Drafts
```bash
# List all pending drafts
openclaw comms drafts-list --all
openclaw comms drafts-list --afm EL123456789
openclaw comms drafts-list --type document-request --pending-approval

# Preview a draft (English summary of Greek content)
openclaw comms preview --draft-id D20260218-001
openclaw comms preview --draft-id D20260218-001 --language el  # Show full Greek text

# Edit a draft before approval
openclaw comms edit --draft-id D20260218-001 --field body --instruction "add mention of the EFKA deadline also due this month"
openclaw comms edit --draft-id D20260218-001 --field tone --value formal  # formal / professional / urgent
```

### Approving and Sending
```bash
# Approve and send a single draft
openclaw comms send --draft-id D20260218-001 --approved-by "yannis.k"

# Approve and send all drafts for a client
openclaw comms send --afm EL123456789 --all-pending --approved-by "yannis.k"

# Send via email (default)
openclaw comms send --draft-id D20260218-001 --via email --approved-by "yannis.k"

# Export as PDF for manual sending (no email integration configured)
openclaw comms send --draft-id D20260218-001 --via pdf-export --approved-by "yannis.k"

# Batch send — e.g. deadline reminders to all affected clients
openclaw comms batch-send --type deadline-reminder --deadline-type VAT --due-within 7-days --approved-by "yannis.k"
```

### Correspondence History
```bash
# View sent communications for a client
openclaw comms history --afm EL123456789 --last 30-days
openclaw comms history --afm EL123456789 --type document-request --year 2026
openclaw comms history --afm EL123456789 --full  # All time

# Firm-wide communication log
openclaw comms log --period 2026-01 --type all --format table
openclaw comms log --period 2026-01 --unsent-drafts  # Drafts that were created but never sent

# Check if a specific type of communication has been sent recently
openclaw comms check-sent --afm EL123456789 --type submission-confirmation --filing-type VAT --period 2026-01
```

### Template Management
```bash
# List available templates
openclaw comms templates-list
openclaw comms templates-list --type document-request

# Preview a template
openclaw comms template-preview --name "vat-submission-confirmation"

# Customise a template for a specific client (client-level override)
openclaw comms template-override --afm EL123456789 --template "monthly-summary" --field salutation --value "Αγαπητέ κ. Παπαδόπουλε,"
```

---

## Communication Templates

### 1. Submission Confirmation Letter

Sent after every successful government filing. References the actual AADE submission receipt.

```
[GREEK TEXT — rendered in Greek in the actual letter]

[Firm letterhead]
[Date in DD/MM/YYYY format]

Αγαπητέ / Αγαπητή [Client contact name],
[or: Αγαπητοί κÏÏιοι, for company-addressed]

Σας ενημεÏώνουμε ότι ολοκληÏώθηκε επιτυχώς η υποβολή της παÏακάτω
φοÏολογικής δήλωσης για λογαÏιασμό σας:

ΤÏπος δήλωσης:   [e.g. Δήλωση ΦΠΑ]
ΠεÏίοδος:        [e.g. ΘανουάÏιος 2026]
ΑΦΜ:             [EL123456789]
ΑÏιθμός υποβολής: [AADE reference number]
ΔμεÏομηνία υποβολής: [DD/MM/YYYY]
Ποσό πληÏωτέο:   [€X,XXX.XX] (εάν υφίσταται)
ΠÏοθεσμία πληÏωμής: [DD/MM/YYYY]

Για οποιαδήποτε αποÏία, παÏακαλώ επικοινωνήστε μαζί μας.

Με εκτίμηση,
[Accountant name]
[Firm name]
[Contact details]
```

```yaml
English_Preview_Fields:
  type: "VAT Return Submission Confirmation"
  client: "Alpha Trading AE (EL123456789)"
  period: "January 2026"
  reference: "AAD-2026-001234"
  submitted: "24/01/2026"
  amount_due: "EUR 3,340.00"
  payment_deadline: "25/02/2026"
```

---

### 2. Monthly Accounting Summary

Sent at month-end. Provides the client with a plain-language overview of what happened to their accounts that month.

```yaml
Monthly_Summary_Structure:
  header:
    - Firm letterhead
    - Client name and AFM
    - Period (Μηνιαία ΕνημέÏωση — Month Year)

  section_1_activity:
    label_el: "ΔÏαστηÏιότητα Μήνα"
    label_en: "Monthly Activity"
    content:
      - Total invoiced income (Συνολικά έσοδα)
      - Total expenses processed (Συνολικά έξοδα)
      - Number of invoices processed
      - VAT position for the month

  section_2_filings:
    label_el: "Υποβολές πÏος ΑÏχές"
    label_en: "Government Filings"
    content:
      - List of submissions made this month (VAT, EFKA, myDATA)
      - Each with reference number and submission date
      - Any outstanding submissions and their deadlines

  section_3_upcoming:
    label_el: "ΕπεÏχόμενες ΥποχÏεώσεις"
    label_en: "Upcoming Obligations"
    content:
      - Deadlines in the next 30 days
      - Any documents still needed from client
      - Any actions required from client

  section_4_attachments:
    conditional: "Only if --include-statements flag used"
    content:
      - Attach P&L summary for the period
      - Attach VAT summary
    note: "Full financial statements attached as PDF from Skill 15 output"

  closing:
    standard_greek_business_closing: true
    contact_details: true
```

---

### 3. Document Request Letter

Sent when documents are missing that are needed to complete a client's accounting for a period.

```yaml
Document_Request_Structure:

  tone_calibration:
    first_request: "Polite — Θα θέλαμε να σας ζητήσουμε..."
    second_request: "Clear — Για την ολοκλήÏωση της λογιστικής σας παÏακολοÏθησης απαιτοÏνται..."
    third_request: "Urgent — Δ απουσία των παÏακάτω εγγÏάφων θα επηÏεάσει την έγκαιÏη υποβολή..."
    note: "System checks correspondence history to determine which tone to use"

  content:
    - Clear list of missing documents in Greek (e.g. "Κινήσεις τÏαπεζικοÏ λογαÏιασμοÏ ΟκτωβÏίου 2025")
    - Why each document is needed (brief, non-technical)
    - Deadline for receipt ("παÏακαλοÏμε να μας τα αποστείλετε έως την DD/MM/YYYY")
    - How to send (email address or preferred method)
    - Contact person at the firm for questions

  auto_populate_from:
    - "/data/clients/{AFM}/documents/pending.json"
    - "openclaw clients compliance-gaps --afm {AFM} --period {period}"
```

---

### 4. Deadline Reminder

```yaml
Deadline_Reminder_Levels:

  informative:          # 30+ days before deadline
    tone_el: "Σας ενημεÏώνουμε ότι πλησιάζει η πÏοθεσμία για..."
    urgency_marker: none

  reminder:             # 14 days before deadline
    tone_el: "Σας υπενθυμίζουμε ότι στις [date] λήγει η πÏοθεσμία για..."
    urgency_marker: none

  urgent:               # 7 days before deadline
    tone_el: "ΣΔΜΑÎΤΘΚΟ: Δ πÏοθεσμία για [type] λήγει σε 7 ημέÏες ([date])."
    urgency_marker: "⚠️ in subject line"

  critical:             # 2 days or less before deadline
    tone_el: "ΕΠΕΘΓΟÎ: Δ πÏοθεσμία για [type] λήγει σε [N] ημέÏες. Απαιτείται άμεση ενέÏγεια."
    urgency_marker: "🚨 in subject line"

  content:
    - Deadline type and date
    - Amount due (if known)
    - What the client needs to do (if anything — usually just "we will handle this")
    - What documents are still needed from them (if any)
    - Firm contact details
```

---

### 5. Annual Tax Summary

Sent once per year (typically February€“March for the prior year). Provides the client with a complete overview of their tax obligations, what was filed, and what is still outstanding.

```yaml
Annual_Summary_Structure:
  sections:
    - All government filings for the year (VAT returns, EFKA, E1 if applicable)
    - Total VAT paid / received
    - Total EFKA contributions (employer and employee)
    - Income tax position (estimated if final not yet assessed)
    - Property taxes (ENFIA) if applicable
    - Any outstanding issues from the year
    - Obligations already known for the coming year
  note: "Pulls from compliance/filings.json for the full year — most comprehensive communication type"
```

---

## Data Sources

```yaml
Required_Data_By_Communication_Type:

  submission_confirmation:
    - "/data/compliance/submissions/{AFM}_{period}_{type}_submission-receipt.json"
    - "/data/clients/{AFM}/compliance/filings.json"
    - "/data/clients/{AFM}/contacts.json"  # recipient details

  monthly_summary:
    - "/data/clients/{AFM}/compliance/filings.json"  # what was filed
    - "/data/banking/reconciliation/{AFM}_{period}_reconciliation.json"  # activity
    - "/data/clients/{AFM}/documents/pending.json"  # what's still missing
    - "/data/clients/{AFM}/financial-statements/{period}_*.json"  # if --include-statements
    - "openclaw deadline check --client {AFM}"  # upcoming obligations

  document_request:
    - "/data/clients/{AFM}/documents/pending.json"
    - "openclaw clients compliance-gaps --afm {AFM}"
    - "/data/clients/{AFM}/correspondence/"  # to determine tone (1st/2nd/3rd request)

  deadline_reminder:
    - "openclaw deadline check --client {AFM} --type {deadline-type}"
    - "/data/clients/{AFM}/contacts.json"

  annual_summary:
    - "/data/clients/{AFM}/compliance/filings.json"  # full year
    - "/data/compliance/vat/" + "/data/compliance/efka/" + "/data/compliance/e1/"
    - "openclaw efka cost-analysis --afm {AFM} --period {year}"
```

---

## File System

```yaml
Communication_File_Structure:

  drafts:
    location: "/data/processing/comms/"
    files:
      - "{draft-id}_{AFM}_{type}_{YYYYMMDD}.json"   # Draft content and metadata
    note: "Ephemeral — cleared after send or explicit discard. Never source of truth."

  sent_records:
    location: "/data/clients/{AFM}/correspondence/"
    files:
      - "{YYYYMMDD}_{type}_{draft-id}_sent.json"    # Immutable record of sent communication
    contains:
      - "draft_id, type, period_reference, recipient_email, sent_by, sent_at_utc"
      - "content_hash (SHA256 of the Greek text sent — not the full text)"
      - "attachments list (filenames only)"
      - "delivery_status: sent / bounced / no-email-configured"
    note: "Sent records are immutable. Never modified after creation."

  firm_communication_log:
    location: "/data/reports/correspondence/"
    files:
      - "{YYYY-MM}_outgoing_log.json"   # Monthly aggregate log across all clients
    note: "For firm-level audit and review. Generated daily, appended during the month."

  templates:
    location: "/data/system/comms-templates/"
    files:
      - "{template-name}.json"          # Base templates
    client_overrides:
      location: "/data/clients/{AFM}/comms-preferences.json"
      contains: "Client-specific salutation, preferred contact, language preference overrides"
```

---

## Approval Workflow

```yaml
Approval_Rules:

  always_required_for:
    - Any communication going to a client
    - Any batch send affecting multiple clients
    - Any custom (free-form) draft

  approval_roles_allowed:
    - senior_accountant   # Can approve all communication types
    - accountant          # Can approve for their assigned clients
    - assistant           # Cannot approve sends — can only create drafts

  approval_gate:
    step_1: "Show draft preview in English (what the letter says)"
    step_2: "Show full Greek text for verification"
    step_3: "Show recipient name and email"
    step_4: "Require: openclaw comms send --draft-id {id} --approved-by {username}"
    step_5: "Verify username has approval role via openclaw auth check-access"
    step_6: "Log approval event to /data/auth/logs/access/"
    step_7: "Send and write sent record"

  no_auto_send_exceptions:
    note: "There are no exceptions. Even batch sends require --approved-by from an authorised user."
```

---

## Memory Integration (Phase 4 — Skill 19 hooks)

```yaml
Memory_Integration:
  log_episodes: true
  episode_types:
    - communication_drafted      # Draft created
    - communication_sent         # Approved and dispatched
    - batch_send_complete        # Batch run completed

  log_failures: true
  failure_types:
    - missing_recipient_email    # Client has no email address configured
    - data_unavailable_for_draft # Required source data not yet in system
    - approval_denied            # Draft reviewed and rejected by accountant
    - delivery_bounced           # Email send attempted but bounced

  rate_limit_group: "phase_3b_operations"

  useful_patterns_to_detect:
    - "Clients who frequently have document requests (chronic missing documents)"
    - "Communication types that are consistently reviewed and edited before send (template improvement candidates)"
    - "Clients where emails bounce (contact details need updating)"
```

---

## Integration Points

```yaml
Upstream_Skills_Read:
  client-data-management:         "Client profile, contact email, correspondence history, pending docs"
  greek-compliance-aade:          "Filing data, submission receipts, VAT amounts"
  greek-financial-statements:     "Statement PDFs to attach to monthly summaries"
  efka-api-integration:           "Contribution amounts for monthly and annual summaries"
  cli-deadline-monitor:           "Upcoming deadlines to reference in reminders and summaries"
  user-authentication-system:     "Verify approval role before any send"

Downstream_Skills_Feed:
  client-data-management:         "Writes sent records to /data/clients/{AFM}/correspondence/"
  conversational-ai-assistant:    "Draft creation triggered via openclaw chat draft, sends via openclaw comms send"
  analytics-and-advisory:         "Correspondence patterns feed Skill 18 (e.g. chronic document requesters)"

Meta_Skill_Integration:
  monthly_process:
    - "Auto-draft submission confirmations after successful VAT/EFKA filing"
    - "Auto-draft monthly summary with --include-statements if statements are ready"
    - "Both drafts queued for human approval — never auto-sent"
  morning_check:
    - "Flags any unsent drafts older than 24 hours as requiring attention"
```

---

## Error Handling

```yaml
Error_Responses:

  no_email_configured:
    output: "Client {AFM} has no email address on file. Draft created — export as PDF for manual delivery."
    action: "Create draft, set delivery_method to pdf-export, log missing email as client record issue"

  missing_source_data:
    output: "Cannot draft {type} for {AFM} {period} — {specific field} not yet available in system."
    action: "Do not create draft. Log as failure. Add to dashboard task queue once data is ready."

  approval_role_insufficient:
    output: "User {username} does not have approval permission for sends. Draft saved — ask an accountant or senior accountant to approve."
    action: "Block send. Log attempt. Draft remains in /data/processing/comms/."

  bounced_delivery:
    output: "Communication to {email} bounced. Draft {id} logged as delivery-failed."
    action: "Write sent record with status=bounced. Alert assigned accountant. Flag client contact details for review."

  template_data_gap:
    output: "Template field [{field}] could not be populated — data not found."
    action: "Populate with [MISSING — please verify] marker. Show to reviewer before approval. Never send with unfilled markers."
```

---

## Success Metrics

A successful deployment of this skill should achieve:
- ✅ Zero communications sent without explicit human approval from an authorised role
- ✅ 100% of sent communications logged against the client record
- ✅ Greek output that a client would receive without knowing it was system-generated
- ✅ Tone correctly escalated for deadline reminders based on days remaining
- ✅ Document request letters draw from live pending.json — never manually typed lists
- ✅ Submission confirmations include actual AADE reference numbers — never placeholders
- ✅ Unfilled template markers ([MISSING]) always caught at review, never sent

Remember: This skill is the firm's voice to its clients. Every letter reflects on the firm's professionalism. Draft quality must be high enough that the reviewer's job is approval, not rewriting.
