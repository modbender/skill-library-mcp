---
name: Umami
description: Deploy Umami analytics avoiding data loss, tracking failures, and integration issues.
metadata: {"clawdbot":{"emoji":"📊","os":["linux","darwin","win32"]}}
---

## Critical Configuration
- `HASH_SALT` must never change — changing it invalidates all existing data, essentially a reset
- SQLite is not supported — despite being Node.js, Umami requires PostgreSQL or MySQL
- Database contains everything — all tracking data, config, users; backup only this

## Tracking Script Traps
- `data-website-id` must match Umami config exactly — wrong ID = zero data, no error shown
- Script blocked by ad blockers — self-host on same domain as site to avoid blocking
- Single Page Apps don't auto-track navigation — must call `umami.track()` on route changes
- Script in `<head>` not `<body>` — late loading misses initial pageview

## SPA Integration
- React: call `umami.track('pageview')` in router effect or navigation handler
- Next.js: use `@umami/next` package — handles app router and pages router
- Vue/Nuxt: router afterEach hook with `umami.track()`
- Check `window.umami` exists before calling — script may load after component mounts

## Custom Events
- Event names appear verbatim in dashboard — use consistent naming scheme
- Properties only searchable via API — not visible in default dashboard
- `umami.track('event', { key: 'value' })` for properties

## Self-Hosting Considerations
- Low resources needed — 256MB RAM handles most sites
- PostgreSQL needs more resources than Umami itself — plan accordingly
- Reverse proxy required for HTTPS — Umami runs HTTP on port 3000
- Backup strategy = database backup — no filesystem state to worry about

## Multi-Site Setup
- One Umami instance handles many sites — add in Dashboard > Settings > Websites
- Each site needs unique tracking script — get from Websites settings
- Share button available per site — generates public dashboard URL

## Troubleshooting
- Zero pageviews — check browser Network tab, verify script loads without error
- Script 404 — verify CORS headers if cross-domain, or self-host on same domain
- Events not appearing — check browser console for `umami` errors
- Dashboard slow — check database performance, PostgreSQL query times

## Common Mistakes
- Using same website ID for dev and prod — pollutes analytics with test data
- Not testing script after deploy — CDN caching or minification can break it
- Expecting real-time updates — dashboard has slight delay, not instant
