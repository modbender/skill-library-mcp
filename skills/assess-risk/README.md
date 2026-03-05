# Assess Risk

Get an independent risk assessment for any proposed Uniswap operation (swap, LP, bridge, token). Returns a clear APPROVE or VETO decision with reasoning.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/assess-risk
```

Or via Clawhub:

```bash
npx clawhub@latest install assess-risk
```

## When to use

Use this skill when:

- You want a **second-opinion risk check** before executing swaps, LP positions, bridges, or interacting with a token.
- You need a **binary APPROVE/VETO decision** plus explanation and mitigation suggestions.
- You care about **slippage, liquidity, contract, and bridge risks** being evaluated in one place.

## Example prompts

- "Assess the risk of swapping 50,000 USDC to WETH on Ethereum right now."
- "Evaluate the risk of LPing 20,000 USDC/OP on Optimism in the 0.3% fee tier pool."
- "How risky is it to bridge 10,000 USDC from Polygon to Base at this time?"
