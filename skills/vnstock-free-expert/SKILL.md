---
name: vnstock-free-expert
description: Runs an end-to-end vnstock workflow for free-tier-safe Vietnam stock valuation, ranking, and API operations with strict rate-limit control; used when users request Vietnamese stock analysis under free-tier constraints.
compatibility: Requires Python 3.x, vnstock package, pandas, internet access, and optional VNSTOCK_API_KEY in .env.
---

# VNStock Free Expert

Use this skill when the user needs advanced Vietnam stock analysis with `vnstock`, while staying safe on free-tier limits.

## Important packaging note
This skill is self-contained and does not require shipping a separate `vnstock/` docs folder.
All operational knowledge needed by the agent is stored under:
- `references/`

## Read order
1. Read `references/capabilities.md`.
2. Read `references/method_matrix.md` for exact class/method mapping.
3. Read `references/free_tier_playbook.md` before large runs.

## Scope and constraints
- Library: `vnstock` only.
- Preferred sources: `kbs` first, `vci` fallback.
- Never use `tcbs`.
- Treat `Screener API` as unavailable unless user confirms it is restored in their installed version.

## Free-tier operating rules
- No API key: target <= 20 requests/minute.
- Free API key: target <= 60 requests/minute.
- Safe default pacing in scripts: 3.2s/request.
- Reuse cached artifacts between steps.

## Shared confidence rubric (required)
Report confidence as `High` / `Medium` / `Low` using this standard:
- `High`: universe coverage >= 95%, critical metrics coverage >= 80%, and hard errors <= 5% of symbols.
- `Medium`: universe coverage >= 80%, critical metrics coverage >= 60%, and hard errors <= 15%.
- `Low`: below `Medium` thresholds or material missing fields that can flip ranking results.

Always output:
1. Confidence level.
2. Coverage stats (`symbols_requested`, `symbols_scored`, `% missing by key metric`).
3. Top missing fields that may change conclusions.

## API key configuration (implemented)
- Skill-local key file: `.env`
- Variable: `VNSTOCK_API_KEY`
- All API-calling scripts auto-load this key and call vnstock auth setup before requests.
- You can override per run with `--api-key "..."`.

## Execution workflow (ordered)
1. Validate environment (`python`, `vnstock`, `pandas`) and load optional API key from `.env`.
2. Build a universe using `scripts/build_universe.py` (`group`, `exchange`, or `symbols` mode).
3. Collect market data with `scripts/collect_market_data.py` using safe pacing.
4. Collect fundamentals with `scripts/collect_fundamentals.py`.
5. Score and rank using `scripts/score_stocks.py`.
6. Generate analyst-style memo with `scripts/generate_report.py`.
7. Apply confidence rubric, disclose missing fields, and summarize risks.

## Downstream handoff bundle (required when doing single-ticker deep dive)
When the user request is about valuing or building a memo for a **specific ticker** (or a small list), output a compact JSON bundle that downstream skills can reuse:
- `ticker`, `as_of_date`, `currency`
- `financials` (income/balance/cashflow + key ratios if available)
- `price_history` (returns 1m/3m/6m/12m)
- `peer_set` (if you built one)
- `metadata.source` and `data_quality_notes`

This bundle is designed to feed `equity-valuation-framework` and `portfolio-risk-manager`.

## Script map

### A) Discovery and universal invocation (for broad feature coverage)

1. `catalog_vnstock.py`
Path: `scripts/catalog_vnstock.py`

Use when:
- You need to inspect available classes/methods in the installed `vnstock` version.
- You want to confirm compatibility before running a method.

2. `invoke_vnstock.py`
Path: `scripts/invoke_vnstock.py`

Use when:
- You need to call any supported class/method beyond the prebuilt valuation pipeline.
- You want one generic entry point for `Listing`, `Quote`, `Company`, `Finance`, `Trading`, `Fund`, or other exported classes.

This script supports dynamic invocation by class name and method name with JSON kwargs.

### B) Valuation pipeline scripts

1. `build_universe.py`
Use when building symbol universe from index/exchange/custom symbol list.
Input: source + mode + group/exchange/symbols.
Output: `outputs/universe_*.csv` and latest pointers.

2. `collect_market_data.py`
Use when collecting OHLCV/momentum fields (3M, 6M, 12M returns).
Input: universe CSV path.
Output: `outputs/market_data_*.csv` + per-symbol errors in JSON.

3. `collect_fundamentals.py`
Use when collecting valuation and quality metrics from finance/company APIs.
Input: universe CSV path.
Output: `outputs/fundamentals_*.csv` + per-symbol errors in JSON.

4. `score_stocks.py`
Use when ranking symbols with composite scoring.
Input: market + fundamentals CSV files.
Output: `outputs/ranking_*.csv`.

5. `generate_report.py`
Use when converting ranking output to analyst-style markdown memo.
Input: ranking CSV file.
Output: `outputs/investment_memo_*.md`.

6. `run_pipeline.py`
Use when running the end-to-end pipeline in one command.
Input: source + universe mode.
Output: all artifacts above in one run.

## Error handling rules
1. Log symbol-level failures and continue processing remaining symbols.
2. Do not claim missing metrics as zeros; mark them as missing.
3. If a critical step fails, stop and report failed step + command + suggested retry scope.

## Recommended decision logic
1. If request is “standard valuation/ranking”: run pipeline scripts.
2. If request needs a specific vnstock capability not in pipeline: use `catalog_vnstock.py` then `invoke_vnstock.py`.
3. If request volume is large: apply `free_tier_playbook.md` throttling and chunking strategy.

## Confidence aggregation (required)
When output includes ranking and valuation interpretation:
1. Compute data confidence from coverage metrics (`symbols_scored`, missing key fields, error ratio).
2. Compute model confidence from method robustness (single metric vs multi-factor consistency).
3. Final confidence = lower of data confidence and model confidence.
4. In `Low` confidence cases, provide directional output only and list required missing inputs.

## Required output template
1. `What Was Run`: scripts, source, universe scope, and pacing profile.
2. `Coverage`: requested symbols, scored symbols, and missingness by key field.
3. `Top Results`: ranked list with score columns.
4. `Key Risks`: concentration, stale data, missing metrics, or provider limitations.
5. `Confidence and Gaps`: final confidence + exact blockers.

## Quick command examples
```bash
python scripts/catalog_vnstock.py --outdir ./outputs
python scripts/invoke_vnstock.py --class-name Quote --init-kwargs '{"source":"kbs","symbol":"VCB"}' --method history --method-kwargs '{"start":"2024-01-01","end":"2024-12-31","interval":"1D"}' --outdir ./outputs
python scripts/run_pipeline.py --source kbs --mode group --group VN30 --outdir ./outputs
```

## Trigger examples
- "Analyze VN30 using vnstock but keep it free-tier safe."
- "Rank Vietnamese stocks by value/quality/momentum with KBS data."
- "Run a full vnstock pipeline and return top candidates with risk notes."
