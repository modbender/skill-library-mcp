# Optimize LP

Get the optimal LP strategy for a token pair: version, fee tier, range width, and rebalance approach based on pair characteristics and risk tolerance.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/optimize-lp
```

Or via Clawhub:

```bash
npx clawhub@latest install optimize-lp
```

## When to use

Use this skill when:

- You want a **single best LP strategy** recommendation for a given token pair.
- You need guidance on **which version (V2/V3/V4), fee tier, and range width** to use.
- You care about **fee APY vs. impermanent loss trade-offs** for your risk tolerance.

## Example prompts

- "Given 10,000 USDC and moderate risk tolerance, what is the optimal way to LP USDC/WETH on Arbitrum?"
- "Design the best LP setup for WBTC/ETH on mainnet, including version, fee tier, and range."
- "For a conservative strategy, how should I LP USDC/DAI on Base?"
