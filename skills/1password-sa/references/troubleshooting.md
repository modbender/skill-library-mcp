# 1Password CLI troubleshooting

## "not signed in"

- Ensure `OP_SERVICE_ACCOUNT_TOKEN` is set in the current shell/runtime.

> **Note:** Diagnostic commands below output metadata (account emails, vault names, IDs). Treat output as sensitive in logged/recorded sessions.
- Verify with:

```bash
op whoami --format json
```

## "account not authorized"

- Confirm service account has access to the target vault/item.
- Check vault permissions in 1Password admin.
- Validate reference path (`op://vault/item/field`) is correct.

## "consent required"

- Open the URL shown by `op` and complete consent/approval.
- Re-run the command after consent.

## Token expired / revoked

- Generate a new service-account token in 1Password admin.
- Update secure storage/runtime secret source.
- Retry and verify:

```bash
op whoami --format json
```

## Rate limits / throttling

- Use exponential backoff (e.g., 1s, 2s, 4s, 8s with jitter).
- Reduce concurrent `op` calls.
- Cache non-sensitive metadata where possible.

## Network errors / timeouts

- Retry with bounded attempts and delay.
- Confirm internet/proxy/VPN/DNS are healthy.
- Re-test with a low-impact command:

```bash
op vault list --format json
```
