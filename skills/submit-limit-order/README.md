# Submit Limit Order

Submit a UniswapX Dutch auction limit order with MEV-protected execution and no gas cost until the order is filled.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/submit-limit-order
```

Or via Clawhub:

```bash
npx clawhub@latest install submit-limit-order
```

## When to use

Use this skill when:

- You want to **set a target price** to buy or sell a token instead of executing immediately.
- You want **MEV-protected execution** via UniswapX fillers.
- You prefer **no upfront gas cost** and are comfortable waiting for fillers to execute your order.

## Example prompts

- "Create a limit order to buy 2 ETH with USDC if the price drops to $2,800."
- "Sell 1,000 UNI for USDC with a minimum price of $8.50 on Ethereum."
- "Place a UniswapX limit order to swap 5 WETH to USDC at a target price of $3,500/ETH."
