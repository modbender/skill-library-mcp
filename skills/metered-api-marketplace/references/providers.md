# Payment provider adapters

The reference server implements a **normalized webhook**. Real providers differ.

## Recommended patterns

### Coinbase Commerce (implemented)
- Create a charge with `metadata.api_key=<key_id>`
- Coinbase sends webhook events to: `POST /v1/payments/webhook/coinbase-commerce`
- Verify with `X-CC-Webhook-Signature` using `COINBASE_COMMERCE_WEBHOOK_SECRET`
- Credits balance only on `charge:confirmed` / `charge:resolved`

### BTCPay Server (implemented)
- Create invoice with `metadata.api_key=<key_id>`
- BTCPay sends webhook events to: `POST /v1/payments/webhook/btcpay`
- Verify `BTCPay-Sig` using `BTCPAY_WEBHOOK_SECRET`
- Credits balance only on settled/completed/confirmed invoice events

### "Bring your own" wallet watcher
If you insist on direct-to-wallet deposits:
- you need unique deposit addresses per customer (HD wallet) OR memo/tag handling
- you need a chain indexer to detect deposits + confirmations

In most cases, use Coinbase/BTCPay to avoid building custody + chain monitoring.
