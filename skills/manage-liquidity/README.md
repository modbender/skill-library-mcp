# Manage Liquidity

Add liquidity, remove liquidity, or collect fees on Uniswap V2/V3/V4 pools. Handles pool selection, range configuration, approvals, safety checks, and execution end to end.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/manage-liquidity
```

Or via Clawhub:

```bash
npx clawhub@latest install manage-liquidity
```

## When to use

Use this skill when:

- You want to **provide new liquidity** to a Uniswap pool (V2, V3, or V4).
- You need to **remove or partially remove an LP position** and collect accrued fees.
- You want help choosing **fee tiers, ranges (for V3/V4), and position sizing** with safety constraints.

## Example prompts

- "Provide $5,000 of USDC/WETH liquidity on Arbitrum, choosing a good V3 range for moderate risk."
- "Remove half of my UNI/ETH V3 position on mainnet and collect all fees."
- "Add balanced liquidity to the highest-volume USDC/ETH pool on Base."
