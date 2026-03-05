# Testing (Paper Mode)

## Test Copy-Trade Engine using mock wallet events

1) Create a JSONL file, e.g. `mock_events.jsonl`:

```json
{"wallet":"WALLET_A","side":"BUY","mint":"<TOKEN_MINT>","ts":1700000000000,"priceRefUsd":0.0012}
{"wallet":"WALLET_A","side":"SELL","mint":"<TOKEN_MINT>","ts":1700000009999,"priceRefUsd":0.0018}
```

2) Run with env var:
```bash
export MOCK_WALLET_EVENTS_JSONL=./mock_events.jsonl
npm run dev -- --mode paper --minutes 10
```

The skill will apply:
- Delay (30–120s)
- Anti-chase (max 20%)
- Risk gate
- Extra copy filters (age, tx count)
- Then simulate BUY/SELL.
