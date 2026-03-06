# Corroboration Engine Rules (Aggregator)

This document defines deterministic verdicting constraints applied by `scripts/proof-bundle.sh`.

## 1) Hard blocks (single-gate BLOCKED allowed)
Single gate failure may produce `BLOCKED` **only** for hard blocks:

- **check_deps**: `status=FAIL`, `confidence>=0.9`, and confirmed evidence (`findings>0` or non-empty `hallucinated[]`)
- **type_check**: `status=FAIL` and `errors>0`
- **slop_scan**: `status=FAIL` and `density_per_kloc > 3 * threshold_per_kloc`

## 2) Non-hard corroboration (multi-signal BLOCKED)
For non-hard failures, `BLOCKED` requires all of:

- `corroborating_signals >= 2`
- `weighted_evidence >= 1.4`
- `corroborating_domain_count >= 2`
- `avg_soft_confidence >= 0.65`

If any of these are missing, verdict degrades to `CAUTION`.

## 3) Evidence domains
Gates are grouped by domain to avoid correlated false blocks:

- dependencies: `check_deps`
- correctness: `type_check`
- code_quality: `slop_scan`
- security: `red_team`, `regex_complexity`
- architecture: `design_review`
- delivery: `ci_integration`
- testing: `coverage_stats`, `mutation_test`
- planning: `ralph_loop`

## 4) Guardrail
No single non-hard gate may directly produce `BLOCKED`.
