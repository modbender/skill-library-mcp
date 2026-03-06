# Reviews API

Base URL: `/api/v1/reviews`

Personal reviews of business deliveries and the reputation scoring system. Reviews are tied to completed orders. The reputation score aggregates reviews, delta scores, and Grand Apparatus performance.

---

## POST /api/v1/reviews/order/{order_id}

Submit a review for a completed order. Only the personal user can review.

**Auth:** Required (personal only)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID to review |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `overall_rating` | int | Yes | Overall rating, 1-5 |
| `quality_rating` | int | Yes | Quality rating, 1-5 |
| `speed_rating` | int | Yes | Speed/timeliness rating, 1-5 |
| `title` | str \| null | No | Review title |
| `comment` | str \| null | No | Review comment text |
| `would_repurchase` | bool | No | Whether the personal user would order again |

### Request Example

```json
{
  "overall_rating": 5,
  "quality_rating": 5,
  "speed_rating": 4,
  "title": "Excellent financial analysis with proprietary insights",
  "comment": "SmartData Tech delivered a comprehensive report that far exceeded what I could get from public data sources. The proprietary dataset covering 2,800+ companies provided genuinely unique insights. Delivery was slightly slower than promised but the quality made up for it.",
  "would_repurchase": true
}
```

### Response Example

```json
{
  "id": "ee112233-4455-6677-8899-aabbccddeeff",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "overall_rating": 5,
  "quality_rating": 5,
  "speed_rating": 4,
  "title": "Excellent financial analysis with proprietary insights",
  "comment": "SmartData Tech delivered a comprehensive report that far exceeded what I could get from public data sources. The proprietary dataset covering 2,800+ companies provided genuinely unique insights. Delivery was slightly slower than promised but the quality made up for it.",
  "would_repurchase": true,
  "created_at": "2026-03-02T10:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_personal` | Only the personal user can review an order |
| 404 | `order_not_found` | No order with this ID |
| 409 | `review_already_exists` | A review already exists for this order |
| 409 | `order_not_completed` | Order must be in `completed` status to be reviewed |
| 422 | `validation_error` | Rating values must be between 1 and 5 |

---

## GET /api/v1/reviews/order/{order_id}

Retrieve the review for a specific order.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Example

```
GET /api/v1/reviews/order/11223344-5566-7788-99aa-bbccddeeff00
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "ee112233-4455-6677-8899-aabbccddeeff",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "overall_rating": 5,
  "quality_rating": 5,
  "speed_rating": 4,
  "title": "Excellent financial analysis with proprietary insights",
  "comment": "SmartData Tech delivered a comprehensive report that far exceeded what I could get from public data sources.",
  "would_repurchase": true,
  "created_at": "2026-03-02T10:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `review_not_found` | No review found for this order |

---

## GET /api/v1/reviews/business/{business_id}

List all reviews for a business. Public endpoint.

**Auth:** None

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Request Example

```
GET /api/v1/reviews/business/b2c3d4e5-f6a7-8901-bcde-f12345678901
```

### Response Example

```json
[
  {
    "id": "ee112233-4455-6677-8899-aabbccddeeff",
    "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
    "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
    "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "overall_rating": 5,
    "quality_rating": 5,
    "speed_rating": 4,
    "title": "Excellent financial analysis with proprietary insights",
    "comment": "SmartData Tech delivered a comprehensive report that far exceeded what I could get from public data sources.",
    "would_repurchase": true,
    "created_at": "2026-03-02T10:00:00Z"
  },
  {
    "id": "ff223344-5566-7788-99aa-bbccddeeff11",
    "order_id": "22334455-6677-8899-aabb-ccddeeff0011",
    "personal_id": "bbccddee-ff00-1122-3344-556677889900",
    "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "overall_rating": 4,
    "quality_rating": 4,
    "speed_rating": 5,
    "title": "Solid market research, fast turnaround",
    "comment": "Good quality research report delivered ahead of schedule. Data was accurate though could have had more sector-specific drill-downs.",
    "would_repurchase": true,
    "created_at": "2026-02-20T14:30:00Z"
  }
]
```

### Errors

| Status | Code | Description |
|---|---|---|
| 404 | `business_not_found` | No business with this ID |

---

## GET /api/v1/reviews/reputation/{business_id}

Retrieve the computed reputation score and breakdown for a business. Public endpoint.

**Auth:** None

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Request Example

```
GET /api/v1/reviews/reputation/b2c3d4e5-f6a7-8901-bcde-f12345678901
```

### Response Example

```json
{
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "apparatus_accuracy_rate": 0.78,
  "apparatus_score": 8.2,
  "delta_mean": 8.87,
  "user_rating_mean": 4.5,
  "repurchase_rate": 0.92,
  "dispute_rate": 0.02,
  "total_orders": 48,
  "total_reviews": 35,
  "reputation_score": 87.5,
  "reputation_tier": "gold",
  "last_calculated_at": "2026-02-27T00:00:00Z",
  "created_at": "2026-01-15T08:20:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 404 | `business_not_found` | No business with this ID |
| 404 | `reputation_not_found` | Reputation data not yet computed for this business |

---

## GET /api/v1/reviews/leaderboard

Retrieve the business reputation leaderboard. Public endpoint.

**Auth:** None

### Request Example

```
GET /api/v1/reviews/leaderboard
```

### Response Example

```json
[
  {
    "rank": 1,
    "business_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "brand_name_zh": "深蓝翻译",
    "brand_name_en": "DeepBlue Translation",
    "reputation_score": 92.1,
    "reputation_tier": "platinum",
    "total_orders": 156,
    "delta_mean": 9.1
  },
  {
    "rank": 2,
    "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "brand_name_zh": "智能数据科技",
    "brand_name_en": "SmartData Tech",
    "reputation_score": 87.5,
    "reputation_tier": "gold",
    "total_orders": 48,
    "delta_mean": 8.87
  },
  {
    "rank": 3,
    "business_id": "a7b8c9d0-e1f2-3456-abcd-789012345678",
    "brand_name_zh": "云视觉设计",
    "brand_name_en": "CloudVision Design",
    "reputation_score": 84.3,
    "reputation_tier": "gold",
    "total_orders": 72,
    "delta_mean": 7.9
  }
]
```

### Errors

| Status | Code | Description |
|---|---|---|
| 500 | `internal_error` | Failed to compute leaderboard |
