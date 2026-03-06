---
name: smart-home-energy-saver
description: Analyze home energy usage and propose safe, read-only automation plans for savings. Use when a user wants Home Assistant energy insights, optimization ideas, or draft automation YAML without directly controlling devices.
---

# Smart Home Energy Saver

## Goal
Provide energy-saving recommendations and draft automations without changing device states.

## Best fit
- Use when the user has Home Assistant energy and device data.
- Use when the user wants schedule recommendations and savings estimates.
- Use when the user wants draft automation YAML for review.

## Not fit
- Avoid when the user asks to apply automations automatically.
- Avoid when critical systems are involved without safety review.
- Avoid when data sources are missing or unreliable.

## Quick orientation
- `references/overview.md` for workflow and quality bar.
- `references/auth.md` for access and token handling.
- `references/endpoints.md` for optional integrations and templates.
- `references/webhooks.md` for async event handling.
- `references/ux.md` for intake questions and output formats.
- `references/troubleshooting.md` for common issues.
- `references/safety.md` for safety and privacy guardrails.

## Required inputs
- Home Assistant instance info and read-only token (if used).
- List of controllable devices and comfort constraints.
- Energy tariff schedule and target savings goals.
- Preferred operating hours and exceptions.

## Expected output
- Energy usage summary and top savings opportunities.
- Draft automation YAML snippets with explanations.
- Estimated impact ranges and assumptions.
- Manual checklist for safe rollout.

## Operational notes
- Only propose automations; never apply changes.
- Respect comfort and safety constraints.
- Flag any automation that could affect safety or accessibility.

## Security notes
- Keep tokens in environment variables if provided.
- Avoid exposing home addresses or device identifiers in outputs.

## Safe mode
- Read-only analysis and draft automation files only.
- No live device control or configuration updates.

## Sensitive ops
- Applying automations or controlling devices is out of scope.
