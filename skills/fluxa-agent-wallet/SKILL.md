---
name: fluxa-agent-wallet
description: >-
  FluxA Agent Wallet integration via CLI. Enables agents to make x402 payments
  for paid APIs, send USDC payouts to any wallet, and create payment links to receive
  payments. Use when the user asks about crypto payments, x402, USDC transfers,
  payment links, or interacting with the FluxA Agent Wallet.
---

# FluxA Agent Wallet

FluxA Agent Wallet lets AI agents perform onchain financial operations — payments, payouts, and payment links — without managing private keys. All operations use the **CLI** (`scripts/fluxa-cli.bundle.js`).

## Setup

The CLI bundle is located at `scripts/fluxa-cli.bundle.js` within this skill directory. It requires Node.js v18+.

```bash
node scripts/fluxa-cli.bundle.js <command> [options]
```

All commands output JSON to stdout:

```json
{ "success": true, "data": { ... } }
```

Or on error:

```json
{ "success": false, "error": "Error message" }
```

Exit code `0` = success, `1` = failure.

## Capabilities

| Capability | What it does | When to use |
|------------|-------------|-------------|
| **x402 Payment (v3)** | Pay for APIs using the x402 protocol with intent mandates | Agent hits HTTP 402, needs to pay for API access |
| **Payout** | Send USDC to any wallet address | Agent needs to transfer funds to a recipient |
| **Payment Link** | Create shareable URLs to receive payments | Agent needs to charge users, create invoices, sell content |

## Prerequisites — Register Agent ID

Before any operation, the agent must have an Agent ID. Register once:

```bash
node scripts/fluxa-cli.bundle.js init \
  --email "agent@example.com" \
  --name "My AI Agent" \
  --client "Agent v1.0"
```

Or pre-configure via environment variables:

```bash
export AGENT_ID="ag_xxxxxxxxxxxx"
export AGENT_TOKEN="tok_xxxxxxxxxxxx"
export AGENT_JWT="eyJhbGciOiJ..."
```

Verify status:

```bash
node scripts/fluxa-cli.bundle.js status
```

The CLI automatically refreshes expired JWTs.

## Opening Authorization URLs (UX Pattern)

Many operations require user authorization via a URL (mandate signing, payout approval, agent registration). When you need the user to open a URL:

1. **Always ask the user first** using `AskUserQuestion` tool with options:
   - "Yes, open the link"
   - "No, show me the URL"

2. **If user chooses YES**: Use the `open` command to open the URL in their default browser:
   ```bash
   open "<URL>"
   ```

3. **If user chooses NO**: Display the URL and ask how they'd like to proceed.

**Example interaction flow:**

```
Agent: I need to open the authorization URL to sign the mandate.
       [Yes, open the link] [No, show me the URL]

User: [Yes, open the link]

Agent: *runs* open "https://agentwallet.fluxapay.xyz/onboard/intent?oid=..."
Agent: I've opened the authorization page in your browser. Please sign the mandate, then let me know when you're done.
```

This pattern applies to:
- Mandate authorization (`authorizationUrl` from `mandate-create`)
- Payout approval (`approvalUrl` from `payout`)
- Agent registration (if manual registration is needed)

## Quick Decision Guide

| I want to... | Document |
|--------------|----------|
| **Pay for an API** that returned HTTP 402 | [X402-PAYMENT.md](X402-PAYMENT.md) |
| **Pay to a payment link** (agent-to-agent) | [PAYMENT-LINK.md](PAYMENT-LINK.md) — "Paying TO a Payment Link" section |
| **Send USDC** to a wallet address | [PAYOUT.md](PAYOUT.md) |
| **Create a payment link** to receive payments | [PAYMENT-LINK.md](PAYMENT-LINK.md) — "Create Payment Link" section |

### Common Flow: Paying to a Payment Link

This is a 6-step process using CLI:

```
1. PAYLOAD=$(curl -s <payment_link_url>)                    → Get full 402 payload JSON
2. mandate-create --desc "..." --amount <amount>            → Create mandate (BOTH flags required)
3. User signs at authorizationUrl                           → Mandate becomes "signed"
4. mandate-status --id <mandate_id>                         → Verify signed (use --id, NOT --mandate)
5. x402-v3 --mandate <id> --payload "$PAYLOAD"              → Get xPaymentB64 (pass FULL 402 JSON)
6. curl -H "X-Payment: <token>" <url>                       → Submit payment
```

**Critical:** The `--payload` for `x402-v3` must be the **complete** 402 response JSON including the `accepts` array, not just extracted fields.

See [PAYMENT-LINK.md](PAYMENT-LINK.md) for the complete walkthrough with examples.

## Amount Format

All amounts are in **smallest units** (atomic units). For USDC (6 decimals):

| Human-readable | Atomic units |
|---------------|-------------|
| 0.01 USDC | `10000` |
| 0.10 USDC | `100000` |
| 1.00 USDC | `1000000` |
| 10.00 USDC | `10000000` |

## CLI Commands Quick Reference

| Command | Required Flags | Description |
|---------|----------------|-------------|
| `status` | (none) | Check agent configuration |
| `init` | `--email`, `--name` | Register agent ID |
| `mandate-create` | `--desc`, `--amount` | Create an intent mandate |
| `mandate-status` | `--id` | Query mandate status (NOT `--mandate`) |
| `x402-v3` | `--mandate`, `--payload` | Execute x402 v3 payment |
| `payout` | `--to`, `--amount`, `--id` | Create a payout |
| `payout-status` | `--id` | Query payout status |
| `paymentlink-create` | `--amount` | Create a payment link |
| `paymentlink-list` | (none) | List payment links |
| `paymentlink-get` | `--id` | Get payment link details |
| `paymentlink-update` | `--id` | Update a payment link |
| `paymentlink-delete` | `--id` | Delete a payment link |
| `paymentlink-payments` | `--id` | Get payment records for a link |

**Common Mistakes to Avoid:**

| Wrong | Correct |
|-------|---------|
| `mandate-create --amount 100000` | `mandate-create --desc "..." --amount 100000` |
| `mandate-status --mandate mand_xxx` | `mandate-status --id mand_xxx` |
| `x402-v3 --payload '{"maxAmountRequired":"100000"}'` | `x402-v3 --payload '<full 402 response with accepts array>'` |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `AGENT_ID` | Pre-configured agent ID |
| `AGENT_TOKEN` | Pre-configured agent token |
| `AGENT_JWT` | Pre-configured agent JWT |
| `AGENT_EMAIL` | Email for auto-registration |
| `AGENT_NAME` | Agent name for auto-registration |
| `CLIENT_INFO` | Client info for auto-registration |
| `FLUXA_DATA_DIR` | Custom data directory (default: `~/.fluxa-ai-wallet-mcp`) |
| `WALLET_API` | Wallet API base URL (default: `https://walletapi.fluxapay.xyz`) |
| `AGENT_ID_API` | Agent ID API base URL (default: `https://agentid.fluxapay.xyz`) |
