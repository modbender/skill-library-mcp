# Setup Local Testnet

Spin up a local Anvil testnet with Uniswap deployed and pre-seeded liquidity. Provides funded accounts and effectively zero gas costs for development.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/setup-local-testnet
```

Or via Clawhub:

```bash
npx clawhub@latest install setup-local-testnet
```

## When to use

Use this skill when:

- You want a **local Uniswap dev environment** for rapid iteration.
- You need a **repeatable way to start Anvil with Uniswap contracts and seeded liquidity**.
- You want **funded test accounts** for agents, bots, or integration testing.

## Example prompts

- "Set up a local Uniswap testnet with seeded USDC/WETH liquidity for development."
- "Start an Anvil instance with Uniswap deployed and provide me with funded test accounts."
- "Create a local test environment suitable for testing cross-chain-like flows with Uniswap."
