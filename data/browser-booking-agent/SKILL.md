---
name: browser-booking-agent
description: Execute booking/search flows via browser automation with verification artifacts. Use for reservation forms, availability checks, and capture of proof (screenshots/confirmation IDs).
---

# Browser Booking Agent

## Workflow
1. Confirm task scope and required fields.
2. Navigate and complete booking/search flow.
3. Capture verification: screenshot + confirmation ID/details.
4. Return concise status: completed / blocked / needs user input.

## Guardrails
- Never submit payment without explicit user approval.
- If blocked by captcha/login/2FA, stop and request user action.
- Preserve evidence of critical steps.

## References
- Read `references/verification-checklist.md`.
