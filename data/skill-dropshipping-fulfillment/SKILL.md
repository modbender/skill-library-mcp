---
name: skill-dropshipping-fulfillment
description: Automates order fulfillment by pushing WooCommerce orders to CJ Dropshipping. Fetches "Processing" orders, matches line items to CJ variants via a supplier selection map, submits orders to CJ API, updates WooCommerce order status, and logs results. Supports dry-run and single-order modes.
metadata:
  openclaw:
    requires: { bins: ["node"] }
---

# CJ Fulfillment Engine

Automates the WooCommerce → CJ Dropshipping order flow. No manual copy-paste.

## What it does
1. Fetches all `processing` orders from WooCommerce
2. Maps line items to CJ variant IDs via `cj-supplier-selection.json`
3. Submits matched items to CJ API as a dropship order
4. Updates WooCommerce order status to `on-hold` (awaiting CJ dispatch)
5. Adds an order note with the CJ order ID
6. Logs all results to `cj-fulfillment-log.json`

## Credentials / paths

| File | Contents |
|---|---|
| `woo-api.json` | `{ url, consumerKey, consumerSecret }` |
| `cj-api.json` | `{ apiKey, baseUrl, accessToken, tokenExpiry }` |
| `cj-supplier-selection.json` | Array of `{ sku, cjProductId, variantId, ... }` |

## Usage

```bash
# Dry run — preview without placing orders
node {baseDir}/scripts/fulfill.js --dry-run

# Fulfill all processing orders
node {baseDir}/scripts/fulfill.js

# Fulfill a single WooCommerce order
node {baseDir}/scripts/fulfill.js --order 1234
```

## cj-supplier-selection.json format

Full 6-field schema — one entry per product variant. Matching is SKU-first with fallback to `wooProductId:wooVariationId`.

```json
[
  {
    "wooProductId": 77261,
    "wooVariationId": 77265,
    "sku": "CJYD2360896-BLACK",
    "cjProductId": "CJ-PRODUCT-ID",
    "variantId": "CJ-VARIANT-ID",
    "productName": "My Product — Black"
  }
]
```

Generate or rebuild this file from CJ API automatically:

```bash
node {baseDir}/scripts/rebuild-mapping.js
```

## FBA / excluded products

Products that should never be fulfilled via CJ (e.g. FBA, in-house). Set via env var:

```bash
FBA_PRODUCT_IDS=75927,75808,2382 node fulfill.js
```

These are skipped with a log entry: `"FBA product — manual fulfillment required"`.

## Output

- Console: per-order summary with matched/unmatched items and CJ order ID
- `cj-fulfillment-log.json`: append-only log with `{ orderId, status, cjOrderId, timestamp }`
- `cj-rejection-log.json`: unmatched/skipped items for manual review

## Unmatched items

If a line item has no SKU match and no `wooProductId:wooVariationId` match, it's logged to the rejection log and the order is skipped. Fix by running `rebuild-mapping.js` or adding the entry manually.

## Environment overrides

```bash
CJ_SELECTION_PATH=/custom/path/selection.json node fulfill.js
FULFILL_LOG_PATH=/custom/path/log.json node fulfill.js
```
