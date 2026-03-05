# Fundamental Stock Analysis (OpenClaw Skill)

This is an **OpenClaw skill** for structured fundamental equity analysis and peer ranking.

It applies a scoring playbook focused on:
- Business quality
- Balance-sheet safety
- Cash-flow quality
- Valuation context
- Risk and confidence modifiers

## What this skill does

Use this skill to:
- Analyze one or more stock tickers from a fundamentals perspective
- Compare peers and rank them
- Produce a decisive, risk-aware verdict with confidence level

The workflow is playbook-driven and explicitly marks missing data as `NA` instead of guessing.

## How to use

### Trigger cases
Use this skill when the user asks things like:
- “Analyze ticker X fundamentally”
- “Compare these 3 stocks and pick the best”
- “Give me a fundamentals-based verdict for [ticker]”

### Required behavior
1. Read `references/playbook.md` before starting.
2. Follow the playbook steps in order.
3. For multi-ticker requests, analyze each ticker first, then rank peers.
4. Always include confidence and call out stale/conflicting data.
5. Append the required machine-readable JSON block at the end.

## Output expectations
- Be decisive, not vague.
- Separate quality, balance-sheet safety, and valuation.
- Never fabricate missing metrics.
- Include data-source links in a final `Sources` section.

## Disclaimer

This skill is for educational and informational purposes only. It is **not** financial, investment, legal, tax, or accounting advice.

No output from this skill is a recommendation or solicitation to buy, sell, or hold any security. Markets are risky, data may be incomplete or stale, and past performance does not guarantee future results. Always do your own research and consult a licensed financial advisor before making investment decisions.
