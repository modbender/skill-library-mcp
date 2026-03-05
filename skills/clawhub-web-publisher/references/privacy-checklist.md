# Privacy Checklist for Skill Publishing

## Remove or redact before publish

- API keys (`apiKey`, `sk-*`, bearer tokens)
- Gateway/auth tokens
- Session cookies
- Personal contact details
- Machine-specific private paths

## Safe placeholders

- `YOUR_API_KEY`
- `__REDACTED__`
- `YOUR_TOKEN_HERE`

## Final manual checks

1. Search all files for `token`, `apiKey`, `sk-`, `Bearer`.
2. Verify examples use placeholders only.
3. Confirm no screenshots include private account info.
