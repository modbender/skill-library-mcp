# Market Launch Checklist

Use this checklist when publishing the skill to a public marketplace and targeting high adoption.

## Positioning

1. Lead with outcome in one line:
- "Backtest stock strategies and output win rate, return, drawdown, and Sharpe in one command."

2. Emphasize differentiation:
- Long-only execution with `t+1` open fills (anti-look-ahead).
- Built-in transaction cost + slippage handling.
- Trade-level CSV plus machine-readable JSON.

3. Include trigger phrases in listing copy:
- "strategy backtest"
- "win rate analysis"
- "收益率回测"
- "量化策略验证"

## Listing Asset Checklist

1. `SKILL.md` has explicit command examples.
2. `agents/openai.yaml` has clear `display_name`, `short_description`, and `default_prompt`.
3. Include one sample CSV for quick demo.
4. Keep script dependency-light to reduce setup friction.

## Conversion Boosters

1. Provide copy/paste examples for three strategy families:
- Trend following (SMA)
- Mean reversion (RSI)
- Breakout

2. Make outputs actionable:
- Show not only returns but also drawdown and trade quality metrics.

3. Add "first run under 60 seconds" claim only if verified in your environment.

## Post-Launch Growth Loop

1. Track user feedback by failure pattern:
- Input parsing issues
- Missing strategy presets
- Output format requests

2. Release frequent small improvements:
- New preset
- Better error messages
- Extra output field

3. Keep changelog visible in marketplace update notes.
