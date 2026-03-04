# Monitor TokenJar

Monitor the Uniswap TokenJar: balances, accumulation rates, burn economics, and projected time to next profitable burn.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/monitor-tokenjar
```

Or via Clawhub:

```bash
npx clawhub@latest install monitor-tokenjar
```

## When to use

Use this skill when:

- You want a **dashboard view of the TokenJar** and protocol fee accumulation.
- You need to know **current balances, accumulation rates, and burn economics**.
- You want a **projection for when the next profitable Firepit burn** is likely.

## Example prompts

- "Monitor the TokenJar and show current balances and estimated time to next profitable burn."
- "Give me a one-shot snapshot of TokenJar holdings and recent accumulation rates."
- "Set up a streaming view of TokenJar metrics for the next few minutes."
