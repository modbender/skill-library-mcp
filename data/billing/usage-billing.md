# Usage-Based Billing

## Metering Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   App/API   │────►│ Metering DB  │────►│ Aggregator  │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                    ┌──────────────┐            │
                    │  Invoicing   │◄───────────┘
                    └──────────────┘
```

## Critical: Idempotency in Metering

```typescript
// BAD: Duplicates inflate bills
async function recordUsage(event) {
  await db.usage.create({ data: event });
}

// GOOD: Idempotent
async function recordUsage(event) {
  await db.usage.upsert({
    where: { eventId: event.id },
    update: {}, // No-op if exists
    create: {
      eventId: event.id,
      customerId: event.customerId,
      quantity: event.quantity,
      timestamp: event.timestamp
    }
  });
}
```

## Aggregation Windows

| Window | Use Case | Complexity |
|--------|----------|------------|
| Real-time | Hard limits, notifications | High |
| Hourly | Dashboard display | Medium |
| Daily | Most billing | Low |
| Monthly | Simple SaaS | Lowest |

**Warning:** Events crossing window boundaries require careful handling.

## Stripe Usage Records

```typescript
// Report usage for metered billing
await stripe.subscriptionItems.createUsageRecord(
  subscriptionItemId,
  {
    quantity: 150, // API calls this period
    timestamp: Math.floor(Date.now() / 1000),
    action: 'increment' // or 'set'
  },
  {
    idempotencyKey: `usage-${customerId}-${period}` // Prevent duplicates
  }
);
```

## Prepaid Credits System

```typescript
interface CreditBalance {
  customerId: string;
  balance: number; // In smallest unit (cents)
  expiresAt: Date | null;
}

async function consumeCredits(customerId: string, amount: number) {
  return await db.$transaction(async (tx) => {
    const credits = await tx.creditBalance.findFirst({
      where: { 
        customerId,
        balance: { gt: 0 },
        OR: [
          { expiresAt: null },
          { expiresAt: { gt: new Date() } }
        ]
      },
      orderBy: { expiresAt: 'asc' } // FIFO expiration
    });
    
    if (!credits || credits.balance < amount) {
      throw new InsufficientCreditsError();
    }
    
    await tx.creditBalance.update({
      where: { id: credits.id },
      data: { balance: { decrement: amount } }
    });
    
    return { consumed: amount, remaining: credits.balance - amount };
  });
}
```

## Overage Handling

| Strategy | UX | Revenue |
|----------|-----|---------|
| Hard limit | Stop service | Predictable but frustrating |
| Soft limit + overage | Continue + charge extra | Good balance |
| Unlimited + throttle | Slow down | Poor monetization |

```typescript
// Soft limit with overage
const included = 10000; // API calls
const overageRate = 0.001; // $0.001 per call over

function calculateBill(usage: number) {
  const baseFee = 49.00;
  const overage = Math.max(0, usage - included) * overageRate;
  return baseFee + overage;
}
```

## Dashboard vs Invoice Discrepancy

**Problem:** Dashboard shows $50, invoice says $80.

**Cause:** Pipeline lag — events take time to aggregate.

**Solution:**
```typescript
// Dashboard: show estimate
const estimatedUsage = await getRealtimeUsage(customerId);

// Invoice: use finalized data
const finalUsage = await getFinalizedUsage(customerId, period);

// Show warning if difference > 10%
if (Math.abs(estimatedUsage - finalUsage) / finalUsage > 0.1) {
  showReconciliationWarning();
}
```
