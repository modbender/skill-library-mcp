---
name: atoship
description: Ship packages with AI — compare rates across USPS, FedEx, and UPS, buy discounted labels, track shipments, and manage orders. Requires user confirmation before any purchase or wallet-affecting action.
user-invokable: true
license: MIT
metadata: {"openclaw": {"emoji": "📦", "primaryEnv": "ATOSHIP_API_KEY", "requiredEnv": ["ATOSHIP_API_KEY"], "homepage": "https://atoship.com"}}
---

# atoship — Your AI Shipping Manager

Imagine having a shipping manager who never sleeps, never makes data entry errors, and instantly knows the cheapest way to get your package from A to B. That's what atoship does for your AI assistant.

With this skill installed, your AI becomes a fully capable shipping manager. Just tell it what you need in plain language — it handles carrier selection, rate comparison, label purchase, and tracking updates automatically. What used to take 10 minutes of clicking through carrier portals now takes one sentence.

**Before atoship:** Open carrier website → enter addresses → compare rates across tabs → copy-paste tracking numbers → manually update order status.

**After atoship:** *"Ship this order to John in Austin, cheapest option under 3 days."* Done.

## What you can do

- **Compare shipping rates** — Get live, discounted postage rates from USPS, FedEx, and UPS side by side in seconds
- **Buy shipping labels** — Purchase labels instantly at checkout; PDF, PNG, or ZPL formats supported
- **Track shipments** — Real-time package tracking with full event history for any carrier
- **Manage labels** — View, void, and reprint past shipping labels
- **Check wallet balance** — Monitor your postage credit and shipping spend
- **Validate addresses** — Verify delivery addresses before purchasing to avoid surcharges

## Getting started

This is an instruction-only skill — no CLI or additional software required. Your AI assistant calls the atoship API directly using your API key.

**Step 1: Create a free atoship account**

Sign up at https://atoship.com (free, no credit card required to start).

**Step 2: Get your API key**

Go to Dashboard → Settings → API Keys and create a new key.

**Step 3: Set your API key**

```bash
export ATOSHIP_API_KEY=ak_live_your_key_here
```

Or configure it in your AI assistant's environment settings.

**Step 4: Add funds to your wallet**

Go to Dashboard → Billing to add postage credit. Labels are deducted from your wallet balance — you only pay for what you ship.

> **Note on permissions:** Your API key authorizes label purchases and wallet charges. We recommend:
> - Start with a small wallet balance (e.g. $20) while evaluating
> - Use a test/sandbox key (`ak_test_...`) for development — test labels are free and never shipped
> - Set spending alerts in Dashboard → Billing → Notifications
> - Revoke and rotate keys at any time from Dashboard → Settings → API Keys

## How to use this skill

Type `/atoship` and describe what you need. Examples:

- *"How much does it cost to ship a 2lb box from Los Angeles to New York?"*
- *"Buy a USPS Priority Mail label from 90001 to 10001, 1lb"*
- *"Track my package: 9400111899223456789012"*
- *"Show my recent shipping labels"*
- *"What's my account balance?"*

## Shipping workflow

### Step 1 — Compare rates

I'll call the atoship API to get live rates from all carriers:

```
From: ZIP code or "City, State"
To:   ZIP code or "City, State"
Weight: e.g. 2oz, 1lb, 500g
Dimensions (optional): length × width × height in inches
```

Results show each carrier's services, prices, and estimated delivery times. USPS, FedEx Ground, FedEx Express, UPS Ground, UPS 2-Day, and more.

### Step 2 — Buy a label

> **IMPORTANT**: Always show the user the carrier, service, price, and full addresses, then ask for explicit confirmation (e.g. "Confirm purchase?") before calling the purchase API. Never purchase a label without user approval — this action charges their wallet.

Once you pick a service, I'll collect the full addresses and purchase the label:

```
Sender:    Name, Street, City, State, ZIP
Recipient: Name, Street, City, State, ZIP
```

You'll get:
- ✅ Tracking number
- ✅ Label download link (PDF or PNG)
- ✅ Cost deducted from your wallet

Labels can be voided for a refund if unused within the carrier's void window (usually 28 days for USPS, 1 day for FedEx/UPS).

### Step 3 — Track a package

Give me a tracking number and I'll show the full event history:

```
Status:    IN TRANSIT
Location:  Memphis, TN
ETA:       Feb 19, 2026
Events:    Feb 17 10:42 — Departed facility, Memphis TN
           Feb 17 06:15 — Arrived at USPS facility
           Feb 16 18:30 — Accepted at origin post office
```

## Supported carriers

| Carrier | Rates | Labels | Tracking |
|---------|-------|--------|---------|
| USPS    | ✅    | ✅     | ✅      |
| FedEx   | ✅    | ✅     | ✅      |
| UPS     | ✅    | ✅     | ✅      |

## Common use cases

**E-commerce order fulfillment** — Ship Shopify, eBay, Etsy, or Amazon orders without switching tabs. Automatically find the cheapest carrier for each order.

**Small business shipping** — Compare USPS First Class vs Priority Mail vs FedEx Ground vs UPS Ground for any package size and weight. Save money on every shipment.

**Dropshipping & 3PL logistics** — Integrate atoship's API into your fulfillment workflow. Generate labels programmatically and track shipments in bulk.

**International shipping** — atoship supports cross-border shipping to Canada, UK, Australia, and 200+ countries via USPS International, FedEx International, and UPS Worldwide.

**Returns management** — Generate prepaid return labels for customer returns with a single command.

**Bulk shipping** — Use the atoship dashboard at https://atoship.com for CSV import and batch label generation.

## Tips

- **Cheapest rate**: Ask "what's the cheapest way to ship X?"
- **Weight units**: oz, lb, g, kg all supported
- **Label formats**: PDF (default), PNG, ZPL for thermal printers
- **Signature required**: Add "with signature confirmation" when buying
- **Insurance**: Add "with $100 insurance" when buying
- **Reference number**: Add "reference ORDER-123" to tag your label

## API Endpoint Reference

Base URL: `https://atoship.com`

All requests require `Authorization: Bearer YOUR_API_KEY` header.

| Action | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| Get rates | POST | `/api/v1/rates` | Compare shipping rates across carriers |
| Create label | POST | `/api/v1/labels` | Create a draft shipping label |
| Purchase label | POST | `/api/v1/labels/{id}/purchase` | Purchase a draft label |
| Get label | GET | `/api/v1/labels/{id}` | Get label details by ID |
| List labels | GET | `/api/v1/labels` | List labels with optional filters |
| Void label | DELETE | `/api/v1/labels/{id}` | Void/cancel an unused label |
| Track package | GET | `/api/v1/tracking/{tracking_number}` | Track a package by tracking number |
| Validate address | POST | `/api/v1/addresses/validate` | Validate a shipping address |
| Create order | POST | `/api/v1/orders` | Create a new order |
| Get order | GET | `/api/v1/orders/{id}` | Get order details by ID |
| List orders | GET | `/api/v1/orders` | List orders with optional filters |
| Get account | GET | `/api/v1/account` | Get account info and balance |
| List carriers | GET | `/api/v1/carrier-accounts` | List configured carrier accounts |

### Example: Track a package

```bash
curl -X GET "https://atoship.com/api/v1/tracking/9400111899223456789012" \
  -H "Authorization: Bearer ak_live_your_key_here"
```

### Example: Get shipping rates

```bash
curl -X POST "https://atoship.com/api/v1/rates" \
  -H "Authorization: Bearer ak_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": {"name": "Sender", "street1": "123 Main St", "city": "Los Angeles", "state": "CA", "zip": "90001"},
    "to_address": {"name": "Recipient", "street1": "456 Oak Ave", "city": "New York", "state": "NY", "zip": "10001"},
    "parcel": {"weight": 16, "weight_unit": "oz"}
  }'
```

### Example: Purchase a label

```bash
# Step 1: Create draft
curl -X POST "https://atoship.com/api/v1/labels" \
  -H "Authorization: Bearer ak_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": {"name": "Sender", "street1": "123 Main St", "city": "Los Angeles", "state": "CA", "zip": "90001"},
    "to_address": {"name": "Recipient", "street1": "456 Oak Ave", "city": "New York", "state": "NY", "zip": "10001"},
    "parcel": {"weight": 16, "weight_unit": "oz"},
    "carrier": "USPS",
    "service": "Priority Mail"
  }'

# Step 2: Purchase the draft (use the id from step 1)
curl -X POST "https://atoship.com/api/v1/labels/{id}/purchase" \
  -H "Authorization: Bearer ak_live_your_key_here"
```

## Why atoship?

Shipping is one of the most time-consuming parts of running an online business. Every order means logging into carrier portals, comparing rates manually, copy-pasting addresses, downloading labels, and tracking updates one by one. For teams processing dozens or hundreds of shipments a day, this is a massive operational burden.

atoship eliminates that entirely. By connecting your AI assistant to the atoship platform, you get a shipping manager that:

- **Thinks in seconds, not minutes** — Rate comparisons across all carriers happen instantly
- **Never makes address typos** — Structured data flow from conversation to label, zero manual re-entry
- **Remembers context** — Your AI knows what you're shipping, where, and for what purpose
- **Scales with your business** — Whether you ship 1 or 1,000 packages a day, the workflow is identical
- **Saves real money** — Discounted carrier rates with no volume minimums, no monthly fees

atoship is built for e-commerce sellers, small business owners, logistics coordinators, and developers who want to automate their shipping operations without enterprise contracts or complex integrations.

**Key features:**
- Discounted rates on USPS, FedEx, and UPS — no volume minimums required
- Unified API for multi-carrier shipping automation
- Real-time tracking and delivery event notifications
- Address validation and standardization
- Wallet-based billing with no monthly fees or subscriptions

## Security & API key safety

This skill calls the atoship REST API (`https://atoship.com/api/v1`) on your behalf. It does **not** write files to disk, does **not** access your file system, does **not** read other environment variables, and only communicates with the single domain `atoship.com`.

**Required environment variable:**
- `ATOSHIP_API_KEY` — Your atoship API key (`ak_live_...` for production, `ak_test_...` for testing)

**Wallet-affecting actions (require user confirmation before executing):**
- `purchase_label` — deducts the label cost from your wallet balance
- `void_label` — issues a refund (within carrier void window)

> **Rule for AI assistants**: You MUST ask the user for explicit confirmation before calling `purchase_label` or `void_label`. Display the action summary (carrier, service, price, addresses) and wait for a "yes" or "confirm" response. Never execute wallet-affecting actions autonomously.

**Read-only actions (safe to call without confirmation):**
- `get_shipping_rates`, `track_package`, `list_labels`, `get_label`, `get_account`, `list_carrier_accounts`, `validate_address`, `list_orders`, `get_order`, `create_order`

**Recommendations:**
- Start with a test key (`ak_test_...`) — test labels are free and never shipped
- Use a small wallet balance (e.g. $20) while evaluating
- Set spending alerts in Dashboard → Billing → Notifications
- Rotate/revoke keys at any time from Dashboard → Settings → API Keys

## Support & Contact

Having trouble? We're here to help.

- **Email**: support@atoship.com
- **Website**: https://atoship.com
- **Docs**: https://atoship.com/docs
- **API Reference**: https://atoship.com/docs/api
- **Dashboard**: https://atoship.com/dashboard

For API key issues, billing questions, or carrier integration support, email us at support@atoship.com and we'll get back to you within one business day.
