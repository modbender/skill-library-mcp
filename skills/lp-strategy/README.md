# LP Strategy

Comprehensive LP strategy comparison for a token pair: versions, fee tiers, range widths, rebalance approaches, fee APY, impermanent loss, and risk.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/lp-strategy
```

Or via Clawhub:

```bash
npx clawhub@latest install lp-strategy
```

## When to use

Use this skill when:

- You want to **compare multiple LP strategies side by side** rather than get a single recommendation.
- You need to see **how APY, IL, gas costs, and rebalance frequency** differ across strategies.
- You're deciding between **tight vs. wide ranges, different fee tiers, or versions**.

## Example prompts

- "Compare several LP strategies for USDC/WETH on Optimism across fee tiers and range widths."
- "Show me a side-by-side LP strategy analysis for WBTC/ETH on Arbitrum, including estimated APY and IL."
- "Given my low risk tolerance, which LP strategies for USDC/DAI on Ethereum make the most sense?"
