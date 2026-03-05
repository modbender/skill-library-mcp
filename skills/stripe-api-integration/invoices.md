# Invoices & Billing — Stripe API

## Invoices

### Create Invoice
```bash
curl https://api.stripe.com/v1/invoices \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX" \
  -d "auto_advance=false"
```

### Add Invoice Item
```bash
curl https://api.stripe.com/v1/invoiceitems \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX" \
  -d "price=price_XXX" \
  -d "invoice=in_XXX"
```

### Finalize Invoice
```bash
curl https://api.stripe.com/v1/invoices/in_XXX/finalize \
  -u "$STRIPE_SECRET_KEY:"
```

### Send Invoice
```bash
curl https://api.stripe.com/v1/invoices/in_XXX/send \
  -u "$STRIPE_SECRET_KEY:"
```

### Pay Invoice
```bash
curl https://api.stripe.com/v1/invoices/in_XXX/pay \
  -u "$STRIPE_SECRET_KEY:"
```

### Void Invoice
```bash
curl https://api.stripe.com/v1/invoices/in_XXX/void \
  -u "$STRIPE_SECRET_KEY:"
```

### Mark Uncollectible
```bash
curl https://api.stripe.com/v1/invoices/in_XXX/mark_uncollectible \
  -u "$STRIPE_SECRET_KEY:"
```

### List Invoices
```bash
curl "https://api.stripe.com/v1/invoices?customer=cus_XXX&status=paid" \
  -u "$STRIPE_SECRET_KEY:"
```

Status: `draft`, `open`, `paid`, `void`, `uncollectible`

---

## Billing Portal

### Create Portal Session
```bash
curl https://api.stripe.com/v1/billing_portal/sessions \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX" \
  -d "return_url=https://example.com/account"
```

Portal allows customers to:
- Update payment methods
- View invoice history
- Cancel/pause subscriptions
- Download invoices

Configure in Dashboard > Settings > Billing > Customer Portal

---

## Quotes

### Create Quote
```bash
curl https://api.stripe.com/v1/quotes \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX" \
  -d "line_items[0][price]=price_XXX" \
  -d "line_items[0][quantity]=1"
```

### Finalize Quote
```bash
curl https://api.stripe.com/v1/quotes/qt_XXX/finalize \
  -u "$STRIPE_SECRET_KEY:"
```

### Accept Quote
```bash
curl https://api.stripe.com/v1/quotes/qt_XXX/accept \
  -u "$STRIPE_SECRET_KEY:"
```

---

## Stripe Tax

### Create Tax Calculation
```bash
curl https://api.stripe.com/v1/tax/calculations \
  -u "$STRIPE_SECRET_KEY:" \
  -d "currency=usd" \
  -d "line_items[0][amount]=1000" \
  -d "line_items[0][reference]=L1" \
  -d "customer_details[address][country]=US" \
  -d "customer_details[address][state]=CA"
```

### Enable Tax on Checkout
```bash
curl https://api.stripe.com/v1/checkout/sessions \
  -u "$STRIPE_SECRET_KEY:" \
  -d "mode=payment" \
  -d "automatic_tax[enabled]=true" \
  -d "line_items[0][price]=price_XXX" \
  -d "line_items[0][quantity]=1" \
  -d "success_url=https://example.com/success" \
  -d "cancel_url=https://example.com/cancel"
```

---

## Usage-Based Billing (Meters)

### Create Meter
```bash
curl https://api.stripe.com/v1/billing/meters \
  -u "$STRIPE_SECRET_KEY:" \
  -d "display_name=API Calls" \
  -d "event_name=api_call" \
  -d "default_aggregation[formula]=sum"
```

### Report Usage Event
```bash
curl https://api.stripe.com/v1/billing/meter_events \
  -u "$STRIPE_SECRET_KEY:" \
  -d "event_name=api_call" \
  -d "payload[stripe_customer_id]=cus_XXX" \
  -d "payload[value]=100"
```

### Create Metered Price
```bash
curl https://api.stripe.com/v1/prices \
  -u "$STRIPE_SECRET_KEY:" \
  -d "product=prod_XXX" \
  -d "currency=usd" \
  -d "recurring[interval]=month" \
  -d "recurring[usage_type]=metered" \
  -d "recurring[meter]=mtr_XXX" \
  -d "unit_amount=1"
```

---

## Subscription Schedules

### Create Schedule (Future Start)
```bash
curl https://api.stripe.com/v1/subscription_schedules \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX" \
  -d "start_date=$(date -d '+7 days' +%s)" \
  -d "end_behavior=release" \
  -d "phases[0][items][0][price]=price_XXX" \
  -d "phases[0][iterations]=1"
```

### Schedule Upgrade
```bash
curl https://api.stripe.com/v1/subscription_schedules \
  -u "$STRIPE_SECRET_KEY:" \
  -d "from_subscription=sub_XXX" \
  -d "phases[0][items][0][price]=price_BASIC" \
  -d "phases[0][iterations]=3" \
  -d "phases[1][items][0][price]=price_PRO" \
  -d "phases[1][iterations]=12"
```

---

## ID Prefixes Reference

| Prefix | Resource |
|--------|----------|
| `in_` | Invoice |
| `ii_` | Invoice Item |
| `qt_` | Quote |
| `sub_sched_` | Subscription Schedule |
| `mtr_` | Meter |
