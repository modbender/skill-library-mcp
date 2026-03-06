# Cross-Chain Swap

Execute a cross-chain token swap via Uniswap's bridge infrastructure, including quoting, safety validation, bridge monitoring, and destination-chain confirmation.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/cross-chain-swap
```

Or via Clawhub:

```bash
npx clawhub@latest install cross-chain-swap
```

## When to use

Use this skill when:

- You want to **swap tokens between different chains** (e.g., Ethereum → Base, Arbitrum → Optimism).
- You need a **single workflow** that handles routing, bridge selection, and safety checks.
- You want **status tracking** from source-chain send to destination-chain receipt.

## Example prompts

- "Swap 1,000 USDC on Ethereum to USDC on Base with full safety checks."
- "Convert 0.5 WETH on Arbitrum into WETH on Optimism."
- "Move my UNI from Polygon to Ethereum as USDC in one cross-chain swap."
