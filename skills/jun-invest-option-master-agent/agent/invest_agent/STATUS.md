# Invest Agent Status

Last updated: 2026-03-01 (America/Los_Angeles)

## Milestone: Data pipeline (Futu options + public ETF fallback)
- OpenD: reachable at 127.0.0.1:11111 (healthcheck OK)
- Futu SDK: futu-api 9.06.5608 installed in invest_agent/.venv
- Futu adapter: implemented (healthcheck, quotes, best-effort options chain summary)
  - File: invest_agent/integrations/futu/futu_adapter.py
  - Note: US ETF quotes (SPY/QQQ) not permitted via Futu in current account; will use public skills as fallback for ETF spot/benchmarks.

## Remaining work (to complete all items)
P0 (close the loop first)

## P0 completed
- Approval packet assembler: invest_agent/bin/assemble_packet (outputs -> invest_agent/outputs/approval_packet.md)
- Validator + CLI + fixtures: invest_agent/bin/invest, invest_agent/tools/*, invest_agent/examples/fixtures/*

P1 (quality enhancements)
- Options chain summary metrics (ATM IV/skew/spread/OI) — DONE (commit 4a75572)
- Validator numeric policy checks (cash buffer / concentration / cash coverage) — DONE

## Completed since last milestone
- Public benchmark fallback via yfinance (SPY/QQQ spot + rv20, VIX proxy): invest_agent/integrations/public/yfinance_fallback.py
- Data snapshot generator (writes invest_agent/outputs/Data.json): invest_agent/bin/data_snapshot

## Pending optimizations (planned)
- Regime (Step 2) needs stronger evidence stack beyond VIX+rv20:
  - trend (MA slope / drawdown / momentum)
  - corr (SPY-QQQ correlation trend)
  - liquidity proxies
  - explicit thresholds per label
- Approval packet must include Decision logic blocks showing how Regime + IV/skew/spread/OI affect:
  - delta/DTE selection
  - position sizing cadence
  - execution (limit + concession)

- EquityAlpha (Step 3) enhancements:
  1) key_levels automation (support/resistance/invalidation_level) via mature skills (no hand-rolled TA)
  2) richer catalysts beyond earnings (macro calendar + sector events) via skills
  3) evidence-backed CSP/CC fit (assignment suitability, manageability)
  4) standardized tradability scoring (spread/OI/volume thresholds; hard rules to switch/skip)

- Risk (Step 6) enhancements:
  1) policy coverage expansion in validator (max drawdown 30%, sector limits, buffer usage calculation with real account cash)
  2) standardized veto/limit reasons taxonomy (machine-readable) + mapping to approval packet
  3) explicit trigger thresholds templates (e.g., underlying % move, IV spike, spread widening) with default values per regime
  4) conflict resolution rules: when Risk=LIMIT/VETO, PM must auto-downgrade and regenerate packet

- Execution (Step 7) enhancements:
  1) standardize execution thresholds (spread limits, max concession rules)
  2) parameterize execution↔risk triggers (structured fields, not only prose)
  3) execution quality logging for Postmortem (mid vs fill, concession, spread at entry)
  4) optional: integrate deeper liquidity signals (if broker supports)
  5) optional: order splitting / staged limit improvements
  6) optional: time-window rules (avoid macro releases; prefer liquid windows)

- PM/Assembler (Step 8) enhancements:
  1) increase auto-fill coverage for all sections (Regime/Alpha/Options/Portfolio/Execution) — DONE (commit c198154)
  2) auto-generate Decision basis block (metrics→meaning→action) — DONE (commit c198154)
  3) consistency/conflict checks across role outputs (auto downgrade to LIMIT) — DONE (commit 07772ef)
  4) add audit metadata header (data sources, asof, OpenD health, skill versions) — DONE (commit 9c6679d)
  5) improve readability: summary-first + appendices for raw JSON — PARTIAL (TL;DR added, commit d684dd0)

## Risks / blockers
- None critical for P0; enhancements are iterative.
