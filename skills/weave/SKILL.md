---
name: weave
description: Create crypto invoices and stablecoin invoices (USDC/USDT), generate payment quotes, and monitor invoice payment status with the Weave CLI.
license: AGPL-3.0-or-later
metadata:
  openclaw:
    requires:
      bins:
        - weave
    install:
      - kind: go
        module: github.com/AryanJ-NYC/weave-cash/apps/cli/cmd/weave
        bins:
          - weave
      - id: node
        kind: node
        package: weave-cash-cli
        label: Fallback: Install Weave CLI (npm)
        bins:
          - weave
    emoji: '🧶'
    homepage: 'https://www.weavecash.com'
  clawdbot:
    requires:
      bins:
        - weave
    install:
      - kind: go
        module: github.com/AryanJ-NYC/weave-cash/apps/cli/cmd/weave
        bins:
          - weave
      - id: node
        kind: node
        package: weave-cash-cli
        label: Fallback: Install Weave CLI (npm)
        bins:
          - weave
    emoji: '🧶'
    homepage: 'https://www.weavecash.com'
---

# Weave

Weave is a CLI for crypto invoicing: create USDC invoices, USDT invoices, and cross-token payment quotes, then track settlement status. Use this when you need a crypto invoice generator for agent workflows or operations.

## Overview

Use `weave` for full Weave Cash invoice lifecycle workflows:

1. Create an invoice (`weave create`)
2. Generate payment instructions (`weave quote`)
3. Track settlement (`weave status` or `weave status --watch`)

## Guardrails

- Crypto-to-crypto only. Do not introduce fiat currencies, fiat conversions, or fiat-denominated behavior.
- Prefer machine-readable JSON output. Use `--human` only when explicitly requested.
- Never expose secrets (private keys, tokens, JWTs) in outputs.
- Treat network/API calls as failure-prone and handle non-zero exits explicitly.

## When Not To Use

- Do not use this skill for fiat invoice or fiat settlement workflows.
- Do not use this skill for editing Weave web UI/frontend code.
- Do not use this skill for unrelated wallet custody or private-key management tasks.
- Do not use this skill when the user wants non-Weave payment rails.

## Preflight

1. Confirm CLI availability:

```bash
weave --help
```

2. Discover runtime token/network support before choosing assets:

```bash
weave tokens
```

3. If `weave` is missing, provide compliant install guidance and ask before running:

```bash
go install github.com/AryanJ-NYC/weave-cash/apps/cli/cmd/weave@latest
weave --help
```

If Go is unavailable, use npm fallback:

```bash
npm i -g weave-cash-cli
weave --help
```

If both Go and npm are unavailable, report the missing prerequisites.

## Compliant Install Policy

- Prefer `metadata.openclaw.install` / `metadata.clawdbot.install` package-manager installs.
- Never suggest remote download commands piped directly to a shell interpreter.
- Detect and instruct; do not auto-install dependencies without explicit user approval.

## Token And Network Selection

- Always trust live `weave tokens` output from the runtime binary.
- Do not hardcode token/network lists in reasoning.
- `--receive-network` is required only for receive tokens that support multiple networks.
- Network aliases are accepted (for example `Ethereum|ETH`, `Solana|SOL`, `Tron|TRX` when supported by runtime output).

## Workflow

### 1) Create Invoice

Collect:

- `receive-token`
- `amount` (positive numeric string)
- `wallet-address`
- `receive-network` only when required by runtime token/network map
- optional buyer fields (`description`, `buyer-name`, `buyer-email`, `buyer-address`)

Command:

```bash
weave create \
  --receive-token USDC \
  --receive-network Ethereum \
  --amount 25 \
  --wallet-address 0x1111111111111111111111111111111111111111
```

Expected JSON shape:

```json
{
  "id": "inv_123",
  "invoiceUrl": "https://www.weavecash.com/invoice/inv_123"
}
```

Capture `id` for downstream `quote`/`status` calls.

### 2) Generate Quote

Collect:

- `invoice-id`
- `pay-token`
- `pay-network`
- `refund-address`

Command:

```bash
weave quote inv_123 \
  --pay-token USDT \
  --pay-network Ethereum \
  --refund-address 0x2222222222222222222222222222222222222222
```

Expected fields:

- `depositAddress`
- `depositMemo` (optional)
- `amountIn`
- `amountOut`
- `timeEstimate`
- `expiresAt`

### 3) Check Status

One-shot:

```bash
weave status inv_123
```

Watch mode:

```bash
weave status inv_123 --watch --interval-seconds 5 --timeout-seconds 900
```

Interpretation:

- Exit `0`: reached terminal status (`COMPLETED`, `FAILED`, `REFUNDED`, `EXPIRED`)
- Exit `2`: watch timeout (not a command failure)
- Exit `1`: command/API/network/validation failure

## Error Handling

When exit code is `1`, surface structured stderr JSON when present. Common API-derived shape:

```json
{
  "error": "api message",
  "status": 409,
  "details": {
    "error": "Invoice is not in PENDING status"
  }
}
```

If watch times out (exit `2`), treat as incomplete progress, not fatal failure. Recommend extending `--timeout-seconds` or rerunning a one-shot `weave status <invoice-id>`.

## Runtime Drift Rule

The installed binary and source tree can drift in token support. Always use runtime discovery (`weave tokens`) when deciding valid token/network combinations.
