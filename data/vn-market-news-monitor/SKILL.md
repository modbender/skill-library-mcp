---
name: vn-market-news-monitor
description: Tracks Vietnam market and sector narratives from major domestic financial media; used when users ask for market stories, sector heat, and most-mentioned Vietnamese tickers.
compatibility: Requires OpenClaw web fetch and Brave API access.
---

# Vietnam Market News Monitor (Web Workflow)

Use this skill to monitor domestic Vietnam market narratives by sector and ticker mentions.

## Data sources
- CafeF: https://cafef.vn/
- VnEconomy: https://vneconomy.vn/
- VietnamFinance: https://vietnamfinance.vn/
- Vietstock: https://vietstock.vn/

## Tooling assumption
- OpenClaw web fetch + Brave API available.
- No Python scripts needed for this skill.

## Execution workflow
1. Fetch latest headlines from all four sources.
2. Tag headlines by sector and potential ticker mentions.
3. Count mention intensity by sector.
4. Compare with previous snapshot (if available) to detect narrative acceleration/deceleration.
5. Highlight possible misinformation/noise risk areas.

## Data quality gate (required)
Run this gate before final output:
1. Freshness: include collection window in ICT (`UTC+7`) and last-update timestamp per source.
2. Coverage: target >= 3 domestic sources; if < 3, set confidence to `Low`.
3. De-duplication: cluster duplicate headlines by normalized title + publisher domain.
4. Evidence tags: mark each major claim as `Fact` (headline/text) or `Inference` (market implication).
5. Bias check: flag concentration if one source contributes > 50% of collected items.

## Shared confidence rubric (required)
Apply this common standard:
- `High`: >= 3 active sources, fresh window (24h/7d explicitly stated), and low concentration bias.
- `Medium`: 2 sources or moderate concentration bias, but sector/ticker narratives are still cross-validated.
- `Low`: < 2 sources, stale window, or highly concentrated/noisy coverage with weak confirmation.

Always output confidence with:
1. Source coverage table.
2. Freshness window (ICT `UTC+7`).
3. Major noise/bias factor that may distort narrative ranking.

## Output format (required)
- Section 1: Source coverage and freshness.
- Section 2: Top sectors by media intensity.
- Section 3: Most-mentioned tickers.
- Section 4: Narrative shift vs previous period.
- Section 5: Risks and validation checklist before investment action.

## Watchlist mode (optional)
If the user provides an `ACTIVE_WATCHLIST` (tickers), add an extra section:
- `Watchlist Impact Map`: for each ticker, list relevant headlines (with links), label `Fact` vs `Inference`, and provide 1–2 monitoring triggers.

Do **not** issue buy/sell commands; this skill is for signal monitoring only.

## Trigger examples
- "What are the hottest Vietnam market narratives today?"
- "Which sectors and tickers are mentioned most in Vietnamese financial media?"
- "Compare this week's market narrative vs last week."

## Quality rules
- Headlines are signals, not direct trading decisions.
- Always recommend cross-checking with `vnstock` quantitative metrics.
- Provide source links for every major statement.
- If source coverage is weak or stale, explicitly downgrade confidence.
