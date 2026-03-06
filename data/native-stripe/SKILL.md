---
name: stripe
description: "Query and manage Stripe data via the Stripe API. Use when you need to list charges, customers, invoices, subscriptions, payment intents, refunds, products, or prices. Supports filtering, pagination, and creating/updating customers and refunds. Calls api.stripe.com directly with no third-party proxy."
metadata:
  openclaw:
    requires:
      env:
        - STRIPE_SECRET_KEY
      bins:
        - python3
    primaryEnv: STRIPE_SECRET_KEY
    files:
      - "scripts/*"
---

# Stripe

Interact with your Stripe account directly via the Stripe API (`api.stripe.com`).

## Setup (one-time)

1. Get your secret key from https://dashboard.stripe.com/apikeys
2. Set environment variable:
   ```
   STRIPE_SECRET_KEY=sk_live_...
   ```
   Use `sk_test_...` for test mode.

## Queries

### List recent charges
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py charges --limit 10
```

### List customers
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py customers --limit 20
```

### Search customers by email
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py customers --email user@example.com
```

### List subscriptions
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py subscriptions --limit 20
```

### List active subscriptions
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py subscriptions --status active --limit 20
```

### List invoices
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py invoices --limit 20
```

### List payment intents
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py payment_intents --limit 20
```

### List products
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py products --limit 20
```

### List prices
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py prices --limit 20
```

### List refunds
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py refunds --limit 20
```

### Get a specific object
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py get charges ch_abc123
python3 /mnt/skills/user/stripe/scripts/stripe_query.py get customers cus_abc123
python3 /mnt/skills/user/stripe/scripts/stripe_query.py get subscriptions sub_abc123
```

### Create a refund
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py create refunds --charge ch_abc123
python3 /mnt/skills/user/stripe/scripts/stripe_query.py create refunds --charge ch_abc123 --amount 1000
```

### Update a customer
```bash
python3 /mnt/skills/user/stripe/scripts/stripe_query.py update customers cus_abc123 --email new@example.com --name "New Name"
```

## Output
Formatted table for lists, JSON for single objects. Use `--json` flag for raw JSON on any command.

## Resources
- charges, customers, invoices, subscriptions, payment_intents, refunds, products, prices, balance_transactions
