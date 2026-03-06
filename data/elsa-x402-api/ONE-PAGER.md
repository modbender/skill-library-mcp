# OpenClaw Elsa x402

**AI-powered DeFi trading with micropayments**

---

## What is it?

A skill-pack that lets OpenClaw AI agents interact with DeFi protocols through the Elsa API, paying per-request with USDC micropayments via the x402 protocol.

## Key Features

| Feature | Description |
|---------|-------------|
| **Pay-per-use** | No subscriptions. Pay only for API calls you make (~$0.01-0.05 per call) |
| **Non-custodial** | Private keys never leave your machine. All signing is local |
| **Budget controls** | Per-call and daily limits prevent runaway spending |
| **Multi-chain** | Base, Ethereum, Arbitrum, Optimism, Polygon, BSC, Avalanche, zkSync |
| **Safe by default** | Execution tools disabled until explicitly enabled |

## Tools

```
Read-Only (Always On)          Execution (Opt-In)
─────────────────────          ──────────────────
elsa_search_token              elsa_execute_swap_confirmed
elsa_get_token_price           elsa_pipeline_get_status
elsa_get_balances              elsa_pipeline_submit_tx_hash
elsa_get_portfolio             elsa_pipeline_run_and_wait
elsa_analyze_wallet
elsa_get_swap_quote
elsa_execute_swap_dry_run
elsa_budget_status
```

## How Swaps Work

```
Quote → Dry Run → User Confirms → Execute
  │        │           │            │
  │        │           │            └─ Signs & broadcasts txs
  │        │           └─ Human in the loop
  │        └─ Creates pipeline, no onchain action
  └─ Shows expected output
```

## Quick Start

```bash
# 1. Clone & install
git clone https://github.com/HeyElsa/elsa-openclaw.git
cd elsa-openclaw && npm install

# 2. Set payment wallet
export PAYMENT_PRIVATE_KEY=0x...

# 3. Test
npx tsx scripts/index.ts elsa_search_token '{"query": "USDC"}'
```

## Use Cases

- **Portfolio tracking** - Monitor wallet balances across chains
- **Token research** - Search and price tokens before trading
- **Automated swaps** - Execute trades with AI agent oversight
- **Risk analysis** - Analyze wallet behavior and risk profiles

## Pricing

| Endpoint | Cost |
|----------|------|
| Search/Price | ~$0.01 |
| Portfolio/Balances | ~$0.02 |
| Swap Quote | ~$0.03 |
| Execute Swap | ~$0.05 |

*Actual costs determined by x402 headers at request time*

## Links

- **GitHub**: [github.com/HeyElsa/elsa-openclaw](https://github.com/HeyElsa/elsa-openclaw)
- **Elsa API**: [x402.heyelsa.ai](https://x402.heyelsa.ai)
- **x402 Protocol**: [x402.org](https://x402.org)

---

*Built with x402 micropayments on Base*
