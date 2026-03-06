---
name: bricklink
description: "BrickLink Store API helper/CLI (OAuth 1.0 request signing). Covers orders, store inventory (read + write), catalog, categories, colors, feedback, and push notifications."
summary: "BrickLink Store API CLI: orders, inventory, catalog, pricing, feedback."
version: 1.4.1
homepage: https://github.com/odrobnik/bricklink-skill
metadata:
  openclaw:
    emoji: "🧱"
    requires:
      bins: ["python3"]
      env: ["BRICKLINK_CONSUMER_KEY", "BRICKLINK_CONSUMER_SECRET", "BRICKLINK_TOKEN_VALUE", "BRICKLINK_TOKEN_SECRET"]
---

# BrickLink

Use `scripts/bricklink.py`.

## Setup

See [SETUP.md](SETUP.md) for prerequisites and setup instructions.

## Commands

### Read-only

- `bricklink.py get-orders [--direction in|out] [--status ...] [--include-status ...] [--exclude-status ...] [--filed true|false]` - Lists orders you received or placed.
- `bricklink.py get-order <order_id>` - Fetches details for a specific order.
- `bricklink.py get-order-items <order_id>` - Fetches the item batches for a specific order.
- `bricklink.py get-order-messages <order_id>` - Fetches messages associated with a specific order.
- `bricklink.py get-order-feedback <order_id>` - Fetches feedback associated with a specific order.

- `bricklink.py get-feedback [--direction in|out]` - Lists feedback you received (`in`) or posted (`out`).
- `bricklink.py get-feedback-item <feedback_id>` - Fetches a single feedback entry by id.

- `bricklink.py get-notifications` - Lists unread push notifications (`/notifications`).

- `bricklink.py get-categories` - Lists all catalog categories.
- `bricklink.py get-category <category_id>` - Fetches a single category by id.

- `bricklink.py get-colors` - Lists all catalog colors.
- `bricklink.py get-color <color_id>` - Fetches a single color by id.

- `bricklink.py get-inventories [--item-type ...] [--status ...] [--category-id ...] [--color-id ...]` - Lists your store inventory lots (supports include/exclude filters).
- `bricklink.py get-inventory <inventory_id>` - Fetches a single inventory lot by id.

- `bricklink.py get-item <type> <no>` - Fetches a catalog item (PART/SET/MINIFIG/…).
- `bricklink.py get-supersets <type> <no> [--color-id N]` - Lists items that contain the specified item.
- `bricklink.py get-subsets <type> <no> [--color-id N] [--box true|false] [--instruction true|false] [--break-minifigs true|false] [--break-subsets true|false]` - Parts out an item into its included items.
- `bricklink.py get-price-guide <type> <no> [--color-id N] [--guide-type stock|sold] [--new-or-used N|U] [--country-code XX] [--region ...] [--currency-code XXX] [--vat N|Y|O]` - Fetches price guide statistics.
- `bricklink.py get-known-colors <type> <no>` - Lists known colors for a catalog item.

### Mutating

> **Note:** Order mutations (update-order, update-order-status, update-payment-status) only work for **store orders** (direction=out, where you are the seller). Purchases (direction=in) return 404 — the BrickLink API does not allow buyers to modify order status or file/archive incoming orders. Use the BrickLink website for those.

- `bricklink.py update-order <order_id> [--remarks ...] [--is-filed true|false] [--shipping-...] [--cost-...]` — Updates allowed order fields (tracking, remarks, shipping/cost fields). Store orders only.
- `bricklink.py update-order-status <order_id> <status>` — Updates the status of an order. Store orders only.
- `bricklink.py update-payment-status <order_id> <payment_status>` — Updates the payment status of an order. Store orders only.
- `bricklink.py send-drive-thru <order_id> [--mail-me]` — Sends a "Drive Thru" email for an order.

- `bricklink.py post-feedback --order-id N --rating 0|1|2 [--comment ...]` - Posts new feedback for an order.
- `bricklink.py reply-feedback <feedback_id> --reply "..."` - Replies to feedback you received.

- `bricklink.py create-inventory [--item-type ... --item-no ... --color-id N --quantity N --unit-price ... --new-or-used N|U ...]` - Creates a single inventory lot from flags.
- `bricklink.py create-inventory --file batch.json` - Creates multiple inventory lots from a validated JSON file (workspace or /tmp only).
- `bricklink.py update-inventory <inventory_id> [--quantity N --unit-price ... --new-or-used N|U --remarks ...]` - Updates an inventory lot.
- `bricklink.py delete-inventory <inventory_id>` - Deletes an inventory lot.

### Utilities

- `bricklink.py order-detail-html <order_id> [--out path] [--inline-images]` - Fetches order+items and renders a compact HTML view (similar to BrickLink orderDetail.asp).
