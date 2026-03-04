# Anti-bot handling (permissioned)

This is about *reliability for legitimate automation* (your own sites, explicit permission, approved internal tooling).

## Escalation ladder
1) **Fetcher/FetcherSession** (fast HTTP)
   - Add delays / retry logic
   - Use session cookies where applicable

2) **DynamicSession** (JS-rendered)
   - Use `network_idle=True` or appropriate waits
   - Consider loading fewer resources if supported

3) **StealthySession** (protected pages)
   - Use when you see:
     - 403/429 patterns
     - Cloudflare/Turnstile interstitial pages
     - "verify you are human" flows

## Practical tips
- Lower concurrency, add jittered sleeps.
- Persist sessions/cookies across requests.
- Rotate proxies **only if** you have the right to access and you’re being rate-limited, not to evade restrictions.
- Always capture the HTML/screenshot of the block page for debugging.

## Minimal StealthySession example
```python
from scrapling.fetchers import StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch("https://example.com", google_search=False)
    title = page.css("title::text").get()
    print(title)
```

## What not to do
- Do not bypass paywalls or private/login-only content without authorization.
- Do not attempt to scrape sensitive personal data.
