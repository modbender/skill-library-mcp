# 2bulu notes (public scraping)

## Useful pages
- Track search/list: https://www.2bulu.com/track/track_search.htm
- Keyword search results: https://www.2bulu.com/track/search-<urlencoded>.htm

## What is safe to do
- Scrape public list/search results: titles + URLs.
- Treat as discovery links; store minimal metadata.

## Manual login (allowed with user involvement)
- Manual login is allowed: user completes WeChat/QQ login and any captcha in the browser.
- Automation may continue **only in the same persisted browser profile**.

## What to avoid
- Do not bypass login/captcha.
- Track-detail downloads may redirect to login; prefer user-exported GPX/KML sent via Telegram when possible.

## Data quality
- List page may contain duplicate links with query params (e.g. ?tabType=2). Normalize and de-duplicate.
