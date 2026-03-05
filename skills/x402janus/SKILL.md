---
name: x402janus
description: >
  x402janus — autonomous on-chain forensic analysis for EVM wallets.
  Scans wallets for risky token approvals, traces approval chains, detects drainers,
  and builds revoke transactions. Every call pays via x402 micropayment (USDC on Base).
  No API keys. No accounts. x402 IS the auth.
metadata:
  emoji: 🔲
  homepage: https://x402janus.com
  requires:
    bins: [node, npx]
    env: [PRIVATE_KEY, JANUS_API_URL]
---

# x402janus — Wallet Security for AI Agents

Nothing passes the gate unchecked.

## What This Does

Your agent sends a wallet address. Janus runs forensic analysis — traces approval chains, correlates threat intelligence, detects drainer patterns — and returns structured JSON your agent can act on. Paid via x402 micropayment. No API key. No account. Done.

## Setup

```bash
SKILL_DIR="$PWD/skills/x402janus"
cd "$SKILL_DIR" && npm install
```

**Required environment variables:**

| Variable | Description |
|----------|-------------|
| `PRIVATE_KEY` | Agent wallet private key. Signs x402 USDC payments. Must have USDC + ETH on Base. |
| `JANUS_API_URL` | API endpoint. Use `https://x402janus.com` |

**Optional:**

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_RPC_URL` | `https://base.gateway.tenderly.co` | RPC for signing transport |

## Commands

**All commands require `cd "$SKILL_DIR"` first.**

### Scan a Wallet

The primary command. Scans a wallet and returns risk score, findings, approvals, and pre-built revoke transactions.

```bash
# Quick scan ($0.01 USDC) — deterministic risk score
JANUS_API_URL=https://x402janus.com PRIVATE_KEY=$PRIVATE_KEY \
  npx tsx scripts/scan-wallet.ts <address> --json

# With chain specification
JANUS_API_URL=https://x402janus.com PRIVATE_KEY=$PRIVATE_KEY \
  npx tsx scripts/scan-wallet.ts <address> --chain base --json
```

**Output (JSON):**
```json
{
  "address": "0x...",
  "scannedAt": "2026-03-01T...",
  "payer": "0x...",
  "coverageLevel": "basic",
  "summary": {
    "totalTokensApproved": 3,
    "unlimitedApprovals": 2,
    "highRiskApprovals": 0,
    "healthScore": 80
  },
  "approvals": [...],
  "recommendations": [...],
  "revokeTransactions": [...]
}
```

**Exit codes:**
- `0` — low risk (score < 25)
- `1` — medium risk (score 25–49)
- `2` — high risk (score 50–74) or insufficient USDC
- `3` — critical risk (score ≥ 75)

**Agent integration pattern:**
```bash
# Run scan, check exit code for go/no-go decision
RESULT=$(JANUS_API_URL=https://x402janus.com PRIVATE_KEY=$PRIVATE_KEY \
  npx tsx scripts/scan-wallet.ts "$WALLET" --json 2>/dev/null)
EXIT=$?
if [ $EXIT -eq 0 ]; then
  echo "Safe to proceed"
else
  echo "Risk detected — halt transaction"
fi
```

### List Approvals

Lists all active token approvals for a wallet with risk assessment.

```bash
JANUS_API_URL=https://x402janus.com PRIVATE_KEY=$PRIVATE_KEY \
  npx tsx scripts/list-approvals.ts <address> --format json

# Filter by risk level
JANUS_API_URL=https://x402janus.com PRIVATE_KEY=$PRIVATE_KEY \
  npx tsx scripts/list-approvals.ts <address> --risk high,critical --format json

# Show only unlimited approvals
JANUS_API_URL=https://x402janus.com PRIVATE_KEY=$PRIVATE_KEY \
  npx tsx scripts/list-approvals.ts <address> --unlimited-only --format json
```

### Revoke Approval

Builds (and optionally executes) a revoke transaction for a specific token approval.

```bash
# Build revoke tx (dry run — outputs calldata)
JANUS_API_URL=https://x402janus.com PRIVATE_KEY=$PRIVATE_KEY \
  npx tsx scripts/revoke-approval.ts <wallet> <token> <spender> --json

# Execute the revoke on-chain
JANUS_API_URL=https://x402janus.com PRIVATE_KEY=$PRIVATE_KEY \
  npx tsx scripts/revoke-approval.ts <wallet> <token> <spender> --execute --json
```

⚠️ **`--execute` sends a real transaction. Confirm with user before executing.**

### Start Monitoring

Subscribes to real-time alerts for a wallet.

```bash
# Webhook alerts
JANUS_API_URL=https://x402janus.com PRIVATE_KEY=$PRIVATE_KEY \
  npx tsx scripts/start-monitoring.ts <address> --webhook https://your-webhook.com --json

# Telegram alerts
JANUS_API_URL=https://x402janus.com PRIVATE_KEY=$PRIVATE_KEY \
  npx tsx scripts/start-monitoring.ts <address> --telegram @username --json
```

## Pricing

| Tier | Price | Response Time | What You Get |
|------|-------|---------------|-------------|
| Quick | $0.01 USDC | <3s | Deterministic risk score, approval list, revoke txs |
| Standard | $0.05 USDC | <10s | + AI threat analysis, deeper lookback |
| Deep | $0.25 USDC | <30s | + Full graph analysis, drainer fingerprinting |

All payments settle via x402 micropayment (EIP-3009 TransferWithAuthorization) through the Thirdweb facilitator on Base. Your agent signs once, the facilitator settles USDC on-chain.

## How x402 Payment Works

1. Agent calls the scan endpoint
2. Server returns HTTP 402 with payment requirements (amount, recipient, asset)
3. Agent signs an EIP-3009 `TransferWithAuthorization` for the required USDC amount
4. Agent retries the request with the signed payment in the `X-PAYMENT` header
5. Thirdweb facilitator verifies and settles the payment on Base
6. Scan result is returned

The skill scripts handle steps 2–4 automatically. Your agent just calls the script.

## Wallet Requirements

The agent wallet (`PRIVATE_KEY`) needs:
- **USDC on Base** — for scan payments ($0.01–$0.25 per scan)
- **ETH on Base** — not required for x402 payments (facilitator pays gas), but needed if using `--execute` on revoke

## Safety

- Private key is used only for signing. Never logged, never in error messages, never in API responses.
- All scripts validate addresses before making requests.
- Revoke transactions require explicit `--execute` flag — dry run by default.
- x402 payments are exact amounts — the facilitator cannot take more than specified.
