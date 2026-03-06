# Subscription Lifecycle

## State Machine

```
┌─────────────┐
│  trialing   │ ← New subscription with trial
└──────┬──────┘
       │ trial ends
       ▼
┌─────────────┐     payment fails     ┌─────────────┐
│   active    │ ──────────────────►   │  past_due   │
└──────┬──────┘                       └──────┬──────┘
       │                                     │
       │ cancel requested                    │ retry succeeds
       ▼                                     │
┌─────────────┐                              │
│  canceled   │ ◄────────────────────────────┘
└──────┬──────┘   all retries fail
       │ period_end reached
       ▼
┌─────────────┐
│   unpaid    │ → Access revoked
└─────────────┘
```

## Dunning Flow

```typescript
const dunningSchedule = [
  { day: 0, action: 'first_attempt' },
  { day: 3, action: 'retry + soft_email' },
  { day: 5, action: 'retry + urgent_email' },
  { day: 7, action: 'retry + card_update_request' },
  { day: 10, action: 'final_retry' },
  { day: 14, action: 'cancel_subscription' }
];
```

**Configure in Stripe Dashboard:** Settings → Billing → Subscriptions → Manage failed payments

## Trial Patterns

| Type | Implementation | Conversion Rate |
|------|---------------|-----------------|
| No-card trial | Collect card at end | ~2-5% |
| Card-on-file trial | Charge at end | ~15-30% |
| Reverse trial | Start paid, downgrade to free | ~40-60% |

```typescript
// Card-on-file trial
const subscription = await stripe.subscriptions.create({
  customer: customerId,
  items: [{ price: priceId }],
  trial_period_days: 14,
  // Card already attached to customer
});
```

## Grace Periods

```typescript
// Check if user should have access
function hasAccess(subscription) {
  if (subscription.status === 'active') return true;
  if (subscription.status === 'trialing') return true;
  if (subscription.status === 'canceled') {
    // Still has access until period ends
    return Date.now() < subscription.current_period_end * 1000;
  }
  if (subscription.status === 'past_due') {
    // Configurable grace period
    const graceDays = 7;
    const graceEnd = subscription.current_period_end * 1000 + (graceDays * 86400000);
    return Date.now() < graceEnd;
  }
  return false;
}
```

## Plan Changes (Proration)

```typescript
// Upgrade mid-cycle
await stripe.subscriptions.update(subscriptionId, {
  items: [{
    id: subscription.items.data[0].id,
    price: newPriceId
  }],
  proration_behavior: 'create_prorations', // Credit + charge
});

// Downgrade (apply at renewal)
await stripe.subscriptions.update(subscriptionId, {
  items: [{
    id: subscription.items.data[0].id,
    price: newPriceId
  }],
  proration_behavior: 'none',
  billing_cycle_anchor: 'unchanged' // Keep same billing date
});
```

## Cancellation Best Practices

```typescript
// Soft cancel (recommended)
await stripe.subscriptions.update(subscriptionId, {
  cancel_at_period_end: true
});
// User keeps access until period ends

// Hard cancel (use sparingly)
await stripe.subscriptions.del(subscriptionId, {
  prorate: true // Refund unused time
});
```

## Pause Instead of Cancel

```typescript
// Stripe Billing pause
await stripe.subscriptions.update(subscriptionId, {
  pause_collection: {
    behavior: 'void', // or 'mark_uncollectible'
    resumes_at: Math.floor(Date.now()/1000) + 30*86400 // 30 days
  }
});
```
