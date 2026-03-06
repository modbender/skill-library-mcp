---
name: us-macro-news-monitor
description: Tracks US macro signals from Bloomberg, WSJ, and Reuters and maps potential spillover to Vietnam sectors; used when users ask about US macro news and likely impacts on Vietnamese equities.
compatibility: Requires OpenClaw web fetch and Brave API access.
---

# US Macro News Monitor (Web Workflow)

Use this skill for US macro monitoring that can indirectly impact Vietnamese equities.

## Data sources
Primary media sources:
- Bloomberg: https://www.bloomberg.com/
- WSJ: https://www.wsj.com/
- Reuters Markets: https://www.reuters.com/markets/

Fallback (open/public macro sources):
- Federal Reserve (FOMC/calendar/speeches): https://www.federalreserve.gov/
- BLS releases (CPI, jobs): https://www.bls.gov/
- BEA releases (GDP, PCE): https://www.bea.gov/
- FRED calendars/series metadata: https://fred.stlouisfed.org/

## Tooling assumption
- OpenClaw web fetch + Brave API available.
- No Python scripts needed for this skill.

## Execution workflow (ordered)
1. Collect fresh headlines from primary sources.
2. Replace blocked/paywalled coverage with fallback public sources.
3. Classify items into macro themes.
4. Tag each item with tone (`risk-on`, `risk-off`, `neutral`).
5. Map transmission channels to Vietnam sectors and representative tickers.
6. Run quality gate and confidence scoring.
7. Produce required output sections with source links.

## Theme taxonomy
Classify each item into these macro themes:
- inflation
- rates/yields
- growth/employment
- USD/FX
- oil/energy
- geopolitics/trade

Summarization horizon:
- 24h changes
- 7d narrative drift

## Data quality gate (required)
Run this gate before finalizing output:
1. Freshness: include only items with explicit publish/update time; report window in ICT (`UTC+7`).
2. Coverage: target >= 3 distinct sources; if < 3, downgrade confidence.
3. De-duplication: remove near-duplicate headlines by normalized title + URL domain.
4. Evidence tags: mark each claim as `Fact` or `Inference`.
5. Missingness log: list blocked/paywalled sources and what fallback replaced them.

## Shared confidence rubric (required)
Apply this common standard:
- `High`: >= 3 distinct sources, <= 24h freshness for core items, and no single-source dominance over 60%.
- `Medium`: 2 sources or partial freshness gaps, but core themes still cross-confirmed.
- `Low`: 1 source only, stale coverage, or major paywall blocks without reliable fallback.

Always output confidence with:
1. Source count and source list.
2. Time window used (ICT `UTC+7`).
3. Main uncertainty driver (paywall, missing source, stale timing, or weak cross-confirmation).

## Output format (required)
- Section 1: Top headlines with source URLs.
- Section 2: Theme counts and tone distribution.
- Section 3: Vietnam sector spillover map.
- Section 4: Actionable watchlist (what to monitor next).

## Watchlist mode (optional)
If the user provides an `ACTIVE_WATCHLIST` (tickers), extend Sections 3–4:
- Add a `Watchlist Impact Map` that maps macro themes → transmission channel → each ticker.
- Provide **monitoring triggers** (what would confirm/negate the impact) and a confidence tag.
- Never output absolute buy/sell instructions; this skill produces signals and watch items.

## Trigger examples
- "What US macro news overnight could move VN stocks today?"
- "Summarize Fed/CPI signals and their impact on Vietnam sectors."
- "Map US rates and USD narrative to Vietnamese equities."

## Quality rules
- Clearly mark inferred impacts as inference.
- Respect paywalls: use only accessible metadata when full text is unavailable.
- Avoid over-claiming causality.
- If source coverage is below threshold, explicitly set confidence to `Low`.
