# Trading Scripts (Nad.fun, Monad Mainnet)

Scripts for buying, selling, P&L check, and full autonomous cycle. **Mainnet only.**

## Setup

```bash
cd trading
npm install
```

Create `.env` file (default: `$HOME/nadfunagent/.env`). You can use a different path by setting `NADFUN_ENV_PATH`:

```env
MONAD_PRIVATE_KEY=0x...
MONAD_RPC_URL=https://monad-mainnet.drpc.org
MONAD_NETWORK=mainnet
```

**Environment variables for custom paths:**
- `NADFUN_ENV_PATH` — path to `.env` file (default: `$HOME/nadfunagent/.env`)
- `POSITIONS_REPORT_PATH` — path to `positions_report.json` (default: `$HOME/nadfunagent/positions_report.json`)

**Example (custom paths):**
```bash
export NADFUN_ENV_PATH=/home/user/myconfig/.env
export POSITIONS_REPORT_PATH=/home/user/myconfig/positions.json
node check-pnl.js
```

## Scripts

| Script | Description |
|--------|-------------|
| `node buy-token.js <address> <MON>` | Buy token (bonding curve or DEX). Records entry price to report. |
| `node sell-token.js --token <address> --amount all` | Sell one token. |
| `node sell-all.js` | Sell all positions (uses Agent API + on-chain balance). |
| `node check-pnl.js` | Show P&L (entry from report, current value from nad.fun quote). |
| `node check-pnl.js --auto-sell` | Same + sell if P&L ≥ +5% or ≤ -10%. |
| `node execute-bonding-v2.js` | Full cycle: check P&L + auto-sell → scan → score → buy top 5 (score ≥50) → final P&L. |

## P&L and entry price

- **Entry price** is written by `buy-token.js` after each successful buy to `positions_report.json`.
- **check-pnl.js** reads entry from that file and gets current value from nad.fun quote contract `getAmountOut(token, balanceWei, false)`.
- Formula: `P&L% = (currentValueMON - entryValueMON) / entryValueMON * 100`.

See `HOW_PNL_WORKS.md` and `ENTRY_PRICE_TRACKING.md` in this folder.

## Run full cycle (e.g. from cron)

```bash
cd /path/to/nadfunagent/trading
node execute-bonding-v2.js
```

Or with env:

```bash
NAD_PRIVATE_KEY=$(grep MONAD_PRIVATE_KEY $HOME/nadfunagent/.env | cut -d= -f2) node execute-bonding-v2.js
```

## LENS / Quote contract

LENS is nad.fun’s on-chain quote contract. Signature: `getAmountOut(address token, uint256 amountIn, bool isBuy)`. Mainnet: `0x7e78A8DE94f21804F7a17F4E8BF9EC2c872187ea`.
