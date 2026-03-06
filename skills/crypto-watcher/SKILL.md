---
name: crypto-watcher
description: Monitor crypto wallets and DeFi positions. Get alerts when things change.
---

# crypto-watcher

Monitor crypto wallets and DeFi positions. Get alerts when things change.

## Features

- **Wallet tracking**: ETH + token balances across chains
- **DeFi positions**: LP positions, lending health, staking rewards
- **Gas alerts**: Notify when gas is cheap for transactions
- **Whale alerts**: Large transfers on watched tokens

## Usage

### Setup
```bash
# Add a wallet to watch
crypto-watcher add 0x1234...abcd --name "main" --chains eth,arb,base

# Configure alerts
crypto-watcher config --gas-alert 20 --balance-change 5%
```

### Commands
```bash
# Check all positions
crypto-watcher status

# Check specific wallet
crypto-watcher status main

# Gas prices
crypto-watcher gas

# DeFi positions (via DefiLlama)
crypto-watcher defi 0x1234...abcd
```

### Heartbeat Integration

Add to HEARTBEAT.md:
```markdown
### Crypto Check
- Run `crypto-watcher status --quiet` 
- Alert if any position health < 1.5 or balance dropped > 10%
- Check gas, alert if < 15 gwei (good time for L1 txs)
```

## Config

`~/.config/crypto-watcher/config.json`:
```json
{
  "wallets": [
    {
      "address": "0x...",
      "name": "main",
      "chains": ["eth", "arb", "base"]
    }
  ],
  "alerts": {
    "gasThreshold": 20,
    "balanceChangePercent": 5,
    "healthFactorMin": 1.5
  }
}
```

## Data Sources

- **Balances**: Public RPCs (no API key needed)
- **DeFi**: DefiLlama API (free)
- **Gas**: eth_gasPrice RPC call
- **Prices**: CoinGecko API (free tier)

## Chains Supported

| Chain | ID | RPC |
|-------|-----|-----|
| Ethereum | eth | https://eth.llamarpc.com |
| Arbitrum | arb | https://arb1.arbitrum.io/rpc |
| Base | base | https://mainnet.base.org |
| Optimism | op | https://mainnet.optimism.io |
| Polygon | matic | https://polygon-rpc.com |
