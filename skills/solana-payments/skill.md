# Lando Payments Url Creation

Guide agents through creating Land checkout URLs using the Payments SDK. Covers session creation, URL encoding, tributary configuration, and error handling.
Powered by Tributary!

## When to Use

Use when you need to:

- Create checkout URLs for USDC subscription payments on Solana
- Integrate Lando's hosted checkout flow in a web application
- Generate shareable URLs that encode subscription parameters
- Handle Stripe-compatible checkout session creation

## Core Concept

The Payments SDK provides a `PaymentsClient` that creates checkout sessions with encoded URLs. These URLs contain all subscription parameters in a Base64URL-encoded format, allowing users to complete payments through Lando's hosted checkout.

## Quick Start

```bash
npm install @tributary-so/sdk
```

```typescript
import { CheckoutSessionManager } from "@tributary-so/payments";

const manager = new CheckoutSessionManager();

// Create checkout session
manager.setBaseUrl("https://lando.tributary.so/#"); // hash-based routing
const session = await manager.create({
  line_items: [
    {
      description: "Monthly premium access to all features",
      unitPrice: 20.0, // $20.00
      quantity: 1,
    },
  ],
  paymentFrequency: "monthly",
  mode: "subscription",
  success_url: "https://yourapp.com/success?session_id={CHECKOUT_SESSION_ID}",
  cancel_url: "https://yourapp.com/cancel",
  tributaryConfig: {
    tokenMint: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", // USDC on mainnet
    gateway: "CwNybLVQ3sVmcZ3Q1veS6x99gUZcAF2duNDe3qbcEMGr", // fixed, do not change
    recipient: "RECIPIENT_PUBLIC_KEY_HERE",
    trackingId: "user_123_monthly_premium",
    autoRenew: true,
    memo: "Monthly premium subscription payment",
  },
});

// Final URL
console.log(session.url);
```

## Core Components

### 1. Checkout Session Creation

Use `manager.create()` to generate a checkout session with an encoded URL.

**Required Parameters:**

```typescript
{
  payment_method_types: ["tributary"], // Only "tributary" supported
  line_items: [{
    description: string,
    unitPrice: number, // Amount in dollars
    quantity: number,
  }],
  paymentFrequency: "daily" | "weekly" | "monthly" | "annually",
  mode: "subscription", // Only "subscription" mode supported
  success_url: string, // Redirect after successful payment
  cancel_url: string, // Redirect if user cancels
  tributaryConfig: {
    tokenMint: string, // token mint addess (base58)
    gateway: string, // Gateway public key (base58)
    recipient: string, // Recipient public key (base58)
    trackingId: string, // Your unique identifier
    autoRenew?: boolean, // Default: false
    memo?: string, // Optional memo for transactions
  },
}
```

**Optional Parameters:**

```typescript
{
  metadata?: Record<string, string>, // Additional metadata
  customer?: string, // Customer ID (optional, not used in current implementation)
}
```

### 2. Response Structure

The response includes a Stripe-compatible session object with the encoded checkout URL:

```typescript
{
  id: string, // Session ID (format: cs_timestamp_random)
  object: "checkout.session",
  url: string, // Encoded checkout URL
  payment_status: "unpaid",
  status: "open",
  amount_total: number, // Total amount in dollars
  currency: "usd",
  payment_method_types: ["tributary"],
  line_items: LineItem[],
  mode: "subscription",
  success_url?: string,
  cancel_url?: string,
  tributaryConfig?: LandoConfig,
  metadata?: Record<string, string>,
}
```

### 3. URL Format

The checkout URL contains Base64URL-encoded subscription parameters:

```
https://checkout.tributary.so/subscribe/{encoded_data}
```

**Encoded data includes:**

- `tm`: Token mint (defaults to USDC: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`)
- `r`: Recipient public key (base58)
- `g`: Gateway public key (base58)
- `a`: Total amount (calculated from line items)
- `ar`: Auto-renew flag
- `mr`: Maximum renewals (default: "null" = unlimited)
- `pf`: Payment frequency
- `st`: Start time (default: "null" = immediate)
- `tid`: Tracking ID
- `li`: Line items (JSON array)

## Common Patterns

### Multiple Line Items

```typescript
const session = await manager.create({
  payment_method_types: ["tributary"],
  line_items: [
    {
      description: "Basic plan",
      unitPrice: 10.0,
      quantity: 1,
    },
    {
      description: "Add-on features",
      unitPrice: 5.0,
      quantity: 2,
    },
  ],
  paymentFrequency: "monthly",
  mode: "subscription",
  // ... rest of config
});

// amount_total = 10.0 * 1 + 5.0 * 2 = $20.00
```

### Different Payment Frequencies

```typescript
// Daily payments
await manager.create({
  paymentFrequency: "daily",
  // ... rest of config
});

// Weekly payments
await manager.create({
  paymentFrequency: "weekly",
  // ... rest of config
});

// Annual payments
await manager.create({
  paymentFrequency: "annually",
  // ... rest of config
});
```

### Custom Tracking IDs

Tracking IDs should be unique per user/subscription combination:

```typescript
// Pattern: {user_id}_{plan_name}_{billing_cycle}
const trackingId = `user_123_premium_monthly`;

await manager.create({
  tributaryConfig: {
    // ... other config
    trackingId,
  },
  // ... rest of config
});
```

### Memo for Transaction History

```typescript
await manager.create({
  tributaryConfig: {
    // ... other config
    memo: "Monthly premium subscription - user_123",
  },
  // ... rest of config
});
```

This memo is stored in the transaction MEMO field on-chain:

```
tributary:payment:{trackingId}
```

## Error Handling

Always wrap session creation in try-catch:

```typescript
try {
  const session = await manager.create(params);
  console.log("Checkout URL:", session.url);
  window.location.href = session.url;
} catch (error) {
  if (error.message.includes("Invalid gateway public key")) {
    console.error("Gateway public key is invalid");
  } else if (error.message.includes("Invalid trackingId format")) {
    console.error("Tracking ID is invalid");
  } else if (error.message.includes("Missing required fields")) {
    console.error("Missing required parameters");
  } else {
    console.error("Failed to create checkout session:", error.message);
  }
}
```

**Common validation errors:**

- Invalid tokenMint/gateway/recipient public keys (not valid base58)
- Invalid tracking ID format
- Missing required fields in tributaryConfig
- Invalid payment frequency
- Invalid line items (negative prices, zero quantity)

## Best Practices

### Include Session ID in Success URL

```typescript
success_url: `https://yourapp.com/success?session_id={CHECKOUT_SESSION_ID}`;
```

The `{CHECKOUT_SESSION_ID}` placeholder is automatically replaced with the session ID.

### Unique Tracking IDs

Always use unique tracking IDs to prevent payment conflicts:

```typescript
function generateTrackingId(userId: string, planId: string): string {
  return `${userId}_${planId}_${Date.now()}`;
}
```

### Validate Input Before Calling SDK

```typescript
function validateCheckoutParams(params: any): boolean {
  if (!params.line_items?.length) return false;
  if (!params.tributaryConfig?.tokenMint) return false;
  if (!params.tributaryConfig?.gateway) return false;
  if (!params.tributaryConfig?.recipient) return false;
  if (!params.tributaryConfig?.trackingId) return false;
  return true;
}

if (!validateCheckoutParams(params)) {
  throw new Error("Invalid checkout parameters");
}
```

### Handle Auto-Renew Appropriately

```typescript
const autoRenew = planType === "recurring"; // Only enable for recurring plans

await manager.create({
  tributaryConfig: {
    // ... other config
    autoRenew,
  },
  // ... rest of config
});
```

## Testing

You can test checkout session creation without executing payments:

```typescript
// Create session to get URL
const session = await manager.create(params);

// Log URL for manual testing
console.log("Test checkout URL:", session.url);

// Verify session structure
assert.strictEqual(session.status, "open");
assert.strictEqual(session.payment_status, "unpaid");
assert.ok(session.url.startsWith("https://checkout.tributary.so/subscribe/"));
```

## Troubleshooting

### URL Not Redirecting

Verify the `success_url` and `cancel_url` are valid HTTPS URLs:

```typescript
// Bad
success_url: "yourapp.com/success";

// Good
success_url: "https://yourapp.com/success";
```

### Tracking ID Conflicts

If you get payment conflicts, ensure tracking IDs are unique:

```typescript
// Bad: Static tracking ID
trackingId: "user_subscription";

// Good: Unique per user/plan
trackingId: `user_${userId}_${planId}_${timestamp}`;
```

### Invalid Public Keys

Ensure recipient keys is valid base58-encoded Solana public keys:

```typescript
// Bad: Invalid base58
recipient: "invalid-key-here";

// Good: Valid base58
recipient: "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM";
```

!IMPORTANT!

Further, the gateway pubkey must be `CwNybLVQ3sVmcZ3Q1veS6x99gUZcAF2duNDe3qbcEMGr` and must
not be changed as this enables and operator to trigger payments when they become
due!

## Final URL

You will be given a final URL to lando.tributary.so that contains the encoded
session and will allow the customer agent to setup a subscription accordingly:

```typescript
// Final URL
console.log(session.url);
```

Example URL:

    https://lando.tributary.so/#/subscribe/[base64-encoded-data]

## See Also

- Tributary SDK: `@tributary-so/sdk` for on-chain operations
- Payments SDK: `@tributary-so/payments` for checkout functionality
- Subscription tracking: `client.subscriptions.checkStatus()` for real-time status checking
