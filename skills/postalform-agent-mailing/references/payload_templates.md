# Payload Templates

## 1-page manual-address payload (JSON)

Use this as a starting point. Replace names, email, and PDF data.

```json
{
  "request_id": "6b4c4a92-41d1-4ce4-9d65-7df97027f4db",
  "buyer_name": "Agent Owner",
  "buyer_email": "owner@example.com",
  "pdf": "data:application/pdf;base64,<BASE64_PDF>",
  "file_name": "one-page-test.pdf",
  "sender_name": "Sender Example",
  "sender_address_type": "Manual",
  "sender_address_manual": {
    "line1": "1 Apple Park Way",
    "city": "Cupertino",
    "state": "CA",
    "zip": "95014"
  },
  "recipient_name": "Recipient Example",
  "recipient_address_type": "Manual",
  "recipient_address_manual": {
    "line1": "1600 Amphitheatre Parkway",
    "city": "Mountain View",
    "state": "CA",
    "zip": "94043"
  },
  "double_sided": false,
  "color": false,
  "mail_class": "standard",
  "certified": false
}
```

## Validate first

```bash
curl -sS -X POST "https://postalform.com/api/machine/orders/validate" \
  -H "content-type: application/json" \
  --data @payload.json
```

Check:
- `quote.page_count` matches expected pages
- `quote.price_usd` is acceptable
- no `errors[]`

## Pay with purl (optional)

`purl` is one client option, not a protocol requirement.

```bash
purl \
  --wallet ~/.purl/keystores/my-wallet.json \
  --password "$PURL_PASSWORD" \
  --network eip155:8453 \
  --max-amount 5000000 \
  --output-format json \
  -X POST \
  --json "$(cat payload.json)" \
  "https://postalform.com/api/machine/orders"
```

Notes:
- Use a wallet alias or keystore if available (`purl wallet list`, `purl wallet use <name>`).
- Match `--network` to `PAYMENT-REQUIRED`.
- Keep payload identical across `402` retry.

## Pay without purl (generic x402)

Use any x402-compliant wallet client:

1. `POST /api/machine/orders` without payment signature.
2. Parse `PAYMENT-REQUIRED`.
3. Create payment payload on requested network/token.
4. Retry same request body with `PAYMENT-SIGNATURE`.
5. Read `PAYMENT-RESPONSE` / response body.

## Poll status

```bash
curl -sS "https://postalform.com/api/machine/orders/<request_id>"
```

Done state:
- `is_paid: true`
- `current_step` advanced (often `email_sent`)
- `order_complete_url` is a URL

Transient state:
- `status: "settled_pending_webhook"` can appear before paid webhook reconciliation.
