---
name: community-mod-pack
description: Assist community moderation with summaries, spam detection suggestions, and draft replies for Discord or Telegram. Use when a user wants moderation help, rule reminders, or daily summaries without automatic enforcement actions.
---

# Community Mod Pack

## Goal
Summarize community activity and surface moderation signals with draft responses only.

## Best fit
- Use when the user needs daily or weekly channel summaries.
- Use when the user wants spam or rule-violation signals.
- Use when the user wants draft moderator replies or rule reminders.

## Not fit
- Avoid when the user asks to auto-ban, kick, or delete messages.
- Avoid when the community rules are missing or unclear.
- Avoid when privacy constraints prohibit analysis.

## Quick orientation
- `references/overview.md` for workflow and quality bar.
- `references/auth.md` for access and token handling.
- `references/endpoints.md` for optional integrations and templates.
- `references/webhooks.md` for async event handling.
- `references/ux.md` for intake questions and output formats.
- `references/troubleshooting.md` for common issues.
- `references/safety.md` for safety and privacy guardrails.

## Required inputs
- Channel logs or message exports within the allowed window.
- Community rules and enforcement preferences.
- Languages to moderate.
- Escalation contacts and severity thresholds.

## Expected output
- Activity summary with key topics and notable threads.
- Flagged messages with reasons and confidence.
- Draft responses or rule reminders.
- Suggested follow-up actions for human moderators.

## Operational notes
- Provide confidence and cite the rule that was triggered.
- Avoid making final enforcement decisions.
- Keep outputs in draft form.

## Security notes
- Respect privacy and minimize data retention.
- Avoid sharing personal data beyond the moderator context.

## Safe mode
- Analyze and draft only; no enforcement actions.
- Use read-only access to logs when possible.

## Sensitive ops
- Muting, banning, deleting messages, or modifying roles is out of scope.
