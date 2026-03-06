# Zinc API Error Reference

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 402 | Payment Required |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict (duplicate) |
| 422 | Validation error |
| 500 | Internal Server Error |
| 502 | Bad Gateway |

## Error Response Format

```json
{ "code": "error_code", "message": "Human-readable message", "details": { "field": "context" } }
```

## API Error Codes

### General
- `not_found` — Resource not found
- `validation_error` — Bad/missing parameter (check `details`)
- `bad_request` — Malformed request
- `already_exists` — Duplicate (e.g. idempotency key)
- `internal_error` — Server-side issue

### Authentication
- `unauthorized`, `forbidden`, `invalid_token`, `token_expired`

### Wallet & Payment
- `insufficient_funds` — Low wallet balance (details include `required`/`available` in cents)
- `payment_failed`, `payment_method_required`, `invalid_payment_method`

### Order Request
- `invalid_shipping_address` — Address validation failed
- `url_unreachable` — Product URL inaccessible
- `invalid_variant` — Variant not found
- `out_of_stock`, `shipping_unavailable`, `non_us_retailer`, `order_not_cancellable`

### External
- `external_service_error`

## Order Processing Error Types

These appear in `error_type` field on failed orders:

### Product
`product_not_found`, `product_out_of_stock`, `product_unavailable`, `invalid_product_url`, `product_variant_required`, `product_variant_unavailable`, `product_quantity_unavailable`

### Price
`max_price_exceeded`

### Cart & Checkout
`add_to_cart_failed`, `cart_empty`, `checkout_blocked`, `checkout_failed`

### Shipping
`shipping_address_invalid`, `shipping_unavailable`, `shipping_method_unavailable`

### Payment
`payment_declined`, `payment_method_invalid`, `payment_failed`

### Account
`login_failed`, `session_expired`, `account_locked`, `account_verification_required`

### Retailer
`retailer_unavailable`, `retailer_not_supported`, `retailer_rate_limited`

### Quantity
`quantity_limit_exceeded`, `order_limit_exceeded`
