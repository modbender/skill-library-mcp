# Crypto Data Sources

## Price & Market Data

| Source | Best For | Rate Limits | Auth |
|--------|----------|-------------|------|
| **CoinGecko** | Price, market cap, 24h volume | 10-50 req/min (free) | Optional API key |
| **CoinMarketCap** | Price, rankings, metadata | 333 req/day (free) | Required |
| **Binance API** | Real-time trading data, OHLCV | 1200 req/min | Optional |
| **TradingView** | Charts (embed only) | N/A | N/A |

### CoinGecko Quick Queries

```bash
# Current price
curl "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,eur"

# Historical (30 days)
curl "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"

# Token by contract
curl "https://api.coingecko.com/api/v3/coins/ethereum/contract/0x..."
```

---

## On-Chain Data

| Chain | Explorer | API |
|-------|----------|-----|
| Ethereum | Etherscan | `api.etherscan.io` |
| Base | Basescan | `api.basescan.org` |
| Arbitrum | Arbiscan | `api.arbiscan.io` |
| Polygon | Polygonscan | `api.polygonscan.com` |
| Solana | Solscan | `api.solscan.io` |
| BNB Chain | BscScan | `api.bscscan.com` |

### Common Explorer Queries

```bash
# Wallet balance
/api?module=account&action=balance&address=0x...

# Transaction list
/api?module=account&action=txlist&address=0x...&startblock=0&endblock=99999999

# Token transfers
/api?module=account&action=tokentx&address=0x...
```

---

## DeFi Data

| Source | Data Type | Best For |
|--------|-----------|----------|
| **DefiLlama** | TVL, protocols, yields | Protocol comparison, TVL tracking |
| **Dune Analytics** | Custom queries | On-chain analytics, dashboards |
| **The Graph** | Indexed data | DEX data, lending protocols |
| **DeFi Pulse** | TVL (Ethereum) | Historical TVL |

### DefiLlama Endpoints

```bash
# All protocols TVL
curl "https://api.llama.fi/protocols"

# Specific protocol
curl "https://api.llama.fi/protocol/uniswap"

# Chain TVL
curl "https://api.llama.fi/chains"

# Yields/APY
curl "https://yields.llama.fi/pools"
```

---

## Gas & Fees

| Source | Chains | Data |
|--------|--------|------|
| **Etherscan Gas Tracker** | ETH | Current gas, historical |
| **GasNow** (deprecated) | ETH | Was real-time, now alternatives |
| **Blocknative** | ETH, Polygon | Gas estimates |
| **L2Fees.info** | L2s | Compare rollup costs |

### Gas Monitoring

```bash
# Etherscan gas oracle
curl "https://api.etherscan.io/api?module=gastracker&action=gasoracle"
# Returns: SafeGasPrice, ProposeGasPrice, FastGasPrice
```

**Typical strategy:** Alert when gas < 20 gwei (Ethereum), execute batch operations during low periods.

---

## NFT Data

| Source | Marketplaces | Data |
|--------|--------------|------|
| **OpenSea API** | OpenSea | Floor, volume, listings |
| **Reservoir** | Multiple | Aggregated NFT data |
| **Blur** | Blur | Floor, bids |
| **Magic Eden** | Solana, multi | SOL NFT data |

---

## News & Sentiment

| Source | Type | Use |
|--------|------|-----|
| **CoinDesk** | News | Major events, institutional |
| **The Block** | News | Research, data journalism |
| **Decrypt** | News | Accessible explanations |
| **CryptoQuant** | On-chain | Whale movements, exchange flows |
| **Santiment** | Sentiment | Social volume, dev activity |

**Rule:** Stick to established sources. Avoid Twitter influencers, Telegram groups, Discord alphas for factual data.

---

## Real-Time Feeds

| Type | Sources |
|------|---------|
| **WebSocket prices** | Binance, Coinbase, Kraken |
| **Block events** | Alchemy, Infura, QuickNode |
| **Mempool** | Blocknative, Flashbots |

---

## Data Aggregation Strategy

1. **Primary:** CoinGecko (free, comprehensive)
2. **Backup:** CoinMarketCap (requires key)
3. **On-chain:** Chain-specific explorer APIs
4. **DeFi:** DefiLlama (no auth needed)
5. **Historical:** CoinGecko or exchange APIs (OHLCV)

**Rate limit handling:** Cache responses (5-15 min TTL for prices, 1h for metadata), exponential backoff on errors.
