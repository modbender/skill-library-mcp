# Entry price tracking and P&L

## Overview

Entry price is stored automatically for each position; P&L is computed from that and current on-chain value.

## How it works

### 1. On buy (buy-token.js)

After a successful buy, `buy-token.js` writes entry to `positions_report.json`:

```bash
cd trading
NAD_PRIVATE_KEY=0x... node buy-token.js 0x123...abc 0.15
```

- Script buys (bonding curve or DEX), then on success writes `entryValueMON` and token info to the report.

### 2. On check (check-pnl.js)

`check-pnl.js` reads entry from the report and current value from the nad.fun quote contract, then computes P&L and shows HOLD / SELL (take profit) / SELL (stop loss).

```bash
cd trading && node check-pnl.js
```

### 3. Auto-sell (check-pnl.js --auto-sell)

Sells positions where P&L >= +5% or <= -10%:

```bash
node check-pnl.js --auto-sell
```

## Report structure (positions_report.json)

Path: `POSITIONS_REPORT_PATH` or `NADFUNAGENT_DATA_DIR/positions_report.json`.

```json
{
  "timestamp": "2026-02-13T19:00:00.000Z",
  "wallet": "0x...",
  "positionsCount": 3,
  "positions": [
    {
      "address": "0xToken...",
      "symbol": "SYMBOL",
      "entryValueMON": 0.15,
      "currentValueMON": 0.1485,
      "pnlPercent": -1.00,
      "balance": 881.03,
      "dataSource": "onchain"
    }
  ]
}
```

## In the autonomous agent

`execute-bonding-v2.js` uses: `check-pnl.js` (and `--auto-sell`) for P&L, `buy-token.js` for buys (which records entry), and `sell-token.js` for sells.

## Commands (from `trading/`)

```bash
NAD_PRIVATE_KEY=0x... node buy-token.js <token-address> 0.15
node check-pnl.js
node check-pnl.js --auto-sell
NAD_PRIVATE_KEY=0x... node sell-token.js --token <address> --amount all
node sell-all.js
```

Entry is written automatically on buy; P&L uses the report and on-chain quote (not API percent).
