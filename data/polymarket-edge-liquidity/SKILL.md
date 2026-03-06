---
name: polymarket-edge-liquidity
displayName: Polymarket Edge Liquidity
description: Trades active Polymarket-imported markets on Simmer when estimated edge and liquidity filters pass.
metadata:
  clawdbot:
    emoji: "📈"
    requires:
      pip: ["simmer-sdk"]
      env: ["SIMMER_API_KEY"]
    cron: "*/20 * * * *"
    automaton:
      managed: true
      entrypoint: "edge_liquidity.py"
version: "1.0.0"
published: true
---

# Polymarket Edge Liquidity

Simple strategy skill based on your starter settings:
- Scan every 20 minutes
- Require minimum edge (`MIN_EDGE`, default `0.03`)
- Require minimum liquidity (`MIN_LIQUIDITY`, default `3000`)
- Default to dry-run unless `--live` is provided

## Environment

- `SIMMER_API_KEY` (required)
- `TRADING_VENUE` (optional, default: `simmer`)
- `SCAN_LIMIT` (optional, default: `25`)
- `MIN_EDGE` (optional, default: `0.03`)
- `MIN_LIQUIDITY` (optional, default: `3000`)
- `TRADE_AMOUNT` (optional, default: `10`)

## Run manually

```bash
python3 edge_liquidity.py
python3 edge_liquidity.py --live
```

## Notes

- Trades are tagged with `source=sdk:polymarket-edge-liquidity` and `skill_slug=polymarket-edge-liquidity`
- Reasoning is always included for each trade
- By default this runs on virtual `$SIM` via `TRADING_VENUE=simmer`
