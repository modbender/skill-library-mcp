# Spritz Setup

Get your Spritz API key to start making off-ramp payments.

## 1. Create a Spritz Account

Go to [app.spritz.finance](https://app.spritz.finance) and sign up or log in.

## 2. Complete Verification

Spritz requires identity verification for fiat payments. Complete KYC in the dashboard if not already done.

## 3. Create an API Key

Navigate to **Settings > API Keys** and create a new key.

- Give it a descriptive name (e.g., "Agent Payments")
- Copy the key immediately — it won't be shown again

## 4. Store the API Key

**Option A: Environment variable**

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export SPRITZ_API_KEY="your-api-key"
```

Then restart your terminal.

**Option B: Agent platform config**

Add to your agent's environment configuration. For Claude Code, you can add it to your project's `.env` or configure it in your MCP server settings.

## 5. Test Your Setup

Verify the key works:

```bash
curl -X GET "https://api.spritz.finance/v1/bank-accounts" \
  -H "Authorization: Bearer $SPRITZ_API_KEY" \
  -H "Content-Type: application/json"
```

Should return `{"data": []}` (empty list for new accounts) or your existing bank accounts.

## 6. Add a Bank Account

Before making payments, add at least one bank account destination. See [bank-accounts.md](bank-accounts.md).

## Wallet Requirement

Spritz handles the fiat side. Your agent also needs a crypto wallet to send tokens to Spritz deposit addresses. Options:

- **Privy** — Server wallets with policy guardrails ([privy-agentic-wallets-skill](https://github.com/privy-io/privy-agentic-wallets-skill))
- **Turnkey** — Institutional-grade key management
- **Any wallet** — Any wallet the agent can sign transactions with

The wallet must be funded with the tokens you plan to off-ramp (e.g., USDC on Base).
