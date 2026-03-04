---
name: receipt-subscription-cleaner
description: Identify recurring charges and subscriptions from receipts or email exports, and produce a clean summary with renewal dates, price changes, and cancellation drafts. Use when a user wants to audit spending without initiating payments or cancellations.
---

# Receipt and Subscription Cleaner

## Goal
Extract and normalize receipts to detect subscriptions, renewal cycles, and potential savings opportunities.

## Best fit
- Use when the user provides email exports, receipts, or billing PDFs.
- Use when the user wants a recurring charge audit and renewal calendar.
- Use when the user wants draft cancellation emails or scripts.

## Not fit
- Avoid when the user asks to cancel, refund, or dispute charges automatically.
- Avoid when the user requests access to payment methods or bank logins.
- Avoid when receipts are not available and the user cannot export data.

## Quick orientation
- `references/overview.md` for workflow and quality bar.
- `references/auth.md` for access and token handling.
- `references/endpoints.md` for optional integrations and templates.
- `references/webhooks.md` for async event handling.
- `references/ux.md` for intake questions and output formats.
- `references/troubleshooting.md` for common issues.
- `references/safety.md` for safety and privacy guardrails.

## Required inputs
- Receipt sources (email export, PDF folder, or CSV list).
- Time window and base currency.
- Known subscriptions or vendors to prioritize.
- User preferences for reminders (frequency, timezone).

## Expected output
- Subscription table with vendor, amount, cycle, and next renewal estimate.
- Anomaly list (price changes, overlapping subscriptions).
- Draft cancellation email templates (not sent).
- Reminder schedule recommendations.

## Operational notes
- Normalize vendor names before clustering.
- Mark confidence levels for each detected subscription.
- Keep all actions read-only; produce drafts only.

## Security notes
- Do not store raw receipts outside the user workspace.
- Redact card numbers and addresses in outputs.

## Safe mode
- Analyze and summarize receipts only.
- Generate draft reminders and cancellation messages without sending.

## Sensitive ops
- Canceling subscriptions, disputing charges, or initiating payments is out of scope.
