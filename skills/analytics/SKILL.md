---
name: Analytics
description: Deploy privacy-first analytics with correct API patterns, rate limits, and GDPR compliance.
---

## Critical Implementation Gotchas

**Umami API timestamps**: Use milliseconds, not seconds. `Date.now()` in JS, `int(time.time() * 1000)` in Python.

**Plausible API v2**: Requires `site_id` parameter, NOT domain name. Get site_id from dashboard URL first.

**PostHog events**: Properties must be JSON serializable. Never pass DOM elements or functions.

**Rate limits**: Umami 600/hour, Plausible 600/hour, PostHog 1000/minute. Implement exponential backoff on 429.

## Environment-Specific Setup

**Development**: ALWAYS use separate project/site for local testing. Production data pollution is irreversible.

**Tracking domains**: Never hardcode. Use env vars to switch between localhost and production.

**Bot filtering**: Enable in settings. Privacy tools have weaker bot detection than Google Analytics.

## GDPR Compliance Gotchas

**EU visitors need explicit consent** even for privacy-first tools. Check IP geolocation before tracking.

**Data retention**: Set automatic deletion - Umami in Settings > Data, Plausible 30 days max, PostHog in project settings.

**Cookie-free warning**: Umami/Plausible don't use cookies but still need consent for EU visitors if collecting identifiers.

## Runtime Safety

**Verify script loads** before sending events. Check for `umami`, `plausible`, or `posthog` globals first.

**Never track PII** (email, names, IP) in custom events. Violates privacy principles.

**Batch PostHog events** via `/batch` endpoint. Umami/Plausible require individual requests.

## Authentication Patterns

**Store API keys in environment variables** only. Never hardcode.

**Umami**: Requires website ID + API key combination.

**Plausible**: Uses Bearer token authentication.

**PostHog**: Uses project-specific API key.
