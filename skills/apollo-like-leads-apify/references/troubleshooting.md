# Troubleshooting

## Missing token
Error:
- `Apify token missing. Pass --apify-token or set APIFY_TOKEN.`

Fix:
- export `APIFY_TOKEN` and retry
- or pass `--apify-token`

## Actor HTTP 4xx/5xx
Possible reasons:
- invalid payload shape
- unsupported filter values
- actor-side temporary issue

Fixes:
- test with a small payload (`max_results: 50`)
- remove optional filters and re-add incrementally
- verify actor is available in Apify console

## Empty rows
Possible reasons:
- too strict filters
- niche target with low coverage

Fixes:
- widen country/region filters
- broaden titles/seniority
- test without `email_status` filter first
