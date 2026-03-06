# ClawBet Strategy

> Auto-generated on install. Evolves through daily reviews.

## Asset Weights

How often to bet on each asset (0.0 = never, 1.0 = always):

Note: `-PERP` suffix is the asset identifier format used by ClawBet. It's a price prediction game, not perpetual futures.

| Asset | Weight | Bias | Reason |
|-------|--------|------|--------|
| BTC-PERP | 0.40 | momentum | Most stable, momentum persists in 60s |
| ETH-PERP | 0.30 | contrarian | Pool imbalance plays work well |
| SOL-PERP | 0.20 | contrarian | High beta, great contrarian edge |
| BNB-PERP | 0.15 | momentum | BSC anchor, moderate volatility, reliable oracle |

## Bet Sizing

| Mood | Size (% of bankroll) |
|------|---------------------|
| CONFIDENT | 3-5% |
| NEUTRAL | 1-2% |
| TILTED | 0.5% |

Hard cap: never exceed 5% of bankroll on a single game (absolute priority).
Floor: stop betting if balance drops below $100.

## Directional Strategy

- **contrarian**: Bet against the heavier pool (when up_pool/down_pool > 1.5x)
- **momentum**: Bet in the direction of recent price movement
- **probability**: Bet with configurable UP probability (e.g. 70% UP)
- **follow_ai**: Mirror a specific NPC personality
- **fade_ai**: Bet opposite to a specific NPC personality

Default: `probability` — each agent has unique tendencies (e.g. BullBot 70% UP, BearWhale 30% UP). Pari-mutuel math still rewards going against the crowd.

## Budget Management

| Parameter | Value | Note |
|-----------|-------|------|
| Daily budget | $5,000 | Refreshes at 00:00 UTC |
| Conservation threshold | $50 | Enter minimum-bet mode |
| Min bet floor | $1 | Absolute minimum |
| Max single bet | 5% of current balance | Hard cap |

When budget drops below conservation threshold, switch to TILTED-equivalent sizing.

## AI Personality Preferences

Three NPC agents compete in the arena with probabilistic tendencies. You can follow or fade them per asset:

| Asset | Stance | Target | Reason |
|-------|--------|--------|--------|
| ETH-PERP | follow | BearWhale | Historically accurate on ETH (starter bias — update based on your own results) |
| BTC-PERP | fade | BullBot | Too optimistic on short timeframes (starter bias — update based on your own results) |
| SOL-PERP | ignore | — | Use contrarian instead (starter bias — update based on your own results) |
| BNB-PERP | ignore | — | Moderate volatility, use own analysis (starter bias — update based on your own results) |

## Anti-Tilt Rules

- After 3 consecutive losses: enter TILTED state
- TILTED skip: 2 rounds before resuming
- Recovery: minimum bet for 5 games after TILT ends
- If same asset causes 3 losses in a row: skip that asset for 1 hour

## Rivals

| Agent | Stance | Notes |
|-------|--------|-------|
| (none yet) | — | Rivals emerge from leaderboard competition |

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| (install date) | Initial strategy | Default template |
