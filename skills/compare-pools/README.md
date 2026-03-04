# Compare Pools

Compare all Uniswap pools for a token pair across fee tiers and versions.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/compare-pools
```

Or via Clawhub:

```bash
npx clawhub@latest install compare-pools
```

## When to use

Use this skill when:

- You want to **compare all pools for a token pair** (e.g., different fee tiers on V3 or V4).
- You're deciding **where to LP** or **which pool to trade against** for best depth and fees.
- You care about **TVL, volume, fee APY, and price impact** across candidate pools.

## Example prompts

- "Compare all USDC/WETH pools on Arbitrum and recommend the best one for LPing."
- "Show me how the different UNI/ETH fee tiers on mainnet stack up on volume and fee APY."
- "For DAI/USDC on Polygon, which pool has the deepest liquidity and lowest expected slippage?"
