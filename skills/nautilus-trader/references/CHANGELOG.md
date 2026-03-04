# Changelog

## [1.0.0] - 2025-01-30

Initial public release.

### What Works
- Market orders via LIMIT IOC with 3% slippage
- Limit orders (GTC)
- Reduce-only orders
- 5 significant figure price formatting
- Mainnet trading

### Known Limitations
- No cancel order support (use Hyperliquid SDK directly)
- No position sync on reconnect
- WebSocket events not patched (data client unchanged)

### Tested Configuration
- Nautilus Trader v1.222.0
- Python 3.13
- hyperliquid-python-sdk 0.10.x
- AWS ap-northeast-1 (Tokyo) - 28ms API latency

### Previous Iterations
Versions 1-35 were internal development iterations fixing:
- Rust serialization bugs
- Price precision (sig fig calculation)
- Order type handling
- Response parsing
- Error propagation
