# Orders API Examples

## Good Example: Filtered Order Retrieval

```bash
curl "https://api.clawver.store/v1/orders?status=confirmed&limit=20" \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

Why this works: uses supported query filters and authenticated owner context.

## Good Example: Refund With Amount + Reason

```bash
curl -X POST https://api.clawver.store/v1/orders/{orderId}/refund \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"amountInCents":2499,"reason":"Customer requested refund"}'
```

Why this works: refund call includes required details for auditability.

## Bad Example: Public Download Without Token

```bash
curl "https://api.clawver.store/v1/orders/{orderId}/download/{itemId}/public"
```

Why it fails: public download endpoint requires `token`.

Fix: call with `?token={downloadToken}` from receipt/order context.

## Bad Example: Invalid Status Filter

```bash
curl "https://api.clawver.store/v1/orders?status=complete" \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

Why it fails: `complete` is not a documented order status and typically yields no matching results.

Fix: use `pending`, `confirmed`, `processing`, `shipped`, `delivered`, or `cancelled`.
