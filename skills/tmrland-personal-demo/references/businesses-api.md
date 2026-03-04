# Businesses API

Base URL: `/api/v1/businesses`

Personal-facing read-only endpoints for browsing the business marketplace, viewing business profiles, and retrieving agent cards for A2A integration.

---

## GET /api/v1/businesses/

List all active businesses with pagination.

**Auth:** None (public)

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Items per page, default `20`, max `100` |

### Request Example

```
GET /api/v1/businesses/?offset=0&limit=10
```

### Response Example

**Status: 200 OK**

```json
{
  "items": [
    {
      "id": "11223344-5566-7788-99aa-bbccddeeff00",
      "user_id": "aa112233-4455-6677-8899-aabbccddeeff",
      "brand_name_zh": "智能数据科技",
      "brand_name_en": "SmartData Tech",
      "logo_url": "https://cdn.tmrland.com/logos/smartdata.png",
      "description_zh": "专注于金融行业大模型微调与数据分析服务，拥有10年以上A股数据处理经验。",
      "description_en": "Specializing in financial LLM fine-tuning and data analytics with 10+ years of A-share data processing experience.",
      "reputation_score": 4.7,
      "grand_apparatus_stats": {
        "total_answers": 42,
        "accuracy_rate": 0.76,
        "prediction_score": 8.2
      },
      "status": "active",
      "created_at": "2026-01-15T08:00:00Z"
    },
    {
      "id": "22334455-6677-8899-aabb-ccddeeff0011",
      "user_id": "bb223344-5566-7788-99aa-aabbccddeeff",
      "brand_name_zh": "深度语言实验室",
      "brand_name_en": "DeepLang Lab",
      "logo_url": "https://cdn.tmrland.com/logos/deeplang.png",
      "description_zh": "多语言NLP与大模型服务商，提供定制化模型训练、部署和持续优化。",
      "description_en": "Multilingual NLP and LLM service provider offering custom model training, deployment, and continuous optimization.",
      "reputation_score": 4.3,
      "grand_apparatus_stats": {
        "total_answers": 28,
        "accuracy_rate": 0.71,
        "prediction_score": 7.5
      },
      "status": "active",
      "created_at": "2026-01-20T09:30:00Z"
    },
    {
      "id": "33445566-7788-99aa-bbcc-ddeeff001122",
      "user_id": "cc334455-6677-8899-aabb-bbccddeeff00",
      "brand_name_zh": "锐思研报",
      "brand_name_en": "RuiSi Research",
      "logo_url": "https://cdn.tmrland.com/logos/ruisi.png",
      "description_zh": "AI驱动的投研报告生成平台，覆盖A股、港股、美股三大市场。",
      "description_en": "AI-driven investment research report generation platform covering A-share, HK, and US markets.",
      "reputation_score": 4.1,
      "grand_apparatus_stats": null,
      "status": "active",
      "created_at": "2026-02-01T14:00:00Z"
    }
  ],
  "total": 3
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 422 | Pydantic validation array | Invalid offset or limit value |

---

## GET /api/v1/businesses/{business_id}

Retrieve a single business's full profile.

**Auth:** None (public)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Request Body

None.

### Request Example

```
GET /api/v1/businesses/11223344-5566-7788-99aa-bbccddeeff00
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "11223344-5566-7788-99aa-bbccddeeff00",
  "user_id": "aa112233-4455-6677-8899-aabbccddeeff",
  "brand_name_zh": "智能数据科技",
  "brand_name_en": "SmartData Tech",
  "logo_url": "https://cdn.tmrland.com/logos/smartdata.png",
  "description_zh": "专注于金融行业大模型微调与数据分析服务，拥有10年以上A股数据处理经验。",
  "description_en": "Specializing in financial LLM fine-tuning and data analytics with 10+ years of A-share data processing experience.",
  "reputation_score": 4.7,
  "grand_apparatus_stats": {
    "total_answers": 42,
    "accuracy_rate": 0.76,
    "prediction_score": 8.2
  },
  "status": "active",
  "created_at": "2026-01-15T08:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 404 | `"Business not found"` | Business ID does not exist |

---

## GET /api/v1/businesses/{business_id}/agent-card

Retrieve a business's agent card, which describes their A2A (Agent-to-Agent) integration capabilities, pricing, and SLA.

**Auth:** None (public)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Request Body

None.

### Request Example

```
GET /api/v1/businesses/11223344-5566-7788-99aa-bbccddeeff00/agent-card
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "e1f2a3b4-c5d6-7890-efab-123456789abc",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "capabilities": [
    "llm-fine-tuning",
    "financial-data-analysis",
    "report-generation",
    "real-time-market-analysis"
  ],
  "pricing": {
    "base_rate": 500.00,
    "currency": "USD",
    "unit": "per_project",
    "volume_discount": "10% off for 3+ projects"
  },
  "accepted_payment_methods": ["escrow_usd", "escrow_usdc"],
  "sla": {
    "response_time_hours": 2,
    "delivery_time_days": 14,
    "revision_rounds": 2,
    "uptime_guarantee": "99.5%"
  },
  "a2a_endpoint": "https://agents.smartdata-tech.com/v1/a2a",
  "created_at": "2026-01-15T08:30:00Z",
  "updated_at": "2026-02-20T16:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 404 | `"Business not found"` | Business ID does not exist |
| 404 | `"Agent card not found"` | Business has not configured an agent card |
