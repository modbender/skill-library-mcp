---
name: groww
description: Trade stocks and manage portfolio on Groww (Indian broker). Use when user asks about Indian stocks, NSE/BSE prices, portfolio holdings, placing buy/sell orders, checking order status, or any Groww-related trading queries. Supports live quotes, LTP, OHLC, historical candles, and order management.
---

# Groww Trading

Trade Indian stocks via Groww. Supports portfolio management, market data, and order execution.

## Setup

1. Get API key from Groww app: Stocks → Settings → API Trading → Generate API key
2. Add to OpenClaw config:
   ```bash
   openclaw configure
   # Add env: GROWW_API_KEY=your_key_here
   ```

## MCP Server Usage

The groww-mcp server is configured. Call tools via mcporter:

```bash
# Portfolio
mcporter call groww-mcp.portfolio

# Market data
mcporter call groww-mcp.market-data action=live-quote symbol=TATAMOTORS
mcporter call groww-mcp.market-data action=ltp symbols=TATAMOTORS,RELIANCE
mcporter call groww-mcp.market-data action=ohlc symbol=TCS

# Orders
mcporter call groww-mcp.place_order symbol=TATAMOTORS quantity=10 side=BUY type=MARKET
mcporter call groww-mcp.order_status orderId=ABC123
mcporter call groww-mcp.cancel_order orderId=ABC123
```

## Direct API (Alternative)

If MCP has issues, use the Groww API directly:

### Base URL
```
https://api.groww.in/v1/
```

### Headers
```bash
Authorization: Bearer $GROWW_API_KEY
Accept: application/json
Content-Type: application/json
```

### Endpoints

**Portfolio/Holdings:**
```bash
curl -H "Authorization: Bearer $GROWW_API_KEY" -H "Accept: application/json" \
  "https://api.groww.in/v1/holdings/user"
```

**Live Quote:**
```bash
curl -H "Authorization: Bearer $GROWW_API_KEY" -H "Accept: application/json" \
  "https://api.groww.in/v1/live-data/quote?exchange=NSE&segment=CASH&trading_symbol=TATAMOTORS"
```

**LTP (Last Traded Price):**
```bash
curl -H "Authorization: Bearer $GROWW_API_KEY" -H "Accept: application/json" \
  "https://api.groww.in/v1/live-data/ltp?segment=CASH&exchange_symbols=NSE:TATAMOTORS,NSE:RELIANCE"
```

**OHLC:**
```bash
curl -H "Authorization: Bearer $GROWW_API_KEY" -H "Accept: application/json" \
  "https://api.groww.in/v1/live-data/ohlc?segment=CASH&exchange_symbols=NSE:TATAMOTORS"
```

**Historical Candles:**
```bash
curl -H "Authorization: Bearer $GROWW_API_KEY" -H "Accept: application/json" \
  "https://api.groww.in/v1/historical/candle/range?exchange=NSE&segment=CASH&trading_symbol=TATAMOTORS&interval=5m&start_time=2024-06-01T09:15:00&end_time=2024-06-01T15:30:00"
```

**Place Order:**
```bash
curl -X POST -H "Authorization: Bearer $GROWW_API_KEY" \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -d '{"trading_symbol":"TATAMOTORS","quantity":10,"validity":"DAY","exchange":"NSE","segment":"CASH","product":"CNC","order_type":"MARKET","transaction_type":"BUY"}' \
  "https://api.groww.in/v1/order/create"
```

**Order Status:**
```bash
curl -H "Authorization: Bearer $GROWW_API_KEY" -H "Accept: application/json" \
  "https://api.groww.in/v1/order/detail/{groww_order_id}?segment=CASH"
```

**Cancel Order:**
```bash
curl -X POST -H "Authorization: Bearer $GROWW_API_KEY" \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -d '{"segment":"CASH","groww_order_id":"ABC123"}' \
  "https://api.groww.in/v1/order/cancel"
```

## Stock Symbols

Use NSE trading symbols:
- TATAMOTORS, RELIANCE, TCS, INFY, HDFCBANK
- WIPRO, ICICIBANK, SBIN, BHARTIARTL, ITC

## Market Hours

- Pre-open: 9:00 - 9:15 AM IST
- Trading: 9:15 AM - 3:30 PM IST
- Monday to Friday (except holidays)

## Example Queries

- "Show my Groww portfolio"
- "What's TATAMOTORS price?"
- "Buy 10 RELIANCE shares"
- "Sell 5 TCS at limit 4200"
- "Cancel order ABC123"
- "Get historical data for INFY"
