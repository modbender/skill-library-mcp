# Create Test Pool

Deploy a custom Uniswap pool on local testnet with configurable parameters for testing agent and strategy behavior.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/create-test-pool
```

Or via Clawhub:

```bash
npx clawhub@latest install create-test-pool
```

## When to use

Use this skill when:

- You already have a **local Uniswap testnet** running and want **custom pools**.
- You need specific **liquidity distributions, fee tiers, or ranges** to test agent behavior.
- You want to **simulate edge cases** like thin liquidity, wide ranges, or volatile pairs.

## Example prompts

- "Create a local test pool for USDC/WETH with very concentrated liquidity around the current price."
- "Deploy a WBTC/ETH test pool with thin liquidity to stress-test slippage handling."
- "Set up a stablecoin/stablecoin pool on local testnet for testing arbitrage bots."
