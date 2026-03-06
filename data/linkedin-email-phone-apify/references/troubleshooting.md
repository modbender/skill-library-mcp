# Troubleshooting

## Missing token
Error:
- `Apify token missing. Pass --apify-token or set APIFY_TOKEN.`

Fix:
- export `APIFY_TOKEN`
- or pass `--apify-token`

## Both branches disabled
Error:
- `At least one branch must be enabled: includeEmails or includePhones.`

Fix:
- set either `includeEmails=true` or `includePhones=true`

## Empty results
Possible reasons:
- URLs are not in actor data coverage
- strict flags `onlyWithEmails=true` / `onlyWithPhones=true`

Fix:
- retry with a broader URL set
- temporarily set `onlyWithEmails=false` or `onlyWithPhones=false`
