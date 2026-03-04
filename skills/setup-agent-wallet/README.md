# Setup Agent Wallet

Set up an agent wallet for Uniswap operations. Supports Privy (development), Turnkey (production), and Safe (maximum security), including spending limits, token allowlists, and gas funding.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/setup-agent-wallet
```

Or via Clawhub:

```bash
npx clawhub@latest install setup-agent-wallet
```

## When to use

Use this skill when:

- You need to **provision a new wallet** for an agent or bot to use Uniswap.
- You want **structured spending limits and token allowlists** rather than an unconstrained wallet.
- You need to **fund the wallet with native gas and initial tokens** for operations.

## Example prompts

- "Set up a Safe-based wallet for my production trading agent on Ethereum with strict spending limits."
- "Create a Privy wallet for dev testing Uniswap flows on Base and fund it with test tokens."
- "Configure a Turnkey wallet for my LP strategy agent, including token allowlists and daily limits."
