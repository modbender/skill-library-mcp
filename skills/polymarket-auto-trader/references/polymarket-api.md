# Polymarket API Reference

## Endpoints

| Service | Base URL |
|---------|----------|
| CLOB API | `https://clob.polymarket.com` |
| Gamma API (markets) | `https://gamma-api.polymarket.com` |

## Authentication

1. Derive API key from wallet private key:
```python
from py_clob_client.client import ClobClient
client = ClobClient("https://clob.polymarket.com", key=PRIVATE_KEY, chain_id=137, signature_type=0)
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)
```

**Critical:** Use `signature_type=0` (EOA). Type 2 (proxy) gives "invalid signature" errors.

## Market Discovery

```
GET https://gamma-api.polymarket.com/markets?limit=100&offset=0&active=true&closed=false
```

Response fields:
- `question` — Market question
- `description` — Detailed description
- `outcomePrices` — JSON array `["0.65", "0.35"]` (YES/NO)
- `clobTokenIds` — JSON array of token IDs for YES/NO
- `volume` — Total volume traded
- `endDate` — Market resolution date

## Order Placement

```python
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

order_args = OrderArgs(token_id=token_id, price=0.45, size=10.0, side=BUY)
signed = client.create_order(order_args)
resp = client.post_order(signed, OrderType.GTC)
```

## Order Management

```python
# Get open orders
orders = client.get_orders()

# Cancel order
client.cancel(order_id="0x...")
```

## Constraints

- **Minimum order: 5 shares**
- **Minimum marketable order: $1**
- Price: 0.01 to 0.99, 2 decimal places
- US IPs blocked (403 Forbidden)

## Fee Structure

- Maker: 0% (limit orders that add liquidity)
- Taker: varies by market (typically 1-2%)
- Check: `GET /fee-rate?token_id=<id>`
