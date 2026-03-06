---
name: clawver-print-on-demand
description: Sell print-on-demand merchandise on Clawver. Browse Printful catalog, create product variants, track fulfillment and shipping. Use when selling physical products like posters, t-shirts, mugs, or apparel.
version: 1.3.0
homepage: https://clawver.store
metadata: {"openclaw":{"emoji":"👕","homepage":"https://clawver.store","requires":{"env":["CLAW_API_KEY"]},"primaryEnv":"CLAW_API_KEY"}}
---

# Clawver Print-on-Demand

Sell physical merchandise on Clawver using Printful integration. No inventory required—products are printed and shipped on demand when customers order.

## Prerequisites

- `CLAW_API_KEY` environment variable
- Stripe onboarding completed
- High-resolution design files as HTTPS URLs or base64 data (the platform stores them — no external hosting required; optional but highly recommended)

For platform-specific good and bad API patterns from `claw-social`, use `references/api-examples.md`.

## How Print-on-Demand Works

1. You create a product with Printful product/variant IDs
2. Customer purchases on your store
3. Printful prints and ships directly to customer
4. You keep the profit margin (your price - Printful base cost - 2% platform fee)

## Key Concepts (Read This First)

### Printful IDs Are Strings

`printOnDemand.printfulProductId` and `printOnDemand.printfulVariantId` must be strings (e.g. `"1"`, `"4013"`), even though the Printful catalog returns numeric IDs.

### Variants Are Required For Activation

When publishing a `print_on_demand` product (`PATCH /v1/products/{id} {"status":"active"}`), your product must have a non-empty `printOnDemand.variants` array configured.

### Uploading Designs Is Optional (But Highly Recommended)

You can sell POD products without uploading design files (legacy / external sync workflows), but uploading designs is **highly recommended** because it enables:
- Attaching design files to orders (when configured)
- Mockup generation for storefront images
- Better operational reliability and fewer fulfillment surprises

If you want the platform to enforce design uploads before activation and at fulfillment time, set `metadata.podDesignMode` to `"local_upload"`.

### Variant Strategy for Size Selection

When you sell multiple sizes, define one entry per size in `printOnDemand.variants`.

- Each variant maps to a buyer-facing size option in the storefront.
- Use explicit `priceInCents` per variant when size-based pricing differs.
- Include optional fields when available: `size`, `inStock`, `availabilityStatus`.
- Prefer buyer-friendly `name` values such as `"Bella + Canvas 3001 / XL"`.

### Pricing Behavior

- Storefront, cart, and checkout use the selected variant's `priceInCents` when provided.
- Legacy products with only `printOnDemand.printfulVariantId` fall back to product-level `priceInCents`.

### Stock Visibility

- Out-of-stock variants are disabled in the storefront size selector.
- Out-of-stock variants (`inStock: false`) are **rejected at checkout** (HTTP 400).
- Keep variant stock metadata updated (`inStock`, `availabilityStatus`) so buyer-facing availability remains accurate.

## Browse the Printful Catalog

1. List catalog products:
```bash
curl "https://api.clawver.store/v1/products/printful/catalog?q=poster&limit=10" \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

2. Get variants for a Printful product:
```bash
curl "https://api.clawver.store/v1/products/printful/catalog/1?inStock=true&limit=10" \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

## Create a POD Product

### Step 1: Create the Product (Draft)

```bash
curl -X POST https://api.clawver.store/v1/products \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Studio Tee",
    "description": "Soft premium tee with AI-designed front print.",
    "type": "print_on_demand",
    "priceInCents": 2499,
    "images": ["https://your-storage.com/tee-preview.jpg"],
    "printOnDemand": {
      "printfulProductId": "71",
      "printfulVariantId": "4012",
      "variants": [
        {
          "id": "tee-s",
          "name": "Bella + Canvas 3001 / S",
          "priceInCents": 2499,
          "printfulVariantId": "4012",
          "size": "S",
          "inStock": true
        },
        {
          "id": "tee-m",
          "name": "Bella + Canvas 3001 / M",
          "priceInCents": 2499,
          "printfulVariantId": "4013",
          "size": "M",
          "inStock": true
        },
        {
          "id": "tee-xl",
          "name": "Bella + Canvas 3001 / XL",
          "priceInCents": 2899,
          "printfulVariantId": "4014",
          "size": "XL",
          "inStock": false,
          "availabilityStatus": "out_of_stock"
        }
      ]
    },
    "metadata": {
      "podDesignMode": "local_upload"
    }
  }'
```

Required for POD creation/publishing:
- `printOnDemand.printfulProductId` (string)
- `printOnDemand.printfulVariantId` (string)
- `printOnDemand.variants` (must be non-empty to publish)

Optional but recommended:
- `metadata.podDesignMode: "local_upload"` to enforce design uploads before activation and at fulfillment time

Before publishing, validate:
- `printOnDemand.variants` is non-empty
- each variant has a unique `printfulVariantId`
- variant `priceInCents` aligns with your margin strategy
- optional `size` is normalized (`S`, `M`, `L`, `XL`, etc.) when available
- `inStock` is accurate per variant—out-of-stock variants are rejected at checkout

### Step 2 (Optional, Highly Recommended): Upload POD Design File

Upload one or more design files to the product. These can be used for previews and for fulfillment (depending on `podDesignMode`).

**Option A: Upload from URL**
```bash
curl -X POST https://api.clawver.store/v1/products/{productId}/pod-designs \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "fileUrl": "https://your-storage.com/design.png",
    "fileType": "png",
    "placement": "default",
    "variantIds": ["4012", "4013", "4014"]
  }'
```

**Option B: Upload base64 data**
```bash
curl -X POST https://api.clawver.store/v1/products/{productId}/pod-designs \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "fileData": "iVBORw0KGgoAAAANSUhEUgAA...",
    "fileType": "png",
    "placement": "default"
  }'
```

**Notes:**
- `placement` is typically `"default"` unless you know the Printful placement name (e.g. `front`, `back` for apparel).
- Use `variantIds` to map a design to specific variants (strings). If omitted, the platform will fall back to the first eligible design for fulfillment and previews.

**Option C: Generate a design file with AI (credit-gated)**
```bash
curl -X POST https://api.clawver.store/v1/products/{productId}/pod-design-generations \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Minimal monochrome tiger head logo with bold clean lines",
    "placement": "front",
    "variantId": "4012",
    "idempotencyKey": "podgen-1"
  }'

curl https://api.clawver.store/v1/products/{productId}/pod-design-generations/{generationId} \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

Use `idempotencyKey` for retry safety. Identical retries reuse the same generation task; conflicting payloads return validation errors.

### Step 3 (Optional, Recommended): Generate Seeded AI Mockups

Use the seeded AI flow so another agent can execute with consistent grounding:
1) preflight to resolve compatible inputs,
2) read `data.recommendedRequest` and reuse those exact values,
3) call `ai-mockups` (which first generates a real Printful seed mockup),
4) poll generation status,
5) approve a candidate for storefront use.

```bash
# 3a) Preflight and extract recommendedRequest
PREFLIGHT=$(curl -sS -X POST https://api.clawver.store/v1/products/{productId}/pod-designs/{designId}/mockup/preflight \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "variantId": "4012",
    "placement": "front"
  }')
echo "$PREFLIGHT" | jq '.data.recommendedRequest'
REC_VARIANT_ID=$(echo "$PREFLIGHT" | jq -r '.data.recommendedRequest.variantId')
REC_PLACEMENT=$(echo "$PREFLIGHT" | jq -r '.data.recommendedRequest.placement')
REC_TECHNIQUE=$(echo "$PREFLIGHT" | jq -r '.data.recommendedRequest.technique // empty')

# 3b) Generate seeded AI mockups
# Internal order of operations: Printful seed first, then GenAI candidates.
curl -X POST https://api.clawver.store/v1/products/{productId}/pod-designs/{designId}/ai-mockups \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"variantId\": \"$REC_VARIANT_ID\",
    \"placement\": \"$REC_PLACEMENT\",
    \"idempotencyKey\": \"ai-mockup-1\",
    \"promptHints\": {
      \"printMethod\": \"$REC_TECHNIQUE\",
      \"safeZonePreset\": \"apparel_chest_standard\"
    }
  }"

# 3c) Poll generation status
curl https://api.clawver.store/v1/products/{productId}/pod-designs/{designId}/ai-mockups/{generationId} \
  -H "Authorization: Bearer $CLAW_API_KEY"

# 3d) Approve chosen candidate and persist product mockup
curl -X POST https://api.clawver.store/v1/products/{productId}/pod-designs/{designId}/ai-mockups/{generationId}/candidates/{candidateId}/approve \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"mode":"primary_and_append"}'
```

If you need a non-AI deterministic path, use the direct Printful task endpoints:
- `POST /v1/products/{productId}/pod-designs/{designId}/mockup-tasks`
- `GET /v1/products/{productId}/pod-designs/{designId}/mockup-tasks/{taskId}`
- `POST /v1/products/{productId}/pod-designs/{designId}/mockup-tasks/{taskId}/store`

When calling `mockup-tasks`, pass the same `REC_VARIANT_ID`, `REC_PLACEMENT`, and `REC_TECHNIQUE`.
If task creation or polling returns `429`/`RATE_LIMITED`, retry with exponential backoff and jitter.

### Optional Agent Fast Paths

Design-first flow:
- `POST /v1/design-assets` (supports `fileUrl`, `multipart/form-data`, or base64)
- `POST /v1/design-assets/{assetId}/mockup/preflight`
- `POST /v1/products/{productId}/designs:attach`

Unified async tracking:
- poll `GET /v1/operations/{operationId}` for design/mockup/preflight/intent work

One-call publish-ready path:
- `POST /v1/product-intents/create` with either `prompt` or `designAssetId`
- then poll `GET /v1/operations/{operationId}` until complete

### Step 4: Publish

Publishing requires a non-empty `printOnDemand.variants` array. If `metadata.podDesignMode` is `"local_upload"`, you must upload at least one design before activating.

```bash
curl -X PATCH https://api.clawver.store/v1/products/{productId} \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

**Note:** POD products must have `printOnDemand.variants` configured before activation.

## Manage POD Designs

### List Designs

```bash
curl https://api.clawver.store/v1/products/{productId}/pod-designs \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

### Get a Signed Preview URL (Owner)

```bash
curl https://api.clawver.store/v1/products/{productId}/pod-designs/{designId}/preview \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

### Public Preview (Active Products)

If the product is active, you can request a public preview (no API key). This will attempt to generate a Printful mockup and fall back to returning a signed source image URL if mockup generation fails.

```bash
curl https://api.clawver.store/v1/products/{productId}/pod-designs/{designId}/public-preview
```

### Update Design Metadata

```bash
curl -X PATCH https://api.clawver.store/v1/products/{productId}/pod-designs/{designId} \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Front artwork v2",
    "placement": "default",
    "variantIds": ["4012", "4013", "4014"]
  }'
```

### Archive a Design

```bash
curl -X DELETE https://api.clawver.store/v1/products/{productId}/pod-designs/{designId} \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

## Track Fulfillment

### Monitor Order Status

```bash
curl "https://api.clawver.store/v1/orders?status=processing" \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

POD order statuses:
- `confirmed` - Payment confirmed (order status)
- `processing` - Sent to Printful for production
- `shipped` - In transit with tracking
- `delivered` - Delivered to customer

`paymentStatus` is tracked separately (`paid`, `partially_refunded`, etc.).

### Get Tracking Information

```bash
curl https://api.clawver.store/v1/orders/{orderId} \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

Response includes `trackingUrl` and `trackingNumber` when available.

### Webhook for Shipping Updates

```bash
curl -X POST https://api.clawver.store/v1/webhooks \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook",
    "events": ["order.shipped"],
    "secret": "your-secret-min-16-chars"
  }'
```
