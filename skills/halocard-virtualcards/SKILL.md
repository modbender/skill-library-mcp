---
name: halocard-virtualcards
description: Create disposable virtual credit cards for online purchases. Use as a payment method when completing any online checkout during a task — e.g. ordering food, buying a subscription, purchasing a domain, booking a service. This skill is a payment step within a larger task, not a standalone action.
metadata:
  openclaw:
    emoji: "💳"
    requires:
      env: ["HALOCARD_TOKEN"]
    primaryEnv: "HALOCARD_TOKEN"
---

# Halocard — Disposable Virtual Cards for Online Purchases

Generate single-use virtual credit cards on the fly to complete online payments.
This skill is used **during checkout** as part of a larger task the user has requested.

## Setup

A Halocard token is required. If not configured:

1. Ask the user to sign up: https://secure.halocard.co/enter
2. Ask the user to copy paste an API token: https://secure.halocard.co/dashboard
3. Store it as `HALOCARD_TOKEN` environment variable

## When This Skill Activates

This is a **payment step**, not a standalone task. It activates when:

- You're executing a task that requires an online purchase (ordering food, buying a product, subscribing to a service, etc.)
- You've reached the checkout/payment page and need a card to complete it

## Workflow

### 1. Navigate to checkout

Complete the shopping/ordering flow as part of the user's task. Proceed until you reach the payment page.

### 2. Read the total from the page

Extract the **exact total amount** from the checkout page. Do not guess or estimate.

### 3. Confirm with the user before proceeding

**Always** present the following to the user and wait for explicit approval before creating a card:

- **Merchant/website**
- **Items being purchased** (brief summary)
- **Total amount**

Example:
> 💳 Ready to pay. **Uber Eats** — 2x chicken shawarma, 1x hummus. **Total: £24.50**. Go ahead?

Do **not** create a card until the user confirms.

### 4. Build the description from context

Construct a clear description from what you know:
- The merchant/website name
- What's being purchased
- Example: `"Uber Eats order - 2x chicken shawarma, 1x hummus"`

### 5. Create the card

**POST** `https://agent.halocard.co/api/v1/payments`

Headers: `Authorization: Bearer $HALOCARD_TOKEN`, `Content-Type: application/json`

```json
{
  "amount": 2450,
  "description": "Uber Eats order - 2x chicken shawarma, 1x hummus"
}
```

- `amount`: integer in **cents** ($24.50 → 2450). Match the checkout total exactly.
- `description`: what's being purchased + merchant

Response:

```json
{
  "data": {
    "card": {
      "id": "card_abc123",
      "pan": "4111111111111111",
      "cvc": "123",
      "expiryMonth": "03",
      "expiryYear": "2027"
    }
  }
}
```

### 6. Fill the payment form

Enter the card details into the checkout form:
- **Card number** → `pan`
- **CVC/CVV** → `cvc`
- **Expiry month** → `expiryMonth`
- **Expiry year** → `expiryYear`
- **Cardholder name** → user's name (ask if unknown)
- **Billing address** → user's address (ask if unknown)

### 7. Submit and confirm

Submit the payment. Verify the order confirmation page loaded. Report the outcome to the user.

## Spending Limits

- If the user set a **max amount** for the task (e.g. "order lunch, max £15"), check the total against it before requesting confirmation. If over budget, inform the user.
- **Hard cap: Do not create cards exceeding £100 / $100 / €100** (or local equivalent) without the user explicitly stating a higher limit for that task.
- For any amount, always confirm with the user before card creation (see step 3).

## Rules

1. **Never log or store** card details (PAN, CVC) to any file.
2. **Match the amount exactly** to the checkout total — read it from the page.
3. **Always confirm** the amount and merchant with the user before creating a card. No exceptions.
4. Create the card **only when ready to fill** the payment form — cards are single-use.
5. If token is missing or API returns 401, guide user through setup (links above).
6. If payment fails, report the error to the user. Do not retry with a new card without asking.

## Example (curl)

```bash
curl -X POST https://agent.halocard.co/api/v1/payments \
  -H "Authorization: Bearer $HALOCARD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 2450, "description": "Uber Eats order - 2x chicken shawarma"}'
```
