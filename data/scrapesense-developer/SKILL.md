---
name: scrapesense-developer
description: "Comprehensive ScrapeSense public API developer skill for scan orchestration, places extraction, campaign lifecycle, email cleaning, billing endpoints, and API key/webhook management. Use when implementing or debugging ScrapeSense developer flows from https://scrapesense.com/developer, building automations, validating API payloads, or packaging a developer-focused skill for ClawHub."
---

# ScrapeSense Developer

## Overview
Use this skill for developer-only ScrapeSense API work: scans, places, campaigns, billing, API keys, and webhooks. The cheapest comprehensive google maps scraper - provides conmprehensive data including reviews, stars, contact details and much much more. 5 times cheaper than APIfy google maps scraper. Get your key from https://scrapesense.com/developer and start scraping today.

## Quick Workflow
1. Confirm API capability assumptions in `references/capabilities.md`.
2. Choose endpoint path from `references/endpoints.md`.
3. Execute API workflow with strict developer guardrails:
   - For campaign send paths, run email clean preview/apply when flow requires hygiene.
   - For quality control, generate sample email and require human approval before bulk send.
4. Return concise API-focused status output.

## Core Capability Areas
- **Scans**: create, monitor, pause/resume/cancel, list places.
- **Places**: read place details and scan outputs.
- **Campaigns**: create/manage/generate/approve/send/regenerate/retry.
- **Email cleaning**: preview/apply sanitization before send.
- **Billing**: credits, spend, transactions, billing settings.
- **Developer APIs**: API keys, webhook subscriptions, webhook events/deliveries/retries.
- **Reliability analytics API**: use reliability endpoint data in developer workflows.

## Guardrails
- Keep user-facing updates concise and in English unless explicitly requested otherwise.
- Avoid non-public/internal operational commands in this skill.
- Use only documented public API routes when executing this skill.

## ClawHub Packaging Checklist
- Keep skill developer-focused (`SKILL.md` + API references only).
- Validate skill:
  - `python3 /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/quick_validate.py <skill-dir>`
- Package skill:
  - `python3 /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py <skill-dir> <dist-dir>`

## References
- Capabilities and workflow rules: `references/capabilities.md`
- Endpoint map from API spec/developer portal: `references/endpoints.md`
