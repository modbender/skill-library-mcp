---
name: pipe17
description: Pipe17 Unified API for searching and reading orders, shipping requests (shipments), fulfillments, and inventory.
---

# pipe17

Use the Pipe17 Unified API to search and read core commerce/operations objects.

This skill focuses on:

- Search + read **Orders**
- Search + read **Shipping Requests** (a.k.a. **Shipments**)
- Search + read **Fulfillments**
- Search **Inventory** by SKU (and optionally location)

## Setup

1. Create / obtain a Pipe17 API key for the target organization/integration.
2. Export it:

```bash
export PIPE17_API_KEY="..."
```

> Keep the API key secret. Use least-privilege keys whenever possible.

## API Basics

**Base URL** (default):

```
https://api-v3.pipe17.com/api/v3
```

All requests should include:

- `X-Pipe17-Key: ${PIPE17_API_KEY}`
- `Accept: application/json`

Example:

```bash
P17_BASE="https://api-v3.pipe17.com/api/v3"

curl "${P17_BASE}/orders" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"
```

## Search & Filtering

Pipe17 commonly supports server-side filtering via query parameters, often including:

- `filters=...` (repeatable)
- `limit=...`
- `page=...`

A common filter encoding pattern looks like:

```
filters={type}~{field}~{operator}~{value}
```

Examples of typical patterns:

- `filters=string~status~equals~readyForFulfillment`
- `filters=string~status~equalsAnyOf~new,onHold,readyForFulfillment`
- `filters=date~extOrderCreatedAt~isGreaterThanOrEqualTo~2024-12-31T00:00:00.000Z`

If your tenant uses a different filter grammar, follow the contract in the API doc.

## Orders

### Search orders

List orders with optional query parameters.

| Parameter | Type | Description |
|-----------|------|-------------|
| `count` | integer (int32) | Number of results to return |
| `skip` | integer (int32) | Number of results to skip (for pagination) |
| `extOrderId` | array[string] | Filter by external order ID(s) |
| `since` | string (date-time) | Filter orders since this UTC ISO timestamp |
| `status` | array[string] | Filter by status(es) |

**Allowed `status` values:** `draft`, `new`, `onHold`, `toBeValidated`, `reviewRequired`, `readyForFulfillment`, `sentToFulfillment`, `partialFulfillment`, `fulfilled`, `inTransit`, `partialReceived`, `received`, `canceled`, `returned`, `refunded`, `archived`, `closed`

```bash
P17_BASE="https://api-v3.pipe17.com/api/v3"

# Example: most recent orders (paging)
curl "${P17_BASE}/orders?count=25&skip=0" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: filter by status
curl "${P17_BASE}/orders?count=25&status=new&status=onHold&status=readyForFulfillment" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: filter by date
curl "${P17_BASE}/orders?count=25&since=2024-12-31T00:00:00.000Z" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: filter by external order ID
curl "${P17_BASE}/orders?extOrderId=EXT-12345" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"
```

### Read order by id

The search endpoint returns an `orderId` for each order. Use it to fetch full order details.

```bash
P17_BASE="https://api-v3.pipe17.com/api/v3"
ORDER_ID="{orderId}"

curl "${P17_BASE}/orders/${ORDER_ID}" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"
```

## Shipping Requests

### Search shipping requests

List shipping requests with optional query parameters.

| Parameter | Type | Description |
|-----------|------|-------------|
| `count` | integer (int32) | Number of results to return |
| `skip` | integer (int32) | Number of results to skip (for pagination) |
| `extOrderId` | array[string] | Filter by external order ID(s) |
| `orderId` | array[string] | Filter by Pipe17 order ID(s) |
| `locationId` | array[string] | Filter by location ID(s) |
| `since` | string (date-time) | Filter shipping requests since this UTC ISO timestamp |
| `status` | array[string] | Filter by status(es) |

**Allowed `status` values:** `new`, `pendingInventory`, `pendingShippingLabel`, `reviewRequired`, `readyForFulfillment`, `sentToFulfillment`, `fulfilled`, `partialFulfillment`, `canceled`, `canceledRestock`, `failed`, `onHold`

```bash
P17_BASE="https://api-v3.pipe17.com/api/v3"

# Example: list shipping requests
curl "${P17_BASE}/shipping_requests?count=25&skip=0" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: filter by status
curl "${P17_BASE}/shipping_requests?count=25&status=readyForFulfillment" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: filter by order ID
curl "${P17_BASE}/shipping_requests?count=25&orderId=ORD-12345" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: filter by location
curl "${P17_BASE}/shipping_requests?count=25&locationId=LOC-001" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"
```

### Read shipping request by id

```bash
P17_BASE="https://api-v3.pipe17.com/api/v3"
SHIPPING_REQUEST_ID="{shippingRequestId}"

curl "${P17_BASE}/shipping_requests/${SHIPPING_REQUEST_ID}" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"
```

## Fulfillments

Fulfillments represent completed shipment execution with tracking and shipped line items. They are typically treated as immutable once created.

### Search fulfillments

List fulfillments with optional query parameters.

| Parameter | Type | Description |
|-----------|------|-------------|
| `count` | integer (int32) | Number of results to return |
| `skip` | integer (int32) | Number of results to skip (for pagination) |
| `extOrderId` | array[string] | Filter by external order ID(s) |
| `orderId` | array[string] | Filter by Pipe17 order ID(s) |
| `shipmentId` | array[string] | Filter by shipment ID(s) |
| `locationId` | array[string] | Filter by location ID(s) |
| `since` | string (date-time) | Filter fulfillments since this UTC ISO timestamp |

```bash
P17_BASE="https://api-v3.pipe17.com/api/v3"

# Example: list fulfillments
curl "${P17_BASE}/fulfillments?count=25&skip=0" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: filter by order ID
curl "${P17_BASE}/fulfillments?count=25&orderId=ORD-12345" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: filter by shipment ID
curl "${P17_BASE}/fulfillments?count=25&shipmentId=SHIP-001" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: filter by date
curl "${P17_BASE}/fulfillments?count=25&since=2024-12-31T00:00:00.000Z" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"
```

### Read fulfillment by id

```bash
P17_BASE="https://api-v3.pipe17.com/api/v3"
FULFILLMENT_ID="{fulfillmentId}"

curl "${P17_BASE}/fulfillments/${FULFILLMENT_ID}" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"
```

## Inventory

Inventory is stored per **SKU** (and often per **location**) and may include multiple quantity types (e.g., onHand, available, committed, etc.).

### Search inventory

List inventory with optional query parameters.

| Parameter | Type | Description |
|-----------|------|-------------|
| `count` | integer (int32) | Number of results to return |
| `skip` | integer (int32) | Number of results to skip (for pagination) |
| `sku` | array[string] | Filter by SKU(s). Mutually exclusive with `sku_gt`/`sku_lt` |
| `locationId` | array[string] | Filter by location ID(s) |
| `since` | string (date-time) | Filter inventory created after this UTC ISO timestamp |
| `available` | integer | Filter where `available` equals this value. Mutually exclusive with `available_gt`/`available_lt` |
| `available_gt` | integer | Filter where `available` is greater than this value |
| `available_lt` | integer | Filter where `available` is less than this value |
| `onHand` | integer | Filter where `onHand` equals this value. Mutually exclusive with `onHand_gt`/`onHand_lt` |
| `onHand_gt` | integer | Filter where `onHand` is greater than this value |
| `onHand_lt` | integer | Filter where `onHand` is less than this value |
| `totals` | boolean | Return inventory totals across all locations (not allowed with `ledger` flag) |
| `ledger` | boolean | Return inventory ledger information (not allowed with `totals` flag) |

> **Default behavior:** Always send `totals=true` unless the user specifically requests ledger detail. `totals` and `ledger` are mutually exclusive.

```bash
P17_BASE="https://api-v3.pipe17.com/api/v3"

# Example: list inventory by SKU (always use totals=true by default)
curl "${P17_BASE}/inventory?count=100&sku=MY-SKU-001&totals=true" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: SKU + location
curl "${P17_BASE}/inventory?count=100&sku=MY-SKU-001&locationId=LOC-001&totals=true" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: find items with zero available
curl "${P17_BASE}/inventory?count=100&available=0&totals=true" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: find items with available > 10
curl "${P17_BASE}/inventory?count=100&available_gt=10&totals=true" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"

# Example: get ledger detail (only when specifically requested)
curl "${P17_BASE}/inventory?count=100&sku=MY-SKU-001&ledger=true" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"
```

### Read inventory record by inventoryId

```bash
P17_BASE="https://api-v3.pipe17.com/api/v3"
INVENTORY_ID="{inventoryId}"

curl "${P17_BASE}/inventory/${INVENTORY_ID}" \
  -H "X-Pipe17-Key: ${PIPE17_API_KEY}" \
  -H "Accept: application/json"
```

## Notes

- Prefer **list/search** endpoints with pagination (`count`, `skip`) for support workflows.
- Favor narrow filters (status/date/sku) to avoid pulling large result sets.
- If you hit rate limits, implement backoff and retry according to response headers.

## References

- Pipe17 Unified API Docs: [https://apidoc.pipe17.com/#/](https://apidoc.pipe17.com/#/)

