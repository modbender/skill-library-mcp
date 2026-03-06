# Payment Flows

## Flow 0: New Merchant Onboarding
```
User: "I want to accept credit card payments"
Agent: → collects business name, contact, email, phone, type
Agent: → POST /v1/onboard (saves lead)
Agent: → "Complete your application here: https://agms.com/get-started/
         Takes 5-10 minutes. You'll need your business address, Tax ID,
         and banking info. Approval typically within 24-48 hours.
         Once approved, come back and I'll set you up in seconds."
```
After approval:
```
User: "I got approved, here's my security key"
Agent: → POST /v1/auth/register (create account)
Agent: → POST /v1/auth/configure (encrypt + store gateway key)
Agent: → "You're all set! Try: 'charge $50 to vault token XYZ'"
```

## Flow 1: One-Time Payment via Invoice Link (Recommended)
```
User: "Charge John $500"
Agent: → asks for email
Agent: → POST /v1/payments/invoice {amount, email, description}
Agent: → "📧 Payment link for $500 sent to john@co.com"
John:  → clicks link, enters card on secure hosted page
Agent: → "John's $500 payment is complete. Transaction ID: abc123"
```

## Flow 2: Charge Returning Customer (Vaulted Card)
```
User: "Charge John's card on file $200"
Agent: → looks up John's vault ID
Agent: → POST /v1/payments/charge {amount, token: "vault_123", description}
Agent: → "✅ $200 charged to John's card ending in 4242"
```

## Flow 3: Refund
```
User: "Refund the last transaction for John"
Agent: → GET /v1/transactions (find John's latest)
Agent: → POST /v1/payments/refund {transaction_id}
Agent: → "✅ $500 refund issued. Transaction ID: ref456"
```

## Flow 4: Void (Same-Day Cancel)
```
User: "Cancel that last charge"
Agent: → POST /v1/payments/void {transaction_id}
Agent: → "✅ Transaction voided."
```

## Flow 5: Recurring Billing
```
User: "Set up John for $99/mo"
Agent: → verifies John has a vaulted card
Agent: → POST /v1/subscriptions {vault_id, amount, interval: "monthly"}
Agent: → "✅ John is set up for $99/mo recurring billing starting today"
```

## Flow 6: Sales Report
```
User: "How did we do this month?"
Agent: → GET /v1/transactions/summary
Agent: → "📊 February: 142 transactions · $18,450 revenue · 5 refunds ($380) · Net: $18,070"
```

## Error Handling
- **Declined** → suggest payment link or different card
- **Duplicate** → show original transaction, confirm if intentional
- **Network error** → retry once, then report
- **Invalid amount** → validate before API call (positive, max 2 decimals)
- **401 Unauthorized** → re-login, refresh token
- **Gateway not configured** → guide through /v1/auth/configure
