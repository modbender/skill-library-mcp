---
name: Stripe Production Engineering
description: Complete methodology for building, scaling, and operating
  production Stripe payment systems. From first checkout to enterprise billing
  at scale.
---

# Stripe Production Engineering

Complete methodology for building, scaling, and operating production Stripe payment systems. From first checkout to enterprise billing at scale.

## Quick Health Check

Run through these 8 signals. Score 1 point each. Below 5 = stop and fix.

1. ✅ Webhook endpoint verified and idempotent
2. ✅ All API calls use idempotency keys
3. ✅ Customer portal enabled for self-service
4. ✅ Stripe Tax or manual tax collection configured
5. ✅ Failed payment retry logic with dunning emails
6. ✅ PCI compliance questionnaire completed (SAQ-A minimum)
7. ✅ Test mode → live mode checklist completed
8. ✅ Monitoring/alerting on payment failures and webhook errors

**Score: /8** — Below 5? Fix gaps before adding features.

---

## Phase 1: Architecture Strategy

### Integration Pattern Decision

| Pattern | Best For | Complexity | PCI Scope |
|---------|----------|------------|-----------|
| **Stripe Checkout (hosted)** | MVPs, quick launch | Low | SAQ-A (minimal) |
| **Payment Element (embedded)** | Custom UX, brand control | Medium | SAQ-A |
| **Card Element (legacy)** | Existing integrations | Medium | SAQ-A-EP |
| **Direct API** | Platform/marketplace | High | SAQ-D (avoid) |

**Decision rule:** Start with Checkout. Move to Payment Element only when you have specific UX requirements that Checkout can't solve.

### Billing Model Selection

| Model | Stripe Product | Use When |
|-------|---------------|----------|
| One-time | Payment Links / Checkout | Single purchases, lifetime deals |
| Recurring flat | Subscriptions | Fixed monthly/annual SaaS |
| Usage-based | Metered billing | API calls, compute, storage |
| Per-seat | Subscriptions + quantity | Team/user-based pricing |
| Tiered | Tiered pricing | Volume discounts |
| Hybrid | Subscription + usage records | Base fee + overage |

### Project Structure

```
src/
  payments/
    stripe.config.ts        # Stripe client initialization
    webhooks.handler.ts     # Webhook endpoint + event routing
    checkout.service.ts     # Checkout session creation
    subscription.service.ts # Subscription lifecycle
    customer.service.ts     # Customer CRUD + portal
    invoice.service.ts      # Invoice customization
    tax.service.ts          # Tax calculation
    types.ts                # Shared types
  middleware/
    webhook-verify.ts       # Signature verification middleware
```

### 7 Architecture Rules

1. **Never trust the client** — verify payment status server-side via webhooks, never from redirect URLs
2. **Webhooks are the source of truth** — your database updates from webhook events, not API call responses
3. **Idempotency everywhere** — every mutating API call gets an idempotency key
4. **One Stripe customer per user** — create customer at signup, store `stripe_customer_id` in your DB
5. **Metadata is your friend** — attach `user_id`, `plan`, `source` to every object for debugging
6. **Test mode mirrors live** — your test environment should use the exact same code paths
7. **Never store card numbers** — use Stripe.js/Elements, never handle raw card data

---

## Phase 2: Core Integration Patterns

### Stripe Client Setup

```typescript
// stripe.config.ts
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-12-18.acacia',  // Pin API version!
  maxNetworkRetries: 2,
  timeout: 10_000,
  telemetry: false,
});

export { stripe };
```

**Rules:**
- Pin API version — never use rolling latest
- Set explicit timeout (10s default is fine)
- Disable telemetry in production if privacy-sensitive
- Use restricted keys with minimum required permissions

### Customer Lifecycle

```typescript
// customer.service.ts
async function getOrCreateCustomer(userId: string, email: string, name?: string) {
  // Check DB first
  const existing = await db.users.findOne({ id: userId });
  if (existing?.stripeCustomerId) {
    return existing.stripeCustomerId;
  }

  // Create in Stripe
  const customer = await stripe.customers.create({
    email,
    name,
    metadata: {
      user_id: userId,
      created_via: 'signup',
    },
  });

  // Store mapping
  await db.users.update({ id: userId }, { stripeCustomerId: customer.id });
  return customer.id;
}
```

**Customer rules:**
- Create at signup, not at first purchase
- Always set metadata.user_id for reverse lookups
- Store stripe_customer_id in your users table
- Use customer email updates to sync — listen for `customer.updated`

### Checkout Session (Recommended Starting Point)

```typescript
// checkout.service.ts
async function createCheckoutSession(params: {
  customerId: string;
  priceId: string;
  mode: 'payment' | 'subscription';
  successUrl: string;
  cancelUrl: string;
  metadata?: Record<string, string>;
}) {
  const session = await stripe.checkout.sessions.create({
    customer: params.customerId,
    mode: params.mode,
    line_items: [{ price: params.priceId, quantity: 1 }],
    success_url: `${params.successUrl}?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: params.cancelUrl,
    metadata: params.metadata ?? {},

    // Recommended defaults
    allow_promotion_codes: true,
    billing_address_collection: 'auto',
    tax_id_collection: { enabled: true },
    customer_update: { address: 'auto', name: 'auto' },
    payment_method_types: ['card'],
    
    // For subscriptions
    ...(params.mode === 'subscription' && {
      subscription_data: {
        metadata: params.metadata ?? {},
        trial_period_days: 14,
      },
    }),
  }, {
    idempotencyKey: `checkout_${params.customerId}_${params.priceId}_${Date.now()}`,
  });

  return session;
}
```

### Payment Element (Custom UI)

```typescript
// Server: create PaymentIntent
async function createPaymentIntent(params: {
  customerId: string;
  amount: number;      // in cents!
  currency: string;
  metadata?: Record<string, string>;
}) {
  return stripe.paymentIntents.create({
    customer: params.customerId,
    amount: params.amount,
    currency: params.currency,
    automatic_payment_methods: { enabled: true },
    metadata: {
      ...params.metadata,
      created_at: new Date().toISOString(),
    },
  }, {
    idempotencyKey: `pi_${params.customerId}_${params.amount}_${Date.now()}`,
  });
}

// Client: React Payment Element
// <PaymentElement /> handles all payment method rendering
// Use confirmPayment() on form submit
```

---

## Phase 3: Subscription Management

### Subscription Lifecycle Events

```
Created → Active → Past Due → Canceled → (optionally) Unpaid
                ↓
            Trialing → Active
                ↓
            Paused → Resumed → Active
```

### Critical Webhook Events for Subscriptions

| Event | Action |
|-------|--------|
| `customer.subscription.created` | Provision access, set plan in DB |
| `customer.subscription.updated` | Handle plan changes, quantity updates |
| `customer.subscription.deleted` | Revoke access, clean up |
| `customer.subscription.trial_will_end` | Send conversion email (3 days before) |
| `invoice.payment_succeeded` | Confirm access renewal |
| `invoice.payment_failed` | Start dunning sequence |
| `customer.subscription.paused` | Restrict access, retain data |
| `customer.subscription.resumed` | Restore access |

### Plan Change Patterns

```typescript
// Upgrade (immediate)
async function upgradePlan(subscriptionId: string, newPriceId: string) {
  const sub = await stripe.subscriptions.retrieve(subscriptionId);
  return stripe.subscriptions.update(subscriptionId, {
    items: [{
      id: sub.items.data[0].id,
      price: newPriceId,
    }],
    proration_behavior: 'create_prorations',  // charge difference immediately
    payment_behavior: 'error_if_incomplete',
  });
}

// Downgrade (at period end)
async function downgradePlan(subscriptionId: string, newPriceId: string) {
  const sub = await stripe.subscriptions.retrieve(subscriptionId);
  return stripe.subscriptions.update(subscriptionId, {
    items: [{
      id: sub.items.data[0].id,
      price: newPriceId,
    }],
    proration_behavior: 'none',               // no refund, change at renewal
    billing_cycle_anchor: 'unchanged',
  });
}

// Cancel (at period end — always prefer this)
async function cancelSubscription(subscriptionId: string) {
  return stripe.subscriptions.update(subscriptionId, {
    cancel_at_period_end: true,
  });
  // User keeps access until period ends
  // Handle `customer.subscription.deleted` to revoke
}
```

### Dunning (Failed Payment Recovery)

```yaml
# Stripe Dashboard → Settings → Subscriptions → Smart Retries
retry_schedule:
  attempt_1: 1 day after failure    # Smart timing
  attempt_2: 3 days after failure
  attempt_3: 5 days after failure
  attempt_4: 7 days after failure   # Final attempt

# Custom dunning emails (supplement Stripe's built-in)
dunning_sequence:
  - day: 0
    action: "Email: payment failed, update card link"
    template: "Your payment of {amount} failed. Update → {portal_url}"
  - day: 3
    action: "Email: second notice, urgency"
    template: "Still unable to charge. Update payment to avoid interruption."
  - day: 5
    action: "Email: final warning"
    template: "Last chance to update. Access pauses in 48 hours."
  - day: 7
    action: "Pause or cancel subscription"
    note: "Automatic via Stripe if all retries fail"
```

### Usage-Based Billing

```typescript
// Report usage for metered billing
async function reportUsage(subscriptionItemId: string, quantity: number) {
  return stripe.subscriptionItems.createUsageRecord(subscriptionItemId, {
    quantity,
    timestamp: Math.floor(Date.now() / 1000),
    action: 'increment',  // or 'set' for absolute value
  }, {
    idempotencyKey: `usage_${subscriptionItemId}_${Date.now()}`,
  });
}

// Best practice: batch usage reports
// Don't report every API call individually — aggregate per hour/day
// Report at least daily to avoid surprise bills at period end
```

---

## Phase 4: Webhooks (The Most Critical Part)

### Webhook Handler Template

```typescript
// webhooks.handler.ts
import { stripe } from './stripe.config';
import type { Request, Response } from 'express';

const WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET!;

// Event handlers map
const handlers: Record<string, (event: Stripe.Event) => Promise<void>> = {
  'checkout.session.completed': handleCheckoutCompleted,
  'customer.subscription.created': handleSubscriptionCreated,
  'customer.subscription.updated': handleSubscriptionUpdated,
  'customer.subscription.deleted': handleSubscriptionDeleted,
  'invoice.payment_succeeded': handleInvoicePaymentSucceeded,
  'invoice.payment_failed': handleInvoicePaymentFailed,
  'customer.subscription.trial_will_end': handleTrialEnding,
  'payment_intent.succeeded': handlePaymentSucceeded,
  'payment_intent.payment_failed': handlePaymentFailed,
};

export async function handleWebhook(req: Request, res: Response) {
  // 1. Verify signature (NEVER skip this)
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(
      req.body,        // raw body, not parsed JSON!
      req.headers['stripe-signature']!,
      WEBHOOK_SECRET,
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return res.status(400).send('Invalid signature');
  }

  // 2. Idempotency check
  const alreadyProcessed = await db.webhookEvents.findOne({ eventId: event.id });
  if (alreadyProcessed) {
    return res.status(200).json({ received: true, duplicate: true });
  }

  // 3. Route to handler
  const handler = handlers[event.type];
  if (handler) {
    try {
      await handler(event);
      await db.webhookEvents.insert({ eventId: event.id, type: event.type, processedAt: new Date() });
    } catch (err) {
      console.error(`Webhook handler failed for ${event.type}:`, err);
      return res.status(500).send('Handler error');  // Stripe will retry
    }
  }

  // 4. Always return 200 quickly
  res.status(200).json({ received: true });
}
```

### 10 Webhook Rules

1. **Verify every signature** — never process unverified events
2. **Use raw body** — don't parse JSON before verification (Express: `express.raw({type: 'application/json'})`)
3. **Idempotency** — store processed event IDs, handle duplicates gracefully
4. **Return 200 fast** — do heavy processing async/in background
5. **Handle out-of-order** — events may arrive in unexpected order; check current state before applying
6. **Don't rely on event data alone** — for critical actions, re-fetch the object from the API
7. **Log everything** — event ID, type, relevant object IDs, processing result
8. **Monitor failures** — alert on repeated 500s or unhandled event types
9. **Use CLI for local dev** — `stripe listen --forward-to localhost:3000/webhooks`
10. **Register only events you handle** — don't subscribe to everything

### Essential Events by Use Case

| Use Case | Must-Have Events |
|----------|-----------------|
| One-time payments | `checkout.session.completed`, `payment_intent.succeeded`, `payment_intent.payment_failed` |
| Subscriptions | All subscription.* + `invoice.payment_succeeded`, `invoice.payment_failed`, `invoice.upcoming` |
| Marketplace/Connect | `account.updated`, `payout.paid`, `payout.failed`, `transfer.created` |
| Invoicing | `invoice.created`, `invoice.finalized`, `invoice.paid`, `invoice.payment_failed` |

---

## Phase 5: Customer Portal & Self-Service

```typescript
// Customer portal — saves you building billing UI
async function createPortalSession(customerId: string, returnUrl: string) {
  return stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: returnUrl,
  });
}

// Configure in Dashboard → Settings → Customer portal
// Enable: Update payment method, Cancel subscription, View invoices
// Optional: Plan switching, Invoice history download
```

### Portal Configuration Checklist

- [ ] Payment method update enabled
- [ ] Subscription cancellation with reason collection
- [ ] Plan switching with proration preview
- [ ] Invoice history visible
- [ ] Business information (name, logo) set
- [ ] Return URL configured
- [ ] Terms of service / privacy policy linked

---

## Phase 6: Tax Collection

### Tax Decision Tree

```
Do you sell to EU customers?
  YES → Need VAT collection
    Use Stripe Tax (automatic) OR manual tax rates
  NO → 
Do you sell to US customers in multiple states?
  YES → Need sales tax (nexus rules)
    Use Stripe Tax (automatic) — manual is nightmare
  NO →
Do you exceed $100K revenue or 200 transactions in any US state?
  YES → You have economic nexus — collect tax
  NO → May not need to collect, but verify with accountant
```

### Stripe Tax Setup

```typescript
// Enable automatic tax on Checkout
const session = await stripe.checkout.sessions.create({
  // ... other config
  automatic_tax: { enabled: true },
  customer_update: { address: 'auto' },  // Required for tax calculation
});

// For subscriptions via API
const subscription = await stripe.subscriptions.create({
  customer: customerId,
  items: [{ price: priceId }],
  automatic_tax: { enabled: true },
});
```

**Tax rules:**
- Stripe Tax handles calculation + collection automatically
- You still need to file/remit taxes yourself (or use Stripe Tax filing in supported regions)
- Always collect billing address for accurate tax calculation
- Enable tax ID collection for B2B reverse charge (EU)

---

## Phase 7: Stripe Connect (Marketplaces & Platforms)

### Connect Account Types

| Type | Control | Onboarding | Best For |
|------|---------|------------|----------|
| **Standard** | Low (Stripe-hosted dashboard) | Stripe-hosted | Marketplaces where sellers manage their own Stripe |
| **Express** | Medium (limited dashboard) | Stripe-hosted | Platforms managing payouts for contractors/sellers |
| **Custom** | Full (you build everything) | You build it | Enterprise platforms needing total control |

**Decision rule:** Use Express unless you have a specific reason not to.

### Payment Flow Patterns

```typescript
// Direct charge (platform takes cut)
const paymentIntent = await stripe.paymentIntents.create({
  amount: 10000,  // $100
  currency: 'usd',
  application_fee_amount: 1500,  // $15 platform fee
  transfer_data: {
    destination: 'acct_seller123',
  },
});

// Destination charge (seller's Stripe processes)
// Same as above but payment appears on seller's statement

// Separate charges and transfers (most flexible)
const charge = await stripe.paymentIntents.create({
  amount: 10000,
  currency: 'usd',
});
// Then transfer to seller
const transfer = await stripe.transfers.create({
  amount: 8500,
  currency: 'usd',
  destination: 'acct_seller123',
  transfer_group: 'order_123',
});
```

---

## Phase 8: Testing Strategy

### Test Mode Checklist

| Test | How | Pass Criteria |
|------|-----|--------------|
| Successful payment | Card: 4242424242424242 | Checkout completes, webhook fires, DB updated |
| Declined card | Card: 4000000000000002 | Error shown, no DB change |
| 3D Secure required | Card: 4000002500003155 | Auth modal shown, completes after |
| Insufficient funds | Card: 4000000000009995 | Graceful failure message |
| Subscription create | Use test price, complete checkout | Sub active, access granted |
| Payment failure + retry | Attach 4000000000000341, trigger invoice | Dunning sequence fires |
| Webhook replay | `stripe events resend evt_xxx` | Idempotent — no duplicate processing |
| Refund | Refund via API or Dashboard | Customer notified, access handled |
| Upgrade/downgrade | Change plan mid-cycle | Proration correct |
| Cancel at period end | Cancel, verify access until period end | Access maintained, then revoked |

### Stripe CLI for Local Development

```bash
# Install
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# Trigger specific events for testing
stripe trigger checkout.session.completed
stripe trigger invoice.payment_failed
stripe trigger customer.subscription.deleted
```

---

## Phase 9: Security & PCI Compliance

### PCI Compliance Levels

| Level | Criteria | Requirement |
|-------|----------|-------------|
| **SAQ-A** | Checkout or Elements (recommended) | Annual questionnaire, no scan |
| **SAQ-A-EP** | Client-side tokenization | Annual questionnaire + quarterly scan |
| **SAQ-D** | Direct API card handling (avoid) | Full audit, quarterly scans, penetration tests |

### Security Checklist (P0 — Mandatory)

- [ ] API keys in environment variables, never in code
- [ ] Webhook signatures verified on every request
- [ ] Restricted API keys with minimum permissions
- [ ] HTTPS everywhere (Stripe requires it)
- [ ] No card numbers logged, stored, or transmitted
- [ ] CSRF protection on payment endpoints
- [ ] Rate limiting on checkout creation
- [ ] Idempotency keys on all mutating calls

### API Key Strategy

```
Live mode:
  sk_live_xxx    → Server only, env var, restricted permissions
  pk_live_xxx    → Client-side (public, safe to expose)
  whsec_xxx      → Webhook secret, server only

Test mode:
  sk_test_xxx    → Same restrictions as live
  pk_test_xxx    → Client-side
  whsec_test_xxx → Webhook secret (different from live!)
```

**Restricted key permissions** (create in Dashboard → API Keys):
- Checkout Sessions: Write
- Customers: Write
- Subscriptions: Read/Write
- Webhook Endpoints: Read
- Everything else: None

---

## Phase 10: Go-Live Checklist

### Pre-Launch (P0 — Mandatory)

- [ ] Webhook endpoint registered and verified in live mode
- [ ] All webhook events subscribed (same as test)
- [ ] Live API keys in production environment
- [ ] Customer portal configured with live branding
- [ ] Test a real $1 payment end-to-end (then refund)
- [ ] Error handling for all payment states (success, failure, pending, requires_action)
- [ ] Logging: payment ID, customer ID, amount, status on every transaction
- [ ] PCI SAQ-A completed in Stripe Dashboard

### Pre-Launch (P1 — Within First Week)

- [ ] Monitoring: alert on payment failure rate > 5%
- [ ] Monitoring: alert on webhook delivery failures
- [ ] Receipt emails configured (Stripe auto-sends or custom)
- [ ] Refund process documented
- [ ] Dispute/chargeback response process
- [ ] Dunning emails active for subscriptions
- [ ] Stripe Tax enabled (if applicable)

### Pre-Launch (P2 — Within First Month)

- [ ] Revenue analytics dashboard
- [ ] MRR/churn tracking
- [ ] Coupon/promotion code strategy
- [ ] Annual vs monthly pricing toggle
- [ ] Customer portal self-service verified

---

## Phase 11: Monitoring & Operations

### Key Metrics Dashboard

```yaml
metrics:
  payment_success_rate:
    calculation: "successful_payments / total_attempts × 100"
    healthy: ">= 95%"
    warning: "90-95%"
    critical: "< 90%"
    
  webhook_delivery_rate:
    calculation: "successful_deliveries / total_events × 100"  
    healthy: ">= 99.5%"
    critical: "< 99%"
    
  average_revenue_per_user:
    calculation: "total_revenue / active_customers"
    track: "weekly trend"
    
  monthly_recurring_revenue:
    calculation: "sum(active_subscription_amounts)"
    track: "monthly growth rate"
    
  churn_rate:
    calculation: "canceled_subscriptions / total_active × 100"
    healthy: "< 5% monthly"
    warning: "5-10%"
    critical: "> 10%"
    
  involuntary_churn:
    calculation: "failed_payment_cancellations / total_churn × 100"
    note: "Should be < 30% of total churn — fix with better dunning"
```

### Weekly Review Checklist

- [ ] Payment success rate vs last week
- [ ] Failed payments — any patterns? (card type, region, amount)
- [ ] Webhook failures — any endpoints timing out?
- [ ] New disputes/chargebacks — respond within 7 days
- [ ] Subscription metrics: new, churned, upgraded, downgraded
- [ ] Revenue: MRR, net new MRR, expansion MRR, contraction MRR

---

## Phase 12: Advanced Patterns

### Pricing Page with Annual Toggle

```typescript
// Create both monthly and annual prices for each plan
const prices = {
  starter: {
    monthly: 'price_starter_monthly',   // $29/mo
    annual: 'price_starter_annual',     // $290/yr (save ~17%)
  },
  pro: {
    monthly: 'price_pro_monthly',       // $79/mo
    annual: 'price_pro_annual',         // $790/yr
  },
};

// Client toggles monthly/annual → creates checkout with correct priceId
```

### Grandfathering & Price Increases

```typescript
// New price, existing customers keep old price
// 1. Create new price object (don't modify existing)
// 2. New signups use new price
// 3. Existing subs stay on old price until they change plans
// 4. Optional: scheduled price migration with notice

async function schedulePriceIncrease(subscriptionId: string, newPriceId: string, effectiveDate: Date) {
  // Create a subscription schedule
  const schedule = await stripe.subscriptionSchedules.create({
    from_subscription: subscriptionId,
  });
  
  // Add phase with new price
  await stripe.subscriptionSchedules.update(schedule.id, {
    phases: [
      { items: [{ price: currentPriceId }], end_date: Math.floor(effectiveDate.getTime() / 1000) },
      { items: [{ price: newPriceId }] },
    ],
  });
}
```

### Coupon & Promotion Codes

```typescript
// Create coupon (reusable)
const coupon = await stripe.coupons.create({
  percent_off: 20,
  duration: 'repeating',
  duration_in_months: 3,
  max_redemptions: 100,
  metadata: { campaign: 'launch_2024' },
});

// Create promotion code (shareable link)
const promoCode = await stripe.promotionCodes.create({
  coupon: coupon.id,
  code: 'LAUNCH20',
  max_redemptions: 50,
  expires_at: Math.floor(new Date('2024-12-31').getTime() / 1000),
});
```

### Handling Disputes (Chargebacks)

```yaml
dispute_response_process:
  when_received:
    - Log dispute details: amount, reason, deadline
    - Alert team immediately
    - Begin evidence collection within 24 hours
    
  evidence_to_collect:
    - Customer communication (emails, chat logs)
    - Delivery proof (access logs, download records)
    - Terms of service acceptance timestamp
    - Refund policy shown at checkout
    - IP address and device fingerprint
    - Prior successful transactions from same customer
    
  submit:
    - Within 7 days (Stripe deadline is usually 21 days, but act fast)
    - Use Stripe Dashboard evidence submission form
    - Include written rebuttal addressing specific reason code
    
  prevention:
    - Clear billing descriptor (customer recognizes charge)
    - Send receipt emails immediately
    - Offer easy refunds before disputes escalate
    - Use Radar for fraud detection
```

---

## 10 Common Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | Trusting client-side redirect as payment confirmation | Always verify via webhook |
| 2 | Parsing JSON body before webhook signature verification | Use raw body buffer |
| 3 | No idempotency keys on API calls | Add to every mutating call |
| 4 | Immediately canceling instead of cancel_at_period_end | Always cancel at period end unless refunding |
| 5 | Amounts in dollars instead of cents | Stripe uses smallest currency unit (cents) |
| 6 | Not handling 3D Secure / requires_action status | Check payment_intent.status, handle authentication |
| 7 | Same webhook secret for test and live | Use separate secrets per environment |
| 8 | Not testing with Stripe CLI locally | Set up `stripe listen` in development |
| 9 | Hardcoding price IDs | Use config/env vars, different per environment |
| 10 | No dunning strategy for failed subscription payments | Configure Smart Retries + custom emails |

---

## Quality Rubric (0-100)

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Webhook reliability | 25% | Signature verification, idempotency, error handling, event coverage |
| Security & PCI | 20% | SAQ-A compliance, key management, no card data exposure |
| Subscription lifecycle | 15% | Create/upgrade/downgrade/cancel/pause all handled correctly |
| Customer experience | 15% | Portal, receipts, dunning emails, clear error messages |
| Testing coverage | 10% | All payment states tested, CLI setup, edge cases |
| Monitoring | 10% | Failure alerts, revenue metrics, dispute tracking |
| Code quality | 5% | TypeScript types, error handling, idempotency keys, logging |

---

## Commands

The agent responds to these natural language requests:

1. "Set up Stripe checkout" → Full Checkout integration with webhook handler
2. "Add subscriptions" → Subscription lifecycle with plan changes and dunning
3. "Configure webhooks" → Webhook handler with signature verification and idempotency
4. "Set up customer portal" → Billing portal configuration
5. "Add usage-based billing" → Metered subscription with usage reporting
6. "Stripe security audit" → PCI compliance check + security hardening
7. "Go-live checklist" → Pre-launch verification for production
8. "Set up Stripe Connect" → Marketplace/platform payment flows
9. "Add coupons and promos" → Promotion code system
10. "Review payment metrics" → Revenue and payment health dashboard
11. "Handle a dispute" → Chargeback response process
12. "Migrate pricing" → Grandfathering and price increase strategy
