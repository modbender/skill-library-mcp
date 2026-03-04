---
name: caseclaw
description: Missed deadlines are the #1 malpractice trigger. caseclaw auto-calculates every deadline from 600+ court rule sets, runs conflict checks before you even open the file, and captures billable time you'd otherwise forget—right from your terminal. Free forever for solo attorneys. Pro for firms that can't afford mistakes.
homepage: https://github.com/legal-tools/caseclaw
metadata: {"clawdbot":{"emoji":"🔱","requires":{"bins":["caseclaw"]},"install":[{"id":"brew","kind":"brew","formula":"legal-tools/tap/caseclaw","bins":["caseclaw"],"label":"Install caseclaw (brew)"}]}}
---

# caseclaw

**One missed deadline ends a career. caseclaw makes sure it never happens.**

Missed deadlines cause more malpractice suits than bad legal advice. Conflicts of interest are a close second. And every attorney has lost thousands in billable hours they forgot to log. caseclaw is the command center that sits in your terminal and guards against all three—silently, ruthlessly, around the clock.

Point it at a matter and it auto-calculates every filing deadline from 600+ court rule sets. Throw a new client name at it and it checks conflicts against your entire case history in under a second. Start typing and it's already timing your work in six-minute increments.

No browser tabs. No clunky SaaS dashboards. No $500/seat enterprise contracts. Just one command and the peace of mind that nothing is slipping through.

**Who it's for:** Solo attorneys drowning in deadlines, small-firm litigators juggling 40+ matters, paralegals who hold everything together, and in-house teams that need audit-proof tracking.

**What it replaces:** The spreadsheet you swore you'd update, the calendar reminder that got buried, and the sinking feeling at 11 PM that you forgot to file something.

---

## Pricing

| Feature | Free | Pro ($29/mo) | Firm ($99/mo) |
|---|---|---|---|
| Deadline tracking (manual) | ✅ | ✅ | ✅ |
| Auto-calculated deadlines | 5/month | Unlimited | Unlimited |
| Court rules database | 50 courts | 600+ courts | 600+ courts |
| Conflict checks | Basic (local) | Full (fuzzy + entity) | Full + cross-matter |
| Case law monitoring | — | 10 alerts | Unlimited alerts |
| Time/billing capture | Basic timer | Smart billing codes | Multi-attorney + LEDES export |
| Opposing counsel intel | — | Win/loss lookup | Full analytics |
| Matters | 3 active | Unlimited | Unlimited |
| Team members | 1 | 1 | Up to 25 |
| API access | — | — | ✅ |
| Priority support | — | Email | Dedicated Slack |

> `caseclaw upgrade pro` to unlock. 14-day free trial, no credit card required.

---

## Setup

```bash
caseclaw init                          # Initialize in current directory
caseclaw auth login                    # Authenticate (free account)
caseclaw config set jurisdiction "NY"  # Set default jurisdiction
caseclaw config set court "SDNY"       # Set default court
```

---

## Core Features

### 1. Deadline Tracking ⏰ (The Malpractice Killer)

The #1 reason attorneys get sued is missed deadlines. caseclaw makes it impossible.

**Add deadlines manually:**
- `caseclaw deadline add --matter "Smith v. Jones" --type "Answer" --due 2026-03-15 --court SDNY`
- `caseclaw deadline add --matter "Smith v. Jones" --type "Discovery cutoff" --due 2026-06-01`
- `caseclaw deadline add --matter "Acme Corp" --type "SOL" --trigger-date 2024-02-01 --statute "NY CPLR 214" --years 3`

**Auto-calculate deadlines (Pro):**
- `caseclaw deadline calc --event "complaint-served" --date 2026-02-10 --court SDNY`
  → Auto-generates: Answer due (21 days), Discovery deadline, Pre-trial conference, etc.
- `caseclaw deadline calc --event "appeal-filed" --date 2026-02-18 --court "2d Cir"`

**View and manage:**
- `caseclaw deadline list`                         — All upcoming deadlines
- `caseclaw deadline list --matter "Smith v. Jones"` — Per-matter deadlines
- `caseclaw deadline list --overdue`               — 🚨 What you missed
- `caseclaw deadline list --next 7`                — Next 7 days
- `caseclaw deadline list --next 30 --json`        — Export for calendaring
- `caseclaw deadline done --id DL-0042`            — Mark complete

**Alerts:**
- `caseclaw deadline alerts --email you@firm.com`  — Daily email digest
- `caseclaw deadline alerts --slack #deadlines`    — Slack notifications (Firm)
- `caseclaw deadline alerts --calendar`            — Sync to Google/Outlook

### 2. Court Rules Compliance 📏

Every court has different rules. Wrong font? Wrong margin? Filing rejected, deadline missed, client furious.

- `caseclaw rules show SDNY`                       — Full rule summary
- `caseclaw rules show SDNY --topic "page-limit"`  — Specific rule
- `caseclaw rules show SDNY --topic "font"`
- `caseclaw rules show SDNY --topic "efiling"`
- `caseclaw rules check brief.pdf --court SDNY`    — ✅/❌ compliance check
- `caseclaw rules diff SDNY EDNY`                  — Compare two courts' rules
- `caseclaw rules search "electronic filing" --state NY`

**Supported checks (Pro):**
- Page/word limits
- Font family and size requirements
- Margin requirements
- Line spacing
- Table of authorities format
- Certificate of service requirements
- E-filing format (PDF/A, bookmarks, OCR layer)
- Caption and cover page format

### 3. Conflict Checks 🔍

Miss a conflict and you're looking at disqualification—or worse, a bar complaint.

- `caseclaw conflict check "John Smith" "Acme Corporation"`
- `caseclaw conflict check "Jane Doe" --thorough`            — Fuzzy matching + entity resolution (Pro)
- `caseclaw conflict add --entity "Acme Corp" --matter "2024-001" --role plaintiff`
- `caseclaw conflict add --entity "Bob Builder" --matter "2024-001" --role witness`
- `caseclaw conflict list --matter "2024-001"`
- `caseclaw conflict search "Acme"`                          — Search across all matters
- `caseclaw conflict export --format csv`

**Fuzzy matching (Pro) catches:**
- Name variations: "Bob Smith" ↔ "Robert Smith" ↔ "R. Smith"
- Entity aliases: "Acme Corp" ↔ "Acme Corporation" ↔ "ACME Inc."
- Related parties: parent/subsidiary/affiliate detection

### 4. Case Law Monitoring 📡 (Pro)

Stop getting surprised at oral argument by a case decided last week.

- `caseclaw watch add --query "qualified immunity" --court "Supreme Court"`
- `caseclaw watch add --query "TCPA" --circuit 2`
- `caseclaw watch add --case "2025-CV-1234" --court SDNY`    — Track a specific case
- `caseclaw watch list`
- `caseclaw watch results --last 7`                          — New hits this week
- `caseclaw watch alerts --email you@firm.com --frequency weekly`

### 5. Time & Billing ⏱️

Every 6 minutes you don't capture is money you'll never see.

**Track time:**
- `caseclaw time start --matter "Smith v. Jones" --task "Draft motion"`
- `caseclaw time stop`
- `caseclaw time add --matter "Smith v. Jones" --hours 1.5 --task "Client call" --date 2026-02-18`
- `caseclaw time status`                                     — What's currently running

**Review and export:**
- `caseclaw time log --matter "Smith v. Jones"`              — Full time log
- `caseclaw time log --today`
- `caseclaw time log --week --summary`
- `caseclaw time log --month --billable-only`
- `caseclaw time export --matter "Smith v. Jones" --format csv`
- `caseclaw time export --month 2026-02 --format ledes`      — LEDES 1998B export (Firm)

**Smart billing codes (Pro):**
- `caseclaw time start --matter "Smith v. Jones" --task "research"`
  → Auto-suggests: UTBMS code L120 (Research - Legal Issues)

### 6. Matter Management 📂

- `caseclaw matter new --name "Smith v. Jones" --type litigation --court SDNY --client "Jane Smith"`
- `caseclaw matter list`
- `caseclaw matter list --status active`
- `caseclaw matter show "Smith v. Jones"`                    — Full matter dashboard
- `caseclaw matter close "Smith v. Jones" --reason "settled"`
- `caseclaw matter archive "Smith v. Jones"`

**Matter dashboard shows:**
- Upcoming deadlines
- Total hours billed / unbilled
- Key dates
- Parties and conflict status
- Recent activity

### 7. Opposing Counsel Intel 🕵️ (Pro)

Know who you're up against before you walk into the courtroom.

- `caseclaw opp lookup "Jane Attorney" --jurisdiction NY`
- `caseclaw opp firm "Dewey & Associates"`
- `caseclaw opp history "Jane Attorney" --court SDNY`        — Past cases
- `caseclaw opp stats "Jane Attorney"`                       — Win/loss, avg settlement (Firm)

---

## Common Workflows

**New Matter Intake**
```bash
# 1. Run conflict check
caseclaw conflict check "New Client LLC" "Opposing Party Inc"

# 2. Create matter
caseclaw matter new --name "NewClient v. Opposing" --type litigation --court SDNY

# 3. Auto-generate deadlines
caseclaw deadline calc --event "complaint-filed" --date 2026-02-18 --court SDNY

# 4. Start the clock
caseclaw time start --matter "NewClient v. Opposing" --task "Client intake"
```

**Morning Dashboard**
```bash
# What's due this week?
caseclaw deadline list --next 7

# Any new case law?
caseclaw watch results --last 1

# Unbilled time?
caseclaw time log --week --unbilled
```

**Pre-Filing Checklist**
```bash
# Check court rules
caseclaw rules show SDNY --topic "page-limit"
caseclaw rules show SDNY --topic "efiling"

# Validate your brief
caseclaw rules check motion.pdf --court SDNY

# Log the filing time
caseclaw time add --matter "Smith v. Jones" --hours 0.5 --task "E-file motion"

# Mark deadline complete
caseclaw deadline done --id DL-0042
```

**End of Month Billing**
```bash
# Review all time entries
caseclaw time log --month 2026-02 --summary

# Export for billing system
caseclaw time export --month 2026-02 --format ledes > february_billing.txt

# Check for unbilled matters
caseclaw time log --month 2026-02 --unbilled --by-matter
```

---

## Notes

- All data stored locally by default in `~/.caseclaw/` — nothing leaves your machine on Free tier
- Pro/Firm features use encrypted API calls; data is never stored on our servers beyond processing
- Deadline calculations based on FRCP, state civil procedure rules, and local court rules
- Court rules database updated weekly (Pro/Firm)
- Combine with `lawclaw` skill for document analysis alongside case management
- Combine with `gog` skill for Google Calendar deadline sync and Gmail integration

## Security & Compliance

- SOC 2 Type II compliant infrastructure (Pro/Firm)
- AES-256 encryption at rest, TLS 1.3 in transit
- No client data used for model training—ever
- Bar-association compliant data handling (ABA Model Rule 1.6)
- Full audit log: `caseclaw audit log --matter "Smith v. Jones"`
- Data export/delete: `caseclaw data export` / `caseclaw data delete --confirm`

## Support

- Free: Community GitHub Issues
- Pro: Email support (24h response)
- Firm: Dedicated Slack channel + onboarding call
- `caseclaw help <command>` for built-in docs
- `caseclaw feedback "your message"` to reach the team
