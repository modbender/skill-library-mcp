---
name: zinc-orders
description: Place, list, and retrieve orders via the Zinc API (zinc.com). Use when the user wants to buy a product from an online retailer, check order status, list recent orders, or anything involving the Zinc e-commerce ordering API. Requires ZINC_API_KEY environment variable.
---

# Zinc Orders

Place and manage orders on online retailers through the Zinc API (`https://api.zinc.com`).

## Prerequisites

- `ZINC_API_KEY` env var must be set. Get one from <https://app.zinc.com>.

## Authentication

All requests use Bearer token auth:

```
Authorization: Bearer $ZINC_API_KEY
```

## Endpoints

### Create Order — `POST /orders`

Place a new order. Orders process asynchronously.

**Required fields:**

- `products` — array of `{ url, quantity?, variant? }` objects
  - `url`: direct product page URL on a supported retailer
  - `quantity`: integer (default 1)
  - `variant`: array of `{ label, value }` for size/color/etc.
- `shipping_address` — object with `first_name`, `last_name`, `address_line1`, `address_line2`, `city`, `state` (2-letter), `postal_code`, `phone_number`, `country` (ISO alpha-2, e.g. "US")
- `max_price` — integer, maximum price **in cents**

**Optional fields:**

- `idempotency_key` — string (max 36 chars) to prevent duplicates
- `retailer_credentials_id` — short ID like `zn_acct_XXXXXXXX`
- `metadata` — arbitrary key-value object
- `po_number` — purchase order number string

**Response:** order object with `id` (UUID), `status`, `items`, `shipping_address`, `created_at`, `tracking_numbers`, etc.

**Order statuses:** `pending` → `in_progress` → `order_placed` | `order_failed` | `cancelled`

### List Orders — `GET /orders`

Returns `{ orders: [...] }` array of order objects.

### Get Order — `GET /orders/{id}`

Retrieve a single order by UUID.

## Example: Place an Order

```bash
curl -X POST https://api.zinc.com/orders \
  -H "Authorization: Bearer $ZINC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "products": [{ "url": "https://example.com/product", "quantity": 1 }],
    "max_price": 5000,
    "shipping_address": {
      "first_name": "Jane",
      "last_name": "Doe",
      "address_line1": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "postal_code": "94105",
      "phone_number": "5551234567",
      "country": "US"
    }
  }'
```

## Error Handling

See [references/errors.md](references/errors.md) for the full error code reference.

Key points:

- HTTP errors return `{ code, message, details }`
- Order processing failures appear in webhook/order response as `error_type`
- Common issues: `max_price_exceeded`, `product_out_of_stock`, `invalid_shipping_address`

## Order Status Tracking

Orders process asynchronously and typically take **5–10 minutes**. After placing an order:

1. Schedule a cron job to check the order status ~7 minutes after creation.
2. Use `GET /orders/{id}` to poll.
3. Report the result back to the user in the same channel.
4. If still pending/in_progress, schedule another check in 5 minutes.

**Terminal statuses:** `order_placed`, `order_failed`, `cancelled` — stop polling.
**Non-terminal:** `pending`, `in_progress` — schedule another check in 3–5 minutes.

Example cron job (isolated, announce back to the channel):

```json
{
  "name": "zinc-order-check-<short_id>",
  "schedule": { "kind": "at", "at": "<ISO-8601 ~7min from now>" },
  "payload": {
    "kind": "agentTurn",
    "message": "Check Zinc order <order_id> via GET https://api.zinc.com/orders/<order_id>"
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce",
    "channel": "<channel>",
    "to": "<channel_id>"
  }
}
```

## Safety

- **Always confirm with the user** before placing an order (`POST /orders`). This spends real money.
- Reading orders (GET) is always safe.
- Validate that `max_price` is reasonable before submitting.
