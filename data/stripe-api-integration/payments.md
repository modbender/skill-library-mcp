# Payment Intents & Methods — Stripe API

## Payment Intents

### Create Payment Intent
```bash
curl https://api.stripe.com/v1/payment_intents \
  -u "$STRIPE_SECRET_KEY:" \
  -d "amount=2000" \
  -d "currency=usd" \
  -d "customer=cus_XXX" \
  -d "payment_method_types[]=card" \
  -d "metadata[order_id]=6735"
```

### Confirm Payment Intent
```bash
curl https://api.stripe.com/v1/payment_intents/pi_XXX/confirm \
  -u "$STRIPE_SECRET_KEY:" \
  -d "payment_method=pm_XXX"
```

### Capture Payment Intent (manual capture)
```bash
curl https://api.stripe.com/v1/payment_intents/pi_XXX/capture \
  -u "$STRIPE_SECRET_KEY:"
```

### Cancel Payment Intent
```bash
curl https://api.stripe.com/v1/payment_intents/pi_XXX/cancel \
  -u "$STRIPE_SECRET_KEY:"
```

### List Payment Intents
```bash
curl "https://api.stripe.com/v1/payment_intents?customer=cus_XXX&limit=10" \
  -u "$STRIPE_SECRET_KEY:"
```

---

## Payment Methods

### List Payment Methods
```bash
curl "https://api.stripe.com/v1/payment_methods?customer=cus_XXX&type=card" \
  -u "$STRIPE_SECRET_KEY:"
```

### Get Payment Method
```bash
curl https://api.stripe.com/v1/payment_methods/pm_XXX \
  -u "$STRIPE_SECRET_KEY:"
```

### Attach to Customer
```bash
curl https://api.stripe.com/v1/payment_methods/pm_XXX/attach \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX"
```

### Detach from Customer
```bash
curl https://api.stripe.com/v1/payment_methods/pm_XXX/detach \
  -u "$STRIPE_SECRET_KEY:"
```

---

## Setup Intents (Save Cards)

### Create Setup Intent
```bash
curl https://api.stripe.com/v1/setup_intents \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_XXX" \
  -d "payment_method_types[]=card"
```

### Confirm Setup Intent
```bash
curl https://api.stripe.com/v1/setup_intents/seti_XXX/confirm \
  -u "$STRIPE_SECRET_KEY:" \
  -d "payment_method=pm_XXX"
```

---

## Refunds

### Full Refund
```bash
curl https://api.stripe.com/v1/refunds \
  -u "$STRIPE_SECRET_KEY:" \
  -d "payment_intent=pi_XXX"
```

### Partial Refund
```bash
curl https://api.stripe.com/v1/refunds \
  -u "$STRIPE_SECRET_KEY:" \
  -d "payment_intent=pi_XXX" \
  -d "amount=500"
```

### Refund with Reason
```bash
curl https://api.stripe.com/v1/refunds \
  -u "$STRIPE_SECRET_KEY:" \
  -d "payment_intent=pi_XXX" \
  -d "reason=requested_by_customer"
```

Reasons: `duplicate`, `fraudulent`, `requested_by_customer`

---

## Disputes (Chargebacks)

### List Disputes
```bash
curl "https://api.stripe.com/v1/disputes?limit=10" \
  -u "$STRIPE_SECRET_KEY:"
```

### Submit Evidence
```bash
curl https://api.stripe.com/v1/disputes/dp_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "evidence[customer_name]=John Doe" \
  -d "evidence[customer_email]=john@example.com" \
  -d "evidence[product_description]=Premium subscription"
```

### Accept Dispute (Close)
```bash
curl https://api.stripe.com/v1/disputes/dp_XXX/close \
  -u "$STRIPE_SECRET_KEY:"
```

---

## Balance

### Get Balance
```bash
curl https://api.stripe.com/v1/balance \
  -u "$STRIPE_SECRET_KEY:"
```

### List Balance Transactions
```bash
curl "https://api.stripe.com/v1/balance_transactions?limit=10" \
  -u "$STRIPE_SECRET_KEY:"
```

### Create Payout
```bash
curl https://api.stripe.com/v1/payouts \
  -u "$STRIPE_SECRET_KEY:" \
  -d "amount=10000" \
  -d "currency=usd"
```

---

## ID Prefixes Reference

| Prefix | Resource |
|--------|----------|
| `pi_` | Payment Intent |
| `pm_` | Payment Method |
| `seti_` | Setup Intent |
| `ch_` | Charge |
| `re_` | Refund |
| `dp_` | Dispute |
| `po_` | Payout |
