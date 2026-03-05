# Payment Integration Patterns

## Checkout Flow Options

### Hosted Checkout (Recommended for most)
Provider handles the payment form. You redirect to their page.
- **Stripe:** Checkout Sessions
- **Paddle:** Paddle.js overlay or redirect
- **LemonSqueezy:** Hosted checkout links

**Pros:** PCI compliant by default, less code, provider handles UX
**Cons:** Less brand control, redirect can lose conversions

### Embedded Elements
Payment form embedded in your site using provider components.
- **Stripe:** Payment Element, Card Element
- **Paddle:** Paddle.js inline

**Pros:** Seamless UX, stays on your site
**Cons:** More integration work, still need to handle states

### Custom Form (Avoid unless required)
You build the form, tokenize via provider SDK.
- Only if you have specific UX requirements
- More PCI responsibility
- More things to break

---

## Webhook Architecture

**Webhooks are the source of truth.** Don't trust client-side callbacks.

### Essential Webhooks to Handle

| Event | Action |
|-------|--------|
| `payment_intent.succeeded` | Fulfill order, grant access |
| `payment_intent.payment_failed` | Notify user, retry logic |
| `invoice.paid` | Update subscription status |
| `customer.subscription.updated` | Handle plan changes |
| `customer.subscription.deleted` | Revoke access |
| `charge.refunded` | Reverse fulfillment |
| `charge.dispute.created` | Alert team, gather evidence |

### Webhook Security

```plaintext
1. Verify webhook signature (provider-specific)
2. Use HTTPS endpoint
3. Return 200 quickly, process async if slow
4. Implement idempotency (handle duplicate events)
5. Log raw payloads for debugging
```

### Webhook Failure Handling

Providers retry failed webhooks. Your endpoint must be:
- Idempotent (same event processed twice = same result)
- Fast (return 200 within 5-30 seconds)
- Resilient (queue for async processing if needed)

---

## Currency and Amount Handling

**Always store amounts in smallest unit (cents, pence).**

```plaintext
✅ $10.00 = 1000 (cents)
✅ €25.50 = 2550 (cents)
❌ $10.00 = 10.00 (floating point disasters)
```

**Display vs Storage:**
- Store: 1000 (integer, cents)
- Display: $10.00 (formatted for user)
- Never calculate on floating point prices

---

## Idempotency

**Every charge request must include an idempotency key.**

Without idempotency:
- Network timeout → You don't know if charge succeeded
- Retry → Possible double charge
- Angry customer + chargeback

With idempotency:
- Same key = same result (no duplicate charges)
- Safe to retry on any failure

```plaintext
Key format: "{order_id}_{timestamp}" or UUID
Store with order to prevent reuse
```

---

## Error Handling

| Error Type | User Action | Your Action |
|------------|-------------|-------------|
| Card declined | Try different card | Log, show clear error |
| Insufficient funds | Try different card | Same as declined |
| Expired card | Update card | Prompt card update |
| Fraud suspected | Contact bank | Block + manual review |
| Processing error | Retry | Retry with backoff, alert if persistent |

**Never expose raw error codes to users.** Map to friendly messages:
- "Your card was declined" not "card_declined"
- "Please try again" not "processing_error"

---

## Testing Checklist

- [ ] Successful payment flow (happy path)
- [ ] Declined card handling
- [ ] Webhook receives and processes events
- [ ] Duplicate webhook handling (idempotency)
- [ ] Refund flow works correctly
- [ ] 3D Secure flow (if applicable)
- [ ] Currency edge cases (JPY has no cents)
- [ ] Cancellation and proration
