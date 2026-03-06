# stripe

A OpenClaw skill for querying and managing your Stripe account — directly via `api.stripe.com`, no third-party proxy.

## What it does

Ask OpenClaw things like:

> "Show me the last 10 charges"  
> "Find the customer with email john@acme.com"  
> "List all active subscriptions"  
> "Refund charge ch_abc123"  
> "Update customer cus_abc123's email"

## Setup

**1. Get your Stripe secret key**

Go to [dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys) and copy your secret key.

- `sk_test_...` for test mode
- `sk_live_...` for production

**2. Set the environment variable**

```bash
export STRIPE_SECRET_KEY=sk_live_...
```

## Supported resources

| Resource | List | Get | Create | Update |
|---|---|---|---|---|
| charges | ✅ | ✅ | | |
| customers | ✅ | ✅ | | ✅ |
| invoices | ✅ | ✅ | | |
| subscriptions | ✅ | ✅ | | |
| payment_intents | ✅ | ✅ | | |
| refunds | ✅ | ✅ | ✅ | |
| products | ✅ | ✅ | | |
| prices | ✅ | ✅ | | |
| balance_transactions | ✅ | ✅ | | |

## Usage

### List resources

```bash
python3 scripts/stripe_query.py charges --limit 10
python3 scripts/stripe_query.py customers --limit 20
python3 scripts/stripe_query.py subscriptions --status active
python3 scripts/stripe_query.py invoices
python3 scripts/stripe_query.py payment_intents
python3 scripts/stripe_query.py products
python3 scripts/stripe_query.py prices
python3 scripts/stripe_query.py refunds
python3 scripts/stripe_query.py balance_transactions
```

**Filters**

```bash
--limit N          # number of results (default: 20)
--email EMAIL      # filter customers by email
--status STATUS    # filter by status (e.g. active, canceled, paid)
--customer ID      # filter by customer ID
--json             # output raw JSON instead of table
```

### Get a specific object

```bash
python3 scripts/stripe_query.py get charges ch_abc123
python3 scripts/stripe_query.py get customers cus_abc123
python3 scripts/stripe_query.py get subscriptions sub_abc123
```

### Create a refund

```bash
# Full refund
python3 scripts/stripe_query.py create refunds --charge ch_abc123

# Partial refund (amount in cents)
python3 scripts/stripe_query.py create refunds --charge ch_abc123 --amount 1000
```

### Update a customer

```bash
python3 scripts/stripe_query.py update customers cus_abc123 --email new@example.com
python3 scripts/stripe_query.py update customers cus_abc123 --name "Jane Doe"
```

## Requirements

- Python 3 (stdlib only, no pip installs)
- `STRIPE_SECRET_KEY` environment variable

## How it works

All requests go directly to `https://api.stripe.com/v1` using your secret key as a Bearer token. No intermediary services, no OAuth flow, no additional dependencies.
