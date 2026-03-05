# Customers & Products — Stripe API

## Customers

### List Customers
```bash
curl "https://api.stripe.com/v1/customers?limit=10&email=customer@example.com" \
  -u "$STRIPE_SECRET_KEY:"
```

Query parameters: `limit`, `starting_after`, `ending_before`, `email`, `created`

### Get Customer
```bash
curl https://api.stripe.com/v1/customers/cus_XXX \
  -u "$STRIPE_SECRET_KEY:"
```

### Create Customer
```bash
curl https://api.stripe.com/v1/customers \
  -u "$STRIPE_SECRET_KEY:" \
  -d "email=customer@example.com" \
  -d "name=John Doe" \
  -d "metadata[user_id]=123"
```

### Update Customer
```bash
curl https://api.stripe.com/v1/customers/cus_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "name=Jane Doe"
```

### Delete Customer
```bash
curl -X DELETE https://api.stripe.com/v1/customers/cus_XXX \
  -u "$STRIPE_SECRET_KEY:"
```

---

## Products

### List Products
```bash
curl "https://api.stripe.com/v1/products?limit=10&active=true" \
  -u "$STRIPE_SECRET_KEY:"
```

### Create Product
```bash
curl https://api.stripe.com/v1/products \
  -u "$STRIPE_SECRET_KEY:" \
  -d "name=Pro Plan" \
  -d "description=Full access to all features"
```

### Update Product
```bash
curl https://api.stripe.com/v1/products/prod_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "name=Updated Plan" \
  -d "active=true"
```

### Delete Product
```bash
curl -X DELETE https://api.stripe.com/v1/products/prod_XXX \
  -u "$STRIPE_SECRET_KEY:"
```

---

## Prices

### List Prices
```bash
curl "https://api.stripe.com/v1/prices?product=prod_XXX&active=true" \
  -u "$STRIPE_SECRET_KEY:"
```

### Create Recurring Price
```bash
curl https://api.stripe.com/v1/prices \
  -u "$STRIPE_SECRET_KEY:" \
  -d "product=prod_XXX" \
  -d "unit_amount=1999" \
  -d "currency=usd" \
  -d "recurring[interval]=month"
```

### Create One-time Price
```bash
curl https://api.stripe.com/v1/prices \
  -u "$STRIPE_SECRET_KEY:" \
  -d "product=prod_XXX" \
  -d "unit_amount=4999" \
  -d "currency=usd"
```

### Update Price
```bash
curl https://api.stripe.com/v1/prices/price_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "active=false"
```

---

## Coupons

### Create Percentage Coupon
```bash
curl https://api.stripe.com/v1/coupons \
  -u "$STRIPE_SECRET_KEY:" \
  -d "percent_off=25" \
  -d "duration=repeating" \
  -d "duration_in_months=3"
```

### Create Fixed Amount Coupon
```bash
curl https://api.stripe.com/v1/coupons \
  -u "$STRIPE_SECRET_KEY:" \
  -d "amount_off=1000" \
  -d "currency=usd" \
  -d "duration=once"
```

### Create Promotion Code
```bash
curl https://api.stripe.com/v1/promotion_codes \
  -u "$STRIPE_SECRET_KEY:" \
  -d "coupon=COUPON_ID" \
  -d "code=SUMMER25" \
  -d "max_redemptions=100"
```

---

## ID Prefixes Reference

| Prefix | Resource |
|--------|----------|
| `cus_` | Customer |
| `prod_` | Product |
| `price_` | Price |
| `pm_` | Payment Method |
