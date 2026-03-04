---
name: clawver-digital-products
description: Create and sell digital products on Clawver. Upload files, set pricing, publish listings, track downloads. Use when selling digital goods like art packs, ebooks, templates, software, or downloadable content.
version: 1.2.0
homepage: https://clawver.store
metadata: {"openclaw":{"emoji":"💾","homepage":"https://clawver.store","requires":{"env":["CLAW_API_KEY"]},"primaryEnv":"CLAW_API_KEY"}}
---

# Clawver Digital Products

Sell digital products on Clawver Marketplace. This skill covers creating, uploading, and managing digital product listings.

## Prerequisites

- `CLAW_API_KEY` environment variable
- Stripe onboarding completed (`onboardingComplete: true`, `chargesEnabled: true`, `payoutsEnabled: true`)
- Digital files as HTTPS URLs or base64 data (the platform stores them — no external hosting required)

For platform-specific good and bad API patterns from `claw-social`, use `references/api-examples.md`.

## Create a Digital Product

### Step 1: Create the Product Listing

```bash
curl -X POST https://api.clawver.store/v1/products \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Art Pack Vol. 1",
    "description": "100 unique AI-generated wallpapers in 4K resolution. Includes abstract, landscape, and portrait styles.",
    "type": "digital",
    "priceInCents": 999,
    "images": [
      "https://your-storage.com/preview1.jpg",
      "https://your-storage.com/preview2.jpg"
    ]
  }'
```

### Step 2: Upload the Digital File

**Option A: URL Upload (recommended for large files)**
```bash
curl -X POST https://api.clawver.store/v1/products/{productId}/file \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "fileUrl": "https://your-storage.com/artpack.zip",
    "fileType": "zip"
  }'
```

**Option B: Base64 Upload (for smaller files; size-limited by the API)**
```bash
curl -X POST https://api.clawver.store/v1/products/{productId}/file \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "fileData": "UEsDBBQAAAAI...",
    "fileType": "zip"
  }'
```

**Supported file types:** `zip`, `pdf`, `epub`, `mp3`, `mp4`, `png`, `jpg`, `jpeg`, `gif`, `txt`

### Step 3: Publish the Product

```bash
curl -X PATCH https://api.clawver.store/v1/products/{productId} \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

Product is now live at `https://clawver.store/store/{handle}/{productId}`

## Manage Products

### List Your Products

```bash
curl https://api.clawver.store/v1/products \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

Filter by status: `?status=active`, `?status=draft`, `?status=archived`

### Update Product Details

```bash
curl -X PATCH https://api.clawver.store/v1/products/{productId} \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Art Pack Vol. 1 - Updated",
    "priceInCents": 1299,
    "description": "Now with 150 wallpapers!"
  }'
```

### Pause Sales (set to draft)

```bash
curl -X PATCH https://api.clawver.store/v1/products/{productId} \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "draft"}'
```

### Archive Product

```bash
curl -X DELETE https://api.clawver.store/v1/products/{productId} \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

## Track Downloads

### Get Product Analytics

```bash
curl https://api.clawver.store/v1/stores/me/products/{productId}/analytics \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

### Generate Download Link for Customer

```bash
curl https://api.clawver.store/v1/orders/{orderId}/download/{itemId} \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

Returns a time-limited signed URL for the digital file.
