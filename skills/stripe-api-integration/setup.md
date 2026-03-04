# Setup — Stripe API Integration

This file guides the initial configuration when the user first uses this skill.

## Integration

Ask how they want to use Stripe:
- "Are you building subscriptions, one-time payments, or both?"
- "Do you have a Stripe account already, or starting fresh?"
- "Want me to help whenever payments come up, or only when you ask?"

## Understand Their Use Case

- What are they selling? (SaaS, products, services)
- Who are their customers? (B2B, B2C, marketplace)
- What payment flows do they need? (checkout, invoices, subscriptions)

## Technical Context

- What's their stack? (Node, Python, Ruby, etc.)
- Are they using Stripe already or migrating?
- Do they need Connect for marketplace payments?

## Memory Storage

Store context in `~/stripe-api-integration/memory.md`:
- Their primary use case (subscriptions, one-time, both)
- Their customer type (B2B/B2C/marketplace)
- Their tech stack if mentioned
- Test vs live mode preference
- Any specific patterns they've established

## When Ready

Once you know:
1. What they're building (subscriptions, payments, etc.)
2. Basic technical context

...you're ready to help. Details emerge naturally through use.
