---
name: agentpay
description: "Buy things from real websites on behalf of your human. Use when you need to purchase a product, complete a checkout, order something online, or propose a purchase for human approval. Handles encrypted credential storage, cryptographic purchase mandates, and headless browser checkout on any merchant site. The agent never sees the card."
metadata: {"openclaw":{"emoji":"💳","requires":{"anyBins":["agentpay","npx"]},"install":[{"id":"npm","kind":"node","package":"agentpay","bins":["agentpay"],"label":"Install AgentPay SDK"}]}}
---

# AgentPay — Secure Checkout for AI Agents

AgentPay lets you buy things from real merchant websites without ever seeing your human's payment credentials. Credentials stay encrypted on the human's machine. You propose purchases; your human approves cryptographically.

## References

- `references/cli-reference.md` — All CLI commands with examples
- `references/workflow.md` — Step-by-step purchase workflow and error handling

## Setup (one-time, human does this)

```bash
npx agentpay setup
```

The human enters their card details and sets a passphrase. Takes ~2 minutes. After this, the agent can propose purchases.

To set spending limits:

```bash
npx agentpay budget --set 500 --limit-per-tx 100
```

## Core Workflow

### 1. Propose a purchase

```bash
npx agentpay buy \
  --merchant "Amazon" \
  --description "Wireless keyboard, Logitech K380" \
  --url "https://www.amazon.com/dp/B0148NPH9I" \
  --amount "39.99"
```

This creates a pending purchase mandate. The human must approve it.

### 2. Human approves

```bash
npx agentpay pending     # list pending purchases
npx agentpay approve <txId>
```

Once approved, the headless browser handles checkout automatically. The agent never sees the card number — credentials are injected directly into the page from the encrypted vault.

### 3. Check status

```bash
npx agentpay status      # wallet status + recent transactions
npx agentpay history     # full transaction log
```

## MCP Server

AgentPay includes a built-in MCP server for direct tool integration:

```bash
npx agentpay mcp         # stdio transport (default)
npx agentpay mcp --http  # HTTP transport
```

This exposes AgentPay operations as MCP tools that any compatible agent can call directly.

## Quick Actions

| Task | Command |
|------|---------|
| Buy something | `npx agentpay buy --merchant "Store" --description "Item" --url "https://..." --amount "29.99"` |
| Check pending | `npx agentpay pending` |
| View budget | `npx agentpay budget` |
| Transaction history | `npx agentpay history` |
| Open dashboard | `npx agentpay dashboard` |

## Important Rules

- **Never** attempt to read, extract, or log payment credentials from the vault
- **Always** include `--merchant`, `--description`, and `--url` when proposing a purchase
- **Always** tell your human what you want to buy and why before proposing
- If a checkout fails, check `npx agentpay status` for error details — do not retry without telling the human
- Respect budget limits. If a purchase exceeds the per-transaction limit, inform the human instead of splitting into multiple transactions

## Ideas to Try

- "Order me a new phone charger under $20 from Amazon"
- "Restock my usual coffee beans from the same store as last time"
- "Find the cheapest flight to Madrid and book it for me"
- "Buy the textbook I need for next semester"
- "Subscribe me to that newsletter we were looking at"
