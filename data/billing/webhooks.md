# Webhooks & Event Handling

## Signature Verification (Critical)

```typescript
// Stripe
const sig = req.headers['stripe-signature'];
const event = stripe.webhooks.constructEvent(
  req.rawBody, // MUST be raw, not JSON-parsed
  sig,
  process.env.STRIPE_WEBHOOK_SECRET
);

// Paddle
const isValid = Paddle.webhooks.verify(
  req.rawBody,
  req.headers['paddle-signature'],
  process.env.PADDLE_WEBHOOK_SECRET
);
```

**Common mistake:** Using `req.body` (parsed) instead of raw body fails verification.

## Idempotency Pattern

```typescript
async function handleWebhook(event: StripeEvent) {
  // Check if already processed
  const existing = await db.webhookLog.findUnique({
    where: { eventId: event.id }
  });
  if (existing) {
    return { status: 'already_processed' };
  }
  
  // Process in transaction
  await db.$transaction(async (tx) => {
    // Log first (prevents race conditions)
    await tx.webhookLog.create({
      data: { eventId: event.id, type: event.type, processedAt: new Date() }
    });
    
    // Then process
    await processEvent(event, tx);
  });
}
```

## Event Ordering Problem

Events arrive out of order. Example:
1. `customer.subscription.updated` (plan changed)
2. `invoice.created` (for new plan)
3. `invoice.paid` ← This might arrive BEFORE #1

**Solution:** Event handlers should be stateless operations, not sequential flows.

```typescript
// BAD: Assumes order
async function handleInvoicePaid(invoice) {
  const sub = await db.subscription.findFirst({...});
  sub.status = 'active'; // Might not exist yet!
}

// GOOD: Self-contained
async function handleInvoicePaid(invoice) {
  await db.subscription.upsert({
    where: { stripeSubscriptionId: invoice.subscription },
    update: { status: 'active', paidThrough: invoice.period_end },
    create: { /* full object */ }
  });
}
```

## Critical Events to Handle

| Event | Priority | Action |
|-------|----------|--------|
| `invoice.paid` | Critical | Grant/extend access |
| `invoice.payment_failed` | Critical | Start dunning flow |
| `customer.subscription.deleted` | Critical | Revoke access |
| `customer.subscription.updated` | High | Sync plan, period dates |
| `payment_intent.requires_action` | High | Notify user (3D Secure) |
| `charge.dispute.created` | High | Alert, gather evidence |
| `customer.updated` | Medium | Sync email, metadata |

## Webhook Endpoint Best Practices

```typescript
app.post('/webhooks/stripe', 
  express.raw({ type: 'application/json' }), // Raw body
  async (req, res) => {
    try {
      const event = verifySignature(req);
      
      // Acknowledge immediately
      res.status(200).json({ received: true });
      
      // Process async (prevents timeout)
      processEventAsync(event);
      
    } catch (err) {
      // Stripe will retry on 4xx/5xx
      res.status(400).send(`Webhook Error: ${err.message}`);
    }
  }
);
```

## Retry Behavior

| PSP | Retry Schedule | Max Retries |
|-----|---------------|-------------|
| Stripe | Exponential over 3 days | ~16 times |
| Paddle | Exponential over 24h | ~8 times |
| PayPal | Immediate, then 1h, 24h | 3 times |

**Design for:** Events may never arrive (network issues). Reconciliation jobs catch gaps.
