# RULES

Security and behavior policy for `bn-square-skill`.

## Domain Safety

1. Only send Binance auth material to `*.binance.com`.
2. Never send cookie/session/csrf tokens to third-party domains.
3. Do not forward auth headers in debugging or webhook calls.

## Session Safety

1. Always run `validate_session` before publish flows.
2. If session is invalid, stop and ask for refreshed credentials.
3. Never auto-invent fallback credentials.

## Content Safety

1. Respect Binance content policy and local regulations.
2. Do not publish spam, scams, impersonation, or malicious links.
3. Keep posts factual when handling financial content.

## Execution Safety

1. Use bounded retries for transient errors only.
2. Stop immediately on `401/403` auth failures.
3. On `429`, back off before retry.

## Data Handling

1. Never print raw secrets in logs.
2. Return only sanitized errors.
3. Keep outputs structured and machine-parseable.
