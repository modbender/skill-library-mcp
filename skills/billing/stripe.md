# Stripe Integration Patterns

## Payment Methods

```typescript
// Attach payment method to customer
const paymentMethod = await stripe.paymentMethods.attach(pmId, {
  customer: customerId
});

// Set as default
await stripe.customers.update(customerId, {
  invoice_settings: { default_payment_method: pmId }
});
```

## Checkout Session

```typescript
const session = await stripe.checkout.sessions.create({
  mode: 'subscription', // or 'payment', 'setup'
  customer: customerId, // Reuse existing customer
  line_items: [{
    price: priceId,
    quantity: 1
  }],
  success_url: `${baseUrl}/success?session_id={CHECKOUT_SESSION_ID}`,
  cancel_url: `${baseUrl}/pricing`,
  subscription_data: {
    metadata: { userId: user.id },
    trial_period_days: 14 // Optional trial
  },
  automatic_tax: { enabled: true }, // If Stripe Tax configured
  allow_promotion_codes: true // Enable coupon field
});
```

## Customer Portal

```typescript
// Let customers manage their own subscriptions
const portalSession = await stripe.billingPortal.sessions.create({
  customer: customerId,
  return_url: `${baseUrl}/account`
});
// Redirect to portalSession.url
```

## Payment Intents (Custom Flows)

```typescript
// Create intent
const intent = await stripe.paymentIntents.create({
  amount: 5000,
  currency: 'usd',
  customer: customerId,
  payment_method: pmId,
  off_session: true, // For recurring/background charges
  confirm: true
});

// Handle different statuses
switch (intent.status) {
  case 'succeeded':
    // Payment complete
    break;
  case 'requires_action':
    // 3D Secure needed
    // Return intent.client_secret to frontend
    break;
  case 'requires_payment_method':
    // Card declined, ask for new card
    break;
}
```

## Subscription Creation

```typescript
const subscription = await stripe.subscriptions.create({
  customer: customerId,
  items: [{ price: priceId }],
  
  // Payment behavior
  payment_behavior: 'default_incomplete', // Don't activate until paid
  payment_settings: {
    payment_method_types: ['card'],
    save_default_payment_method: 'on_subscription'
  },
  
  // Billing settings
  collection_method: 'charge_automatically',
  billing_cycle_anchor: specificTimestamp, // Optional: set billing date
  
  // Trial
  trial_period_days: 14,
  // OR specific end date:
  trial_end: Math.floor(Date.now()/1000) + 14*86400,
  
  // Metadata
  metadata: { userId: user.id, plan: 'pro' }
});

// Return client_secret for payment confirmation
const { client_secret } = subscription.latest_invoice.payment_intent;
```

## Coupons and Promotions

```typescript
// Create coupon
const coupon = await stripe.coupons.create({
  percent_off: 25,
  duration: 'repeating',
  duration_in_months: 3
});

// Create promotion code (user-facing)
const promoCode = await stripe.promotionCodes.create({
  coupon: coupon.id,
  code: 'LAUNCH25',
  max_redemptions: 100,
  expires_at: Math.floor(Date.now()/1000) + 30*86400
});

// Apply to subscription
await stripe.subscriptions.update(subscriptionId, {
  coupon: coupon.id
});
```

## Invoicing

```typescript
// Create invoice manually
const invoice = await stripe.invoices.create({
  customer: customerId,
  collection_method: 'send_invoice',
  days_until_due: 30
});

// Add line items
await stripe.invoiceItems.create({
  customer: customerId,
  invoice: invoice.id,
  amount: 5000,
  currency: 'usd',
  description: 'Consulting - March 2024'
});

// Finalize and send
await stripe.invoices.finalizeInvoice(invoice.id);
await stripe.invoices.sendInvoice(invoice.id);
```

## Error Handling

```typescript
try {
  const charge = await stripe.charges.create({...});
} catch (err) {
  if (err.type === 'StripeCardError') {
    // Card declined
    const { code, decline_code, message } = err;
    // code: 'card_declined', 'expired_card', 'incorrect_cvc'
    // decline_code: 'insufficient_funds', 'lost_card', etc.
  } else if (err.type === 'StripeInvalidRequestError') {
    // Invalid parameters
  } else if (err.type === 'StripeAPIError') {
    // Stripe API issue, retry
  } else if (err.type === 'StripeRateLimitError') {
    // Too many requests, back off
  }
}
```

## Idempotency Keys

```typescript
// Prevent duplicate charges
const charge = await stripe.charges.create(
  {
    amount: 5000,
    currency: 'usd',
    source: 'tok_visa'
  },
  {
    idempotencyKey: `charge-${orderId}` // Same key = same result
  }
);
```

## Testing

| Card Number | Result |
|-------------|--------|
| 4242424242424242 | Success |
| 4000000000000002 | Decline |
| 4000002500003155 | 3DS required |
| 4000000000009995 | Insufficient funds |
| 4000000000000341 | Attaching fails |
