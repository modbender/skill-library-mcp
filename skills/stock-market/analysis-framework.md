# Analysis Framework — Stock Market

Use this framework to turn broad market commentary into a decision-ready setup.

## 1) Context Snapshot

Capture market context in one pass:
- Index trend: up, down, range
- Liquidity regime: normal, thin, event-driven
- Volatility regime: compressed, normal, expanding
- Sector leadership: risk-on, defensive, mixed

If context is unstable, reduce position size assumptions.

## 2) Ticker Thesis Card

| Field | Prompt |
|------|--------|
| Setup type | Breakout, pullback, mean reversion, event repricing |
| Time horizon | Intraday, swing, position |
| Catalyst | Earnings, macro print, company event, sector flow |
| Base case | Most likely path if thesis is right |
| Failure mode | What invalidates the thesis |

Do not continue without a valid failure mode.

## 3) Evidence Grading

Grade each evidence line:
- `A`: confirmed by current data
- `B`: directional but incomplete
- `C`: narrative only

Minimum standard for action:
- At least two `A` signals, or
- One `A` plus one near-term catalyst

Otherwise classify as watchlist-only.

## 4) Scenario Map

| Scenario | Trigger | Action |
|----------|---------|--------|
| Bull case | Price confirms with volume | Execute planned entry and risk |
| Neutral case | Price stalls in range | Hold watchlist status |
| Bear case | Invalidation hit | Exit or no-trade |

Keep scenarios explicit to avoid emotional drift during live moves.

## 5) Decision Output

End analysis with one of:
- `Trade candidate` with trigger, invalidation, and target path
- `Watchlist candidate` with what to wait for
- `No-trade` with concrete reason

A missing decision label means analysis is incomplete.
