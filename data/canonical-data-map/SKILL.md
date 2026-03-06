---
name: canonical-data-map
description: Single source of truth for all paths, naming conventions, and data formats across the OpenClaw Greek Accounting system. Reference document.
version: 1.1.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "data-map", "reference"]
metadata: {"openclaw": {"requires": {"bins": [], "env": ["OPENCLAW_DATA_DIR"]}}}
---

# Canonical Data Directory Map
## OpenClaw Greek Accounting System — v1.1

## Setup

This skill is a reference document — it defines the directory structure and naming conventions used by all other Greek accounting skills. No binaries or credentials required.

```bash
# Set the data directory (all skills read this)
export OPENCLAW_DATA_DIR="/data"

# Initialize the full directory structure
mkdir -p $OPENCLAW_DATA_DIR/{incoming/{invoices,receipts,statements,government},processing,clients,compliance/{vat,efka,mydata,e1,e3},banking/{imports/{alpha,nbg,eurobank,piraeus},processing,reconciliation},ocr/{incoming,output},reports,auth,system/{logs,process-locks},backups}
```

This document defines the complete file system architecture for the OpenClaw Greek Accounting system. It is the authoritative reference for all path decisions. No skill may introduce a new top-level directory or deviate from the naming conventions defined here without a version update to this document.

**v1.1 change:** Added `/data/memory/` — agent episodic memory, failure logs, pattern store, GitHub proposal queue, and rate-limit state. Owner: `memory-feedback` (Skill 19, Phase 4). All Phase 3B+ skills must include episode and failure log hooks that write into this tree.

---

## Root Structure

```
/data/
╔══ incoming/          # All raw input — documents arriving into the system
╔══ processing/        # Temporary working space — files mid-pipeline
╔══ clients/           # Canonical client records — the source of truth
╔══ compliance/        # Government filings and submissions
╔══ banking/           # Bank statement processing pipeline
╔══ ocr/               # OCR processing pipeline
╔══ efka/              # EFKA/social security processing pipeline
╔══ reports/           # Generated reports for human consumption
╔══ exports/           # Data exports leaving the system
╔══ imports/           # Bulk data imports entering the system
╔══ dashboard/         # Dashboard state, config, cache, history
╔══ auth/              # Authentication and access control
╔══ backups/           # Encrypted system backups
╔══ gdpr-exports/      # GDPR subject access request exports
╔══ memory/            # Agent episodic memory, failure logs, learning patterns, proposals
└══ system/            # System-level files: logs, schema versions, locks
```

---

## 1. `/data/incoming/` — Raw Input

All documents entering the system land here first, regardless of source (email attachment, manual drop, scanner, bank download). Nothing in `/data/incoming/` is processed yet.

```
/data/incoming/
╔══ invoices/          # Supplier invoices (PDF, image)
╔══ receipts/          # Receipts (PDF, image, phone photo)
╔══ statements/        # Bank statements (PDF, CSV, OFX)
╔══ government/        # AADE/EFKA notifications and documents
╔══ payroll/           # Hour sheets, employee documents
╔══ tax-documents/     # Tax certificates, employer statements (βεβαιώσεις)
╔══ contracts/         # Contracts and legal documents
└══ other/             # Uncategorised — routed after classification
```

**Naming convention for incoming files:**
Files dropped here may arrive with any name. The system must NOT rename them on arrival — the original filename is preserved for audit purposes. The system assigns a canonical name only when moving to `/data/processing/`.

---

## 2. `/data/processing/` — In-Flight Pipeline

Temporary working space. Files here are mid-pipeline and may be incomplete. No other skill should read from `/data/processing/` as a final source — always read from `/data/clients/` or `/data/compliance/` for canonical data.

```
/data/processing/
╔══ ocr/               # OCR in progress
╚   ╔══ queued/        # Waiting for OCR
╚   ╔══ enhanced/      # Image pre-processing complete
╚   ╔══ extracted/     # Text extracted, not yet validated
╚   └══ validated/     # OCR output validated, ready to route
╔══ classification/    # Document type identification in progress
╔══ reconciliation/    # Bank reconciliation working files
╚   ╔══ matching/      # Transaction matching in progress
╚   └══ flagged/       # Items needing human review
╔══ compliance/        # Filing preparation working files
╚   ╔══ vat/           # VAT return preparation
╚   ╔══ efka/          # EFKA declaration preparation
╚   └══ mydata/        # myDATA submission preparation
└══ imports/           # Bulk import validation in progress
```

**Cleanup policy:** Files in `/data/processing/` are deleted or archived after the pipeline completes successfully. They are never the canonical record.

---

## 3. `/data/clients/` — Client Master Records

The single source of truth for all client data. Every other skill that needs client information reads from here. Only the `client-data-management` skill writes to this tree.

```
/data/clients/
╔══ _index.json                    # Global client index (name, AFM, status, assignee)
╔══ _audit-log.json                # All access and change events across all clients
╔══ _schema-version.json           # Current schema version for migration tracking
└══ {AFM}/                         # One directory per client, keyed by AFM (e.g. EL123456789)
    ╔══ profile.json               # Master client record
    ╔══ identifiers.json           # AFM, GEMI, EFKA employer ID, IBANs
    ╔══ contacts.json              # Contact persons
    ╔══ notes.json                 # Relationship notes and meeting logs
    ╔══ compliance/
    ╚   ╔══ filings.json           # All completed filings (VAT, EFKA, E1, etc.)
    ╚   ╔══ obligations.json       # Recurring obligation schedule
    ╚   └══ gaps.json              # Missing/overdue filing log
    ╔══ documents/
    ╚   ╔══ registry.json          # Metadata index of all documents for this client
    ╚   ╔══ pending.json           # Documents awaiting processing or review
    ╚   └══ archive-index.json     # References to archived documents
    ╔══ correspondence/
    ╚   └══ {YYYYMMDD}_{type}_{draft-id}_sent.json  # Immutable sent communication records
    ╔══ comms-preferences.json     # Client-specific salutation, contact, language overrides
    ╔══ payroll/
    ╚   └══ {YYYY-MM}/             # One folder per pay period
    ╚       ╔══ hours-input.csv    # Raw hours data
    ╚       ╔══ calculations.json  # Computed payroll data
    ╚       └══ {employee-slug}_payslip.pdf   # Generated payslips
    ╔══ financial-statements/
    ╚   ╔══ index.json             # All generated statements, versions, periods, status
    ╚   ╔══ {YYYY-MM}_pl_v{N}.json               # P&L machine-readable
    ╚   ╔══ {YYYY-MM}_balance-sheet_v{N}.json     # Balance sheet machine-readable
    ╚   ╔══ {YYYY-MM}_cash-flow_v{N}.json         # Cash flow machine-readable
    ╚   └══ {YYYY-MM}_vat-summary_v{N}.json       # VAT summary machine-readable
    └══ gdpr/
        ╔══ consent.json           # Consent records
        ╔══ retention-policy.json  # Retention schedule for this client
        └══ deletion-log.json      # Record of any deletions performed
```

**AFM format:** Always `EL` + 9 digits, uppercase. Example: `EL123456789`. Never store without the `EL` prefix. Never use the 9-digit-only form as a directory name.

---

## 4. `/data/compliance/` — Government Filings

Stores the actual submission files (XML, PDF) generated for government platforms. The filing *record* lives in `/data/clients/{AFM}/compliance/filings.json` — this directory holds the *file artefacts* themselves.

```
/data/compliance/
╔══ vat/
╚   └══ {AFM}_{YYYY}{MM}_vat_return.xml      # VAT return XML for TAXIS
╔══ mydata/
╚   └══ {AFM}_{YYYY}{MM}_{invoice-number}_mydata.xml
╔══ efka/
╚   └══ {AFM}_{YYYY}{MM}_efka_declaration.xml
╔══ e1/
╚   └══ {AFM}_{YYYY}_e1_form.xml             # Individual tax returns
╔══ e3/
╚   └══ {AFM}_{YYYY}_e3_form.xml             # Business activity statements
╔══ corporate-tax/
╚   └══ {AFM}_{YYYY}_corporate_tax.xml
└══ submissions/
    └══ {AFM}_{YYYY}{MM}_{type}_submission-receipt.json   # Government confirmation receipts
```

**Naming convention:** `{AFM}_{period}_{type}.{ext}` — always lowercase type, always ISO period format (YYYYMM or YYYY), always the full AFM with EL prefix.

---

## 5. `/data/banking/` — Bank Statement Pipeline

```
/data/banking/
╔══ imports/
╚   ╔══ alpha/         # Alpha Bank raw statement files
╚   ╔══ nbg/           # National Bank of Greece
╚   ╔══ eurobank/      # Eurobank
╚   ╔══ piraeus/       # Piraeus Bank
╚   └══ other/         # Other banks
╔══ processing/
╚   ╔══ raw/           # Imported, not yet validated
╚   ╔══ validated/     # Format validation complete
╚   ╔══ categorized/   # Transactions categorised
╚   └══ reconciled/    # Reconciliation complete
╔══ reconciliation/
╚   └══ {AFM}_{YYYY-MM}_reconciliation.json  # Per-client reconciliation reports
└══ exports/
    └══ {AFM}_{YYYY-MM}_transactions.csv     # Clean transaction exports
```

**Note:** `/data/alpha-bank/`, `/data/nbg-statements/`, `/data/eurobank/`, `/data/piraeus-bank/` used in earlier skill versions are **deprecated**. All bank imports go through `/data/banking/imports/{bank}/`.

---

## 6. `/data/ocr/` — OCR Processing Pipeline

```
/data/ocr/
╔══ incoming/
╚   ╔══ scanned/       # Flatbed scanner input
╚   ╔══ photos/        # Mobile phone photos of documents
╚   ╔══ government/    # Government-issued documents (AADE letters, etc.)
╚   └══ handwritten/   # Handwritten documents requiring special handling
╔══ preprocessing/
╚   └══ enhanced/      # Image-enhanced versions awaiting OCR
╔══ processing/
╚   ╔══ greek-ocr/     # Greek language OCR in progress
╚   ╔══ classification/ # Document type being determined
╚   └══ validation/    # OCR output being validated
╔══ output/
╚   ╔══ text-extracted/       # Raw text output from OCR
╚   ╔══ structured-data/      # Structured JSON extracted from text
╚   └══ searchable-pdf/       # PDFs with embedded text layer
└══ accounting-ready/          # Processed output ready for accounting-workflows skill
```

**Note:** `/data/scanned-documents/` used in earlier skill versions is **deprecated**. All scanned input goes to `/data/ocr/incoming/scanned/`.

---

## 7. `/data/efka/` — EFKA Processing Pipeline

```
/data/efka/
╔══ employees/
╚   ╔══ active/        # Current employee records
╚   ╔══ pending/       # New employees awaiting EFKA registration
╚   ╔══ terminated/    # Terminated employees (retained per legal requirements)
╚   ╔══ imports/       # Bulk employee data imports
╚   ╔══ updates/       # Pending employee record changes
╚   └══ validated/     # Imports validated, ready to commit
╔══ contributions/
╚   ╔══ monthly/       # Monthly contribution calculations by period
╚   ╔══ quarterly/     # Quarterly summaries
╚   ╔══ annual/        # Annual totals
╚   ╔══ calculated/    # Computed contributions awaiting validation
╚   ╔══ validated/     # Validated, ready to submit
╚   └══ payments/      # Payment confirmation records
╔══ payroll/
╚   ╔══ input/         # Raw hours and salary data
╚   ╔══ validated/     # Validated input
╚   ╔══ processed/     # Calculations complete
╚   └══ ready-submit/  # Ready for EFKA portal submission
╔══ submissions/
╚   ╔══ ready/         # Submission files ready to send
╚   ╔══ efka-portal/   # Submitted to EFKA portal (confirmation pending)
╚   └══ aade-cross/    # Cross-referenced with AADE for consistency
╔══ responses/
╚   ╔══ confirmations/ # EFKA acceptance receipts
╚   └══ corrections/   # EFKA rejection/correction requests
╔══ deadlines/
╚   ╔══ upcoming/      # Deadlines in the next 30 days
╚   └══ overdue/       # Missed deadlines requiring urgent action
╔══ audit/
╚   ╔══ employee-records/    # Audit-ready employee documentation
╚   └══ contribution-proof/  # Proof of contribution payments
└══ compliance/
    └══ monitoring/    # Ongoing compliance status tracking
```

---

## 8. `/data/reports/` — Generated Reports

Human-readable reports. These are outputs, not inputs to other skills.

```
/data/reports/
╔══ daily/
╚   └══ {YYYY-MM-DD}_daily_summary.pdf
╔══ weekly/
╚   └══ {YYYY-WNN}_weekly_report.pdf
╔══ monthly/
╚   └══ {YYYY-MM}_monthly_report.pdf
╔══ client/
╚   └══ {AFM}_{YYYY-MM}_{report-type}.pdf
╔══ compliance/
╚   └══ {AFM}_{YYYY-MM}_compliance_status.pdf
╔══ reconciliation/
╚   └══ {AFM}_{YYYY-MM}_reconciliation_report.pdf
└══ financial-statements/
    └══ {AFM}_{YYYY-MM}_financial-pack_v{N}.pdf   # Client-facing PDF statement pack
```

**Note:** `/data/reports/monthly-expenses.json` (used in Skill 1) is deprecated. Expense data belongs in `/data/clients/{AFM}/compliance/` or exported via `/data/exports/`.

---

## 9. `/data/exports/` — Data Leaving the System

Files generated for external consumption (Excel exports, CSV downloads, accounting software imports).

```
/data/exports/
╔══ clients/
╚   └══ {YYYY-MM-DD}_client_export.{xlsx|csv|json}
╔══ transactions/
╚   └══ {AFM}_{YYYY-MM}_transactions.{csv|xlsx}
╔══ compliance/
╚   └══ {AFM}_{YYYY}_compliance_summary.xlsx
└══ accounting-software/
    └══ {AFM}_{YYYY-MM}_{target-system}.{qbx|csv|xlsx}
```

---

## 10. `/data/imports/` — Bulk Data Entering the System

Structured bulk imports (spreadsheets of client lists, employee rosters, etc.) — not raw documents (those go to `/data/incoming/`).

```
/data/imports/
╔══ clients/           # Bulk client onboarding files
╔══ employees/         # Bulk employee roster imports
└══ historical/        # Historical data migration files
```

---

## 11. `/data/dashboard/` — Dashboard State

```
/data/dashboard/
╔══ config/
╚   ╔══ firm-settings.yaml
╚   ╔══ alert-rules.yaml
╚   ╔══ report-templates.yaml
╚   └══ user-preferences/{username}.yaml
╔══ state/
╚   ╔══ client-status.json      # Current status snapshot for all clients
╚   ╔══ current-alerts.json     # Active alerts
╚   ╔══ deadline-tracker.json   # Upcoming deadlines
╚   ╔══ task-queue.json         # Pending task list
╚   └══ system-health.json      # Skill integration health
╔══ cache/
╚   ╔══ aade-latest.json
╚   ╔══ efka-latest.json
╚   ╔══ bank-feeds-latest.json
╚   └══ ocr-queue-status.json
╔══ reports/
╚   ╔══ daily/
╚   ╔══ weekly/
╚   ╔══ monthly/
╚   └══ client-specific/
└══ history/
    ╔══ alerts/
    ╔══ compliance-scores/
    └══ performance-metrics/
```

---

## 12. `/data/auth/` — Authentication & Access Control

```
/data/auth/
╔══ users/
╚   └══ {username}/
╚       ╔══ profile.json
╚       ╔══ credentials.json     # Hashed — never plaintext
╚       ╔══ permissions.json
╚       ╔══ 2fa/
╚       └══ sessions/
╚           └══ {session-id}.json
╔══ roles/
╚   ╔══ senior_accountant.json
╚   ╔══ accountant.json
╚   ╔══ assistant.json
╚   ╔══ viewer.json
╚   └══ custom/
╔══ access/
╚   ╔══ client_assignments.json
╚   ╔══ policies.json
╚   └══ ip_whitelist.json
└══ logs/
    ╔══ logins/
    ╔══ access/
    ╔══ admin/
    └══ security/
```

---

## 13. `/data/backups/` — Encrypted Backups

```
/data/backups/
╔══ full_{YYYYMMDD}.tar.enc                        # Full system backup (weekly)
╔══ incremental_{YYYYMMDD}.tar.enc                 # Incremental backup (daily)
╔══ clients_{YYYYMMDD}_{HHMMSS}.json.enc           # Client snapshot (event-driven)
╔══ compliance_{YYYYMMDD}_{HHMMSS}.json.enc        # Compliance snapshot (post-submission)
╔══ auth_{YYYYMMDD}.json.enc                       # Auth data backup
╔══ restore-test/                                  # Ephemeral — restore verification workspace
└══ archives/                                      # Long-term retention archives (post-active)
```

**Naming convention:** Always include date and time in backup filename. Always `.enc` extension for encrypted files. Encryption keys are stored outside `/data/` — never adjacent to backup files.

---

## 14. `/data/gdpr-exports/` — GDPR Subject Access Exports

```
/data/gdpr-exports/
└══ {AFM}_gdpr_export_{YYYYMMDD}.json
```

---

## 15. `/data/system/` — System Files

```
/data/system/
╔══ skill-versions.json          # Installed skill versions and checksums
╔══ migration-log.json           # Schema migration history
╔══ process-locks/               # Concurrency locks (prevent double-processing)
╔══ error-log/
╚   └══ {YYYY-MM-DD}_errors.log
╔══ migrations/
╚   └══ v{N.N}_{YYYYMMDD}_{description}.json  # Schema migration definitions
╔══ integrity/
╚   ╔══ audit-log.json           # Permanent integrity event log (all checks and results)
╚   ╔══ hash-registry.json       # SHA256 hashes of all canonical data files
╚   ╔══ retention-schedule.json  # Active retention schedule configuration
╚   └══ last-check-results.json  # Most recent integrity check results (dashboard feed)
╔══ backups/
╚   └══ backup-manifest.json     # Index of all backup files with metadata and verify status
╔══ chat-sessions/
╚   └══ {username}/
╚       └══ {YYYY-MM-DD}_{session-id}.json   # Conversational assistant session logs
└══ chat-context/
    └══ {username}/
        └══ active-context.json              # Active session context (cleared on session end)
```

---

## 16. `/data/memory/` — Agent Memory & Feedback

The agent's episodic memory, failure capture, pattern learning store, GitHub proposal queue, and rate-limit state. Written to by all skills (episode and failure hooks) and managed by the `memory-feedback` skill (Skill 19). No skill other than `memory-feedback` reads from this tree for decision-making — it is strictly write-on-event, read-by-Skill-19.

```
/data/memory/
╔══ episodes/
╚   └══ {YYYY-MM-DD}/
╚       └══ {session-id}_{action-type}.json    # Successful/completed agent actions
╔══ failures/
╚   └══ {YYYY-MM-DD}/
╚       └══ {session-id}_{failure-type}.json   # Failures with structured reflection
╔══ patterns/
╚   ╔══ successes/
╚   ╚   └══ {pattern-id}.json                  # Recurring good outcomes extracted from episodes
╚   └══ failures/
╚       └══ {pattern-id}.json                  # Recurring problems extracted from failures
╔══ corrections/
╚   └══ {YYYY-MM-DD}_{correction-id}.json      # Human corrections to agent behaviour
╔══ proposals/
╚   └══ {YYYY-MM-DD}_{skill-name}_{id}.md      # Draft skill improvements awaiting GitHub PR
└══ rate-limits/
    ╔══ current-state.json                      # Live token and storage consumption
    ╔══ daily-log.json                          # Per-day consumption history
    └══ config.json                             # Configurable limits (hard floors enforced)
```

**Episode logging trigger:** Any agent action that makes a decision, produces output, or interacts with a government system. Trivial reads are not logged.

**Failure logging trigger:** Any error, intent misread, missing data condition, or human correction. Always includes `what_should_have_happened` field.

**Pattern scan schedule:** Once daily at 02:00 Athens time. Never during business hours. Maximum 3 proposals per day. Maximum 2 GitHub PRs per day.

**Storage limits (defaults):**
- Episodes: 500 MB max — auto-archive after 90 days
- Failures: 200 MB max
- Patterns: 50 MB max
- Proposals: 50 MB max
- Total `/data/memory/`: 2 GB hard ceiling — system halts memory writes at 90% capacity

**GitHub integration:** When a failure pattern reaches confidence threshold (≥0.85, ≥3 occurrences), `memory-feedback` creates a branch on GitHub and opens a pull request against the relevant SKILL.md file. Human must review and merge. Agent never pushes directly to main. Rejected PRs are logged — the same change is never re-proposed.

**Rate limit tokens:** Memory and reflection operations are budgeted separately from accounting operations. Default: 5,000 tokens/day for all memory processes combined.

---

## Global Naming Conventions

### Identifiers

| Identifier | Format | Example | Notes |
|---|---|---|---|
| AFM (VAT) | `EL` + 9 digits | `EL123456789` | Always uppercase EL prefix. Never 9-digit-only. |
| EFKA employer ID | 8 digits | `12345678` | No prefix |
| GEMI | 9€“12 digits | `012345678` | May have leading zeros — preserve them |
| Contact ID | `C` + 3 digits | `C001` | Per-client sequential |
| Filing ID | `{type}-{AFM}-{YYYY}-{MM}` | `VAT-EL123456789-2026-01` | |
| Document ID | `D` + 6 digits | `D000123` | Global sequential |
| Audit event ID | `AUD-{YYYYMMDD}-{6digits}` | `AUD-20260218-001234` | |
| Backup ID | `{type}_{YYYYMMDD}_{HHMMSS}` | `clients_20260218_143022` | |
| Episode ID | `EP-{YYYYMMDD}-{3digits}` | `EP-20260218-001` | Global sequential per day |
| Failure ID | `FAIL-{YYYYMMDD}-{3digits}` | `FAIL-20260218-003` | Global sequential per day |
| Pattern ID | `PAT-{YYYYMMDD}-{3digits}` | `PAT-20260218-007` | Assigned at detection |
| Correction ID | `COR-{YYYYMMDD}-{3digits}` | `COR-20260218-001` | Human-assigned |
| Session ID | `S{YYYYMMDD}-{3digits}` | `S20260218-001` | Per user session |

### Date & Time Formats

| Context | Format | Example | Notes |
| File names | `YYYYMMDD` | `20260218` | No separators in filenames |
| File names with time | `YYYYMMDD_HHMMSS` | `20260218_143022` | |
| Period references | `YYYY-MM` | `2026-01` | Monthly periods |
| ISO timestamps (JSON) | `YYYY-MM-DDTHH:MM:SSZ` | `2026-02-18T14:30:00Z` | Always UTC in storage |
| Display to users | `DD/MM/YYYY` | `18/02/2026` | Greek date format |
| CLI arguments `--date` | `YYYY-MM-DD` | `2026-02-18` | ISO for CLI args |
| CLI arguments `--period` | `YYYY-MM` | `2026-01` | |

### Currency

| JSON storage | Numeric, 2dp | `12500.00` | Never include € symbol in stored values |
| File names | No currency | `12500` | Integer amounts only in filenames |
| Display to users | `€XX,XXX.XX` | `€12,500.00` | Standard EU format |
| CLI output | `EUR XX,XXX.XX` | `EUR 12,500.00` | ASCII-safe for terminal |

### File Naming Pattern

**Pattern:** `{AFM}_{YYYY-MM}_{type}_{optional-detail}.{ext}`

Examples:
- `EL123456789_2026-01_vat_return.xml`
- `EL123456789_2026-02_reconciliation_report.pdf`
- `EL123456789_2025_e1_form.xml`
- `EL123456789_2026-02_payslip_nikos-papadopoulos.pdf`

**Rules:**
- Lowercase type and detail segments
- Hyphens within segments (not underscores)
- Underscores between segments
- No spaces anywhere in file names
- No Greek characters in file names — use Latin transliteration for employee names
- No special characters except hyphens and underscores

### Employee Name Slugs (for file names)

Greek names in file names must be transliterated to ASCII lowercase with hyphens:
- `Îίκος Παπαδόπουλος` → `nikos-papadopoulos`
- `ΜαÏία Κωνσταντίνου` → `maria-konstantinou`
- `ΔήμητÏα ΚαλαμαÏά` → `dimitra-kalamara`

---

## Deprecated Paths — Do Not Use

These paths appear in earlier skill versions and must not be used in any new skill. When encountered in existing commands, treat as aliases that redirect to the canonical paths.

| Deprecated | Canonical Replacement |
|---|---|
| `/data/alpha-bank/` | `/data/banking/imports/alpha/` |
| `/data/nbg-statements/` | `/data/banking/imports/nbg/` |
| `/data/eurobank/` | `/data/banking/imports/eurobank/` |
| `/data/piraeus-bank/` | `/data/banking/imports/piraeus/` |
| `/data/bank-imports/` | `/data/banking/imports/` |
| `/data/scanned-documents/` | `/data/ocr/incoming/scanned/` |
| `/data/email-attachments` | `/data/incoming/` (classified) |
| `/data/email-imports/` | `/data/incoming/` |
| `/data/invoices` | `/data/incoming/invoices/` (if raw) or `/data/clients/{AFM}/documents/` (if processed) |
| `/data/processed/invoices/` | `/data/clients/{AFM}/documents/` + registry entry |
| `/data/processed/receipts/` | `/data/clients/{AFM}/documents/` + registry entry |
| `/data/processed/E1_2025.pdf` | `/data/compliance/e1/EL{AFM}_2025_e1_form.xml` |
| `/data/processing/classification` | `/data/processing/classification/` |
| `/data/processing/extraction` | `/data/processing/ocr/extracted/` |
| `/data/processing/validation` | `/data/processing/ocr/validated/` |
| `/data/reports/monthly-expenses.json` | `/data/clients/{AFM}/compliance/` or `/data/exports/` |
| `/data/payroll/monthly.xlsx` | `/data/efka/payroll/input/` or `/data/clients/{AFM}/payroll/` |
| `/data/export/accounting-software` | `/data/exports/accounting-software/` |
| `/data/aade-downloads/` | `/data/incoming/government/` |
| `/data/aade-outputs/` | `/data/reports/` or `/data/compliance/` (by type) |
| `/data/aade-processing/` | `/data/processing/compliance/` |
| `/data/compliance-updates/` | `/data/incoming/government/` |

---

## Skill Responsibility Matrix

Which skill owns (writes to) each top-level directory:

| Directory | Owner Skill | Other Skills May Read |
|---|---|---|
| `/data/incoming/` | `accounting-workflows` | All skills |
| `/data/processing/` | Pipeline skill handling the job | None as final source |
| `/data/clients/` | `client-data-management` | All skills (read only) |
| `/data/compliance/` | `greek-compliance-aade` | `aade-api-monitor`, `efka-api-integration`, `dashboard` |
| `/data/banking/` | `greek-banking-integration` | `accounting-workflows`, `dashboard` |
| `/data/ocr/` | `greek-document-ocr` | `accounting-workflows`, `greek-email-processor` |
| `/data/efka/` | `efka-api-integration` | `greek-compliance-aade`, `dashboard` |
| `/data/reports/` | `dashboard-greek-accounting` | All skills (read) |
| `/data/reports/analytics/` | `analytics-and-advisory-intelligence` | `conversational-ai-assistant`, `dashboard-greek-accounting` |
| `/data/reports/system/` | `system-integrity-and-backup` | `dashboard-greek-accounting` (read) |
| `/data/clients/{AFM}/financial-statements/` | `greek-financial-statements` | `conversational-ai-assistant`, `client-communication-engine`, `analytics-and-advisory-intelligence` |
| `/data/clients/{AFM}/correspondence/` | `client-communication-engine` | `conversational-ai-assistant`, `analytics-and-advisory-intelligence` |
| `/data/processing/comms/` | `client-communication-engine` | Ephemeral drafts only — cleared after send |
| `/data/backups/` | `system-integrity-and-backup` | All skills trigger event-driven snapshots via meta-skill |
| `/data/system/integrity/` | `system-integrity-and-backup` | All skills write hash on canonical file write |
| `/data/exports/` | Any skill (with `--export`) | External consumers |
| `/data/imports/` | `client-data-management` | `efka-api-integration` |
| `/data/dashboard/` | `dashboard-greek-accounting` | `user-authentication-system` |
| `/data/auth/` | `user-authentication-system` | All skills (auth check) |
| `/data/gdpr-exports/` | `client-data-management` | None |
| `/data/system/` | OpenClaw system | All skills (read) |
| `/data/memory/` | `memory-feedback` (Skill 19) | All skills write episode/failure hooks; only Skill 19 reads for analysis |

---

## Enforcement Rules for All Skills

1. **Never introduce a new top-level directory** under `/data/` without updating this document first.
2. **Never write processed/canonical data to `/data/processing/`** — it is temporary only.
3. **Never write client data outside `/data/clients/{AFM}/`** — client-data-management is the only writer.
4. **Always use the full AFM with EL prefix** in all paths, filenames, and JSON keys.
5. **Always use ISO date format** (`YYYY-MM-DD` or `YYYYMMDD`) in file names and JSON — never `DD/MM/YYYY` in stored data.
6. **Never use Greek characters in file names or directory names** — only in JSON values and display output.
7. **Currency values in JSON are always numeric** — never strings with € symbols.
8. **All timestamps in JSON are UTC** — display conversion to `Europe/Athens` happens at the output layer only.
9. **The `/data/processing/` tree is ephemeral** — never reference it as the source of truth from another skill.
10. **Deprecated paths are read-only legacy** — redirect to canonical paths, never create new files at deprecated locations.


---

## Unified Audit Event Schema

Every skill must log significant actions using this single JSON schema. Audit events are written to `/data/system/logs/audit/` and are the authoritative record for regulatory inspection.

```json
{
  "event_id": "EVT-20260219-143022-a7b3",
  "timestamp": "2026-02-19T14:30:22Z",
  "skill": "greek-compliance-aade",
  "action": "vat_return_submitted",
  "category": "government_submission",
  "user": {
    "username": "m.papadopoulou",
    "role": "senior_accountant",
    "ip_address": "192.168.1.42"
  },
  "client": {
    "afm": "EL123456789",
    "name": "ALPHA TRADING AE"
  },
  "details": {
    "period": "2026-01",
    "filing_type": "F2_VAT_RETURN",
    "amount": 3340.00,
    "submission_ref": "AADE-2026-0142"
  },
  "before_state": null,
  "after_state": "submitted",
  "approval": {
    "prepared_by": "a.nikolaou",
    "approved_by": "m.papadopoulou",
    "approved_at": "2026-02-19T14:28:00Z"
  },
  "data_classification": "confidential",
  "result": "success"
}
```

**Required fields for all events:** `event_id`, `timestamp`, `skill`, `action`, `category`, `user.username`, `user.role`, `result`.

**Optional fields:** `client`, `details`, `before_state`, `after_state`, `approval`, `data_classification`.

**Event categories:**
- `government_submission` — any filing sent to AADE, EFKA, myDATA
- `data_modification` — create, update, or delete of client records
- `access_event` — login, logout, session activity, access denial
- `document_processing` — OCR, classification, extraction, validation
- `financial_output` — statement generation, amendment, report creation
- `communication` — client correspondence sent
- `system_operation` — backup, integrity check, schema migration
- `security_event` — lockout, 2FA failure, session revocation, permission change

**Storage:** `/data/system/logs/audit/{YYYY-MM-DD}_audit.jsonl` (one JSON object per line, append-only).

**Retention:** Audit logs are retained for 10 years per Greek tax law and EU regulatory requirements.

---

## Encryption-at-Rest Specification

Directories containing sensitive data must be encrypted at rest in production deployments. This is required for GDPR compliance (EU Regulation 2016/679, implemented in Greece by Law 4624/2019).

### Directories Requiring Encryption

| Directory | Classification | Encryption Required | Rationale |
|---|---|---|---|
| `/data/auth/` | Restricted | **Mandatory** | Credential hashes, session data, 2FA secrets |
| `/data/clients/` | Confidential | **Mandatory** | Financial records, PII (names, AFMs, IBANs) |
| `/data/compliance/` | Confidential | **Mandatory** | Tax filings containing financial data |
| `/data/efka/` | Confidential | **Mandatory** | Employee PII, salary data, social security numbers |
| `/data/banking/` | Confidential | **Recommended** | Bank statements, account numbers |
| `/data/backups/` | Confidential | **Already encrypted** | AES-256 via Skill 17 |
| `/data/gdpr-exports/` | Confidential | **Mandatory** | Subject access request data |
| `/data/processing/` | Internal | Optional | Ephemeral — deleted after pipeline |
| `/data/reports/` | Internal | Recommended | May contain client financial summaries |
| `/data/system/` | Internal | Optional | Logs and operational data |

### Implementation

```yaml
Encryption_At_Rest:
  method: "AES-256-GCM"
  key_management:
    master_key_source: "Environment variable OPENCLAW_ENCRYPTION_KEY or hardware security module"
    key_rotation: "Annual, or immediately on suspected compromise"
    never: "Never store the master key inside /data/ or in any SKILL.md file"
    
  options:
    full_disk: "Preferred — use LUKS/dm-crypt on the volume hosting /data/"
    directory_level: "Alternative — use fscrypt or gocryptfs per directory"
    file_level: "Minimum — encrypt individual JSON files with per-file keys derived from master"
    
  verification:
    command: "openclaw integrity verify-encryption --check-all-sensitive-dirs"
    schedule: "Weekly, as part of system integrity check"
```

### Data Classification Labels

Every JSON record stored in encrypted directories should include a `data_classification` field:

```json
{
  "data_classification": "confidential"
}
```

Valid values: `public`, `internal`, `confidential`, `restricted`.

This field enables rapid scoping during GDPR breach notification (72-hour requirement) — you can quickly determine what classification of data was exposed.

---

## Professional Liability Disclaimer Template

Every client-facing document generated by the system must include this disclaimer. Skills that produce client-visible output (Skills 15, 16, 18) must append this to their output templates.

### Standard Disclaimer (Greek)

```
Το παρόν έγγραφο συντάχθηκε με τη χρήση αυτοματοποιημένου λογισμικού λογιστικής
υποβοήθησης. Οι πληροφορίες που περιέχονται δεν αποτελούν επαγγελματική λογιστική
ή φορολογική συμβουλή. Συνιστάται η επανεξέταση από αδειοδοτημένο λογιστή πριν
από τη λήψη οποιασδήποτε απόφασης βάσει αυτού του εγγράφου.
```

### Standard Disclaimer (English)

```
This document was prepared with the assistance of automated accounting software.
The information contained herein does not constitute professional accounting or
tax advice. Review by a licensed accountant is recommended before making any
decisions based on this document.
```

### Usage Rules

- **Financial statements** (Skill 15): Include both Greek and English disclaimers in PDF footer
- **Client correspondence** (Skill 16): Include Greek disclaimer in email footer
- **Advisory reports** (Skill 18): Include English disclaimer in internal reports, Greek in client-facing
- **Government submissions**: Disclaimer is NOT included in filings sent to AADE/EFKA (these are formal submissions, not advisory documents)

---

## Input Validation Rules

All skills must validate incoming data against these rules before processing. Invalid input must be rejected with a clear error message — never silently accepted.

### Identifier Validation

```yaml
Validation_Rules:
  afm:
    format: "EL followed by exactly 9 digits"
    regex: "^EL[0-9]{9}$"
    examples_valid: ["EL123456789", "EL000000001"]
    examples_invalid: ["123456789", "EL12345", "el123456789", "GR123456789"]
    
  iban:
    format: "GR followed by 25 alphanumeric characters"
    regex: "^GR[0-9]{25}$"
    note: "Validate check digits per ISO 13616"
    
  ama:
    description: "EFKA registration number"
    format: "Numeric, variable length up to 12 digits"
    regex: "^[0-9]{1,12}$"
    
  amka:
    description: "Social security number"
    format: "Exactly 11 digits (DDMMYY + 5 sequence digits)"
    regex: "^[0-9]{11}$"
```

### Financial Value Validation

```yaml
Financial_Validation:
  currency_amounts:
    type: "numeric (float or decimal)"
    precision: "2 decimal places"
    never: "Never store as string with euro symbol"
    range: "0.00 to 999,999,999.99 for normal operations"
    negative: "Allowed for credit notes and adjustments — flag if unexpected"
    
  vat_rates:
    valid_values: [0.24, 0.13, 0.06, 0.0]
    labels: ["24% standard", "13% reduced", "6% super-reduced", "0% exempt"]
    note: "Reject any other rate — may indicate data entry error"
    
  periods:
    monthly: "YYYY-MM format, e.g. 2026-01"
    annual: "YYYY format, e.g. 2025"
    regex_monthly: "^[0-9]{4}-(0[1-9]|1[0-2])$"
    regex_annual: "^[0-9]{4}$"
```

### Date and Time Validation

```yaml
Date_Validation:
  stored_format: "ISO 8601: YYYY-MM-DD for dates, YYYY-MM-DDTHH:MM:SSZ for timestamps"
  display_format: "DD/MM/YYYY for Greek client output, YYYY-MM-DD for internal"
  timezone: "All stored timestamps in UTC. Convert to Europe/Athens only at display layer."
  never: "Never store DD/MM/YYYY in JSON — only in display templates"
  
  fiscal_year:
    default: "Calendar year (January 1 — December 31)"
    alternative: "Some entities use non-calendar fiscal years — check client profile"
```

### String Validation

```yaml
String_Validation:
  client_names:
    charset: "Greek Unicode (U+0370-U+03FF) and Latin characters, spaces, hyphens, periods"
    max_length: 200
    note: "Store in original case — never force uppercase in storage (uppercase for display only)"
    
  file_names:
    charset: "Latin alphanumeric, hyphens, underscores, periods only"
    never: "Never use Greek characters, spaces, or special characters in file names"
    max_length: 255
    
  descriptions:
    charset: "Any UTF-8"
    max_length: 2000
```
