# satsrail-mcp

Give any MCP-compatible AI agent the ability to accept Bitcoin Lightning payments. Create orders, generate invoices, and check payment status — all through natural language. No browser, no forms, no redirects.

**Works with:** Claude Desktop · Cursor · Windsurf · Cline · any MCP client

## What This Skill Does

This skill configures OpenClaw to use the [SatsRail MCP server](https://github.com/SatsRail/satsrail-mcp), enabling your agent to:

- Create Lightning payment orders
- Generate bolt11 invoices
- Check payment status in real-time
- List payments and orders
- Create hosted checkout sessions

## Why Lightning for AI Agents?

| | Credit Cards | Lightning (SatsRail) |
|---|---|---|
| **Integration** | Browser forms, redirects | One API call → invoice string |
| **Settlement** | 2-3 business days | Instant (seconds) |
| **Fees** | 2.9% + $0.30 | Fractions of a cent |
| **Microtransactions** | Economically irrational | Works at any amount |
| **Custody** | Held by processor | Non-custodial — your sats |

## Setup

### 1. Get your API key

Sign up at [satsrail.com](https://satsrail.com) and grab your secret key (`sk_live_...` or `sk_test_...`).

### 2. Configure MCP server

Add to your OpenClaw MCP config or Claude Desktop config:

```json
{
  "mcpServers": {
    "satsrail": {
      "command": "npx",
      "args": ["-y", "satsrail-mcp"],
      "env": {
        "SATSRAIL_API_KEY": "sk_test_your_key_here"
      }
    }
  }
}
```

### 3. Use it

Ask your agent:

> "Create a $25 order for a monthly subscription and generate a Lightning invoice"

## Available Tools

### Orders
- `create_order` — Create a payment order with optional auto-generated Lightning invoice
- `get_order` — Get order details by ID
- `list_orders` — List and filter orders by status
- `cancel_order` — Cancel a pending order

### Invoices & Payments
- `get_invoice` — Get invoice details including bolt11 Lightning payment string
- `generate_invoice` — Generate a new invoice for an existing order
- `check_invoice_status` — Real-time payment verification
- `list_payments` — List confirmed payments
- `get_payment` — Get payment details by ID

### Checkout & Config
- `create_checkout_session` — Create a hosted checkout session
- `get_merchant` — Get merchant profile and settings
- `list_wallets` — List connected Lightning wallets

## Example Flow

```
User: "Charge me $50 for the pro plan"

Agent → create_order(amount_cents: 5000, description: "Pro Plan", generate_invoice: true)
     ← bolt11: "lnbc500u1pj...kqq5yxmetu"

Agent: "Here's your Lightning invoice — scan or copy the payment string."

User: "Paid!"

Agent → check_invoice_status(invoice_id: "inv_xyz789")
     ← { status: "paid" }

Agent: "Payment confirmed! ⚡"
```

## Use Cases

- **SaaS billing** — Sell API access, subscriptions, or per-task services in the conversation
- **Agent-to-agent commerce** — Autonomous agents paying each other with instant settlement
- **Micropayments** — Pay-per-query, pay-per-generation — amounts too small for credit cards
- **Invoice automation** — Generate and send Lightning invoices based on usage or milestones

## Resources

- [GitHub](https://github.com/SatsRail/satsrail-mcp)
- [npm](https://www.npmjs.com/package/satsrail-mcp)
- [Developer Docs](https://satsrail.com/developers)
- [AI Agents Guide](https://satsrail.com/developers/ai-agents)
- [satsrail.com](https://satsrail.com)
