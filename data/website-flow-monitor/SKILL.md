---
name: website-flow-monitor
description: Analyze a website URL, discover business-critical user flows to monitor, propose a monitoring plan, and after explicit user confirmation schedule cron health checks. Use when a user asks to monitor a website, check uptime/checkout/onboarding flows, design synthetic checks, or automate recurring website flow checks.
---

# Website Flow Monitor

Take a user-provided website URL and build a practical monitoring plan.

## Workflow

1. Normalize input URL (ensure `https://`).
2. Discover likely flows by scanning:
   - homepage
   - pricing
   - docs/api
   - blog/changelog
   - downloads/signup/login/dashboard if present
   - robots/sitemaps
3. Categorize checks by impact:
   - **Revenue**: pricing, checkout, billing links, purchase CTAs
   - **Onboarding**: signup/login/download/get-started flows
   - **Product/API**: docs and API endpoints (including expected auth failures like 401)
   - **Trust**: privacy, terms, contact/support
   - **SEO/Discovery**: robots.txt and sitemaps
   - **Content**: blog posts, changelog entries
4. Return a proposed monitoring set with:
   - URL
   - expected behavior (200, redirect, 401/403, etc.)
   - impact category
5. Ask for confirmation before scheduling cron.
6. After confirmation, create/update a cron job with:
   - `sessionTarget: isolated`
   - concise agentTurn task that checks all agreed flows
   - delivery mode announce

## Rules

- Do not schedule cron until user confirms the proposed flow list and frequency.
- Prefer actionable summaries: failures first, then healthy checks.
- Flag as **ALERT** for 4xx/5xx (except expected 401/403 on auth-required API checks), redirect loops, or missing critical links.
- If the user requests changes (skip/add endpoint), update the existing cron job instead of creating duplicates.

## Discovery helper

Use this script for quick link discovery:

```bash
python3 {baseDir}/scripts/discover_flows.py --url https://example.com
```

It returns JSON with discovered internal/external links and suggested flow candidates.

## Cron prompt template (adapt per site)

Use this shape in `payload.message`:

- mention this is a recurring reminder
- list exact URLs and expected behavior
- require output format: `OK / WARN / ALERT`
- require impact tags: revenue/onboarding/product/trust/seo/support
- include "if all healthy, short OK summary" instruction

Keep it short and deterministic.
