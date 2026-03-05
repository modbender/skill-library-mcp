# Delta API

Base URL: `/api/v1/delta`

The Delta system measures business quality by comparing a bare-model baseline response against the business's actual delivery. An LLM-as-judge scores the difference, producing a delta score that quantifies the value added by the business.

All endpoints require authentication.

---

## POST /api/v1/delta/generate/{intention_id}

Generate a bare-model baseline response for an intention. This creates a Delta record and runs the baseline LLM against the intention description.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID | Yes | Intention ID to generate baseline for |

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID \| None | No | Optionally associate with an order |

### Request Body

None.

### Request Example

```
POST /api/v1/delta/generate/f6a7b8c9-d0e1-2345-fabc-456789012345?order_id=55667788-99aa-bbcc-ddee-ff0011223344
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "99001122-3344-5566-7788-99aabbccddee",
  "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "bare_model_response": "根据公开数据分析，A股市场大模型微调的一般方法包括：1. 使用财报文本进行预训练续写；2. 基于研报摘要做指令微调；3. 利用行情数据构建时序特征嵌入。建议使用LoRA方法降低训练成本，参考数据量约500万条。",
  "business_response": null,
  "delta_analysis": null,
  "delta_summary": null,
  "delta_score": null,
  "status": "baseline_generated",
  "baseline_generated_at": "2026-02-27T15:30:00Z",
  "compared_at": null,
  "created_at": "2026-02-27T15:30:00Z",
  "updated_at": "2026-02-27T15:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 404 | `"Intention not found"` | Intention ID does not exist |
| 409 | `"Delta already exists for this intention"` | Baseline already generated |

---

## GET /api/v1/delta/{delta_id}

Retrieve a Delta record by its ID.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `delta_id` | UUID | Yes | Delta record ID |

### Request Body

None.

### Request Example

```
GET /api/v1/delta/99001122-3344-5566-7788-99aabbccddee
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "99001122-3344-5566-7788-99aabbccddee",
  "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "bare_model_response": "根据公开数据分析，A股市场大模型微调的一般方法包括：1. 使用财报文本进行预训练续写；2. 基于研报摘要做指令微调；3. 利用行情数据构建时序特征嵌入。建议使用LoRA方法降低训练成本，参考数据量约500万条。",
  "business_response": "我们提供完整的金融大模型微调方案：1. 自建A股财报解析流水线，覆盖5年3800+上市公司完整财报（含附注）；2. 专有研报指令集20万条，含分析师评级标签；3. 实时行情接入层，支持Level-2逐笔数据；4. 基于QLoRA的分阶段训练策略，阶段一通用金融知识，阶段二行情分析专项。评测显示在金融问答准确率上比基线提升37%。",
  "delta_analysis": "商家方案在以下维度显著优于基线：(1) 数据覆盖度：5年3800家完整财报 vs 基线的泛化描述；(2) 方法论深度：分阶段QLoRA训练 vs 基线的单一LoRA建议；(3) 实际验证：提供了37%准确率提升的评测结果 vs 基线无评测；(4) 独特资源：20万条专有研报指令集、Level-2行情接入。",
  "delta_summary": "商家方案远超基线，具备独有数据资产和验证过的训练策略。",
  "delta_score": 0.87,
  "status": "compared",
  "baseline_generated_at": "2026-02-27T15:30:00Z",
  "compared_at": "2026-03-11T11:00:00Z",
  "created_at": "2026-02-27T15:30:00Z",
  "updated_at": "2026-03-11T11:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 404 | `"Delta not found"` | Delta ID does not exist |

---

## GET /api/v1/delta/by-order/{order_id}

Retrieve the Delta record associated with an order.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

None.

### Request Example

```
GET /api/v1/delta/by-order/55667788-99aa-bbcc-ddee-ff0011223344
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "99001122-3344-5566-7788-99aabbccddee",
  "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "bare_model_response": "根据公开数据分析，A股市场大模型微调的一般方法包括...",
  "business_response": "我们提供完整的金融大模型微调方案...",
  "delta_analysis": "商家方案在以下维度显著优于基线...",
  "delta_summary": "商家方案远超基线，具备独有数据资产和验证过的训练策略。",
  "delta_score": 0.87,
  "status": "compared",
  "baseline_generated_at": "2026-02-27T15:30:00Z",
  "compared_at": "2026-03-11T11:00:00Z",
  "created_at": "2026-02-27T15:30:00Z",
  "updated_at": "2026-03-11T11:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 404 | `"Delta not found for this order"` | No delta record linked to this order |

---

## GET /api/v1/delta/by-intention/{intention_id}

Retrieve the Delta record associated with an intention.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID | Yes | Intention ID |

### Request Body

None.

### Request Example

```
GET /api/v1/delta/by-intention/f6a7b8c9-d0e1-2345-fabc-456789012345
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "99001122-3344-5566-7788-99aabbccddee",
  "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "bare_model_response": "根据公开数据分析，A股市场大模型微调的一般方法包括...",
  "business_response": "我们提供完整的金融大模型微调方案...",
  "delta_analysis": "商家方案在以下维度显著优于基线...",
  "delta_summary": "商家方案远超基线，具备独有数据资产和验证过的训练策略。",
  "delta_score": 0.87,
  "status": "compared",
  "baseline_generated_at": "2026-02-27T15:30:00Z",
  "compared_at": "2026-03-11T11:00:00Z",
  "created_at": "2026-02-27T15:30:00Z",
  "updated_at": "2026-03-11T11:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 404 | `"Delta not found for this intention"` | No delta record linked to this intention |

---

## POST /api/v1/delta/{delta_id}/compare

Submit the business's response and trigger the LLM-as-judge comparison. The delta analysis, summary, and score are generated by comparing the business response against the bare-model baseline.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `delta_id` | UUID | Yes | Delta record ID (must be in `baseline_generated` status) |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `business_response` | str | Yes | The business's actual delivery/response text |

### Request Example

```json
{
  "business_response": "我们提供完整的金融大模型微调方案：1. 自建A股财报解析流水线，覆盖5年3800+上市公司完整财报（含附注）；2. 专有研报指令集20万条，含分析师评级标签；3. 实时行情接入层，支持Level-2逐笔数据；4. 基于QLoRA的分阶段训练策略，阶段一通用金融知识，阶段二行情分析专项。评测显示在金融问答准确率上比基线提升37%。"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "99001122-3344-5566-7788-99aabbccddee",
  "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "bare_model_response": "根据公开数据分析，A股市场大模型微调的一般方法包括：1. 使用财报文本进行预训练续写；2. 基于研报摘要做指令微调；3. 利用行情数据构建时序特征嵌入。建议使用LoRA方法降低训练成本，参考数据量约500万条。",
  "business_response": "我们提供完整的金融大模型微调方案：1. 自建A股财报解析流水线，覆盖5年3800+上市公司完整财报（含附注）；2. 专有研报指令集20万条，含分析师评级标签；3. 实时行情接入层，支持Level-2逐笔数据；4. 基于QLoRA的分阶段训练策略，阶段一通用金融知识，阶段二行情分析专项。评测显示在金融问答准确率上比基线提升37%。",
  "delta_analysis": "商家方案在以下维度显著优于基线：(1) 数据覆盖度：5年3800家完整财报 vs 基线的泛化描述；(2) 方法论深度：分阶段QLoRA训练 vs 基线的单一LoRA建议；(3) 实际验证：提供了37%准确率提升的评测结果 vs 基线无评测；(4) 独特资源：20万条专有研报指令集、Level-2行情接入。",
  "delta_summary": "商家方案远超基线，具备独有数据资产和验证过的训练策略。",
  "delta_score": 0.87,
  "status": "compared",
  "baseline_generated_at": "2026-02-27T15:30:00Z",
  "compared_at": "2026-03-11T11:00:00Z",
  "created_at": "2026-02-27T15:30:00Z",
  "updated_at": "2026-03-11T11:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 404 | `"Delta not found"` | Delta ID does not exist |
| 409 | `"Delta is not in baseline_generated status"` | Baseline not yet generated or already compared |
| 422 | Pydantic validation array | Empty business_response |
