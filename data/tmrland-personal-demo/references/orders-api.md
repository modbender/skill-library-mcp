# Orders API

Base URL: `/api/v1/orders`

Orders represent a personal user-business transaction. The personal user creates an order, pays (triggering escrow freeze), and later confirms delivery (releasing funds) or cancels. Businesses deliver and submit deliverables.

All endpoints require authentication. Role annotations indicate which party can perform each action.

---

## POST /api/v1/orders/

Create a new order in `pending` status. The personal user selects a business (typically from match results) and sets the order amount.

**Auth:** Required (personal)

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID \| None | No | Associated intention ID |
| `business_id` | UUID | Yes | Target business ID |
| `contract_template_id` | UUID \| None | No | Contract template to use |
| `contract_id` | UUID \| None | No | Pre-negotiated contract instance ID |
| `contract_terms` | dict | No | Ad-hoc contract terms, default `{}` |
| `amount` | float | Yes | Order amount, must be > 0 |
| `currency` | str | No | Currency code, default `"USD"` |

### Request Example

```json
{
  "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "contract_template_id": "44556677-8899-aabb-ccdd-eeff00112233",
  "contract_terms": {
    "delivery_days": 14,
    "revision_rounds": 2,
    "scope": "金融大模型微调，含A股5年数据"
  },
  "amount": 8000.00,
  "currency": "USD"
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "contract_template_id": "44556677-8899-aabb-ccdd-eeff00112233",
  "contract_id": null,
  "contract_terms": {
    "delivery_days": 14,
    "revision_rounds": 2,
    "scope": "金融大模型微调，含A股5年数据"
  },
  "amount": 8000.00,
  "platform_fee": 400.00,
  "currency": "USD",
  "status": "pending",
  "paid_at": null,
  "delivered_at": null,
  "confirmed_at": null,
  "delivery_notes": null,
  "deliverable_url": null,
  "milestones": null,
  "created_at": "2026-02-27T14:30:00Z",
  "updated_at": "2026-02-27T14:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 400 | `"Business not found or inactive"` | Invalid or inactive business ID |
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 422 | Pydantic validation array | Missing required fields or invalid amount |

---

## GET /api/v1/orders/

List orders for the current user with optional role and status filtering.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `role` | str | No | Filter by role perspective, default `"personal"`. Values: `"personal"`, `"business"` |
| `status_filter` | str \| None | No | Filter by order status: `"pending"`, `"paid"`, `"in_progress"`, `"delivered"`, `"confirmed"`, `"cancelled"`, `"disputed"` |
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Items per page, default `20`, max `100` |

### Request Example

```
GET /api/v1/orders/?role=personal&status_filter=paid&offset=0&limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "items": [
    {
      "id": "55667788-99aa-bbcc-ddee-ff0011223344",
      "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
      "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "contract_template_id": "44556677-8899-aabb-ccdd-eeff00112233",
      "contract_id": null,
      "contract_terms": {
        "delivery_days": 14,
        "revision_rounds": 2,
        "scope": "金融大模型微调，含A股5年数据"
      },
      "amount": 8000.00,
      "platform_fee": 400.00,
      "currency": "USD",
      "status": "paid",
      "paid_at": "2026-02-27T15:00:00Z",
      "delivered_at": null,
      "confirmed_at": null,
      "delivery_notes": null,
      "deliverable_url": null,
      "milestones": null,
      "created_at": "2026-02-27T14:30:00Z",
      "updated_at": "2026-02-27T15:00:00Z"
    }
  ],
  "total": 1
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |

---

## GET /api/v1/orders/{order_id}

Retrieve a single order. Both the personal user and business party can access.

**Auth:** Required (party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

None.

### Request Example

```
GET /api/v1/orders/55667788-99aa-bbcc-ddee-ff0011223344
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "contract_template_id": "44556677-8899-aabb-ccdd-eeff00112233",
  "contract_id": "66778899-aabb-ccdd-eeff-001122334455",
  "contract_terms": {
    "delivery_days": 14,
    "revision_rounds": 2,
    "scope": "金融大模型微调，含A股5年数据"
  },
  "amount": 8000.00,
  "platform_fee": 400.00,
  "currency": "USD",
  "status": "delivered",
  "paid_at": "2026-02-27T15:00:00Z",
  "delivered_at": "2026-03-10T09:00:00Z",
  "confirmed_at": null,
  "delivery_notes": "已完成模型微调，包含基线评测报告和API接口文档。",
  "deliverable_url": "https://cdn.tmrland.com/deliverables/55667788/model-v1.tar.gz",
  "milestones": [
    {"name": "数据预处理", "status": "completed", "completed_at": "2026-03-03T10:00:00Z"},
    {"name": "模型训练", "status": "completed", "completed_at": "2026-03-08T16:00:00Z"},
    {"name": "评测交付", "status": "completed", "completed_at": "2026-03-10T09:00:00Z"}
  ],
  "created_at": "2026-02-27T14:30:00Z",
  "updated_at": "2026-03-10T09:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to access this order"` | User is not personal or business of this order |
| 404 | `"Order not found"` | Order ID does not exist |

---

## POST /api/v1/orders/{order_id}/pay

Pay for an order. Freezes the order amount from the personal user's wallet via escrow.

**Auth:** Required (personal only)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID (must be in `pending` status) |

### Request Body

None.

### Request Example

```
POST /api/v1/orders/55667788-99aa-bbcc-ddee-ff0011223344/pay
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "contract_template_id": "44556677-8899-aabb-ccdd-eeff00112233",
  "contract_id": null,
  "contract_terms": {
    "delivery_days": 14,
    "revision_rounds": 2,
    "scope": "金融大模型微调，含A股5年数据"
  },
  "amount": 8000.00,
  "platform_fee": 400.00,
  "currency": "USD",
  "status": "paid",
  "paid_at": "2026-02-27T15:00:00Z",
  "delivered_at": null,
  "confirmed_at": null,
  "delivery_notes": null,
  "deliverable_url": null,
  "milestones": null,
  "created_at": "2026-02-27T14:30:00Z",
  "updated_at": "2026-02-27T15:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 400 | `"Insufficient wallet balance"` | Available balance < order amount |
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Only the personal user can pay for this order"` | User is not the personal user |
| 404 | `"Order not found"` | Order ID does not exist |
| 409 | `"Order is not in pending status"` | Order status is not `pending` |

---

## POST /api/v1/orders/{order_id}/confirm

Confirm delivery and release escrowed funds to the business.

**Auth:** Required (personal only)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID (must be in `delivered` status) |

### Request Body

None.

### Request Example

```
POST /api/v1/orders/55667788-99aa-bbcc-ddee-ff0011223344/confirm
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "contract_template_id": "44556677-8899-aabb-ccdd-eeff00112233",
  "contract_id": "66778899-aabb-ccdd-eeff-001122334455",
  "contract_terms": {
    "delivery_days": 14,
    "revision_rounds": 2,
    "scope": "金融大模型微调，含A股5年数据"
  },
  "amount": 8000.00,
  "platform_fee": 400.00,
  "currency": "USD",
  "status": "confirmed",
  "paid_at": "2026-02-27T15:00:00Z",
  "delivered_at": "2026-03-10T09:00:00Z",
  "confirmed_at": "2026-03-11T10:00:00Z",
  "delivery_notes": "已完成模型微调，包含基线评测报告和API接口文档。",
  "deliverable_url": "https://cdn.tmrland.com/deliverables/55667788/model-v1.tar.gz",
  "milestones": [
    {"name": "数据预处理", "status": "completed", "completed_at": "2026-03-03T10:00:00Z"},
    {"name": "模型训练", "status": "completed", "completed_at": "2026-03-08T16:00:00Z"},
    {"name": "评测交付", "status": "completed", "completed_at": "2026-03-10T09:00:00Z"}
  ],
  "created_at": "2026-02-27T14:30:00Z",
  "updated_at": "2026-03-11T10:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Only the personal user can confirm this order"` | User is not the personal user |
| 404 | `"Order not found"` | Order ID does not exist |
| 409 | `"Order is not in delivered status"` | Order has not been delivered yet |

---

## POST /api/v1/orders/{order_id}/cancel

Cancel an order. If the order has been paid, escrowed funds are released back to the personal user.

**Auth:** Required (personal only)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID (must be in `pending` or `paid` status) |

### Request Body

None.

### Request Example

```
POST /api/v1/orders/55667788-99aa-bbcc-ddee-ff0011223344/cancel
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "contract_template_id": "44556677-8899-aabb-ccdd-eeff00112233",
  "contract_id": null,
  "contract_terms": {
    "delivery_days": 14,
    "revision_rounds": 2,
    "scope": "金融大模型微调，含A股5年数据"
  },
  "amount": 8000.00,
  "platform_fee": 400.00,
  "currency": "USD",
  "status": "cancelled",
  "paid_at": "2026-02-27T15:00:00Z",
  "delivered_at": null,
  "confirmed_at": null,
  "delivery_notes": null,
  "deliverable_url": null,
  "milestones": null,
  "created_at": "2026-02-27T14:30:00Z",
  "updated_at": "2026-02-27T16:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Only the personal user can cancel this order"` | User is not the personal user |
| 404 | `"Order not found"` | Order ID does not exist |
| 409 | `"Cannot cancel order in current status"` | Order is in `delivered`, `confirmed`, or `disputed` status |

---

## POST /api/v1/orders/{order_id}/dispute

Open a dispute on an order. Both personal and business can initiate disputes.

**Auth:** Required (personal or business)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `reason` | str | Yes | Dispute reason, minimum 10 characters |
| `evidence` | list[str] | No | URLs to evidence files, default `[]` |

### Request Example

```json
{
  "reason": "商家交付的模型微调质量严重不达标，评测指标低于合同约定的基线阈值。",
  "evidence": [
    "https://cdn.tmrland.com/evidence/eval-report-55667788.pdf",
    "https://cdn.tmrland.com/evidence/chat-log-55667788.html"
  ]
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "77889900-aabb-ccdd-eeff-112233445566",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "initiator_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "reason": "商家交付的模型微调质量严重不达标，评测指标低于合同约定的基线阈值。",
  "evidence": [
    "https://cdn.tmrland.com/evidence/eval-report-55667788.pdf",
    "https://cdn.tmrland.com/evidence/chat-log-55667788.html"
  ],
  "contract_snapshot": {},
  "status": "open",
  "resolution": null,
  "resolution_notes": null,
  "resolved_at": null,
  "created_at": "2026-03-12T09:00:00Z",
  "updated_at": "2026-03-12T09:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to dispute this order"` | User is not personal or business |
| 404 | `"Order not found"` | Order ID does not exist |
| 409 | `"Dispute already exists for this order"` | A dispute is already open |
| 409 | `"Cannot dispute order in current status"` | Order status does not allow disputes |
| 422 | Pydantic validation array | Reason too short |

---

## GET /api/v1/orders/{order_id}/dispute

Retrieve the dispute associated with an order.

**Auth:** Required (party or admin)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

None.

### Request Example

```
GET /api/v1/orders/55667788-99aa-bbcc-ddee-ff0011223344/dispute
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "77889900-aabb-ccdd-eeff-112233445566",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "initiator_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "reason": "商家交付的模型微调质量严重不达标，评测指标低于合同约定的基线阈值。",
  "evidence": [
    "https://cdn.tmrland.com/evidence/eval-report-55667788.pdf",
    "https://cdn.tmrland.com/evidence/chat-log-55667788.html"
  ],
  "contract_snapshot": {},
  "status": "open",
  "resolution": null,
  "resolution_notes": null,
  "resolved_at": null,
  "created_at": "2026-03-12T09:00:00Z",
  "updated_at": "2026-03-12T09:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to view this dispute"` | User is not a party or admin |
| 404 | `"Order not found"` | Order ID does not exist |
| 404 | `"Dispute not found"` | No dispute exists for this order |

---

## POST /api/v1/orders/{order_id}/review

Submit a review and generate a receipt after confirming delivery.

**Auth:** Required (personal only)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID (must be in `confirmed` status) |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `rating` | int | Yes | Overall rating, 1-5 |
| `would_repurchase` | bool | No | Whether the personal user would buy again, default `false` |
| `comment` | str \| None | No | Review comment |

### Request Example

```json
{
  "rating": 5,
  "would_repurchase": true,
  "comment": "模型微调效果超出预期，A股行情分析准确率显著提升，交付文档也非常专业。"
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "88990011-2233-4455-6677-8899aabbccdd",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "amount": 8000.00,
  "platform_fee": 400.00,
  "business_income": 7600.00,
  "currency": "USD",
  "cost_breakdown": {
    "subtotal": 8000.00,
    "platform_fee": 400.00,
    "platform_fee_rate": 0.05,
    "business_payout": 7600.00
  },
  "personal_signal": {
    "rating": 5,
    "would_repurchase": true,
    "comment": "模型微调效果超出预期，A股行情分析准确率显著提升，交付文档也非常专业。"
  },
  "delta_score": 0.87,
  "response_time_ms": 1423,
  "contract_id": "66778899-aabb-ccdd-eeff-001122334455",
  "created_at": "2026-03-11T10:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Only the personal user can review this order"` | User is not the personal user |
| 404 | `"Order not found"` | Order ID does not exist |
| 409 | `"Order is not in confirmed status"` | Order has not been confirmed yet |
| 409 | `"Review already submitted for this order"` | Personal already reviewed |
| 422 | Pydantic validation array | Rating out of range |

---

## GET /api/v1/orders/{order_id}/receipt

Retrieve the receipt for a completed order.

**Auth:** Required (party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

None.

### Request Example

```
GET /api/v1/orders/55667788-99aa-bbcc-ddee-ff0011223344/receipt
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "88990011-2233-4455-6677-8899aabbccdd",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "amount": 8000.00,
  "platform_fee": 400.00,
  "business_income": 7600.00,
  "currency": "USD",
  "cost_breakdown": {
    "subtotal": 8000.00,
    "platform_fee": 400.00,
    "platform_fee_rate": 0.05,
    "business_payout": 7600.00
  },
  "personal_signal": {
    "rating": 5,
    "would_repurchase": true,
    "comment": "模型微调效果超出预期，A股行情分析准确率显著提升，交付文档也非常专业。"
  },
  "delta_score": 0.87,
  "response_time_ms": 1423,
  "contract_id": "66778899-aabb-ccdd-eeff-001122334455",
  "created_at": "2026-03-11T10:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to view this receipt"` | User is not a party to the order |
| 404 | `"Order not found"` | Order ID does not exist |
| 404 | `"Receipt not found"` | Order has not been reviewed yet |
