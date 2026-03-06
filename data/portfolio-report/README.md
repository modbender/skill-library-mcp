# Portfolio Report

Generate a portfolio report for a wallet's Uniswap positions: total value, PnL, fee earnings, impermanent loss, and composition across chains.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/portfolio-report
```

Or via Clawhub:

```bash
npx clawhub@latest install portfolio-report
```

## When to use

Use this skill when:

- You want a **snapshot of your Uniswap portfolio** across all supported chains.
- You need to see **PNL, fee earnings, IL, and position composition** in one report.
- You're deciding **which positions to keep, rebalance, or exit** based on performance.

## Example prompts

- "Generate a Uniswap portfolio report for my wallet 0x... across all chains."
- "Show me which LP positions are losing to impermanent loss and which are profitable."
- "Summarize my Uniswap fee earnings and PnL over the last 90 days."
