# Stripe CLI Workflows

## 1) Webhook Local Loop (recommended)

### Goal
Validate local webhook handler behavior quickly and repeatedly.

### Steps
1. Start local app endpoint
2. Start Stripe CLI listener:

```bash
stripe listen --forward-to localhost:4242/webhook
```

3. Copy generated signing secret (`whsec_...`) into local env
4. Trigger test event:

```bash
stripe trigger checkout.session.completed
```

5. Verify local logs + Stripe logs tail

### Notes
- `stripe trigger` creates side effects in test mode
- Keep listener running while iterating

---

## 2) Subscriptions / Proration Diagnostics

### Goal
Debug upgrade, downgrade, cycle switch (monthly/yearly), and invoice impacts.

### Pattern
1. Fetch current subscription and item IDs
2. Preview invoice/proration before update
3. Apply update with intended `proration_behavior`
4. Validate resulting invoice/events

### Example sequence

```bash
# list subscriptions for customer
stripe subscriptions list --customer cus_xxx --limit 5

# preview upcoming invoice after a change (example)
stripe invoices create_preview \
  -d customer=cus_xxx \
  -d subscription=sub_xxx \
  -d "subscription_details[items][0][id]=si_xxx" \
  -d "subscription_details[items][0][price]=price_new"

# apply update
stripe subscriptions update sub_xxx \
  -d "items[0][id]=si_xxx" \
  -d "items[0][price]=price_new" \
  -d proration_behavior=always_invoice
```

### Why `always_invoice`
For immediate charge on upgrade deltas.

---

## 3) Fixture-Driven Test Flows

Use fixtures when a single `trigger` event is insufficient.

```bash
stripe fixtures ./fixtures/checkout-subscription.json
```

Best practice:
- Keep fixtures in version control
- Keep test IDs/env vars parameterized

---

## 4) Incident Debug Loop

```bash
stripe logs tail
stripe events list --limit 20
stripe events retrieve evt_xxx
stripe events resend evt_xxx --webhook-endpoint=we_xxx
```

Use this when webhook consumer missed events or had temporary failures.
