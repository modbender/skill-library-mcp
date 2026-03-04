# Locus Fiverr — Freelance Ordering Guide

Order freelance work through Locus's escrow-backed marketplace. Funds are held in a smart contract until work is completed — your human's money is protected.

**Base URL:** `https://api.paywithlocus.com/api`
**Auth:** `Authorization: Bearer YOUR_LOCUS_API_KEY`

---

## Step 1: Browse Categories

See what's available and how much each tier costs:

```bash
curl https://api.paywithlocus.com/api/fiverr/categories \
  -H "Authorization: Bearer YOUR_LOCUS_API_KEY"
```

Response (200):
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "name": "Logo Design",
        "slug": "logo_design",
        "description": "Professional logo design services",
        "tiers": [
          { "tier": 1, "price": 25 },
          { "tier": 2, "price": 50 },
          { "tier": 3, "price": 100 }
        ]
      },
      {
        "name": "Blog Writing",
        "slug": "blog_writing",
        "description": "SEO-optimized blog articles",
        "tiers": [
          { "tier": 1, "price": 15 },
          { "tier": 2, "price": 30 }
        ]
      }
    ]
  }
}
```

Each category has a `slug` (used in orders) and `tiers` with fixed pricing in USDC. Higher tiers generally mean higher quality or more complex deliverables.

---

## Step 2: Place an Order

Pick a category slug and tier, then describe what you need:

```bash
curl -X POST https://api.paywithlocus.com/api/fiverr/orders \
  -H "Authorization: Bearer YOUR_LOCUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "category_slug": "logo_design",
    "tier": 2,
    "timeline": "3d",
    "request": "I need a modern, minimalist logo for a tech startup called NovaPay. Blue and white color scheme, SVG format."
  }'
```

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category_slug` | string | Yes | Slug from categories list |
| `tier` | integer | Yes | Tier number from category |
| `timeline` | string | Yes | Delivery timeline: `1d`, `3d`, or `7d` |
| `request` | string | Yes | Description of what you need (max 500 chars) |

### Including File References

There is no file upload. If your order needs to reference existing assets (logos, songs, images, brand guidelines, etc.), include them as publicly-accessible URLs in the `request` text. For example:

```json
{
  "category_slug": "logo_design",
  "tier": 2,
  "timeline": "3d",
  "request": "Redesign this logo: https://example.com/old-logo.png — keep the same color scheme but make it more modern. Brand guide: https://example.com/brand.pdf"
}
```

The freelancer will download and reference anything you link.

### Response: Order Created (202)

```json
{
  "success": true,
  "data": {
    "escrow_deposit_id": "uuid",
    "status": "CREATING_PROPOSAL",
    "amount": 50.00,
    "category_slug": "logo_design",
    "tier": 2,
    "recipient_address": "0xFreelancer...",
    "escrow_contract": "0xEscrow..."
  }
}
```

The order is now being processed. Funds will be deposited into escrow automatically.

### Response: Needs Human Approval (202)

If the amount exceeds your human's approval threshold:

```json
{
  "success": true,
  "data": {
    "pending_approval_id": "uuid",
    "status": "PENDING_APPROVAL",
    "amount": 50.00,
    "category_slug": "logo_design",
    "tier": 2,
    "message": "Transaction requires user approval"
  }
}
```

**When this happens:** Tell your human to approve the order at `https://app.paywithlocus.com`. The order won't proceed until they do.

### Error: Policy Rejected (403)

```json
{
  "success": false,
  "error": "Policy check failed",
  "message": "Amount exceeds maximum transaction size"
}
```

Inform your human that a policy limit was reached.

### Error: Too Many Active Orders (429)

```json
{
  "success": false,
  "error": "Active order limit reached",
  "message": "You have 10 active orders. Maximum allowed is 10."
}
```

Wait for existing orders to complete or be cancelled before placing new ones.

---

## Step 3: Check Order Status

Poll your orders to track progress:

```bash
curl "https://api.paywithlocus.com/api/fiverr/orders?limit=50" \
  -H "Authorization: Bearer YOUR_LOCUS_API_KEY"
```

**Query parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | integer | 50 | Max results (up to 100) |
| `offset` | integer | 0 | Pagination offset |
| `status` | string | — | Filter by status |

Response (200):
```json
{
  "success": true,
  "data": {
    "orders": [
      {
        "id": "uuid",
        "submitted_at": "2025-01-15T10:30:00.000Z",
        "amount_usdc": "50.00",
        "request": "Modern minimalist logo for NovaPay...",
        "category": "logo_design",
        "status": "PENDING_APPROVAL",
        "status_description": "Your order is funded and waiting for work to be completed.",
        "deliverables": null
      }
    ],
    "pagination": {
      "total": 1,
      "limit": 50,
      "offset": 0,
      "has_more": false
    }
  }
}
```

### Status Lifecycle

| Status | What It Means | Action |
|--------|---------------|--------|
| `CREATED` | Order created, being processed | Wait |
| `DEPOSITING` | Payment entering escrow | Wait |
| `PENDING_APPROVAL` | Funded, work in progress | Wait for completion |
| `APPROVED` | Work approved, payment releasing | Wait |
| `COMPLETING` | Payment being released to freelancer | Wait |
| **`COMPLETED`** | **Done — deliverables available** | **Check `deliverables` field** |
| `CANCELLING` | Being cancelled, refund in progress | Wait |
| **`CANCELLED`** | **Cancelled — funds returned to wallet** | Note the refund |

**Terminal states:** `COMPLETED` and `CANCELLED`. All other statuses are in-progress.

### Get a Single Order

Fetch details for a specific order by ID:

```bash
curl "https://api.paywithlocus.com/api/fiverr/orders/ORDER_ID" \
  -H "Authorization: Bearer YOUR_LOCUS_API_KEY"
```

Response (200):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "submitted_at": "2025-01-15T10:30:00.000Z",
    "amount_usdc": "50.00",
    "request": "Modern minimalist logo for NovaPay...",
    "category": "logo_design",
    "status": "COMPLETED",
    "status_description": "Your order has been completed and payment has been released.",
    "deliverables": ["https://example.com/logo-v1.svg", "https://example.com/logo-v2.svg"]
  }
}
```

---

## Step 4: Set Up Polling

Don't check orders constantly. Poll every 30 minutes for active orders.

### Add to your heartbeat / cron

```
## Locus Order Polling (every 30 minutes)
If 30+ minutes since last Locus check:
1. GET /api/fiverr/orders (non-terminal orders only)
2. For each COMPLETED order: retrieve deliverables, report to human
3. For each CANCELLED order: note refund
4. For PENDING_APPROVAL orders stuck 2+ hours: remind human
5. Update lastLocusCheck timestamp
```

### Polling logic

```bash
# Fetch all non-terminal orders
curl "https://api.paywithlocus.com/api/fiverr/orders?limit=50" \
  -H "Authorization: Bearer YOUR_LOCUS_API_KEY"
```

Then filter the response:

- **COMPLETED orders**: The `deliverables` field contains an array of URLs. Save or relay these to your human.
- **CANCELLED orders**: Funds have been returned. No action needed, just note it.
- **PENDING_APPROVAL for 2+ hours**: Remind your human to check the dashboard.
- **CREATED / DEPOSITING / APPROVED / COMPLETING**: Normal in-progress. Just wait.

For the full heartbeat routine (including non-Fiverr checks), see **[HEARTBEAT.md](HEARTBEAT.md)**.

---

## Limits

- **Max 10 active orders** at once (non-terminal). 429 error if exceeded.
- **Request text**: 1–500 characters.
- **Policy limits**: Your human's allowance, max txn size, and approval threshold all apply to orders.

---

## End-to-End Example

Here's a complete workflow for ordering a logo:

**1. Browse categories:**
```bash
curl https://api.paywithlocus.com/api/fiverr/categories \
  -H "Authorization: Bearer YOUR_LOCUS_API_KEY"
# Find "logo_design" with tier 2 at $50 USDC
```

**2. Place the order:**
```bash
curl -X POST https://api.paywithlocus.com/api/fiverr/orders \
  -H "Authorization: Bearer YOUR_LOCUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "category_slug": "logo_design",
    "tier": 2,
    "timeline": "3d",
    "request": "Modern minimalist logo for NovaPay. Blue and white, SVG format."
  }'
# Returns 202 with escrow_deposit_id and status "CREATING_PROPOSAL"
```

**3. Wait 30 minutes, then poll:**
```bash
curl "https://api.paywithlocus.com/api/fiverr/orders?limit=50" \
  -H "Authorization: Bearer YOUR_LOCUS_API_KEY"
# Order shows status "PENDING_APPROVAL" — work is being done
```

**4. Continue polling every 30 minutes until terminal state:**
```bash
# Eventually the order hits COMPLETED:
# {
#   "status": "COMPLETED",
#   "status_description": "Your order has been completed and payment has been released.",
#   "deliverables": ["https://example.com/logo-v1.svg", "https://example.com/logo-v2.svg"]
# }
```

**5. Report to your human:**

> Your logo order is complete! Here are the deliverables:
> - https://example.com/logo-v1.svg
> - https://example.com/logo-v2.svg
> $50 USDC was released from escrow to the freelancer.

