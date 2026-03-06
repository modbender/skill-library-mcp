---
name: a2a-payments
description: "Blockchain USDC payments via APay — pay services, manage budgets, open streaming channels, and handle x402 protocol."
metadata:
  {
    "openclaw":
      {
        "emoji": "💰",
        "requires": {},
        "install":
          [
            {
              "id": "plugin",
              "kind": "node",
              "package": "@a2a/openclaw-plugin",
              "label": "Install A2A Corp plugin",
            },
          ],
      },
  }
---

# A2A Payments (APay)

Blockchain-native USDC payments for AI agents on Base chain. Pay for services, manage budgets, and handle micropayments.

## Quick Start

Check your balance:

```
Use apay_check_balance to see my USDC balance
```

Pay a service:

```
Use apay_pay_service with serviceId "svc-123" and amount "0.50"
```

## Available Tools

### Balance & Budget

| Tool | Description |
|------|-------------|
| `apay_check_balance` | Check USDC balance, daily budget, spending limits |
| `apay_budget_check` | Verify if a specific amount is affordable |
| `apay_spending_history` | Get spending analytics and history |

### Payments

| Tool | Description |
|------|-------------|
| `apay_pay_service` | Pay a service (agent pays gas) |
| `apay_pay_signed` | Gasless signed payment (server submits on-chain) |
| `apay_estimate_cost` | Estimate cost including 0.5% platform fee |

### Services

| Tool | Description |
|------|-------------|
| `apay_list_services` | List available APay services |
| `apay_get_service` | Get detailed service info |

### Payment Channels (Streaming)

| Tool | Description |
|------|-------------|
| `apay_channel_status` | Check channel status |
| `apay_stream_open` | Open channel with USDC deposit |
| `apay_stream_pay` | Sign off-chain micropayment |
| `apay_stream_close` | Close channel (refund unspent) |

### x402 Protocol

| Tool | Description |
|------|-------------|
| `apay_x402_fetch` | Fetch URL with automatic x402 payment on HTTP 402 |

## Workflows

### Pay for a tool execution

1. `apay_budget_check` — verify affordability
2. `apay_estimate_cost` — see total with fees
3. `apay_pay_service` — execute payment
4. Receive payment receipt with tx hash

### Streaming micropayments

For services that charge per-request (API calls, data feeds):

1. `apay_stream_open` — deposit USDC into channel
2. `apay_stream_pay` — sign micropayments (off-chain, instant)
3. `apay_stream_close` — settle on-chain, refund remainder

### x402 auto-payment

For services using the HTTP 402 payment protocol:

```
Use apay_x402_fetch with url "https://api.example.com/premium/data" and maxPayment "1.00"
```

The tool automatically detects 402 responses, pays the required amount, and retries the request.

## Network

- **Chain**: Base (Coinbase L2)
- **Stablecoin**: USDC (6 decimals)
- **Model**: Escrow-based sessions with spending limits
- **Testnet**: base-sepolia for development
