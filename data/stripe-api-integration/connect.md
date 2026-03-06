# Stripe Connect — Marketplace Payments

## Connect Account Types

| Type | Control | Onboarding | Payouts | Use Case |
|------|---------|------------|---------|----------|
| Standard | Low | Stripe-hosted | Direct to account | Independent businesses |
| Express | Medium | Stripe-hosted | Platform controls | Gig workers, sellers |
| Custom | Full | Build your own | Platform controls | White-label platforms |

## Create Connected Account

### Express Account
```bash
curl https://api.stripe.com/v1/accounts \
  -u "$STRIPE_SECRET_KEY:" \
  -d "type=express" \
  -d "country=US" \
  -d "email=seller@example.com" \
  -d "capabilities[card_payments][requested]=true" \
  -d "capabilities[transfers][requested]=true"
```

### Standard Account
```bash
curl https://api.stripe.com/v1/accounts \
  -u "$STRIPE_SECRET_KEY:" \
  -d "type=standard" \
  -d "country=US" \
  -d "email=merchant@example.com"
```

### Custom Account
```bash
curl https://api.stripe.com/v1/accounts \
  -u "$STRIPE_SECRET_KEY:" \
  -d "type=custom" \
  -d "country=US" \
  -d "email=user@example.com" \
  -d "capabilities[card_payments][requested]=true" \
  -d "capabilities[transfers][requested]=true" \
  -d "business_type=individual"
```

## Account Onboarding

### Create Account Link (Express/Custom)
```bash
curl https://api.stripe.com/v1/account_links \
  -u "$STRIPE_SECRET_KEY:" \
  -d "account=acct_XXX" \
  -d "refresh_url=https://example.com/reauth" \
  -d "return_url=https://example.com/return" \
  -d "type=account_onboarding"
```

### Check Onboarding Status
```bash
curl https://api.stripe.com/v1/accounts/acct_XXX \
  -u "$STRIPE_SECRET_KEY:"

# Check: charges_enabled, payouts_enabled, requirements
```

## Payment Flows

### Direct Charge (Funds go to connected account)
```bash
curl https://api.stripe.com/v1/payment_intents \
  -u "$STRIPE_SECRET_KEY:" \
  -H "Stripe-Account: acct_XXX" \
  -d "amount=10000" \
  -d "currency=usd" \
  -d "application_fee_amount=1000"
```

### Destination Charge (Funds go to platform, then transferred)
```bash
curl https://api.stripe.com/v1/payment_intents \
  -u "$STRIPE_SECRET_KEY:" \
  -d "amount=10000" \
  -d "currency=usd" \
  -d "transfer_data[destination]=acct_XXX" \
  -d "transfer_data[amount]=9000"
```

### Separate Charges and Transfers
```bash
# 1. Charge customer
curl https://api.stripe.com/v1/payment_intents \
  -u "$STRIPE_SECRET_KEY:" \
  -d "amount=10000" \
  -d "currency=usd"

# 2. Transfer to connected account
curl https://api.stripe.com/v1/transfers \
  -u "$STRIPE_SECRET_KEY:" \
  -d "amount=9000" \
  -d "currency=usd" \
  -d "destination=acct_XXX" \
  -d "source_transaction=ch_XXX"
```

## Application Fees

### On Direct Charge
```bash
-d "application_fee_amount=1000"
```

### On Destination Charge
```bash
-d "transfer_data[amount]=9000"  # Platform keeps 10000-9000 = 1000
```

## Payouts to Connected Accounts

### Create Payout (for Express/Custom)
```bash
curl https://api.stripe.com/v1/payouts \
  -u "$STRIPE_SECRET_KEY:" \
  -H "Stripe-Account: acct_XXX" \
  -d "amount=10000" \
  -d "currency=usd"
```

### Check Account Balance
```bash
curl https://api.stripe.com/v1/balance \
  -u "$STRIPE_SECRET_KEY:" \
  -H "Stripe-Account: acct_XXX"
```

## Refunds with Connect

### Refund Direct Charge (Refund from connected account)
```bash
curl https://api.stripe.com/v1/refunds \
  -u "$STRIPE_SECRET_KEY:" \
  -H "Stripe-Account: acct_XXX" \
  -d "charge=ch_XXX"
```

### Refund Destination Charge (Reverse transfer too)
```bash
curl https://api.stripe.com/v1/refunds \
  -u "$STRIPE_SECRET_KEY:" \
  -d "charge=ch_XXX" \
  -d "reverse_transfer=true"
```

### Refund Application Fee
```bash
curl https://api.stripe.com/v1/refunds \
  -u "$STRIPE_SECRET_KEY:" \
  -d "charge=ch_XXX" \
  -d "refund_application_fee=true"
```

## Express Dashboard

### Create Login Link
```bash
curl https://api.stripe.com/v1/accounts/acct_XXX/login_links \
  -u "$STRIPE_SECRET_KEY:"
```

Redirects to Express dashboard where sellers can:
- View balance and payouts
- Update banking info
- See transaction history

## Account Updates

### Update Connected Account
```bash
curl https://api.stripe.com/v1/accounts/acct_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "business_profile[url]=https://seller.example.com" \
  -d "business_profile[mcc]=5734"
```

### Delete Connected Account
```bash
curl -X DELETE https://api.stripe.com/v1/accounts/acct_XXX \
  -u "$STRIPE_SECRET_KEY:"
```

## Connect Webhooks

| Event | When | Action |
|-------|------|--------|
| `account.updated` | Account status changes | Check charges_enabled |
| `account.application.authorized` | OAuth authorized | Store account ID |
| `account.application.deauthorized` | OAuth revoked | Disable features |
| `payout.paid` | Payout sent | Notify seller |
| `payout.failed` | Payout failed | Alert and retry |

## Common Patterns

### Split Payment (Multiple Sellers)
```bash
# Pay to platform, then transfer to multiple accounts
curl https://api.stripe.com/v1/payment_intents \
  -u "$STRIPE_SECRET_KEY:" \
  -d "amount=10000" \
  -d "currency=usd"

# Transfer to Seller A
curl https://api.stripe.com/v1/transfers \
  -u "$STRIPE_SECRET_KEY:" \
  -d "amount=4000" \
  -d "destination=acct_SELLER_A" \
  -d "source_transaction=ch_XXX"

# Transfer to Seller B
curl https://api.stripe.com/v1/transfers \
  -u "$STRIPE_SECRET_KEY:" \
  -d "amount=5000" \
  -d "destination=acct_SELLER_B" \
  -d "source_transaction=ch_XXX"

# Platform keeps 1000
```

### Hold and Release
```bash
# Create transfer with manual payout timing
curl https://api.stripe.com/v1/accounts/acct_XXX \
  -u "$STRIPE_SECRET_KEY:" \
  -d "settings[payouts][schedule][delay_days]=manual"

# Later, trigger payout
curl https://api.stripe.com/v1/payouts \
  -u "$STRIPE_SECRET_KEY:" \
  -H "Stripe-Account: acct_XXX" \
  -d "amount=5000" \
  -d "currency=usd"
```
