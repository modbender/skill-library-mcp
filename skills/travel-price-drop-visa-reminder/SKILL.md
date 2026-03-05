---
name: travel-price-drop-visa-reminder
description: Plan travel price monitoring and visa or document reminders with safe, read-only guidance. Use when a user wants price drop alerts, travel checklists, or visa timelines without booking or payment actions.
---

# Travel Price Drop and Visa Reminder

## Goal
Create a travel monitoring plan with price thresholds and visa or document reminders.

## Best fit
- Use when the user wants flight or hotel price tracking.
- Use when the user needs visa, passport, or document timelines.
- Use when the user wants a clear reminder schedule.

## Not fit
- Avoid when the user asks to book or pay.
- Avoid when the user wants scraped data from restricted sites.
- Avoid when legal or visa advice is requested.

## Quick orientation
- `references/overview.md` for workflow and quality bar.
- `references/auth.md` for access and token handling.
- `references/endpoints.md` for optional integrations and templates.
- `references/webhooks.md` for async event handling.
- `references/ux.md` for intake questions and output formats.
- `references/troubleshooting.md` for common issues.
- `references/safety.md` for safety and privacy guardrails.

## Required inputs
- Origin, destination, and date range with flexibility.
- Budget or target price thresholds.
- Traveler nationality and passport expiry date.
- Reminder preferences and timezone.

## Expected output
- Price watch plan with thresholds and alert cadence.
- Visa or document checklist with due dates.
- Draft reminder messages.
- Summary of assumptions and data sources.

## Operational notes
- Use only official or user-provided data sources.
- Flag that price data can be delayed or incomplete.
- Do not provide legal advice; cite official sources only.

## Security notes
- Do not request payment details or account credentials.
- Avoid sharing personal travel documents.

## Safe mode
- Monitor and draft reminders only.
- No booking or payment actions.

## Sensitive ops
- Booking, paying, or handling visas directly is out of scope.
