# Execute Swap

Execute a Uniswap token swap with quotes, safety checks, simulation, and execution. Supports V2, V3, V4, UniswapX, and cross-chain routing on all supported chains.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/execute-swap
```

Or via Clawhub:

```bash
npx clawhub@latest install execute-swap
```

## When to use

Use this skill when:

- You want to **swap one token for another** on any Uniswap-supported chain.
- You care about **slippage, price impact, and safety limits** being enforced automatically.
- You want the agent to **choose the best routing** across V2/V3/V4/UniswapX, or honor a specific routing preference.

## Example prompts

- "Swap 1,000 USDC to WETH on Base with 0.5% max slippage."
- "Buy 0.5 WBTC with USDC on Arbitrum using UniswapX if it's cheaper."
- "Sell 10 UNI for ETH on mainnet and show me price impact and gas cost."
