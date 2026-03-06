# Find Yield

Find the highest-yield LP pools on Uniswap filtered by risk tolerance and minimum TVL.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/find-yield
```

Or via Clawhub:

```bash
npx clawhub@latest install find-yield
```

## When to use

Use this skill when:

- You want to **maximize LP fee yield** subject to a minimum TVL and risk tolerance.
- You're deciding **where to allocate fresh capital** for LP returns.
- You want a **ranked list of candidate pools** by expected fee APY.

## Example prompts

- "Find the highest-yield LP pools for USDC pairs on Arbitrum with at least $5M TVL."
- "Given a medium risk tolerance, where should I LP with WETH on Base for the best fees?"
- "List top 10 yield opportunities across all chains for stablecoin/stablecoin pools."
