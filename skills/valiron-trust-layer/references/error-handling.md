# Error Handling

## Classes

- `NETWORK_ERROR`: transient network path issue
- `TIMEOUT_ERROR`: trust lookup exceeded timeout
- `API_ERROR`: non-2xx from trust API
- `INVALID_COUNTERPARTY_ID`: identity missing or malformed

## Runtime behavior

- Retry at most once for transient errors.
- Do not loop retries on hot payment path.
- Apply configured fallback mode immediately on unresolved errors.
- Return concise operator-safe messages to caller.
