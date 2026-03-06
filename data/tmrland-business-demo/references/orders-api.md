# Orders API

Base URL: `/api/v1/orders`

Order lifecycle endpoints. Businesses interact with orders primarily to view orders assigned to them and to deliver completed work. The `role=business` query parameter filters orders to those where the authenticated user is the business.

---

## POST /api/v1/orders/

Create a new order. Typically initiated by a personal user, but businesses can also create orders when receiving direct requests.

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID \| null | No | Link to a personal user intention that triggered this order |
| `business_id` | UUID | Yes | The business fulfilling the order |
| `contract_template_id` | UUID \| null | No | Contract template to apply |
| `contract_id` | UUID \| null | No | Existing negotiated contract to use |
| `contract_terms` | dict | No | Custom contract terms. Default `{}` |
| `amount` | float | Yes | Order amount, must be greater than 0 |
| `currency` | str | No | Payment currency. Default `"USD"` |

### Request Example

```json
{
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "contract_template_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "contract_terms": {
    "delivery_days": 3,
    "revisions": 2,
    "scope": "Full financial analysis report with visualizations"
  },
  "amount": 150.00,
  "currency": "USD"
}
```

### Response Example

```json
{
  "id": "11223344-5566-7788-99aa-bbccddeeff00",
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "contract_template_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "contract_id": null,
  "contract_terms": {
    "delivery_days": 3,
    "revisions": 2,
    "scope": "Full financial analysis report with visualizations"
  },
  "amount": 150.00,
  "platform_fee": 15.00,
  "currency": "USD",
  "status": "pending_payment",
  "paid_at": null,
  "delivered_at": null,
  "confirmed_at": null,
  "delivery_notes": null,
  "deliverable_url": null,
  "milestones": null,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `business_not_found` | No business with the given ID |
| 422 | `validation_error` | Amount must be greater than 0 or missing required fields |

---

## GET /api/v1/orders/

List orders for the authenticated user. Use `role=business` to retrieve orders where you are the assigned business.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `role` | str | No | `"personal"` or `"business"`. Default `"business"`. **Use `"business"` to view orders assigned to you as a business.** |
| `status_filter` | str \| null | No | Filter by order status (e.g., `"paid"`, `"delivered"`, `"completed"`) |
| `offset` | int | No | Pagination offset. Default `0` |
| `limit` | int | No | Number of results. Default `20` |

### Request Example

```
GET /api/v1/orders/?role=business&status_filter=paid&offset=0&limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "items": [
    {
      "id": "11223344-5566-7788-99aa-bbccddeeff00",
      "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
      "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
      "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "contract_template_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
      "contract_id": null,
      "contract_terms": {
        "delivery_days": 3,
        "revisions": 2,
        "scope": "Full financial analysis report with visualizations"
      },
      "amount": 150.00,
      "platform_fee": 15.00,
      "currency": "USD",
      "status": "paid",
      "paid_at": "2026-02-27T11:00:00Z",
      "delivered_at": null,
      "confirmed_at": null,
      "delivery_notes": null,
      "deliverable_url": null,
      "milestones": null,
      "created_at": "2026-02-27T10:30:00Z",
      "updated_at": "2026-02-27T11:00:00Z"
    }
  ],
  "total": 1
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 422 | `validation_error` | Invalid role or status_filter value |

---

## GET /api/v1/orders/{order_id}

Retrieve a specific order. Both the personal user and business parties can access.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Example

```
GET /api/v1/orders/11223344-5566-7788-99aa-bbccddeeff00
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "11223344-5566-7788-99aa-bbccddeeff00",
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "contract_template_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "contract_id": null,
  "contract_terms": {
    "delivery_days": 3,
    "revisions": 2,
    "scope": "Full financial analysis report with visualizations"
  },
  "amount": 150.00,
  "platform_fee": 15.00,
  "currency": "USD",
  "status": "paid",
  "paid_at": "2026-02-27T11:00:00Z",
  "delivered_at": null,
  "confirmed_at": null,
  "delivery_notes": null,
  "deliverable_url": null,
  "milestones": null,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T11:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not the personal user or business on this order |
| 404 | `order_not_found` | No order with this ID |

---

## POST /api/v1/orders/{order_id}/deliver

Submit a delivery for an order. **Business only.** Transitions the order status to `delivered`.

**Auth:** Required (business only)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `delivery_notes` | str \| null | No | Notes describing the deliverable |
| `deliverable_url` | str \| null | No | URL to the delivered artifact |

### Request Example

```json
{
  "delivery_notes": "Comprehensive financial analysis report covering Q4 2025 market trends, sector performance breakdown, and 2026 outlook with 15 interactive visualizations.",
  "deliverable_url": "https://cdn.tmrland.com/deliverables/11223344/report-v1.pdf"
}
```

### Response Example

```json
{
  "id": "11223344-5566-7788-99aa-bbccddeeff00",
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "contract_template_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "contract_id": null,
  "contract_terms": {
    "delivery_days": 3,
    "revisions": 2,
    "scope": "Full financial analysis report with visualizations"
  },
  "amount": 150.00,
  "platform_fee": 15.00,
  "currency": "USD",
  "status": "delivered",
  "paid_at": "2026-02-27T11:00:00Z",
  "delivered_at": "2026-02-28T09:15:00Z",
  "confirmed_at": null,
  "delivery_notes": "Comprehensive financial analysis report covering Q4 2025 market trends, sector performance breakdown, and 2026 outlook with 15 interactive visualizations.",
  "deliverable_url": "https://cdn.tmrland.com/deliverables/11223344/report-v1.pdf",
  "milestones": null,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-28T09:15:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_business` | Only the assigned business can deliver |
| 404 | `order_not_found` | No order with this ID |
| 409 | `invalid_status_transition` | Order is not in a deliverable state (must be `paid`) |

---

## POST /api/v1/orders/{order_id}/cancel

Cancel an order. Only the personal user can cancel.

**Auth:** Required (personal only)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

None.

### Request Example

```
POST /api/v1/orders/11223344-5566-7788-99aa-bbccddeeff00/cancel
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "11223344-5566-7788-99aa-bbccddeeff00",
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "contract_template_id": null,
  "contract_id": null,
  "contract_terms": {},
  "amount": 150.00,
  "platform_fee": 15.00,
  "currency": "USD",
  "status": "cancelled",
  "paid_at": null,
  "delivered_at": null,
  "confirmed_at": null,
  "delivery_notes": null,
  "deliverable_url": null,
  "milestones": null,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T12:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_personal` | Only the personal user can cancel an order |
| 404 | `order_not_found` | No order with this ID |
| 409 | `invalid_status_transition` | Order cannot be cancelled in its current state |

---

## POST /api/v1/orders/{order_id}/dispute

Open a dispute on an order. Both personal and business can initiate.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `reason` | str | Yes | Dispute reason, minimum 10 characters |
| `evidence` | list[str] | No | URLs to supporting evidence. Default `[]` |

### Request Example

```json
{
  "reason": "The personal user has not responded to the delivery for over 7 days, requesting auto-confirmation of the order.",
  "evidence": [
    "https://cdn.tmrland.com/evidence/delivery-confirmation-screenshot.png",
    "https://cdn.tmrland.com/evidence/message-history-export.pdf"
  ]
}
```

### Response Example

```json
{
  "id": "99887766-5544-3322-1100-ffeeddccbbaa",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "initiated_by": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "reason": "The personal user has not responded to the delivery for over 7 days, requesting auto-confirmation of the order.",
  "evidence": [
    "https://cdn.tmrland.com/evidence/delivery-confirmation-screenshot.png",
    "https://cdn.tmrland.com/evidence/message-history-export.pdf"
  ],
  "contract_snapshot": {},
  "status": "open",
  "resolution": null,
  "resolved_at": null,
  "created_at": "2026-03-05T14:00:00Z",
  "updated_at": "2026-03-05T14:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not the personal user or business on this order |
| 404 | `order_not_found` | No order with this ID |
| 409 | `dispute_already_exists` | A dispute is already open for this order |
| 422 | `validation_error` | Reason must be at least 10 characters |

---

## GET /api/v1/orders/{order_id}/dispute

Retrieve the dispute associated with an order.

**Auth:** Required (personal, business, or admin)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Example

```
GET /api/v1/orders/11223344-5566-7788-99aa-bbccddeeff00/dispute
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "99887766-5544-3322-1100-ffeeddccbbaa",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "initiated_by": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "reason": "The personal user has not responded to the delivery for over 7 days, requesting auto-confirmation of the order.",
  "evidence": [
    "https://cdn.tmrland.com/evidence/delivery-confirmation-screenshot.png"
  ],
  "contract_snapshot": {},
  "status": "open",
  "resolution": null,
  "resolved_at": null,
  "created_at": "2026-03-05T14:00:00Z",
  "updated_at": "2026-03-05T14:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not a party to this order or an admin |
| 404 | `dispute_not_found` | No dispute found for this order |

---

## GET /api/v1/orders/{order_id}/receipt

Retrieve the receipt for a completed order. Includes cost breakdown and delta score.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Example

```
GET /api/v1/orders/11223344-5566-7788-99aa-bbccddeeff00/receipt
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "aabb1122-3344-5566-7788-99aabbccddee",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "amount": 150.00,
  "platform_fee": 15.00,
  "business_income": 135.00,
  "currency": "USD",
  "cost_breakdown": {
    "base_amount": 150.00,
    "platform_fee_rate": 0.10,
    "platform_fee": 15.00,
    "business_payout": 135.00
  },
  "personal_signal": "satisfied",
  "delta_score": 8.7,
  "response_time_ms": 45200,
  "contract_id": null,
  "created_at": "2026-03-01T16:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not a party to this order |
| 404 | `receipt_not_found` | Order has no receipt (not yet completed) |
