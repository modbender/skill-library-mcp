# Batch Swap

Execute multiple token swaps in sequence (rebalance, multi-step trading plan). Each swap is validated independently with full safety checks.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/batch-swap
```

Or via Clawhub:

```bash
npx clawhub@latest install batch-swap
```

## When to use

Use this skill when:

- You want to **rebalance a portfolio** across several tokens in one workflow.
- You need to **execute a sequence of swaps** (e.g., USDC → WETH → UNI) as a plan.
- You want each leg of a multi-swap plan to have its **own slippage and safety checks**.

## Example prompts

- "Rebalance my wallet: convert 50% of my USDC to WETH and 25% to UNI on Base."
- "Sell 2 WBTC into USDC, then split that USDC 70/30 into ETH and UNI."
- "Execute a series of swaps to go from DAI to OP via USDC on Optimism."
