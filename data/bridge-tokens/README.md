# Bridge Tokens

Bridge tokens from one chain to another without swapping. The same token is sent on the source chain and received on the destination chain.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/bridge-tokens
```

Or via Clawhub:

```bash
npx clawhub@latest install bridge-tokens
```

## When to use

Use this skill when:

- You want to **move a token from one chain to another** without changing it (e.g., USDC Ethereum → USDC Base).
- You need **simple bridging only**, not a swap plus bridge.
- You want safety checks around **bridge choice, limits, and completion status**.

## Example prompts

- "Bridge 1,000 USDC from Ethereum to Base."
- "Move my WETH from Arbitrum to Optimism without swapping."
- "Bridge 500 USDT from Polygon to Ethereum and confirm when it arrives."
