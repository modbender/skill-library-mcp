---
name: kraken-pro
description: Manage Kraken exchange accounts — portfolio, market data, trading, earn/staking, ledger export. REST API via python-kraken-sdk. Use when the user wants to check crypto portfolio, get prices, place/cancel orders, manage staking, export ledger for taxes, deposit/withdraw funds, or interact with Kraken in any way.
metadata: {"openclaw":{"requires":{"bins":["python3"],"env":["KRAKEN_API_KEY","KRAKEN_API_SECRET"]},"primaryEnv":"KRAKEN_API_KEY"}}
---

# Kraken Skill

Manage your Kraken exchange account via CLI.

## Setup

```bash
pip3 install -r requirements.txt
```

Set credentials via environment variables or OpenClaw config (`skills.entries.kraken-pro.env`).

Get API key: https://www.kraken.com/u/security/api

## Commands

Run: `python3 kraken_cli.py <command> [options]`

All commands accept `--json` for raw JSON output.

### Portfolio (auth required)

| Command | Description |
|---------|-------------|
| summary | Portfolio overview (handles flex vs bonded earn correctly) |
| net-worth | Single net worth number |
| holdings | Asset breakdown with USD values |
| balance | Raw asset quantities |

### Market Data (no auth)

| Command | Description |
|---------|-------------|
| ticker --pair XBTUSD | Price and 24h stats |
| pairs | Trading pairs |
| assets | Asset list |

### Order History (auth required)

| Command | Description |
|---------|-------------|
| open-orders | Active orders |
| closed-orders [--limit N] | Completed orders |
| trades [--limit N] [--csv] | Trade execution history (CSV for export) |

### Ledger (auth required)

```
ledger [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--asset BTC] [--type trade|deposit|withdrawal|staking] [--csv] [--limit N]
```

Auto-paginates (Kraken returns max 50/request). `--csv` dumps raw Kraken data.

### Trading (auth required)

All trading commands require `--confirm`. Use `--validate` for dry-run.

| Command | Description |
|---------|-------------|
| buy --pair XBTUSD --type market\|limit --amount N [--price P] --confirm | Place buy order |
| sell --pair XBTUSD --type market\|limit --amount N [--price P] --confirm | Place sell order |
| cancel-order --id OXXXXX --confirm | Cancel specific order |
| cancel-all --confirm | Cancel all open orders |

**Always confirm with the user before placing real orders. Use `--validate` first.**

### Earn/Staking (auth required)

| Command | Description |
|---------|-------------|
| earn-positions | Current staking allocations |
| earn-strategies | Available yield programs |
| earn-status | Pending requests |
| earn-allocate --strategy-id ID --amount N --confirm | Stake funds |
| earn-deallocate --strategy-id ID --amount N --confirm | Unstake funds |

### Funding (auth required)

| Command | Description |
|---------|-------------|
| deposit-methods --asset BTC | Deposit methods for an asset |
| deposit-address --asset BTC | Get deposit address |
| withdraw --asset BTC --key NAME --amount N --confirm | Withdraw to saved address |
| withdraw-status | Recent withdrawal status |

**Withdrawal notes:**
- Addresses must be pre-configured in Kraken's web UI (can't add via API)
- Can't list saved address names via API — ask the user for the key name
- Addresses are per-asset: a SOL address won't work for USDC withdrawals even if it's the same wallet. Each asset needs its own entry.
- `--key` is the saved address name in Kraken, not the actual address

## Example Usage

| User Request | Command |
|---|---|
| What's my portfolio? | summary |
| BTC price? | ticker --pair XBTUSD |
| Export 2025 ledger for taxes | ledger --start 2025-01-01 --end 2025-12-31 --csv |
| Export trade history | trades --csv |
| Buy 0.1 BTC at market | buy --pair XBTUSD --type market --amount 0.1 --confirm |
| Show staking positions | earn-positions |

## Kraken Pair Naming

Kraken uses non-standard names: XBT (not BTC), XETH (not ETH), Z-prefix for fiat (ZUSD, ZCAD). When unsure of a pair name, run `pairs --json` and grep for the asset.

## Portfolio Logic

Kraken has two earn types:
- **Auto Earn (flex):** in main wallet, included in trade balance equity
- **Bonded staking:** separate earn wallet, NOT in trade balance

`summary` calculates: **Total = Trade Balance Equity + Bonded Staking Only**

## API Permissions

| Feature | Permission |
|---------|-----------|
| Balances, portfolio, ledger | Query Funds |
| Orders, trades (view) | Query Open/Closed Orders & Trades |
| Place/cancel orders | Create & Modify Orders |
| Earn allocate/deallocate | Withdraw Funds |
| Withdrawals | Withdraw Funds |
| Market data | None |
