# Intentions API

Base URL: `/api/v1/intentions`

Intentions represent a personal user's structured need. The personal user creates an intention, publishes it, and then triggers matching to find business candidates via multi-path recall (rules + Elasticsearch BM25 + Milvus vector + RRF fusion).

All endpoints require authentication. Personal users have full CRUD access plus match triggering.

---

## POST /api/v1/intentions/

Create a new intention in `draft` status.

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | str | Yes | Intention content, 2-5000 characters. Describes what you need. |
| `budget_min` | float \| None | No | Minimum budget amount |
| `budget_max` | float \| None | No | Maximum budget amount |
| `tags` | list[str] \| None | No | Free-form tags for discovery |
| `locale` | str | No | Locale for LLM processing, default `"zh"` |

### Request Example

```json
{
  "content": "我们需要一个针对中国A股市场的大语言模型微调服务，要求支持实时行情分析和研报生成，训练数据需覆盖最近5年的财报和公告数据。",
  "budget_min": 5000.00,
  "budget_max": 15000.00,
  "tags": ["金融", "大模型", "微调", "A股"],
  "locale": "zh"
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "content": "我们需要一个针对中国A股市场的大语言模型微调服务，要求支持实时行情分析和研报生成，训练数据需覆盖最近5年的财报和公告数据。",
  "title": null,
  "description": null,
  "category": "other",
  "budget_min": 5000.00,
  "budget_max": 15000.00,
  "currency": "USD",
  "status": "draft",
  "tags": ["金融", "大模型", "微调", "A股"],
  "locale": "zh",
  "match_count": 0,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 422 | Pydantic validation array | Content too short/long |

---

## GET /api/v1/intentions/

List intentions belonging to the current user.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Items per page, default `20`, max `100` |

### Request Example

```
GET /api/v1/intentions/?offset=0&limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "items": [
    {
      "id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "需要金融行业大模型微调服务",
      "description": "我们需要一个针对中国A股市场的大语言模型微调服务...",
      "category": "model",
      "budget_min": 5000.00,
      "budget_max": 15000.00,
      "currency": "USD",
      "status": "published",
      "tags": ["金融", "大模型", "微调", "A股"],
      "locale": "zh",
      "match_count": 3,
      "created_at": "2026-02-27T10:30:00Z",
      "updated_at": "2026-02-27T11:00:00Z"
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

## GET /api/v1/intentions/{intention_id}

Retrieve a single intention by ID. Only the owner can access their intentions.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID | Yes | Intention ID |

### Request Body

None.

### Request Example

```
GET /api/v1/intentions/f6a7b8c9-d0e1-2345-fabc-456789012345
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "需要金融行业大模型微调服务",
  "description": "我们需要一个针对中国A股市场的大语言模型微调服务，要求支持实时行情分析和研报生成，训练数据需覆盖最近5年的财报和公告数据。",
  "category": "model",
  "budget_min": 5000.00,
  "budget_max": 15000.00,
  "currency": "USD",
  "status": "published",
  "tags": ["金融", "大模型", "微调", "A股"],
  "locale": "zh",
  "match_count": 3,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T11:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to access this intention"` | User is not the owner |
| 404 | `"Intention not found"` | ID does not exist |

---

## PATCH /api/v1/intentions/{intention_id}

Update a draft intention. Only draft intentions can be edited.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID | Yes | Intention ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | str \| None | No | Updated content, 2-5000 characters |
| `budget_min` | float \| None | No | Updated minimum budget |
| `budget_max` | float \| None | No | Updated maximum budget |
| `tags` | list[str] \| None | No | Updated tags |

### Request Example

```json
{
  "budget_max": 20000.00,
  "tags": ["金融", "大模型", "微调", "A股", "研报生成"]
}
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "需要金融行业大模型微调服务",
  "description": "我们需要一个针对中国A股市场的大语言模型微调服务，要求支持实时行情分析和研报生成，训练数据需覆盖最近5年的财报和公告数据。",
  "category": "model",
  "budget_min": 5000.00,
  "budget_max": 20000.00,
  "currency": "USD",
  "status": "draft",
  "tags": ["金融", "大模型", "微调", "A股", "研报生成"],
  "locale": "zh",
  "match_count": 0,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T11:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to access this intention"` | User is not the owner |
| 404 | `"Intention not found"` | ID does not exist |
| 409 | `"Can only edit intentions in draft status"` | Intention is not in draft |
| 422 | Pydantic validation array | Invalid field values |

---

## POST /api/v1/intentions/{intention_id}/publish

Transition an intention from `draft` to `published`, making it eligible for matching.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID | Yes | Intention ID |

### Request Body

None.

### Request Example

```
POST /api/v1/intentions/f6a7b8c9-d0e1-2345-fabc-456789012345/publish
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "需要金融行业大模型微调服务",
  "description": "我们需要一个针对中国A股市场的大语言模型微调服务，要求支持实时行情分析和研报生成，训练数据需覆盖最近5年的财报和公告数据。",
  "category": "model",
  "budget_min": 5000.00,
  "budget_max": 20000.00,
  "currency": "USD",
  "status": "published",
  "tags": ["金融", "大模型", "微调", "A股", "研报生成"],
  "locale": "zh",
  "match_count": 0,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T12:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to access this intention"` | User is not the owner |
| 404 | `"Intention not found"` | ID does not exist |
| 409 | `"Can only publish intentions in draft status"` | Intention is not in draft |

---

## POST /api/v1/intentions/{intention_id}/cancel

Cancel a published or draft intention.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID | Yes | Intention ID |

### Request Body

None.

### Request Example

```
POST /api/v1/intentions/f6a7b8c9-d0e1-2345-fabc-456789012345/cancel
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "需要金融行业大模型微调服务",
  "description": "我们需要一个针对中国A股市场的大语言模型微调服务...",
  "category": "model",
  "budget_min": 5000.00,
  "budget_max": 20000.00,
  "currency": "USD",
  "status": "cancelled",
  "tags": ["金融", "大模型", "微调", "A股", "研报生成"],
  "locale": "zh",
  "match_count": 3,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T13:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to access this intention"` | User is not the owner |
| 404 | `"Intention not found"` | ID does not exist |
| 409 | `"Cannot cancel intention in current status"` | Intention already cancelled or completed |

---

## POST /api/v1/intentions/{intention_id}/match

Trigger business matching for a published intention. Uses multi-path recall: rule-based filtering, Elasticsearch BM25 keyword search, Milvus vector similarity, and RRF fusion ranking.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID | Yes | Intention ID (must be in `published` status) |

### Request Body

None.

### Request Example

```
POST /api/v1/intentions/f6a7b8c9-d0e1-2345-fabc-456789012345/match
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 202 Accepted**

```json
{
  "task_id": "abc123-task-id",
  "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "status": "dispatched"
}
```

Poll `GET /api/v1/intentions/{intention_id}/match/status` to check matching progress.

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to access this intention"` | User is not the owner |
| 404 | `"Intention not found"` | ID does not exist |
| 409 | `"Can only match published intentions"` | Intention is not in `published` status |

---

## GET /api/v1/intentions/{intention_id}/match/status

Poll matching progress after triggering `POST /match`.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID | Yes | Intention ID |

### Request Body

None.

### Response Example

**Status: 200 OK**

```json
{
  "status": "completed",
  "intention": {
    "id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "content": "我们需要一个针对中国A股市场的大语言模型微调服务...",
    "title": null,
    "description": null,
    "category": "other",
    "budget_min": 5000.00,
    "budget_max": 20000.00,
    "currency": "USD",
    "status": "matched",
    "tags": ["金融", "大模型", "微调", "A股"],
    "locale": "zh",
    "match_count": 3,
    "created_at": "2026-02-27T10:30:00Z",
    "updated_at": "2026-02-27T14:00:00Z"
  },
  "profile": {
    "id": "a7b8c9d0-e1f2-3456-abcd-567890123456",
    "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
    "domain_tags": ["金融科技", "资本市场"],
    "required_capabilities": ["大模型微调", "行情分析", "研报生成"],
    "complexity_score": 0.8,
    "urgency_score": 0.5,
    "semantic_summary": "金融大模型微调，A股市场行情分析与研报生成",
    "created_at": "2026-02-27T14:00:00Z"
  },
  "candidates": [
    {
      "id": "b8c9d0e1-f2a3-4567-bcde-678901234567",
      "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
      "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "rank": 1,
      "score": 0.92,
      "recall_sources": ["bm25", "vector", "rule"],
      "explanation": "该商家专注于金融大模型微调，拥有丰富的A股数据处理经验。",
      "business_name_zh": "智能数据科技",
      "business_name_en": "SmartData Tech",
      "business_reputation": 4.7
    }
  ],
  "error": null
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to access this intention"` | User is not the owner |
| 404 | `"Intention not found"` | ID does not exist |

---

## POST /api/v1/intentions/search

One-shot quick search: creates an intention, generates an NLP profile, matches businesses, and returns results synchronously.

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | str | Yes | What you need, 2-5000 characters |
| `budget_min` | float \| None | No | Minimum budget amount |
| `budget_max` | float \| None | No | Maximum budget amount |
| `tags` | list[str] \| None | No | Free-form tags |
| `locale` | str | No | Locale, default `"zh"` |

### Request Example

```json
{
  "content": "我需要一个AI客服解决方案，支持中英文多轮对话",
  "budget_max": 10000.00,
  "locale": "zh"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "intention": {
    "id": "...",
    "user_id": "...",
    "content": "我需要一个AI客服解决方案，支持中英文多轮对话",
    "title": null,
    "description": null,
    "category": "other",
    "budget_min": null,
    "budget_max": 10000.00,
    "currency": "USD",
    "status": "published",
    "tags": null,
    "locale": "zh",
    "match_count": 2,
    "created_at": "2026-02-27T14:00:00Z",
    "updated_at": "2026-02-27T14:00:00Z"
  },
  "candidates": [
    {
      "id": "...",
      "intention_id": "...",
      "business_id": "...",
      "rank": 1,
      "score": 0.88,
      "recall_sources": ["bm25", "vector"],
      "explanation": "专注于多语言AI客服方案",
      "business_name_zh": "智能客服科技",
      "business_name_en": "SmartCS Tech",
      "business_reputation": 4.5
    }
  ]
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 422 | Pydantic validation array | Content too short/long |

---

## POST /api/v1/intentions/search/stream

Same as `POST /search` but returns results as Server-Sent Events (SSE) for streaming UI updates.

**Auth:** Required

### Request Body

Same as `POST /intentions/search`.

### Response

SSE stream with events: `intention_created`, `profile_generated`, `candidates_found`, `done`, `error`.

---

## GET /api/v1/intentions/{intention_id}/matches

Retrieve saved match candidates for an intention.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID | Yes | Intention ID |

### Request Body

None.

### Request Example

```
GET /api/v1/intentions/f6a7b8c9-d0e1-2345-fabc-456789012345/matches
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
[
  {
    "id": "b8c9d0e1-f2a3-4567-bcde-678901234567",
    "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
    "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
    "rank": 1,
    "score": 0.92,
    "recall_sources": ["bm25", "vector", "rule"],
    "explanation": "该商家专注于金融大模型微调，拥有丰富的A股数据处理经验，预算匹配度高。",
    "business_name_zh": "智能数据科技",
    "business_name_en": "SmartData Tech",
    "business_reputation": 4.7
  },
  {
    "id": "c9d0e1f2-a3b4-5678-cdef-789012345678",
    "intention_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
    "business_id": "22334455-6677-8899-aabb-ccddeeff0011",
    "rank": 2,
    "score": 0.85,
    "recall_sources": ["bm25", "vector"],
    "explanation": "提供通用大模型微调服务，有金融行业案例，但专注度略低于首选。",
    "business_name_zh": "深度语言实验室",
    "business_name_en": "DeepLang Lab",
    "business_reputation": 4.3
  }
]
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to access this intention"` | User is not the owner |
| 404 | `"Intention not found"` | ID does not exist |
