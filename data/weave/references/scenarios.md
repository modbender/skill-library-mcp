# Weave Skill Scenarios

All examples are crypto-only and use placeholder addresses (no secrets).

## Scenario 1: Full Lifecycle (Multi-Network Receive Token)

Goal: create an invoice, quote payer instructions, and watch status.

1. Preflight

```bash
weave --help
weave tokens
```

2. Create invoice (USDC on Ethereum)

```bash
weave create \
  --receive-token USDC \
  --receive-network Ethereum \
  --amount 25 \
  --wallet-address 0x1111111111111111111111111111111111111111
```

3. Quote with payer asset/network

```bash
weave quote <invoice-id> \
  --pay-token USDT \
  --pay-network Ethereum \
  --refund-address 0x2222222222222222222222222222222222222222
```

4. Watch status

```bash
weave status <invoice-id> --watch --interval-seconds 5 --timeout-seconds 900
```

Success criteria:

- `create` returns `id` + `invoiceUrl`
- `quote` returns deposit instructions and expiry
- `status --watch` exits `0` on terminal state

## Scenario 2: Single-Network Receive Token (No Receive-Network Flag)

Goal: validate inferred receive network for single-network token.

```bash
weave create \
  --receive-token BTC \
  --amount 0.005 \
  --wallet-address bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

Success criteria:

- command succeeds without `--receive-network`
- response includes a valid invoice id

## Scenario 3: Timeout Handling In Watch Mode

Goal: classify timeout as incomplete progress, not hard failure.

```bash
weave status <invoice-id> --watch --interval-seconds 2 --timeout-seconds 20
echo $?
```

Expected:

- exit code `2` when timeout hits
- stderr JSON includes `error=status watch timed out` and `timeoutSeconds`

Follow-up:

- rerun with larger timeout, or
- run one-shot `weave status <invoice-id>`

## Scenario 4: Missing CLI Binary (Negative Path)

Goal: detect missing dependency and provide install instructions only.

Expected behavior:

- if `weave --help` fails with command-not-found, return install guidance:

```bash
go install github.com/AryanJ-NYC/weave-cash/apps/cli/cmd/weave@latest
weave --help
```

- if Go is not available, fallback to:

```bash
npm i -g weave-cash-cli
weave --help
```

- if both Go and npm are unavailable, report missing prerequisites clearly
- do not auto-execute install commands

## Manual Prompt Test Matrix

Use these prompts to verify trigger coverage:

1. "Create a Weave invoice for 25 USDC on Ethereum."
2. "Generate quote instructions for invoice `<id>` using USDT on Ethereum."
3. "Watch invoice `<id>` until final status."
4. "I don't have weave installed, help me run this flow."

Pass condition:

- skill follows preflight, JSON-first flow, and correct exit-code/error handling rules.
