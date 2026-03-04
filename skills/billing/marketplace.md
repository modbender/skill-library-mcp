# Marketplace Payments

## Stripe Connect Account Types

| Type | Onboarding | Control | Use Case |
|------|------------|---------|----------|
| Standard | Stripe-hosted | Low | Simple referral |
| Express | Stripe-hosted | Medium | Marketplaces |
| Custom | Self-hosted | Full | White-label |

## Split Payments

```typescript
// Direct charge with application fee
const paymentIntent = await stripe.paymentIntents.create({
  amount: 10000, // $100
  currency: 'usd',
  application_fee_amount: 1500, // $15 platform fee
  transfer_data: {
    destination: connectedAccountId // Vendor gets $85
  }
});

// Destination charge (alternative)
const charge = await stripe.charges.create({
  amount: 10000,
  currency: 'usd',
  source: sourceId,
  destination: {
    account: connectedAccountId,
    amount: 8500 // Explicit vendor amount
  }
});
```

## Multi-Vendor Cart

```typescript
// Separate PaymentIntents per vendor
async function checkoutMultiVendor(cart: CartItem[]) {
  const vendorGroups = groupBy(cart, 'vendorId');
  
  const intents = await Promise.all(
    Object.entries(vendorGroups).map(([vendorId, items]) =>
      stripe.paymentIntents.create({
        amount: sumAmounts(items),
        currency: 'usd',
        application_fee_amount: calculateFee(items),
        transfer_data: { destination: vendorId },
        metadata: { orderId, vendorId }
      })
    )
  );
  
  return intents;
}

// Or: Single charge, multiple transfers
const payment = await stripe.paymentIntents.create({
  amount: totalAmount,
  currency: 'usd'
});

// After payment succeeds
for (const vendor of vendors) {
  await stripe.transfers.create({
    amount: vendor.amount,
    currency: 'usd',
    destination: vendor.stripeAccountId,
    source_transaction: payment.charges.data[0].id
  });
}
```

## Payout Timing

| Strategy | Cash Flow | Risk |
|----------|-----------|------|
| Immediate | Best for vendors | High (chargebacks) |
| 7-day hold | Balanced | Medium |
| 14-day hold | Conservative | Low |
| Manual | Full control | Operational overhead |

```typescript
// Configure payout schedule per vendor
await stripe.accounts.update(connectedAccountId, {
  settings: {
    payouts: {
      schedule: {
        delay_days: 7, // Hold for 7 days
        interval: 'daily'
      }
    }
  }
});
```

## Refunds in Marketplace

```typescript
// Who pays for refund?
async function processMarketplaceRefund(chargeId: string, amount: number) {
  // Option 1: Platform absorbs
  await stripe.refunds.create({
    charge: chargeId,
    amount: amount,
    reverse_transfer: false // Don't claw back from vendor
  });
  
  // Option 2: Vendor absorbs
  await stripe.refunds.create({
    charge: chargeId,
    amount: amount,
    reverse_transfer: true // Claw back from vendor
  });
  
  // Option 3: Split
  await stripe.refunds.create({
    charge: chargeId,
    amount: amount * 0.5, // Customer gets full refund
    reverse_transfer: true
  });
  // Platform eats the other half
}
```

## Tax Liability (EU DAC7)

In EU, marketplace may be liable for VAT if:
- Facilitates B2C sales
- Sets prices or T&Cs
- Handles fulfillment

**Solution:** Become "deemed supplier" or use Stripe Tax.

## 1099-K Reporting (US)

Threshold: $600/year per vendor (as of 2024).

```typescript
// Collect required data during onboarding
await stripe.accounts.update(connectedAccountId, {
  individual: {
    first_name: 'Jane',
    last_name: 'Doe',
    ssn_last_4: '1234', // Or full SSN
    address: { /* ... */ }
  }
});

// Stripe handles 1099-K generation and filing
```

## Connected Account Onboarding

```typescript
// Express account (recommended for most)
const account = await stripe.accounts.create({
  type: 'express',
  country: 'US',
  email: 'vendor@example.com',
  capabilities: {
    card_payments: { requested: true },
    transfers: { requested: true }
  }
});

// Generate onboarding link
const accountLink = await stripe.accountLinks.create({
  account: account.id,
  refresh_url: 'https://example.com/onboarding/refresh',
  return_url: 'https://example.com/onboarding/complete',
  type: 'account_onboarding'
});
// Redirect vendor to accountLink.url
```
