---
name: expense-claims-ops
description: Process personal/work expenses and reimbursement claims in a structured, low-friction workflow. Use when collecting receipts, categorizing spend, preparing claim-ready summaries, checking missing fields, generating submission checklists, and drafting claim notes/follow-ups.
---

# Expense & Claims Ops

## Workflow
1. Collect inputs: receipt set, date range, currency, policy constraints (if any), and claim destination (company tool/email/manual).
2. Extract line items: date, merchant, amount, currency, category, payment method, receipt proof status.
3. Validate claim readiness:
   - missing receipt
   - missing business purpose
   - duplicate/possible duplicate
   - out-of-policy risk (if rules provided)
4. Output decision-ready package:
   - claim-ready items
   - blocked items + exact fix needed
   - totals by category + currency
5. Generate submission artifacts:
   - claim summary block
   - per-item notes
   - follow-up draft for exceptions/approvals

## Output Standard
- Keep concise and actionable.
- Use max 3 sections: Ready, Blocked, Next action.
- Always include totals and missing-doc count.
- If policy unknown, mark checks as "policy not provided".

## References
- For item schema and status labels, read `references/expense-schema.md`.
- For copy-paste claim templates, read `references/claim-templates.md`.
- For weekly processing cadence, read `references/ops-cadence.md`.
