# Crypto Utilities & Calculations

## Unit Conversions

### Ethereum Units
| Unit | Wei | Common Use |
|------|-----|------------|
| Wei | 1 | Smallest unit |
| Gwei | 10^9 | Gas prices |
| Ether | 10^18 | Balances, transfers |

```javascript
// Conversions
const ethToWei = eth => eth * 1e18
const weiToEth = wei => wei / 1e18
const gweiToEth = gwei => gwei / 1e9
const ethToGwei = eth => eth * 1e9
```

### Common Decimals by Token
| Token | Decimals | 1 Token in Smallest Unit |
|-------|----------|--------------------------|
| ETH | 18 | 1,000,000,000,000,000,000 |
| USDC | 6 | 1,000,000 |
| USDT | 6 | 1,000,000 |
| WBTC | 8 | 100,000,000 |
| DAI | 18 | 1,000,000,000,000,000,000 |

**Critical:** Always check decimals before calculations. USDC/USDT (6) vs DAI (18) causes bugs.

---

## Gas Cost Calculations

```
Transaction Cost = Gas Used × Gas Price (in Gwei) × ETH Price

Example:
- Gas used: 21,000 (simple transfer)
- Gas price: 30 gwei
- ETH price: $2,500

Cost = 21,000 × 30 × 10^-9 × 2500 = $1.58
```

### Typical Gas Usage
| Action | Gas Units |
|--------|-----------|
| ETH transfer | 21,000 |
| ERC-20 transfer | 65,000 |
| Uniswap swap | 150,000-300,000 |
| NFT mint | 100,000-200,000 |
| Contract deploy | 1,000,000+ |

---

## Portfolio Calculations

### Cost Basis (FIFO)
```
Buy 1 BTC @ $30,000
Buy 1 BTC @ $40,000
Sell 1 BTC @ $50,000

FIFO gain: $50,000 - $30,000 = $20,000
(First in, first out — sold the $30k one)
```

### Average Cost Basis
```
Buy 1 BTC @ $30,000
Buy 1 BTC @ $40,000
Total: 2 BTC for $70,000
Average: $35,000 per BTC
```

### ROI (Return on Investment)
```
ROI = (Current Value - Total Invested) / Total Invested × 100

Example:
Invested: $10,000
Current: $15,000
ROI = ($15,000 - $10,000) / $10,000 × 100 = 50%
```

### Unrealized vs Realized
- **Unrealized:** Paper gains/losses (haven't sold)
- **Realized:** Actual gains/losses (have sold)

Only realized matters for taxes.

---

## DCA (Dollar Cost Averaging) Tracking

```
Monthly $100 BTC purchase:
- Jan: 0.003 BTC @ $33,333
- Feb: 0.004 BTC @ $25,000
- Mar: 0.0025 BTC @ $40,000

Total: 0.0095 BTC for $300
Average price: $31,579 per BTC
```

---

## Address Validation

### Ethereum/EVM
- 42 characters (0x + 40 hex)
- Checksum: mixed case encodes checksum
- Example: `0x742d35Cc6634C0532925a3b844Bc9e7595f4A9A1`

### Bitcoin
- Legacy (P2PKH): Starts with 1, 26-35 chars
- SegWit (P2SH): Starts with 3
- Native SegWit: Starts with bc1

### Solana
- Base58, 32-44 characters
- Example: `7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU`

**Never:** Send to wrong chain address (BTC to ETH address = lost)

---

## Quick Formulas

### Market Cap
```
Market Cap = Circulating Supply × Price
FDV (Fully Diluted) = Max Supply × Price
```

### Liquidity Depth
```
If pool has $1M liquidity:
- $10k trade: ~1% slippage
- $100k trade: ~10% slippage
- $500k trade: ~50% slippage (don't)
```

### APY vs APR
```
APR = Simple interest
APY = Compound interest

APY = (1 + APR/n)^n - 1
where n = compounding periods per year

Example: 10% APR compounded daily
APY = (1 + 0.10/365)^365 - 1 = 10.52%
```

---

## Transaction CSV Export Format

For tax purposes, export with these columns:

```csv
Date,Type,Asset,Amount,Price_USD,Fee_USD,Exchange,TxHash
2025-01-15,BUY,BTC,0.5,25000,5,Coinbase,0x...
2025-02-01,SELL,ETH,2.0,2400,3,Kraken,0x...
2025-03-10,TRANSFER,BTC,0.5,0,2,Ledger→Binance,0x...
```

**Types:** BUY, SELL, TRANSFER, RECEIVE, SEND, SWAP, STAKE, UNSTAKE, REWARD

---

## Useful Online Tools

| Tool | Purpose | URL |
|------|---------|-----|
| **Revoke.cash** | Manage approvals | revoke.cash |
| **Debank** | Portfolio tracking | debank.com |
| **Zerion** | Multi-chain portfolio | zerion.io |
| **Zapper** | DeFi positions | zapper.xyz |
| **Koinly** | Tax reporting | koinly.io |
| **CoinTracker** | Tax reporting | cointracker.io |
