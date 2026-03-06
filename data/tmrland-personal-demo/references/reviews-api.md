# Reviews API

Base URL: `/api/v1/reviews`

The reviews system captures personal feedback on orders and aggregates business reputation scores. Reputation combines Grand Apparatus accuracy, Delta scores, user ratings, repurchase rates, and dispute rates.

---

## POST /api/v1/reviews/order/{order_id}

Submit a review for a completed order.

**Auth:** Required (personal only)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID (must be in `confirmed` status) |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `overall_rating` | int | Yes | Overall rating, 1-5 |
| `quality_rating` | int \| None | No | Quality sub-rating, 1-5 |
| `speed_rating` | int \| None | No | Speed sub-rating, 1-5 |
| `title` | str \| None | No | Review title |
| `comment` | str \| None | No | Review comment text |
| `would_repurchase` | bool | No | Whether the personal user would buy again, default `false` |

### Request Example

```json
{
  "overall_rating": 5,
  "quality_rating": 5,
  "speed_rating": 4,
  "title": "专业的金融大模型微调服务",
  "comment": "智能数据科技团队对A股数据的理解非常深入，模型在研报生成任务上的表现远超我们的预期。交付速度略慢于预期，但最终质量非常高。",
  "would_repurchase": true
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "aabb0011-2233-4455-6677-889900112233",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "overall_rating": 5,
  "quality_rating": 5,
  "speed_rating": 4,
  "title": "专业的金融大模型微调服务",
  "comment": "智能数据科技团队对A股数据的理解非常深入，模型在研报生成任务上的表现远超我们的预期。交付速度略慢于预期，但最终质量非常高。",
  "would_repurchase": true,
  "helpful_count": 0,
  "unhelpful_count": 0,
  "created_at": "2026-03-11T11:00:00Z",
  "updated_at": "2026-03-11T11:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Only the personal user can review this order"` | User is not the personal user |
| 404 | `"Order not found"` | Order ID does not exist |
| 409 | `"Order is not in confirmed status"` | Order has not been confirmed |
| 409 | `"Review already exists for this order"` | Personal already submitted a review |
| 422 | Pydantic validation array | Rating out of range |

---

## GET /api/v1/reviews/order/{order_id}

Retrieve the review for a specific order.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

None.

### Request Example

```
GET /api/v1/reviews/order/55667788-99aa-bbcc-ddee-ff0011223344
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "aabb0011-2233-4455-6677-889900112233",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "overall_rating": 5,
  "quality_rating": 5,
  "speed_rating": 4,
  "title": "专业的金融大模型微调服务",
  "comment": "智能数据科技团队对A股数据的理解非常深入，模型在研报生成任务上的表现远超我们的预期。交付速度略慢于预期，但最终质量非常高。",
  "would_repurchase": true,
  "helpful_count": 12,
  "unhelpful_count": 1,
  "created_at": "2026-03-11T11:00:00Z",
  "updated_at": "2026-03-11T11:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 404 | `"Order not found"` | Order ID does not exist |
| 404 | `"Review not found"` | No review for this order |

---

## GET /api/v1/reviews/business/{business_id}

List all reviews for a business with pagination.

**Auth:** None (public)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Items per page, default `20`, max `100` |

### Request Example

```
GET /api/v1/reviews/business/11223344-5566-7788-99aa-bbccddeeff00?offset=0&limit=10
```

### Response Example

**Status: 200 OK**

```json
{
  "items": [
    {
      "id": "aabb0011-2233-4455-6677-889900112233",
      "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
      "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "overall_rating": 5,
      "quality_rating": 5,
      "speed_rating": 4,
      "title": "专业的金融大模型微调服务",
      "comment": "智能数据科技团队对A股数据的理解非常深入...",
      "would_repurchase": true,
      "helpful_count": 12,
      "unhelpful_count": 1,
      "created_at": "2026-03-11T11:00:00Z",
      "updated_at": "2026-03-11T11:00:00Z"
    },
    {
      "id": "bbcc0022-3344-5566-7788-990011223344",
      "order_id": "66778899-aabb-ccdd-eeff-223344556677",
      "personal_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
      "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "overall_rating": 4,
      "quality_rating": 4,
      "speed_rating": 5,
      "title": "数据清洗服务高效可靠",
      "comment": "处理了300万条原始财报数据，清洗质量和速度都令人满意。",
      "would_repurchase": true,
      "helpful_count": 5,
      "unhelpful_count": 0,
      "created_at": "2026-03-05T09:00:00Z",
      "updated_at": "2026-03-05T09:00:00Z"
    }
  ],
  "total": 2
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 404 | `"Business not found"` | Business ID does not exist |

---

## GET /api/v1/reviews/reputation/{business_id}

Retrieve the aggregated reputation score for a business. Combines multiple signal sources into a composite score.

**Auth:** None (public)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Request Body

None.

### Request Example

```
GET /api/v1/reviews/reputation/11223344-5566-7788-99aa-bbccddeeff00
```

### Response Example

**Status: 200 OK**

```json
{
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "apparatus_accuracy_rate": 0.76,
  "apparatus_score": 8.2,
  "delta_mean": 0.83,
  "user_rating_mean": 4.5,
  "repurchase_rate": 0.85,
  "dispute_rate": 0.02,
  "total_orders": 47,
  "total_reviews": 38,
  "reputation_score": 4.7,
  "reputation_tier": "gold",
  "last_calculated_at": "2026-02-27T00:00:00Z",
  "created_at": "2026-01-15T08:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 404 | `"Business not found"` | Business ID does not exist |
| 404 | `"Reputation data not found"` | No reputation data calculated yet |

---

## GET /api/v1/reviews/leaderboard

Retrieve the business reputation leaderboard, ranked by reputation score.

**Auth:** None (public)

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `limit` | int | No | Number of entries to return, default `20`, max `100` |

### Request Example

```
GET /api/v1/reviews/leaderboard?limit=5
```

### Response Example

**Status: 200 OK**

```json
[
  {
    "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
    "apparatus_accuracy_rate": 0.76,
    "apparatus_score": 8.2,
    "delta_mean": 0.83,
    "user_rating_mean": 4.5,
    "repurchase_rate": 0.85,
    "dispute_rate": 0.02,
    "total_orders": 47,
    "total_reviews": 38,
    "reputation_score": 4.7,
    "reputation_tier": "gold",
    "last_calculated_at": "2026-02-27T00:00:00Z",
    "created_at": "2026-01-15T08:00:00Z"
  },
  {
    "business_id": "22334455-6677-8899-aabb-ccddeeff0011",
    "apparatus_accuracy_rate": 0.71,
    "apparatus_score": 7.5,
    "delta_mean": 0.79,
    "user_rating_mean": 4.3,
    "repurchase_rate": 0.78,
    "dispute_rate": 0.04,
    "total_orders": 32,
    "total_reviews": 25,
    "reputation_score": 4.3,
    "reputation_tier": "silver",
    "last_calculated_at": "2026-02-27T00:00:00Z",
    "created_at": "2026-01-20T09:30:00Z"
  },
  {
    "business_id": "33445566-7788-99aa-bbcc-ddeeff001122",
    "apparatus_accuracy_rate": 0.68,
    "apparatus_score": 7.0,
    "delta_mean": 0.75,
    "user_rating_mean": 4.1,
    "repurchase_rate": 0.72,
    "dispute_rate": 0.05,
    "total_orders": 21,
    "total_reviews": 16,
    "reputation_score": 4.1,
    "reputation_tier": "silver",
    "last_calculated_at": "2026-02-27T00:00:00Z",
    "created_at": "2026-02-01T14:00:00Z"
  }
]
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 422 | Pydantic validation array | Invalid limit value |
