# Scrapling quick reference (practical)

## Fetchers

- `scrapling.fetchers.Fetcher`
  - Best first try (fast HTTP fetch)
  - Common use: `Fetcher.get(url, timeout=...)`

- `scrapling.fetchers.StealthyFetcher`
  - Browser-backed stealth mode for anti-bot friction
  - Common use: `StealthyFetcher.fetch(url, headless=True, network_idle=True, timeout=...)`

- `scrapling.fetchers.DynamicFetcher`
  - Playwright-backed browser automation for JS-heavy sites
  - Common use: `DynamicFetcher.fetch(url, headless=True, network_idle=True, timeout=...)`
  - Requires: `pip install playwright` + `playwright install chromium`

## Response object (common fields)

Scrapling responses are not `requests.Response`.
Common useful attributes/methods:

- `response.status` (int)
- `response.url` (str)
- `response.html_content` (str) — decoded HTML (preferred)
- `response.body` (bytes) — raw bytes
- `response.css(selector)` / `response.xpath(expr)` — selection API

## Next.js extraction

Many Next.js sites embed JSON at:

- `<script id="__NEXT_DATA__" type="application/json"> ... </script>`

Parse that JSON and read `props.pageProps...`.

## Practical escalation ladder

1) `Fetcher`
2) `StealthyFetcher`
3) `DynamicFetcher`
