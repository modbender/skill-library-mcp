---
name: Banking
slug: banking
version: 1.0.0
homepage: https://clawic.com/skills/banking
description: Manage retail and business banking workflows with payment operations, account controls, reconciliation, fraud response, and compliant communication.
changelog: Initial release with structured banking workflows for intake, operations, incident response, and customer-safe messaging.
metadata: {"clawdbot":{"emoji":"B","requires":{"bins":[],"config":["~/banking/"]},"os":["darwin","linux","win32"],"configPaths":["~/banking/"]}}
---

## Setup

On first use, read `setup.md` for activation boundaries and context capture priorities.

## When to Use

Use this skill for banking operations support: account onboarding workflows, payment operations, reconciliation triage, fraud incidents, and customer communication that must stay clear and compliant.

## Architecture

Memory lives in `~/banking/`. See `memory-template.md` for structure and status fields.

```text
~/banking/
|-- memory.md                 # Status, activation scope, operating context
|-- incidents.md              # Open fraud and operations incidents
|-- payment-controls.md       # Verified controls by rail and account type
`-- communication-notes.md    # Approved customer messaging patterns
```

## Quick Reference

Use the smallest relevant file for the task to keep decisions precise under time pressure.

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Request intake and classification | `intake-checklist.md` |
| Payment rails and controls | `payment-ops.md` |
| Fraud and outage handling | `incident-response.md` |
| Customer-safe wording | `customer-messaging.md` |
| Regulatory and legal boundaries | `compliance-scope.md` |

## Core Rules

### 1. Classify the Request Before Giving Steps
- Label each request first: onboarding, payment execution, reconciliation, fraud, dispute, or compliance question.
- If the category is unclear, ask one short clarification before proposing actions.

### 2. Confirm Jurisdiction and Account Context
- Capture country or region, customer type (consumer or business), and account type before compliance-sensitive guidance.
- Never give jurisdiction-specific legal conclusions without explicit location context.

### 3. Use Control-First Payment Guidance
- For every transfer path, verify account ownership, amount, cutoff timing, approval threshold, and rollback options.
- If any required control is unknown, pause execution advice and request the missing control.

### 4. Treat Incidents as Containment Then Recovery
- For suspected fraud or unauthorized activity, prioritize containment actions before root-cause analysis.
- Keep incident actions timestamped and reversible where possible.

### 5. Keep Communication Clear, Neutral, and Accurate
- Use plain language that states current status, next step, owner, and ETA window.
- Avoid guarantees, blame language, or speculative claims about pending investigations.

### 6. Keep Memory Actionable and Verifiable
- Record only durable context: operating boundaries, approved controls, known constraints, and recurring failure patterns.
- Do not store full account numbers, authentication data, or sensitive personal identifiers in memory notes.

### 7. Escalate High-Risk or Restricted Requests
- Escalate when requests involve sanctions, KYC circumvention, legal interpretation, or irreversible fund movement without controls.
- Refuse instructions that circumvent required approvals, customer consent, or regulatory safeguards.

## Common Traps

- Starting with product explanations instead of request classification -> slower resolution and wrong workflow.
- Giving transfer steps before confirming controls -> elevated operational and fraud risk.
- Mixing legal interpretation with operations guidance -> compliance exposure and user confusion.
- Responding to incidents with generic advice only -> delayed containment and larger losses.
- Using absolute language such as "guaranteed" or "always" -> credibility and regulatory risk.
- Logging sensitive data in memory notes -> avoidable privacy and security exposure.

## Data Storage

- Local notes only in `~/banking/` (memory file, incident notes, and control references).
- Keep stored content minimal and operational: controls, status, and decisions.
- Do not store full account numbers, authentication data, or unnecessary personal identifiers.

## Security & Privacy

Data that leaves your machine:
- None by default. This skill is instruction and workflow guidance only.

Data that stays local:
- Operational context and notes in `~/banking/`.

This skill does NOT:
- Access bank portals or execute fund transfers automatically.
- Request undeclared network calls.
- Store authentication data or full account numbers in memory files.
- Modify files outside `~/banking/` for storage.
- NEVER modifies its own skill definition file.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `payments` - Payment workflows and transaction operations patterns.
- `accounting` - Ledger, reconciliation, and financial reporting support.
- `invoice` - Invoice lifecycle workflows and settlement tracking.
- `money` - Personal money management and budgeting fundamentals.
- `invest` - Investment analysis workflows for portfolio decisions.

## Feedback

- If useful: `clawhub star banking`
- Stay updated: `clawhub sync`
