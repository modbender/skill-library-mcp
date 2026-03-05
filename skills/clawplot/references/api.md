# ClawPlot API Reference

Base URL: `https://clawplot.com`

## GET /api/catalog

Returns all available options, current pricing, and payment methods.

**Response:** JSON object with `sizes`, `papers`, `inks`, `options`, `payment_methods`, and `submission` fields.

No authentication required. Cache for up to 1 hour.

## POST /api/order

Create a new plot order.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| svg | string | Valid SVG 1.1 markup (max 500KB) |
| size | string | One of: `6x8`, `9x12`, `11x14`, `19x24` |
| paper | string | One of: `white`, `black`, `natural` |
| ink | string[] | Array of ink colors: `black`, `white`, `silver`, `gold`, `blue`, `red` |
| payment_method | string | One of: `stripe`, `usdc_solana`, `usdc_base` |
| shipping | object | Shipping address (see below) |

**Shipping object:**

| Field | Type | Required |
|-------|------|----------|
| name | string | yes |
| address | string | yes |
| city | string | yes |
| state | string | yes (use province/region for non-US) |
| zip | string | yes |
| country | string | yes (2-letter ISO code) |

**Optional fields:**

| Field | Type | Description |
|-------|------|-------------|
| copies | number | Number of copies (default: 1) |
| multipen | boolean | Use multiple ink colors (adds $25) |

**Success response (200):**

```json
{
  "order_id": "plt_abc123",
  "status": "pending_payment",
  "total_usd": 95,
  "payment": {
    "method": "stripe",
    "checkout_url": "https://checkout.stripe.com/..."
  }
}
```

**For crypto payments**, the response includes `wallet_address` and `amount_usdc` instead of `checkout_url`.

**Error response (400):**

```json
{
  "error": "Validation failed",
  "details": ["Invalid size: 10x10. Valid: 6x8, 9x12, 11x14, 14x17, 19x24"]
}
```

## GET /api/status?id=plt_xxx

Check order status.

**Response:**

```json
{
  "order_id": "plt_abc123",
  "status": "plotting",
  "created_at": "2026-02-16T12:00:00Z",
  "estimated_ship_date": "2026-02-21"
}
```

**Statuses:** `pending_payment` → `queued` → `plotting` → `quality_check` → `shipped` → `delivered` | `cancelled` | `refunded`

## POST /api/create-checkout-session

Alternative Stripe-only checkout. Simpler for agents that just want a payment link.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| size | string | Size code |
| paper | string | Paper type |
| ink | string | Ink color |
| addons | string[] | Optional: `["multicolor"]` |

**Response:**

```json
{
  "success": true,
  "url": "https://checkout.stripe.com/...",
  "session_id": "cs_...",
  "amount_total": 9500
}
```

## Rate Limits

- 100 requests per 60-second window per IP
- Catalog endpoint: cache-friendly, prefer caching responses

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid request / validation error |
| 405 | Wrong HTTP method |
| 429 | Rate limited |
| 500 | Server error |
| 503 | Service temporarily unavailable |
