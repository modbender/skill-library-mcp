# Delta API

Base URL: `/api/v1/delta`

The Delta system measures business quality by comparing a bare LLM baseline response against the business's actual delivery. An LLM-as-judge scores the difference, producing a delta score that feeds into the business's reputation.

---

## POST /api/v1/delta/generate/{intention_id}

Generate a bare-model baseline response for an intention. This establishes the baseline that the business's delivery will be compared against.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID | Yes | Intention to generate a baseline for |

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID \| null | No | Link to a specific order |

### Request Example

```
POST /api/v1/delta/generate/f6a7b8c9-d0e1-2345-fab0-678901234567?order_id=11223344-5566-7788-99aa-bbccddeeff00
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "dd112233-4455-6677-8899-aabbccddeeff",
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "bare_model_response": "Based on publicly available financial data for Q4 2025, the technology sector showed moderate growth of approximately 8.2% driven by AI infrastructure spending. Key trends include increased enterprise adoption of generative AI tools, continued semiconductor demand, and a shift toward edge computing architectures...",
  "business_response": null,
  "delta_analysis": null,
  "delta_summary": null,
  "delta_score": null,
  "status": "baseline_generated",
  "baseline_generated_at": "2026-02-27T10:30:00Z",
  "compared_at": null,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `intention_not_found` | No intention with this ID |
| 409 | `baseline_already_generated` | A baseline already exists for this intention/order pair |
| 500 | `llm_generation_failed` | The LLM service failed to generate a baseline |

---

## GET /api/v1/delta/{delta_id}

Retrieve a specific delta evaluation by ID.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `delta_id` | UUID | Yes | Delta evaluation ID |

### Request Example

```
GET /api/v1/delta/dd112233-4455-6677-8899-aabbccddeeff
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "dd112233-4455-6677-8899-aabbccddeeff",
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "bare_model_response": "Based on publicly available financial data for Q4 2025, the technology sector showed moderate growth of approximately 8.2%...",
  "business_response": "Our proprietary analysis of Q4 2025 technology sector performance reveals 9.1% growth, outpacing consensus estimates by 0.9pp. Using our real-time data pipeline covering 2,847 public and private companies, we identified three underreported catalysts: (1) sovereign AI infrastructure spending in APAC grew 34% QoQ...",
  "delta_analysis": {
    "dimensions": {
      "accuracy": {"score": 9.2, "rationale": "Business provides more precise growth figures backed by proprietary data covering 2,847 companies vs generic public data estimates"},
      "depth": {"score": 8.8, "rationale": "Three specific underreported catalysts identified with quantitative backing"},
      "actionability": {"score": 8.5, "rationale": "Clear investment implications and sector-specific recommendations"},
      "timeliness": {"score": 9.0, "rationale": "Real-time pipeline data more current than baseline's publicly available summaries"}
    },
    "overall_assessment": "Business delivery significantly exceeds the bare-model baseline across all evaluation dimensions"
  },
  "delta_summary": "Business output demonstrates substantial value-add through proprietary data coverage (2,847 companies), more precise growth metrics (9.1% vs estimated 8.2%), and identification of three underreported market catalysts with quantitative support.",
  "delta_score": 8.87,
  "status": "compared",
  "baseline_generated_at": "2026-02-27T10:30:00Z",
  "compared_at": "2026-03-01T16:30:00Z",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-03-01T16:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `delta_not_found` | No delta evaluation with this ID |

---

## GET /api/v1/delta/by-order/{order_id}

Retrieve the delta evaluation associated with a specific order.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Example

```
GET /api/v1/delta/by-order/11223344-5566-7788-99aa-bbccddeeff00
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "dd112233-4455-6677-8899-aabbccddeeff",
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "bare_model_response": "Based on publicly available financial data for Q4 2025...",
  "business_response": "Our proprietary analysis of Q4 2025 technology sector performance...",
  "delta_analysis": {
    "dimensions": {
      "accuracy": {"score": 9.2, "rationale": "More precise growth figures backed by proprietary data"},
      "depth": {"score": 8.8, "rationale": "Three specific underreported catalysts identified"},
      "actionability": {"score": 8.5, "rationale": "Clear investment implications"},
      "timeliness": {"score": 9.0, "rationale": "Real-time pipeline data"}
    },
    "overall_assessment": "Business delivery significantly exceeds the bare-model baseline"
  },
  "delta_summary": "Business output demonstrates substantial value-add through proprietary data coverage and more precise metrics.",
  "delta_score": 8.87,
  "status": "compared",
  "baseline_generated_at": "2026-02-27T10:30:00Z",
  "compared_at": "2026-03-01T16:30:00Z",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-03-01T16:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `delta_not_found` | No delta evaluation found for this order |

---

## GET /api/v1/delta/by-intention/{intention_id}

Retrieve the delta evaluation associated with a specific intention.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID | Yes | Intention ID |

### Request Example

```
GET /api/v1/delta/by-intention/f6a7b8c9-d0e1-2345-fab0-678901234567
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "dd112233-4455-6677-8899-aabbccddeeff",
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "bare_model_response": "Based on publicly available financial data for Q4 2025...",
  "business_response": null,
  "delta_analysis": null,
  "delta_summary": null,
  "delta_score": null,
  "status": "baseline_generated",
  "baseline_generated_at": "2026-02-27T10:30:00Z",
  "compared_at": null,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `delta_not_found` | No delta evaluation found for this intention |

---

## POST /api/v1/delta/{delta_id}/compare

Submit the business's response and trigger the LLM-as-judge comparison against the bare-model baseline.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `delta_id` | UUID | Yes | Delta evaluation ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `business_response` | str | Yes | The business's delivered response text |

### Request Example

```json
{
  "business_response": "Our proprietary analysis of Q4 2025 technology sector performance reveals 9.1% growth, outpacing consensus estimates by 0.9pp. Using our real-time data pipeline covering 2,847 public and private companies, we identified three underreported catalysts: (1) sovereign AI infrastructure spending in APAC grew 34% QoQ, (2) enterprise AI agent deployment reached 23% penetration in Fortune 500, up from 8% in Q3, and (3) edge computing revenue crossed $48B annualized. Our sector-weighted model projects continued outperformance into Q1 2026 with a 7.5-9.0% expected range."
}
```

### Response Example

```json
{
  "id": "dd112233-4455-6677-8899-aabbccddeeff",
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "bare_model_response": "Based on publicly available financial data for Q4 2025, the technology sector showed moderate growth of approximately 8.2%...",
  "business_response": "Our proprietary analysis of Q4 2025 technology sector performance reveals 9.1% growth, outpacing consensus estimates by 0.9pp...",
  "delta_analysis": {
    "dimensions": {
      "accuracy": {"score": 9.2, "rationale": "Business provides more precise growth figures backed by proprietary data covering 2,847 companies"},
      "depth": {"score": 8.8, "rationale": "Three specific underreported catalysts identified with quantitative backing"},
      "actionability": {"score": 8.5, "rationale": "Forward-looking projection with specific range estimate"},
      "timeliness": {"score": 9.0, "rationale": "Real-time pipeline data more current than baseline's publicly available summaries"}
    },
    "overall_assessment": "Business delivery significantly exceeds the bare-model baseline across all evaluation dimensions"
  },
  "delta_summary": "Business output demonstrates substantial value-add through proprietary data coverage (2,847 companies), more precise growth metrics (9.1% vs estimated 8.2%), and identification of three underreported market catalysts with quantitative support.",
  "delta_score": 8.87,
  "status": "compared",
  "baseline_generated_at": "2026-02-27T10:30:00Z",
  "compared_at": "2026-03-01T16:30:00Z",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-03-01T16:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `delta_not_found` | No delta evaluation with this ID |
| 409 | `already_compared` | This delta has already been compared |
| 409 | `baseline_not_ready` | Baseline has not been generated yet |
| 500 | `llm_comparison_failed` | The LLM judge service failed |
