# Deploy Agent Token

Deploy an agent token with a Uniswap V4 pool: configure hooks, bootstrap initial liquidity, optionally lock LP, and set up post-deployment monitoring.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/deploy-agent-token
```

Or via Clawhub:

```bash
npx clawhub@latest install deploy-agent-token
```

## When to use

Use this skill when:

- You want to **launch an agent token** with a properly configured Uniswap V4 pool.
- You need **custom hooks** (e.g., anti-snipe, revenue share) and **bootstrapped liquidity**.
- You care about **LP locking and monitoring** after launch.

## Example prompts

- "Deploy a new agent token with a V4 pool that shares a portion of fees with the treasury."
- "Launch an agent token on Base with anti-sniping and initial liquidity from 5 ETH + 10,000 tokens."
- "Create a V4 pool for an existing token with a revenue-share hook and lock the initial LP."
