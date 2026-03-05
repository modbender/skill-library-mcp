# Subscriptions — Stripe API

## Subscription Lifecycle

```
created → active → past_due → canceled
                 ↘ unpaid ↗
                 ↘ paused → active
```

## Status Reference

| Status | Meaning | Action |
|--------|---------|--------|
| `incomplete` | Initial payment failed | Retry or cancel |
| `incomplete_expired` | 23h passed without payment | Start over |
| `trialing` | In trial period | No action needed |
| `active` | Payments current | Normal operation |
| `past_due` | Payment failed, in retry | Contact customer |
| `unpaid` | Retries exhausted | Cancel or intervention |
| `canceled` | Subscription ended | Resubscribe if wanted |
| `paused` | Collection paused | Resume when ready |

## Create Subscription Patterns

### Simple Subscription
```bash
curl https://api.stripe.com/v1/subscriptions \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX" \
  -d "items[0][price]=price_XXX"
```

### With Trial
```bash
curl https://api.stripe.com/v1/subscriptions \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX" \
  -d "items[0][price]=price_XXX" \
  -d "trial_period_days=14"
```

### With Specific Trial End
```bash
curl https://api.stripe.com/v1/subscriptions \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX" \
  -d "items[0][price]=price_XXX" \
  -d "trial_end=$(($(date +%s) + 604800))"  # 7 days from now
```

### With Default Payment Method
```bash
curl https://api.stripe.com/v1/subscriptions \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX" \
  -d "items[0][price]=price_XXX" \
  -d "default_payment_method=pm_XXX"
```

### With Coupon
```bash
curl https://api.stripe.com/v1/subscriptions \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX" \
  -d "items[0][price]=price_XXX" \
  -d "coupon=WELCOME20"
```

## Plan Changes (Upgrades/Downgrades)

### Immediate Upgrade with Proration
```bash
curl https://api.stripe.com/v1/subscriptions/sub_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "items[0][id]=si_XXX" \
  -d "items[0][price]=price_HIGHER" \
  -d "proration_behavior=create_prorations"
```

### Downgrade at Period End
```bash
curl https://api.stripe.com/v1/subscriptions/sub_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "items[0][id]=si_XXX" \
  -d "items[0][price]=price_LOWER" \
  -d "proration_behavior=none" \
  -d "billing_cycle_anchor=unchanged"
```

### Preview Proration
```bash
curl https://api.stripe.com/v1/invoices/upcoming \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX" \
  -d "subscription=sub_XXX" \
  -d "subscription_items[0][id]=si_XXX" \
  -d "subscription_items[0][price]=price_NEW" \
  -d "subscription_proration_behavior=create_prorations"
```

## Cancellation Patterns

### Cancel Immediately
```bash
curl -X DELETE https://api.stripe.com/v1/subscriptions/sub_XXX \
  -u "$STRIPE_SECRET_KEY:"
```

### Cancel at Period End
```bash
curl https://api.stripe.com/v1/subscriptions/sub_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "cancel_at_period_end=true"
```

### Cancel at Specific Date
```bash
curl https://api.stripe.com/v1/subscriptions/sub_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "cancel_at=$(($(date +%s) + 2592000))"  # 30 days from now
```

### Undo Pending Cancellation
```bash
curl https://api.stripe.com/v1/subscriptions/sub_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "cancel_at_period_end=false"
```

## Pause and Resume

### Pause Collection
```bash
curl https://api.stripe.com/v1/subscriptions/sub_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "pause_collection[behavior]=mark_uncollectible"
```

Behaviors:
- `mark_uncollectible`: Invoices created but marked uncollectible
- `keep_as_draft`: Invoices created as drafts
- `void`: Invoices voided

### Pause Until Date
```bash
curl https://api.stripe.com/v1/subscriptions/sub_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "pause_collection[behavior]=mark_uncollectible" \
  -d "pause_collection[resumes_at]=$(($(date +%s) + 2592000))"
```

### Resume
```bash
curl https://api.stripe.com/v1/subscriptions/sub_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "pause_collection="
```

## Multiple Items (Add-ons)

### Add Item to Subscription
```bash
curl https://api.stripe.com/v1/subscription_items \
  -u "$STRIPE_SECRET_KEY:" \
  -d "subscription=sub_XXX" \
  -d "price=price_ADDON" \
  -d "quantity=1"
```

### Remove Item
```bash
curl -X DELETE https://api.stripe.com/v1/subscription_items/si_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "proration_behavior=create_prorations"
```

### Update Item Quantity
```bash
curl https://api.stripe.com/v1/subscription_items/si_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "quantity=5"
```

## Billing Cycle

### Change Billing Anchor (Next Renewal Date)
```bash
curl https://api.stripe.com/v1/subscriptions/sub_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "billing_cycle_anchor=now" \
  -d "proration_behavior=create_prorations"
```

### Bill Immediately (Mid-cycle)
```bash
curl https://api.stripe.com/v1/subscriptions/sub_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "billing_cycle_anchor=now"
```

## Metered Billing

### Report Usage
```bash
curl https://api.stripe.com/v1/subscription_items/si_XXX/usage_records \
  -u "$STRIPE_SECRET_KEY:" \
  -d "quantity=100" \
  -d "timestamp=$(date +%s)" \
  -d "action=increment"
```

Actions:
- `increment`: Add to existing usage
- `set`: Replace usage for timestamp

### Get Usage Summary
```bash
curl "https://api.stripe.com/v1/subscription_items/si_XXX/usage_record_summaries?limit=10" \
  -u "$STRIPE_SECRET_KEY:"
```

## Failed Payment Handling

### Retry Invoice Payment
```bash
curl https://api.stripe.com/v1/invoices/in_XXX/pay \
  -u "$STRIPE_SECRET_KEY:"
```

### Update Payment Method and Retry
```bash
# Update customer's default payment method
curl https://api.stripe.com/v1/customers/cus_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "invoice_settings[default_payment_method]=pm_NEW"

# Retry the failed invoice
curl https://api.stripe.com/v1/invoices/in_XXX/pay \
  -u "$STRIPE_SECRET_KEY:"
```

## Webhook Events for Subscriptions

| Event | When | Action |
|-------|------|--------|
| `customer.subscription.created` | New subscription | Provision access |
| `customer.subscription.updated` | Plan change, renewal | Update access |
| `customer.subscription.deleted` | Canceled | Revoke access |
| `customer.subscription.trial_will_end` | 3 days before trial ends | Send reminder |
| `customer.subscription.paused` | Subscription paused | Limit access |
| `customer.subscription.resumed` | Subscription resumed | Restore access |
| `invoice.payment_failed` | Payment failed | Send dunning email |
| `invoice.paid` | Subscription renewed | Confirm renewal |
