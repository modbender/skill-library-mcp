---
name: paypilot
description: Process payments, send invoices, issue refunds, manage subscriptions, and detect fraud via a secure payment gateway proxy. Use when a user asks to charge someone, send a payment link, check sales, issue a refund, create recurring billing, view fraud analytics, configure fraud rules, or manage any payment-related task. Supports 3D Secure, AVS/CVV verification, and risk scoring. Also use for merchant onboarding and first-time payment setup.
homepage: https://agms.com/paypilot/
source: https://github.com/agmsyumet/paypilot-skill
author: AGMS (Avant-Garde Marketing Solutions)
requires:
  tools: [curl, jq, mkdir, chmod]
  network: [paypilot.agms.com]
credentials:
  - name: PAYPILOT_EMAIL
    description: Your merchant email for the PayPilot API
  - name: PAYPILOT_PASSWORD
    description: Your merchant password (used only during login to obtain a JWT)
  - name: PAYPILOT_GATEWAY_KEY
    description: Your payment gateway security key (encrypted at rest on the server)
config:
  path: ~/.config/paypilot/config.json
  permissions: "600"
  contents: api_url, email, token (JWT)
---

# PayPilot — Payment Processing for AI Agents

Accept payments, send invoices, issue refunds, and track sales — all through conversation.

## Setup

PayPilot connects to a hosted API proxy at `https://paypilot.agms.com`. On first use, check for credentials:

```bash
cat ~/.config/paypilot/config.json
```

If no config exists, guide the user through setup:

1. **Register** on the PayPilot proxy:
```bash
curl -s "https://paypilot.agms.com/v1/auth/register" -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"BUSINESS_NAME","email":"EMAIL","password":"PASSWORD"}'
```

2. **Login** to get an access token:
```bash
curl -s "https://paypilot.agms.com/v1/auth/login" -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"EMAIL","password":"PASSWORD"}'
```

3. **Configure** the payment gateway key:
```bash
curl -s "https://paypilot.agms.com/v1/auth/configure" -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"gateway_key":"YOUR_GATEWAY_KEY"}'
```

4. **Save** credentials locally:
```bash
mkdir -p ~/.config/paypilot
cat > ~/.config/paypilot/config.json << 'EOF'
{
  "api_url": "https://paypilot.agms.com",
  "email": "merchant@example.com",
  "token": "jwt_token_here"
}
EOF
chmod 600 ~/.config/paypilot/config.json
```

If the user doesn't have a gateway account, start the onboarding process:

1. Collect basic info conversationally:
   - Business name
   - Contact name
   - Email
   - Phone
   - Business type (retail, restaurant, ecommerce, mobile, etc.)

2. Save the lead to our system:
```bash
curl -s "https://paypilot.agms.com/v1/onboard" -X POST \
  -H "Content-Type: application/json" \
  -d '{"business_name":"Acme Corp","contact_name":"John Doe","email":"john@acme.com","phone":"555-1234","business_type":"retail"}'
```

3. Send them the full application link to complete and e-sign:
> "Great! To finish your application, complete the form here: **https://agms.com/get-started/**
> It takes about 5-10 minutes. You'll need your business address, Tax ID, and banking info. After you submit, you'll e-sign right away and typically get approved within 24-48 hours.
> Once approved, come back and I'll set up your payment processing in seconds."

**Important:** The agent NEVER collects SSN, Tax ID, bank account/routing numbers, or other sensitive PII. Those go through the secure AGMS form only.

## Authentication

All payment endpoints require a JWT bearer token. Load config and set headers:

```bash
CONFIG=$(cat ~/.config/paypilot/config.json)
API=$(echo $CONFIG | jq -r '.api_url')
TOKEN=$(echo $CONFIG | jq -r '.token')
AUTH="Authorization: Bearer $TOKEN"
```

If a request returns 401, re-login and update the saved token.

To refresh an expired token:
```bash
# Re-login
LOGIN=$(curl -s "$API/v1/auth/login" -X POST \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$(echo $CONFIG | jq -r '.email')\",\"password\":\"YOUR_PASSWORD\"}")
NEW_TOKEN=$(echo $LOGIN | jq -r '.access_token')

# Update config
jq --arg t "$NEW_TOKEN" '.token = $t' ~/.config/paypilot/config.json > /tmp/pp.json && mv /tmp/pp.json ~/.config/paypilot/config.json
chmod 600 ~/.config/paypilot/config.json
```

## Core Commands

### Charge / Sale
Process a payment using a vaulted card token. **Never handle raw card numbers.**

```bash
curl -s "$API/v1/payments/charge" -X POST \
  -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"amount":500.00,"token":"VAULT_ID","description":"Consulting — January"}'
```

Enable 3D Secure for higher-value or flagged transactions:
```bash
curl -s "$API/v1/payments/charge" -X POST \
  -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"amount":2500.00,"token":"VAULT_ID","description":"Premium service","three_d_secure":true}'
```

The response includes risk assessment and verification:
```json
{
  "transaction_id": "123",
  "status": "complete",
  "amount": 2500,
  "risk": { "score": "low", "flags": [] },
  "verification": { "avs": "Y", "cvv": "M" },
  "three_d_secure": true
}
```

### Send Invoice / Payment Link
```bash
curl -s "$API/v1/payments/invoice" -X POST \
  -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"amount":500.00,"email":"john@example.com","description":"Consulting — January"}'
```

### Refund
```bash
# Full refund
curl -s "$API/v1/payments/refund" -X POST \
  -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"transaction_id":"TXN_ID"}'

# Partial refund
curl -s "$API/v1/payments/refund" -X POST \
  -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"transaction_id":"TXN_ID","amount":50.00}'
```

### Void (same-day cancel)
```bash
curl -s "$API/v1/payments/void" -X POST \
  -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"transaction_id":"TXN_ID"}'
```

### View Transactions
```bash
curl -s "$API/v1/transactions" -H "$AUTH" | jq .
```

### Sales Summary
```bash
curl -s "$API/v1/transactions/summary" -H "$AUTH" | jq .
```

### Customer Vault (Tokenize Cards Securely)
Store a card securely — returns a vault token. The customer enters card details through a secure form; raw card data never touches the agent.

```bash
curl -s "$API/v1/vault/add" -X POST \
  -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"first_name":"John","last_name":"Smith","email":"john@example.com"}'
```

### Charge a Vaulted Card
```bash
curl -s "$API/v1/vault/charge" -X POST \
  -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"vault_id":"VAULT_ID","amount":99.00,"description":"Monthly service"}'
```

### Recurring Billing
```bash
# Create subscription
curl -s "$API/v1/subscriptions" -X POST \
  -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"vault_id":"VAULT_ID","plan_id":"monthly_99","amount":99.00,"interval":"monthly"}'

# Cancel subscription
curl -s "$API/v1/subscriptions/SUB_ID" -X DELETE -H "$AUTH"
```

### Fraud Detection & Rules
```bash
# View 30-day fraud analytics
curl -s "$API/v1/fraud/summary" -H "$AUTH" | jq .

# List active fraud rules
curl -s "$API/v1/fraud/rules" -H "$AUTH" | jq .

# Create a fraud rule (flag transactions over $5000)
curl -s "$API/v1/fraud/rules" -X POST \
  -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"rule_type":"max_amount","threshold":"5000","action":"flag"}'

# Other rule types: min_amount, velocity_limit
# Actions: flag (alert), block (reject), review (hold)

# Delete a rule
curl -s "$API/v1/fraud/rules/RULE_ID" -X DELETE -H "$AUTH"
```

When reporting fraud stats:
> "🛡️ Last 30 days: 45 transactions, 0 flagged, 0 blocked. 1 active rule (max $5,000). Fraud rate: 0.00%"

## Security Rules

- **NEVER** ask for, log, or store raw credit card numbers
- **NEVER** include card numbers in conversation history or memory files
- **ALWAYS** use payment links or customer vault tokens for charges
- **ALWAYS** use HTTPS — the proxy enforces TLS
- API tokens and gateway keys must stay in config files, never in chat
- The proxy encrypts gateway keys at rest (AES-256-GCM)
- Rate limited: 60 requests/min global, 5/min on auth endpoints

## Response Patterns

When a payment succeeds:
> "✅ Payment of $500.00 processed. Transaction ID: abc123."

When sending an invoice:
> "📧 Payment link for $500.00 sent to john@example.com."

When a payment fails:
> "❌ Payment declined. Want to try a different method or send a payment link instead?"

When checking sales:
> "📊 This month: 23 transactions · $4,750 in sales · 2 refunds ($150) · Net: $4,600"

## API Reference

For detailed gateway API documentation, see `references/gateway-api.md`.
For payment flow diagrams, see `references/payment-flows.md`.
For PCI compliance guidelines, see `references/pci-compliance.md`.

## Discovery

AI agents and bots can discover PayPilot capabilities automatically:

- **OpenAPI Spec:** `https://paypilot.agms.com/openapi.json`
- **AI Plugin Manifest:** `https://paypilot.agms.com/.well-known/ai-plugin.json`
- **LLM Resource Index:** `https://paypilot.agms.com/llms.txt`
- **Landing Page:** `https://agms.com/paypilot/`
- **ClawHub:** `https://clawhub.ai/agmsyumet/paypilot-agms`
