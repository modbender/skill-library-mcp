# Weave CLI Contract Snapshot

This reference captures the current command/output contract for the `weave` CLI as of 2026-02-26.

Source precedence used here:

1. CLI implementation (`apps/cli/internal/cmd/*`, `apps/cli/internal/output/output.go`)
2. CLI docs (`apps/cli/docs/*`)

## Global Flags

- `--api-url string` (default `https://www.weavecash.com`)
- `--human` (default `false`; machine-oriented JSON is default)

## Commands

### `weave create`

Required flags:

- `--receive-token`
- `--amount`
- `--wallet-address`

Conditionally required:

- `--receive-network` for tokens with multiple supported networks

Optional:

- `--description`
- `--buyer-name`
- `--buyer-email`
- `--buyer-address`

JSON output shape:

```json
{
  "id": "inv_123",
  "invoiceUrl": "https://www.weavecash.com/invoice/inv_123"
}
```

### `weave quote [invoice-id]`

Required flags:

- `--pay-token`
- `--pay-network`
- `--refund-address`

JSON output fields:

- `depositAddress`
- `depositMemo` (optional)
- `amountIn`
- `amountOut`
- `timeEstimate`
- `expiresAt`

### `weave status [invoice-id]` (alias: `get`)

Default: one-shot invoice snapshot.

Watch mode flags:

- `--watch`
- `--interval-seconds` (default `5`)
- `--timeout-seconds` (default `900`)

Watch mode emits NDJSON events in JSON mode and exits:

- `0` on terminal status
- `2` on timeout

### `weave tokens`

Returns runtime token/network support and aliases.

This command is the runtime source of truth for token/network decisions in skill workflows.

## Exit Codes

- `0`: success (including terminal completion in watch mode)
- `1`: validation, API, network, or command failure
- `2`: watch timeout before terminal status

## Error Output

Error payloads are emitted as JSON on stderr.

API-derived failures include HTTP status and API payload when parseable:

```json
{
  "error": "api message",
  "status": 409,
  "details": {
    "error": "Invoice is not in PENDING status"
  }
}
```

Watch timeout shape:

```json
{
  "error": "status watch timed out",
  "status": "AWAITING_DEPOSIT",
  "timeoutSeconds": 900
}
```

## Runtime Token-Map Caveat

Current source token map (`apps/cli/internal/cmd/tokens_generated.go`) includes:

- Tokens: `BTC`, `ETH`, `PAXG`, `SOL`, `USDC`, `USDT`, `XAUT`, `ZEC`
- Networks: `Bitcoin`, `Ethereum`, `Solana`, `Tron`, `Zcash`

Some built artifacts can lag this map. Skill logic must query `weave tokens` from the installed runtime before making token/network assumptions.
