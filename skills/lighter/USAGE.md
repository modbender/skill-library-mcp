# Lighter v2 Usage (Direct Mainnet API)

This usage guide intentionally targets **Lighter native mainnet endpoints** directly.

- Base URL: `https://mainnet.zklighter.elliot.ai`
- API prefix: `/api/v1`

---

## Environment

```bash
export LIGHTER_API_KEY="..."
export LIGHTER_ACCOUNT_INDEX="..."
export LIGHTER_L1_ADDRESS="0x..."   # optional
```

---

## Read-only (safe by default)

### 1) List all order books
```bash
curl "https://mainnet.zklighter.elliot.ai/api/v1/orderBooks"
```

### 2) Get one market order book (ETH-USD usually `market_id=1`)
```bash
curl "https://mainnet.zklighter.elliot.ai/api/v1/orderBook?market_id=1"
```

### 3) Get recent trades for a market
```bash
curl "https://mainnet.zklighter.elliot.ai/api/v1/trades?market_id=1"
```

### 4) Resolve account index by L1 address
```bash
curl "https://mainnet.zklighter.elliot.ai/api/v1/accountsByL1Address?l1_address=$LIGHTER_L1_ADDRESS"
```

---

## Authenticated account queries

### 5) Account by index
```bash
curl -H "x-api-key: $LIGHTER_API_KEY" \
  "https://mainnet.zklighter.elliot.ai/api/v1/account?by=index&value=$LIGHTER_ACCOUNT_INDEX"
```

### 6) API key metadata (if enabled on account)
```bash
curl -H "x-api-key: $LIGHTER_API_KEY" \
  "https://mainnet.zklighter.elliot.ai/api/v1/apikeys?account_index=$LIGHTER_ACCOUNT_INDEX&api_key_index=255"
```

---

## Operator flows via curl only (no `/lighter` calls)

### Status / markets / risk context
```bash
# order books snapshot (market depth)
curl "https://mainnet.zklighter.elliot.ai/api/v1/orderBooks"

# account snapshot by index
curl -H "x-api-key: $LIGHTER_API_KEY" \
  "https://mainnet.zklighter.elliot.ai/api/v1/account?by=index&value=$LIGHTER_ACCOUNT_INDEX"

# open orders (if endpoint available in your account tier)
curl -H "x-api-key: $LIGHTER_API_KEY" \
  "https://mainnet.zklighter.elliot.ai/api/v1/orders?account_index=$LIGHTER_ACCOUNT_INDEX"
```

### Pre-trade simulation pattern (local calc + market data)
```bash
# pull order book for target market
curl "https://mainnet.zklighter.elliot.ai/api/v1/orderBook?market_id=1"
# then compute expected fill/slippage client-side before signing/sending tx
```

### Order execution pattern (signed tx via SDK)
```bash
# 1) get next nonce
curl -H "x-api-key: $LIGHTER_API_KEY" \
  "https://mainnet.zklighter.elliot.ai/api/v1/nextNonce?account_index=$LIGHTER_ACCOUNT_INDEX&api_key_index=3"

# 2) sign transaction locally (lighter-python SignerClient)
# 3) broadcast signed tx
curl -X POST "https://mainnet.zklighter.elliot.ai/api/v1/sendTx" \
  -H "x-api-key: $LIGHTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"tx":"<signed_tx_payload>"}'
```

---

## Security notes

- Read-only calls first; simulate before any live order.
- Keep `confirm=true` mandatory for execution paths.
- Store keys only in `~/.openclaw/secrets.env`.
- Never echo or log private keys.

---

## Reference docs

- Lighter API docs: https://apidocs.lighter.xyz/docs/get-started-for-programmers-1
- Mainnet endpoint: https://mainnet.zklighter.elliot.ai
- SDK repo: https://github.com/elliottech/lighter-python
