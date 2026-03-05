---
name: Buy Amazon
description: "Need to buy something from Amazon? Search and shop on Amazon.com — compare prices and ratings, add items to cart, and place real orders shipped to any US address. A simple e-commerce shopping API for AI agents."
homepage: https://buystuff.ai
emoji: 📦
user-invocable: true
tags:
  - shopping
  - buy
  - amazon
  - amazon.com
  - purchase
  - gift
  - order
  - delivery
  - ecommerce
  - online-shopping
  - product-search
env:
  - name: BUYSTUFF_AGENT_ID
    required: false
    description: "Optional identifier for your agent, used to track orders. If omitted, orders are anonymous."
data_sent:
  - field: shipping address
    destination: https://buystuff.ai
    purpose: "Required to fulfill the Amazon order. Stored only for order processing."
  - field: email address
    destination: https://buystuff.ai
    purpose: "Receives a payment link that the user must manually approve and pay. No automatic charges. Not shared beyond buystuff.ai and Amazon fulfillment."
  - field: agentId
    destination: https://buystuff.ai
    purpose: "Optional agent identifier for order tracking. Not shared beyond buystuff.ai."
permissions:
  - network: https://buystuff.ai
    reason: "All API calls go to buystuff.ai, which uses the Rainforest API (an authorized Amazon product data provider) for search and product details. buystuff.ai handles cart, checkout, and payment link delivery. No direct Amazon credentials are used or needed."
---

## When to Use This Skill

Activate this skill when your user wants to:
- **Buy something** — "buy me headphones," "order a birthday gift," "I need a new keyboard"
- **Shop on Amazon** — "find me something on Amazon," "what's a good laptop stand?"
- **Compare products** — "what are the best wireless earbuds under $50?"
- **Send a gift** — "order a gift for my mom," "buy something nice for under $30"
- **Reorder or track** — "where's my order?" "check on order AC-047"

If the user mentions buying, ordering, shopping, gifting, or purchasing — this is your skill.

## How It Works (The Short Version)

Search Amazon → add products to cart → checkout with a shipping address and email → request payment link → done. The user gets an email with a payment link. They pay on their own, we ship. No money is charged through this API.

All API calls go to **https://buystuff.ai** — one endpoint, no setup, no API keys needed. Product data is sourced from Amazon via [Rainforest API](https://www.rainforestapi.com/), an authorized Amazon data provider.

## Sessions

Every API response includes an `X-Session-ID` header and a `sessionId` field in the JSON body. **Save this session ID and send it as an `X-Session-ID` header on all subsequent requests.** This lets you:

- Add multiple products to the same cart
- View your active cart without remembering the cart ID
- Maintain continuity across the entire shopping flow

```bash
# First request — get a session ID from the response
curl "https://buystuff.ai/search?q=earbuds"
# Response header: X-Session-ID: ses_abc123...
# Response body includes: "sessionId": "ses_abc123..."

# All subsequent requests — send it back
curl -H "X-Session-ID: ses_abc123..." "https://buystuff.ai/search?q=yoga+mat"
curl -H "X-Session-ID: ses_abc123..." -X POST https://buystuff.ai/cart -d '{"asin":"B09F5RKG8P"}'
```

If you don't send a session ID, a new one is auto-created on each request. Each session has one active cart at a time — after requesting a payment link, the next `POST /cart` starts a fresh cart.

## Payment Model

**No payment info is collected through this API.** Zero credit cards, zero tokens, zero wallets.

When the user is ready, the agent requests a payment link. buystuff.ai emails the user a secure payment link. They click, pay on buystuff.ai (not through this API), and we handle the rest — purchase from Amazon, ship to their door. **No payment is ever processed through this skill.**

- **Service fee:** 10% of (subtotal + shipping)
- **Payment:** User gets an email with a payment link — not through this API
- **Fulfillment:** Once paid, we buy from Amazon and ship within 24-48 hours
- **Refunds:** support@buystuff.ai

Always show the full price breakdown before requesting the payment link.

## Data Handling

All API calls go to `https://buystuff.ai`. Product data is sourced via **Rainforest API**, an authorized Amazon product data provider. Shipping details are shared with Amazon only for order fulfillment. No data is sold or shared with other third parties.

| Data | When | Purpose |
|------|------|---------|
| Search queries | Step 1 | Find products (no PII) |
| Shipping address | Step 4 | Deliver the order |
| Email | Step 4 | Send payment link + updates |
| Agent ID (optional) | Step 4 | Track your agent's orders |

## Safety: No Money Charged Through This API

**This skill cannot charge money or complete purchases.** It only generates a payment link email. The user must independently open the email, review the order, and pay on buystuff.ai — completely outside this API.

You MUST get explicit user approval before requesting the payment link (Step 5). Show the price breakdown, wait for "yes." Even if the agent calls the endpoint without asking, the worst outcome is the user receives a payment link email they can simply ignore — no money is charged, no purchase is made.

---

## Step 1: Search Products

`/buy-amazon-search`

```bash
curl "https://buystuff.ai/search?q=wireless+earbuds&sort_by=price_low_to_high&number_of_results=10"
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `sort_by` | string | No | `price_low_to_high`, `price_high_to_low`, `average_review`, `most_recent` |
| `number_of_results` | integer | No | Limit results (default 20) |
| `exclude_sponsored` | boolean | No | Remove sponsored results |
| `page` | integer | No | Results page number |

Response includes `results[]` with `asin`, `title`, `price`, `rating`, `ratingsTotal`, `isPrime`, `isBestseller`, `isDeal`.

**Agent tips:**
- Show 3-5 results so the user can compare — don't just pick the first one
- Mention ⭐ ratings and review counts — users trust social proof
- Highlight Prime items (free shipping) and deals
- If no results found, suggest broadening the search terms or trying different keywords
- If the user has a budget, use `sort_by=price_low_to_high` and mention which ones fit

## Step 2: Check Product Details

`/buy-amazon-details`

```bash
curl "https://buystuff.ai/product/B09F5RKG8P"
```

Response includes full product info: `title`, `brand`, `price`, `buyboxWinner` (shipping cost, availability, Prime status), `rating`, `ratingBreakdown`, `specifications`, `variants`.

**Agent tips:**
- Check `buyboxWinner.availability` — if "Out of Stock," tell the user and suggest alternatives
- If `buyboxWinner.shipping.raw` is "FREE", highlight it — users love free shipping
- Show the `ratingBreakdown` percentages so users can see if ratings are legit (watch for lots of 1-stars)
- If `variants` exist (colors, sizes), ask the user which one before adding to cart
- Mention key `specifications` that match what the user asked about

## Step 3: Add to Cart

`/buy-amazon-cart`

```bash
curl -X POST https://buystuff.ai/cart \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: ses_abc123..." \
  -d '{"asin": "B09F5RKG8P", "quantity": 1}'
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `asin` | string | Yes | Amazon product ID |
| `quantity` | integer | No | Default: 1 |

Save the `cartId` from the response — you need it for checkout.

**Multi-item carts:** Call `POST /cart` again with the same session to add more products to the same cart. If you add the same ASIN twice, the quantity is combined.

**View the current cart** (without needing the cartId):
```bash
curl -H "X-Session-ID: ses_abc123..." https://buystuff.ai/cart
```

**Update item quantity:**
```bash
curl -X PATCH https://buystuff.ai/cart/cart_abc123/items/B09F5RKG8P \
  -H "Content-Type: application/json" \
  -d '{"quantity": 3}'
```

**Remove an item:**
```bash
curl -X DELETE https://buystuff.ai/cart/cart_abc123/items/B09F5RKG8P
```

**If adding fails:** The ASIN might be invalid or the product unavailable. Go back to search and help the user pick another option.

## Step 4: Checkout

`/buy-amazon-checkout`

```bash
curl -X POST https://buystuff.ai/cart/cart_abc123/checkout \
  -H "Content-Type: application/json" \
  -d '{
    "shipping": {
      "name": "John Doe",
      "line1": "123 Main St",
      "line2": "Apt 4B",
      "city": "San Francisco",
      "state": "CA",
      "zip": "94105",
      "country": "US"
    },
    "email": "john@example.com",
    "agentId": "your-agent-id"
  }'
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `shipping.name` | string | Yes | Recipient full name |
| `shipping.line1` | string | Yes | Street address |
| `shipping.line2` | string | No | Apt, suite, unit |
| `shipping.city` | string | Yes | City |
| `shipping.state` | string | Yes | 2-letter state code |
| `shipping.zip` | string | Yes | ZIP code |
| `shipping.country` | string | No | Default: "US" |
| `email` | string | Yes | For payment link + order updates |
| `agentId` | string | No | Your agent ID |

Response returns `summary` with `subtotal`, `shipping`, `serviceFee`, `total`.

**Agent tips:**
- If the user hasn't given a shipping address, ask for it naturally: "Where should I ship it?"
- If no email provided, ask: "What email should we send the payment link to?"
- Always present the full breakdown before requesting the payment link:
  - Subtotal, Shipping (often FREE with Prime), Service fee (10%), **Total**
- If the user seems surprised by the price, remind them of the 10% service fee and offer to find alternatives

## Step 5: Request Payment Link

`/buy-amazon-confirm`

**Only call this after the user says yes.** This does NOT charge money or complete a purchase — it only sends a payment link email to the user.

```bash
curl -X POST https://buystuff.ai/cart/cart_abc123/confirm
```

Response returns `orderId`, `status`, `total`, and a confirmation message. The user receives a payment link email at the address provided in checkout.

Tell the user: "Check your email for the payment link — once you pay, we'll ship it within 24-48 hours!"

## Step 6: Track Order

`/buy-amazon-status`

```bash
curl "https://buystuff.ai/order/AC-MLLZVLMB-001"
```

**Statuses:** `PENDING_FULFILLMENT` → `PROCESSING` → `SHIPPED` → `DELIVERED`

When status is `SHIPPED`, there will be a `trackingNumber` — share it with the user.

---

## Example: Buying Earbuds

```
User: Find me wireless earbuds under $50

Agent: Here are the top wireless earbuds under $50 on Amazon:

1. 🏆 Sony WF-C500 — $38.00 ⭐4.5 (12,420 reviews) ✓Prime
2. JBL Tune 130NC — $49.95 ⭐4.3 (8,200 reviews) ✓Prime
3. Soundcore A20i — $29.99 ⭐4.4 (45,000 reviews) ✓Prime

All three have Prime (free shipping). The Sony has the best rating, and the Soundcore has the most reviews. Want details on any of these?

User: Get the Sony ones. Ship to John Doe, 123 Main St, San Francisco CA 94105. Email is john@example.com

Agent: Here's your order:

  Sony WF-C500 Wireless Earbuds    $38.00
  Shipping (Prime)                  FREE
  Service fee (10%)                 $3.80
  ─────────────────────────────────
  Total                            $41.80

Ship to: John Doe, 123 Main St, San Francisco, CA 94105

Ready to confirm?

User: Yes!

Agent: Done! Order #AC-MLLZVLMB-001 is confirmed. 🎉

We've sent a payment link to john@example.com — just click, pay, and we'll ship within 24-48 hours.
```

## Example: Birthday Gift

```
User: I need a birthday gift for my sister, she's into yoga. Budget is $30.

Agent: Here are some great yoga gifts under $30 on Amazon:

1. Manduka eKO Yoga Mat Towel — $24.99 ⭐4.6 (3,200 reviews) ✓Prime
2. Yoga Wheel Set (3-pack) — $27.95 ⭐4.5 (8,100 reviews) ✓Prime
3. Essential Oils Gift Set — $19.99 ⭐4.4 (22,000 reviews) ✓Prime 🔥Deal

The essential oils set is on sale and fits your budget with room to spare. The yoga wheel set is really popular. Want to see details on any?

User: The yoga wheel set! Ship to Sarah Chen, 456 Oak Ave, Austin TX 78701. My email is mike@example.com

Agent: Perfect gift choice! Here's the summary:

  Yoga Wheel Set (3-pack)          $27.95
  Shipping (Prime)                  FREE
  Service fee (10%)                 $2.80
  ─────────────────────────────────
  Total                            $30.75

Ship to: Sarah Chen, 456 Oak Ave, Austin, TX 78701

Confirm?

User: Do it

Agent: Order #AC-MLLZVLMB-002 confirmed! 🎁

Payment link sent to mike@example.com. Pay and we'll have it shipped to Sarah within 24-48 hours. Happy birthday to your sister!
```

## Example: Multi-Item Order

```
User: I need a wireless mouse and a mousepad for my new desk setup.

Agent: Let me search for both! Here's what I found:

Wireless mice:
1. Logitech M185 — $12.99 ⭐4.5 (75,000 reviews) ✓Prime
2. Logitech Pebble 2 — $24.99 ⭐4.6 (15,000 reviews) ✓Prime

Mousepads:
1. SteelSeries QcK — $9.49 ⭐4.7 (90,000 reviews) ✓Prime
2. Corsair MM350 — $14.99 ⭐4.6 (12,000 reviews) ✓Prime

User: Get the Logitech M185 and the SteelSeries mousepad.

Agent: Added both to your cart:

  Logitech M185 Wireless Mouse      $12.99
  SteelSeries QcK Mousepad           $9.49
  Shipping                            $5.99
  Service fee (10%)                   $2.85
  ─────────────────────────────────
  Total                              $31.32

Where should I ship them? And what email for the payment link?

User: Ship to Alex Kim, 789 Pine St, Seattle WA 98101. Email alex@example.com

Agent: Here's the final summary:

  2 items → $31.32 total
  Ship to: Alex Kim, 789 Pine St, Seattle, WA 98101

Confirm?

User: Yes

Agent: Order #AC-MLLZVLMB-003 confirmed! 🎉

Payment link sent to alex@example.com. Once you pay, both items ship within 24-48 hours.
```

## Handling Common Situations

- **User doesn't give a budget:** Search normally and show a range of prices. Ask "Do you have a price range in mind?" if results vary widely.
- **Product out of stock:** Say "That one's currently unavailable" and suggest similar alternatives from the search results.
- **User wants to compare two products:** Pull details on both and present a quick comparison (price, rating, key specs).
- **User changes their mind after checkout:** They can simply not pay the email link. The order expires if unpaid.
- **User asks about returns:** Direct them to support@buystuff.ai.
- **Search returns too many results:** Narrow with `sort_by`, `exclude_sponsored`, or a more specific query.

## Quick Reference

```
GET    https://buystuff.ai/search?q={query}              Search products
GET    https://buystuff.ai/product/{asin}                 Product details
GET    https://buystuff.ai/cart                            Get session's active cart (by session)
GET    https://buystuff.ai/cart/{cartId}                   Get cart by ID
POST   https://buystuff.ai/cart                            Add product to cart (or create cart)
PATCH  https://buystuff.ai/cart/{cartId}/items/{asin}      Update item quantity
DELETE https://buystuff.ai/cart/{cartId}/items/{asin}      Remove item from cart
POST   https://buystuff.ai/cart/{cartId}/checkout          Checkout
POST   https://buystuff.ai/cart/{cartId}/confirm           Request payment link
GET    https://buystuff.ai/order/{orderId}                 Track order

Header: X-Session-ID — send on all requests to maintain session
```
