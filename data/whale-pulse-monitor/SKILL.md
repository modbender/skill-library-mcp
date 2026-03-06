---
name: whale-pulse-monitor
description: "Real-time BTC Orderbook Imbalance (OBI) tracking for professional traders. Detects high-conviction whale activity before it hits the tape. Powered by Sovereign-Futures logic."
metadata:
  {
    "openclaw": { "emoji": "🐋" },
    "author": "System Architect Zero",
    "x402": { "fee": 0.25, "currency": "USDC", "network": "base" }
  }
---

# Whale Pulse Monitor

Stop guessing. Start tracking the money. This skill provides direct access to the Sovereign-Futures OBI scanning engine, alerting you when a physical imbalance is detected on OKX/Binance.

## Features
- **Whale Fingerprinting**: Distinguishes between retail noise and institutional iceberg orders.
- **S-Level Alerts**: Triggers only when OBI > 5.0 for maximum conviction.
- **Low Latency**: Directly interfaced with the Rust-based market-cli.

## Usage
```bash
npx openclaw skill run whale-pulse-monitor
```

## Why it costs $0.25?
To filter out non-professional noise and maintain our high-performance infrastructure.
