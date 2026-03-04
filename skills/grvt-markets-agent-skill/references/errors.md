# Error Handling & Troubleshooting

## Exit Codes

| Code | Constant | Meaning |
|------|----------|---------|
| `0` | `EXIT_SUCCESS` | Command completed successfully |
| `2` | `EXIT_USAGE` | Usage or validation error (bad flags, missing required options, invalid values) |
| `3` | `EXIT_AUTH` | Authentication or permission error (expired session, missing/invalid API key or private key, 401/403 from API) |
| `4` | `EXIT_PARTIAL` | Partial failure in batch operations (e.g. `cancel-all` where some cancels failed) |
| `5` | `EXIT_API` | API or network error (server errors, timeouts, rate limits, connection failures) |

## Common Error Scenarios

### Authentication Errors (Exit 3)

**Session expired**
```
Error: HTTP 401: Unauthorized
```
Recovery: Run `grvt auth login` to get a fresh session cookie.

**API key not set**
```
Error: --api-key is required (or set apiKey in config)
```
Recovery: Run `grvt config set apiKey YOUR_KEY` or pass `--api-key` to the command.

**Private key missing (for write operations)**
```
Error: Private key required for order signing. Run `grvt config set privateKey <key>` or `grvt auth login --private-key <key>`.
```
Recovery: Set the private key with `grvt config set privateKey 0xKEY`.

**Invalid API key**
```
Error: Auth failed: invalid api key
```
Recovery: Verify your API key at https://grvt.io and re-set it with `grvt config set apiKey CORRECT_KEY`.

**Wrong environment**
```
Error: Auth failed: ...
```
Recovery: Check the current environment with `grvt config get env` and ensure your API key is valid for that environment. Different environments have separate API keys.

---

### Validation Errors (Exit 2)

**Missing required option**
```
Error: --instrument is required
Error: Either --order-id or --client-order-id is required
Error: --price is required for limit orders
```
Recovery: Add the missing required flag. Check `grvt <command> --help` for required options.

**Invalid instrument name**
```
Error: Instrument not found: BTCUSDT
```
Recovery: Use the correct naming convention (e.g. `BTC_USDT_Perp` not `BTCUSDT`). Discover valid instruments with `grvt market instruments`.

**Invalid sub-account ID**
```
Error: --sub-account-id is required (or set subAccountId in config)
```
Recovery: Set a default with `grvt config set subAccountId YOUR_ID` or pass `--sub-account-id`.

**Invalid time-in-force**
```
Error: Invalid time-in-force: XXX. Use GTT, IOC, AON, or FOK.
```
Recovery: Use one of the valid values: `GTT`, `IOC`, `AON`, `FOK` (or their full forms).

**Invalid Ethereum address**
```
Error: --to-address must be a valid Ethereum address (0x...)
```
Recovery: Provide a valid 42-character address starting with `0x`.

**Invalid countdown value**
```
Error: --countdown must be 0 (disable) or between 1000 and 300000 ms
```
Recovery: Use `0` to disable, or a value between `1000` and `300000`.

---

### API / Network Errors (Exit 5)

**Rate limiting**
```
Error: HTTP 429: Too Many Requests
```
Recovery: The CLI automatically retries with exponential backoff (configurable via `http.backoffMs`, `http.maxBackoffMs`, `http.retries`). If this persists, reduce request frequency or increase `http.maxBackoffMs`.

**Server error**
```
Error: HTTP 500: Internal Server Error
Error: HTTP 503: Service Unavailable
```
Recovery: The CLI automatically retries 5xx errors. If the issue persists, the GRVT API may be experiencing downtime. Wait and retry.

**Timeout**
```
Error: The operation was aborted
```
Recovery: Increase the timeout with `--timeout-ms 30000` or `grvt config set http.timeoutMs 30000`. Timeouts are also retried automatically.

**Connection failure**
```
Error: fetch failed
Error: ECONNREFUSED
```
Recovery: Check your network connectivity and verify the environment is correct (`grvt config get env`). Ensure the GRVT API is reachable.

**Insufficient balance**
```
Error: insufficient balance
```
Recovery: Check balances with `grvt account summary` and `grvt account funding`. Ensure the sub-account has enough funds for the operation.

**Order rejected**
```
Error: order rejected: ...
```
Recovery: Common causes include insufficient margin, invalid price (outside allowed range), or exceeding position limits. Check `grvt market margin-rules --instrument <name>` and `grvt account summary`.

---

### Partial Failures (Exit 4)

**cancel-all partial failure**
```
Error: Some orders could not be canceled
```
Recovery: Re-run `grvt trade order cancel-all` to retry remaining orders. Check `grvt trade order open` to see which orders are still open.

---

## Retry Behavior

The HTTP client automatically retries on:
- HTTP 429 (rate limiting)
- HTTP 5xx (server errors)
- Request timeouts (AbortError)

Retry configuration (via config or global flags):
- `retries`: Number of retry attempts (default: `3`)
- `backoffMs`: Initial backoff delay (default: `200ms`)
- `maxBackoffMs`: Maximum backoff delay (default: `10000ms`)

Backoff formula: `min(backoffMs * 2^attempt, maxBackoffMs)`

Non-retryable errors (4xx except 429) fail immediately.

---

## Debugging Tips

1. **Check auth state**: `grvt auth whoami` (local) or `grvt auth status` (API call)
2. **Verbose output**: Use `--output json --pretty` to see full response details
3. **Dry-run writes**: Always available on write commands to preview the signed payload
4. **Check config**: `grvt config list` to see all settings (secrets redacted)
5. **Raw API response**: Use `--output raw` to see the unprocessed API response
6. **Config file location**: `grvt config path` to find the config file for manual inspection
