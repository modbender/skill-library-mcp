---
name: stripe-best-practices
description: Best practices for building Stripe payment integrations
metadata:
  version: "245b3bbb"
  type: knowledge
  format: uasp
---

# Stripe Best Practices

Best practices for building Stripe payment integrations

## Keywords

stripe, payment, checkout, subscription, billing

## Intents

- integrate payment processing
- handle subscriptions
- process credit cards

## Constraints

### Never

- Charges API
- Sources API
- Card Element
- Payment Element in card-only mode
- Tokens API (unless specific need)
- mixing Connect charge types
- legacy Connect terms (Standard/Express/Custom)

### Always

- latest API/SDK version (unless specified otherwise)
- advise PCI compliance proof for raw PAN handling
- use controller properties for Connect (not legacy terms)

### Preferences

- Prefer **CheckoutSessions** over PaymentIntents when on-session payments
- Prefer **Stripe-hosted Checkout** over embedded Checkout when default choice
- Prefer **embedded Checkout** over Payment Element when more control needed
- Prefer **dynamic payment methods** over explicit payment_method_types when using Payment Element
- Prefer **SetupIntents** over Sources when saving payment methods
- Prefer **Confirmation Tokens** over createPaymentMethod/createToken when inspecting card before payment
- Prefer **Billing APIs** over raw PaymentIntents when subscriptions/recurring
- Prefer **direct charges** over destination charges when platform wants Stripe to take risk
- Prefer **destination charges** over direct charges when platform accepts liability

## Decisions

- **When** user wants Charges API: advise migration to CheckoutSessions or PaymentIntents
- **When** user wants Card Element: advise migration to Payment Element
- **When** recurring revenue / subscription / SaaS: recommend Billing APIs + Checkout frontend
- **When** platform / marketplace / Connect: follow integration recommendations, use controller properties
- **When** migrating PAN data from another processor: point to migration process
- **When** render Payment Element before creating intent: use Confirmation Tokens

## References

- [stripe:integration-options](https://docs.stripe.com/payments/payment-methods/integration-options) - primary integration design reference
- [stripe:api-tour](https://docs.stripe.com/payments-api/tour) - API overview
- [stripe:go-live](https://docs.stripe.com/get-started/checklist/go-live) - pre-launch checklist
- [stripe:migration/charges](https://docs.stripe.com/payments/payment-intents/migration/charges) - Charges to PaymentIntents migration
- [stripe:migration/payment-element](https://docs.stripe.com/payments/payment-element/migration) - Card Element to Payment Element migration
- [stripe:billing/design-integration](https://docs.stripe.com/billing/subscriptions/designing-integration) - subscription integration planning
- [stripe:connect/recommendations](https://docs.stripe.com/connect/integration-recommendations) - Connect charge type selection
- [stripe:pan-import](https://docs.stripe.com/get-started/data-migrations/pan-import) - PAN data migration

---

*Converted from UASP format (knowledge skill)*