# Rebalance Position

Rebalance an out-of-range Uniswap V3/V4 LP position: close the old position, collect fees, and open a new one centered around the current price.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/rebalance-position
```

Or via Clawhub:

```bash
npx clawhub@latest install rebalance-position
```

## When to use

Use this skill when:

- Your **V3/V4 LP position is out of range** and no longer earning fees.
- You want to **realign your range** around the current price while collecting all accumulated fees.
- You need guidance on **new range width** based on volatility and risk tolerance.

## Example prompts

- "My USDC/WETH V3 position on Optimism is out of range—rebalance it around the current price."
- "Close and reopen my WBTC/ETH V3 position on Arbitrum with a wider range for lower maintenance."
- "Collect fees and re-center my UNI/ETH position on mainnet, targeting a medium-width range."
