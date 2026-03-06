# Exchange API Reference

## Binance

**API Base URL**: `https://api.binance.com`

**Price Endpoint**: `/api/v3/ticker/price?symbol=BTCUSDT`

**Response**:
```json
{
  "symbol": "BTCUSDT",
  "price": "68477.45000000"
}
```

**Trading Fee**: 0.1% (VIP levels available)

**Rate Limits**: 1200 requests/minute

---

## OKX

**API Base URL**: `https://www.okx.com`

**Price Endpoint**: `/api/v5/market/ticker?instId=BTC-USDT`

**Symbol Format**: `BTC-USDT` (with hyphen)

**Response**:
```json
{
  "code": "0",
  "data": [{
    "instId": "BTC-USDT",
    "last": "68481.3",
    "askPx": "68481.3",
    "bidPx": "68481.2"
  }]
}
```

**Trading Fee**: 0.08% (VIP levels available)

**Rate Limits**: 20 requests/2 seconds

---

## Gate.io

**API Base URL**: `https://api.gateio.ws`

**Price Endpoint**: `/api/v4/spot/tickers?currency_pair=BTC_USDT`

**Symbol Format**: `BTC_USDT` (with underscore)

**Response**:
```json
[{
  "currency_pair": "BTC_USDT",
  "last": "68482.9",
  "lowest_ask": "68483",
  "highest_bid": "68482.9"
}]
```

**Trading Fee**: 0.2%

**Rate Limits**: 900 requests/minute

---

## Huobi (火币)

**API Base URL**: `https://api.huobi.pro`

**Price Endpoint**: `/market/detail/merged?symbol=btcusdt`

**Symbol Format**: `btcusdt` (lowercase, no separator)

**Response**:
```json
{
  "tick": {
    "close": "68480.5",
    "open": "68650.3",
    "high": "70118",
    "low": "67288"
  }
}
```

**Trading Fee**: 0.2%

**Rate Limits**: 100 requests/10 seconds

---

## Fee Calculation

Total cost for cross-exchange arbitrage:

```
Total Fee = Buy Fee + Sell Fee + Withdrawal Fee

Example (BTCUSDT):
- Buy on Binance (0.1%)
- Sell on OKX (0.08%)
- Withdrawal: ~0.0005 BTC

Profit = (Sell Price - Buy Price) / Buy Price - Total Fee
```

## Tips

1. **Use stablecoins**: USDT/USDC have lower withdrawal fees than BTC/ETH
2. **Check withdrawal status**: Some exchanges pause withdrawals during maintenance
3. **Account for slippage**: Large orders may move the price
4. **Verify deposits**: Ensure destination exchange supports the token
