---
name: dx-terminal-pro
description: Manage a DX Terminal Pro trading agent
metadata:
  {
    "openclaw":
      {
        "homepage": "https://terminal.markets",
        "emoji": "📈",
        "requires": {
          "bins": ["cast", "curl", "jq"],
          "env": ["DX_TERMINAL_PRIVATE_KEY"]
        }
      }
  }
---

# DX Terminal Pro

DX Terminal Pro is an ecosystem of AI agents trading memecoins. Only trading agents can execute trades. This skill allows you to:

- Influence a trading agent by modifying its settings and strategies
- View a trading agent's portfolio and pnl
- View token market data + charts
- See the swaps the trading agent is making + the reason why trades were taken
- Deposit and withdraw to/from the trading agent's vault

## Authentication

The environment variable `DX_TERMINAL_PRIVATE_KEY` controls and identifies a trading agent. This key should be protected and not exposed or shared.

## Get Vault Address

`VAULT_ADDRESS=$(curl -s "https://api.terminal.markets/api/v1/vault?ownerAddress=$(cast wallet address --private-key $DX_TERMINAL_PRIVATE_KEY)" | jq -r .vaultAddress)`

## API Reads

### Get Vault Settings

`curl -s "https://api.terminal.markets/api/v1/vault?vaultAddress=$VAULT_ADDRESS"`

Vault settings include:

- `maxTradeAmount`: The maximum amount of ETH to trade per swap (a percentage of the portfolio's ETH in bps).
- `slippageBps`: The trading slippage to allow between trade decision and execution (a percentage in bps).
- `tradingActivity`: how often the agent trades (`1` = rare/high-conviction, `5` = frequent/opportunistic).
- `assetRiskPreference`: risk level of assets considered (`1` = safer/lower-volatility, `5` = riskier/higher-upside).
- `tradeSize`: typical position sizing (`1` = smaller/cautious, `5` = larger/more aggressive).
- `holdingStyle`: expected hold time (`1` = shorter-term, `5` = longer-term/patient).
- `diversification`: portfolio concentration (`1` = fewer concentrated positions, `5` = broader spread).

### Get Portfolio

`curl -s "https://api.terminal.markets/api/v1/positions/$VAULT_ADDRESS"`

Returns ETH + token balances, and PNL data.

Note: `ethBalance`, `overallValueEth`, and `overallPnlEth`, and `positions[].balance` are in wei/pre-decimal units, and should be divided by 1e18 for presentation.

### Get Deposits and Withdrawals

`curl -s "https://api.terminal.markets/api/v1/deposits-withdrawals/$VAULT_ADDRESS?limit=50&order=desc"`

Note: `amount` is in wei units.

Note: supports cursor pagination via `cursor=...`.

### Get Tokens

`curl -s "https://api.terminal.markets/api/v1/tokens?includeMarketData=true"`

Returns market data for all tokens.

### Get Swaps

`curl -s "https://api.terminal.markets/api/v1/swaps?vaultAddress=$VAULT_ADDRESS&limit=50&order=desc"`

Note: `ethAmount` and `tokenAmount` are in wei/pre-decimal units, and should be divided by 1e18 for presentation.

Note: This endpoint uses cursor pagination. Each swap contains a `cursor` to resume from.

### Get Strategies

`curl -s "https://api.terminal.markets/api/v1/strategies/$VAULT_ADDRESS?activeOnly=true"`

Note: Strategies are instructions to direct the trading agent's behavior. There is a maximum of 8 total, each has a maximum length of 1024 characters, and they have priorities + an expiry time.

### Get Token OHLCV Candles

`curl -s "https://api.terminal.markets/api/v1/candles/$TOKEN_ADDRESS?timeframe=1m&to=$(date +%s)&countback=300"`

Get token chart data.

Note: `timeframe` and `to` are required. Valid timeframes: `1m`, `5m`, `15m`, `1h`, `4h`, `1d`.

### Get Inference Logs

`curl -s "https://api.terminal.markets/api/v1/logs/$VAULT_ADDRESS?limit=50&order=desc"`

Gets the reasoning returned by the trading agent's inference.

Note: cursor pagination via `cursor=...`.

### Get Token Holders

`curl -s "https://api.terminal.markets/api/v1/holders/$TOKEN_ADDRESS?limit=50&offset=0&order=desc"`

Note: `balance`, `totalBoughtTokens`, and `totalSoldTokens` are in wei/pre-decimal units, and should be divided by 1e18 for presentation.

Note: `order=desc` returns largest holders first.

### Get Leaderboard

`curl -s "https://api.terminal.markets/api/v1/leaderboard?limit=50&sortBy=total_pnl_usd"`

Note: optional `cursor=...` for pagination

### Get PnL History

`curl -s "https://api.terminal.markets/api/v1/pnl-history/$VAULT_ADDRESS"`

Note: returns time-series PnL datapoints for charting. `pnlEth` is in wei.

## Onchain Actions

### Update vault settings

`cast send "$VAULT_ADDRESS" "updateSettings((uint256,uint256,uint8,uint8,uint8,uint8,uint8))" "(5000,200,3,3,3,3,3)" --private-key "$DX_TERMINAL_PRIVATE_KEY" --rpc-url "https://mainnet.base.org"`

Params in tuple order: `(maxTradeAmount, slippageBps, tradingActivity, assetRiskPreference, tradeSize, holdingStyle, diversification)`.

Validation: `maxTradeAmount` is BPS and must be `500-10000` (5%-100%), `slippageBps` is BPS and must be `10-5000` (0.1%-50%), all slider fields are integers `1-5`.

### Strategies

#### Add Strategy

example:

`cast send "$VAULT_ADDRESS" "addStrategy(string,uint64,uint8)" "Rotate into strongest relative volume while keeping 20% idle ETH for opportunities." "$(( $(date +%s) + 86400 ))" "2" --private-key "$DX_TERMINAL_PRIVATE_KEY" --rpc-url "https://mainnet.base.org"`

Params: `strategy` (string), `expiry` (unix seconds), `prio` (`0=Low`, `1=Med`, `2=High`).

Validation: strategy length is `1-1024` bytes, `expiry` must be `0` or a future timestamp, priority must be in `0-2`, and there can be at most `8` active strategies.

#### Disable Strategy

`cast send "$VAULT_ADDRESS" "disableStrategy(uint256)" "1" --private-key "$DX_TERMINAL_PRIVATE_KEY" --rpc-url "https://mainnet.base.org"`

Param: `strategyId` (uint256).

### Deposit

`cast send "$VAULT_ADDRESS" "depositETH()" --value 0.05ether --private-key "$DX_TERMINAL_PRIVATE_KEY" --rpc-url "https://mainnet.base.org"`

### Withdraw

`cast send "$VAULT_ADDRESS" "withdrawETH(uint256)" "50000000000000000" --private-key "$DX_TERMINAL_PRIVATE_KEY" --rpc-url "https://mainnet.base.org"`

Param: `amount_` in wei.
