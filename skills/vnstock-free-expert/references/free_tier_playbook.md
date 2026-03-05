# Free-Tier Playbook

## Rate limit profile
- Guest/no key: 20 requests/minute.
- Free key: up to 60 requests/minute.

## Execution controls
- Default minimum interval: 3.2 seconds/request.
- For unstable network/provider: increase to 4-5 seconds/request.
- Process symbols in chunks (e.g. 20-50 symbols/batch).

## Resilience checklist
- Retry transient failures with backoff.
- Log per-symbol failures; do not fail the whole run if a single symbol fails.
- Save intermediate artifacts (`universe`, `market_data`, `fundamentals`) for resume.

## Data quality checklist
- Confirm expected columns exist before calculation.
- Track missing metrics ratio.
- Flag stale data windows and low-bar histories.

## Portfolio-analysis checklist
- Use relative ranking, not absolute threshold only.
- Validate top picks against recent macro/news context.
- Apply sector diversification and risk caps.
