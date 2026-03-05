# Minimal Compatibility Mode

Use this mode when Python scripts are unavailable or model capability is limited.

## Goal

Maximize success rate and correctness with minimal token and logic complexity.

## Rules

1. Read at most 3 recent reports for the same ticker.
2. Use minimal sources:
- one official disclosure source
- one reliable market data source (Yahoo Finance acceptable)
3. Keep output short and deterministic.
4. Still include one self-improvement action from prior misses.

## Minimal Output Schema

- `recommendation`: Buy/Hold/Sell/Watch
- `pred_close_t1`: point estimate
- `prev_pred_close_t1`: if available, else `N/A`
- `prev_actual_close_t1`: if available, else `N/A/pending`
- `AE`, `APE`: if available, else `N/A`
- `improvement_actions`: exactly 1 item
- `status`: `ok|pending_data|blocked`

## Minimal Source Checklist

1. Official disclosure page (exchange/regulator/IR)
2. Market quote page (for example Yahoo Finance quote)

If the two sources conflict on critical values, set confidence to `Low`.
