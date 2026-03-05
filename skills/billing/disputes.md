# Chargebacks & Disputes

## Dispute Lifecycle

```
┌────────────┐     ┌─────────────┐     ┌─────────────┐
│  Inquiry   │────►│   Dispute   │────►│  Decision   │
│ (optional) │     │   Opened    │     │             │
└────────────┘     └──────┬──────┘     └─────────────┘
     │                    │
     │                    ▼
     │              Evidence Due
     │              (7-21 days)
     │                    │
     └────────────────────┘
            Resolved early
```

## Evidence Submission

```typescript
await stripe.disputes.update(disputeId, {
  evidence: {
    customer_name: 'John Doe',
    customer_email_address: 'john@example.com',
    billing_address: '123 Main St...',
    
    // Transaction proof
    receipt: 'file_xxx', // Upload receipt PDF
    customer_signature: 'file_xxx', // If applicable
    
    // Service proof
    service_date: '2024-03-15',
    service_documentation: 'file_xxx', // Logs, screenshots
    
    // Shipping proof (physical goods)
    shipping_carrier: 'FedEx',
    shipping_tracking_number: '123456789',
    shipping_documentation: 'file_xxx',
    
    // Policy acknowledgment
    refund_policy: 'Our refund policy states...',
    refund_policy_disclosure: 'file_xxx',
    
    // Narrative
    uncategorized_text: 'Customer purchased on X date...'
  }
});
```

## Friendly Fraud Detection

Pattern indicators:
- High LTV customer suddenly disputes
- Dispute after service fully rendered
- Multiple accounts, same payment method
- Dispute immediately after refund denied

```typescript
async function assessFraudRisk(dispute) {
  const customer = await getCustomer(dispute.customerId);
  
  const indicators = {
    highLTV: customer.totalSpend > 1000,
    serviceRendered: await wasServiceDelivered(dispute.chargeId),
    previousDisputes: customer.disputeCount > 0,
    recentRefundDenied: await wasRefundDenied(customer.id, 30) // days
  };
  
  const riskScore = Object.values(indicators).filter(Boolean).length;
  return riskScore >= 3 ? 'high_fraud_risk' : 'normal';
}
```

## PCI-DSS Compliance

### What You CAN Store
- PSP tokens (`pm_*`, `cus_*`)
- Last 4 digits (alone, not with expiry)
- Card brand
- Billing address

### What You CANNOT Store
- Full PAN (card number)
- CVV/CVC/CVV2
- Magnetic stripe data
- PIN/PIN block

### Implementation

```typescript
// GOOD: Token-based
const paymentMethod = await stripe.paymentMethods.create({
  type: 'card',
  card: { token: stripeJsToken } // From client-side
});

// BAD: Raw card data in your backend
// NEVER do this
const pm = await stripe.paymentMethods.create({
  card: { number: '4242...', exp_month: 12 } // PCI violation!
});
```

## 3D Secure (SCA Compliance)

Required in EU for transactions >€30 (with exemptions).

```typescript
const paymentIntent = await stripe.paymentIntents.create({
  amount: 5000,
  currency: 'eur',
  payment_method: pmId,
  confirmation_method: 'manual',
  confirm: true,
  return_url: 'https://example.com/return'
});

if (paymentIntent.status === 'requires_action') {
  // Redirect customer to 3DS challenge
  return { redirectUrl: paymentIntent.next_action.redirect_to_url.url };
}
```

## Chargeback Prevention

| Action | Impact |
|--------|--------|
| Clear billing descriptor | -30% "unrecognized charge" disputes |
| Pre-transaction auth | -20% fraud |
| Velocity checks | -15% card testing |
| AVS/CVV verification | -25% fraud |
| 3DS on high-risk | -50% fraud disputes |

```typescript
// Set clear descriptor
await stripe.charges.create({
  amount: 5000,
  source: sourceId,
  statement_descriptor: 'ACME*SUBSCRIPTION', // Shows on card statement
  statement_descriptor_suffix: 'MONTHLY' // Appended detail
});
```
