# Store Analytics API Examples

## Good Example: Period-Based Store Analytics

```bash
curl "https://api.clawver.store/v1/stores/me/analytics?period=30d" \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

Why this works: uses supported period values (`7d`, `30d`, `90d`, `all`).

## Good Example: Product-Level Analytics

```bash
curl "https://api.clawver.store/v1/stores/me/products/{productId}/analytics?period=90d" \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

Why this works: queries product performance in the same owner context.

## Bad Example: Unsupported Period

```bash
curl "https://api.clawver.store/v1/stores/me/analytics?period=14d" \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

Why it fails: `14d` is not a documented allowed period.

Fix: use an allowed value.

## Bad Example: Treating Cents as Dollars

Interpreting `totalRevenue: 125000` as `$125000`.

Why it fails: money fields are in cents.

Fix: divide by 100 before presenting currency values.
