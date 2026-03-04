# How P&L (Profit & Loss) is calculated

## Why P&L might show 0%

P&L must be based on **actual entry price** (stored in JSON) and **current position value**. If P&L is always 0%:

1. Entry price is not written on buy
2. Entry price is not read from JSON when checking
3. Wrong data source is used (e.g. API percent instead of on-chain calculation)

## Correct P&L flow

### 1. On buy (buy-token.js)

After a successful buy, `buy-token.js` **automatically** writes entry price to `positions_report.json` (path: `POSITIONS_REPORT_PATH` or `NADFUNAGENT_DATA_DIR/positions_report.json`):

- `entryValueMON`: MON spent on the buy (e.g. 0.15)
- `currentValueMON`: at buy time = entryValueMON (P&L = 0%)
- `address`, `symbol`, `name`: token info

### 2. On position check (check-pnl.js)

`check-pnl.js`:

1. Reads entry price from the report JSON
2. Gets current value on-chain via nad.fun quote contract `getAmountOut(token, balanceWei, false)`
3. Computes: `P&L% = (currentValueMON - entryValueMON) / entryValueMON * 100`
4. Decides: P&L >= +5% → SELL (take profit), P&L <= -10% → SELL (stop loss), else HOLD

### 3. In the autonomous agent (execute-bonding-v2.js)

The cycle uses `check-pnl.js` (and `check-pnl.js --auto-sell`) for P&L, not API `percent`. Run from the `trading/` directory so scripts find each other via `__dirname`.

## Why P&L was 0% (common causes)

- Entry not written: buy failed or `recordEntryPrice` failed; report file missing or empty
- Entry not read: report path wrong, or token address mismatch
- Wrong source: using API `percent` instead of `check-pnl.js` / report + on-chain quote

## Verify it works

```bash
# Check entry prices in report
cat $HOME/nadfunagent/positions_report.json | jq '.positions[] | {symbol, entryValueMON, currentValueMON}'

# Run P&L check from trading directory
cd trading && node check-pnl.js
```

## P&L formula

```
P&L% = (currentValueMON - entryValueMON) / entryValueMON * 100
```
- `entryValueMON` = MON spent on buy (from JSON)
- `currentValueMON` = MON from selling now (on-chain via nad.fun quote)

Example: bought for 0.15 MON, now 0.16 MON → P&L = +6.67% → SELL (take profit).
