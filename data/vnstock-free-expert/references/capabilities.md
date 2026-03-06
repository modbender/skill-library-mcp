# VNStock Capability Reference (Self-Contained)

## Core capabilities
- Symbol universe and classification: exchanges, industries, index groups, derivatives/bonds/warrants listings.
- Company intelligence: overview, shareholders, officers, subsidiaries, affiliates, events, reports (source-dependent).
- Market data: historical OHLCV, intraday prints, board snapshots, market depth (source-dependent).
- Financial statements and ratios: income statement, balance sheet, cash flow, ratio with period modes.
- Fund data: investment fund listings and related metadata.
- External connectors: available depending on environment and API keys.

## Source strategy
- Primary source: `kbs`.
- Secondary fallback: `vci`.
- Do not use `tcbs`.

## Data caveats
- Method availability differs by source.
- Some methods may return empty frames for specific symbols/time windows.
- Realtime/near-realtime outputs depend on market hours and provider freshness.

## Safe analysis pattern
1. Fetch raw data.
2. Validate shape/columns.
3. Handle empty/missing values.
4. Compute derived metrics.
5. Separate factual output from interpretation.
