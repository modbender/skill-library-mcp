# Error Handling

## Status Codes

| Status | Meaning | What to Do |
|--------|---------|------------|
| 400 | Bad request / missing fields | Fix your request |
| 401 | Invalid API key | Check your key, do not retry |
| 403 | Denied by spending rules | Do not retry with same params |
| 429 | Rate limited | Wait and retry |
| 5xx | Server error | Retry with backoff |

## Key Details

- USDC address on Base: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- Network: Base mainnet (`eip155:8453`)
- USDC amounts use 6 decimals: `1000000` = $1.00
- Card amounts use cents: `100` = $1.00
- Poll `/authorize/status` every 3 seconds max
- `/settle` is idempotent — safe to call multiple times
