# Subscription

Check subscription status, tier, credits usage, and renewal dates.

## Command

```bash
genviral.sh subscription              # human-friendly output
genviral.sh subscription --json       # raw JSON data
genviral.sh get-subscription          # alias
```

### Options

| Flag | Type | Description |
|------|------|-------------|
| `--json` | flag | Output raw JSON data |

## Response Data

| Field | Description |
|-------|-------------|
| `scope` | `workspace` or `personal` |
| `workspace_id` | Workspace ID (null for personal keys) |
| `subscription.status` | e.g., `active`, `canceled` |
| `subscription.tier` | `small`, `medium`, `large`, etc. |
| `subscription.billing_interval` | `month` or `year` |
| `subscription.renews_at` | Next renewal timestamp |
| `subscription.credits.limit` | Monthly credit allowance |
| `subscription.credits.used_this_period` | Credits consumed |
| `subscription.credits.remaining` | Credits available |
| `subscription.credits.reset_at` | When credits reset |

## Use Cases

- **Before generating** - Check if enough credits remain
- **Budget tracking** - Monitor usage across billing periods
- **Tier awareness** - Know what features are available

## Error Codes

| Code | Meaning |
|------|---------|
| `401` | Auth failed |
| `402 subscription_required` | No active plan |
| `403 tier_not_allowed` | Scheduler tier blocked |
| `500 subscription_lookup_failed` | Server error |
